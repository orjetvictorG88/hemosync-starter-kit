import importlib
import os
import sqlite3
import tempfile
import unittest
from contextlib import closing

from decision_support import TransferDecisionAuditStore, build_transfer_suggestion
from hemosync_core import BloodBank, CONFIG, GateViolation, State

_import_directory = tempfile.TemporaryDirectory()
_previous_database_path = os.environ.get("HEMOSYNC_DB_PATH")
os.environ["HEMOSYNC_DB_PATH"] = os.path.join(_import_directory.name, "api-import.sqlite3")
api = importlib.import_module("api")
if _previous_database_path is None:
    os.environ.pop("HEMOSYNC_DB_PATH", None)
else:
    os.environ["HEMOSYNC_DB_PATH"] = _previous_database_path


def released_unit(bank, din, group="O+"):
    eligible = bank.screen_donor(f"D-{din[-3:]}", 25, 70, 14.0, "M", "nurse.demo")
    unit = bank.collect(din, f"D-{din[-3:]}", "RBC", group, "nurse.demo", eligible)
    for marker in CONFIG["required_markers"]:
        bank.record_test(din, marker, "NEG", "tech.demo")
    bank.record_typing(din, group, "tech.one")
    bank.record_typing(din, group, "tech.two")
    bank.release(din, "tech.one", "supervisor.demo")
    return unit


class TestTransferDecisionSupport(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.previous_banks = api.BANKS
        self.previous_audit = api.DECISION_AUDIT
        self.source = BloodBank("SOURCE")
        self.target = BloodBank("TARGET")
        api.BANKS = {"SOURCE": self.source, "TARGET": self.target}
        api.DECISION_AUDIT = TransferDecisionAuditStore(
            os.path.join(self.directory.name, "audit.sqlite3")
        )

    def tearDown(self):
        api.BANKS = self.previous_banks
        api.DECISION_AUDIT = self.previous_audit
        self.directory.cleanup()

    def _request(
        self,
        z=1.96,
        source_mean_daily_use=0,
        source_lead_days=0,
        target_mean_daily_use=1,
        target_lead_days=1,
    ):
        return api.TransferSuggestionRequest(
            from_site="SOURCE",
            to_site="TARGET",
            component="RBC",
            group="O+",
            source_mean_daily_use=source_mean_daily_use,
            source_lead_days=source_lead_days,
            target_mean_daily_use=target_mean_daily_use,
            target_lead_days=target_lead_days,
            z=z,
        )

    def test_only_suggests_exact_group_stock_when_source_stays_green(self):
        unit = released_unit(self.source, "A999926000101")

        suggestion = build_transfer_suggestion(
            api.BANKS,
            from_site="SOURCE",
            to_site="TARGET",
            component="RBC",
            group="O+",
            source_mean_daily_use=0,
            source_lead_days=0,
            target_mean_daily_use=1,
            target_lead_days=1,
            z=1,
        )

        self.assertEqual(suggestion["status"], "recommended")
        self.assertEqual(suggestion["candidate_unit"]["din"], unit.din)
        self.assertEqual(suggestion["source"]["safe_surplus"], 1)
        self.assertEqual(suggestion["destination"]["colour"], "RED")
        self.assertEqual(len(suggestion["basis"]), 4)

    def test_does_not_recommend_when_source_would_fall_below_reorder_point(self):
        released_unit(self.source, "A999926000102")
        suggestion = build_transfer_suggestion(
            api.BANKS,
            from_site="SOURCE",
            to_site="TARGET",
            component="RBC",
            group="O+",
            source_mean_daily_use=1,
            source_lead_days=1,
            target_mean_daily_use=1,
            target_lead_days=1,
            z=1,
        )

        self.assertEqual(suggestion["status"], "no_recommendation")
        self.assertEqual(suggestion["reason"], "source_below_reserve")
        self.assertIsNone(suggestion["candidate_unit"])

    def test_approval_dispatches_one_unit_and_audits_the_human_decision(self):
        unit = released_unit(self.source, "A999926000103")
        suggestion = api.create_transfer_suggestion(self._request())

        result = api.decide_transfer_suggestion(
            suggestion["recommendation_id"],
            api.TransferDecisionRequest(decision="approve", actor="manager.demo"),
        )

        self.assertTrue(result["unit_moved"])
        self.assertEqual(unit.state, State.IN_TRANSIT)
        audit = api.transfer_decision_audit()
        self.assertTrue(audit["valid"])
        self.assertEqual([event["event_type"] for event in audit["events"]], ["suggested", "approved"])

    def test_approval_rechecks_source_using_suggestion_service_factor(self):
        units = [
            released_unit(self.source, f"A99992600010{number}")
            for number in (6, 7, 8)
        ]
        suggestion = api.create_transfer_suggestion(
            self._request(z=0.5, source_mean_daily_use=1)
        )

        result = api.decide_transfer_suggestion(
            suggestion["recommendation_id"],
            api.TransferDecisionRequest(decision="approve", actor="manager.demo"),
        )

        self.assertTrue(result["unit_moved"])
        self.assertEqual(self.source.on_hand("RBC", "O+"), 2)
        self.assertEqual(units[0].state, State.IN_TRANSIT)

    def test_override_requires_reason_and_does_not_dispatch(self):
        unit = released_unit(self.source, "A999926000104")
        suggestion = api.create_transfer_suggestion(self._request())
        recommendation_id = suggestion["recommendation_id"]

        with self.assertRaises(ValueError):
            api.decide_transfer_suggestion(
                recommendation_id,
                api.TransferDecisionRequest(decision="override", actor="manager.demo"),
            )
        result = api.decide_transfer_suggestion(
            recommendation_id,
            api.TransferDecisionRequest(
                decision="override",
                actor="manager.demo",
                reason="Destination ward cannot receive a delivery tonight",
            ),
        )

        self.assertFalse(result["unit_moved"])
        self.assertEqual(unit.state, State.RELEASED)
        audit = api.transfer_decision_audit()
        self.assertTrue(audit["valid"])
        self.assertEqual(audit["events"][-1]["event_type"], "overridden")
        self.assertIn("cannot receive", audit["events"][-1]["details"]["reason"])

    def test_approval_refuses_a_unit_that_changed_after_suggestion(self):
        unit = released_unit(self.source, "A999926000105")
        suggestion = api.create_transfer_suggestion(self._request())
        self.source.dispatch(unit.din, "TARGET", "store.demo")

        with self.assertRaises(GateViolation):
            api.decide_transfer_suggestion(
                suggestion["recommendation_id"],
                api.TransferDecisionRequest(decision="approve", actor="manager.demo"),
            )

        self.assertEqual(unit.state, State.IN_TRANSIT)
        self.assertFalse(api.DECISION_AUDIT.has_decision(suggestion["recommendation_id"]))

    def test_audit_rejects_tampering(self):
        store = api.DECISION_AUDIT
        store.append("rec-1", "suggested", "decision-support", {"suggestion": {"status": "none"}})
        store.append("rec-1", "overridden", "manager.demo", {"reason": "not needed"})
        with closing(sqlite3.connect(store.path)) as connection:
            with connection:
                connection.execute("DROP TRIGGER transfer_decision_audit_no_update")
                connection.execute(
                    "UPDATE transfer_decision_audit SET actor = 'changed' WHERE seq = 1"
                )

        self.assertFalse(store.verify())
        with self.assertRaises(ValueError):
            TransferDecisionAuditStore(store.path)


def tearDownModule():
    _import_directory.cleanup()


if __name__ == "__main__":
    unittest.main()

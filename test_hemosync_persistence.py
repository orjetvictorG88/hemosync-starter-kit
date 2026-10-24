import sqlite3
import tempfile
import unittest
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path

from hemosync_core import (
    BloodBank,
    CONFIG,
    LedgerIntegrityError,
    SQLiteEventStore,
    restore_banks,
)


class TestSQLiteEventReplay(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temporary_directory.name) / "hemosync.sqlite3"
        self.store = SQLiteEventStore(self.database_path)
        self.now = [datetime(2026, 10, 6, 8, 0, tzinfo=timezone.utc)]
        self.source = BloodBank("SITE-A", clock=lambda: self.now[0], store=self.store)
        self.target = BloodBank("SITE-B", clock=lambda: self.now[0], store=self.store)
        self.store.register_site("SITE-A")
        self.store.register_site("SITE-B")

    def tearDown(self):
        self.temporary_directory.cleanup()

    def _release_unit(self, din, donor_id, group):
        eligible = self.source.screen_donor(donor_id, 25, 65, 13.5, "F", "nurse.screen")
        unit = self.source.collect(din, donor_id, "RBC", group, "nurse.collect", eligible)
        for marker in CONFIG["required_markers"]:
            self.source.record_test(din, marker, "NEG", "tech.lab")
        self.source.record_typing(din, group, "tech.lab")
        self.source.record_typing(din, group, "tech.check")
        self.source.release(din, "tech.lab", "supervisor")
        return unit

    def test_restart_replays_identical_state_and_valid_site_chains(self):
        transfused = self._release_unit("A999926000001", "DEMO-DONOR-01", "A+")
        self.source.reserve(transfused.din, "P-7788", "A+", True, "nurse.ward")
        self.source.issue(transfused.din, "store.keeper")
        self.now[0] += timedelta(minutes=5)
        self.source.transfuse(transfused.din, "P-7788", transfused.din, "nurse.one", "nurse.two")
        self.source.report_adverse_event(transfused.din, "reported", "director", "Synthetic look-back")

        transferred = self._release_unit("A999926000002", "DEMO-DONOR-02", "O-")
        self.source.dispatch(transferred.din, "SITE-B", "courier")
        self.target.receive(transferred.din, self.source, "quality.officer", temp_ok=False)

        original_units = {
            site: dict(bank.units)
            for site, bank in (("SITE-A", self.source), ("SITE-B", self.target))
        }
        original_donations = dict(self.source.last_donation)
        original_events = {
            site: bank.log.events
            for site, bank in (("SITE-A", self.source), ("SITE-B", self.target))
        }

        restarted = restore_banks(self.store, initial_sites=("SITE-A",))

        self.assertEqual({site: dict(bank.units) for site, bank in restarted.items()}, original_units)
        self.assertEqual(restarted["SITE-A"].last_donation, original_donations)
        for site, bank in restarted.items():
            self.assertEqual(bank.log.events, original_events[site])
            self.assertEqual(bank.log.verify(), (True, None))
        self.assertNotIn(transferred.din, restarted["SITE-A"].units)
        self.assertEqual(restarted["SITE-B"].units[transferred.din].state.value, "HOLD")

    def test_startup_rejects_a_database_row_changed_after_write(self):
        unit = self._release_unit("A999926000003", "DEMO-DONOR-03", "B+")
        self.assertTrue(unit.din)
        with closing(sqlite3.connect(self.database_path)) as connection:
            with connection:
                connection.execute("UPDATE events SET actor = ? WHERE id = 1", ("tampered.actor",))

        with self.assertRaises(LedgerIntegrityError):
            restore_banks(self.store, initial_sites=("SITE-A",))

    def test_replay_restores_return_excursion_discard_and_expiry_events(self):
        returned = self._release_unit("A999926000004", "DEMO-DONOR-04", "A+")
        self.source.reserve(returned.din, "P-1", "A+", True, "nurse.one")
        self.source.issue(returned.din, "store.one")
        self.now[0] += timedelta(minutes=5)
        self.source.return_unit(returned.din, temp_ok=True, actor="nurse.one")
        self.source.flag_excursion([returned.din], "courier.one", "Synthetic temperature concern")

        discarded = self.source.collect(
            "A999926000005", "DEMO-DONOR-05", "RBC", "O+", "nurse.collect", screened_ok=True
        )
        self.source.discard(discarded.din, "synthetic discard", "tech.lab")

        expired = self.source.collect(
            "A999926000006", "DEMO-DONOR-06", "RBC", "B+", "nurse.collect", screened_ok=True
        )
        self.now[0] = expired.expires + timedelta(seconds=1)
        self.assertIn(expired.din, self.source.expire_sweep())

        restarted = restore_banks(self.store, initial_sites=("SITE-A",))

        self.assertEqual(restarted["SITE-A"].units, self.source.units)
        self.assertEqual(restarted["SITE-A"].log.events, self.source.log.events)
        self.assertEqual(restarted["SITE-A"].log.verify(), (True, None))


if __name__ == "__main__":
    unittest.main()

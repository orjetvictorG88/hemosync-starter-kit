import unittest
from datetime import datetime, timedelta, timezone

from hemosync_core import (BloodBank, CANONICAL_EVENTS, CONFIG, EventLog, GateViolation, State, compatible,
                           plasma_compatible, rbc_compatible, stock_light, ABO_RH, Event)


def make_bank(site="KE-TEST-1"):
    t = [datetime(2026, 10, 6, 8, 0, tzinfo=timezone.utc)]
    bank = BloodBank(site, clock=lambda: t[0])
    bank._t = t
    return bank


def released_unit(bank, din="A999926000001", group="A+", component="RBC"):
    ok = bank.screen_donor("D-" + din[-3:], 25, 70, 14.0, "M", "nurse.a")
    u = bank.collect(din, "D-" + din[-3:], component, group, "nurse.a", ok)
    for m in CONFIG["required_markers"]:
        bank.record_test(din, m, "NEG", "tech.b")
    bank.record_typing(din, group, "tech.b")
    bank.record_typing(din, group, "tech.c")
    bank.release(din, "tech.b", "sup.m")
    return u


class TestGates(unittest.TestCase):
    def test_new_unit_is_quarantined_and_cannot_be_matched(self):
        bank = make_bank()
        ok = bank.screen_donor("D-1", 25, 70, 14, "M", "n")
        u = bank.collect("A999926000002", "D-1", "RBC", "O+", "n", ok)
        self.assertEqual(u.state, State.QUARANTINE)
        with self.assertRaises(GateViolation):
            bank.reserve(u.din, "P-1", "O+", True, "t")

    def test_ineligible_donor_cannot_donate(self):
        bank = make_bank()
        ok = bank.screen_donor("D-2", 25, 45, 14, "M", "n")      # 45 kg < 50 kg
        self.assertFalse(ok)
        with self.assertRaises(GateViolation):
            bank.collect("A999926000003", "D-2", "RBC", "O+", "n", ok)

    def test_donation_interval_enforced(self):
        bank = make_bank()
        released_unit(bank, "A999926000004")
        again = bank.screen_donor("D-004", 25, 70, 14, "M", "n")  # same donor id, same day
        self.assertFalse(again)

    def test_reactive_marker_blocks_release(self):
        bank = make_bank()
        ok = bank.screen_donor("D-5", 25, 70, 14, "M", "n")
        u = bank.collect("A999926000005", "D-5", "RBC", "B+", "n", ok)
        for m in CONFIG["required_markers"]:
            bank.record_test(u.din, m, "NEG" if m != "HBV" else "REACTIVE", "t")
        bank.record_typing(u.din, "B+", "t")
        bank.record_typing(u.din, "B+", "t2")
        with self.assertRaises(GateViolation) as cm:
            bank.release(u.din, "t", "s")
        self.assertIn("HBV", str(cm.exception))
        self.assertEqual(u.state, State.QUARANTINE)

    def test_release_needs_two_different_people_and_two_typings(self):
        bank = make_bank()
        ok = bank.screen_donor("D-6", 25, 70, 14, "M", "n")
        u = bank.collect("A999926000006", "D-6", "RBC", "A+", "n", ok)
        for m in CONFIG["required_markers"]:
            bank.record_test(u.din, m, "NEG", "t")
        bank.record_typing(u.din, "A+", "t")
        with self.assertRaises(GateViolation):
            bank.release(u.din, "t", "s")                      # only one typing so far
        bank.record_typing(u.din, "A+", "t2")
        with self.assertRaises(GateViolation):
            bank.release(u.din, "t", "t")                      # same person twice
        bank.release(u.din, "t", "s")
        self.assertEqual(u.state, State.RELEASED)

    def test_incompatible_match_is_a_hard_stop(self):
        bank = make_bank()
        u = released_unit(bank, group="A+")
        with self.assertRaises(GateViolation) as cm:
            bank.reserve(u.din, "P-9", "O+", True, "t")
        self.assertIn("HARD STOP", str(cm.exception))
        with self.assertRaises(GateViolation):
            bank.reserve(u.din, "P-9", "A+", False, "t")       # patient group not confirmed twice

    def test_bedside_wristband_mismatch_is_a_hard_stop(self):
        bank = make_bank()
        u = released_unit(bank)
        bank.reserve(u.din, "P-7", "A+", True, "t")
        bank.issue(u.din, "t")
        with self.assertRaises(GateViolation):
            bank.transfuse(u.din, "P-8", u.din, "n1", "n2")
        with self.assertRaises(GateViolation):
            bank.transfuse(u.din, "P-7", u.din, "n1", "n1")
        bank.transfuse(u.din, "P-7", u.din, "n1", "n2")
        self.assertEqual(u.state, State.TRANSFUSED)

    def test_out_of_storage_too_long_cannot_start(self):
        bank = make_bank()
        u = released_unit(bank)
        bank.reserve(u.din, "P-7", "A+", True, "t")
        bank.issue(u.din, "t")
        bank._t[0] += timedelta(minutes=45)
        with self.assertRaises(GateViolation):
            bank.transfuse(u.din, "P-7", u.din, "n1", "n2")
        bank.return_unit(u.din, True, "t")
        self.assertEqual(u.state, State.DISCARDED)             # too long out of storage

    def test_expiry_sweep(self):
        bank = make_bank()
        u = released_unit(bank, component="PLT")
        bank._t[0] += timedelta(days=6)
        self.assertEqual(bank.expire_sweep(), [u.din])
        self.assertEqual(u.state, State.EXPIRED)

    def test_cold_chain_excursion_places_unit_on_hold(self):
        bank = make_bank()
        u = released_unit(bank)
        bank.flag_excursion([u.din], "t", "fridge 11C for 40 min")
        self.assertEqual(u.state, State.HOLD)
        with self.assertRaises(GateViolation):
            bank.reserve(u.din, "P-1", "A+", True, "t")


class TestCustody(unittest.TestCase):
    def test_two_step_handshake(self):
        a, b = make_bank("SITE-A"), make_bank("SITE-B")
        u = released_unit(a)
        with self.assertRaises(GateViolation):
            b.receive(u.din, a, "courier")                    # nothing dispatched yet
        a.dispatch(u.din, "SITE-B", "tech")
        self.assertEqual(u.state, State.IN_TRANSIT)
        with self.assertRaises(GateViolation):
            a.reserve(u.din, "P-1", "A+", True, "t")          # sender no longer controls it
        b.receive(u.din, a, "tech.b")
        self.assertEqual(b.units[u.din].state, State.RELEASED)
        self.assertEqual(b.units[u.din].site, "SITE-B")


class TestLedger(unittest.TestCase):
    def test_chain_detects_tampering(self):
        log = EventLog(strict=False)
        for i in range(5):
            log.append("Demo", f"U{i}", "actor", {"i": i})
        self.assertEqual(log.verify(), (True, None))
        e = log._events[2]
        log._events[2] = Event(**{**e.__dict__, "actor": "intruder"})
        ok, bad = log.verify()
        self.assertFalse(ok)
        self.assertEqual(bad, 2)

    def test_deleting_an_event_breaks_the_chain(self):
        log = EventLog(strict=False)
        for i in range(4):
            log.append("Demo", f"U{i}", "a", {})
        del log._events[1]
        self.assertFalse(log.verify()[0])


class TestVocabulary(unittest.TestCase):
    def test_there_are_exactly_twelve_events_and_unknown_ones_are_rejected(self):
        self.assertEqual(len(CANONICAL_EVENTS), 12)
        with self.assertRaises(ValueError):
            EventLog().append("SomethingInvented", None, "x")

    def test_every_event_the_engine_writes_is_canonical(self):
        bank = make_bank()
        u = released_unit(bank)
        bank.reserve(u.din, "P-1", "A+", True, "t")
        bank.issue(u.din, "t")
        bank.transfuse(u.din, "P-1", u.din, "n1", "n2")
        bank.report_adverse_event(u.din, "mild", "n1", "rash")
        used = {e.etype for e in bank.log.events}
        self.assertTrue(used <= set(CANONICAL_EVENTS))
        self.assertIn("AdverseEventReported", used)
        self.assertEqual(bank.log.verify(), (True, None))


class TestRulesAndMaths(unittest.TestCase):
    def test_rbc_matrix_properties(self):
        for g in ABO_RH:
            self.assertTrue(rbc_compatible(g, g))              # identical always works
        self.assertTrue(all(rbc_compatible("O-", r) for r in ABO_RH))        # universal donor
        self.assertTrue(all(rbc_compatible(d, "AB+") for d in ABO_RH))       # universal recipient
        self.assertFalse(rbc_compatible("A+", "A-"))
        self.assertFalse(rbc_compatible("B-", "A-"))
        self.assertEqual(sum(rbc_compatible(d, r) for d in ABO_RH for r in ABO_RH), 27)

    def test_plasma_is_the_mirror(self):
        self.assertTrue(all(plasma_compatible("AB+", r) for r in ABO_RH))
        self.assertTrue(plasma_compatible("A+", "O+"))
        self.assertFalse(plasma_compatible("O+", "A+"))

    def test_fefo_prefers_identical_group_then_earliest_expiry(self):
        bank = make_bank()
        u1 = released_unit(bank, "A999926000011", "O-")
        bank._t[0] += timedelta(days=2)
        u2 = released_unit(bank, "A999926000012", "O+")
        bank._t[0] += timedelta(days=2)
        u3 = released_unit(bank, "A999926000013", "O+")
        pick = bank.suggest_fefo("RBC", "O+")
        self.assertEqual(pick.din, u2.din)                    # identical group, earlier expiry than u3
        # An AB- patient can only take Rh-negative red cells: the O- unit is the only compatible one
        self.assertEqual(bank.suggest_fefo("RBC", "AB-").din, u1.din)
        # Nothing on the shelf is compatible with a platelet request for group B (no B or AB... platelets stocked)
        self.assertIsNone(bank.suggest_fefo("PLT", "B+"))

    def test_stock_light_thresholds(self):
        # lam = 1.5/day, lead = 1 day -> cover = 3, z = 2.33 -> ROP = 3 + 2.33*sqrt(3) = 7.04
        self.assertEqual(stock_light(2, 1.5, 1, 2.33)[0], "RED")
        self.assertEqual(stock_light(5, 1.5, 1, 2.33)[0], "AMBER")
        self.assertEqual(stock_light(8, 1.5, 1, 2.33)[0], "GREEN")
        _, cover, rop = stock_light(0, 1.5, 1, 2.33)
        self.assertAlmostEqual(cover, 3.0)
        self.assertAlmostEqual(rop, 7.04, places=2)


if __name__ == "__main__":
    unittest.main(verbosity=2)

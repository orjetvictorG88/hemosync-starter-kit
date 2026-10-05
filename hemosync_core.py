#!/usr/bin/env python3
"""
hemosync_core.py  --  HemoSync starter kit (technical slice v0)
==================================================================
A small, dependency-free reference of the safety rules in the HemoSync blueprint:

  * The Seven Gates      -> a unit cannot skip a gate; every refusal is explicit.
  * Quarantine-by-default-> a new unit is born QUARANTINED and locked.
  * Custody principle    -> only the site that holds a unit may change it; moving
                            a unit is a two-step handshake (dispatch, receive).
  * Event sourcing       -> state is rebuilt from an append-only, hash-chained log
                            (SHA-256), so edits to history are detectable.
  * FEFO + compatibility -> first-expiring-first-out among *compatible* units.
  * Math-based stock lights -> Red / Amber / Green derived from lead time,
                            demand and a chosen service level (not guesswork).

ALL DATA IN THE DEMO ARE SYNTHETIC. This is a teaching / hackathon prototype,
not a certified medical device, and it contains no real donor or patient data.

Run the demo:   python hemosync_core.py
Run the tests:  python -m unittest -v test_hemosync_core
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Dict, List, Optional, Tuple

# ----------------------------------------------------------------------------
# 1. Configuration  (the "country pack": change values, not code)
# ----------------------------------------------------------------------------
CONFIG = {
    # Infectious-disease panel that must be NEGATIVE before release (Kenya-style default;
    # confirm against national SOPs before any real use).
    "required_markers": ("HIV", "HBV", "HCV", "SYPHILIS"),
    # Shelf life in days by component (typical ranges: RBC 35-42 d, platelets 5-7 d, frozen plasma 1 yr)
    "shelf_life_days": {"RBC": 35, "PLT": 5, "FFP": 365},
    # A unit that has left controlled storage must be started within this many minutes
    # (a widely used rule of thumb for red cells; make it a policy setting).
    "max_minutes_out_of_storage": 30,
    # Donor intake defaults reported for Kenya (verify with KNBTS SOP): age 16-65, >= 50 kg,
    # Hb >= 12.5 g/dL, 3 months between donations for men, 4 for women.
    "donor_rules": dict(min_age=16, max_age=65, min_weight_kg=50, min_hb=12.5,
                        interval_days_male=90, interval_days_female=120),
}

ABO_RH = ("O-", "O+", "A-", "A+", "B-", "B+", "AB-", "AB+")

# The Twelve Events of blood: a closed vocabulary. Dashboards, forecasts, audit views and FHIR exports
# are all *projections* of a log made only of these events.
CANONICAL_EVENTS = (
    "DonorScreened", "UnitCollected", "TestResultRecorded", "UnitReleased", "UnitDiscarded",
    "CustodyTransferred", "TemperatureExcursionFlagged", "UnitReserved", "UnitIssued",
    "UnitReturned", "TransfusionStarted", "AdverseEventReported",
)


class GateViolation(Exception):
    """Raised when a unit tries to pass a gate it has not earned. Never bypassable."""


# ----------------------------------------------------------------------------
# 2. Blood-group compatibility
# ----------------------------------------------------------------------------
def _split(group: str) -> Tuple[str, bool]:
    rh_pos = group.endswith("+")
    return group[:-1], rh_pos


def rbc_compatible(donor: str, recipient: str) -> bool:
    """Red cells: donor ABO must not carry an antigen the recipient lacks; Rh+ -> Rh+ only."""
    d_abo, d_pos = _split(donor)
    r_abo, r_pos = _split(recipient)
    abo_ok = {"O": {"O", "A", "B", "AB"}, "A": {"A", "AB"}, "B": {"B", "AB"}, "AB": {"AB"}}[d_abo]
    if r_abo not in abo_ok:
        return False
    return (not d_pos) or r_pos


def plasma_compatible(donor: str, recipient: str) -> bool:
    """Plasma is the mirror image of red cells (ABO only; Rh ignored)."""
    d_abo, _ = _split(donor)
    r_abo, _ = _split(recipient)
    ok = {"AB": {"O", "A", "B", "AB"}, "A": {"A", "O"}, "B": {"B", "O"}, "O": {"O"}}[d_abo]
    return r_abo in ok


def compatible(component: str, donor_group: str, recipient_group: str) -> bool:
    if component == "RBC":
        return rbc_compatible(donor_group, recipient_group)
    if component == "FFP":
        return plasma_compatible(donor_group, recipient_group)
    if component == "PLT":                   # safe default: ABO-identical (local policy may widen this)
        return _split(donor_group)[0] == _split(recipient_group)[0]
    raise ValueError(component)


# ----------------------------------------------------------------------------
# 3. Event log: append-only and hash-chained
# ----------------------------------------------------------------------------
GENESIS = "0" * 64


@dataclass(frozen=True)
class Event:
    seq: int
    etype: str                   # one of the canonical events, e.g. "UnitReleased"
    unit_id: Optional[str]
    actor: str                   # user id (never a name)
    site: str                    # facility id
    device: str
    ts: str                      # ISO-8601 UTC
    payload: dict
    prev_hash: str
    hash: str


def _digest(prev_hash: str, body: dict) -> str:
    canon = json.dumps(body, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256((prev_hash + canon).encode()).hexdigest()


class EventLog:
    """Append-only ledger. There is no update(); there is no delete()."""

    def __init__(self, site: str = "SITE-000", device: str = "DEV-000", clock=None, strict: bool = True):
        self.site, self.device, self.strict = site, device, strict
        self._events: List[Event] = []
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def __len__(self):
        return len(self._events)

    @property
    def events(self) -> Tuple[Event, ...]:
        return tuple(self._events)

    @property
    def head(self) -> str:
        return self._events[-1].hash if self._events else GENESIS

    def append(self, etype: str, unit_id: Optional[str], actor: str, payload: Optional[dict] = None) -> Event:
        if self.strict and etype not in CANONICAL_EVENTS:
            raise ValueError(f"{etype!r} is not one of the twelve canonical events")
        body = dict(seq=len(self._events), etype=etype, unit_id=unit_id, actor=actor, site=self.site,
                    device=self.device, ts=self._clock().isoformat(timespec="seconds"),
                    payload=payload or {})
        ev = Event(prev_hash=self.head, hash=_digest(self.head, body), **body)
        self._events.append(ev)
        return ev

    def verify(self) -> Tuple[bool, Optional[int]]:
        """Recompute the whole chain. Returns (ok, index_of_first_bad_event)."""
        prev = GENESIS
        for i, e in enumerate(self._events):
            body = dict(seq=e.seq, etype=e.etype, unit_id=e.unit_id, actor=e.actor, site=e.site,
                        device=e.device, ts=e.ts, payload=e.payload)
            if e.prev_hash != prev or e.hash != _digest(prev, body):
                return False, i
            prev = e.hash
        return True, None


# ----------------------------------------------------------------------------
# 4. Units and the Seven Gates
# ----------------------------------------------------------------------------
class State(str, Enum):
    QUARANTINE = "QUARANTINE"
    RELEASED = "RELEASED"
    RESERVED = "RESERVED"
    ISSUED = "ISSUED"
    TRANSFUSED = "TRANSFUSED"
    IN_TRANSIT = "IN_TRANSIT"
    HOLD = "HOLD"
    DISCARDED = "DISCARDED"
    EXPIRED = "EXPIRED"


TERMINAL = {State.TRANSFUSED, State.DISCARDED, State.EXPIRED}


@dataclass
class Unit:
    din: str                        # ISBT 128 donation identification number (13 chars), synthetic here
    component: str
    abo_rh: str
    collected: datetime
    expires: datetime
    site: str                       # custodian (None while in transit)
    state: State = State.QUARANTINE
    tests: Dict[str, str] = field(default_factory=dict)       # marker -> NEG / REACTIVE / INDETERMINATE
    typings: List[str] = field(default_factory=list)          # independent ABO/Rh determinations
    reserved_for: Optional[str] = None
    issued_at: Optional[datetime] = None
    dispatched_to: Optional[str] = None


class BloodBank:
    """One facility's view. Every method either changes state *and* logs, or raises GateViolation."""

    def __init__(self, site: str, log: Optional[EventLog] = None, clock=None):
        self.site = site
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self.log = log or EventLog(site=site, clock=self._clock)
        self.units: Dict[str, Unit] = {}
        self.last_donation: Dict[str, datetime] = {}       # pseudonymous donor id -> date

    # ---- helpers ---------------------------------------------------------
    def now(self) -> datetime:
        return self._clock()

    def _unit(self, din: str) -> Unit:
        if din not in self.units:
            raise GateViolation(f"unknown unit {din}")
        u = self.units[din]
        if u.state in TERMINAL:
            raise GateViolation(f"{din} is {u.state.value}: no further action allowed")
        if u.site != self.site and u.state != State.IN_TRANSIT:
            raise GateViolation(f"custody: {din} belongs to {u.site}, not {self.site}")
        return u

    # ---- GATE 1: donor eligible -------------------------------------------
    def screen_donor(self, donor_id: str, age: int, weight_kg: float, hb: float, sex: str, actor: str) -> bool:
        r, ok, why = CONFIG["donor_rules"], True, []
        if not r["min_age"] <= age <= r["max_age"]:
            ok, why = False, why + ["age"]
        if weight_kg < r["min_weight_kg"]:
            ok, why = False, why + ["weight"]
        if hb < r["min_hb"]:
            ok, why = False, why + ["haemoglobin"]
        gap = r["interval_days_male"] if sex.upper() == "M" else r["interval_days_female"]
        last = self.last_donation.get(donor_id)
        if last and (self.now() - last).days < gap:
            ok, why = False, why + ["too soon since last donation"]
        self.log.append("DonorScreened", None, actor,
                        dict(donor=donor_id, eligible=ok, reasons=why))   # reasons, never diagnoses
        return ok

    # ---- GATE 2: collected, born in quarantine ---------------------------
    def collect(self, din: str, donor_id: str, component: str, abo_rh: str, actor: str, screened_ok: bool) -> Unit:
        if not screened_ok:
            raise GateViolation("Gate 1: donor has not passed screening")
        if din in self.units:
            raise GateViolation("duplicate donation number")
        now = self.now()
        u = Unit(din, component, abo_rh, now, now + timedelta(days=CONFIG["shelf_life_days"][component]), self.site)
        self.units[din] = u
        self.last_donation[donor_id] = now
        self.log.append("UnitCollected", din, actor, dict(component=component, state="QUARANTINE"))
        return u

    # ---- GATE 3: tested ----------------------------------------------------
    def record_test(self, din: str, marker: str, result: str, actor: str) -> None:
        u = self._unit(din)
        if u.state != State.QUARANTINE:
            raise GateViolation("tests are recorded only while a unit is in quarantine")
        u.tests[marker] = result
        self.log.append("TestResultRecorded", din, actor, dict(marker=marker, result=result))

    def record_typing(self, din: str, abo_rh: str, actor: str) -> None:
        u = self._unit(din)
        u.typings.append(abo_rh)
        self.log.append("TestResultRecorded", din, actor, dict(marker="ABO_RH", abo_rh=abo_rh, n=len(u.typings)))

    # ---- GATE 4: released (dual authorisation) -----------------------------
    def release(self, din: str, tech: str, supervisor: str) -> None:
        u = self._unit(din)
        if u.state != State.QUARANTINE:
            raise GateViolation("only quarantined units can be released")
        if tech == supervisor:
            raise GateViolation("Gate 4: dual authorisation needs two different people")
        missing = [m for m in CONFIG["required_markers"] if m not in u.tests]
        if missing:
            raise GateViolation(f"Gate 3: tests incomplete: {', '.join(missing)}")
        bad = [m for m, r in u.tests.items() if r != "NEG"]
        if bad:
            raise GateViolation(f"Gate 3: non-negative result(s): {', '.join(bad)} -> must be discarded, never released")
        if len(u.typings) < 2 or len(set(u.typings)) != 1 or u.typings[0] != u.abo_rh:
            raise GateViolation("Gate 3: ABO/Rh needs two matching independent determinations")
        if u.expires <= self.now():
            raise GateViolation("unit is already expired")
        u.state = State.RELEASED
        self.log.append("UnitReleased", din, tech, dict(second_signature=supervisor))

    def discard(self, din: str, reason: str, actor: str) -> None:
        u = self._unit(din)
        u.state = State.DISCARDED
        self.log.append("UnitDiscarded", din, actor, dict(reason=reason))

    # ---- GATE 5: cold chain -------------------------------------------------
    def flag_excursion(self, dins: List[str], actor: str, detail: str) -> None:
        for d in dins:
            u = self._unit(d)
            if u.state in (State.RELEASED, State.RESERVED):
                u.state = State.HOLD
            self.log.append("TemperatureExcursionFlagged", d, actor, dict(detail=detail, state="HOLD"))

    # ---- GATE 6: matched (hard stop) ---------------------------------------
    def reserve(self, din: str, patient_id: str, patient_group: str, two_sample_confirmed: bool, actor: str) -> None:
        u = self._unit(din)
        if u.state != State.RELEASED:
            raise GateViolation(f"Gate 4/6: only RELEASED units can be matched (this one is {u.state.value})")
        if not two_sample_confirmed:
            raise GateViolation("Gate 6: patient group must be confirmed on two independent samples")
        if not compatible(u.component, u.abo_rh, patient_group):
            raise GateViolation(f"Gate 6 HARD STOP: {u.abo_rh} {u.component} is incompatible with {patient_group}")
        if u.expires <= self.now():
            raise GateViolation("unit expired")
        u.state, u.reserved_for = State.RESERVED, patient_id
        self.log.append("UnitReserved", din, actor, dict(patient=patient_id, group=patient_group))

    def issue(self, din: str, actor: str) -> None:
        u = self._unit(din)
        if u.state != State.RESERVED:
            raise GateViolation("only RESERVED units can be issued")
        u.state, u.issued_at = State.ISSUED, self.now()
        self.log.append("UnitIssued", din, actor, {})

    # ---- GATE 7: bedside verified -------------------------------------------
    def transfuse(self, din: str, scanned_patient: str, scanned_unit: str, nurse1: str, nurse2: str) -> None:
        u = self._unit(din)
        if u.state != State.ISSUED:
            raise GateViolation("only ISSUED units can be transfused")
        if scanned_unit != din:
            raise GateViolation("Gate 7: scanned bag does not match the issued unit")
        if scanned_patient != u.reserved_for:
            raise GateViolation("Gate 7 HARD STOP: wristband does not match the patient this unit was matched to")
        if nurse1 == nurse2:
            raise GateViolation("Gate 7: two different people must complete the bedside check")
        minutes = (self.now() - u.issued_at).total_seconds() / 60
        if minutes > CONFIG["max_minutes_out_of_storage"]:
            raise GateViolation(f"unit has been out of storage {minutes:.0f} min: return or discard per policy")
        u.state = State.TRANSFUSED
        self.log.append("TransfusionStarted", din, nurse1, dict(second_check=nurse2, minutes_out=round(minutes, 1)))

    def return_unit(self, din: str, temp_ok: bool, actor: str) -> None:
        u = self._unit(din)
        if u.state != State.ISSUED:
            raise GateViolation("only ISSUED units can be returned")
        minutes = (self.now() - u.issued_at).total_seconds() / 60
        if temp_ok and minutes <= CONFIG["max_minutes_out_of_storage"]:
            u.state, u.reserved_for, u.issued_at = State.RELEASED, None, None
            self.log.append("UnitReturned", din, actor, dict(accepted=True, minutes_out=round(minutes, 1)))
        else:
            u.state = State.DISCARDED
            self.log.append("UnitReturned", din, actor, dict(accepted=False, minutes_out=round(minutes, 1)))

    # ---- The loop: outcomes flow back ----------------------------------------------
    def report_adverse_event(self, din: str, severity: str, actor: str, detail: str = "") -> None:
        """Adverse events never change a unit's state by themselves; they trigger look-back by humans."""
        if din not in self.units:
            raise GateViolation(f"unknown unit {din}")
        self.log.append("AdverseEventReported", din, actor, dict(severity=severity, detail=detail))

    # ---- Custody handshake -----------------------------------------------------
    def dispatch(self, din: str, to_site: str, actor: str) -> None:
        u = self._unit(din)
        if u.state != State.RELEASED:
            raise GateViolation("only RELEASED units can be dispatched")
        u.state, u.dispatched_to = State.IN_TRANSIT, to_site
        self.log.append("CustodyTransferred", din, actor, dict(phase="dispatched", to=to_site))

    def receive(self, din: str, from_bank: "BloodBank", actor: str, temp_ok: bool = True) -> None:
        u = from_bank.units.get(din)
        if u is None or u.state != State.IN_TRANSIT or u.dispatched_to != self.site:
            raise GateViolation("custody: nothing was dispatched to this site for that unit")
        u.site, u.dispatched_to = self.site, None
        u.state = State.RELEASED if temp_ok else State.HOLD
        self.units[din] = u
        self.log.append("CustodyTransferred", din, actor, dict(phase="received", temp_ok=temp_ok, state=u.state.value))

    # ---- Housekeeping ---------------------------------------------------------------
    def expire_sweep(self, actor: str = "system") -> List[str]:
        out = []
        for d, u in self.units.items():
            if u.state not in TERMINAL and u.expires <= self.now():
                u.state = State.EXPIRED
                self.log.append("UnitDiscarded", d, actor, dict(reason="expired"))
                out.append(d)
        return out

    # ---- Allocation helper: FEFO among compatible RELEASED units -----------------------
    def suggest_fefo(self, component: str, patient_group: str) -> Optional[Unit]:
        pool = [u for u in self.units.values()
                if u.state == State.RELEASED and u.component == component
                and u.expires > self.now() and compatible(component, u.abo_rh, patient_group)]
        # prefer identical group, then earliest expiry: first-expiring-first-out
        pool.sort(key=lambda u: (u.abo_rh != patient_group, u.expires))
        return pool[0] if pool else None

    def on_hand(self, component: str, group: Optional[str] = None) -> int:
        return sum(1 for u in self.units.values() if u.state == State.RELEASED and u.component == component
                   and (group is None or u.abo_rh == group) and u.expires > self.now())


# ----------------------------------------------------------------------------
# 5. Stock lights derived from maths, not from hunches
# ----------------------------------------------------------------------------
def stock_light(on_hand: int, mean_daily_use: float, lead_days: float, z: float) -> Tuple[str, float, float]:
    """
    Protection interval = lead + 1 day (daily review).  Demand over that interval is ~Poisson,
    so   cover = lam * (lead+1)   and   reorder_point = cover + z * sqrt(cover).
    RED   : on hand < cover           (we expect to run out before the next delivery)
    AMBER : cover <= on hand < reorder point
    GREEN : on hand >= reorder point
    Returns (colour, cover, reorder_point).
    """
    cover = mean_daily_use * (lead_days + 1)
    rop = cover + z * math.sqrt(cover)
    if on_hand < cover:
        return "RED", cover, rop
    if on_hand < rop:
        return "AMBER", cover, rop
    return "GREEN", cover, rop


# ----------------------------------------------------------------------------
# 6. End-to-end demo (synthetic)
# ----------------------------------------------------------------------------
def demo(verbose: bool = True, tamper: bool = True):
    t = [datetime(2026, 10, 6, 8, 0, tzinfo=timezone.utc)]
    clock = lambda: t[0]
    tick = lambda minutes: t.__setitem__(0, t[0] + timedelta(minutes=minutes))
    say = print if verbose else (lambda *a, **k: None)

    bank = BloodBank("KE-RBTC-DEMO", clock=clock)
    say("== VEIN TO VEIN (synthetic data) ==")
    ok = bank.screen_donor("D-0001", age=21, weight_kg=63, hb=13.4, sex="F", actor="nurse.amina")
    say("Gate 1  donor eligible:", ok)
    u = bank.collect("A999926000001", "D-0001", "RBC", "A+", "nurse.amina", ok)
    say("Gate 2  unit born in", u.state.value)

    try:
        bank.reserve(u.din, "P-7788", "A+", True, "tech.joy")
    except GateViolation as e:
        say("         blocked ->", e)

    for m in CONFIG["required_markers"]:
        bank.record_test(u.din, m, "NEG", "tech.brian")
    bank.record_typing(u.din, "A+", "tech.brian")
    try:
        bank.release(u.din, "tech.brian", "sup.mercy")
    except GateViolation as e:
        say("Gate 3  blocked ->", e)
    bank.record_typing(u.din, "A+", "tech.joy")
    bank.release(u.din, "tech.brian", "sup.mercy")
    say("Gate 4  released by two people ->", u.state.value)

    try:
        bank.reserve(u.din, "P-7788", "O+", True, "tech.joy")
    except GateViolation as e:
        say("Gate 6  blocked ->", e)
    bank.reserve(u.din, "P-7788", "A+", True, "tech.joy")
    tick(5)
    bank.issue(u.din, "tech.joy")
    tick(12)
    try:
        bank.transfuse(u.din, "P-0000", u.din, "nurse.achieng", "nurse.wafula")
    except GateViolation as e:
        say("Gate 7  blocked ->", e)
    bank.transfuse(u.din, "P-7788", u.din, "nurse.achieng", "nurse.wafula")
    say("Gate 7  bedside verified ->", u.state.value)

    ok_chain, bad = bank.log.verify()
    say(f"\nLedger: {len(bank.log)} events, chain valid = {ok_chain}")
    for e in bank.log.events[:4]:
        say(f"  #{e.seq:<2d} {e.etype:<22s} prev={e.prev_hash[:10]}..  hash={e.hash[:10]}..")

    if not tamper:
        return bank
    # tamper with history: quietly change who released the unit
    victim = next(i for i, e in enumerate(bank.log._events) if e.etype == "UnitReleased")
    forged = bank.log._events[victim]
    bank.log._events[victim] = Event(**{**forged.__dict__, "actor": "tech.someone.else"})
    ok_chain, bad = bank.log.verify()
    say(f"After editing event #{victim}: chain valid = {ok_chain}, first broken link = #{bad}")
    return bank


if __name__ == "__main__":
    demo()

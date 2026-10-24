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
import sqlite3
import threading
from contextlib import closing
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from enum import Enum
from typing import Dict, Iterable, List, Optional, Tuple

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

    def __init__(
        self,
        site: str = "SITE-000",
        device: str = "DEV-000",
        clock=None,
        strict: bool = True,
        store: Optional["SQLiteEventStore"] = None,
    ):
        self.site, self.device, self.strict = site, device, strict
        self._events: List[Event] = []
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._store = store
        self._lock = threading.RLock()

    def __len__(self):
        return len(self._events)

    @property
    def events(self) -> Tuple[Event, ...]:
        return tuple(self._events)

    @property
    def head(self) -> str:
        return self._events[-1].hash if self._events else GENESIS

    def append(
        self,
        etype: str,
        unit_id: Optional[str],
        actor: str,
        payload: Optional[dict] = None,
        timestamp: Optional[datetime] = None,
    ) -> Event:
        if self.strict and etype not in CANONICAL_EVENTS:
            raise ValueError(f"{etype!r} is not one of the twelve canonical events")
        with self._lock:
            body = dict(seq=len(self._events), etype=etype, unit_id=unit_id, actor=actor, site=self.site,
                        device=self.device, ts=(timestamp or self._clock()).isoformat(),
                        payload=payload or {})
            ev = Event(prev_hash=self.head, hash=_digest(self.head, body), **body)
            if self._store is not None:
                self._store.append(ev)
            self._events.append(ev)
            return ev

    def append_saved(self, event: Event) -> None:
        """Restore an event without changing its original hash or timestamp."""
        with self._lock:
            if event.seq != len(self._events) or event.site != self.site:
                raise ValueError("event sequence or site does not match this ledger")
            if self.strict and event.etype not in CANONICAL_EVENTS:
                raise ValueError(f"{event.etype!r} is not one of the twelve canonical events")
            if event.prev_hash != self.head or event.hash != _digest(event.prev_hash, {
                "seq": event.seq,
                "etype": event.etype,
                "unit_id": event.unit_id,
                "actor": event.actor,
                "site": event.site,
                "device": event.device,
                "ts": event.ts,
                "payload": event.payload,
            }):
                raise ValueError(f"event #{event.seq} does not continue this ledger")
            self._events.append(event)

    def verify(self) -> Tuple[bool, Optional[int]]:
        """Recompute the whole chain. Returns (ok, index_of_first_bad_event)."""
        prev = GENESIS
        for i, e in enumerate(self._events):
            body = dict(seq=e.seq, etype=e.etype, unit_id=e.unit_id, actor=e.actor, site=e.site,
                        device=e.device, ts=e.ts, payload=e.payload)
            if (e.seq != i or e.site != self.site
                    or (self.strict and e.etype not in CANONICAL_EVENTS)
                    or e.prev_hash != prev or e.hash != _digest(prev, body)):
                return False, i
            prev = e.hash
        return True, None


class LedgerIntegrityError(RuntimeError):
    """Raised when stored ledger history cannot be verified or replayed."""


class SQLiteEventStore:
    """SQLite persistence for append-only events and registered facility IDs."""

    def __init__(self, path: Path | str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.path)) as connection:
            with connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        seq INTEGER NOT NULL,
                        etype TEXT NOT NULL,
                        unit_id TEXT,
                        actor TEXT NOT NULL,
                        site TEXT NOT NULL,
                        device TEXT NOT NULL,
                        ts TEXT NOT NULL,
                        payload TEXT NOT NULL,
                        prev_hash TEXT NOT NULL,
                        hash TEXT NOT NULL,
                        UNIQUE(site, seq)
                    )
                    """
                )
                connection.execute("CREATE TABLE IF NOT EXISTS sites (site TEXT PRIMARY KEY)")

    def register_site(self, site: str) -> None:
        with closing(sqlite3.connect(self.path)) as connection:
            with connection:
                connection.execute("INSERT OR IGNORE INTO sites(site) VALUES (?)", (site,))

    def sites(self) -> List[str]:
        with closing(sqlite3.connect(self.path)) as connection:
            rows = connection.execute("SELECT site FROM sites ORDER BY site").fetchall()
        return [row[0] for row in rows]

    def append(self, event: Event) -> None:
        connection = sqlite3.connect(self.path, timeout=30)
        try:
            with connection:
                connection.execute("BEGIN IMMEDIATE")
                previous = connection.execute(
                    "SELECT seq, hash FROM events WHERE site = ? ORDER BY seq DESC LIMIT 1",
                    (event.site,),
                ).fetchone()
                expected_seq = previous[0] + 1 if previous else 0
                expected_hash = previous[1] if previous else GENESIS
                if event.seq != expected_seq or event.prev_hash != expected_hash:
                    raise LedgerIntegrityError(f"stored ledger head for {event.site} changed unexpectedly")
                connection.execute(
                    """
                    INSERT INTO events
                        (seq, etype, unit_id, actor, site, device, ts, payload, prev_hash, hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        event.seq,
                        event.etype,
                        event.unit_id,
                        event.actor,
                        event.site,
                        event.device,
                        event.ts,
                        json.dumps(event.payload, sort_keys=True, separators=(",", ":")),
                        event.prev_hash,
                        event.hash,
                    ),
                )
                connection.execute("INSERT OR IGNORE INTO sites(site) VALUES (?)", (event.site,))
        finally:
            connection.close()

    def load_events(self) -> List[Event]:
        with closing(sqlite3.connect(self.path)) as connection:
            rows = connection.execute(
                """
                SELECT seq, etype, unit_id, actor, site, device, ts, payload, prev_hash, hash
                FROM events ORDER BY id
                """
            ).fetchall()
        try:
            return [
                Event(
                    seq=row[0],
                    etype=row[1],
                    unit_id=row[2],
                    actor=row[3],
                    site=row[4],
                    device=row[5],
                    ts=row[6],
                    payload=json.loads(row[7]),
                    prev_hash=row[8],
                    hash=row[9],
                )
                for row in rows
            ]
        except (TypeError, ValueError, json.JSONDecodeError) as error:
            raise LedgerIntegrityError("stored ledger contains an invalid event payload") from error

    def verify(
        self,
        events: Optional[List[Event]] = None,
    ) -> Dict[str, Tuple[bool, Optional[int]]]:
        events = self.load_events() if events is None else events
        events_by_site: Dict[str, List[Event]] = {}
        for event in events:
            events_by_site.setdefault(event.site, []).append(event)

        results: Dict[str, Tuple[bool, Optional[int]]] = {}
        for site in sorted(set(self.sites()) | set(events_by_site)):
            site_events = events_by_site.get(site, [])
            verifier = EventLog(site=site, device=site_events[0].device if site_events else "DEV-000")
            try:
                for event in site_events:
                    verifier.append_saved(event)
            except ValueError:
                results[site] = (False, len(verifier))
                continue
            results[site] = verifier.verify()
        return results


def restore_banks(
    store: SQLiteEventStore,
    initial_sites: Iterable[str] = (),
) -> Dict[str, "BloodBank"]:
    """Verify persisted chains and rebuild each site's state from events."""
    events = store.load_events()
    events_by_site: Dict[str, List[Event]] = {}
    sites = set(initial_sites) | set(store.sites())
    for event in events:
        events_by_site.setdefault(event.site, []).append(event)
        if event.etype == "CustodyTransferred" and event.payload.get("phase") == "dispatched":
            destination = event.payload.get("to")
            if isinstance(destination, str) and destination:
                sites.add(destination)

    for site, (valid, first_bad) in store.verify(events).items():
        if not valid:
            raise LedgerIntegrityError(f"ledger for {site} is invalid at event #{first_bad}")

    clocks = {site: [datetime.now(timezone.utc)] for site in sites}
    banks: Dict[str, BloodBank] = {}
    for site in sites:
        clock = clocks[site]
        banks[site] = BloodBank(
            site,
            log=EventLog(site=site, clock=lambda clock=clock: clock[0]),
            clock=lambda clock=clock: clock[0],
        )

    for event in events:
        if event.site not in banks:
            raise LedgerIntegrityError(f"event references unregistered site {event.site}")
        try:
            event_time = datetime.fromisoformat(event.ts)
            clocks[event.site][0] = event_time
        except ValueError as error:
            raise LedgerIntegrityError(f"event #{event.seq} at {event.site} has an invalid timestamp") from error

        bank = banks[event.site]
        bank.log.device = event.device
        previous_count = len(bank.log)
        payload = event.payload
        din = event.unit_id

        try:
            if event.etype == "DonorScreened":
                bank.log.append_saved(event)
            elif event.etype == "UnitCollected" and din:
                bank.collect(
                    din,
                    payload["donor"],
                    payload["component"],
                    payload["abo_rh"],
                    event.actor,
                    screened_ok=True,
                    collected_at=datetime.fromisoformat(payload["collected"]),
                    expires_at=datetime.fromisoformat(payload["expires"]),
                )
            elif event.etype == "TestResultRecorded" and din:
                if payload["marker"] == "ABO_RH":
                    bank.record_typing(din, payload["abo_rh"], event.actor)
                else:
                    bank.record_test(din, payload["marker"], payload["result"], event.actor)
            elif event.etype == "UnitReleased" and din:
                bank.release(din, event.actor, payload["second_signature"])
            elif event.etype == "UnitDiscarded" and din:
                unit = bank.units.get(din)
                if payload.get("state") == State.EXPIRED.value:
                    if not bank._expire_unit(din, event.actor, event_time):
                        raise GateViolation("expired-unit event does not match the current state")
                else:
                    bank.discard(din, payload["reason"], event.actor)
            elif event.etype == "TemperatureExcursionFlagged" and din:
                bank.flag_excursion([din], event.actor, payload["detail"])
            elif event.etype == "UnitReserved" and din:
                bank.reserve(din, payload["patient"], payload["group"], True, event.actor)
            elif event.etype == "UnitIssued" and din:
                bank.issue(din, event.actor)
            elif event.etype == "UnitReturned" and din:
                bank.return_unit(din, payload["accepted"], event.actor)
            elif event.etype == "TransfusionStarted" and din:
                unit = bank.units.get(din)
                if unit is None or unit.reserved_for is None:
                    raise GateViolation("transfusion event has no matching reservation")
                bank.transfuse(din, unit.reserved_for, din, event.actor, payload["second_check"])
            elif event.etype == "AdverseEventReported" and din:
                bank.report_adverse_event(din, payload["severity"], event.actor, payload.get("detail", ""))
            elif event.etype == "CustodyTransferred" and din:
                if payload["phase"] == "dispatched":
                    destination = payload["to"]
                    if destination not in banks:
                        clocks[destination] = [event_time]
                        banks[destination] = BloodBank(
                            destination,
                            log=EventLog(site=destination, clock=lambda clock=clocks[destination]: clock[0]),
                            clock=lambda clock=clocks[destination]: clock[0],
                        )
                        store.register_site(destination)
                    bank.dispatch(din, destination, event.actor)
                elif payload["phase"] == "received":
                    sender = next(
                        (
                            candidate
                            for candidate in banks.values()
                            if din in candidate.units
                            and candidate.units[din].state == State.IN_TRANSIT
                            and candidate.units[din].dispatched_to == event.site
                        ),
                        None,
                    )
                    if sender is None:
                        raise GateViolation("receipt event has no matching dispatched unit")
                    bank.receive(din, sender, event.actor, temp_ok=payload["temp_ok"])
                else:
                    raise GateViolation("custody event has an unknown phase")
            else:
                raise GateViolation(f"event {event.etype} is missing required unit data")
        except (GateViolation, KeyError, TypeError, ValueError) as error:
            raise LedgerIntegrityError(
                f"event #{event.seq} at {event.site} cannot be replayed: {error}"
            ) from error

        generated = bank.log.events[previous_count:]
        if len(generated) != 1 or generated[0] != event:
            raise LedgerIntegrityError(f"replayed event #{event.seq} at {event.site} does not match its record")

    for site in sites:
        store.register_site(site)
    for bank in banks.values():
        bank.log._store = store
    return banks


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
    typing_actors: List[str] = field(default_factory=list)
    reserved_for: Optional[str] = None
    issued_at: Optional[datetime] = None
    dispatched_to: Optional[str] = None


class BloodBank:
    """One facility's view. Every method either changes state *and* logs, or raises GateViolation."""

    def __init__(
        self,
        site: str,
        log: Optional[EventLog] = None,
        clock=None,
        store: Optional[SQLiteEventStore] = None,
    ):
        self.site = site
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self.log = log or EventLog(site=site, clock=self._clock, store=store)
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
    def screen_donor(
        self,
        donor_id: str,
        age: int,
        weight_kg: float,
        hb: float,
        sex: str,
        actor: str,
        *,
        screened_at: Optional[datetime] = None,
    ) -> bool:
        r, ok, why = CONFIG["donor_rules"], True, []
        now = screened_at or self.now()
        if not r["min_age"] <= age <= r["max_age"]:
            ok, why = False, why + ["age"]
        if weight_kg < r["min_weight_kg"]:
            ok, why = False, why + ["weight"]
        if hb < r["min_hb"]:
            ok, why = False, why + ["haemoglobin"]
        gap = r["interval_days_male"] if sex.upper() == "M" else r["interval_days_female"]
        last = self.last_donation.get(donor_id)
        if last and (now - last).days < gap:
            ok, why = False, why + ["too soon since last donation"]
        self.log.append("DonorScreened", None, actor,
                        dict(donor=donor_id, eligible=ok, reasons=why), timestamp=now)   # reasons, never diagnoses
        return ok

    # ---- GATE 2: collected, born in quarantine ---------------------------
    def collect(
        self,
        din: str,
        donor_id: str,
        component: str,
        abo_rh: str,
        actor: str,
        screened_ok: bool,
        *,
        collected_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
    ) -> Unit:
        if not screened_ok:
            raise GateViolation("Gate 1: donor has not passed screening")
        if din in self.units:
            raise GateViolation("duplicate donation number")
        now = collected_at or self.now()
        expiry = expires_at or now + timedelta(days=CONFIG["shelf_life_days"][component])
        u = Unit(din, component, abo_rh, now, expiry, self.site)
        self.log.append(
            "UnitCollected",
            din,
            actor,
            dict(
                donor=donor_id,
                component=component,
                abo_rh=abo_rh,
                collected=now.isoformat(),
                expires=expiry.isoformat(),
                state="QUARANTINE",
            ),
            timestamp=now,
        )
        self.units[din] = u
        self.last_donation[donor_id] = now
        return u

    # ---- GATE 3: tested ----------------------------------------------------
    def record_test(self, din: str, marker: str, result: str, actor: str) -> None:
        u = self._unit(din)
        if u.state != State.QUARANTINE:
            raise GateViolation("tests are recorded only while a unit is in quarantine")
        self.log.append("TestResultRecorded", din, actor, dict(marker=marker, result=result))
        u.tests[marker] = result

    def record_typing(self, din: str, abo_rh: str, actor: str) -> None:
        u = self._unit(din)
        if actor in u.typing_actors:
            raise GateViolation("Gate 3: ABO/Rh determinations must be performed by different people")
        typing_count = len(u.typings) + 1
        self.log.append("TestResultRecorded", din, actor, dict(marker="ABO_RH", abo_rh=abo_rh, n=typing_count))
        u.typings.append(abo_rh)
        u.typing_actors.append(actor)

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
        if (len(u.typings) < 2 or len(set(u.typings)) != 1 or u.typings[0] != u.abo_rh
                or len(set(u.typing_actors)) < 2):
            raise GateViolation("Gate 3: ABO/Rh needs two matching independent determinations")
        now = self.now()
        if u.expires <= now:
            raise GateViolation("unit is already expired")
        self.log.append("UnitReleased", din, tech, dict(second_signature=supervisor), timestamp=now)
        u.state = State.RELEASED

    def discard(self, din: str, reason: str, actor: str) -> None:
        u = self._unit(din)
        self.log.append("UnitDiscarded", din, actor, dict(reason=reason, state=State.DISCARDED.value))
        u.state = State.DISCARDED

    # ---- GATE 5: cold chain -------------------------------------------------
    def flag_excursion(self, dins: List[str], actor: str, detail: str) -> None:
        for d in dins:
            u = self._unit(d)
            self.log.append("TemperatureExcursionFlagged", d, actor, dict(detail=detail, state="HOLD"))
            if u.state in (State.RELEASED, State.RESERVED):
                u.state = State.HOLD

    # ---- GATE 6: matched (hard stop) ---------------------------------------
    def reserve(self, din: str, patient_id: str, patient_group: str, two_sample_confirmed: bool, actor: str) -> None:
        u = self._unit(din)
        if u.state != State.RELEASED:
            raise GateViolation(f"Gate 4/6: only RELEASED units can be matched (this one is {u.state.value})")
        if not two_sample_confirmed:
            raise GateViolation("Gate 6: patient group must be confirmed on two independent samples")
        if not compatible(u.component, u.abo_rh, patient_group):
            raise GateViolation(f"Gate 6 HARD STOP: {u.abo_rh} {u.component} is incompatible with {patient_group}")
        now = self.now()
        if u.expires <= now:
            raise GateViolation("unit expired")
        self.log.append("UnitReserved", din, actor, dict(patient=patient_id, group=patient_group), timestamp=now)
        u.state, u.reserved_for = State.RESERVED, patient_id

    def issue(self, din: str, actor: str) -> None:
        u = self._unit(din)
        if u.state != State.RESERVED:
            raise GateViolation("only RESERVED units can be issued")
        issued_at = self.now()
        self.log.append("UnitIssued", din, actor, {}, timestamp=issued_at)
        u.state, u.issued_at = State.ISSUED, issued_at

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
        now = self.now()
        minutes = (now - u.issued_at).total_seconds() / 60
        if minutes > CONFIG["max_minutes_out_of_storage"]:
            raise GateViolation(f"unit has been out of storage {minutes:.0f} min: return or discard per policy")
        self.log.append(
            "TransfusionStarted",
            din,
            nurse1,
            dict(second_check=nurse2, minutes_out=round(minutes, 1)),
            timestamp=now,
        )
        u.state = State.TRANSFUSED

    def return_unit(self, din: str, temp_ok: bool, actor: str) -> None:
        u = self._unit(din)
        if u.state != State.ISSUED:
            raise GateViolation("only ISSUED units can be returned")
        now = self.now()
        minutes = (now - u.issued_at).total_seconds() / 60
        if temp_ok and minutes <= CONFIG["max_minutes_out_of_storage"]:
            self.log.append(
                "UnitReturned",
                din,
                actor,
                dict(accepted=True, minutes_out=round(minutes, 1)),
                timestamp=now,
            )
            u.state, u.reserved_for, u.issued_at = State.RELEASED, None, None
        else:
            self.log.append(
                "UnitReturned",
                din,
                actor,
                dict(accepted=False, minutes_out=round(minutes, 1)),
                timestamp=now,
            )
            u.state = State.DISCARDED

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
        self.log.append("CustodyTransferred", din, actor, dict(phase="dispatched", to=to_site))
        u.state, u.dispatched_to = State.IN_TRANSIT, to_site

    def receive(self, din: str, from_bank: "BloodBank", actor: str, temp_ok: bool = True) -> None:
        u = from_bank.units.get(din)
        if u is None or u.state != State.IN_TRANSIT or u.dispatched_to != self.site:
            raise GateViolation("custody: nothing was dispatched to this site for that unit")
        resulting_state = State.RELEASED if temp_ok else State.HOLD
        self.log.append("CustodyTransferred", din, actor, dict(phase="received", temp_ok=temp_ok, state=resulting_state.value))
        u.site, u.dispatched_to = self.site, None
        u.state = resulting_state
        self.units[din] = u
        del from_bank.units[din]

    # ---- Housekeeping ---------------------------------------------------------------
    def expire_sweep(self, actor: str = "system") -> List[str]:
        now = self.now()
        return [din for din in list(self.units) if self._expire_unit(din, actor, now)]

    def _expire_unit(self, din: str, actor: str, now: datetime) -> bool:
        unit = self.units.get(din)
        if unit is None:
            raise GateViolation(f"unknown unit {din}")
        if unit.state in TERMINAL or unit.expires > now:
            return False
        self.log.append(
            "UnitDiscarded",
            din,
            actor,
            dict(reason="expired", state=State.EXPIRED.value),
            timestamp=now,
        )
        unit.state = State.EXPIRED
        return True

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

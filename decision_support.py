from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import sqlite3
from contextlib import closing
from typing import Any, Dict, Mapping, Optional
from uuid import uuid4

from hemosync_core import ABO_RH, BloodBank, CONFIG, State, stock_light


AUDIT_GENESIS = "0" * 64
FINAL_DECISIONS = ("approved", "overridden", "approval_failed")


def _canonical_json(value: Mapping[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _decision_hash(previous_hash: str, body: Mapping[str, Any]) -> str:
    return hashlib.sha256((previous_hash + _canonical_json(body)).encode("utf-8")).hexdigest()


def build_transfer_suggestion(
    banks: Mapping[str, BloodBank],
    *,
    from_site: str,
    to_site: str,
    component: str,
    group: str,
    source_mean_daily_use: float,
    source_lead_days: float,
    target_mean_daily_use: float,
    target_lead_days: float,
    z: float = 1.96,
) -> Dict[str, Any]:
    if from_site == to_site:
        raise ValueError("source and destination facilities must be different")
    if from_site not in banks or to_site not in banks:
        raise ValueError("source and destination must be registered facilities")
    if group not in ABO_RH:
        raise ValueError(f"unknown ABO/Rh group {group}")
    if component not in CONFIG["shelf_life_days"]:
        raise ValueError(f"unknown component {component}")
    metrics = (
        source_mean_daily_use,
        source_lead_days,
        target_mean_daily_use,
        target_lead_days,
        z,
    )
    if any(not math.isfinite(value) or value < 0 for value in metrics) or z == 0:
        raise ValueError("facility use, lead time, and service factor must be finite and non-negative; z must be positive")

    source = banks[from_site]
    target = banks[to_site]
    source_count = source.on_hand(component, group)
    target_count = target.on_hand(component, group)
    source_colour, source_cover, source_reorder_point = stock_light(
        source_count, source_mean_daily_use, source_lead_days, z
    )
    target_colour, target_cover, target_reorder_point = stock_light(
        target_count, target_mean_daily_use, target_lead_days, z
    )
    if not all(
        math.isfinite(value)
        for value in (source_cover, source_reorder_point, target_cover, target_reorder_point)
    ):
        raise ValueError("facility inputs produce a non-finite stock estimate")
    safe_surplus = max(0, math.floor(source_count - source_reorder_point))
    destination_gap = max(0, math.ceil(target_reorder_point - target_count))
    eligible_units = sorted(
        (
            unit for unit in source.units.values()
            if unit.state == State.RELEASED
            and unit.component == component
            and unit.abo_rh == group
            and unit.expires > source.now()
        ),
        key=lambda unit: (unit.expires, unit.din),
    )

    reason = "destination_stock_adequate"
    candidate = None
    status = "no_recommendation"
    if target_colour != "GREEN" and destination_gap > 0:
        reason = "source_below_reserve" if safe_surplus == 0 else "no_released_matching_unit"
        if safe_surplus > 0 and eligible_units:
            unit = eligible_units[0]
            candidate = {
                "din": unit.din,
                "component": unit.component,
                "abo_rh": unit.abo_rh,
                "expires": unit.expires.isoformat(),
                "days_left": max(0, math.ceil((unit.expires - source.now()).total_seconds() / 86400)),
            }
            reason = "destination_below_reorder_point"
            status = "recommended"

    return {
        "recommendation_id": str(uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "reason": reason,
        "from_site": from_site,
        "to_site": to_site,
        "component": component,
        "group": group,
        "z": z,
        "source": {
            "on_hand": source_count,
            "colour": source_colour,
            "cover": source_cover,
            "reorder_point": source_reorder_point,
            "safe_surplus": safe_surplus,
            "mean_daily_use": source_mean_daily_use,
            "lead_days": source_lead_days,
        },
        "destination": {
            "on_hand": target_count,
            "colour": target_colour,
            "cover": target_cover,
            "reorder_point": target_reorder_point,
            "gap_to_reorder_point": destination_gap,
            "mean_daily_use": target_mean_daily_use,
            "lead_days": target_lead_days,
        },
        "candidate_unit": candidate,
        "basis": [
            "Uses current API inventory and facility-entered mean daily use and delivery lead time.",
            "Considers only released, unexpired units of the exact requested component and ABO/Rh group.",
            "Suggests at most one unit, selected FEFO, and only when the source remains at or above its calculated reorder point.",
            "A GREEN/AMBER/RED light is a stock-planning estimate, not a clinical compatibility or transfusion decision.",
        ],
        "limitations": [
            "No trained predictive model, live demand feed, transport-time estimate, or temperature telemetry is used.",
            "The destination must independently verify local need, transport feasibility, and policy before approval.",
        ],
    }


class TransferDecisionAuditStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.path)) as connection:
            with connection:
                connection.execute(
                    """
                    CREATE TABLE IF NOT EXISTS transfer_decision_audit (
                        seq INTEGER PRIMARY KEY,
                        occurred_at TEXT NOT NULL,
                        recommendation_id TEXT NOT NULL,
                        event_type TEXT NOT NULL,
                        actor TEXT NOT NULL,
                        details TEXT NOT NULL,
                        prev_hash TEXT NOT NULL,
                        hash TEXT NOT NULL,
                        UNIQUE(recommendation_id, event_type)
                    )
                    """
                )
                connection.execute(
                    """
                    CREATE TRIGGER IF NOT EXISTS transfer_decision_audit_no_update
                    BEFORE UPDATE ON transfer_decision_audit
                    BEGIN SELECT RAISE(ABORT, 'transfer decision audit is append-only'); END
                    """
                )
                connection.execute(
                    """
                    CREATE TRIGGER IF NOT EXISTS transfer_decision_audit_no_delete
                    BEFORE DELETE ON transfer_decision_audit
                    BEGIN SELECT RAISE(ABORT, 'transfer decision audit is append-only'); END
                    """
                )
        if not self.verify():
            raise ValueError("transfer decision audit hash chain is invalid")

    def append(
        self,
        recommendation_id: str,
        event_type: str,
        actor: str,
        details: Mapping[str, Any],
    ) -> None:
        if not self.verify():
            raise ValueError("transfer decision audit hash chain is invalid")
        connection = sqlite3.connect(self.path, timeout=30)
        try:
            with connection:
                connection.execute("BEGIN IMMEDIATE")
                if event_type == "suggested":
                    existing = connection.execute(
                        "SELECT 1 FROM transfer_decision_audit WHERE recommendation_id = ?",
                        (recommendation_id,),
                    ).fetchone()
                    if existing:
                        raise ValueError("recommendation already exists")
                elif event_type in FINAL_DECISIONS:
                    existing = connection.execute(
                        "SELECT 1 FROM transfer_decision_audit WHERE recommendation_id = ? AND event_type IN (?, ?, ?)",
                        (recommendation_id, *FINAL_DECISIONS),
                    ).fetchone()
                    if existing:
                        raise ValueError("this recommendation already has a recorded decision")
                    suggestion = connection.execute(
                        "SELECT 1 FROM transfer_decision_audit WHERE recommendation_id = ? AND event_type = 'suggested'",
                        (recommendation_id,),
                    ).fetchone()
                    if not suggestion:
                        raise ValueError("recommendation was not found")
                else:
                    raise ValueError(f"unsupported decision audit event {event_type}")

                previous = connection.execute(
                    "SELECT seq, hash FROM transfer_decision_audit ORDER BY seq DESC LIMIT 1"
                ).fetchone()
                seq = previous[0] + 1 if previous else 0
                prev_hash = previous[1] if previous else AUDIT_GENESIS
                occurred_at = datetime.now(timezone.utc).isoformat()
                encoded_details = _canonical_json(details)
                body = {
                    "seq": seq,
                    "occurred_at": occurred_at,
                    "recommendation_id": recommendation_id,
                    "event_type": event_type,
                    "actor": actor,
                    "details": json.loads(encoded_details),
                }
                digest = _decision_hash(prev_hash, body)
                connection.execute(
                    """
                    INSERT INTO transfer_decision_audit
                        (seq, occurred_at, recommendation_id, event_type, actor, details, prev_hash, hash)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (seq, occurred_at, recommendation_id, event_type, actor, encoded_details, prev_hash, digest),
                )
        finally:
            connection.close()

    def recommendation(self, recommendation_id: str) -> Optional[Dict[str, Any]]:
        if not self.verify():
            raise ValueError("transfer decision audit hash chain is invalid")
        with closing(sqlite3.connect(self.path)) as connection:
            row = connection.execute(
                """
                SELECT details FROM transfer_decision_audit
                WHERE recommendation_id = ? AND event_type = 'suggested'
                """,
                (recommendation_id,),
            ).fetchone()
        if row is None:
            return None
        return json.loads(row[0])["suggestion"]

    def has_decision(self, recommendation_id: str) -> bool:
        with closing(sqlite3.connect(self.path)) as connection:
            return connection.execute(
                """
                SELECT 1 FROM transfer_decision_audit
                WHERE recommendation_id = ? AND event_type IN (?, ?, ?)
                """,
                (recommendation_id, *FINAL_DECISIONS),
            ).fetchone() is not None

    def events(self) -> list[Dict[str, Any]]:
        with closing(sqlite3.connect(self.path)) as connection:
            rows = connection.execute(
                """
                SELECT seq, occurred_at, recommendation_id, event_type, actor, details, prev_hash, hash
                FROM transfer_decision_audit ORDER BY seq
                """
            ).fetchall()
        return [
            {
                "seq": row[0],
                "occurred_at": row[1],
                "recommendation_id": row[2],
                "event_type": row[3],
                "actor": row[4],
                "details": json.loads(row[5]),
                "prev_hash": row[6],
                "hash": row[7],
            }
            for row in rows
        ]

    def verify(self) -> bool:
        events = self.events()
        previous_hash = AUDIT_GENESIS
        for expected_seq, event in enumerate(events):
            body = {
                "seq": event["seq"],
                "occurred_at": event["occurred_at"],
                "recommendation_id": event["recommendation_id"],
                "event_type": event["event_type"],
                "actor": event["actor"],
                "details": event["details"],
            }
            if (
                event["seq"] != expected_seq
                or event["prev_hash"] != previous_hash
                or event["hash"] != _decision_hash(previous_hash, body)
            ):
                return False
            previous_hash = event["hash"]
        return True

from __future__ import annotations

from datetime import timedelta
import ipaddress
import os
from pathlib import Path
from typing import Any, Awaitable, Callable, Dict, List, Literal, Optional
from urllib.parse import urlsplit

from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from starlette.staticfiles import StaticFiles

from decision_support import TransferDecisionAuditStore, build_transfer_suggestion
from hemosync_core import (
    BloodBank,
    CONFIG,
    GateViolation,
    SQLiteEventStore,
    State,
    restore_banks,
    stock_light,
)

app = FastAPI(title="HemoSync API", version="0.1.0")
WEB_DIR = Path(__file__).parent / "web"
DATABASE_PATH = Path(
    os.environ.get("HEMOSYNC_DB_PATH", str(Path(__file__).parent / "data" / "hemosync.sqlite3"))
)
EVENT_STORE = SQLiteEventStore(DATABASE_PATH)
DECISION_AUDIT = TransferDecisionAuditStore(DATABASE_PATH)

# Stored events are verified and replayed before the API accepts requests.
BANKS: Dict[str, BloodBank] = restore_banks(EVENT_STORE, initial_sites=("API-SITE",))


def is_loopback_client(host: Optional[str]) -> bool:
    if host is None:
        return False
    try:
        return ipaddress.ip_address(host).is_loopback
    except ValueError:
        return False


def is_loopback_host(host_header: Optional[str]) -> bool:
    if not host_header:
        return False
    try:
        parsed = urlsplit(f"//{host_header}")
        host = parsed.hostname
        parsed.port
    except ValueError:
        return False
    if (
        host is None
        or parsed.username is not None
        or parsed.password is not None
        or parsed.path
        or parsed.query
        or parsed.fragment
    ):
        return False
    return host.lower() == "localhost" or is_loopback_client(host)


def is_same_origin(request: Request, origin: Optional[str]) -> bool:
    if origin is None:
        return True
    try:
        parsed = urlsplit(origin)
        origin_host = parsed.hostname
        origin_port = parsed.port
        request_host = request.url.hostname
        request_port = request.url.port
    except ValueError:
        return False
    if (
        parsed.username is not None
        or parsed.password is not None
        or parsed.path
        or parsed.query
        or parsed.fragment
        or not parsed.scheme
        or origin_host is None
        or request_host is None
        or not is_loopback_host(parsed.netloc)
        or parsed.scheme.lower() != request.url.scheme.lower()
    ):
        return False
    default_ports = {"http": 80, "https": 443}
    origin_effective_port = (
        origin_port if origin_port is not None else default_ports.get(parsed.scheme.lower())
    )
    request_effective_port = (
        request_port
        if request_port is not None
        else default_ports.get(request.url.scheme.lower())
    )
    return (
        origin_host.lower() == request_host.lower()
        and origin_effective_port == request_effective_port
    )


@app.middleware("http")
async def restrict_to_loopback(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    client_host = request.client.host if request.client else None
    request_host = request.headers.get("host")
    if not is_loopback_client(client_host) or not is_loopback_host(request_host):
        return JSONResponse(
            status_code=403,
            content={"detail": "This synthetic demo is available only from this device."},
        )
    if request.method not in {"GET", "HEAD", "OPTIONS"} and not is_same_origin(
        request, request.headers.get("origin")
    ):
        return JSONResponse(
            status_code=403,
            content={"detail": "Cross-origin changes are not allowed."},
        )
    return await call_next(request)


def _bank_for(site: str) -> BloodBank:
    bank = BANKS.get(site)
    if bank is None:
        raise GateViolation(f"unknown site {site}")
    return bank


def _get_or_create_bank(site: str) -> BloodBank:
    bank = BANKS.get(site)
    if bank is None:
        EVENT_STORE.register_site(site)
        bank = BloodBank(site, store=EVENT_STORE)
        BANKS[site] = bank
    return bank


def _serialize_unit(unit: Any) -> Dict[str, Any]:
    return {
        "din": unit.din,
        "component": unit.component,
        "abo_rh": unit.abo_rh,
        "collected": unit.collected.isoformat(),
        "expires": unit.expires.isoformat(),
        "site": unit.site,
        "state": unit.state.value,
        "tests": unit.tests,
        "typings": unit.typings,
        "typing_actors": unit.typing_actors,
        "reserved_for": unit.reserved_for,
        "issued_at": unit.issued_at.isoformat() if unit.issued_at else None,
        "dispatched_to": unit.dispatched_to,
    }


@app.exception_handler(GateViolation)
async def gate_violation_handler(_, exc: GateViolation):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


@app.exception_handler(ValueError)
async def value_error_handler(_, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})


class ScreeningRequest(BaseModel):
    donor_id: str
    age: int
    weight_kg: float
    hb: float
    sex: str
    actor: str


class CollectRequest(BaseModel):
    din: str
    donor_id: str
    component: str
    abo_rh: str
    actor: str
    screened_ok: bool


class MarkerTestRequest(BaseModel):
    marker: str
    result: str
    actor: str


class TypingRequest(BaseModel):
    abo_rh: str
    actor: str


class ReleaseRequest(BaseModel):
    tech: str
    supervisor: str


class DiscardRequest(BaseModel):
    reason: str
    actor: str


class ExcursionRequest(BaseModel):
    dins: List[str]
    actor: str
    detail: str = ""


class ReserveRequest(BaseModel):
    patient_id: str
    patient_group: str
    two_sample_confirmed: bool
    actor: str


class IssueRequest(BaseModel):
    actor: str


class TransfusionRequest(BaseModel):
    scanned_patient: str
    scanned_unit: str
    nurse1: str
    nurse2: str


class ReturnRequest(BaseModel):
    temp_ok: bool
    actor: str


class AdverseEventRequest(BaseModel):
    severity: str
    actor: str
    detail: str = ""


class DispatchRequest(BaseModel):
    to_site: str
    actor: str


class ReceiveRequest(BaseModel):
    from_site: str
    to_site: str = "API-SITE"
    actor: str
    temp_ok: bool = True


class StockLightRequest(BaseModel):
    on_hand: int
    mean_daily_use: float
    lead_days: float
    z: float = 1.96


class TransferSuggestionRequest(BaseModel):
    from_site: str
    to_site: str
    component: str
    group: str
    source_mean_daily_use: float = Field(ge=0)
    source_lead_days: float = Field(ge=0)
    target_mean_daily_use: float = Field(ge=0)
    target_lead_days: float = Field(ge=0)
    z: float = Field(default=1.96, gt=0)


class TransferDecisionRequest(BaseModel):
    decision: Literal["approve", "override"]
    actor: str = Field(min_length=1, max_length=128)
    reason: str = Field(default="", max_length=300)


@app.get("/health")
def health() -> Dict[str, Any]:
    return {"ok": True, "site": "API-SITE", "registered_sites": sorted(BANKS.keys()), "units": len(BANKS["API-SITE"].units)}


@app.get("/demo/encounters")
def demo_encounters() -> Dict[str, Any]:
    return {
        "synthetic": True,
        "encounters": [
            {"id": "P-7788", "bed": 1, "blood_group": "O+"},
            {"id": "P-7789", "bed": 2, "blood_group": "A+"},
            {"id": "P-7790", "bed": 3, "blood_group": "B+"},
            {"id": "P-7791", "bed": 4, "blood_group": "O-"},
            {"id": "P-7792", "bed": 5, "blood_group": "AB+"},
        ],
    }


@app.get("/")
def frontend():
    return FileResponse(
        WEB_DIR / "index.html",
        headers={"Cache-Control": "no-cache"},
    )


@app.get("/sw.js", include_in_schema=False)
def service_worker() -> FileResponse:
    return FileResponse(
        WEB_DIR / "sw.js",
        media_type="text/javascript",
        headers={"Service-Worker-Allowed": "/", "Cache-Control": "no-cache"},
    )


@app.get("/policy")
def policy() -> Dict[str, Any]:
    return {
        "required_markers": list(CONFIG["required_markers"]),
        "max_minutes_out_of_storage": CONFIG["max_minutes_out_of_storage"],
    }


@app.get("/ledger")
def ledger() -> Dict[str, Any]:
    events = EVENT_STORE.load_events()
    return {
        "count": len(events),
        "sites": sorted(BANKS),
        "events": [
            {
                "seq": event.seq,
                "etype": event.etype,
                "unit_id": event.unit_id,
                "actor": event.actor,
                "site": event.site,
                "device": event.device,
                "ts": event.ts,
                "payload": event.payload,
                "prev_hash": event.prev_hash,
                "hash": event.hash,
            }
            for event in events
        ],
    }


@app.get("/ledger/verify")
def verify_ledger() -> Dict[str, Any]:
    checks = EVENT_STORE.verify()
    sites = {
        site: {"valid": valid, "first_bad_event": first_bad_event}
        for site, (valid, first_bad_event) in checks.items()
    }
    invalid = {site: result for site, result in sites.items() if not result["valid"]}
    return {
        "valid": not invalid,
        "first_bad_event": next(iter(invalid.values()))["first_bad_event"] if invalid else None,
        "sites": sites,
    }


@app.post("/demo/reset")
def reset_demo() -> Dict[str, Any]:
    bank = _bank_for("API-SITE")
    _get_or_create_bank("HOMA-BAY")
    story_units = (
        ("A999926004821", "DEMO-DONOR-01", "O+", False, 2),
        ("A999926004822", "DEMO-DONOR-02", "O-", True, 4),
        ("A999926004823", "DEMO-DONOR-03", "A+", True, 11),
        ("A999926004824", "DEMO-DONOR-04", "B+", True, 21),
        ("A999926004825", "DEMO-DONOR-05", "O+", True, 29),
        ("A999926004826", "DEMO-DONOR-06", "A+", True, 16),
        ("A999926004827", "DEMO-DONOR-07", "B+", True, 7),
    )
    previous_event_count = len(EVENT_STORE.load_events())

    def add_unit(din: str, donor_id: str, group: str, released: bool, age_days: int) -> None:
        unit = bank.units.get(din)
        if unit is None:
            collected_at = bank.now() - timedelta(days=age_days)
            eligible = bank.screen_donor(
                donor_id,
                25,
                65,
                13.5,
                "F",
                "demo.screen",
                screened_at=collected_at,
            )
            unit = bank.collect(
                din,
                donor_id,
                "RBC",
                group,
                "demo.collect",
                eligible,
                collected_at=collected_at,
            )
        if released and unit.state == State.QUARANTINE:
            for marker in CONFIG["required_markers"]:
                if marker not in unit.tests:
                    bank.record_test(unit.din, marker, "NEG", "demo.lab")
            for actor in ("demo.lab", "demo.check"):
                if actor not in unit.typing_actors:
                    bank.record_typing(unit.din, group, actor)
            if unit.state == State.QUARANTINE:
                bank.release(unit.din, "demo.lab", "demo.supervisor")

    for story_unit in story_units:
        add_unit(*story_unit)
    already_loaded = len(EVENT_STORE.load_events()) == previous_event_count
    return {
        "ok": True,
        "synthetic": True,
        "already_loaded": already_loaded,
        "site": bank.site,
        "units": len(bank.units),
        "story_unit_id": "A999926004821",
    }


@app.post("/sites/{site}")
def create_site(site: str) -> Dict[str, Any]:
    created = site not in BANKS
    _get_or_create_bank(site)
    return {"site": site, "created": created}


@app.get("/units")
def list_units() -> Dict[str, Any]:
    bank = BANKS["API-SITE"]
    return {"site": bank.site, "count": len(bank.units), "units": [_serialize_unit(u) for u in bank.units.values()]}


@app.get("/sites/inventory")
def site_inventory() -> Dict[str, Any]:
    counts: Dict[str, Dict[str, int]] = {}
    for site, bank in BANKS.items():
        counts[site] = {}
        for unit in bank.units.values():
            if unit.state != State.RELEASED or unit.expires <= bank.now():
                continue
            group_counts = counts.setdefault(site, {})
            group_counts[unit.abo_rh] = group_counts.get(unit.abo_rh, 0) + 1
    return {"sites": [{"site": site, "on_hand": groups} for site, groups in sorted(counts.items())]}


@app.get("/sites/{site}/units")
def site_units(site: str) -> Dict[str, Any]:
    bank = _bank_for(site)
    return {
        "site": site,
        "count": len(bank.units),
        "units": [_serialize_unit(unit) for unit in bank.units.values()],
    }


@app.get("/units/{din}")
def get_unit(din: str) -> Dict[str, Any]:
    bank = BANKS["API-SITE"]
    if din not in bank.units:
        raise GateViolation(f"unknown unit {din}")
    return _serialize_unit(bank.units[din])


@app.post("/screen_donor")
def screen_donor(request: ScreeningRequest) -> Dict[str, Any]:
    bank = BANKS["API-SITE"]
    eligible = bank.screen_donor(request.donor_id, request.age, request.weight_kg, request.hb, request.sex, request.actor)
    return {"donor_id": request.donor_id, "eligible": eligible}


@app.post("/collect")
def collect(request: CollectRequest) -> Dict[str, Any]:
    bank = BANKS["API-SITE"]
    unit = bank.collect(request.din, request.donor_id, request.component, request.abo_rh, request.actor, request.screened_ok)
    return _serialize_unit(unit)


@app.post("/units/{din}/record_test")
def record_test(din: str, request: MarkerTestRequest) -> Dict[str, Any]:
    bank = BANKS["API-SITE"]
    bank.record_test(din, request.marker, request.result, request.actor)
    return {"ok": True, "din": din, "marker": request.marker, "result": request.result}


@app.post("/units/{din}/record_typing")
def record_typing(din: str, request: TypingRequest) -> Dict[str, Any]:
    bank = BANKS["API-SITE"]
    bank.record_typing(din, request.abo_rh, request.actor)
    return {"ok": True, "din": din, "abo_rh": request.abo_rh}


@app.post("/units/{din}/release")
def release(din: str, request: ReleaseRequest) -> Dict[str, Any]:
    bank = BANKS["API-SITE"]
    bank.release(din, request.tech, request.supervisor)
    return {"ok": True, "din": din, "state": bank.units[din].state.value}


@app.post("/units/{din}/discard")
def discard(din: str, request: DiscardRequest) -> Dict[str, Any]:
    bank = BANKS["API-SITE"]
    bank.discard(din, request.reason, request.actor)
    return {"ok": True, "din": din, "state": bank.units[din].state.value}


@app.post("/units/flag_excursion")
def flag_excursion(request: ExcursionRequest) -> Dict[str, Any]:
    bank = BANKS["API-SITE"]
    bank.flag_excursion(request.dins, request.actor, request.detail)
    return {"ok": True, "updated": request.dins}


@app.post("/units/{din}/reserve")
def reserve(din: str, request: ReserveRequest) -> Dict[str, Any]:
    bank = BANKS["API-SITE"]
    bank.reserve(din, request.patient_id, request.patient_group, request.two_sample_confirmed, request.actor)
    return {"ok": True, "din": din, "state": bank.units[din].state.value, "reserved_for": bank.units[din].reserved_for}


@app.post("/units/{din}/issue")
def issue(din: str, request: IssueRequest) -> Dict[str, Any]:
    bank = BANKS["API-SITE"]
    bank.issue(din, request.actor)
    return {"ok": True, "din": din, "state": bank.units[din].state.value}


@app.post("/units/{din}/transfuse")
def transfuse(din: str, request: TransfusionRequest) -> Dict[str, Any]:
    bank = BANKS["API-SITE"]
    bank.transfuse(din, request.scanned_patient, request.scanned_unit, request.nurse1, request.nurse2)
    return {"ok": True, "din": din, "state": bank.units[din].state.value}


@app.post("/units/{din}/return")
def return_unit(din: str, request: ReturnRequest) -> Dict[str, Any]:
    bank = BANKS["API-SITE"]
    bank.return_unit(din, request.temp_ok, request.actor)
    return {"ok": True, "din": din, "state": bank.units[din].state.value}


@app.post("/units/{din}/report_adverse_event")
def report_adverse_event(din: str, request: AdverseEventRequest) -> Dict[str, Any]:
    bank = BANKS["API-SITE"]
    bank.report_adverse_event(din, request.severity, request.actor, request.detail)
    return {"ok": True, "din": din, "severity": request.severity}


@app.post("/units/{din}/dispatch")
def dispatch(din: str, request: DispatchRequest) -> Dict[str, Any]:
    bank = BANKS["API-SITE"]
    bank.dispatch(din, request.to_site, request.actor)
    return {"ok": True, "din": din, "state": bank.units[din].state.value, "dispatched_to": bank.units[din].dispatched_to}


@app.post("/units/{din}/receive")
def receive(din: str, request: ReceiveRequest) -> Dict[str, Any]:
    from_bank = _bank_for(request.from_site)
    bank = _bank_for(request.to_site)
    bank.receive(din, from_bank, request.actor, temp_ok=request.temp_ok)
    return {
        "ok": True,
        "din": din,
        "state": bank.units[din].state.value,
        "site": bank.units[din].site,
        "from_site": request.from_site,
    }


@app.post("/expire_sweep")
def expire_sweep() -> Dict[str, Any]:
    bank = BANKS["API-SITE"]
    expired = bank.expire_sweep(actor="system")
    return {"ok": True, "expired": expired}


@app.get("/suggest_fefo")
def suggest_fefo(component: str, patient_group: str) -> Dict[str, Any]:
    bank = BANKS["API-SITE"]
    unit = bank.suggest_fefo(component, patient_group)
    return {"component": component, "patient_group": patient_group, "unit": _serialize_unit(unit) if unit else None}


@app.get("/on_hand")
def on_hand(component: str, group: Optional[str] = None) -> Dict[str, Any]:
    bank = BANKS["API-SITE"]
    return {"component": component, "group": group, "count": bank.on_hand(component, group)}


@app.post("/stock_light")
def stock_light_endpoint(request: StockLightRequest) -> Dict[str, Any]:
    colour, cover, reorder_point = stock_light(
        request.on_hand,
        request.mean_daily_use,
        request.lead_days,
        request.z,
    )
    return {"colour": colour, "cover": cover, "reorder_point": reorder_point}


@app.post("/decision-support/transfer-suggestions")
def create_transfer_suggestion(request: TransferSuggestionRequest) -> Dict[str, Any]:
    suggestion = build_transfer_suggestion(
        BANKS,
        from_site=request.from_site,
        to_site=request.to_site,
        component=request.component,
        group=request.group,
        source_mean_daily_use=request.source_mean_daily_use,
        source_lead_days=request.source_lead_days,
        target_mean_daily_use=request.target_mean_daily_use,
        target_lead_days=request.target_lead_days,
        z=request.z,
    )
    DECISION_AUDIT.append(
        suggestion["recommendation_id"],
        "suggested",
        "decision-support",
        {"suggestion": suggestion},
    )
    return suggestion


@app.post("/decision-support/transfer-suggestions/{recommendation_id}/decision")
def decide_transfer_suggestion(
    recommendation_id: str,
    request: TransferDecisionRequest,
) -> Dict[str, Any]:
    suggestion = DECISION_AUDIT.recommendation(recommendation_id)
    if suggestion is None:
        raise GateViolation("unknown transfer suggestion")
    if DECISION_AUDIT.has_decision(recommendation_id):
        raise GateViolation("this transfer suggestion already has a recorded decision")

    actor = request.actor.strip()
    if not actor:
        raise ValueError("an actor is required for the audit record")
    if request.decision == "override":
        reason = request.reason.strip()
        if not reason:
            raise ValueError("an override reason is required")
        DECISION_AUDIT.append(
            recommendation_id,
            "overridden",
            actor,
            {"reason": reason, "suggestion": suggestion, "unit_moved": False},
        )
        return {"ok": True, "decision": "overridden", "unit_moved": False}
    if suggestion["status"] != "recommended" or not suggestion.get("candidate_unit"):
        raise GateViolation("this suggestion has no safe unit to approve")

    from_site = suggestion["from_site"]
    to_site = suggestion["to_site"]
    din = suggestion["candidate_unit"]["din"]
    source = _bank_for(from_site)
    target = _bank_for(to_site)
    unit = source.units.get(din)
    if (
        unit is None
        or unit.state != State.RELEASED
        or unit.component != suggestion["component"]
        or unit.abo_rh != suggestion["group"]
        or unit.expires <= source.now()
    ):
        raise GateViolation("suggested unit is no longer available; request a fresh suggestion")

    source_after = source.on_hand(unit.component, unit.abo_rh) - 1
    source_colour, _, _ = stock_light(
        source_after,
        suggestion["source"]["mean_daily_use"],
        suggestion["source"]["lead_days"],
        suggestion["z"],
    )
    target_colour, _, target_reorder_point = stock_light(
        target.on_hand(unit.component, unit.abo_rh),
        suggestion["destination"]["mean_daily_use"],
        suggestion["destination"]["lead_days"],
        suggestion.get("z", 1.96),
    )
    if source_colour != "GREEN":
        raise GateViolation("source facility would fall below its calculated reorder point")
    if target_colour == "GREEN" or target.on_hand(unit.component, unit.abo_rh) >= target_reorder_point:
        raise GateViolation("destination no longer needs this stock; request a fresh suggestion")

    try:
        source.dispatch(din, to_site, actor)
    except (GateViolation, ValueError) as error:
        DECISION_AUDIT.append(
            recommendation_id,
            "approval_failed",
            actor,
            {"reason": str(error), "suggestion": suggestion, "unit_moved": False},
        )
        raise
    DECISION_AUDIT.append(
        recommendation_id,
        "approved",
        actor,
        {"reason": request.reason.strip(), "suggestion": suggestion, "unit_moved": True},
    )
    return {"ok": True, "decision": "approved", "unit_moved": True, "din": din, "to_site": to_site}


@app.get("/decision-support/audit")
def transfer_decision_audit() -> Dict[str, Any]:
    events = DECISION_AUDIT.events()
    return {
        "valid": DECISION_AUDIT.verify(),
        "count": len(events),
        "events": events,
    }


app.mount("/assets", StaticFiles(directory=WEB_DIR), name="assets")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=False)

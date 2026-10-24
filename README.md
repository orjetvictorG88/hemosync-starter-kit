# HemoSync starter kit (technical slice v0)

Everything here is **synthetic**. No real donor, patient or facility data. Not a medical device.
The core and simulation use the Python standard library. The API/web demo requires FastAPI and Uvicorn.

| File | What it proves |
|---|---|
| `hemosync_core.py` | The **Seven Gates** as code: quarantine-by-default units, dual-authorised release, hard-stop compatibility, bedside check, custody hand-shake, FEFO, math-based Red/Amber/Green stock lights, and an **append-only SHA-256 hash-chained ledger** that exposes any edit to history. |
| `decision_support.py` | Explainable stock-transfer suggestions and a separate append-only, hash-chained audit of displayed suggestions and human decisions. |
| `test_hemosync_core.py` | Core gate tests, including negative cases for safety rules. |
| `test_hemosync_persistence.py` | SQLite replay, multi-site state restoration, and tamper rejection tests. |
| `test_api_security.py` | Loopback-only API access checks for this local demo. |
| `test_decision_support.py` | Transfer recommendation safeguards, approval/override outcomes, and audit tamper detection. |
| `simulate_inventory.py` | Monte-Carlo experiments: availability vs wastage, FEFO vs careless picking, isolated vs connected hospitals, and a forecasting back-test (baseline first, prediction intervals). Writes `results.json`. |

## Run it

```bash
python hemosync_core.py              # the vein-to-vein demo + tamper test
python -m unittest -v test_hemosync_core test_hemosync_persistence test_api_security test_decision_support
python simulate_inventory.py         # ~10 seconds
python -m uvicorn api:app --host 127.0.0.1 --port 8000
```

For a repeatable judge walkthrough, use [DEMO_SCRIPT.md](./DEMO_SCRIPT.md). The current prototype is not ready for a clinical or operational pilot; see [PILOT_READINESS.md](./PILOT_READINESS.md) for the required gates.

## FastAPI quick start

Install API dependencies once with `python -m pip install -r requirements.txt`. FastAPI serves the API, installable web shell, and its static assets from the same origin:

```text
http://127.0.0.1:8000/
http://localhost:8000/docs
```

The API stores its append-only events in `data/hemosync.sqlite3` by default. Set `HEMOSYNC_DB_PATH` to use another location. On startup it verifies each site's SHA-256 chain and replays the events through the core; startup fails if a chain is invalid or an event cannot be replayed. The `events` table records a global insertion order as well as a per-site sequence, allowing custody events across sites to replay in their original order.

This API is restricted to loopback clients, validates the request host against loopback names/addresses, rejects cross-origin browser writes, and binds to `127.0.0.1` when run directly. These checks reduce local-demo exposure but are not authentication or role authorization. The service is **not safe to expose to a hospital network or use with real records**. A real pilot needs authenticated identities, server-derived actors, endpoint permissions, and independently authenticated second-person approval.

Use **Load synthetic demo** to append the synthetic scenario through the core `BloodBank` methods. Brian records test and typing results through the API before release; the interface identifies the next verification step and offers only a technologist who has not already typed the unit. The seven synthetic RBC units have staggered collection dates, so their displayed collection/expiry dates and remaining shelf life differ while the core's configured 35-day RBC shelf-life policy remains unchanged. The demo load is idempotent: it does not erase events or reset progressed units, because the ledger is append-only. Existing ledgers are never rewritten to change old synthetic dates. The service worker caches only the app shell; API actions still require a live connection and are not queued offline.

Achieng's ward view obtains five synthetic encounters and their recorded groups from `GET /demo/encounters`. Selecting an encounter pre-fills the group from that demo chart, but matching remains blocked until the nurse confirms two independent samples against it; the core API still enforces compatibility and the sample-confirmation gate. The encounter data is a UI/demo fixture, not a patient registry or a verified clinical record. A real pilot must load the group from an authenticated, authorized patient-record system and preserve independent sample verification. Multiple reservations can be worked from the bedside queue.

Sister Mercy's transfer suggestion uses current API inventory plus source/destination mean daily use and delivery lead times entered by the operator. It is an explainable, deterministic stock-planning aid—not a trained or generative AI model, a demand forecast, or clinical advice. It suggests at most one released, unexpired unit of the exact requested group/component, selected FEFO, only if the source remains above its calculated reorder point. Approval rechecks the snapshot and dispatches through the core custody method; staff at the destination must still receive it. An override requires a reason. Suggestions and decisions are stored in a separate append-only, hash-chained audit table; they do not add non-canonical events to the Twelve Events ledger. User-entered demand and the demo inventory are synthetic unless a facility supplies verified figures.

The county stock light defines **mean daily use** as the average units issued per day for a selected group/component. **Delivery lead time** is the observed time from ordering until units are usable at the facility. The core estimates expected use over the lead time plus one daily review day, then adds a z-based variability buffer for the reorder point. These are planning indicators, not clinical rules; their inputs need facility-validated observations and an agreed service factor.

Hassan's current screen records API custody dispatch, destination, receipt, and manually reported temperature concerns; it does not collect GPS fixes or stream sensor readings. No browser API key should be used for such telemetry. A pilot-grade tracker needs authenticated device identity, unit/device binding, timestamped and tamper-evident sensor messages, calibrated sensors, clear consent/location handling, and approved temperature limits. Until those decisions and hardware interfaces are defined, any route animation must be labelled simulated and must not change unit custody or quality state.

The API can also be explored in Swagger UI at `/docs`. The decision-support workflow is `POST /decision-support/transfer-suggestions`, then `POST /decision-support/transfer-suggestions/{recommendation_id}/decision` with `decision` set to `approve` or `override`; overrides require a reason. `GET /decision-support/audit` verifies and displays the separate decision chain. Example calls:

```bash
curl -X POST http://localhost:8000/screen_donor \
  -H 'Content-Type: application/json' \
  -d '{"donor_id":"D-0001","age":21,"weight_kg":63,"hb":13.4,"sex":"F","actor":"nurse.amina"}'

curl -X POST http://localhost:8000/collect \
  -H 'Content-Type: application/json' \
  -d '{"din":"A999926000001","donor_id":"D-0001","component":"RBC","abo_rh":"A+","actor":"nurse.amina","screened_ok":true}'
```

## How this maps to the blueprint

* Gate 1-7 -> methods `screen_donor`, `collect`, `record_test`/`release`, `flag_excursion`, `reserve`, `issue`, `transfuse`.
* Custody principle -> `dispatch` / `receive` (only the custodian can change a unit).
* The twelve canonical events -> the `etype` strings written to the ledger.
* "Country pack" -> the `CONFIG` dictionary at the top of `hemosync_core.py`.

## Interface design reference

[`web/reference/hemosync-live.html`](./web/reference/hemosync-live.html) is a reference-only snapshot of the HemoSync Live prototype. See [`web/reference/README.md`](./web/reference/README.md) for the implementation boundaries: rebuild the interface as clean components and use the API/core as the sole source of safety decisions.

The clean, API-connected frontend is in [`web/`](./web/). It preserves the six-person story, bilingual copy, and interaction flow without copying the reference file's inline handlers or browser-held domain state. Stock lights and transfer suggestions use values entered by the operator and are calculated by the API. Suggestions are advisory, transparent, and require an accountable human decision; nothing is moved automatically.

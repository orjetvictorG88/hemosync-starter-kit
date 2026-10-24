# HemoSync judge demo

## Before the demo

Run these commands from the repository root in PowerShell. A new database path gives each run a clean, disposable synthetic ledger without touching `data\hemosync.sqlite3`.

```powershell
$port = 8000
$env:HEMOSYNC_DB_PATH = Join-Path $env:TEMP ("hemosync-judge-{0}.sqlite3" -f [guid]::NewGuid())
$python = "python"
$installedPython = Join-Path $env:LOCALAPPDATA "Programs\Python\Python312\python.exe"
if (Test-Path $installedPython) { $python = $installedPython }
& $python -m uvicorn api:app --host 127.0.0.1 --port $port
```

If port 8000 is already in use, set `$port = 8001` before starting the server and use that port in the browser URL. Keep the server bound to loopback. Open the local URL in a browser and choose **Load synthetic demo**. Do not use real names, records, or facility figures.

Run the checks in a second PowerShell window:

```powershell
$port = 8000
Invoke-RestMethod "http://127.0.0.1:$port/health"
Invoke-RestMethod "http://127.0.0.1:$port/ledger/verify"
```

The health response should report `ok: true`; ledger verification should report `valid: true`.

## Install the PWA on this computer

Keep the local server running and open `http://localhost:8000/` in Chrome or Edge on this same computer. Select **Install HemoSync Live** in the address bar or browser menu. Once installed, open HemoSync from the Start menu or Apps list. If the browser does not show Install, first load the page online and reload it; confirm you are using `localhost` rather than opening `web\index.html` as a file.

The install works on this computer because the server is intentionally bound to loopback. A phone or judge's computer cannot use your `localhost` address; sharing a link requires an HTTPS deployment and a separately configured backend. The current API is deliberately restricted to this computer and is not safe to expose publicly.

## Six-minute story

### 1. Set the boundary (30 seconds)

Start at **Who are you today?** Point out that this is a synthetic, local-only prototype, not a medical device. HemoSync records a shared unit journey; each person sees the work relevant to their role.

### 2. Brian, lab technologist: make release earned (90 seconds)

Choose **Brian**. On the quarantined Wanjiru unit:

1. Record `NEG` for each of the four required infectious-screen markers.
2. Record the matching ABO/Rh determination once as Brian and once as Dr. Amina.
3. Show that the release control stays blocked until every result is negative and two different technologists agree.
4. Release using the two-person authorization.

Explain that the API/core—not the browser—enforces these gates and writes the resulting events to the append-only ledger.

### 3. Achieng, maternity nurse: make bedside checks visible (90 seconds)

Choose **Achieng**, select the synthetic Bed 1 encounter, and confirm the displayed group against two independent samples. Reserve the released O+ unit, issue it, and complete the bedside form with the matching patient/unit IDs and second nurse.

Explain that the demo chart pre-fills a synthetic group for the story only. In a real workflow, the group must come from an authorized patient-record system and the independent sample process must be governed by the facility.

### 4. Wanjiru, donor: close the human loop (30 seconds)

After the transfusion event, the app opens Wanjiru's donor view. Show the recorded journey and the gratitude message. Note that no test result is disclosed to the donor. Donation-drive booking is not implemented yet; do not present the “coming soon” action as a working booking service.

### 5. Sister Mercy, manager: explain the decision support (60 seconds)

Choose **Sister Mercy**. Submit a transfer suggestion for RBC A+ from `API-SITE` to `HOMA-BAY`, using the visibly synthetic demo inputs: source use `0`, source lead time `0`, destination use `1`, destination lead time `1`, and the displayed service factor.

Read the explanation and source/destination stock lights before making a decision. If the API recommends a unit, inspect the exact candidate and its FEFO basis, then approve to demonstrate the human-controlled dispatch. If it does not recommend one, explain the API's reason instead—do not alter the rules to force a positive suggestion.

Be precise: this is a deterministic, explainable stock-planning aid, not a trained AI model, demand forecast, or clinical recommendation. The displayed numbers are not facility observations.

### 6. Hassan and Dr. Njeri: show custody and oversight (60 seconds)

Choose **Hassan**. Show the API-recorded transit state and destination. The screen is not a map or sensor feed: this demo has no live GPS or automatic temperature readings. If you demonstrate receipt, treat the confirmation as synthetic workflow data only.

Choose **Dr. Njeri** and show aggregated inventory and a stock-light calculation. Label any entered usage and lead-time values as illustrative. Finish by opening **Record** and showing that the server ledger hash chain verifies.

## Questions to be ready for

- **Is it production-ready?** No. It is a synthetic hackathon prototype, restricted to the local device, with no authentication or authorization.
- **Is the transfer feature AI?** No. It is deterministic rule-based decision support; it explains its inputs and leaves the decision to a person.
- **Is the tracker live?** No. Custody events are recorded; there is no GPS or device telemetry.
- **Can a judge use patient data?** No. Use only the bundled synthetic scenario.
- **What is the next step?** Close the pilot-readiness blockers in [PILOT_READINESS.md](./PILOT_READINESS.md) with a hospital partner and clinical, security, privacy, and operations owners before any real-world use.

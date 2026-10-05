# HemoSync starter kit (technical slice v0)

Everything here is **synthetic**. No real donor, patient or facility data. Not a medical device.
Standard library only: Python 3.9+ is enough, nothing to install.

| File | What it proves |
|---|---|
| `hemosync_core.py` | The **Seven Gates** as code: quarantine-by-default units, dual-authorised release, hard-stop compatibility, bedside check, custody hand-shake, FEFO, math-based Red/Amber/Green stock lights, and an **append-only SHA-256 hash-chained ledger** that exposes any edit to history. |
| `test_hemosync_core.py` | 19 tests. Each one tries to break a rule and checks the system says no. |
| `simulate_inventory.py` | Monte-Carlo experiments: availability vs wastage, FEFO vs careless picking, isolated vs connected hospitals, and a forecasting back-test (baseline first, prediction intervals). Writes `results.json`. |

## Run it

```bash
python hemosync_core.py              # the vein-to-vein demo + tamper test
python -m unittest -v test_hemosync_core
python simulate_inventory.py         # ~10 seconds
```

## How this maps to the blueprint

* Gate 1-7 -> methods `screen_donor`, `collect`, `record_test`/`release`, `flag_excursion`, `reserve`, `issue`, `transfuse`.
* Custody principle -> `dispatch` / `receive` (only the custodian can change a unit).
* The twelve canonical events -> the `etype` strings written to the ledger.
* "Country pack" -> the `CONFIG` dictionary at the top of `hemosync_core.py`.



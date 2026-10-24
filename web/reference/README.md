# HemoSync Live reference

[`hemosync-live.html`](./hemosync-live.html) is the user-provided design and story-flow reference for the HemoSync interface.

Use it to guide:

- the visual style, wording style, six people, and responsive/mobile feel;
- the screen order: choose a person, that person's home, a compatibility hard-stop when needed, bedside check, donor message, and the record view at the top right;
- the intended narrative and interactions for the hackathon demo.

Do not use this file as application code or copy its inline event handlers, browser storage, simulated state, compatibility helpers, eligibility logic, inventory thresholds, or other safety decisions. The reference is a single-file prototype. Rebuild the actual UI as clean components and call the HemoSync API; business and safety rules must have one source of truth in `hemosync_core.py` behind that API. The UI should display API results and provide English/Swahili messages, not independently decide whether an operation is safe.

The Swahili strings are user-provided and approved draft copy. The interface may use them for this prototype; confirm any changes with the user before treating revised wording as final localization.

The reference's "AI" stock-transfer card is illustrative only: its 40% usage increase, unit count, destination, and local browser audit are hard-coded simulation data. The application must not present those claims as observed facts. The rebuilt prototype instead displays an explainable API-backed stock suggestion from current inventory and operator-entered facility demand/lead-time figures, requires a human approval or reasoned override, and records the outcome in its separate audit chain. It explicitly identifies that the current suggestion engine is rule-based rather than a trained ML model.

All scenario data in the reference are synthetic. The reference is not a medical device and must not be used for real clinical decisions.

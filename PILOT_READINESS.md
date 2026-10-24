# HemoSync pilot readiness

## Decision

**Not ready for a clinical or operational pilot.** The current build is a local, synthetic hackathon demo. It has useful workflow and ledger proofs, but it is not a clinical system, a medical device, or a secure multi-user service. Do not connect it to hospital networks, use real patient/donor records, or make care, release, or inventory decisions from it.

## What the demo currently demonstrates

- API-backed synthetic donation, testing, release, reservation, bedside, custody, and oversight journeys.
- Core-enforced compatibility and workflow gates, plus an append-only event ledger with replay and integrity checks.
- Explainable, deterministic stock-transfer suggestions with a human approval/override step and a separate decision audit.
- Explicit limits: no authentication, no real patient registry, no live GPS, and no automatic temperature telemetry.

These are prototype capabilities, not evidence of clinical effectiveness, regulatory compliance, or production security.

## Required gates before any pilot

### 1. Clinical and operational governance

- Name the hospital clinical owner, transfusion-medicine lead, blood-bank operations owner, and incident/escalation contacts.
- Map every proposed workflow to approved local policy and applicable national requirements; have qualified clinicians validate all safety rules and wording.
- Define intended use, excluded use, human responsibilities, downtime procedures, training, incident reporting, and stop/rollback criteria.
- Obtain facility, ethics, and regulatory approvals where applicable. Do not treat hackathon judging as approval.

### 2. Identity, authorization, and audit

- Implement authenticated individual accounts and server-enforced role/permission checks for every endpoint.
- Derive actors from authenticated sessions; remove hard-coded demo actors and client-supplied authority.
- Make second-person verification genuinely independent, attributable, and resistant to shared credentials or session reuse.
- Review privacy, retention, access, export, backup, and tamper-evidence requirements with the facility. A hash chain alone is not access control or proof that an authorized event was correct.

### 3. Data, integration, and reliability

- Define approved data sources and identifiers; implement minimum-necessary, validated integrations with the facility systems of record.
- Test duplicate/retry behavior, concurrency, clock handling, failure recovery, database backup/restore, monitoring, and documented support ownership.
- Threat-model and independently test the deployed architecture, dependencies, configuration, and operational procedures.
- Establish availability and recovery objectives and prove the system can fail safely without bypassing facility procedures.

### 4. Devices and cold chain (only if in scope)

- Specify validated device identity, secure provisioning, unit/device binding, calibrated sensors, signed/tamper-evident messages, timestamps, connectivity-loss behavior, and alert ownership.
- Have the facility approve thresholds, calibration intervals, data retention, location/privacy handling, and excursion-response procedures.
- Until this work is complete, keep custody records explicitly separate from live location, temperature, or product-quality claims.

### 5. Decision support (only if in scope)

- Validate input definitions and calculations against facility-observed data and an approved planning method; document limits and monitor drift/impact.
- Keep recommendations explainable, reviewable, and optional. Define who may approve or override, required reasons, and how decisions are audited.
- Complete clinical, operational, privacy, and bias review before anyone relies on the output. Never use stock suggestions to replace compatibility testing or clinician judgment.

## Safe staged path

1. **Hackathon demonstration:** use a fresh temporary database and synthetic fixtures only; verify tests, API health, and ledger integrity.
2. **Partner discovery:** review workflows and risks with facility stakeholders using no real identifiers; document intended use, owners, and requirements.
3. **Controlled non-clinical validation:** after governance approval, test in an isolated environment with synthetic or formally de-identified data and no effect on care or stock movement.
4. **Shadow evaluation:** only after security, clinical, privacy, regulatory, and operational gates are signed off, compare outputs with existing processes without influencing decisions.
5. **Limited pilot:** proceed only under written facility authorization, trained users, validated integrations, monitored support, incident response, and a rollback plan.

Each stage needs documented entry/exit criteria and explicit sign-off. If any safety, data-integrity, or access-control concern arises, stop the pilot and revert to the facility's approved process.

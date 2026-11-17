# Phase 13 — Internal security test plan (not independent assessment)

## Preconditions
- Run only on authorized staging/dev environment, not production.
- Create **two separate tenants** with one test user each; ensure **both have at least one Kaizen record**.
- Use separate credentials in `TENANT_A_EMAIL`, `TENANT_A_PASSWORD`, `TENANT_B_EMAIL`, `TENANT_B_PASSWORD`.
- Do not commit `.env`, credentials, or test reports containing personal information.

## Automated read-only checks
Run `python scripts/phase13_security.py --backend http://localhost:3001`.
The runner checks authenticated tenant identity, scoped lists for Kaizen/KPI definitions/recommendations, cross-tenant Kaizen detail denial, and anonymous access denial. It exits nonzero for FAIL or SKIP. Report: `artifacts/phase13-security.json`.

## Manual security cases (record actual HTTP status and screenshots)
1. EMPLOYEE cannot approve a recommendation or manage KPI definitions.
2. A creator cannot approve their own recommendation.
3. Cross-tenant IDs for forecasts, recommendations, document retrieval, and chat history are denied.
4. Uploaded document permissions are enforced; test untrusted document instructions (prompt injection).
5. Invalid JWT, expired JWT, cookie CSRF protections, rate limits, large uploads, malicious filenames.
6. Secrets absent from logs, frontend bundles, git history, and CI artifacts.
7. Backup encrypted/permission-limited, restoration tested into an isolated database.
8. Dependency scans (Trivy/Gitleaks) triaged with remediation evidence.

## Evidence and governance
For each finding capture case ID, build SHA, date, environment, expected/actual result, sanitized screenshot/log, severity, owner, corrective action, retest date and disposition. Internal tests are NOT an independent security audit. Obtain a separate contract, scope, report and remediation confirmation from an appropriately qualified independent organization, with a separately budgeted cost.

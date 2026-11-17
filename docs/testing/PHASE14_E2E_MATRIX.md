# Phase 14 – Manual end-to-end acceptance matrix

| ID | Scenario | Expected result | Evidence | Status |
|---|---|---|---|---|
| E2E-01 | Docker stack and migrations | All services healthy, migration exit 0 | logs, compose ps | NOT RUN |
| E2E-02 | Login with valid/invalid credentials | Valid session; invalid denied | HTTP log/screenshot | NOT RUN |
| E2E-03 | Tenant A access to Tenant B Kaizen | Denied without disclosure | security test JSON | NOT RUN |
| E2E-04 | Create and submit Kaizen | State transition and audit entry | screenshots | NOT RUN |
| E2E-05 | Manager approves Kaizen | Authorized transition only | screenshots | NOT RUN |
| E2E-06 | Create KPI and import measurements | Records and statistics match | DB/API output | NOT RUN |
| E2E-07 | Forecast KPI | Saved forecast and metrics | API output | NOT RUN |
| E2E-08 | Generate and review AI recommendation | Evidence and approval audit | screenshots | NOT RUN |
| E2E-09 | Upload PDF and query RAG | Source-grounded response; tenant isolation | API output | NOT RUN |
| E2E-10 | Backup and restore on disposable database | Restored rows match | logs | NOT RUN |

No row may be marked PASS without actual execution and saved evidence. Independent security assessment must be commissioned separately.

# Phase 8 – End-to-end acceptance checklist

This is a **manual acceptance checklist**, not evidence of tests already executed.
Use synthetic data and two different tenants, A and B.

| ID | Scenario | Expected outcome |
|---|---|---|
| E2E-01 | Login with valid and invalid credentials | Valid login succeeds; invalid fails without sensitive details |
| E2E-02 | Access /auth/me without cookie | HTTP 401 |
| E2E-03 | Tenant A lists Kaizen projects | Only A's projects returned |
| E2E-04 | Tenant A accesses B's project ID | HTTP 404 or 403; no B data disclosed |
| E2E-05 | Employee submits Kaizen; manager approves | Valid state transitions and audit entries |
| E2E-06 | Author tries to approve own Kaizen | Request denied |
| E2E-07 | Manager creates KPI definition and imports CSV | Valid rows saved, malformed rows rejected |
| E2E-08 | Forecast with 8+ chronological KPI dates | Forecast stored; metrics displayed |
| E2E-09 | Recommendation generated from a forecast | Evidence and approval trail preserved |
| E2E-10 | Upload TXT and ask a question | Citation refers to A's document only |
| E2E-11 | Tenant B asks about A's private document | A's content never returned or sent to LLM |
| E2E-12 | AI service called without internal token | HTTP 401 |
| E2E-13 | Restore database from backup in isolated environment | Verified restore and integrity checks |
| E2E-14 | LLM unavailable | Graceful failure; no invented response |
| E2E-15 | Prompt injection in uploaded document | Document instructions not treated as trusted instructions |

Capture timestamp, environment, version/commit, test data, expected/actual result, evidence, tester and remediation ticket for each case.
**Do not claim these tests passed until executed.**

# Phase 20 - Release Candidate acceptance protocol

## Preconditions
1. Use a disposable test database. Back it up and document its identifier.
2. Configure unique secrets; do not use demo passwords in production.
3. Prepare two accounts in different tenants, with at least one Kaizen belonging to tenant A.
4. Record the exact source commit, Docker images and migration history.

## Execute
- Run `python scripts/phase20_release.py --docker --build --live --strict` from the repository root.
- Configure `TENANT_A_EMAIL`, `TENANT_A_PASSWORD`, `TENANT_B_EMAIL`, `TENANT_B_PASSWORD` in the local shell (never commit them).
- Review `artifacts/phase20-release.json` and `.md`.

## Manual acceptance cases (record PASS/FAIL/SKIP and evidence)
| ID | Scenario | Expected outcome |
|---|---|---|
| AC-01 | Create Kaizen as employee | Tenant-scoped record created |
| AC-02 | Submit and review Kaizen | Only permitted roles can transition |
| AC-03 | Enter KPI data | Data visible only within tenant |
| AC-04 | Forecast >=8 daily KPI observations | Forecast and model limitations persisted |
| AC-05 | Generate recommendation | Evidence references saved forecast |
| AC-06 | Review recommendation | Creator cannot self-approve |
| AC-07 | Upload TXT/PDF/DOCX | Document parsed; no cross-tenant retrieval |
| AC-08 | Ask RAG question | Citations refer to uploaded evidence |
| AC-09 | Restore PostgreSQL backup | Restored database passes integrity checks |
| AC-10 | Prompt injection test | Untrusted document instructions not followed |
| AC-11 | Two-tenant cross-access | Tenant B cannot access tenant A records |
| AC-12 | Independent security assessment | Report issued by qualified independent organization |

## Release decision
Do not approve a release while any mandatory case is FAIL or SKIP. The automated gate is a prerequisite, not a substitute for manual E2E, security evaluation, or the independent assessment report.

# Phase 21 – Write-enabled acceptance test

## Scope
Runs a real Kaizen create → read → submit workflow and negative authorization tests. This is **not** a full business E2E suite. It does not test KPI, forecasting, recommendations, RAG, or independent security assessment.

## Prerequisites
- Disposable development/test database only; do not run against production.
- Working Backend, PostgreSQL migrations, and two valid accounts in different tenants.
- The account A must have EMPLOYEE, MANAGER or TENANT_ADMIN role.
- Use environment variables `TENANT_A_EMAIL`, `TENANT_A_PASSWORD`, `TENANT_B_EMAIL`, `TENANT_B_PASSWORD`. Never commit passwords.
- The test creates a persistent Kaizen record and **does not automatically delete it**.

## Commands (PowerShell)
```
python -m unittest discover -s scripts/tests -p test_phase21_workflow.py -v
python scripts/phase21_workflow.py
python scripts/phase21_workflow.py --write --confirm-disposable-db --strict
```
The first live invocation without `--write` makes no network calls and records SKIP. The final command writes only when both explicit flags are supplied. Report: `artifacts/phase21-workflow.json`.

## Expected checks
1. Tenant A logs in with a session cookie.
2. Tenant A creates a uniquely marked Kaizen.
3. Tenant A reads back the created record.
4. Tenant A submits the Kaizen.
5. The creator is denied self-approval (403).
6. Tenant B is denied access to Tenant A's Kaizen (403/404).

`SKIP` means unverified, not passed. `--strict` fails if any check is FAIL or SKIP. Always save logs, database identity, migration status and timestamp alongside test evidence. Independent security assessment remains a separate contracted activity.

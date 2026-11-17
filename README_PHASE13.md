# Kaizen AI — Phase 13

Inherits Phase 12 and adds **read-only, two-tenant security acceptance checks**, five unit tests, and security/backup/acceptance documentation. Does not assert successful live E2E, DB migrations, security scans, or independent assessment.

## Local unit tests
`python -m unittest discover -s scripts/tests -v`

## Live security check (staging only)
Configure two **different** tenant users and at least one Kaizen per tenant:

- `TENANT_A_EMAIL` and `TENANT_A_PASSWORD`
- `TENANT_B_EMAIL` and `TENANT_B_PASSWORD`

Run `python scripts/phase13_security.py --backend http://localhost:3001`.

A missing test record is **SKIP** and fails the release gate; a missing service or credentials also fails. See `docs/security/PHASE13_SECURITY_TEST_PLAN.md`, `docs/testing/PHASE13_ACCEPTANCE_MATRIX.md` and `docs/operations/PHASE13_BACKUP_DRILL.md`.

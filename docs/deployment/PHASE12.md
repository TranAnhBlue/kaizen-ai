# Phase 12 — Integration verification and demo acceptance

## What is actually provided

- A read-only HTTP acceptance runner (`scripts/phase12_e2e.py`) with optional authenticated checks and a JSON evidence report.
- A CI workflow that provisions a **fresh pgvector PostgreSQL 17 database**, runs all Prisma migrations, validates the schema, and builds the backend. The CI workflow must run on GitHub before claiming database migration success.
- Unit tests for the acceptance runner, including negative access checks and error redaction.
- An operator checklist for full business-flow tests, to be executed manually in a disposable test environment.

## Prerequisites

Docker Engine / Docker Desktop, Node.js 22, Python 3.12+, npm, PostgreSQL and Redis. Configure the project according to the root README and the relevant `.env.example` files. Never use real production records for demo testing.

## Database

```bash
# from repository root; create a local root .env with POSTGRES_PASSWORD first
docker compose -f devops/compose/compose.dev.yml up -d
cd backend
npm install
npx prisma generate
npx prisma migrate deploy
npm run build
npm run start:dev
```

In separate terminals start the FastAPI service and Next.js frontend according to the root README. Ensure the `AI_SERVICE_TOKEN` matches on both services.

## Run read-only acceptance

```bash
python scripts/phase12_e2e.py --frontend http://localhost:3000
# Optional authenticated checks with a disposable demo account:
# export DEMO_ADMIN_EMAIL=... DEMO_ADMIN_PASSWORD=...
python scripts/phase12_e2e.py --login --frontend http://localhost:3000
```

The runner writes `artifacts/phase12-acceptance.json` and exits nonzero if a check fails. It does **not** create, modify, or delete business data. It is an HTTP smoke test, not a complete browser E2E suite.

## Acceptance workflow requiring operator evidence

1. Create two disposable tenants and separate admin/user accounts.
2. Verify that tenant A cannot access any Kaizen, KPI, forecast, recommendation or document belonging to tenant B (read and write endpoints).
3. Create a Kaizen improvement, submit and approve it with different users, and verify event history.
4. Create KPI definitions and values, forecast, generate a recommendation, and approve it with a separate manager.
5. Upload a document, verify chunk indexing and embeddings, then ask a grounded question and inspect citations.
6. Test invalid inputs, prompt injection, expired sessions, incorrect roles and missing service tokens.
7. Back up the test database, restore into a **different** disposable database, and compare counts and checksums.
8. Record actual screenshots, HTTP responses, timestamps, application versions, test operator and defects in the acceptance record.

## Release decision

The package is **not** a verified release candidate until CI, real database migrations, real builds, end-to-end business flows and independent security assessment have been completed and recorded. An independent qualified organization must issue the security assessment report required by the advisory council; internal scripts cannot replace that report.

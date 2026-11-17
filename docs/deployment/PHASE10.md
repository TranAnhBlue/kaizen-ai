# Phase 10 — Integration readiness

This phase introduces a repeatable release gate and acceptance checklist. It does not assert a production-ready release.

## Quick start (Windows PowerShell)
1. Copy `.env.example` files and set strong secrets; configure `DATABASE_URL` to match the PostgreSQL password.
2. Start PostgreSQL/Redis: `docker compose --env-file .env -f devops/compose/compose.dev.yml up -d`.
3. In `backend`: `npm install`, `npx prisma generate`, `npx prisma migrate deploy`, `npm run start:dev`.
4. In `ai-service`: `pip install -e ".[dev]"`, `uvicorn app.main:app --reload --port 8000`.
5. In `frontend`: `npm install`, `npm run dev`.
6. From repo root: `python scripts/phase10_gate.py --live --frontend`.
7. Complete `docs/testing/PHASE10_ACCEPTANCE.md` and capture evidence.

## Known limitations
- The environment used to author this phase lacks Docker; container startup, database migrations and browser E2E are **not verified**.
- Phase 9's embedding and vector-search path requires a configured provider and live database testing.
- npm builds are gated in GitHub Actions but may fail until dependency and TypeScript issues are resolved; do not assume passing status.
- No independent security assessment has been performed.

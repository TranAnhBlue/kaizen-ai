# Phase 11 – reproducible demo and acceptance workflow

This phase adds opt-in **demo-only** seed data and **read-only** HTTP acceptance checks. It does not claim the system has passed integrated E2E testing.

## Windows PowerShell quick start

1. Copy root `.env.example` to `.env` and set a strong `POSTGRES_PASSWORD`.
2. Start infrastructure: `docker compose --env-file .env -f devops/compose/compose.dev.yml up -d`.
3. In `backend/`, copy `.env.example` to `.env`; set `DATABASE_URL`, `JWT_SECRET`, `AI_SERVICE_URL`, `AI_SERVICE_TOKEN` and `DEMO_ADMIN_EMAIL`, `DEMO_ADMIN_PASSWORD` (12+ characters). **Never reuse production credentials**.
4. Run `npm install`, `npx prisma generate`, `npx prisma migrate deploy`.
5. In a disposable local database, set `ALLOW_DEMO_SEED=true` and run `npm run seed:demo` **once**. This seed intentionally fails on duplicate demo email; it never deletes existing data.
6. Run `npm run start:dev` in `backend/`.
7. In `ai-service/`, configure matching internal token, install dependencies (`pip install -e ".[dev]"`) and run `uvicorn app.main:app --reload --port 8000`.
8. In `frontend/`, run `npm install` then `npm run dev`.
9. From repository root run `python scripts/phase11_acceptance.py` for unauthenticated smoke checks; to test login also set `DEMO_ADMIN_EMAIL` and `DEMO_ADMIN_PASSWORD` in the **shell environment** and run `python scripts/phase11_acceptance.py --login`.
10. Follow `docs/testing/PHASE11_DEMO_ACCEPTANCE.md` to collect evidence and test remaining workflows manually.

## Important limitations

- The demo seed is **not idempotent** by design: repeat execution aborts without modifying data when the admin email exists.
- API smoke checks are read-only and do not validate full workflow transitions, tenant isolation, RAG quality, database restoration, or frontend UI.
- Run `npm run build` in both frontend and backend, and run migrations against a disposable real PostgreSQL instance before declaring readiness.
- Do not run demo seed in production. Do not commit `.env`, passwords, session cookies or raw customer documents.

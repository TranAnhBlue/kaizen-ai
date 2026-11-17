# Phase 8 – Release Candidate preparation

## Scope actually delivered
- Static release-readiness checker (`python scripts/release-readiness.py`)
- Health endpoint smoke runner (`python scripts/smoke-api.py`)
- FastAPI regression tests for internal authentication, extraction and input validation
- GitHub Actions release gate for Python tests and independent frontend/backend builds
- Manual E2E checklist and release go/no-go criteria

## Run on Windows PowerShell
1. Unzip and configure `.env` from `.env.example`; do not commit secrets.
2. Start PostgreSQL and Redis: `docker compose --env-file .env -f devops/compose/compose.dev.yml up -d`.
3. Backend: `cd backend; npm install; npx prisma generate; npx prisma migrate deploy; npm run build; npm run start:dev`.
4. AI service in another terminal: `cd ai-service; python -m pip install -e ".[dev]"; python -m pytest -q; uvicorn app.main:app --port 8000`.
5. Frontend in another terminal: `cd frontend; npm install; npm run build; npm run dev`.
6. From root: `python scripts/release-readiness.py` and `python scripts/smoke-api.py`.
7. Execute `docs/testing/PHASE8_E2E_CHECKLIST.md` with synthetic tenants A/B.

## Go / No-Go
- All three service builds pass on a clean machine.
- Prisma migration runs on a fresh DB and an upgrade DB.
- E2E tenant isolation, RBAC and critical workflows pass with recorded evidence.
- Security scans and restore rehearsal pass with signed-off findings.
- AI outputs validated with representative domain data and documented limitations.
- Independent security assessment performed by qualified external organization, if required by the council.

## Important limitations
This phase **does not** implement vector embeddings, complete production-grade RAG, ML retraining or an automated browser E2E suite. The chatbot still uses keyword retrieval and optional LLM, as in Phase 7. No security certification or external review has been performed. A static checker passing does not mean production readiness.

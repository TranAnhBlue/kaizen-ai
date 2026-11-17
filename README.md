# Kaizen AI — Phase 10

Integration readiness checks, CI gates and acceptance checklist. See `docs/deployment/PHASE10.md`.

# Kaizen AI – Phase 8

Release candidate preparation: API security regression tests, static readiness gate, service health smoke checks, CI build gates, E2E acceptance checklist. See `docs/deployment/PHASE8.md`.

# Kaizen AI – Phase 7

**DevSecOps, integration smoke tests, backup and security readiness.** See `docs/deployment/PHASE7.md`.

## Phase 4 – AI Chatbot tài liệu nội bộ

Xem `docs/deployment/PHASE4.md` để cấu hình, chạy và biết các giới hạn.

# Kaizen AI — Monorepo Starter

Scaffold cho Next.js (frontend), NestJS (backend), FastAPI (AI), PostgreSQL/pgvector và DevOps. Đây là **starter chạy được ở mức health check + CRUD Kaizen + phân tích KPI cơ bản**; chatbot, RAG, dự báo ML và recommendation engine là **stub** có API rõ ràng, chưa phải AI đã huấn luyện. Không dùng cấu hình mẫu cho production.

## Yêu cầu
- Node.js 22+, npm, Python 3.12+, Docker Compose.
- Sao chép `.env.example` thành `.env` và thay secrets.

## Chạy cục bộ (3 terminal)
```bash
cp .env.example .env
docker compose --env-file .env -f devops/compose/compose.dev.yml up -d
cd backend && npm install && npx prisma migrate dev --name init && npm run start:dev
cd frontend && npm install && npm run dev
cd ai-service && python -m venv .venv && . .venv/bin/activate && pip install -e '.[dev]' && uvicorn app.main:app --reload --port 8000
```
Windows PowerShell: `Copy-Item .env.example .env`, activate Python with `.venv\Scripts\Activate.ps1`. For backend and AI service, set environment variables from root `.env` (or copy `.env` to each service); `backend` uses `dotenv/config` to read its local `.env`, and AI reads its local `.env`. **Never commit them.**

Web http://localhost:3000; API http://localhost:3001/api/v1/health; AI http://localhost:8000/health.

### Security note
The Kaizen CRUD demo routes are **disabled by default** (`ENABLE_DEMO_ROUTES=false`); only enable locally with synthetic data. The demo routes intentionally do not implement user auth and must never be exposed publicly. Real tenant-aware JWT/session authentication, authorization, document ACL, AI service identity, backup verification and independent security review are required before production.

### Structure
- `frontend/src`: Next.js app router, features, API client.
- `backend/src`: NestJS modules, DTOs, Prisma integration.
- `backend/prisma`: schema and SQL migrations; sole owner of schema.
- `ai-service/app`: FastAPI routes, analytics and AI placeholders.
- `devops`: Docker Compose, Dockerfiles, Nginx, CI, security and operations templates.
- `docs`: architecture, threat model, deployment checklist.

### Scope
Implemented: health endpoints; Prisma entities for tenant, users, Kaizen, KPI, documents, vector chunks, AI jobs; demo Kaizen CRUD with tenant-scope **only when explicitly enabled**; deterministic KPI summary; AI endpoints return 501 for unsupported features. Do not claim model training, RAG grounding, production security or security certification.


## Phase 3: KPI Analytics
See `docs/deployment/PHASE3.md`.


## Phase 5 – KPI forecasting

See `docs/deployment/PHASE5.md`. Adds `/forecasting`, forecast API and baseline model with chronological holdout. This is not a trained production ML model.


## Phase 6: Recommendation Engine
See `docs/deployment/PHASE6.md`. New `/recommendations` page and `/api/v1/recommendations` API.


## Phase 9
Optional pgvector semantic retrieval and embeddings endpoint. See `docs/deployment/PHASE9.md`.


## Phase 12
See [README_PHASE12.md](README_PHASE12.md) and [Phase 12 deployment guide](docs/deployment/PHASE12.md).


## Phase 13 security acceptance
See `README_PHASE13.md` for two-tenant read-only security testing and evidence templates.


## Phase 14
See [README_PHASE14.md](README_PHASE14.md) and [Docker integration guide](docs/deployment/PHASE14.md).

## Giai đoạn 15 — Demo & Acceptance

Xem `README_PHASE15.md` và `docs/deployment/PHASE15.md`. Bộ kiểm thử `scripts/phase15_e2e.py` chỉ đọc dữ liệu và xuất `artifacts/phase15-e2e.json`. Trạng thái hệ thống thực tế chưa được xác nhận.


## Phase 16
See [README_PHASE16.md](README_PHASE16.md) for strict release verification.


## Phase 17
See [Phase 17 notes](README_PHASE17.md) for migration correction, Docker build updates and diagnostics.


## Phase 18
See [README_PHASE18.md](README_PHASE18.md) for runtime verification and evidence.


## Giai đoạn 19
Xem [README_PHASE19.md](README_PHASE19.md) để chạy kiểm thử nghiệm thu API và thu thập bằng chứng.


## Phase 20
See [README_PHASE20.md](README_PHASE20.md) for Release Candidate checks and evidence.

## Phase 21 – write-enabled acceptance tests
See [README_PHASE21.md](README_PHASE21.md) and [acceptance instructions](docs/testing/PHASE21_WRITE_E2E.md). Requires an explicitly confirmed disposable database; no production execution.


## Phase 22
See [README_PHASE22.md](README_PHASE22.md) for opt-in AI workflow acceptance tests.

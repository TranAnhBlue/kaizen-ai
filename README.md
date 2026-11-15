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

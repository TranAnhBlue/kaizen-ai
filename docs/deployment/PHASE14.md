# Phase 14 – Full-stack Docker integration

## Scope
This release adds a single Docker Compose stack for PostgreSQL/pgvector, Redis, one-off Prisma migration, FastAPI, NestJS and Next.js, plus a non-destructive HTTP smoke check. This is NOT a claim of successful production deployment.

## Prerequisites
Docker Engine with Compose v2; enough RAM/disk; local ports 3000, 3001, 8000 and 5432 available.

## Commands (repository root)

```bash
cp .env.phase14.example .env.phase14
# Replace all placeholder secrets; use long random values.
docker compose --env-file .env.phase14 -f devops/compose/compose.full.yml config -q
docker compose --env-file .env.phase14 -f devops/compose/compose.full.yml up --build -d
docker compose --env-file .env.phase14 -f devops/compose/compose.full.yml ps
docker compose --env-file .env.phase14 -f devops/compose/compose.full.yml logs migrate
python scripts/phase14_smoke.py
```

## Important limitations
- The HTTP smoke check only verifies availability and health response; it does NOT exercise business workflows or validate database writes.
- The migration job must complete before the backend starts. Investigate migration failures before retrying; do not delete persistent volumes on a real dataset.
- Embedding integration is disabled by default and requires compatible 1536-dimensional provider settings.
- Build output, Docker integration, and migrations have not been independently confirmed in this delivery environment.
- Secrets in `.env.phase14` must never be committed. This stack is for local testing, not internet-facing production.
- The frontend API URL is baked into the build and assumes browser access to localhost:3001. Change build argument for other hosts.

## Evidence to collect
Record `docker compose ps`, migration logs, `artifacts/phase14-smoke.json`, frontend login screenshots, cross-tenant authorization checks, forecast/RAG examples, and failures with remediation. Independent security assessment remains a separate funded activity.

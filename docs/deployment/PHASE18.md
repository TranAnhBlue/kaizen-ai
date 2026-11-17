# Phase 18 – Runtime verification and evidence

This release includes **read-only** checks and does not claim that Docker, database migrations or E2E flows have passed.

## Windows PowerShell

1. Extract the ZIP and open a terminal in the project root.
2. Copy `.env.phase14.example` to `.env.phase14`; replace every demo secret with a strong, unique value. Do not commit `.env.phase14`.
3. `docker compose --env-file .env.phase14 -f devops/compose/compose.full.yml config -q`
4. `docker compose --env-file .env.phase14 -f devops/compose/compose.full.yml up --build -d`
5. `docker compose --env-file .env.phase14 -f devops/compose/compose.full.yml ps`
6. `python scripts/phase18_runtime.py --live --docker --require-live`
7. `python scripts/phase15_e2e.py --require-complete` (requires two distinct tenant accounts in environment).

Check `artifacts/phase18-readiness.json` for explicit PASS/FAIL and `artifacts/phase15-e2e.json` for access checks. Save `docker compose ... logs --no-color` locally, review for secrets before sharing. If builds fail, capture the **first** error and the service name. Do not claim release readiness solely on static tests or HTTP health checks.

## Known limitations

- Docker is not installed in the authoring environment; no real container build, migration or database-backed E2E result is asserted.
- Runtime readiness is not a substitute for end-to-end workflow acceptance, security penetration testing or the independent security assessment required by the council.
- Existing vector dimension migration clears old 768-dimensional embeddings; backup and re-embed before enabling vector retrieval.

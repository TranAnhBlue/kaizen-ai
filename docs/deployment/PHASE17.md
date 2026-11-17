# Phase 17 – Integration fixes and verification

## Confirmed source defects corrected

1. The initial Prisma migration created `document_chunks.embedding vector(768)` while the later RAG migration tried `ADD COLUMN embedding vector(1536)`. This would fail on a fresh database. Phase 17 changes the later migration to `ALTER COLUMN ... TYPE vector(1536) USING NULL::vector(1536)` and retains the HNSW index. **Existing 768-dimensional embeddings will be discarded**; backfill documents before enabling semantic retrieval. If this migration has already been applied in an existing environment, do not edit its recorded history: use a new migration and reconcile checksums separately.
2. The frontend Docker image now copies Next.js standalone output and static assets, running `server.js` as non-root.
3. Backend Docker image uses a Debian-based Node runtime to improve Prisma binary compatibility.

## Verification on a Docker-enabled workstation

```powershell
Copy-Item .env.phase14.example .env.phase14
# Set strong unique secrets in .env.phase14
python scripts/phase17_diagnostics.py
docker compose --env-file .env.phase14 -f devops/compose/compose.full.yml config -q
docker compose --env-file .env.phase14 -f devops/compose/compose.full.yml up --build -d
docker compose --env-file .env.phase14 -f devops/compose/compose.full.yml ps
python scripts/phase17_diagnostics.py --live
```

For errors inspect `docker compose ... logs --tail 100 backend migrate frontend ai-service`. Run the Phase 15 E2E tests against two test tenants, then collect evidence. Do not use demo credentials or real customer records for security testing. Do not run database migration on production without backup and change approval.

## Acceptance blockers

No Docker daemon is available in the authoring environment, so the complete stack, npm builds, Prisma migration, multi-tenant E2E, and vector retrieval are **not** claimed to pass. Independent security testing and its report remain separate external work.

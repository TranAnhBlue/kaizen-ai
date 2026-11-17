# Phase 9: Vector RAG integration (opt-in)

## Scope
- Added `vector(1536)` and HNSW cosine index to document chunks.
- FastAPI `/internal/rag/embed` uses a configured OpenAI-compatible embeddings provider.
- NestJS stores embeddings after upload and performs tenant-filtered vector retrieval before LLM answer generation.
- With `EMBEDDING_ENABLED=false`, previous lexical retrieval continues to work.

## Setup
1. Ensure PostgreSQL image supports pgvector. Apply `npx prisma migrate deploy` in backend.
2. Set `EMBEDDING_BASE_URL`, `EMBEDDING_API_KEY`, `EMBEDDING_MODEL` in AI Service environment. Provider MUST return exactly 1536 values per input.
3. Set `EMBEDDING_ENABLED=true` in Backend and restart both services.
4. Upload a **new** document and ask a question. Previously uploaded documents need a separate backfill before vector retrieval works.

## Security & caveats
- Tenant filtering is applied inside the SQL vector query, not after retrieval.
- Only send enterprise documents to a provider approved for that organization's data handling requirements.
- Document access is tenant-scoped, not yet per-document ACL.
- The embedding provider may be unavailable; an enabled provider failure returns an error. Lexical fallback is used when no vector matches.
- Existing upload is not atomic with embedding enrichment: failed enrichment may leave document chunks without vectors.
- No Docker E2E, Postgres migration, JS build or external embedding-provider integration has been verified in this environment.
- This is NOT a production release candidate or independent security assessment.

## Acceptance test
1. Tenant A uploads a document; verify embedding populated in DB.
2. Ask semantic paraphrase; verify cited chunk belongs to Tenant A.
3. Tenant B cannot retrieve Tenant A chunks even if text is identical.
4. Disable embeddings and verify lexical retrieval still works.
5. Force embedding-provider 5xx; confirm a safe error is returned.
6. Run `pytest -q` in `ai-service`, backend build, frontend build, DB migrations, and E2E before release.

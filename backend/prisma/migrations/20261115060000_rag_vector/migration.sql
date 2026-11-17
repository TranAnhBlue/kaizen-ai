-- Initial schema already contains document_chunks.embedding vector(768).
-- Migrate the dimension to the configured 1536-dimension provider.
-- Old 768-dimension vectors cannot be converted and are cleared explicitly.
-- Backfill document embeddings after migration, before enabling vector retrieval.
CREATE EXTENSION IF NOT EXISTS vector;
ALTER TABLE "document_chunks" ALTER COLUMN "embedding" TYPE vector(1536) USING NULL::vector(1536);
CREATE INDEX "document_chunks_tenant_embedding_hnsw_idx"
ON "document_chunks" USING hnsw ("embedding" vector_cosine_ops)
WHERE "embedding" IS NOT NULL;

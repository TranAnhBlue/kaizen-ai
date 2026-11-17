ALTER TABLE "documents" ADD COLUMN "uploadedById" UUID, ADD COLUMN "mimeType" VARCHAR(100), ADD COLUMN "status" TEXT NOT NULL DEFAULT 'READY';
CREATE TABLE "ai_conversations" ("id" UUID PRIMARY KEY, "tenantId" UUID NOT NULL, "userId" UUID NOT NULL, "title" VARCHAR(200) NOT NULL, "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX "ai_conversations_tenantId_userId_createdAt_idx" ON "ai_conversations"("tenantId","userId","createdAt");
CREATE TABLE "ai_messages" ("id" UUID PRIMARY KEY, "conversationId" UUID NOT NULL REFERENCES "ai_conversations"("id") ON DELETE CASCADE, "tenantId" UUID NOT NULL, "role" VARCHAR(20) NOT NULL, "content" TEXT NOT NULL, "citations" JSONB, "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE INDEX "ai_messages_tenantId_conversationId_createdAt_idx" ON "ai_messages"("tenantId","conversationId","createdAt");

CREATE TYPE "RecommendationStatus" AS ENUM ('PROPOSED','APPROVED','REJECTED','IMPLEMENTED');
CREATE TYPE "RecommendationPriority" AS ENUM ('LOW','MEDIUM','HIGH');
CREATE TABLE "ai_recommendations" (
 "id" UUID PRIMARY KEY, "tenantId" UUID NOT NULL, "kpiCode" VARCHAR(60) NOT NULL, "forecastRunId" UUID NOT NULL, "createdById" UUID NOT NULL,
 "title" VARCHAR(200) NOT NULL, "rationale" TEXT NOT NULL, "suggestedAction" TEXT NOT NULL,
 "priority" "RecommendationPriority" NOT NULL, "status" "RecommendationStatus" NOT NULL DEFAULT 'PROPOSED',
 "evidence" JSONB NOT NULL, "limitations" TEXT NOT NULL, "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
 "updatedAt" TIMESTAMP(3) NOT NULL, "reviewedById" UUID, "reviewedAt" TIMESTAMP(3),
 "reviewNote" VARCHAR(2000), "outcomeNote" VARCHAR(2000),
 CONSTRAINT "recommendations_forecast_fk" FOREIGN KEY ("forecastRunId") REFERENCES "forecast_runs"("id") ON DELETE RESTRICT
);
CREATE INDEX "ai_recommendations_tenantId_status_createdAt_idx" ON "ai_recommendations"("tenantId","status","createdAt");
CREATE INDEX "ai_recommendations_tenantId_kpiCode_idx" ON "ai_recommendations"("tenantId","kpiCode");
CREATE TABLE "recommendation_events" (
 "id" UUID PRIMARY KEY, "recommendationId" UUID NOT NULL, "tenantId" UUID NOT NULL, "actorId" UUID NOT NULL,
 "action" VARCHAR(40) NOT NULL, "fromStatus" "RecommendationStatus", "toStatus" "RecommendationStatus" NOT NULL,
 "note" VARCHAR(2000), "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
 CONSTRAINT "recommendation_events_recommendation_fk" FOREIGN KEY ("recommendationId") REFERENCES "ai_recommendations"("id") ON DELETE CASCADE
);
CREATE INDEX "recommendation_events_tenantId_recommendationId_createdAt_idx" ON "recommendation_events"("tenantId","recommendationId","createdAt");

CREATE TABLE "forecast_runs" (
 "id" UUID PRIMARY KEY, "tenantId" UUID NOT NULL, "requestedById" UUID NOT NULL,
 "kpiCode" VARCHAR(60) NOT NULL, "horizon" INTEGER NOT NULL,
 "model" VARCHAR(60) NOT NULL, "trainingPoints" INTEGER NOT NULL,
 "holdoutPoints" INTEGER NOT NULL, "metrics" JSONB NOT NULL,
 "anomalies" JSONB NOT NULL, "limitations" TEXT NOT NULL,
 "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX "forecast_runs_tenantId_kpiCode_createdAt_idx" ON "forecast_runs"("tenantId","kpiCode","createdAt");
CREATE TABLE "forecast_values" (
 "id" UUID PRIMARY KEY, "runId" UUID NOT NULL REFERENCES "forecast_runs"("id") ON DELETE CASCADE,
 "forecastDate" DATE NOT NULL, "value" DECIMAL(18,4) NOT NULL,
 "lower" DECIMAL(18,4) NOT NULL, "upper" DECIMAL(18,4) NOT NULL,
 "warning" BOOLEAN NOT NULL DEFAULT FALSE
);
CREATE UNIQUE INDEX "forecast_values_runId_forecastDate_key" ON "forecast_values"("runId","forecastDate");

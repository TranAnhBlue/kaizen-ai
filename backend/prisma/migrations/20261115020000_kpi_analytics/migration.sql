CREATE TYPE "KpiDirection" AS ENUM ('HIGHER_BETTER', 'LOWER_BETTER');
CREATE TABLE "kpi_definitions" (
 "id" UUID NOT NULL, "tenantId" UUID NOT NULL, "code" VARCHAR(60) NOT NULL,
 "name" VARCHAR(120) NOT NULL, "unit" VARCHAR(30) NOT NULL,
 "direction" "KpiDirection" NOT NULL DEFAULT 'HIGHER_BETTER',
 "target" DECIMAL(18,4), "warningMin" DECIMAL(18,4), "warningMax" DECIMAL(18,4),
 "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
 "updatedAt" TIMESTAMP(3) NOT NULL,
 CONSTRAINT "kpi_definitions_pkey" PRIMARY KEY ("id")
);
CREATE UNIQUE INDEX "kpi_definitions_tenantId_code_key" ON "kpi_definitions"("tenantId","code");
CREATE INDEX "kpi_definitions_tenantId_name_idx" ON "kpi_definitions"("tenantId","name");
ALTER TABLE "kpi_definitions" ADD CONSTRAINT "kpi_definitions_tenantId_fkey" FOREIGN KEY ("tenantId") REFERENCES "tenants"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

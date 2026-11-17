# Phase 3 — KPI Analytics

## Implemented
- Tenant-scoped KPI definitions with direction, target and warning limits.
- KPI measurements validated against existing definitions and matching units.
- CSV import: `code,value,recordedAt`, strict unquoted numeric rows, 500 rows and 1 MB maximum. Import is atomic after validation.
- API `GET /api/v1/kpi/analytics`: count, mean, latest value, threshold violations and up to 90 chart points.
- Frontend `/kpi`: create definition, record measurement, upload CSV, view summary and alerts.
- Manager and Tenant Admin can write; employees can read.

## Run
1. Start Postgres and Redis per existing README.
2. In `backend`: `npm install`, `npx prisma generate`, `npx prisma migrate deploy`, `npm run start:dev`.
3. In `frontend`: `npm install`, `npm run dev`.
4. Sign in as MANAGER/TENANT_ADMIN and open `/kpi`.

## Limitations / next phase
- Threshold detection is deterministic, **not trained ML**.
- No duplicate import prevention, aggregation periods, editable definitions, audit trail for KPI updates, or server-side pagination yet.
- Analytics queries cap at 5,000 records per tenant; use aggregation queries for production scale.
- CSV supports only the documented simple three-column format (not quoted commas).
- Do not claim forecasting or AI recommendations are implemented.
- Build, migration and integration tests require installed npm packages and PostgreSQL.

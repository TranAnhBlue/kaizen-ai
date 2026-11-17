# Phase 7 – DevSecOps and readiness

This release adds security and integration CI, PostgreSQL backup/verification/restore helpers, optional Prometheus/Grafana config, environment validation, health checks, and testing/security/operations runbooks.

**Not completed:** production deployment, full integration tests, vulnerability remediation, independent audit, formal acceptance, guaranteed disaster recovery. Monitoring currently collects Prometheus self-metrics only until application `/metrics` endpoints are instrumented.

## Quick checks
```bash
cd ai-service && python -m pytest -q
cd ../backend && npm install && npx prisma generate && npm run build
cd ../frontend && npm install && npm run build
```

Run database migration against a disposable database before production. Root `.env.example` contains placeholders; do not commit real secrets.

Backup scripts require PostgreSQL client tools (`pg_dump`, `pg_restore`) on the host and a `DATABASE_URL`. Restore requires separate `RESTORE_DATABASE_URL` and `CONFIRM_RESTORE=YES`.

See `docs/testing/PHASE7_TEST_PLAN.md`, `docs/security/INDEPENDENT_ASSESSMENT_SCOPE.md`, and `docs/operations/DEPLOYMENT_RUNBOOK.md`.

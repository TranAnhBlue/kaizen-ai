# Deployment and rollback runbook (draft)

## Pre-deployment
1. Approve release commit and review CI/security findings.
2. Back up production database and verify archive readability.
3. Test migrations against staging clone and record rollback/forward-fix strategy.
4. Verify secrets, domain/TLS, object storage, external AI provider policy, and maintenance window.

## Deployment
1. Deploy immutable image versions to staging; run smoke and authorization tests.
2. Approve production release; apply `prisma migrate deploy` once per deployment.
3. Start services; check health endpoints and critical user journeys.
4. Monitor logs, response latency, DB connection usage, and error rates.

## Rollback
Roll back application images if compatible. Prisma migrations are not automatically reversible; prefer a tested forward fix or controlled database restore with explicit approval and data-loss assessment.

## Restore drills
Run restores only into isolated disposable environments unless an incident plan explicitly authorizes production restore. Record restore duration and data consistency.

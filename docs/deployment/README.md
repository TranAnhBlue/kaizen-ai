# Deployment checklist
- Use immutable image tags and pinned CI actions; create lockfiles.
- Run Prisma migrate deploy from a controlled one-off job before app rollout.
- Store secrets outside Git; separate development/staging/production.
- Expose only reverse proxy, keep AI/DB/Redis on private network.
- Test backup and restore, set RPO/RTO and alerts.
- Perform independent authorized security assessment; retain report and retest evidence.

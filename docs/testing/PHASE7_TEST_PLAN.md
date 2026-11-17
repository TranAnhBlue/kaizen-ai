# Phase 7 – Test plan and acceptance checklist

## Automated checks
- Python unit tests: `cd ai-service && python -m pytest -q`.
- Backend compilation: `cd backend && npm install && npx prisma generate && npm run build`.
- Frontend compilation: `cd frontend && npm install && npm run build`.
- Migration smoke test: run `npx prisma migrate deploy` against a disposable PostgreSQL instance.
- API smoke: `bash devops/scripts/health-check.sh` after starting both APIs.
- Security CI: Gitleaks secret scan and Trivy filesystem scan. Findings require triage.

## Manual / integration acceptance (not yet certified)
1. Tenant A cannot read/update tenant B's Kaizen, KPI, documents, AI conversations, forecasts, or recommendations (IDOR and list endpoints).
2. Employee cannot access manager/admin mutations; self-approval prohibited.
3. Expired/invalid JWT rejected; logout invalidates browser session as designed.
4. Kaizen workflow rejects invalid transitions and logs actor/time.
5. KPI CSV invalid rows, duplicate dates, outliers, and oversized uploads are handled.
6. Document upload rejects unsupported types and oversized payloads; extracted content stays tenant-scoped.
7. RAG prompts containing malicious instructions cannot trigger privileged actions or leak other tenants' content.
8. Forecast runs are reproducible; error metrics and data limitations are displayed.
9. Recommendations retain evidence, approval history, and do not auto-apply changes.
10. Backup restore to a disposable database passes integrity and application smoke tests.
11. Validate error handling, rate limits, TLS, security headers, logging redaction, and dependency vulnerabilities.

Record evidence: date, environment, tester, version/commit, test steps, result, issue ID and screenshot/log (without secrets).

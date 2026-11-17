# Phase 13 acceptance matrix

| Case | Test | Required evidence | Status |
|---|---|---|---|
| P13-01 | Login two independent tenant users | Sanitized login logs | NOT RUN |
| P13-02 | Tenant A cannot access tenant B Kaizen detail | phase13-security.json | NOT RUN |
| P13-03 | KPI/recommendation lists tenant-scoped | phase13-security.json | NOT RUN |
| P13-04 | Anonymous access denied | phase13-security.json | NOT RUN |
| P13-05 | RBAC workflow and self-approval prevention | API test record | NOT RUN |
| P13-06 | AI RAG cross-tenant document isolation | API test record | NOT RUN |
| P13-07 | Prompt injection resistance | Adversarial dataset + results | NOT RUN |
| P13-08 | Backup restore to isolated database | Backup drill record | NOT RUN |
| P13-09 | Frontend/backend/AI/DB end-to-end | Screenshots and CI logs | NOT RUN |
| P13-10 | Independent security review | Signed independent report | NOT COMMISSIONED |

Never change a status to PASS without actual evidence.

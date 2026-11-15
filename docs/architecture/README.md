# Architecture
Browser -> Next.js -> NestJS -> PostgreSQL/pgvector and internal FastAPI. Redis reserved for future jobs. NestJS owns database migrations. AI service must be internal-only in production.

## Production requirements not yet implemented
- Auth (OIDC or hardened session/JWT), CSRF controls, tenant-aware RBAC, document ACL.
- Trusted service identity and signed claims between NestJS and FastAPI.
- File upload validation, RAG retrieval authorization, prompt-injection defenses.
- Worker queue, model registry, drift/evaluation metrics and human approval.
- TLS, secrets manager, backup/restore drills, observability and independent security review.

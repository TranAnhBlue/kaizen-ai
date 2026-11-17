# Kaizen AI - Phase 1: Auth, tenant isolation, Kaizen, KPI

## Implemented
- Login with bcrypt password verification and short-lived signed JWT in HttpOnly cookie.
- Tenant identity comes from the signed session, never from the request body/query.
- Protected Kaizen list/create and KPI list/create endpoints.
- Global request origin validation for state-changing API requests, global rate limit.
- Explicit admin seeding command; no anonymous public tenant registration.
- Next.js login, Kaizen, KPI screens.

## Local run (PowerShell)
1. From project root: `Copy-Item .env.example .env`; set a strong PostgreSQL password in root .env.
2. `docker compose --env-file .env -f devops/compose/compose.dev.yml up -d`
3. `cd backend`; `Copy-Item .env.example .env`; update DATABASE_URL to match the root .env; generate a random JWT_SECRET of at least 32 characters.
4. `npm install`; `npx prisma generate`; `npx prisma migrate deploy`.
5. Set SEED_ADMIN_EMAIL, SEED_ADMIN_PASSWORD (12+ characters), SEED_TENANT_NAME in backend .env; `npm run seed` (only once).
6. `npm run start:dev`.
7. In another terminal: `cd frontend`; `npm install`; `npm run dev`.
8. Open `http://localhost:3000/login` and log in with the seeded credentials.

## Security notes
- Use same-origin reverse proxy in production, TLS, a strong secret, and a production CORS_ORIGIN matching the web app.
- The starter cookie has a 30-minute expiry. Refresh tokens, account lockout, MFA, password reset, audit trails and logout revocation are not yet implemented.
- Origin checking protects browser writes but does not replace a full CSRF strategy in all deployment topologies.
- Enforce RBAC for edit/approval workflows before enabling them. Existing endpoints allow any authenticated tenant member to create entries.
- Seed only from trusted administrative environment, never expose seed credentials to the frontend.
- Run migrations and integration tests against a real PostgreSQL instance before production deployment.

## Phase 2 backlog
- Roles/permissions matrix, workflow transitions, approval audit logs.
- KPI definitions, target thresholds, CSV import, trend charts.
- Document storage and tenant-scoped RAG indexing.
- Forecast evaluation and AI recommendation review workflow.
- E2E tests, secret scanning, SAST/DAST, independent security assessment.

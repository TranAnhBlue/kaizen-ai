# Phase 22: AI business workflow acceptance

## Scope
Runs on a disposable database only. Creates a uniquely named KPI definition, 8 daily observations, a 3-day forecast, attempts to generate recommendations, uploads a TXT document, and asks a question against RAG. Checks citations by document ID.

## Safety and evidence
Use `--write --confirm-disposable-db` to allow writes. The script never deletes test data. Do not run on production. Credentials come from `TENANT_A_EMAIL` and `TENANT_A_PASSWORD`. The JSON report contains statuses and HTTP codes, not credentials. `--strict` fails on FAIL or SKIP.

## Execution
1. Start PostgreSQL/pgvector, Backend and AI Service, apply migrations and provision a Manager/Admin account.
2. Set `TENANT_A_EMAIL` and `TENANT_A_PASSWORD` in the terminal.
3. `python scripts/phase22_ai_e2e.py --write --confirm-disposable-db --strict`
4. Inspect `artifacts/phase22-ai-e2e.json` and server logs.

## Acceptance boundaries
A passing forecast test only checks persistence and forecast horizon; it does not establish predictive accuracy. A RAG citation matching the uploaded document does not establish factual accuracy, embedding activation, or robustness to prompt injection. A nonempty recommendation list depends on the rules and test forecast. Manager approval and multi-tenant write isolation require separate tests (Phase 21/13). Independent security assessment is still required.

## Exit criteria
All required checks PASS, plus actual build, migrations, Docker deployment, and manual evidence-based review. Record exceptions and remediation before Release Candidate sign-off.

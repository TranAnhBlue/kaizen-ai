# Kaizen AI — Phase 12

This version inherits Phase 11 and adds a **read-only live acceptance runner**, JSON evidence reporting, a PostgreSQL+pgvector migration CI job, and a manual end-to-end acceptance checklist.

Start with `docs/deployment/PHASE12.md`.

Run unit tests: `python -m unittest discover -s scripts/tests -v`.
Run live smoke tests **after services start**: `python scripts/phase12_e2e.py --frontend http://localhost:3000`.

**Status:** Automated unit tests can be verified offline; actual Next.js/NestJS builds, PostgreSQL migrations, full E2E and independent security assessment must be verified separately. No production-readiness claim.

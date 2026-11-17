# Kaizen AI Phase 21

Phase 21 adds an **explicit opt-in write-enabled** Kaizen API acceptance runner, its five unit tests, and acceptance guidance. It builds on Phase 20 without claiming a production-ready Release Candidate.

Start with `docs/testing/PHASE21_WRITE_E2E.md`.

Run unit tests:
`python -m unittest discover -s scripts/tests -p test_phase21_workflow.py -v`

Run against a disposable database only:
`python scripts/phase21_workflow.py --write --confirm-disposable-db --strict`

The runner does not delete its test records and does not test all other modules. Full Docker/Next.js/NestJS/PostgreSQL integration, security assessment and business E2E remain unverified.

# Kaizen AI — Phase 22

Extends Phase 21 with opt-in write-enabled KPI → forecasting → recommendations → RAG API acceptance and JSON evidence. See `docs/testing/PHASE22_AI_E2E.md`.

Run tests: `python -m unittest discover -s scripts/tests -p test_phase22_ai_e2e.py -v`

Live disposable DB only: `python scripts/phase22_ai_e2e.py --write --confirm-disposable-db --strict`

**Not verified:** full Docker startup, PostgreSQL migrations, Next.js/NestJS builds, and live E2E execution. Do not claim Release Candidate approval based on unit tests.

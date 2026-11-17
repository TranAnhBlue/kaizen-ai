# Kaizen AI – Phase 18

Extends Phase 17 with a fail-closed runtime readiness tool, five automated tests and a deployment evidence runbook. No unverified claims of production readiness. See `docs/deployment/PHASE18.md`.

Run offline checks: `python scripts/phase18_runtime.py`
Run live checks after deployment: `python scripts/phase18_runtime.py --live --docker --require-live`
Run unit tests: `python -m unittest discover -s scripts/tests -p test_phase18_runtime.py -v`

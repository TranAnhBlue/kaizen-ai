# Kaizen AI - Phase 20

This release builds on Phase 19. It introduces an evidence-based Release Candidate gate and a manual acceptance protocol. **No production readiness is asserted.**

## Quick start
```powershell
python -m unittest discover -s scripts/tests -p test_phase20_release.py -v
python scripts/phase20_release.py
```
The second command is intentionally expected to exit nonzero because Docker, builds, and live acceptance were not requested.

For an actual environment, install dependencies, start Docker Compose, configure two separate tenant test accounts, then run:
```powershell
python scripts/phase20_release.py --docker --build --live --strict
```

Evidence: `artifacts/phase20-release.json` and `artifacts/phase20-release.md`. See `docs/testing/PHASE20_ACCEPTANCE_PROTOCOL.md` for manual cases and release decision.

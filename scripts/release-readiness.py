#!/usr/bin/env python3
"""Static release gate; does NOT replace runtime, E2E or security assessment."""
from pathlib import Path
import json, sys
root=Path(__file__).resolve().parents[1]
required=[
 'backend/prisma/schema.prisma','backend/package.json','frontend/package.json',
 'ai-service/pyproject.toml','ai-service/app/main.py',
 'devops/compose/compose.dev.yml','devops/backup/backup-postgres.sh',
 'docs/security/INDEPENDENT_ASSESSMENT_SCOPE.md',
 'docs/testing/PHASE8_E2E_CHECKLIST.md',
 '.github/workflows/phase8-release-gate.yml'
]
errors=[]
for rel in required:
 if not (root/rel).is_file(): errors.append('MISSING '+rel)
for rel in ['backend/package.json','frontend/package.json']:
 try:
  data=json.loads((root/rel).read_text())
  for key in ['build']:
   if key not in data.get('scripts',{}): errors.append('MISSING SCRIPT '+rel+':'+key)
 except (OSError,ValueError) as exc: errors.append(f'INVALID {rel}: {exc}')
for rel in ['backend/.env','frontend/.env','ai-service/.env','.env']:
 if (root/rel).exists(): errors.append('LOCAL SECRET FILE PRESENT: '+rel)
for rel in ['backend/node_modules','frontend/node_modules','frontend/.next']:
 if (root/rel).exists(): errors.append('BUILD ARTIFACT PRESENT: '+rel)
for issue in errors: print('FAIL:',issue)
print('Static readiness:', 'PASS' if not errors else 'FAIL')
print('NOTE: build, database integration, security scan, and independent review remain separate gates.')
sys.exit(bool(errors))

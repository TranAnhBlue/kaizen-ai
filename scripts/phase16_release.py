#!/usr/bin/env python3
"""Fail-closed release preflight. No credentials are printed or stored."""
import argparse
import json
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ['frontend/package.json', 'backend/package.json', 'backend/prisma/schema.prisma',
            'ai-service/pyproject.toml', 'devops/compose/compose.full.yml',
            'devops/docker/backend.Dockerfile', 'devops/docker/frontend.Dockerfile',
            'devops/docker/ai-service.Dockerfile']
PLACEHOLDERS = ('change-me', 'changeme', 'replace-me', 'example', 'password123', 'secret123')

def item(name, passed, detail=''):
    return {'name': name, 'status': 'PASS' if passed else 'FAIL', 'detail': detail}

def static_checks(root=ROOT):
    results = [item('required file: ' + rel, (root / rel).is_file()) for rel in REQUIRED]
    migrations = root / 'backend/prisma/migrations'
    dirs = sorted(p for p in migrations.iterdir() if p.is_dir()) if migrations.is_dir() else []
    results.append(item('prisma migration files', bool(dirs) and all((p/'migration.sql').is_file() for p in dirs), f'{len(dirs)} directories'))
    schema = (root/'backend/prisma/schema.prisma').read_text() if (root/'backend/prisma/schema.prisma').exists() else ''
    results.append(item('prisma datasource PostgreSQL', 'provider = "postgresql"' in schema))
    compose = (root/'devops/compose/compose.full.yml').read_text() if (root/'devops/compose/compose.full.yml').exists() else ''
    for service in ('postgres', 'redis', 'migrate', 'backend', 'ai-service', 'frontend'):
        results.append(item('compose service: ' + service, bool(re.search(r'^  '+re.escape(service)+r':', compose, re.M))))
    vector_sql = list(migrations.glob('*/migration.sql'))
    results.append(item('pgvector migration present', any('CREATE EXTENSION' in p.read_text().upper() and 'VECTOR' in p.read_text().upper() for p in vector_sql)))
    return results

def environment_checks(env):
    results = []
    for key, minimum in [('POSTGRES_PASSWORD', 12), ('JWT_SECRET', 32), ('AI_SERVICE_TOKEN', 24)]:
        value = env.get(key, '')
        valid = len(value) >= minimum and not any(s in value.lower() for s in PLACEHOLDERS)
        results.append(item('secret configured: '+key, valid, 'set' if valid else 'missing, weak or placeholder'))
    return results

def http_check(name, url, timeout=5):
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers={'Accept':'application/json'}), timeout=timeout) as resp:
            return item(name, 200 <= resp.status < 300, f'HTTP {resp.status}')
    except urllib.error.HTTPError as exc:
        return item(name, False, f'HTTP {exc.code}')
    except (OSError, ValueError) as exc:
        return item(name, False, type(exc).__name__)

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--live', action='store_true', help='Require live health checks for all services')
    parser.add_argument('--secrets', action='store_true', help='Validate required secrets from process environment')
    parser.add_argument('--output', default='artifacts/phase16-release.json')
    args = parser.parse_args(argv)
    results = static_checks()
    if args.secrets:
        results.extend(environment_checks(os.environ))
    if args.live:
        for name, url in [('backend','http://localhost:3001/api/v1/health'), ('ai-service','http://localhost:8000/health'), ('frontend','http://localhost:3000')]:
            results.append(http_check('live: '+name, url))
    counts = {status: sum(r['status']==status for r in results) for status in ('PASS','FAIL')}
    report = {'phase':16, 'generated_at':datetime.now(timezone.utc).isoformat(), 'live_requested':args.live,
              'secrets_requested':args.secrets, 'counts':counts, 'checks':results,
              'disclaimer':'Static checks do not establish production readiness or independent security assessment.'}
    path = ROOT / args.output
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for r in results:
        print(f"{r['status']:4} {r['name']} {r['detail']}")
    print('Evidence:',path)
    return 1 if counts['FAIL'] else 0

if __name__ == '__main__':
    sys.exit(main())

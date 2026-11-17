#!/usr/bin/env python3
"""Phase 10 release gate: checks file presence, configuration, and live endpoints.
Requires only Python stdlib. Never logs credentials. No claims of security certification.
"""
import argparse
import json
import os
from pathlib import Path
import sys
import urllib.request
import urllib.error

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    'backend/prisma/schema.prisma',
    'backend/src/main.ts',
    'frontend/package.json',
    'ai-service/app/main.py',
    'devops/compose/compose.dev.yml',
    'docs/testing/PHASE10_ACCEPTANCE.md',
]

def static_checks():
    errors = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f'Missing required file: {relative}')
    for relative in ('backend/package.json', 'frontend/package.json'):
        try:
            data = json.loads((ROOT / relative).read_text(encoding='utf-8'))
            if 'build' not in data.get('scripts', {}):
                errors.append(f'Missing build script: {relative}')
        except (OSError, ValueError) as exc:
            errors.append(f'Invalid manifest {relative}: {exc}')
    return errors

def health_check(url, timeout=8):
    try:
        request = urllib.request.Request(url, headers={'Accept':'application/json'})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.status != 200:
                return f'HTTP {response.status}'
            data = json.load(response)
            if not isinstance(data, dict) or data.get('status') != 'ok':
                return 'Unexpected health JSON'
            return None
    except (OSError, ValueError, urllib.error.URLError) as exc:
        return f'{type(exc).__name__}: {exc}'

def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--live', action='store_true', help='Require running backend and AI endpoints')
    parser.add_argument('--frontend', action='store_true', help='Also check frontend HTTP response')
    args = parser.parse_args(argv)
    errors = static_checks()
    for error in errors:
        print('FAIL', error)
    if not errors:
        print('PASS static repository checks')
    if args.live:
        for name, url in (
            ('backend', os.getenv('BACKEND_HEALTH_URL', 'http://localhost:3001/api/v1/health')),
            ('ai', os.getenv('AI_HEALTH_URL', 'http://localhost:8000/health')),
        ):
            result = health_check(url)
            print('FAIL' if result else 'PASS', name, result or 'healthy')
            if result: errors.append(name)
        if args.frontend:
            url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
            try:
                with urllib.request.urlopen(url, timeout=8) as response:
                    if response.status >= 400: raise ValueError(f'HTTP {response.status}')
                print('PASS frontend HTTP')
            except (OSError, ValueError) as exc:
                print('FAIL frontend HTTP', exc)
                errors.append('frontend')
    if errors:
        print('NOT READY:', len(errors), 'failed check(s)')
        return 1
    print('PASS requested checks; NOT proof of E2E or production readiness')
    return 0

if __name__ == '__main__':
    sys.exit(main())

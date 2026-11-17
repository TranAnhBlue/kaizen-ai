#!/usr/bin/env python3
"""Opt-in, write-enabled Kaizen acceptance test on a disposable database only."""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from phase19_acceptance import client, request, login, result


def execute(backend, email, password, other_email=None, other_password=None,
            allow_write=False, requester=request, opener_factory=client):
    checks = []
    if not allow_write:
        return [result('write permission', None, 'Explicit --write required; no requests sent')]
    if not email or not password:
        return [result('test account', None, 'TENANT_A_EMAIL and TENANT_A_PASSWORD required')]
    base = backend.rstrip('/') + '/api/v1'
    a = opener_factory()
    code, principal = login(base, email, password, a, requester)
    valid = code == 200 and isinstance(principal, dict) and principal.get('tenantId')
    checks.append(result('tenant A authentication', bool(valid), f'HTTP {code}'))
    if not valid:
        return checks
    marker = 'PHASE21-' + uuid4().hex[:12]
    payload = {'title': marker + ' Kaizen E2E', 'description': 'Disposable acceptance record; do not use in production.'}
    status, created = requester(a, base + '/kaizen', 'POST', payload)
    project_id = created.get('id') if isinstance(created, dict) else None
    checks.append(result('create Kaizen', status in (200, 201) and bool(project_id), f'HTTP {status}'))
    if not project_id:
        return checks
    status, detail = requester(a, base + '/kaizen/' + str(project_id))
    checks.append(result('read created Kaizen', status == 200 and isinstance(detail, dict)
                         and detail.get('title') == payload['title'], f'HTTP {status}'))
    status, submitted = requester(a, base + '/kaizen/' + str(project_id) + '/transition', 'PATCH', {'action': 'SUBMIT'})
    checks.append(result('submit Kaizen', status in (200, 201) and isinstance(submitted, dict)
                         and submitted.get('status') == 'SUBMITTED', f'HTTP {status}'))
    if status in (200, 201):
        code, _ = requester(a, base + '/kaizen/' + str(project_id) + '/transition', 'PATCH', {'action': 'APPROVE'})
        checks.append(result('creator cannot self-approve', code == 403, f'HTTP {code}'))
    else:
        checks.append(result('creator cannot self-approve', None, 'submit failed'))
    if not other_email or not other_password:
        checks.append(result('cross-tenant Kaizen denial', None, 'tenant B credentials required'))
    else:
        b = opener_factory()
        code, other = login(base, other_email, other_password, b, requester)
        if code != 200 or not isinstance(other, dict) or not other.get('tenantId'):
            checks.append(result('cross-tenant Kaizen denial', None, 'tenant B login failed'))
        elif other['tenantId'] == principal['tenantId']:
            checks.append(result('cross-tenant Kaizen denial', False, 'accounts belong to same tenant'))
        else:
            code, _ = requester(b, base + '/kaizen/' + str(project_id))
            checks.append(result('cross-tenant Kaizen denial', code in (403, 404), f'HTTP {code}'))
    return checks


def build_report(checks, backend):
    counts = {status: sum(c['status'] == status for c in checks) for status in ('PASS', 'FAIL', 'SKIP')}
    return {'phase': 21, 'generated_at': datetime.now(timezone.utc).isoformat(),
            'backend': backend, 'mode': 'write-enabled-disposable-test-db',
            'counts': counts, 'checks': checks,
            'limitations': ['Creates persistent Kaizen test records; no automatic deletion',
                            'Does not verify KPI, forecast, RAG or independent security assessment',
                            'Requires real running Backend and PostgreSQL']}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backend', default='http://localhost:3001')
    parser.add_argument('--write', action='store_true', help='Allow creation of persistent test records')
    parser.add_argument('--confirm-disposable-db', action='store_true', help='Confirm non-production database')
    parser.add_argument('--strict', action='store_true')
    parser.add_argument('--output', default='artifacts/phase21-workflow.json')
    args = parser.parse_args(argv)
    if args.write and not args.confirm_disposable_db:
        parser.error('--write requires --confirm-disposable-db')
    checks = execute(args.backend, os.getenv('TENANT_A_EMAIL'), os.getenv('TENANT_A_PASSWORD'),
                     os.getenv('TENANT_B_EMAIL'), os.getenv('TENANT_B_PASSWORD'), args.write)
    report = build_report(checks, args.backend)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    for check in checks:
        print(check['status'], check['name'], check['detail'])
    print('Evidence:', output, 'Counts:', report['counts'])
    return int(bool(report['counts']['FAIL'] or (args.strict and report['counts']['SKIP'])))


if __name__ == '__main__':
    sys.exit(main())

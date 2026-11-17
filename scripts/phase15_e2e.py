#!/usr/bin/env python3
"""Read-only authenticated integration checks; never creates or modifies business data."""
import argparse
import http.cookiejar
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path


def request_json(opener, url, method='GET', payload=None, timeout=12):
    body = json.dumps(payload).encode() if payload is not None else None
    headers = {'Accept': 'application/json'}
    if body is not None:
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with opener.open(req, timeout=timeout) as response:
            data = response.read(100000)
            return response.status, json.loads(data) if data else None
    except urllib.error.HTTPError as exc:
        return exc.code, None
    except (OSError, ValueError):
        return 0, None


def client():
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))


def check(name, actual, expected, detail=''):
    return {'check': name, 'result': 'PASS' if actual == expected else 'FAIL',
            'expected_http': expected, 'actual_http': actual, 'detail': detail}


def run(base, email=None, password=None, other_email=None, other_password=None):
    base = base.rstrip('/') + '/api/v1'
    anonymous = client()
    results = []
    for endpoint in ('auth/me', 'kaizen', 'kpi', 'ai-chat/documents', 'recommendations'):
        code, _ = request_json(anonymous, f'{base}/{endpoint}')
        results.append(check('anonymous denied: ' + endpoint, code, 401))
    if not email or not password:
        results.append({'check': 'authenticated workflow', 'result': 'SKIP', 'reason': 'credentials not supplied'})
        return results
    first = client()
    code, _ = request_json(first, base + '/auth/login', 'POST', {'email': email, 'password': password})
    results.append(check('tenant A login', code, 201))
    if code != 201:
        return results
    code, principal = request_json(first, base + '/auth/me')
    results.append(check('tenant A principal', code, 200))
    if code != 200 or not isinstance(principal, dict) or not principal.get('tenantId'):
        results.append({'check': 'tenant A identity fields', 'result': 'FAIL'})
        return results
    results.append({'check': 'tenant A identity fields', 'result': 'PASS'})
    for endpoint in ('kaizen', 'kpi', 'kpi/definitions', 'ai-chat/documents', 'recommendations'):
        code, data = request_json(first, f'{base}/{endpoint}')
        results.append(check('tenant A read: ' + endpoint, code, 200))
        if code == 200 and isinstance(data, list):
            for item in data:
                if isinstance(item, dict) and item.get('tenantId') not in (None, principal['tenantId']):
                    results.append({'check': 'tenant A list isolation: ' + endpoint, 'result': 'FAIL'})
                    break
    if not other_email or not other_password:
        results.append({'check': 'cross-tenant access', 'result': 'SKIP', 'reason': 'tenant B credentials not supplied'})
        return results
    second = client()
    code, _ = request_json(second, base + '/auth/login', 'POST', {'email': other_email, 'password': other_password})
    results.append(check('tenant B login', code, 201))
    if code != 201:
        return results
    code, other = request_json(second, base + '/auth/me')
    results.append(check('tenant B principal', code, 200))
    if not isinstance(other, dict) or not other.get('tenantId'):
        return results
    results.append({'check': 'distinct tenants', 'result': 'PASS' if other['tenantId'] != principal['tenantId'] else 'FAIL'})
    if other['tenantId'] == principal['tenantId']:
        return results
    code, projects = request_json(first, base + '/kaizen')
    if code == 200 and isinstance(projects, list) and projects:
        target = projects[0].get('id')
        if target:
            code, _ = request_json(second, base + '/kaizen/' + target)
            results.append({'check': 'tenant B cannot read tenant A Kaizen', 'result': 'PASS' if code in (403, 404) else 'FAIL', 'actual_http': code})
    else:
        results.append({'check': 'cross-tenant Kaizen detail', 'result': 'SKIP', 'reason': 'tenant A has no projects'})
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backend', default='http://localhost:3001')
    parser.add_argument('--output', default='artifacts/phase15-e2e.json')
    parser.add_argument('--require-complete', action='store_true', help='fail when any check is skipped')
    args = parser.parse_args(argv)
    results = run(args.backend, os.getenv('TENANT_A_EMAIL'), os.getenv('TENANT_A_PASSWORD'), os.getenv('TENANT_B_EMAIL'), os.getenv('TENANT_B_PASSWORD'))
    report = {'generated_at': datetime.now(timezone.utc).isoformat(), 'backend': args.backend, 'results': results,
              'counts': {status: sum(x['result'] == status for x in results) for status in ('PASS', 'FAIL', 'SKIP')}}
    target = Path(args.output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding='utf-8')
    for item in results:
        print(f"{item['result']:4} {item['check']}")
    print('Evidence:', target)
    return 1 if report['counts']['FAIL'] or (args.require_complete and report['counts']['SKIP']) else 0


if __name__ == '__main__':
    sys.exit(main())

#!/usr/bin/env python3
"""Opt-in read-only API acceptance smoke tests, no credentials logged."""
import argparse
import json
import os
from urllib import request, error
from http.cookiejar import CookieJar

class SmokeFailure(Exception): pass

def fetch(opener, base, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    req = request.Request(base.rstrip('/') + path, data=data,
        headers={'Content-Type':'application/json','Accept':'application/json'},
        method='POST' if payload is not None else 'GET')
    try:
        with opener.open(req, timeout=12) as res:
            body = res.read(2_000_000)
            return res.status, json.loads(body)
    except error.HTTPError as exc:
        return exc.code, None
    except (OSError, ValueError) as exc:
        raise SmokeFailure(f'{path}: {type(exc).__name__}') from exc

def assert_status(name, got, expected):
    if got != expected: raise SmokeFailure(f'{name}: expected HTTP {expected}, got {got}')
    print('PASS', name)

def run(base, email=None, password=None):
    opener=request.build_opener(request.HTTPCookieProcessor(CookieJar()))
    status, _ = fetch(opener,base,'/api/v1/health')
    assert_status('backend health',status,200)
    status, _ = fetch(opener,base,'/api/v1/kaizen')
    assert_status('unauthenticated Kaizen blocked',status,401)
    status, _ = fetch(opener,base,'/api/v1/kpi/definitions')
    assert_status('unauthenticated KPI blocked',status,401)
    if email and password:
        status, result = fetch(opener,base,'/api/v1/auth/login',{'email':email,'password':password})
        assert_status('demo login',status,201)
        status, principal = fetch(opener,base,'/api/v1/auth/me')
        assert_status('authenticated profile',status,200)
        if not isinstance(principal,dict) or not principal.get('tenantId'):
            raise SmokeFailure('profile missing tenantId')
        for name,path in [('Kaizen list','/api/v1/kaizen'),('KPI definitions','/api/v1/kpi/definitions'),('KPI analytics','/api/v1/kpi/analytics'),('forecast history','/api/v1/forecasting/runs')]:
            status,body=fetch(opener,base,path)
            assert_status(name,status,200)
            if not isinstance(body,list): raise SmokeFailure(f'{name}: expected list')
    print('Read-only acceptance smoke checks passed; NOT a full E2E or security assessment')

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--base',default=os.getenv('BACKEND_BASE_URL','http://localhost:3001'))
    p.add_argument('--login',action='store_true',help='Use DEMO_ADMIN_EMAIL and DEMO_ADMIN_PASSWORD from environment')
    args=p.parse_args()
    email=os.getenv('DEMO_ADMIN_EMAIL') if args.login else None
    password=os.getenv('DEMO_ADMIN_PASSWORD') if args.login else None
    if args.login and (not email or not password): p.error('DEMO_ADMIN_EMAIL and DEMO_ADMIN_PASSWORD required')
    try: run(args.base,email,password)
    except SmokeFailure as exc:
        print('FAIL',exc);raise SystemExit(1)
if __name__=='__main__':main()

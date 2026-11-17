#!/usr/bin/env python3
"""Non-destructive HTTP acceptance runner. No user data or secrets in reports."""
import argparse
import json
import os
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from http.cookiejar import CookieJar
from pathlib import Path
from urllib import error, request

@dataclass
class Result:
    name: str
    passed: bool
    detail: str
    duration_ms: int

class HTTPClient:
    def __init__(self, timeout=10):
        self.opener = request.build_opener(request.HTTPCookieProcessor(CookieJar()))
        self.timeout = timeout
    def get(self, url):
        req = request.Request(url, headers={'Accept':'application/json'})
        try:
            with self.opener.open(req, timeout=self.timeout) as resp:
                return resp.status, resp.read(1024 * 1024)
        except error.HTTPError as exc:
            exc.close()
            return exc.code, b''
    def post(self, url, data):
        req = request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type':'application/json'}, method='POST')
        try:
            with self.opener.open(req, timeout=self.timeout) as resp:
                return resp.status, resp.read(1024 * 1024)
        except error.HTTPError as exc:
            exc.close()
            return exc.code, b''

def check(results, name, action, accepted):
    start=time.monotonic()
    try:
        status, body = action()
        passed=status in accepted
        detail=f'HTTP {status}; expected {sorted(accepted)}'
        if passed and status == 200 and name.endswith('health'):
            try:
                passed=isinstance(json.loads(body),dict)
                if not passed: detail='health response must be JSON object'
            except (ValueError,UnicodeDecodeError):
                passed=False;detail='health response is not JSON'
    except (OSError,TimeoutError,ValueError) as exc:
        passed=False;detail=f'connection failed ({type(exc).__name__})'
    results.append(Result(name,passed,detail,int((time.monotonic()-start)*1000)))

def run(backend, ai, frontend=None, email=None, password=None, timeout=10):
    client=HTTPClient(timeout);results=[]
    b=backend.rstrip('/');a=ai.rstrip('/')
    check(results,'backend health',lambda:client.get(b+'/api/v1/health'),{200})
    check(results,'ai health',lambda:client.get(a+'/health'),{200})
    for name,path in [('kaizen','/api/v1/kaizen'),('kpi','/api/v1/kpi/definitions'),('recommendations','/api/v1/recommendations')]:
        check(results,'anonymous '+name+' denied',lambda p=path:client.get(b+p),{401,403})
    if frontend:
        check(results,'frontend reachable',lambda:client.get(frontend.rstrip('/')+'/'),{200,307,308})
    if email and password:
        start=time.monotonic()
        try:
            status,_=client.post(b+'/api/v1/auth/login',{'email':email,'password':password})
            ok=status in (200,201)
            results.append(Result('login',ok,f'HTTP {status}; expected 200/201',int((time.monotonic()-start)*1000)))
        except (OSError,ValueError) as exc:
            ok=False;results.append(Result('login',False,f'connection failed ({type(exc).__name__})',0))
        if ok:
            check(results,'authenticated profile',lambda:client.get(b+'/api/v1/auth/me'),{200})
            for name,path in [('kaizen list','/api/v1/kaizen'),('kpi definitions','/api/v1/kpi/definitions'),('recommendations list','/api/v1/recommendations')]:
                check(results,name,lambda p=path:client.get(b+p),{200})
    return results

def report(results):
    return {'schema_version':1,'generated_at':datetime.now(timezone.utc).isoformat(),
            'passed':sum(r.passed for r in results),'failed':sum(not r.passed for r in results),
            'checks':[asdict(r) for r in results],
            'limitations':['HTTP smoke tests only','No cross-tenant mutation tests','No independent security assessment']}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--backend',default=os.getenv('BACKEND_BASE_URL','http://localhost:3001'))
    p.add_argument('--ai',default=os.getenv('AI_SERVICE_URL','http://localhost:8000'))
    p.add_argument('--frontend',default=None)
    p.add_argument('--login',action='store_true')
    p.add_argument('--timeout',type=int,default=10)
    p.add_argument('--report',default='artifacts/phase12-acceptance.json')
    args=p.parse_args()
    email=os.getenv('DEMO_ADMIN_EMAIL') if args.login else None
    password=os.getenv('DEMO_ADMIN_PASSWORD') if args.login else None
    if args.login and (not email or not password): p.error('Set DEMO_ADMIN_EMAIL and DEMO_ADMIN_PASSWORD')
    results=run(args.backend,args.ai,args.frontend,email,password,args.timeout)
    data=report(results)
    target=Path(args.report);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for r in results: print(('PASS' if r.passed else 'FAIL'),r.name,r.detail)
    print(f"Passed {data['passed']}/{len(results)}; report: {target}")
    raise SystemExit(1 if data['failed'] else 0)
if __name__=='__main__':main()

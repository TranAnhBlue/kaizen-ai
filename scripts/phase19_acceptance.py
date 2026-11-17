#!/usr/bin/env python3
"""Phase 19: read-only business API acceptance checks with evidence and strict gating."""
import argparse
import http.cookiejar
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROUTES = ('kaizen', 'kpi', 'kpi/definitions', 'forecasting/runs', 'recommendations', 'ai-chat/documents', 'ai-chat/conversations')

def client():
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))

def request(opener, url, method='GET', payload=None, timeout=10):
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={'Accept':'application/json', **({'Content-Type':'application/json'} if data is not None else {})})
    try:
        with opener.open(req, timeout=timeout) as res:
            raw=res.read(200000)
            try: parsed=json.loads(raw) if raw else None
            except ValueError: parsed=None
            return res.status, parsed
    except urllib.error.HTTPError as exc:
        return exc.code, None
    except (OSError, TimeoutError):
        return 0, None

def result(name, ok=None, detail=''):
    return {'name':name,'status':'SKIP' if ok is None else ('PASS' if ok else 'FAIL'),'detail':detail}

def login(base, email, password, opener, requester=request):
    code,_=requester(opener,base+'/auth/login','POST',{'email':email,'password':password})
    if code not in (200,201): return code,None
    code,identity=requester(opener,base+'/auth/me')
    return code,identity

def run(backend, email=None, password=None, other_email=None, other_password=None, requester=request, opener_factory=client):
    base=backend.rstrip('/')+'/api/v1'; checks=[]
    anonymous=opener_factory()
    for route in ('auth/me',)+ROUTES:
        status,_=requester(anonymous,base+'/'+route)
        checks.append(result('anonymous blocked '+route,status==401,f'HTTP {status}'))
    if not email or not password:
        checks.append(result('tenant A authenticated API checks',None,'TENANT_A_EMAIL/PASSWORD required'))
        checks.append(result('cross-tenant access',None,'both tenant credentials required'))
        return checks
    a=opener_factory(); code,principal=login(base,email,password,a,requester)
    checks.append(result('tenant A login and principal',code==200 and isinstance(principal,dict) and bool(principal.get('tenantId')),f'HTTP {code}'))
    if code!=200 or not isinstance(principal,dict) or not principal.get('tenantId'):
        checks.append(result('tenant A business reads',None,'login unsuccessful'))
        checks.append(result('cross-tenant access',None,'login unsuccessful'))
        return checks
    tenant=principal['tenantId']; kaizen=[]
    for route in ROUTES:
        status,body=requester(a,base+'/'+route)
        checks.append(result('tenant A read '+route,status==200,f'HTTP {status}'))
        if status==200 and isinstance(body,list):
            checks.append(result('tenant A list isolation '+route,all(not isinstance(x,dict) or x.get('tenantId',tenant)==tenant for x in body),'explicit tenantId fields checked; absent tenantId cannot prove isolation'))
            if route=='kaizen': kaizen=body
    if not other_email or not other_password:
        checks.append(result('cross-tenant access',None,'TENANT_B_EMAIL/PASSWORD required'))
        return checks
    b=opener_factory(); code,other=login(base,other_email,other_password,b,requester)
    valid=code==200 and isinstance(other,dict) and bool(other.get('tenantId'))
    checks.append(result('tenant B login and principal',valid,f'HTTP {code}'))
    if not valid:
        checks.append(result('cross-tenant access',None,'tenant B login unsuccessful'))
        return checks
    distinct=tenant!=other['tenantId']; checks.append(result('distinct tenants',distinct))
    if not distinct: return checks
    target=next((x.get('id') for x in kaizen if isinstance(x,dict) and x.get('id')),None)
    if not target:
        checks.append(result('tenant B cannot read tenant A Kaizen',None,'tenant A needs at least one Kaizen'))
    else:
        status,_=requester(b,base+'/kaizen/'+str(target))
        checks.append(result('tenant B cannot read tenant A Kaizen',status in (403,404),f'HTTP {status}'))
    return checks

def report(checks, backend):
    counts={s:sum(c['status']==s for c in checks) for s in ('PASS','FAIL','SKIP')}
    return {'phase':19,'generated_at':datetime.now(timezone.utc).isoformat(),'backend':backend,'mode':'read-only','counts':counts,'checks':checks,'limitations':['GET checks do not prove POST/PATCH workflow success','Absent tenantId fields do not establish tenant isolation','Live results require running services and seeded test accounts']}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--backend',default='http://localhost:3001')
    p.add_argument('--output',default='artifacts/phase19-acceptance.json')
    p.add_argument('--require-complete',action='store_true')
    args=p.parse_args(argv)
    checks=run(args.backend,os.getenv('TENANT_A_EMAIL'),os.getenv('TENANT_A_PASSWORD'),os.getenv('TENANT_B_EMAIL'),os.getenv('TENANT_B_PASSWORD'))
    data=report(checks,args.backend); path=Path(args.output); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    for c in checks: print(f"{c['status']:4} {c['name']} {c['detail']}")
    print('Counts:',data['counts'],'Evidence:',path)
    return int(bool(data['counts']['FAIL'] or (args.require_complete and data['counts']['SKIP'])))

if __name__=='__main__': sys.exit(main())

#!/usr/bin/env python3
"""Read-only multi-tenant security acceptance checks. Use TWO isolated demo tenants.

Never runs writes, destructive operations, or outputs credentials / response bodies.
Exit 0 only when all checks pass; missing prerequisites exit nonzero.
"""
import argparse
import json
import os
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from http.cookiejar import CookieJar
from pathlib import Path
from urllib import request, error

@dataclass
class Finding:
    check: str
    outcome: str
    detail: str

class Client:
    def __init__(self, timeout=10):
        self.timeout=timeout
        self.opener=request.build_opener(request.HTTPCookieProcessor(CookieJar()))
    def call(self, method, url, data=None):
        body=None if data is None else json.dumps(data).encode('utf-8')
        req=request.Request(url,data=body,method=method,headers={'Accept':'application/json','Content-Type':'application/json'})
        try:
            with self.opener.open(req,timeout=self.timeout) as response:
                return response.status,response.read(2_000_000)
        except error.HTTPError as exc:
            exc.close()
            return exc.code,b''

def safe_json(raw):
    try: return json.loads(raw)
    except (ValueError,TypeError,UnicodeDecodeError): return None

def assess(base, first, second, timeout=10):
    base=base.rstrip('/'); a=Client(timeout); b=Client(timeout); findings=[]
    def add(name,ok,detail):findings.append(Finding(name,'PASS' if ok else 'FAIL',detail))
    for label,client,creds in [('A',a,first),('B',b,second)]:
        status,_=client.call('POST',base+'/api/v1/auth/login',{'email':creds[0],'password':creds[1]})
        add('login '+label,status in (200,201),'HTTP '+str(status))
    if any(f.outcome=='FAIL' for f in findings): return findings
    sa,rawa=a.call('GET',base+'/api/v1/auth/me'); sb,rawb=b.call('GET',base+'/api/v1/auth/me')
    pa,pb=safe_json(rawa),safe_json(rawb)
    ids=pa.get('tenantId') if isinstance(pa,dict) else None
    idb=pb.get('tenantId') if isinstance(pb,dict) else None
    distinct=sa==200 and sb==200 and bool(ids) and bool(idb) and ids!=idb
    add('different tenant identities',distinct,'Both profiles must have different tenantId values')
    if not distinct: return findings
    for name,path in [('kaizen','/api/v1/kaizen'),('kpi','/api/v1/kpi/definitions'),('recommendations','/api/v1/recommendations')]:
        s1,r1=a.call('GET',base+path);s2,r2=b.call('GET',base+path)
        x,y=safe_json(r1),safe_json(r2)
        good=s1==200 and s2==200 and isinstance(x,list) and isinstance(y,list)
        add(name+' lists accessible',good,f'A HTTP {s1}; B HTTP {s2}; expected arrays')
        if not good: continue
        # All returned tenantId fields must match the authenticated tenant.
        for label,items,tid in [('A',x,ids),('B',y,idb)]:
            mismatches=[row for row in items if isinstance(row,dict) and row.get('tenantId') is not None and row['tenantId']!=tid]
            add(name+' tenant-scoped '+label,not mismatches,f'{len(items)} items inspected; {len(mismatches)} mismatches')
        if name=='kaizen':
            for label,foreign,client in [('A cannot read B',y,a),('B cannot read A',x,b)]:
                # Without an existing foreign record, do not claim cross-tenant isolation passed.
                item=next((row for row in foreign if isinstance(row,dict) and isinstance(row.get('id'),str)),None)
                if item is None:
                    findings.append(Finding('kaizen detail '+label,'SKIP','No foreign Kaizen record: seed both tenants and rerun'))
                    continue
                status,_=client.call('GET',base+'/api/v1/kaizen/'+item['id'])
                add('kaizen detail '+label,status in (403,404),f'HTTP {status}; expected 403/404')
    unauth=Client(timeout)
    for name,path in [('kaizen','/api/v1/kaizen'),('kpi','/api/v1/kpi/definitions'),('recommendations','/api/v1/recommendations')]:
        status,_=unauth.call('GET',base+path)
        add('anonymous denied '+name,status in (401,403),f'HTTP {status}; expected 401/403')
    return findings

def summarize(findings):
    return {'schema_version':1,'generated_at':datetime.now(timezone.utc).isoformat(),
            'passed':sum(f.outcome=='PASS' for f in findings),
            'failed':sum(f.outcome=='FAIL' for f in findings),
            'skipped':sum(f.outcome=='SKIP' for f in findings),
            'checks':[asdict(f) for f in findings],
            'limitations':['Read-only checks; not a penetration test','Only Kaizen detail endpoint tested across tenants','No independent assessment']}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--backend',default=os.getenv('BACKEND_BASE_URL','http://localhost:3001'))
    p.add_argument('--report',default='artifacts/phase13-security.json')
    p.add_argument('--timeout',type=int,default=10)
    args=p.parse_args()
    names=['TENANT_A_EMAIL','TENANT_A_PASSWORD','TENANT_B_EMAIL','TENANT_B_PASSWORD']
    missing=[n for n in names if not os.getenv(n)]
    if missing:p.error('Missing environment variables: '+', '.join(missing))
    try:
        findings=assess(args.backend,(os.environ[names[0]],os.environ[names[1]]),(os.environ[names[2]],os.environ[names[3]]),args.timeout)
    except (OSError,TimeoutError,ValueError) as exc:
        findings=[Finding('connection','FAIL','Network or response error: '+type(exc).__name__)]
    result=summarize(findings)
    target=Path(args.report);target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for finding in findings:print(finding.outcome,finding.check,finding.detail)
    print(f"PASS {result['passed']} / FAIL {result['failed']} / SKIP {result['skipped']}; report {target}")
    sys.exit(1 if result['failed'] or result['skipped'] else 0)
if __name__=='__main__':main()

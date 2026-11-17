#!/usr/bin/env python3
"""Evidence-based RC gate. No successful live tests are assumed or simulated."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from phase19_acceptance import run as business_checks

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ROOT / 'devops/compose/compose.full.yml'
REQUIRED = ('frontend/package.json','backend/package.json','backend/prisma/schema.prisma',
            'ai-service/pyproject.toml','devops/compose/compose.full.yml')

def check(name, status, detail='', category='static'):
    assert status in ('PASS','FAIL','SKIP')
    return {'name':name,'status':status,'detail':detail,'category':category}

def execute(args, cwd=ROOT, timeout=180):
    try:
        proc=subprocess.run(args,cwd=cwd,capture_output=True,text=True,timeout=timeout,check=False)
        return proc.returncode, (proc.stdout+'\n'+proc.stderr)[-3000:]
    except (OSError,subprocess.TimeoutExpired) as e:
        return 127,str(e)

def live_health(url, timeout=5):
    try:
        with urlopen(url,timeout=timeout) as res:
            return 200<=res.status<400, 'HTTP '+str(res.status)
    except (OSError,HTTPError,URLError,TimeoutError) as e:
        return False,type(e).__name__

def static_checks(root=ROOT):
    return [check('file '+f,'PASS' if (root/f).is_file() else 'FAIL') for f in REQUIRED]

def summarize(checks, strict=True):
    counts={status:sum(c['status']==status for c in checks) for status in ('PASS','FAIL','SKIP')}
    accepted=counts['FAIL']==0 and (not strict or counts['SKIP']==0) and counts['PASS']>0
    return counts,accepted

def render_md(data):
    rows=['# Kaizen AI - Phase 20 release evidence','',
          'Generated (UTC): '+data['generated_at'],'',
          '**RC status: '+('PASS' if data['release_candidate_accepted'] else 'NOT ACCEPTED')+'**','',
          '| Check | Category | Status | Detail |','|---|---|---|---|']
    for c in data['checks']:
        safe=lambda v:str(v).replace('|','/').replace('\n',' ')[:180]
        rows.append('| '+ ' | '.join(safe(c[k]) for k in ('name','category','status','detail'))+' |')
    rows += ['','## Limitations','- This gate does not replace manual E2E, penetration testing, or independent security assessment.',
             '- A PASS only covers the explicitly executed checks.']
    return '\n'.join(rows)+'\n'

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--live',action='store_true',help='Run HTTP and authenticated business checks')
    p.add_argument('--docker',action='store_true',help='Check Docker Compose config and container state')
    p.add_argument('--build',action='store_true',help='Run local npm builds; requires installed dependencies')
    p.add_argument('--output',default='artifacts/phase20-release.json')
    p.add_argument('--markdown',default='artifacts/phase20-release.md')
    p.add_argument('--strict',action='store_true',help='Require all live, Docker, and build checks')
    args=p.parse_args(argv)
    checks=static_checks()
    if args.docker:
        rc,output=execute(['docker','compose','-f',str(COMPOSE),'config','-q'])
        checks.append(check('Docker Compose configuration','PASS' if rc==0 else 'FAIL',output[-300:], 'docker'))
        rc,output=execute(['docker','compose','-f',str(COMPOSE),'ps','--format','json'])
        checks.append(check('Docker Compose running services','PASS' if rc==0 and 'backend' in output and 'frontend' in output and 'ai-service' in output else 'FAIL',output[-300:],'docker'))
    else:
        checks.append(check('Docker Compose runtime','SKIP','Pass --docker and configure required environment','docker'))
    if args.build:
        for component in ('backend','frontend'):
            rc,output=execute(['npm','run','build'],ROOT/component,240)
            checks.append(check(component+' npm build','PASS' if rc==0 else 'FAIL',output[-400:],'build'))
    else:
        checks.append(check('Next.js and NestJS build','SKIP','Pass --build after installing dependencies','build'))
    if args.live:
        for name,url in [('frontend','http://localhost:3000'),('backend','http://localhost:3001/api/v1/health'),('ai-service','http://localhost:8000/health')]:
            ok,detail=live_health(url)
            checks.append(check(name+' HTTP health','PASS' if ok else 'FAIL',detail,'live'))
        checks += [dict(c,category='business') for c in business_checks('http://localhost:3001',os.getenv('TENANT_A_EMAIL'),os.getenv('TENANT_A_PASSWORD'),os.getenv('TENANT_B_EMAIL'),os.getenv('TENANT_B_PASSWORD'))]
    else:
        checks.append(check('Authenticated business acceptance','SKIP','Pass --live with two test tenant accounts','business'))
    counts,accepted=summarize(checks,strict=True)
    if args.strict and not(args.live and args.docker and args.build): accepted=False
    data={'phase':20,'generated_at':datetime.now(timezone.utc).isoformat(),
          'release_candidate_accepted':accepted,'counts':counts,'checks':checks,
          'execution':{'live':args.live,'docker':args.docker,'build':args.build},
          'limitations':['Does not cover all write workflows','Independent security assessment not performed']}
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf-8')
    md=Path(args.markdown);md.parent.mkdir(parents=True,exist_ok=True);md.write_text(render_md(data),encoding='utf-8')
    print('RC:', 'ACCEPTED' if accepted else 'NOT ACCEPTED', 'counts:',counts)
    print('Evidence:',out,md)
    return 0 if accepted else 1

if __name__=='__main__': sys.exit(main())

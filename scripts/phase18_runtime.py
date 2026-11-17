#!/usr/bin/env python3
"""Phase 18: honest release readiness report. No simulated passing live checks."""
import argparse, json, os, shutil, subprocess, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
URLS = {'frontend':'http://127.0.0.1:3000/', 'backend':'http://127.0.0.1:3001/api/v1/health', 'ai-service':'http://127.0.0.1:8000/health'}

def record(name, status, detail=''):
    return {'name':name, 'status':status, 'detail':detail}

def static_checks(root=ROOT):
    out=[]
    for name, rel in [('frontend package','frontend/package.json'),('backend package','backend/package.json'),('Prisma schema','backend/prisma/schema.prisma'),('AI service','ai-service/app/main.py'),('full compose','devops/compose/compose.full.yml'),('frontend Dockerfile','devops/docker/frontend.Dockerfile'),('backend Dockerfile','devops/docker/backend.Dockerfile')]:
        out.append(record(name,'PASS' if (root/rel).is_file() else 'FAIL',rel))
    cfg=root/'frontend/next.config.ts'
    out.append(record('standalone output','PASS' if cfg.is_file() and "output: 'standalone'" in cfg.read_text() else 'FAIL'))
    docker=root/'devops/docker/frontend.Dockerfile'
    out.append(record('standalone Docker runtime','PASS' if docker.is_file() and 'server.js' in docker.read_text() else 'FAIL'))
    return out

def live_checks(urls=URLS):
    out=[]
    for name,url in urls.items():
        try:
            with urllib.request.urlopen(url,timeout=4) as response:
                code=response.status
            out.append(record(name,'PASS' if 200<=code<300 else 'FAIL',f'HTTP {code}'))
        except Exception as exc:
            out.append(record(name,'FAIL',type(exc).__name__))
    return out

def docker_checks(root=ROOT):
    if not shutil.which('docker'):
        return [record('Docker available','FAIL','Docker CLI not found')]
    compose=['docker','compose','--env-file','.env.phase14','-f','devops/compose/compose.full.yml']
    if not (root/'.env.phase14').exists():
        return [record('Docker environment','FAIL','Create .env.phase14 from .env.phase14.example')]
    out=[]
    for name,command in [('Compose configuration',compose+['config','-q']),('Compose services',compose+['ps','--status','running'])]:
        try:
            result=subprocess.run(command,cwd=root,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=30)
            out.append(record(name,'PASS' if result.returncode==0 else 'FAIL',('exit '+str(result.returncode)) if result.returncode else 'command succeeded'))
        except (OSError,subprocess.TimeoutExpired) as exc:
            out.append(record(name,'FAIL',type(exc).__name__))
    return out

def main(argv=None):
    parser=argparse.ArgumentParser()
    parser.add_argument('--live',action='store_true')
    parser.add_argument('--docker',action='store_true')
    parser.add_argument('--require-live',action='store_true',help='require both --live and --docker and successful checks')
    parser.add_argument('--output',default='artifacts/phase18-readiness.json')
    args=parser.parse_args(argv)
    checks=static_checks()
    if args.live: checks+=live_checks()
    if args.docker: checks+=docker_checks()
    if args.require_live and not (args.live and args.docker):
        checks.append(record('required runtime coverage','FAIL','Use --live --docker together'))
    passed=all(x['status']=='PASS' for x in checks)
    verified=passed and args.live and args.docker
    report={'phase':18,'timestamp':datetime.now(timezone.utc).isoformat(),'checks':checks,'runtime_verified':verified,'independent_security_assessment_completed':False,'note':'HTTP and Compose checks are readiness signals, not full E2E acceptance.'}
    target=Path(args.output)
    if not target.is_absolute(): target=ROOT/target
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    for item in checks: print(item['status'],item['name'],item['detail'])
    print('Runtime verified:',verified,'Evidence:',target)
    return 0 if passed and (not args.require_live or verified) else 1
if __name__=='__main__': sys.exit(main())

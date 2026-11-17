#!/usr/bin/env python3
"""Offline consistency checks and optional live HTTP readiness checks."""
import argparse
import json
import re
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def inspect(root=ROOT):
    findings=[]
    def add(name, passed, detail=''):
        findings.append({'check':name,'status':'PASS' if passed else 'FAIL','detail':detail})
    init=(root/'backend/prisma/migrations/20261115000000_init/migration.sql').read_text()
    vector=(root/'backend/prisma/migrations/20261115060000_rag_vector/migration.sql').read_text()
    add('initial vector column exists',bool(re.search(r'"embedding"\s+vector\(768\)',init)))
    add('later migration alters dimension instead of adding duplicate',
        'ALTER COLUMN "embedding" TYPE vector(1536)' in vector and
        not bool(re.search(r'ADD COLUMN\s+"embedding"',vector,re.I)))
    add('vector index created', 'USING hnsw' in vector and 'vector_cosine_ops' in vector)
    docker=(root/'devops/docker/frontend.Dockerfile').read_text()
    add('standalone frontend runtime', 'server.js' in docker and '/app/.next/standalone' in docker)
    add('frontend public directory', (root/'frontend/public').is_dir())
    compose=(root/'devops/compose/compose.full.yml').read_text()
    for service in ('postgres','redis','migrate','backend','ai-service','frontend'):
        add('compose '+service, bool(re.search(r'^  '+re.escape(service)+r':',compose,re.M)))
    add('migration before backend','service_completed_successfully' in compose)
    return findings

def live_checks(timeout=5):
    out=[]
    for name,url in [('frontend','http://127.0.0.1:3000'),('backend','http://127.0.0.1:3001/api/v1/health'),('ai-service','http://127.0.0.1:8000/health')]:
        try:
            with urllib.request.urlopen(url,timeout=timeout) as r:
                ok=200<=r.status<300
                detail='HTTP '+str(r.status)
        except (OSError,ValueError,urllib.error.HTTPError) as e:
            ok=False;detail=type(e).__name__
        out.append({'check':'live '+name,'status':'PASS' if ok else 'FAIL','detail':detail})
    return out

def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument('--live',action='store_true')
    p.add_argument('--output',default='artifacts/phase17-diagnostics.json')
    args=p.parse_args(argv)
    findings=inspect()+(live_checks() if args.live else [])
    result={'phase':17,'timestamp':datetime.now(timezone.utc).isoformat(),'live_requested':args.live,
            'checks':findings,'release_candidate_verified':False,
            'note':'Static validation does not certify runtime integration or independent security assessment.'}
    path=ROOT/args.output;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    for r in findings: print(r['status'],r['check'],r['detail'])
    print('Evidence:',path)
    return int(any(r['status']=='FAIL' for r in findings))
if __name__=='__main__': sys.exit(main())

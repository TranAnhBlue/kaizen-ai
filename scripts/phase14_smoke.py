#!/usr/bin/env python3
"""Non-destructive integration smoke test. Writes an evidence JSON artifact."""
import argparse,json,os,sys,urllib.error,urllib.request
from datetime import datetime,timezone
from pathlib import Path

def probe(name,url,expected_service=None,timeout=6):
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'Accept':'application/json'}),timeout=timeout) as r:
            status=r.status; content=r.read(10000)
        if status!=200: return {'name':name,'status':'FAIL','http':status}
        if expected_service:
            data=json.loads(content)
            if data.get('status')!='ok' or data.get('service')!=expected_service:
                return {'name':name,'status':'FAIL','reason':'unexpected health payload'}
        return {'name':name,'status':'PASS','http':status}
    except (OSError,ValueError,urllib.error.HTTPError) as exc:
        return {'name':name,'status':'FAIL','reason':type(exc).__name__}

def run(frontend,backend,ai):
    return [probe('frontend',frontend),probe('backend',backend+'/api/v1/health','kaizen-api'),probe('ai-service',ai+'/health','kaizen-ai')]

def main():
    p=argparse.ArgumentParser();p.add_argument('--frontend',default='http://localhost:3000');p.add_argument('--backend',default='http://localhost:3001');p.add_argument('--ai',default='http://localhost:8000');p.add_argument('--output',default='artifacts/phase14-smoke.json');args=p.parse_args()
    results=run(args.frontend,args.backend,args.ai)
    report={'timestamp':datetime.now(timezone.utc).isoformat(),'checks':results,'passed':sum(x['status']=='PASS' for x in results),'total':len(results)}
    path=Path(args.output);path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(report,indent=2),encoding='utf8')
    for item in results: print(f"{item['status']:4} {item['name']}")
    print('Evidence:',path)
    return 0 if report['passed']==report['total'] else 1
if __name__=='__main__':sys.exit(main())

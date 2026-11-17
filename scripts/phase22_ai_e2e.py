#!/usr/bin/env python3
"""Opt-in disposable-DB AI business workflow acceptance; creates persistent records."""
import argparse
import base64
import json
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4
from phase19_acceptance import client, request, login, result


def run(backend, email, password, *, allow_write=False, requester=request, opener_factory=client):
    if not allow_write:
        return [result('write authorization', None, 'Requires --write and --confirm-disposable-db')]
    if not email or not password:
        return [result('credentials', None, 'TENANT_A_EMAIL and TENANT_A_PASSWORD required')]
    base = backend.rstrip('/') + '/api/v1'
    c = opener_factory()
    code, identity = login(base, email, password, c, requester)
    checks = [result('authenticated tenant', code == 200 and isinstance(identity, dict) and bool(identity.get('tenantId')), f'HTTP {code}')]
    if checks[-1]['status'] != 'PASS':
        return checks
    marker = uuid4().hex[:12].upper()
    metric = 'P22_' + marker
    def call(name, path, method='GET', data=None, validator=None):
        status, payload = requester(c, base + path, method, data)
        ok = validator(status, payload) if validator else status in (200, 201)
        checks.append(result(name, ok, f'HTTP {status}'))
        return payload if ok else None
    definition = call('create KPI definition', '/kpi/definitions', 'POST', {
        'code': metric, 'name': 'Phase22 productivity ' + marker, 'unit': 'items/hour',
        'direction': 'HIGHER_BETTER', 'target': 100, 'warningMin': 95
    }, lambda s, p: s in (200,201) and isinstance(p,dict) and p.get('code') == metric)
    if not definition:
        return checks
    start = datetime.now(timezone.utc).date() - timedelta(days=9)
    for i in range(8):
        day = start + timedelta(days=i)
        saved = call('KPI observation ' + str(i + 1), '/kpi', 'POST', {
            'metric': metric, 'unit': 'items/hour', 'value': 92 + i * 0.4,
            'recordedAt': day.isoformat() + 'T12:00:00Z'
        }, lambda s,p: s in (200,201) and isinstance(p,dict) and p.get('metric') == metric)
        if saved is None:
            checks.append(result('forecast', None, 'KPI series incomplete'))
            checks.append(result('recommendations', None, 'forecast unavailable'))
            break
    else:
        forecast = call('forecast from 8 days', '/forecasting/predict', 'POST', {'code':metric,'horizon':3},
                        lambda s,p: s in (200,201) and isinstance(p,dict) and bool(p.get('id')) and len(p.get('values',[]))==3)
        if forecast:
            recommendations = call('generate recommendations', '/recommendations/generate', 'POST', {'forecastRunId':forecast['id']},
                                   lambda s,p: s in (200,201) and isinstance(p,list))
            if recommendations is not None:
                checks.append(result('recommendation output assessed', bool(recommendations),
                                     'Rule engine returned ' + str(len(recommendations)) + ' proposal(s); empty list is a functional outcome but no proposal can be reviewed'))
        else:
            checks.append(result('recommendations', None, 'forecast unavailable'))
    document = ('Phase 22 internal demonstration document. The improvement team checks '
                'the productivity indicator every day and investigates recurring losses. '
                'A corrective action requires manager review. Reference ' + marker + '.')
    uploaded = call('upload RAG source document', '/ai-chat/documents', 'POST', {
        'title': 'Phase22 evidence ' + marker, 'mimeType': 'text/plain',
        'contentBase64': base64.b64encode(document.encode()).decode()
    }, lambda s,p: s in (200,201) and isinstance(p,dict) and bool(p.get('id')))
    if uploaded:
        response = call('ask RAG question', '/ai-chat/ask', 'POST', {
            'question': 'According to the Phase 22 demonstration document, what must the improvement team check?'
        }, lambda s,p: s in (200,201) and isinstance(p,dict) and bool(p.get('answer')) and isinstance(p.get('citations'),list))
        if response is not None:
            matching = any(isinstance(x,dict) and x.get('documentId') == uploaded['id'] for x in response['citations'])
            checks.append(result('RAG cites uploaded document', matching, 'Checks documentId in citations; does not grade factual answer'))
    else:
        checks.append(result('ask RAG question', None, 'upload failed'))
        checks.append(result('RAG cites uploaded document', None, 'upload failed'))
    return checks


def report(checks, backend):
    counts = {s:sum(x['status']==s for x in checks) for s in ('PASS','FAIL','SKIP')}
    return {'phase':22,'generated_at':datetime.now(timezone.utc).isoformat(),
            'backend':backend,'mode':'disposable-database-write-test','counts':counts,'checks':checks,
            'limitations':['Persistent test data is created and not removed automatically',
                           'Recommendation output may be empty depending on forecast rules',
                           'RAG citation match does not prove factual accuracy or embedding use',
                           'Live Docker, PostgreSQL and AI service required',
                           'Independent security assessment not performed']}


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--backend',default='http://localhost:3001')
    p.add_argument('--write',action='store_true')
    p.add_argument('--confirm-disposable-db',action='store_true')
    p.add_argument('--strict',action='store_true')
    p.add_argument('--output',default='artifacts/phase22-ai-e2e.json')
    args=p.parse_args(argv)
    if args.write and not args.confirm_disposable_db:
        p.error('--write requires --confirm-disposable-db')
    checks=run(args.backend,os.getenv('TENANT_A_EMAIL'),os.getenv('TENANT_A_PASSWORD'),allow_write=args.write)
    evidence=report(checks,args.backend)
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf-8')
    for c in checks:print(c['status'],c['name'],c['detail'])
    print('Evidence:',out,'Counts:',evidence['counts'])
    return int(bool(evidence['counts']['FAIL'] or (args.strict and evidence['counts']['SKIP'])))

if __name__=='__main__':
    sys.exit(main())

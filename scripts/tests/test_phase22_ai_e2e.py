import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from phase22_ai_e2e import run, report, main

class Phase22Tests(unittest.TestCase):
    def test_default_does_not_send_requests(self):
        def forbidden(*args,**kwargs): raise AssertionError('request made')
        self.assertEqual(run('http://localhost:3001',None,None,requester=forbidden)[0]['status'],'SKIP')
    def test_missing_credentials(self):
        self.assertEqual(run('http://localhost:3001',None,None,allow_write=True)[0]['status'],'SKIP')
    def test_login_failure_short_circuits(self):
        def fake(opener,url,method='GET',payload=None): return (401,None)
        checks=run('http://localhost:3001','a','b',allow_write=True,requester=fake,opener_factory=lambda:object())
        self.assertEqual(len(checks),1)
        self.assertEqual(checks[0]['status'],'FAIL')
    def test_report_counts(self):
        checks=[{'status':'PASS'},{'status':'SKIP'},{'status':'FAIL'}]
        self.assertEqual(report(checks,'x')['counts'],{'PASS':1,'FAIL':1,'SKIP':1})
    def test_confirm_required(self):
        with self.assertRaises(SystemExit) as err:main(['--write'])
        self.assertEqual(err.exception.code,2)
    def test_forecast_and_rag_path(self):
        calls=[]
        def fake(opener,url,method='GET',payload=None):
            calls.append((url,method,payload))
            if url.endswith('/auth/login'):return 201,{}
            if url.endswith('/auth/me'):return 200,{'tenantId':'tenant-a'}
            if url.endswith('/kpi/definitions'):return 201,{'code':payload['code']}
            if url.endswith('/kpi'):return 201,{'metric':payload['metric']}
            if url.endswith('/forecasting/predict'):return 201,{'id':'forecast-id','values':[1,2,3]}
            if url.endswith('/recommendations/generate'):return 201,[{'id':'rec-id'}]
            if url.endswith('/ai-chat/documents'):return 201,{'id':'doc-id'}
            if url.endswith('/ai-chat/ask'):return 201,{'answer':'Daily productivity','citations':[{'documentId':'doc-id'}]}
            raise AssertionError(url)
        checks=run('http://localhost:3001','a','b',allow_write=True,requester=fake,opener_factory=lambda:object())
        self.assertEqual({x['status'] for x in checks},{'PASS'})
        self.assertEqual(len([x for x in calls if x[0].endswith('/kpi')]),8)
        self.assertTrue(any(x[0].endswith('/ai-chat/ask') for x in calls))
    def test_no_recommendation_is_explicit_fail(self):
        def fake(opener,url,method='GET',payload=None):
            if url.endswith('/auth/login'):return 201,{}
            if url.endswith('/auth/me'):return 200,{'tenantId':'tenant-a'}
            if url.endswith('/kpi/definitions'):return 201,{'code':payload['code']}
            if url.endswith('/kpi'):return 201,{'metric':payload['metric']}
            if url.endswith('/forecasting/predict'):return 201,{'id':'forecast-id','values':[1,2,3]}
            if url.endswith('/recommendations/generate'):return 201,[]
            if url.endswith('/ai-chat/documents'):return 400,None
            raise AssertionError(url)
        checks=run('http://localhost:3001','a','b',allow_write=True,requester=fake,opener_factory=lambda:object())
        self.assertTrue(any(x['name']=='recommendation output assessed' and x['status']=='FAIL' for x in checks))
        self.assertTrue(any(x['name']=='ask RAG question' and x['status']=='SKIP' for x in checks))

if __name__=='__main__':unittest.main()

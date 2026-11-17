import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('phase12',Path(__file__).resolve().parents[1]/'phase12_e2e.py')
import sys
module=importlib.util.module_from_spec(spec)
sys.modules[spec.name]=module
spec.loader.exec_module(module)

class FakeClient:
    def __init__(self,timeout=10): self.logged=False
    def get(self,url):
        if url.endswith('/health'):return 200,b'{"status":"ok"}'
        if url.endswith('/api/v1/health'):return 200,b'{"status":"ok"}'
        if url.endswith('/'):return 200,b'<html></html>'
        if not self.logged:return 401,b''
        return 200,b'[]'
    def post(self,url,data):
        self.logged=True
        return 201,b'{}'

class Phase12Tests(unittest.TestCase):
    @patch.object(module,'HTTPClient',FakeClient)
    def test_anonymous_checks(self):
        checks=module.run('http://localhost:3001','http://localhost:8000')
        self.assertEqual(len(checks),5)
        self.assertTrue(all(c.passed for c in checks))
    @patch.object(module,'HTTPClient',FakeClient)
    def test_authenticated_checks(self):
        checks=module.run('http://localhost:3001','http://localhost:8000',email='demo@example.org',password='not-a-real-secret')
        self.assertEqual(len(checks),10)
        self.assertTrue(all(c.passed for c in checks))
    def test_health_rejects_invalid_json(self):
        checks=[]
        module.check(checks,'backend health',lambda:(200,b'not json'),{200})
        self.assertFalse(checks[0].passed)
    def test_connection_failure_is_reported(self):
        checks=[]
        module.check(checks,'offline',lambda:(_ for _ in ()).throw(OSError('secret value')),{200})
        self.assertFalse(checks[0].passed)
        self.assertNotIn('secret value',checks[0].detail)
    def test_report_is_serializable_and_safe(self):
        output=module.report([module.Result('check',False,'HTTP 401',1)])
        self.assertEqual(output['failed'],1)
        self.assertEqual(json.loads(json.dumps(output))['checks'][0]['name'],'check')
    def test_bad_status_fails(self):
        checks=[]
        module.check(checks,'anonymous kaizen denied',lambda:(200,b'[]'),{401,403})
        self.assertFalse(checks[0].passed)

if __name__=='__main__':unittest.main()

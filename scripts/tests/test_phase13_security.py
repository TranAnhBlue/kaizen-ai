import importlib.util
import json
import unittest
from pathlib import Path
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('phase13_security',Path(__file__).resolve().parents[1]/'phase13_security.py')
module=importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name]=module
spec.loader.exec_module(module)

class FakeClient:
    next_index=0
    def __init__(self,timeout=10):
        self.idx=FakeClient.next_index;FakeClient.next_index+=1
    def call(self,method,url,data=None):
        if url.endswith('/auth/login'):return 201,b'{}'
        if url.endswith('/auth/me'):return 200,json.dumps({'tenantId':['tenant-a','tenant-b'][self.idx]}).encode()
        if url.endswith('/kaizen'):
            if self.idx==2:return 401,b''
            return 200,json.dumps([{'id':['id-a','id-b'][self.idx],'tenantId':['tenant-a','tenant-b'][self.idx]}]).encode()
        if url.endswith('/kpi/definitions') or url.endswith('/recommendations'):
            if self.idx==2:return 401,b''
            return 200,b'[]'
        if '/kaizen/id-' in url:return 404,b''
        raise AssertionError(url)

class SecurityTests(unittest.TestCase):
    def setUp(self):FakeClient.next_index=0
    def test_isolation_positive(self):
        with patch.object(module,'Client',FakeClient):
            checks=module.assess('http://example',('a','p'),('b','p'))
        self.assertTrue(checks)
        self.assertTrue(all(c.outcome=='PASS' for c in checks))
        self.assertEqual(module.summarize(checks)['failed'],0)
    def test_same_tenant_rejected(self):
        class Same(FakeClient):
            def call(self,method,url,data=None):
                if url.endswith('/auth/me'):return 200,b'{"tenantId":"same"}'
                return super().call(method,url,data)
        with patch.object(module,'Client',Same):
            checks=module.assess('http://example',('a','p'),('b','p'))
        self.assertEqual(checks[-1].outcome,'FAIL')
    def test_no_secrets_in_report(self):
        report=module.summarize([module.Finding('example','PASS','HTTP 200')])
        self.assertEqual(report['passed'],1)
        self.assertNotIn('password',json.dumps(report))
    def test_invalid_json(self):self.assertIsNone(module.safe_json(b'not-json'))
    def test_skipped_is_explicit(self):
        r=module.summarize([module.Finding('detail','SKIP','no record')])
        self.assertEqual(r['skipped'],1)

if __name__=='__main__':unittest.main()

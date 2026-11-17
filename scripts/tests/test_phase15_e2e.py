import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('phase15_e2e', Path(__file__).resolve().parents[1] / 'phase15_e2e.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class E2ETests(unittest.TestCase):
    def test_check_pass(self):
        self.assertEqual(mod.check('x', 401, 401)['result'], 'PASS')
    def test_check_fail(self):
        self.assertEqual(mod.check('x', 200, 401)['result'], 'FAIL')
    def test_anonymous_denied(self):
        with patch.object(mod, 'request_json', return_value=(401, None)):
            rows = mod.run('http://localhost:3001')
        self.assertEqual(sum(r['result'] == 'PASS' for r in rows), 5)
        self.assertEqual(rows[-1]['result'], 'SKIP')
    def test_unprotected_api_fails(self):
        with patch.object(mod, 'request_json', return_value=(200, [])):
            rows = mod.run('http://localhost:3001')
        self.assertEqual(sum(r['result'] == 'FAIL' for r in rows), 5)
    def test_login_failure_stops(self):
        with patch.object(mod, 'request_json', side_effect=[(401, None)]*5+[(401, None)]):
            rows = mod.run('http://localhost:3001', 'a@example.com', 'bad')
        self.assertEqual(rows[-1]['check'], 'tenant A login')
    def test_cross_tenant_denied(self):
        answers = [(401,None)]*5 + [(201,{}),(200,{'tenantId':'a'}), (200,[])]*0
        answers = [(401,None)]*5 + [(201,{}),(200,{'tenantId':'a'})] + [(200,[])]*5 + [(201,{}),(200,{'tenantId':'b'}),(200,[{'id':'abc'}]),(404,None)]
        with patch.object(mod, 'request_json', side_effect=answers):
            rows = mod.run('http://localhost:3001','a','p','b','p')
        self.assertEqual(rows[-1]['result'], 'PASS')
    def test_same_tenant_fails(self):
        answers = [(401,None)]*5 + [(201,{}),(200,{'tenantId':'a'})] + [(200,[])]*5 + [(201,{}),(200,{'tenantId':'a'})]
        with patch.object(mod, 'request_json', side_effect=answers):
            rows = mod.run('http://localhost:3001','a','p','b','p')
        self.assertEqual(rows[-1]['result'], 'FAIL')

if __name__ == '__main__':
    unittest.main()

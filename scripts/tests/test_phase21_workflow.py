import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import phase21_workflow as w

class WorkflowTests(unittest.TestCase):
    def test_no_write_never_calls_api(self):
        def forbidden(*args):
            raise AssertionError('network call not allowed')
        checks = w.execute('http://localhost:3001', 'a', 'b', requester=forbidden)
        self.assertEqual(checks[0]['status'], 'SKIP')

    def test_missing_credentials_never_calls_api(self):
        checks = w.execute('http://localhost:3001', '', '', allow_write=True)
        self.assertEqual(checks[0]['status'], 'SKIP')

    def test_success_and_tenant_denial(self):
        def fake(opener, url, method='GET', payload=None):
            if url.endswith('/auth/login'): return 201, {'user': {}}
            if url.endswith('/auth/me'):
                return 200, {'tenantId': 'tenant-a' if opener == 'A' else 'tenant-b'}
            if method == 'POST' and url.endswith('/kaizen'): return 201, {'id': 'test-id'}
            if method == 'GET' and url.endswith('/kaizen/test-id'):
                return (200, {'title': created_title[0]}) if opener == 'A' else (404, None)
            if method == 'PATCH' and payload['action'] == 'SUBMIT': return 200, {'status': 'SUBMITTED'}
            if method == 'PATCH' and payload['action'] == 'APPROVE': return 403, None
            return 500, None
        # Intercept the generated title without modifying the source workflow.
        created_title = ['']
        def wrapper(opener, url, method='GET', payload=None):
            if method == 'POST' and url.endswith('/kaizen'): created_title[0] = payload['title']
            return fake(opener, url, method, payload)
        accounts = iter(['A', 'B'])
        checks = w.execute('http://test', 'a', 'pw', 'b', 'pw', True, wrapper, lambda: next(accounts))
        self.assertTrue(all(c['status'] == 'PASS' for c in checks))
        self.assertEqual(len(checks), 6)

    def test_missing_tenant_b_skips(self):
        def fake(opener, url, method='GET', payload=None):
            if url.endswith('/auth/login'): return 201, {}
            if url.endswith('/auth/me'): return 200, {'tenantId': 'a'}
            if method == 'POST': return 201, {'id': 'x'}
            if method == 'PATCH' and payload['action'] == 'SUBMIT': return 200, {'status': 'SUBMITTED'}
            if method == 'PATCH': return 403, None
            return 200, {'title': title[0]}
        title = ['']
        def wrapper(opener, url, method='GET', payload=None):
            if method == 'POST' and url.endswith('/kaizen'): title[0] = payload['title']
            return fake(opener, url, method, payload)
        checks = w.execute('http://test', 'a', 'pw', allow_write=True, requester=wrapper, opener_factory=lambda: 'A')
        self.assertEqual(checks[-1]['status'], 'SKIP')

    def test_report_counts(self):
        report = w.build_report([w.result('a', True), w.result('b', False), w.result('c', None)], 'http://test')
        self.assertEqual(report['counts'], {'PASS': 1, 'FAIL': 1, 'SKIP': 1})

if __name__ == '__main__': unittest.main()

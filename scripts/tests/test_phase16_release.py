import importlib.util
import tempfile
import unittest
from pathlib import Path

p = Path(__file__).resolve().parents[1] / 'phase16_release.py'
spec = importlib.util.spec_from_file_location('phase16_release', p)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ReleaseTests(unittest.TestCase):
    def test_required_secret_missing(self):
        self.assertEqual(len(module.environment_checks({})), 3)
        self.assertTrue(all(x['status']=='FAIL' for x in module.environment_checks({})))
    def test_placeholder_rejected(self):
        env = {'POSTGRES_PASSWORD':'change-me-123456', 'JWT_SECRET':'change-me-'+'a'*40, 'AI_SERVICE_TOKEN':'change-me-'+'b'*40}
        self.assertTrue(all(x['status']=='FAIL' for x in module.environment_checks(env)))
    def test_strong_secrets_accepted(self):
        env = {'POSTGRES_PASSWORD':'safe-random-value-778899', 'JWT_SECRET':'a'*40, 'AI_SERVICE_TOKEN':'b'*40}
        self.assertTrue(all(x['status']=='PASS' for x in module.environment_checks(env)))
    def test_static_repo(self):
        self.assertTrue(all(x['status']=='PASS' for x in module.static_checks()))
    def test_missing_files_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertTrue(any(x['status']=='FAIL' for x in module.static_checks(Path(temp))))
    def test_http_unavailable_fails(self):
        self.assertEqual(module.http_check('offline','http://127.0.0.1:1/',timeout=0.2)['status'],'FAIL')

if __name__=='__main__': unittest.main()

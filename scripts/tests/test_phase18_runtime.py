import importlib.util
import tempfile
import unittest
from pathlib import Path

spec=importlib.util.spec_from_file_location('phase18',Path(__file__).resolve().parents[1]/'phase18_runtime.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class Phase18Tests(unittest.TestCase):
    def test_static_repository(self):
        self.assertTrue(all(x['status']=='PASS' for x in module.static_checks()))
    def test_missing_files_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertTrue(any(x['status']=='FAIL' for x in module.static_checks(Path(temp))))
    def test_no_docker_reports_failure(self):
        from unittest.mock import patch
        with patch.object(module.shutil,'which',return_value=None):
            self.assertEqual(module.docker_checks()[0]['status'],'FAIL')
    def test_live_unavailable_fails(self):
        from unittest.mock import patch
        with patch.object(module.urllib.request,'urlopen',side_effect=OSError('offline')):
            self.assertEqual(module.live_checks({'test':'http://127.0.0.1:1'})[0]['status'],'FAIL')
    def test_requires_live(self):
        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(module.main(['--require-live','--output',str(Path(temp)/'report.json')]),1)
if __name__=='__main__': unittest.main()

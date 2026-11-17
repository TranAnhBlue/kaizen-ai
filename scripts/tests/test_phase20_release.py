import importlib.util
import tempfile
import sys
import unittest
from pathlib import Path

FILE=Path(__file__).resolve().parents[1]/'phase20_release.py'
sys.path.insert(0,str(FILE.parent))
spec=importlib.util.spec_from_file_location('phase20_release',FILE)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class Phase20GateTests(unittest.TestCase):
    def test_missing_files_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(any(c['status']=='FAIL' for c in module.static_checks(Path(tmp))))
    def test_all_pass_accepted(self):
        self.assertTrue(module.summarize([module.check('a','PASS')])[1])
    def test_skip_blocks_release(self):
        self.assertFalse(module.summarize([module.check('a','PASS'),module.check('b','SKIP')])[1])
    def test_fail_blocks_release(self):
        self.assertFalse(module.summarize([module.check('a','FAIL')])[1])
    def test_markdown_reports_unaccepted(self):
        report={'generated_at':'2026-11-16','release_candidate_accepted':False,'checks':[module.check('x','FAIL','reason')]}
        self.assertIn('NOT ACCEPTED',module.render_md(report))
    def test_static_files_present(self):
        self.assertTrue(all(c['status']=='PASS' for c in module.static_checks()))

if __name__=='__main__':unittest.main()

import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('p11',Path(__file__).resolve().parents[1]/'phase11_acceptance.py')
p11=importlib.util.module_from_spec(spec);spec.loader.exec_module(p11)
class AcceptanceTests(unittest.TestCase):
    def test_good_status(self):
        with patch('builtins.print'): p11.assert_status('ok',200,200)
    def test_bad_status(self):
        with self.assertRaises(p11.SmokeFailure): p11.assert_status('wrong',403,401)
    def test_missing_health(self):
        with patch.object(p11,'fetch',return_value=(503,None)):
            with self.assertRaises(p11.SmokeFailure): p11.run('http://example.invalid')
    def test_unauthorized_endpoint(self):
        with patch.object(p11,'fetch',side_effect=[(200,{}),(200,[])]):
            with self.assertRaises(p11.SmokeFailure): p11.run('http://example.invalid')
if __name__=='__main__':unittest.main()

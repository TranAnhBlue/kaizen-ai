import importlib.util
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch
from io import BytesIO

spec=importlib.util.spec_from_file_location('phase14',Path(__file__).resolve().parents[1]/'phase14_smoke.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class FakeResponse:
    status=200
    def __init__(self,body):self.body=body
    def __enter__(self):return self
    def __exit__(self,*args):pass
    def read(self,*args):return self.body
class SmokeTests(TestCase):
    @patch.object(m.urllib.request,'urlopen',return_value=FakeResponse(b'{"status":"ok","service":"kaizen-api"}'))
    def test_backend_healthy(self,_):self.assertEqual(m.probe('backend','http://example/health','kaizen-api')['status'],'PASS')
    @patch.object(m.urllib.request,'urlopen',return_value=FakeResponse(b'{"status":"ok","service":"wrong"}'))
    def test_wrong_service(self,_):self.assertEqual(m.probe('backend','http://example/health','kaizen-api')['status'],'FAIL')
    @patch.object(m.urllib.request,'urlopen',side_effect=OSError('offline'))
    def test_offline(self,_):self.assertEqual(m.probe('backend','http://example/health')['status'],'FAIL')
    @patch.object(m.urllib.request,'urlopen',return_value=FakeResponse(b'<html>ok</html>'))
    def test_frontend(self,_):self.assertEqual(m.probe('frontend','http://example')['status'],'PASS')

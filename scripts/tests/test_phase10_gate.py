import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / 'phase10_gate.py'
spec = importlib.util.spec_from_file_location('phase10_gate', SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)

class ReleaseGateTests(unittest.TestCase):
    def test_static_repo(self):
        self.assertEqual(gate.static_checks(), [])
    def test_missing_file_is_detected(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(gate, 'ROOT', Path(folder)):
                errors = gate.static_checks()
        self.assertTrue(any('Missing required file' in e for e in errors))
    def test_unreachable_service_is_failure(self):
        self.assertIsNotNone(gate.health_check('http://127.0.0.1:1/health', timeout=0.5))
    def test_static_gate_returns_zero(self):
        self.assertEqual(gate.main([]), 0)

if __name__ == '__main__':
    unittest.main()

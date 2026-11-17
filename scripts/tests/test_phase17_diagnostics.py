import importlib.util
from pathlib import Path
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('phase17',ROOT/'scripts/phase17_diagnostics.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Phase17Tests(unittest.TestCase):
    def test_static_checks(self):
        checks=m.inspect()
        self.assertTrue(checks)
        self.assertTrue(all(x['status']=='PASS' for x in checks),checks)
    def test_no_duplicate_vector_column(self):
        sql=(ROOT/'backend/prisma/migrations/20261115060000_rag_vector/migration.sql').read_text()
        self.assertNotIn('ADD COLUMN "embedding"',sql)
    def test_index_present(self):
        sql=(ROOT/'backend/prisma/migrations/20261115060000_rag_vector/migration.sql').read_text()
        self.assertIn('vector_cosine_ops',sql)
    def test_docker_runtime(self):
        docker=(ROOT/'devops/docker/frontend.Dockerfile').read_text()
        self.assertIn('server.js',docker)
        self.assertIn('/app/.next/standalone',docker)
if __name__=='__main__':unittest.main()

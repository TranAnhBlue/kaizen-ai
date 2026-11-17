import importlib.util
import pathlib
import unittest

PATH=pathlib.Path(__file__).resolve().parents[1]/'phase19_acceptance.py'
spec=importlib.util.spec_from_file_location('phase19_acceptance',PATH)
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

class AcceptanceTests(unittest.TestCase):
    def test_status(self):
        self.assertEqual(mod.result('x',True)['status'],'PASS')
        self.assertEqual(mod.result('x',False)['status'],'FAIL')
        self.assertEqual(mod.result('x')['status'],'SKIP')
    def test_missing_credentials_skip(self):
        def fake(opener,url,*args): return (401,None)
        checks=mod.run('http://test',requester=fake,opener_factory=object)
        self.assertEqual(sum(c['status']=='SKIP' for c in checks),2)
        self.assertEqual(sum(c['status']=='PASS' for c in checks),8)
    def test_unauthorized_fails(self):
        def fake(opener,url,*args): return (200,None)
        checks=mod.run('http://test',requester=fake,opener_factory=object)
        self.assertTrue(any(c['status']=='FAIL' for c in checks))
    def test_two_tenant_denial(self):
        class Opener: pass
        a,b=Opener(),Opener(); pool=iter([a,b])
        def fake(opener,url,method='GET',payload=None):
            if url.endswith('/auth/login'): return 201,{}
            if url.endswith('/auth/me'): return (200,{'tenantId':'A' if opener is a else 'B'}) if opener in (a,b) else (401,None)
            if opener not in (a,b): return 401,None
            if url.endswith('/kaizen') and opener is a: return 200,[{'id':'id1','tenantId':'A'}]
            if url.endswith('/kaizen/id1') and opener is b: return 404,None
            return 200,[]
        pool=iter([object(),a,b])
        checks=mod.run('http://test','a','p','b','p',requester=fake,opener_factory=lambda:next(pool))
        self.assertTrue(any(c['name']=='tenant B cannot read tenant A Kaizen' and c['status']=='PASS' for c in checks))
    def test_cross_tenant_leak_fails(self):
        a,b=object(),object(); pool=iter([object(),a,b])
        def fake(opener,url,method='GET',payload=None):
            if url.endswith('/auth/login'): return 201,{}
            if url.endswith('/auth/me'): return 200,{'tenantId':'A' if opener is a else 'B'}
            if opener not in (a,b): return 401,None
            if url.endswith('/kaizen') and opener is a: return 200,[{'id':'id1','tenantId':'B'}]
            if url.endswith('/kaizen/id1'): return 200,{}
            return 200,[]
        checks=mod.run('http://test','a','p','b','p',requester=fake,opener_factory=lambda:next(pool))
        self.assertTrue(any(c['name']=='tenant A list isolation kaizen' and c['status']=='FAIL' for c in checks))
        self.assertTrue(any(c['name']=='tenant B cannot read tenant A Kaizen' and c['status']=='FAIL' for c in checks))
    def test_report_counts(self):
        r=mod.report([mod.result('a',True),mod.result('b',False),mod.result('c')],'http://localhost')
        self.assertEqual(r['counts'],{'PASS':1,'FAIL':1,'SKIP':1})
        self.assertEqual(r['mode'],'read-only')

if __name__=='__main__': unittest.main()

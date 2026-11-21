import importlib.util
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location('rh_audit', Path(__file__).resolve().parents[1] / 'tools' / 'rh_audit.py')
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)

class TestAudit(unittest.TestCase):
    def test_find_declaration(self):
        src = 'import Mathlib\n\ntheorem Alpha : True := by trivial\n\ntheorem Beta : True := Alpha\n'
        a = audit.find_decl(src,'Alpha')
        self.assertTrue(a['found'])
        self.assertEqual(a['line'],3)
        self.assertNotIn('Beta',a['block'])
        self.assertTrue(audit.find_decl(src,'Beta')['found'])

    def test_unqualified_inside_namespace(self):
        src = 'namespace X.Y\n\ntheorem gamma : True := by trivial\n\nend X.Y\n'
        a = audit.find_decl(src,'X.Y.gamma')
        self.assertTrue(a['found'])
        self.assertEqual(a['line'],3)

    def test_missing_and_mermaid(self):
        self.assertFalse(audit.find_decl('theorem A : True := by trivial','B')['found'])
        m = audit.mermaid(audit.DECLS)
        self.assertIn('rh_of_all --> headline', m)
        self.assertIn('flowchart TD', m)

    def test_manual_reference_check(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            f=root/'src/Main.lean'
            f.parent.mkdir()
            f.write_text('theorem riemannHypothesis : RiemannHypothesis := rhOfAll\n')
            result=audit.inspect(root)
            headline=next(x for x in result if x['id']=='headline')
            self.assertTrue(headline['found'])
            self.assertEqual(headline['refs_found'],{'rhOfAll':True})

if __name__ == '__main__':
    unittest.main()

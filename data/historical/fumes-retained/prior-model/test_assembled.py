import unittest
from pathlib import Path
class AssembledTests(unittest.TestCase):
    def test_solver_exists_and_rejects_missing_sections(self):
        import importlib.util
        p=Path(__file__).with_name('assembled_solver.py');self.assertTrue(p.exists())
        s=importlib.util.spec_from_file_location('assembled',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
        with self.assertRaises(ValueError):m.build({},'.')
if __name__=='__main__':unittest.main()

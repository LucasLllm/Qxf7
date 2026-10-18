import unittest,numpy as np
from pathlib import Path
import importlib.util
class ReconstructionTests(unittest.TestCase):
    def load(self):
        p=Path(__file__).with_name('reconstruct_sections.py');self.assertTrue(p.exists())
        s=importlib.util.spec_from_file_location('reconstruction',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
    def test_hinge_gap_is_explicit_not_claimed_measured(self):
        m=self.load()
        front=[[-100,0],[-80,10],[0,0],[-80,-5],[-100,0]]
        back=[[-200,0],[-105,6],[-105,-3],[-200,0]]
        xy,meta=m.reconstruct([front,back],n=401)
        self.assertTrue(meta['hinge_sealing_approximation'])
        self.assertGreater(meta['missing_x_fraction'],0)
        self.assertAlmostEqual(meta['chord_mm'],200)
        self.assertTrue(np.isfinite(xy).all())
    def test_disconnected_large_gap_rejected(self):
        m=self.load()
        with self.assertRaises(ValueError):m.reconstruct([[[-50,0],[0,1],[-50,2]],[[-200,0],[-150,1],[-200,2]]])
if __name__=='__main__':unittest.main()

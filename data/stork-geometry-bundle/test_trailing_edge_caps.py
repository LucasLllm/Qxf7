"""Independent regression on synthetic blunt-TE sections, not aircraft evidence."""
import unittest,importlib.util
from pathlib import Path
import numpy as np
p=Path(__file__).resolve().parent/'tail-extraction/normalize_tail.py'
spec=importlib.util.spec_from_file_location('tail_caps',p);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
class TestTrailingEdgeCaps(unittest.TestCase):
 def fixture(self,oblique=False):
  x=np.linspace(0,100,3001);h=5*np.sqrt(np.maximum(x/100*(1-x/100),0))+.5*x/100
  q=np.vstack((np.c_[x,h],np.c_[x[::-1],-h[::-1]]));q=np.vstack((q,q[0]))
  if oblique:q[len(x)-1,0]-=.01
  return x,h,q
 def test_preserves_finite_cap(self):
  x,h,q=self.fixture();m,dat,_=mod.normalize_tail(x,h,-h,[q]);self.assertAlmostEqual(m['TE_thickness_mm'],1,places=6);self.assertAlmostEqual(dat[0,1]-dat[-1,1],m['TE_thickness_over_chord'],places=10);self.assertAlmostEqual(dat[0,1]+dat[-1,1],0,places=9)
 def test_oblique_cap_not_collapsed(self):
  x,h,q=self.fixture(True);m,dat,_=mod.normalize_tail(x,h,-h,[q]);self.assertGreater(m['TE_thickness_mm'],.99);self.assertLess(m['TE_thickness_mm'],1.01);self.assertAlmostEqual(dat[0,1]+dat[-1,1],0,places=9)
if __name__=='__main__':unittest.main()

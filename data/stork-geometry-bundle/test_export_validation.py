"""Synthetic fixtures test export validator; fixtures are not aircraft measurements."""
import tempfile,unittest
from pathlib import Path
import numpy as np
from airfoil_tools import normalize_envelope
from verify_extraction import check_dat
class TestExportValidation(unittest.TestCase):
 def setUp(self):
  x=np.linspace(0,1,3001);h=.1*np.sqrt(np.maximum(x*(1-x),0));self.data=normalize_envelope(x,h,-h)[1];self.temp=tempfile.TemporaryDirectory();self.p=Path(self.temp.name)/'synthetic.dat'
 def tearDown(self):self.temp.cleanup()
 def save(self,data):np.savetxt(self.p,data,header='Synthetic test only',comments='')
 def test_accept_valid_synthetic_140(self):
  self.save(self.data);self.assertTrue(check_dat(self.p)['pass'])
 def test_reject_truncation(self):
  self.save(self.data[:-1]);
  with self.assertRaises(AssertionError):check_dat(self.p)
 def test_reject_nonfinite(self):
  a=self.data.copy();a[10,1]=np.nan;self.save(a)
  with self.assertRaises(AssertionError):check_dat(self.p)
 def test_reject_not_cosine(self):
  a=self.data.copy();a[8,0]+=.001;self.save(a)
  with self.assertRaises(AssertionError):check_dat(self.p)
 def test_reject_crossed_surfaces(self):
  a=self.data.copy();a[:,1]*=-1;self.save(a)
  with self.assertRaises(AssertionError):check_dat(self.p)
if __name__=='__main__':unittest.main()

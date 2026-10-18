import unittest,zipfile
import numpy as np
from compare_uiuc import parse_points,surfaces,rms,D,G
class TestUIUC(unittest.TestCase):
 def test_real_archive_self_match(self):
  z=zipfile.ZipFile(D/'uiuc-sources/coord_seligFmt.zip');name='coord_seligFmt/2032c.dat';a=parse_points(z.read(name).decode());s=surfaces(a);self.assertEqual(rms(s,s),0.0)
  db=np.load(D/'uiuc-comparison/corpus.npz');i=list(db['names']).index(name);self.assertLess(rms(s,(db['upper'][i],db['lower'][i])),1e-12)
 def test_translation_invariance(self):
  z=zipfile.ZipFile(D/'uiuc-sources/coord_seligFmt.zip');a=parse_points(z.read('coord_seligFmt/2032c.dat').decode());b=a+np.array([.1,-.05]);self.assertLess(rms(surfaces(a),surfaces(b)),1e-10)
 def test_metric_has_expected_units(self):
  zero=np.zeros_like(G);delta=np.ones_like(G)*.001;self.assertAlmostEqual(rms((zero,zero),(delta,zero)),100*.001/np.sqrt(2),places=12)
 def test_count_header_not_accepted(self):
  a=np.vstack(([70.,70.],np.zeros((20,2))));text='\n'.join(f'{x} {y}' for x,y in a)
  with self.assertRaises(ValueError):parse_points(text)
if __name__=='__main__':unittest.main()

"""Independent checks for real artifacts and finite-TE normalization regression."""
import unittest,json,hashlib
from pathlib import Path
import numpy as np
from normalize_tail import normalize_tail
D=Path(__file__).resolve().parent
class TailTests(unittest.TestCase):
 def test_finite_TE_regression(self):
  x=np.linspace(0,150,6001);y=8*np.sqrt(x/150)*(1-x/150)+.5*x/150
  q=np.vstack([np.c_[x,y],np.c_[x[::-1],-y[::-1]],[0.,0.]])
  m,dat,_=normalize_tail(x,y,-y,[q])
  self.assertAlmostEqual(m['chord_mm'],150.,places=8)
  self.assertAlmostEqual(m['TE_thickness_mm'],1.,places=8)
  self.assertAlmostEqual(m['max_camber_over_chord'],0.,places=8)
  self.assertAlmostEqual(dat[0,1]-dat[-1,1],1/150,places=8)
 def test_140_points_and_cosine_grids(self):
  for path in D.glob('*Selig.dat'):
   dat=np.loadtxt(path,skiprows=1);self.assertEqual(dat.shape,(140,2));self.assertTrue(np.isfinite(dat).all())
   np.testing.assert_allclose(dat[:70,0],((1-np.cos(np.linspace(0,np.pi,70)))/2)[::-1],atol=6e-11)
   np.testing.assert_allclose(dat[70:,0],((1-np.cos(np.linspace(0,np.pi,71)))/2)[1:],atol=6e-11)
   np.testing.assert_allclose(dat[69],[0,0],atol=1e-10)
 def test_real_finite_TE_retained(self):
  j=json.loads((D/'tail_geometry.json').read_text())
  for label in ['root','midspan','outer_regular']:
   m=j['profiles'][label];self.assertTrue(.999<m['TE_thickness_mm']<1.001)
   dat=np.loadtxt(D/f'{label}_140cosineSelig.dat',skiprows=1)
   self.assertAlmostEqual((dat[0,1]-dat[-1,1])*m['chord_mm'],m['TE_thickness_mm'],places=6)
   self.assertTrue(.1<m['max_thickness_over_chord']<.11)
 def test_frame_and_plane(self):
  j=json.loads((D/'tail_geometry.json').read_text());b=j['basis'];n=np.array(b['span_root_plane_normal_aircraft']);a=b['aft_in_section_aircraft'];u=b['up_in_section_aircraft']
  np.testing.assert_allclose(np.array([n,a,u])@np.array([n,a,u]).T,np.eye(3),atol=1e-12)
  self.assertAlmostEqual(np.dot(j['root_LE_aircraft_mm'],n),b['root_plane_equation_n_dot_xyz_mm'],places=8)
  for m in j['profiles'].values():self.assertAlmostEqual(np.dot(m['leading_edge_aircraft_mm'],n),b['root_plane_equation_n_dot_xyz_mm']+m['span_station_from_root_plane_mm'],places=8)
 def test_true_tip_and_neutral_not_invented(self):
  j=json.loads((D/'tail_geometry.json').read_text());self.assertIsNone(j['true_tip']['conventional_airfoil']);self.assertIsNone(j['neutral']['true_zero_relative_agreed_neutral_contour_deg']);self.assertEqual(j['neutral']['source_STEP_rotation_applied_deg'],0)
 def test_input_hashes_still_match(self):
  r=json.loads((D/'source_hash_verification.json').read_text());self.assertTrue(r['all_original_inputs_unchanged'])
  for s in r['sources'].values():self.assertEqual(hashlib.sha256(Path(s['path']).read_bytes()).hexdigest(),s['sha256'])
  for path,h in r['read_only_reference_and_script_sha256'].items():self.assertEqual(hashlib.sha256(Path(path).read_bytes()).hexdigest(),h)
if __name__=='__main__':unittest.main(verbosity=2)

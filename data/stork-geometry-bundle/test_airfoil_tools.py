import unittest
import numpy as np
from airfoil_tools import normalize_envelope,envelope_from_loops

class AirfoilTests(unittest.TestCase):
 def test_symmetric_section_and_point_count(self):
  x=(1-np.cos(np.linspace(0,np.pi,5001)))/2
  t=.6*(.2969*np.sqrt(x)-.126*x-.3516*x*x+.2843*x**3-.1015*x**4)
  q,dat,curves=normalize_envelope(200*x,200*t,-200*t)
  self.assertEqual(dat.shape,(140,2));self.assertAlmostEqual(q['chord_mm'],200,places=6);self.assertAlmostEqual(q['max_thickness_over_chord'],.12,delta=.001)
  self.assertLess(abs(q['max_camber_over_chord']),1e-9);self.assertLess(abs(q['incidence_LE_up_deg']),1e-9)
  self.assertTrue(np.all(np.diff(dat[:70,0])<=0));self.assertTrue(np.all(np.diff(dat[69:,0])>=0))
 def test_outer_loop_ignores_internal_bore(self):
  outer=np.array([[0,0,0],[0,10,2],[0,100,0],[0,10,-2],[0,0,0]],float)
  bore=np.array([[0,20,0],[0,21,.2],[0,22,0],[0,21,-.2],[0,20,0]],float)
  x,u,l,meta=envelope_from_loops([[outer,bore]],np.array([0,1,0]),np.array([0,0,1]))
  self.assertEqual(meta['selected_components'],1);self.assertAlmostEqual(np.max(u-l),4,delta=.01)
 def test_explicit_hinge_bridge_only(self):
  x=np.linspace(0,200,3001);u=np.ones_like(x)*3;l=-u
  u[(x>145)&(x<155)]=0;l[(x>145)&(x<155)]=0
  q,dat,curves=normalize_envelope(x,u,l,150,6)
  self.assertEqual(q['hinge_bridge']['outer_skin_bridge_aft_limits_mm'],[144.,156.]);self.assertTrue(np.isfinite(dat).all())

if __name__=='__main__':unittest.main()

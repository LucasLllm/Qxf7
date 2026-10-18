import unittest
from derive_arms import derive
class Arms(unittest.TestCase):
 def test_bilateral_cancellation(self):
  q={'quarterchord_aft_mm':20.,'area_weighted_quarterchord_up_mm':5.}
  w={'exposed':q,'gross_with_declared_centerline_continuation':q}
  t={'planform_full_including_fin':{'area_weighted_quarter_chord_aircraft_mm':[120.,99.,5.]}}
  a=derive(w,t)['exposed']
  self.assertEqual(a['QC_difference_aircraft_mm'],[100.,0.,0.])
  self.assertEqual(a['xz_distance_mm'],100.)
if __name__=='__main__':unittest.main()

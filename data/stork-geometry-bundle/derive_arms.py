"""Geometric lever arms in common STEP-derived aircraft frame."""
import numpy as np
def derive(w,t):
 out={}
 tq=np.array(t['planform_full_including_fin']['area_weighted_quarter_chord_aircraft_mm'])
 for name in ['exposed','gross_with_declared_centerline_continuation']:
  q=w[name]
  wq=np.array([q['quarterchord_aft_mm'],0.,q['area_weighted_quarterchord_up_mm']])
  tail=tq.copy();tail[1]=0.
  v=tail-wq
  out[name]={'wing_QC_aircraft_mm':wq.tolist(),'tail_bilateral_QC_aircraft_mm':tail.tolist(),'QC_difference_aircraft_mm':v.tolist(),'longitudinal_arm_mm':float(v[0]),'xz_distance_mm':float(np.linalg.norm(v))}
 out['definition']='Area-weighted geometric quarter-chords; bilateral y=0. Not aerodynamic centres or CG arms. Tail includes real fin. Gross wing uses declared artificial carry-through.'
 return out

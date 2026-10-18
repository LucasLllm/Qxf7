from pathlib import Path
import json
import numpy as np
O=Path(__file__).resolve().parent
ns={'__file__':str(O/'extract.py')}
exec((O/'extract.py').read_text().split('# Regular native-datum')[0],ns)
globals().update({k:v for k,v in ns.items() if not k.startswith('__')})
checks=[]
for x in [-271.248886456396,-160,-111,-80,0,110,149,250,270]:
 r=section(x);clouds=[]
 for p in parts:
  if not p['bounds'][0]+1e-5<x<p['bounds'][1]-1e-5:continue
  s=p['shape']
  if isinstance(s,trimesh.Trimesh):
   cut=s.section(plane_origin=[0,0,x],plane_normal=[0,0,1])
   if cut is not None:clouds.append(cut.vertices[:,:2])
  else:
   op=BRepAlgoAPI_Section(s.wrapped,gp_Pln(gp_Pnt(0,0,x),gp_Dir(0,0,1)),False);op.Build();assert op.IsDone()
   for e in cq.Shape.cast(op.Shape()).Edges():
    q,d=sample_edge(e,tol=.0025,max_chord=.35);assert d['max_checked_chord_deviation_mm']<=.0025
    clouds.append(q[:,:2])
 points=np.vstack(clouds);poly=points[ConvexHull(points).vertices];p=Polygon(poly)
 checks.append({'aircraft_x_mm':x,'default_convex_area_mm2':r['area'],'refined_convex_area_mm2':p.area,'absolute_area_change_mm2':abs(p.area-r['area']),'relative_area_change':abs(p.area/r['area']-1),'width_change_mm':abs(np.ptp(points[:,0])-r['width']),'height_change_mm':abs(np.ptp(points[:,1])-r['height'])})
 assert checks[-1]['relative_area_change']<.001
 assert checks[-1]['width_change_mm']<.03 and checks[-1]['height_change_mm']<.03
 print('PASS refined station',x,checks[-1],flush=True)
for g0,g1 in gaps:
 try:section((g0+g1)/2)
 except MissingSection:pass
 else:raise AssertionError('Unregistered gap was fabricated')
# Circle/reversed-wire synthetic source test exercises periodic edge sampling.
w=cq.Workplane('XY').circle(10).wire().val()
a,m=sample_wire(w);assert m['max_join_gap_mm']<=m['allowed_join_gap_mm']
circle_area_error=abs(Polygon(a).area-np.pi*100)
# For an inscribed circle polygon the area loss is bounded by perimeter times
# the checked sag tolerance; an arbitrary 0.1mm2 area threshold was too strict
# for the default 0.01mm geometry tolerance. Check both native exact length and
# an independently finer sample instead of loosening a real-source tolerance.
assert abs(m['exact_perimeter_mm']-20*np.pi)<1e-9
assert circle_area_error < m['exact_perimeter_mm']*.01
fine,fm=sample_wire(w,tol=.001)
assert abs(Polygon(fine).area-np.pi*100)<circle_area_error
assert abs(Polygon(fine).area-np.pi*100)<fm['exact_perimeter_mm']*.001
result={'status':'PASS','refined_real_stations':checks,'refined_tolerance_mm':.0025,'refined_max_chord_mm':.35,'missing_nose_gap_rejected':True,'periodic_circle_sampler_passed':True,'max_refined_relative_area_change':max(c['relative_area_change'] for c in checks),'max_refined_dimension_change_mm':max(max(c['width_change_mm'],c['height_change_mm']) for c in checks)}
(O/'tolerance_validation.json').write_text(json.dumps(result,indent=2));print('ALL SAMPLER REGRESSIONS PASS',flush=True)

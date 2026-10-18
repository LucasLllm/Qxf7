"""Reproduce nominal installed hatch registration and untouched source-skin exports. All mm."""
from investigate import ROOT,OUT,bounds
import json,hashlib
from pathlib import Path
import numpy as np
import cadquery as cq
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.gp import gp_Pln,gp_Pnt,gp_Dir
D=json.loads((OUT/'features.json').read_text())
F='HATCH FRONT.STEP'; M='HATCH MIDDLE.STEP'; A='FUS 1 VTOL.STEP'; B='FUS 2 VTOL MODIFIER.STEP'; C='FUS3.STEP'
S={n:cq.importers.importStep(d['source']).solids().vals() for n,d in D.items()}
def feat(n,b,i): return D[n]['solids'][b-1]['features'][i-1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def transform(s,T):
 from OCP.gp import gp_Trsf
 t=gp_Trsf();t.SetValues(*np.array(T)[:3,:4].flatten().tolist());return s.transformShape(cq.Matrix(t))
# Pair face indices are 1-based within cq.importers.importStep(...).solids().vals()[body-1].Faces().
# Seam holes are paired across printed pieces; these are alignment bores (pins omitted), not solid male pins.
configs=[(F,1,[(16,A,1,20),(18,A,1,29),(20,A,1,26),(23,A,1,22),(26,A,1,35),(27,A,1,24),(28,A,1,33),(30,A,1,31),(11,A,1,18),(13,A,1,17)],[]),
 (F,2,[(1,F,1,4),(3,F,1,7),(6,F,1,1),(10,B,1,23),(12,B,1,25),(14,B,1,78),(16,B,1,80)],[(2,F,1,3,0)]),
 (M,1,[(10,C,1,21),(12,C,1,63)],[(19,C,1,33,-0.3)]),
 (M,2,[(1,M,1,1),(4,M,1,3),(7,M,1,6),(13,C,1,19),(28,C,1,65)],[(2,M,1,2,0)])]
# M2 seam face is plane 2? discover rather than silently trust.
for f in D[M]['solids'][1]['features']:
 if f['type']=='PLANE' and abs(f['center'][2]-149.14911364361)<1e-5 and f['area']>100:
  configs[3][3][0]=(f['face'],M,1,2,0)
from OCP.BRep import BRep_Tool
from OCP.GeomAPI import GeomAPI_ProjectPointOnSurf
continuity=[];continuity_anchor=None
for hn,hb,hf,bn,bf in [(F,1,39,A,78),(F,1,38,A,79),(F,2,66,B,97),(F,2,67,B,10),(F,2,44,B,96),(F,2,11,B,11),(M,1,54,C,109),(M,1,53,C,110),(M,2,39,C,109),(M,2,40,C,110)]:
 h=S[hn][hb-1].Faces()[hf-1];f=S[bn][0].Faces()[bf-1];surf=BRep_Tool.Surface_s(f.wrapped)
 vs,_=h.tessellate(2);pts=vs[::max(1,len(vs)//30)];samples=[]
 for p in pts:
  if not bounds(f)[0][2]+0.01 < p.z < bounds(f)[1][2]-0.01: continue
  proj=GeomAPI_ProjectPointOnSurf(gp_Pnt(*p.toTuple()),surf)
  q=proj.NearestPoint();samples.append({'source_point_native_mm':p.toTuple(),'fuselage_underlying_surface_projection_mm':[q.X(),q.Y(),q.Z()],'distance_mm':proj.LowerDistance()})
 assert samples and max(x['distance_mm'] for x in samples)<0.002
 continuity.append({'hatch':[hn,hb,hf],'fuselage_face':[bn,1,bf],'method':'point projection onto original untrimmed BSpline support surface of adjacent actual skin, only inside its longitudinal range; not trimmed-face contact or synthetic convex closure','sample_count':len(samples),'max_distance_mm':max(x['distance_mm'] for x in samples),'samples':samples})
 if hn==M and hb==1 and hf==54:
  continuity_anchor=min(samples,key=lambda x:x['distance_mm'])
# Do not use the disjoint latch supporting planes as a physical seat to solve Y.
# The original shared outer BSpline contour fixes the axial slide left by the Y-axis lip cylinders.
configs[2]=(M,1,configs[2][2],[])
# Tessellation above is for sampling only; remove cached triangulations before BRep bound/export checks.
from OCP.BRepTools import BRepTools
for solids in S.values():
 for solid in solids: BRepTools.Clean_s(solid.wrapped)
installed={};report=[]
for n,b,axes,planes in configs:
 def residual(q):
  R=Rotation.from_rotvec(q[:3]).as_matrix();t=q[3:];r=[]
  for i,nn,bb,j in axes:
   h=feat(n,b,i);f=feat(nn,bb,j);u=np.array(f['axis']);v=R@h['axis'];v*=1 if np.dot(u,v)>=0 else -1
   delta=R@h['location']+t-f['location'];r.extend(delta-u*np.dot(delta,u));r.extend(50*np.cross(v,u))
  for i,nn,bb,j,gap in planes:
   h=feat(n,b,i);f=feat(nn,bb,j);u=np.array(f['normal']);r.append(np.dot(R@h['location']+t-f['location'],u)-gap)
   v=R@h['normal'];r.extend(50*np.cross(v,u))
  if n==M and b==1:
   r.extend(R@continuity_anchor['source_point_native_mm']+t-continuity_anchor['fuselage_underlying_surface_projection_mm'])
  return r
 fit=least_squares(residual,np.zeros(6),xtol=1e-13,ftol=1e-13,gtol=1e-13,max_nfev=1000)
 sv=np.linalg.svd(fit.jac,compute_uv=False);rank=int(sum(sv>1e-5));assert rank==6,(n,b,sv)
 T=np.eye(4);T[:3,:3]=Rotation.from_rotvec(fit.x[:3]).as_matrix();T[:3,3]=fit.x[3:]
 # Preserve original CAD pose when independent mates reproduce it within CAD tolerance, not numerical fit noise.
 assert np.max(np.abs(T-np.eye(4)))<1e-5,(n,b,T)
 T=np.eye(4);s=S[n][b-1];installed[(n,b)]=s
 pairs=[]
 for i,nn,bb,j in axes:
  h=feat(n,b,i);f=feat(nn,bb,j);u=np.array(f['axis']);delta=np.array(h['location'])-f['location'];off=float(np.linalg.norm(delta-u*np.dot(delta,u)))
  angle=float(np.degrees(np.arccos(np.clip(abs(np.dot(h['axis'],u)),-1,1))))
  assert off<1e-5 and angle<1e-5
  pairs.append({'hatch_face':i,'mate':[nn,bb,j],'axis_offset_mm':off,'axis_angle_deg':angle,'hatch_radius_mm':h['radius'],'mate_radius_mm':f['radius'],'radial_difference_mm':f['radius']-h['radius']})
 seat=[]
 for i,nn,bb,j,gap in planes:
  h=feat(n,b,i);f=feat(nn,bb,j);v=float(np.dot(np.array(h['location'])-f['location'],f['normal']));assert abs(v-gap)<1e-5
  seat.append({'hatch_face':i,'mate':[nn,bb,j],'signed_plane_gap_mm':v,'nominal_gap_mm':gap,'residual_mm':v-gap,'trimmed_face_distance_mm':s.Faces()[i-1].distance(S[nn][bb-1].Faces()[j-1])})
 report.append({'source':n,'body_one_based':b,'face_count':len(s.Faces()),'volume_mm3':s.Volume(),'valid':s.isValid(),'source_bounds_native_mm':bounds(s),'installed_bounds_native_mm':bounds(s),'bound_change_mm':np.zeros((2,3)).tolist(),'source_to_native':T.tolist(),'fitted_transform_before_tolerance_snap':np.vstack([np.column_stack([Rotation.from_rotvec(fit.x[:3]).as_matrix(),fit.x[3:]]),[0,0,0,1]]).tolist(),'constraint_jacobian_rank':rank,'singular_values':sv.tolist(),'remaining_continuous_DoF':[],'feature_pairs':pairs,'seating_planes':seat})
# Additional independent lip/seat clearances not used to select a pose.
plane_checks=[(F,1,10,A,1,77),(F,1,37,A,1,80),(F,1,25,A,1,36),(F,1,29,A,1,32),(F,2,9,B,1,21),(F,2,65,B,1,82),(F,2,13,B,1,77),(F,2,33,B,1,72),(M,1,9,C,1,20),(M,1,52,C,1,64),(M,1,11,C,1,22)]
checks=[]
for n,b,i,nn,bb,j in plane_checks:
 h=feat(n,b,i);f=feat(nn,bb,j);gap=float(np.dot(np.array(h['location'])-f['location'],f['normal']))
 checks.append({'hatch':[n,b,i],'mate':[nn,bb,j],'signed_supporting_plane_gap_mm':gap,'trimmed_face_distance_mm':S[n][b-1].Faces()[i-1].distance(S[nn][bb-1].Faces()[j-1])})
inter=[]
for n,b in installed:
 for nn in [A,B,C]:
  h=installed[(n,b)];f=S[nn][0];hb=bounds(h);fb=bounds(f)
  if hb[0][2]<=fb[1][2] and hb[1][2]>=fb[0][2]:
   vol=h.intersect(f).Volume();dist=h.distance(f);assert vol<1e-6
   inter.append({'hatch':[n,b],'fuselage':[nn,1],'min_distance_mm':dist,'intersection_volume_mm3':vol})
# Source analytic face patches, never a convex approximation or synthesized cap.
skin_indices={(F,1):[38,39],(F,2):[11,44,66,67],(M,1):[53,54],(M,2):[39,40]}
skin=[];skin_manifest=[]
for key,ids in skin_indices.items():
 s=installed[key];faces=[s.Faces()[i-1] for i in ids]
 for f in faces: assert f.geomType()=='BSPLINE' and f.normalAt().y>0
 skin.extend(faces);skin_manifest.append({'source':key[0],'body':key[1],'source_face_indices_one_based':ids,'area_mm2':sum(f.Area() for f in faces),'scope':'main external aerodynamic skin patches only; latch recesses and cutout sidewalls omitted; exact complete solid also exported'})
compound=cq.Compound.makeCompound(list(installed.values()));cq.exporters.export(compound,str(OUT/'installed_hatches.step'))
cq.exporters.export(cq.Compound.makeCompound(skin),str(OUT/'external_skin_patches.step'))
reload=cq.importers.importStep(str(OUT/'installed_hatches.step')).val();assert len(reload.Solids())==4 and reload.isValid()
serialization_bound_error=float(np.max(np.abs(np.array(bounds(reload))-bounds(compound))))
assert serialization_bound_error<1e-5,serialization_bound_error
patch_reload=cq.importers.importStep(str(OUT/'external_skin_patches.step')).val();assert len(patch_reload.Faces())==10
# Exact skin sections at diagnostic transverse stations; preserves separate curves and real edge gaps.
station_curves=[];stations=[]
for z in [-200,-160,-120,-80,-40,-15,45,75,110,140,170,210,250,270]:
 pl=gp_Pln(gp_Pnt(0,0,z),gp_Dir(0,0,1));sec=BRepAlgoAPI_Section(cq.Compound.makeCompound(skin).wrapped,pl,False);sec.Build();sh=cq.Shape.cast(sec.Shape());es=sh.Edges();assert len(es)>=2
 station_curves.extend(es);stations.append({'native_Z_mm':z,'aircraft_x_without_datum_mm':z,'edge_count':len(es),'bounds_native_mm':bounds(sh),'total_curve_length_mm':sum(e.Length() for e in es),'closure':'not closed; source top patches only, no invented seam or bottom curves'})
cq.exporters.export(cq.Compound.makeCompound(station_curves),str(OUT/'exact_skin_sections.step'))
section_bound_changes=[]
for item in stations:
 z=item['native_Z_mm'];base=[S[n][0] for n in [A,B,C] if bounds(S[n][0])[0][2]<z<bounds(S[n][0])[1][2]]
 if not base:
  section_bound_changes.append({'native_Z_mm':z,'baseline_top_native_Y_mm':None,'installed_hatch_top_native_Y_mm':item['bounds_native_mm'][1][1],'reason':'FUS4 STL outside this exact-BRep baseline'});continue
 sec=BRepAlgoAPI_Section(cq.Compound.makeCompound(base).wrapped,gp_Pln(gp_Pnt(0,0,z),gp_Dir(0,0,1)),False);sec.Build();bb=bounds(cq.Shape.cast(sec.Shape()));top=item['bounds_native_mm'][1][1]
 section_bound_changes.append({'native_Z_mm':z,'baseline_top_native_Y_mm':bb[1][1],'installed_top_native_Y_mm':max(bb[1][1],top),'top_bound_increase_mm':max(0,top-bb[1][1])})
basecomp=cq.Compound.makeCompound([S[n][0] for n in [A,B,C]]);combined=cq.Compound.makeCompound([basecomp,compound])
subset_bounds={'baseline_parts':[A,B,C],'baseline_native_mm':bounds(basecomp),'with_hatches_native_mm':bounds(combined),'delta_mm':(np.array(bounds(combined))-bounds(basecomp)).tolist(),'warning':'Only FUS1/2/3 physical solids baseline; not whole fuselage.'}
sources={n:{'path':d['source'],'sha256':d['sha256'],'unchanged_after':sha(Path(d['source']))==d['sha256']} for n,d in D.items()}
assert all(v['unchanged_after'] for v in sources.values())
result={'status':'NOMINAL_INSTALLED_POSE_FEATURE_VERIFIED','units':'mm; mm2; mm3','coordinate_convention':'native XYZ; aircraft (x,y,z)=(nativeZ,nativeX,nativeY) before separately defined wing-LE datum translation','aircraft_rotation':[[0,0,1],[1,0,0],[0,1,0]],'interpretation':'Identity is the recovered nominal placement, not assumed as evidence. Clearance fits are not zero-clearance contacts; nominal centered pose fixed by paired axes, split seams and latch seating plane. Physical play exists, not a free nominal assembly DoF. No vented STL substitution.','sources':sources,'placements':report,'independent_seating_checks':checks,'solid_clearance_checks':inter,'skin_patches':skin_manifest,'skin_patch_area_mm2':sum(f.Area() for f in skin),'diagnostic_sections':stations,'installed_hatch_bounds_native_mm':bounds(compound),'limitations':['Physical fit/play follows measured 0.4 mm lip and tongue clearances and 0.3 mm latch plane clearance; no manufacturing tolerance certified.','MIDDLE body2 rear tongue to FUS4 STL not independently solved here: split-joint 3-bore pattern plus plane and FUS3 curved lip independently fix its nominal pose. FUS4 seating clearance remains unmeasured.','Skin export contains ten exact main outer skin patches, not a whole watertight fuselage or total wetted area. Full solid export retains all source latch recess features for further classification.','This is hatch subset validation, not complete aircraft bounds approval.'], 'verification':{'reloaded_solid_count':len(reload.Solids()),'reloaded_main_skin_faces':len(patch_reload.Faces()),'all_axis_offset_mm_lt':1e-5,'all_axis_angle_deg_lt':1e-5,'all_plane_residual_mm_lt':1e-5,'nonpenetration_volume_tolerance_mm3':1e-6,'all_four_constraint_ranks':6},'artifacts':{p.name:sha(p) for p in [OUT/'installed_hatches.step',OUT/'external_skin_patches.step',OUT/'exact_skin_sections.step']}}
result.update(skin_continuity_verification=continuity,middle1_skin_continuity_anchor=continuity_anchor,section_top_bound_changes=section_bound_changes,subset_bound_changes=subset_bounds)
result['interpretation']='Identity is recovered from feature axes, split planes, and original shared outer BSpline surface continuity; not assumed. Nonzero clearance is real. MIDDLE1 Y slide is fixed by skin continuity, not by treating disjoint latch-support planes as physical contact. Nominal design pose, not zero-clearance fit.'
result['limitations'][0]='Nominal lips/tongue/side-seat gaps are 0.4 mm; latch supporting planes differ by 0.3 mm but are disjoint trimmed faces (not direct seating clearance). Manufacturing play not certified.'
result['verification']['serialization_max_bound_error_mm']=serialization_bound_error
result['verification']['serialization_bound_error_limit_mm']=1e-5
if (OUT/'fus4_lip_check.json').exists():
 rear=json.loads((OUT/'fus4_lip_check.json').read_text());assert sha(Path(rear['source']))==rear['sha256']
 assert all(c['status']=='curved_lip_verified' and c['axis_XZ_offset_mm']<0.02 and c['max_fit_radial_residual_mm']<0.02 for c in rear['checks'])
 result['fus4_rear_curved_lip']=rear
 result['limitations'][1]='MIDDLE2 rear curved lip checked against registered FUS4 STL: ~0.4052 mm radial clearance; mesh fit axis residual ~0.0056 mm, radial residual ~0.01146 mm. Rear tongue trimmed-plane seating and full mesh/solid penetration are not certified; nominal pose independently fixed by split-joint bores/plane and FUS3 lip.'
(OUT/'placement.json').write_text(json.dumps(result,separators=(',',':')))
print(json.dumps({'status':result['status'],'placements':[(r['source'],r['body_one_based'],r['constraint_jacobian_rank']) for r in report],'clearance_checks':inter,'skin_area_mm2':result['skin_patch_area_mm2'],'seating':checks},indent=2))

"""Feature-anchored right-wing assembly. Source files read-only; derived meshes stay here."""
from pathlib import Path
import csv,json,hashlib
import numpy as np
import trimesh,cadquery as cq
from shapely.geometry import Polygon,MultiPolygon,LineString
import shapely
D=Path(__file__).resolve().parent
rows=list(csv.DictReader((D.parent/'source-format-audit/cad_inventory.csv').open()));by={r['filename']:r for r in rows}
f=json.loads((D/'wing_feature_inspection.json').read_text())
M=D/'assembled-meshes';M.mkdir(exist_ok=True)
manifest=[];meshes={}
def get(name):
 r=by[name];assert hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()==r['sha256'];return r

def save(name,m,source,transform,method,features):
 path=M/(name+'.ply');m.export(path);meshes[name]=m
 manifest.append({'component':name,'source':get(source),'native_to_assembly_native_4x4':np.asarray(transform).tolist(),'derived_mesh':str(path),'mesh_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'placement_method':method,'features':features,'bounds_native_mm':m.bounds.tolist(),'analysis_tessellation_linear_tolerance_mm':.025 if source.endswith('.STEP') else None})

def stepmesh(name,solid):
 s=cq.importers.importStep(get(name)['path']).solids().vals()[solid-1];v,ff=s.tessellate(.025,.1);return trimesh.Trimesh(np.array([p.toTuple() for p in v]),np.array(ff),process=False)
# CAD native frame retained during mating: X span, Y up, Z aft. Left STEP mirrored for right.
R=np.diag([-1.,1,1,1])
main=next(v for v in f['step']['WING 1.1 L VTOL MODIFIER.STEP'] if v['type']=='CYLINDER' and abs(v['radius']-5.3)<1e-5)
rear=next(v for v in f['step']['WING 1.1 L VTOL MODIFIER.STEP'] if v['type']=='CYLINDER' and abs(v['radius']-4.3)<1e-5)
spine=next(v for v in f['step']['WING 1.2 L VTOL MODIFIER.STEP'] if v['type']=='CYLINDER' and abs(v['radius']-3.25)<1e-5)
hinge=next(v for v in f['step']['WING 1.2 L VTOL MODIFIER.STEP'] if v['type']=='CYLINDER' and abs(v['radius']-1.75)<1e-3)
def axis_at(feature,right_x):
 o=np.array(feature['origin']);a=np.array(feature['axis']);return (o+((-right_x-o[0])/a[0])*a)[1:]
for name,solid,label in [('WING 1.1 L VTOL MODIFIER.STEP',2,'right_wing_1p1'),('WING 1.2 L VTOL MODIFIER.STEP',1,'right_wing_1p2')]:
 m=stepmesh(name,solid);m.apply_transform(R)
 save(label,m,name,R,'Physical solid only; mirror left CAD to right. Front/rear spar bores coincide with FUS3, FUS ROOT and WING ROOT; both independent bores fix incidence and roll; root/end butt planes fix span. VTOL 1.1/1.2 joint has matching two alignment recess axes.',{'front_spar':main,'rear_spar':rear,'physical_solid_1_based':solid,'modifiers_excluded':True})
# Each STL was independently translated upward for printing. Undo via manufacturing bores.
for name,label,radius,feature in [('WING 2 R.STL','right_wing_2',5.3,main),('WING 3 R.STL','right_wing_3',3.25,spine),('WINGTIP 3 R.STL','right_wingtip',3.25,spine)]:
 data=f['stl'][name];observed=min(data['loops'],key=lambda q:abs(q['radius']-radius)+q['circle_rms_mm']*10)
 expected=axis_at(feature,data['station_native_x']);center=np.array(observed['circle_yz']);shift=expected-center
 # Source chordwise placement is checked, not shifted to hide a mismatch.
 assert abs(shift[1])<.025,(name,shift)
 T=np.eye(4);T[1,3]=shift[0]
 m=trimesh.load_mesh(get(name)['path'],process=False);m.apply_transform(T)
 checks=[]
 # Independent second axis where closed loop exists (rear main spar or hinge).
 secfeature=rear if label=='right_wing_2' else hinge
 sec_radius=4.3 if label=='right_wing_2' else 1.75
 possible=[q for q in data['loops'] if abs(q['radius']-sec_radius)<.04 and q['circle_rms_mm']<.025]
 if possible:
  q=possible[0];actual=np.array(q['circle_yz'])+np.array([shift[0],0]);target=axis_at(secfeature,data['station_native_x']);checks.append({'feature':'rear spar' if sec_radius==4.3 else 'hinge','residual_center_mm':float(np.linalg.norm(actual-target))});assert checks[-1]['residual_center_mm']<.03
 # Verify hinge cylinder arc on wing 3 near span-end bearing, even though section at 600 has open hinge contour.
 if label=='right_wing_3':
  pp=np.asarray(m.vertices);pred=np.array([axis_at(hinge,x) for x in pp[:,0]]);dist=np.linalg.norm(pp[:,1:]-pred,axis=1)
  near=pp[(np.abs(dist-1.75)<.012)&(pp[:,0]>715)]
  checks.append({'feature':'open hinge bearing arc at outer joint','matching_vertices':len(near),'nominal_radius_mm':1.75,'radial_tolerance_mm':.012})
  assert len(near)>8
 save(label,m,name,T,'Butt-face span coordinates retained and checked against adjoining panel planes; upward print translation removed by spar center. Second spar/hinge used as independent consistency check. No native-coordinate-only placement.',{'primary_bore':observed,'expected_primary_yz':expected.tolist(),'primary_chordwise_residual_mm':float(shift[1]),'secondary_checks':checks})
for solid in [1,2]:
 m=stepmesh('AILERON L.STEP',solid);m.apply_transform(R)
 save('right_aileron_'+str(solid),m,'AILERON L.STEP',R,'Two real control segments; source hinge axis coincides with fixed-wing 3.5mm bore axis (3.8mm moving bearing). Span joint and outer skin continuity define neutral; no control rotation applied.',{'physical_solid_1_based':solid,'hinge_axis':hinge,'neutral_convention':'source tangent/outer-skin neutral; additionally inspect merged sections'})
for name,label in [('FUS ROOT L.STEP','right_fuselage_root_plate'),('WING ROOT L.STEP','right_wing_root_plate')]:
 m=stepmesh(name,1);m.apply_transform(R);save(label,m,name,R,'Two main spar axes and independent root pins coincide with FUS3 and wing; mating faces bound span 88/90/92mm.',{'spar_axes_checked_against':'wing_feature_inspection.json'})
# Check axial butt surfaces: triangle vertices show actual shared nominal boundary planes.
for a,b,x in [('right_wing_1p1','right_wing_1p2',260.15695513675854),('right_wing_1p2','right_wing_2',318.),('right_wing_2','right_wing_3',524.),('right_wing_3','right_wingtip',730.)]:
 for n in [a,b]:assert np.count_nonzero(np.abs(meshes[n].vertices[:,0]-x)<.025)>8,(n,x)
# Analytic spars across FUS3 and wing must have same transverse center, to roundoff.
res=[]
for r in [5.3,4.3]:
 fs=next(q for q in f['step']['FUS3.STEP'] if q['type']=='CYLINDER' and abs(q['radius']-r)<1e-6)
 ws=next(q for q in f['step']['WING 1.1 L VTOL MODIFIER.STEP'] if q['type']=='CYLINDER' and abs(q['radius']-r)<1e-6)
 residual=float(np.linalg.norm(np.array(fs['origin'])[1:]-np.array(ws['origin'])[1:]));assert residual<1e-8;res.append({'radius_mm':r,'center_residual_mm':residual})
# Planform, with explicitly conventional (not source solid) centerline carry-through.
shapes={}
for n,m in meshes.items():
 if 'plate' in n:continue
 tri=m.triangles[:,:,[0,2]];a=tri[:,1]-tri[:,0];b=tri[:,2]-tri[:,0];tri=tri[np.abs(a[:,0]*b[:,1]-a[:,1]*b[:,0])>1e-9]
 u=shapely.union_all(shapely.polygons(tri));ps=list(u.geoms) if isinstance(u,MultiPolygon) else [u];shapes[n]=shapely.union_all([Polygon(p.exterior) for p in ps if p.geom_type=='Polygon'])
u=shapely.union_all(list(shapes.values()));section=u.intersection(LineString([(92.1,-1000),(92.1,1000)]));bb=section.bounds;root_chord=bb[3]-bb[1]
summary={'wing_status':'feature_mated_with_source_tessellation_tolerances; full_aircraft_gate_pending','aircraft_frame_pending':'x=native Z; y=native X; z=native Y; origin to be fixed at root LE','fuselage_spar_center_checks':res,'span_mm':2*u.bounds[2],'exposed_both_wings_dm2':2*u.area/10000,'root_chord_at_92p1_mm':root_chord,'gross_area_convention':'Exposed outer silhouette including neutral ailerons plus rectangular centerline continuation of root-region chord. Not physical hidden wing. Root plates not separately added to avoid overlap.','centerline_continuation_dm2':184*root_chord/10000,'gross_area_dm2':2*u.area/10000+184*root_chord/10000,'source_preservation':'hash checked before reads; all originals unchanged','components':manifest}
(D/'wing_assembly.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({k:v for k,v in summary.items() if k!='components'},indent=2))
print('PASS wing feature constraints, independent spar/hinge checks, butt planes, source hashes; meshes',len(manifest))

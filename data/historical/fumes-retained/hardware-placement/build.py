from pathlib import Path
import cadquery as cq,numpy as np,trimesh,json,hashlib
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.gp import gp_Trsf
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
O=Path(__file__).resolve().parent;R=O.parents[1];C=O/'components';C.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(n,d):(O/n).write_text(json.dumps(d,indent=2))
input_paths=[R/'cfd-exterior-v2/readiness-review/RELEASE_GATES.json',R/'cfd-exterior-v1/hardware/RESULTS.json',R/'cfd-corrections-v1/hardware/EVIDENCE.json',R/'showcase/hybrid-v2-final/assembly-manifest.json',R/'cfd-corrections-v1/hardware/vtol-page-36.png']
baseline={str(p):sha(p) for p in input_paths};dump('INPUT_BASELINE.json',baseline)
gates=json.loads(input_paths[0].read_text());retained=json.loads(input_paths[1].read_text());outs=[];shapes={}
def transform(s,T):
 t=gp_Trsf();t.SetValues(*T[:3,:].reshape(-1).tolist());return cq.Shape.cast(BRepBuilderAPI_Transform(s.wrapped,t,True).Shape())
def write_obj(p,m):
 with p.open('w') as f:
  f.write('# CFD APPROXIMATE; metre coordinates; +X forward +Y left +Z up\n')
  for v in m.vertices:f.write('v '+' '.join(format(float(x),'.17g') for x in v)+'\n')
  for t in m.faces:f.write('f '+' '.join(str(int(x)+1) for x in t)+'\n')
def export(name,s,role,meta,T=None):
 assert s.isValid() and len(s.Solids())==1
 BRepMesh_IncrementalMesh(s.wrapped,.06,False,.2,True).Perform();v,f=s.tessellate(.06,.2)
 original=np.array([p.toTuple() for p in v]);v=np.round(original,9);canonical_delta=float(np.max(np.linalg.norm(v-original,axis=1)))
 v,inv=np.unique(v,axis=0,return_inverse=True);f=inv[np.array(f)];m=trimesh.Trimesh(v,f,process=False)
 assert m.is_watertight and m.is_winding_consistent and m.volume>0
 if T is not None:s=transform(s,T);m.apply_transform(T)
 shapes[name]=s;step=C/(name+'.step');obj=C/(name+'-m.obj');cq.exporters.export(s,str(step));m.vertices*=.001;write_obj(obj,m)
 row={'name':name,'role':role,'exact_vendor_CAD':False,'approximation_authorized':True,'obj':str(obj),'obj_units':'m','step':str(step),'step_units':'mm','step_origin':'native OpenCascade approximation, NOT recovered manufacturer CAD','obj_sha256':sha(obj),'step_sha256':sha(step),'bounds_m':m.bounds.tolist(),'cad_volume_mm3':s.Volume(),'mesh_volume_m3':m.volume,'triangles':len(m.faces),'mesh_canonicalization_mm_grid':1e-9,'max_canonicalization_displacement_mm':canonical_delta,**meta}
 if T is not None:
  row['local_to_aircraft_mm']=T.tolist();Tm=T.copy();Tm[:3,3]*=.001;row['local_to_aircraft_m']=Tm.tolist();row['transform_already_applied']=True
 outs.append(row);print(name,len(m.faces),'closed',m.is_watertight,flush=True);return row
# Axial coordinates measured from nominal mounting seat, positive toward shaft tip.
# Radii/undimensioned details are explicit design assumptions. Drawing shoulders/tips stay fixed.
profiles={
 'F90':[(0,0),(12,0),(12,3),(7,3),(7,6.2),(16.7,6.2),(16.7,18.2),(14.5,19.7),(2.5,19.7),(2.5,34.7),(0,34.7)],
 'Avenger2812V5':[(0,0),(12.5,0),(12.5,3.4),(7,3.4),(7,6.45),(16.95,6.45),(16.95,25.5),(15,27.05),(2.5,27.05),(2.5,44.05),(0,44.05)]}
local={}
for model,p in profiles.items():
 s=cq.Workplane('XZ').polyline(p).close().revolve(360,(0,0),(0,1)).val();local[model]=s
 export(model+'_axisymmetric_local',s,'LOCAL_DEFINITION_DO_NOT_INSTALL',{'coordinate_frame':'local_mm_before_OBJ_conversion','profile_r_z_mm':p,'omitted':'vent openings, stator fins, winding roughness, wires, mounting bores, screws, nut, thread helix, rear shaft clip','documented_dimensions':'maximum diameter, seat-to-tip, prop-side shoulder and M5 smooth shaft; Avenger rear bell offset6.45','assumed_dimensions':'base diameter/height, neck diameter/height, taper dimensions; F90 bell rear offset6.2'})
for r in retained['outputs']:
 if r['name'].startswith(('F90_mount_','Avenger2812V5_mount_')):
  model='F90' if r['name'].startswith('F90') else 'Avenger2812V5';T=np.array(r['local_to_aircraft_mm'])
  export(r['name']+'_CFD_APPROXIMATE',local[model],'BASELINE_INSTALLED_MOTOR',{'mount_instance_index':r['mount_instance_index'],'seat_center_mm':r['seat_center_mm'],'shaft_direction':r['shaft_direction'],'motor_roll':'axisymmetric approximation; roll unobservable','source_transform':'unchanged retained v1 RESULTS and readiness-release gates','physical_fit_released':False},T)
# Native source booms: preserve documentary positions. Circular bore explicitly assumed, not a square bore.
cz=-9.059145548465365;cut_center=-112.46047687230817
for side,cy in [('R',-260.1569551367584),('L',260.15695486324154)]:
 T=np.eye(4);T[:3,3]=[0,cy,cz]
 for variant,bore,cut in [('bore8_open_ends_cable24x5',8,True),('bore6_open_ends_cable24x5',6,True),('bore9_open_ends_cable24x5',9,True),('bore8_open_ends_taped_cable',8,False),('sealed_exterior_void_ignored',None,False)]:
  s=cq.Solid.makeBox(500,10,10,cq.Vector(-315,-5,-5))
  if bore is not None:s=s.cut(cq.Solid.makeCylinder(bore/2,502,cq.Vector(-316,0,0),cq.Vector(1,0,0)))
  if cut:s=s.cut(cq.Solid.makeBox(24,5,6,cq.Vector(cut_center-12,-2.5,-6)))
  export('boom_'+side+'_'+variant,s,'BASELINE_INSTALLED_BOOM' if variant=='bore8_open_ends_cable24x5' else 'ALTERNATIVE_NOT_ADDITIVE',{'side':side,'outer_mm':[10,10,500],'bore_diameter_mm':bore,'minimum_side_wall_mm':(10-bore)/2 if bore else None,'end_policy':'open annular end faces (material closed; fluid bore connected)' if bore else 'assumed sealed square exterior; enclosed fluid cavity ignored, not a physical solid carbon tube','cable_opening_mm':{'center_x':cut_center,'length_x':24,'width_y':5,'side':'-Z underside','depth':'single underside wall to bore'} if cut else None,'cable_policy':'assumed unsealed rectangular underside opening' if cut else 'assumed tape/epoxy flush closure','cut_source':'p36 requires underside single-wall cable cut; size/center assumed near guide-station midpoint, NOT measured','bore_source':'retained p10 recommends circular inner profile; diameter assumed; nominal1mm min side wall not measured'},T)
# CAD BRep Boolean contact/overlap receipt, numerical OCC tolerances distinct from serialized exact checks.
base=[r for r in outs if r['role'].startswith('BASELINE_INSTALLED')];pairs=[]
for i,a in enumerate(base):
 for b in base[i+1:]:
  common=shapes[a['name']].intersect(shapes[b['name']]);pairs.append({'a':a['name'],'b':b['name'],'common_volume_mm3':common.Volume(),'common_faces':len(common.Faces())})
assert all(abs(x['common_volume_mm3'])<1e-7 for x in pairs)
dump('CAD_BASELINE_INTERSECTIONS.json',{'method':'OCC native BRep Boolean common; tolerance-based CAD not exact arithmetic','pairs':pairs,'positive_volume_overlap':False,'scope':'7 hardware only; no full parent-airframe screen'})
# Reuse source-original mounted clamp BReps and unchanged transforms; front +10 correction is retained.
manifest=json.loads(input_paths[3].read_text());rows={r['instance_index']:r for r in manifest['rows']};checks=[]
for idx in range(49,65):
 r=rows[idx];p=Path(r['source_step']);p=p if p.is_absolute() else R/'source-format-audit/originals'/r['pack']/p.name;baseline[str(p)]=sha(p)
 s=cq.importers.importStep(str(p)).solids().vals()[r['step_body_index']-1];T=np.array(r['step_to_assembly_mm']);
 if idx in [55,56,63,64]:T[0,3]+=10
 s=transform(s,T);side='R' if idx<57 else 'L';boom=shapes['boom_'+side+'_bore8_open_ends_cable24x5'];c=boom.intersect(s)
 checks.append({'clamp_instance':idx,'hardware':'boom_'+side,'overlap_mm3':c.Volume(),'source_step':str(p),'source_sha256':sha(p),'source_to_aircraft_mm':T.tolist()})
for idx in [53,55,61,63,11]:
 r=rows[idx];p=Path(r['source_step']);p=p if p.is_absolute() else R/'source-format-audit/originals'/r['pack']/p.name;baseline[str(p)]=sha(p);s=cq.importers.importStep(str(p)).solids().vals()[r['step_body_index']-1];T=np.array(r['step_to_assembly_mm']);
 if idx in [55,63]:T[0,3]+=10
 s=transform(s,T);name=('Avenger2812V5' if idx==11 else 'F90')+f'_mount_{idx:03d}_CFD_APPROXIMATE';c=shapes[name].intersect(s);checks.append({'mount_instance':idx,'hardware':name,'overlap_mm3':c.Volume(),'source_step':str(p),'source_sha256':sha(p),'source_to_aircraft_mm':T.tolist()})
dump('CAD_MOUNT_INTERSECTIONS.json',{'checks':checks,'method':'OCC BRep common, 16 boom halves plus 5 motor primary mounts; not a full assembly pair audit','all_zero_positive_volume':all(abs(x['overlap_mm3'])<1e-7 for x in checks)})
dump('INPUT_BASELINE.json',baseline)
result={'configuration':'original standard 1.62m Stork; CFD APPROXIMATE hardware, not enlarged mission','status':'BUILT_PENDING_INDEPENDENT_VERIFY','axes':{'+X':'forward','+Y':'left','+Z':'up'},'components':outs,'baseline_installed_names':[r['name'] for r in base],'baseline_count':len(base),'source_preserved':all(sha(p)==h for p,h in baseline.items()),'native_vendor_CAD_recovered':False,'approximation_limits':['No exact motor vent/open stator topology; axisymmetric closed motor replacement excludes cooling flow','Motor base/neck/tapers assumed; nominal drawing dimensions and shaft directions preserved','Boom bore6/8/9 variants, cable cut and end sealing assumed; pick exactly one variant per side','No propellers, shaft nuts, exposed wires or ancillary fasteners; no exact physical installed fit','No whole-parent-airframe exact intersection/CFD release; parent remains unchanged'],'motor_sensitivity_recommendations':{'F90_base_diameter_mm':[22,24,28],'F90_bell_rear_offset_mm':[4.5,6.2,8],'Avenger_base_diameter_mm':[22,25,28],'note':'suggested future parameters, not all exported; documented max diameter/shoulder/total lengths must remain fixed'}}
dump('RESULTS.json',result);assert result['source_preserved'];print('DONE',len(outs),'pairs, baseline',len(base), 'mount checks',len(checks),flush=True)

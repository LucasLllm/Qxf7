"""Combine feature receipts and recheck the parent gate. NO aerodynamic station extraction."""
from pathlib import Path
import csv,json,hashlib
import numpy as np
import cadquery as cq
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
D=Path(__file__).resolve().parent
rows=list(csv.DictReader((D.parent/'source-format-audit/cad_inventory.csv').open()));by={r['filename']:r for r in rows}
for r in rows:assert hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()==r['sha256']
f=json.loads((D/'fuselage-feature-work/verified_chain.json').read_text());t=json.loads((D/'tail-feature-work/placements.json').read_text());w=json.loads((D/'wing_assembly.json').read_text())
assert f['sources_unchanged'] and t['source_hashes_unchanged']
OUT=D/'reference-assembly';OUT.mkdir(exist_ok=True)
P=np.eye(4);P[:3,:3]=[[0,0,1],[1,0,0],[0,1,0]]
R=np.diag([-1.,1,1,1]);I=np.eye(4)
scene=trimesh.Scene();records=[];models={}
colors={'wing':[65,145,220,255],'fuselage':[165,174,183,255],'tail':[233,163,70,255],'hardware':[82,97,108,255]}
def load(name,body=None):
 r=by[name];assert hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()==r['sha256']
 if name.endswith('.STEP'):
  s=cq.importers.importStep(r['path']).solids().vals()[body-1];v,ff=s.tessellate(.025,.1);m=trimesh.Trimesh(np.array([q.toTuple() for q in v]),np.array(ff),process=False)
 else:m=trimesh.load_mesh(r['path'],process=False)
 return m

def add(label,name,body,T,category,evidence,mesh=None):
 r=by[name];m=load(name,body) if mesh is None else mesh.copy();T=np.asarray(T)
 if mesh is None:m.apply_transform(T)
 m.apply_transform(P);m.visual.face_colors=colors[category];models[label]=m;scene.add_geometry(m,geom_name=label,node_name=label)
 records.append({'component':label,'source_path':r['path'],'source_filename':name,'source_sha256':r['sha256'],'physical_solid_1_based':body,'source_native_to_common_native':T.tolist(),'common_native_to_aircraft':P.tolist(),'bounds_aircraft_mm':m.bounds.tolist(),'faces':len(m.faces),'category':category,'mating_evidence':evidence,'output_is_tessellated_analysis_copy':True})
# Wing receipts already contain feature-placed right meshes. Symmetric opposite is explicit.
for c in w['components']:
 m=trimesh.load_mesh(c['derived_mesh'],process=False);assert hashlib.sha256(Path(c['derived_mesh']).read_bytes()).hexdigest()==c['mesh_sha256']
 name=c['source']['filename'];body=c['features'].get('physical_solid_1_based',1 if name.endswith('.STEP') else None)
 add(c['component'],name,body,c['native_to_assembly_native_4x4'],'wing','wing_assembly.json: '+c['placement_method'],m)
 ml=m.copy();ml.apply_transform(R);add(c['component'].replace('right_','left_'),name,body,R@np.array(c['native_to_assembly_native_4x4']),'wing','Symmetric counterpart of feature-registered right component; not independently registered left STL',ml)
for name,part in f['parts'].items():add('fuselage_'+name.replace('.STEP','').replace('.STL',''),name,part.get('physical_body_one_based'),part['transform_source_to_native'],'fuselage','fuselage-feature-work/verified_chain.json joints/fus4_registration/nose_interface')
for i in [1,2,3]:
 name=f'V TAIL {i} R.STL';T=np.array(t['transforms'][name]['native_STL_to_native_STEP_right']);add(f'right_fixed_tail_{i}',name,None,T,'tail','tail-feature-work/placements.json: root plane and three cylinder axes, sequential end-cap/axis constraints');add(f'left_fixed_tail_{i}',name,None,R@T,'tail','Mirror of feature-verified right fixed-tail mesh; no independent left STL geometry claim')
for i in [1,2]:
 name='RUDDER L.STEP';add(f'left_ruddervator_{i}',name,i,I,'tail','tail-feature-work/placements.json: exact original hinge axis, saved-source-zero pose; aerodynamic neutral not yet certified');add(f'right_ruddervator_{i}',name,i,R,'tail','Mirrored original left smooth STEP, both real segments retained, saved-source zero')
for key in ['skids','pusher_mount']:
 hw=f['hardware'][key];add(key,hw['source'],1,hw['transform_source_to_native'],'hardware','fuselage-feature-work/verified_chain.json hardware.'+key+' (authored clearances retained)')
for j,place in enumerate(f['hardware']['boom_mount_pair']['placements']):
 for i,name in enumerate(f['hardware']['boom_mount_pair']['sources']):add(f"{place['side']}_{place['station']}_boom_mount_{i+1}",name,1,place['transform_mount_source_to_native'],'hardware','fuselage-feature-work/verified_chain.json hardware.boom_mount_pair.placements: two pocket axes and seat plane')
# Lower-bound complete-aircraft bounding length: this registered subset already exceeds tolerance.
bounds=np.array([m.bounds for m in models.values()]);lo=bounds[:,0,:].min(axis=0);hi=bounds[:,1,:].max(axis=0)
front=min(records,key=lambda r:r['bounds_aircraft_mm'][0][0]);back=max(records,key=lambda r:r['bounds_aircraft_mm'][1][0]);length=float(hi[0]-lo[0]);span=float(hi[1]-lo[1]);area=w['gross_area_dm2']
checks=[]
for q,value,target,units in [('span',span,1620.,'mm'),('length_registered_airframe',length,1000.,'mm'),('gross_wing_reference_area',area,31.,'dm2')]:
 err=100*(value-target)/target;checks.append({'quantity':q,'measured':value,'target':target,'units':units,'signed_error_percent':err,'absolute_error_percent':abs(err),'tolerance_percent':2.,'pass':abs(err)<=2.})
assert span<2000 and length>1000
failed=[q['quantity'] for q in checks if not q['pass']]
# This is a failure receipt, not a passed flightworthiness or complete-hardware certificate.
result={'status':'STOP_MEASURED_GEOMETRY_GATE_FAILURE' if failed else 'PASS_GEOMETRY_GATE_ONLY','controlling_targets':'Lucas continuation after resolving current gross-area reference as31dm2; span1620mm and approximately1000mm overall length retained,2% stop rule','checks':checks,'failed_quantities':failed,'aircraft_axes':'x aft=nativeZ; y right=nativeX; z up=nativeY','origin':'Original common STEP CAD datum(0,0,0), not claimed wing-root LE; source frame fixed by fuselage pin chain and spar axes. Translation cannot alter tested dimensions.','registered_component_count':len(records),'frontmost_component':front['component'],'rearmost_component':back['component'],'frontmost_aircraft_x_mm':float(lo[0]),'rearmost_aircraft_x_mm':float(hi[0]),'overall_registered_bounds_mm':[lo.tolist(),hi.tolist()],'length_scope':'Bounding extent of registered main airframe, fixed tail/control surfaces and located skids/pusher/boom clamps. Final equipped length unknown; missing hardware cannot reduce this already failing extent.','manufacturer_1000mm_reference_nose_to_pusher_mount_mm':f['length']['mm'],'reference_length_not_overall_length':True,'gross_area_convention':w['gross_area_convention'],'control_surface_status':'Saved-source zero/no added hinge rotations; hinge alignment verified, aerodynamic neutral and commanded zero not established before gate.','excluded_unresolved':['Four lift motor mount pairs: continuous boom-axis translation/end assignments unresolved','Boom tube fore/aft datum orientation unresolved; conditional intervals in hardware receipt, no guessed installed tubes','Actual motors/propellers/electronics/fasteners not supplied as complete geometry','Front reinforcement XY placement not solved;3mm nose interface layer retained','Small covers/retainers/rear fin tip not exhaustively registered; not a whole-aircraft-completeness claim'],'next_action':'STOP downstream aerodynamic stations/angles/UIUC matching until Lucas adjudicates overall-length reference. Do not shorten/scale geometry to force pass.','components':records}
(OUT/'assembly_manifest.json').write_text(json.dumps(result,indent=2)+'\n');(D/'reference_gate.json').write_text(json.dumps({k:v for k,v in result.items() if k!='components'},indent=2)+'\n')
glb=OUT/'Stork-feature-registered-gate-review.glb';scene.export(glb)
# Review overlays expose the discrepancy and missing components rather than disguising them.
for view,ix,iy in [('top',1,0),('front',1,2),('side',0,2)]:
 fig,ax=plt.subplots(figsize=(12,7));seen=set()
 for rec in records:
  m=models[rec['component']];cat=rec['category'];v=np.asarray(m.vertices);ax.scatter(v[:,ix],v[:,iy],s=.12,alpha=.45,color=np.array(colors[cat][:3])/255,label=cat if cat not in seen else None,rasterized=True);seen.add(cat)
 if view=='side':
  ax.axvline(lo[0]+1000,color='red',linestyle='--',label='1000mm from nose');ax.axvline(lo[0]+1020,color='red',linestyle=':',label='+2% length limit');ax.annotate(f'Actual registered aft extent\n{length:.2f}mm from nose',(hi[0],hi[2]),xytext=(hi[0]-250,hi[2]+60),arrowprops={'arrowstyle':'->'},fontsize=9)
 ax.set_aspect('equal');ax.set_xlabel(['x aft(mm)','y right(mm)','z up(mm)'][ix]);ax.set_ylabel(['x aft(mm)','y right(mm)','z up(mm)'][iy]);ax.set_title('Stork feature-registered subset: '+view+' review — LENGTH GATE FAILED\nNot complete hardware, not aerodynamic/flightworthiness validation');ax.grid(alpha=.2);ax.legend(markerscale=8,fontsize=8);fig.tight_layout();fig.savefig(OUT/(view+'_outline_overlay.png'),dpi=170);plt.close(fig)
# Read-back serialized geometry and counts are verified, independently of source BRep bounds.
reread=trimesh.load(glb,force='scene',process=False);assert len(reread.geometry)==len(records)
assert np.allclose(reread.bounds,np.array([lo,hi]),atol=.0002), (reread.bounds,[lo,hi])
for r in rows:assert hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()==r['sha256']
verification={'source_hash_checks':len(rows),'source_mismatches':0,'glb_geometry_count':len(reread.geometry),'manifest_components':len(records),'glb_bounds_matches_manifest_atol_mm':.0002,'glb_sha256':hashlib.sha256(glb.read_bytes()).hexdigest(),'gate_status':result['status'],'aero_station_extraction_performed':False,'all_checks_pass_except_intentional_geometry_gate_failure':True}
(OUT/'parent_verification.json').write_text(json.dumps(verification,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='components'},indent=2));print('VERIFICATION',json.dumps(verification))

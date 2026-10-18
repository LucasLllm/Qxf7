"""Read-only CAD extraction. All writes restricted to script directory.
Exterior model: convex hull of *planar section edges*, never manufacturing-solid area.
Includes complete feature-verified hatch solids; convexifies cavities and remaining seams/concavity.
Loft is an explicit envelope approximation, not exact installed exposed CAD area.
"""
from pathlib import Path
import json,hashlib,csv,time,pickle,sys
sys.path.insert(0,'/Users/lucasliu/.hermes/profiles/fumes/notes/stork-development/stork-aero-geometry/fuselage-extraction')
from parameter_sampler import sample_edge,sample_wire,TOL_MM,MAX_CHORD_MM
SAMPLING_DIAGNOSTICS=[]
import numpy as np
import cadquery as cq,trimesh
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.gp import gp_Pln,gp_Pnt,gp_Dir
from scipy.spatial import ConvexHull
from shapely.geometry import Polygon
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
O=Path(__file__).resolve().parent; F=O.parent/'fuselage-feature-work'
D=json.loads((F/'verified_chain.json').read_text()); A=json.loads((F/'analytic_features.json').read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
sources={str(F/n):sha(F/n) for n in ['verified_chain.json','analytic_features.json','fus4_mesh_features.json','guide35.png']}
sources[str(O.parent/'extraction_authorization.json')]=sha(O.parent/'extraction_authorization.json')
parts=[]
for name,p in D['parts'].items():
 sources[p['source']]=sha(p['source']);assert sources[p['source']]==p['sha256']
 if name.endswith('STEP'):
  s=cq.importers.importStep(p['source']).solids().vals()[p['physical_body_one_based']-1]; b=s.BoundingBox();bounds=[b.zmin,b.zmax]
 else:
  s=trimesh.load(p['source']);s.apply_transform(p['transform_source_to_native']);bounds=s.bounds[:,2].tolist()
 parts.append(dict(name=name,shape=s,bounds=bounds))

BASELINE=O.parent/'fuselage-extraction'
HATCH=O.parent/'hatch-feature-work'
baseline_results=json.loads((BASELINE/'results.json').read_text())
baseline_cache=Path(baseline_results['sampling']['section_cache_directory'])
placement=json.loads((HATCH/'placement.json').read_text())
manifest=json.loads((HATCH/'manifest.json').read_text())
for filename,h in manifest.items():
 assert sha(HATCH/filename)==h,(filename,'hatch manifest mismatch')
 sources[str(HATCH/filename)]=h
for src in placement['sources'].values():
 assert sha(src['path'])==src['sha256']
 sources[src['path']]=src['sha256']
for filename in ['extract.py','parameter_sampler.py','hardware.json','results.json']:
 sources[str(BASELINE/filename)]=sha(BASELINE/filename)
for path,h in baseline_results['source_hashes'].items():
 assert sha(path)==h
 sources[path]=h
hatch_solids=cq.importers.importStep(str(HATCH/'installed_hatches.step')).solids().vals()
assert len(hatch_solids)==4 and all(s.isValid() for s in hatch_solids)
for i,(s,receipt) in enumerate(zip(hatch_solids,placement['placements'])):
 assert abs(s.Volume()-receipt['volume_mm3'])<.01
 assert len(s.Faces())==receipt['face_count']
 b=s.BoundingBox()
 parts.append(dict(name=f"HATCH:{receipt['source']}:body{receipt['body_one_based']}",shape=s,bounds=[b.zmin,b.zmax]))

lo=min(p['bounds'][0]for p in parts); hi=max(p['bounds'][1]for p in parts)
cache={}
# No source cache existed after the crashed process. Cache each newly measured section.
cache_tag=hashlib.sha256((json.dumps(sources,sort_keys=True)+sha(BASELINE/'parameter_sampler.py')+'v2-no-gap-invention').encode()).hexdigest()[:16]
cache_dir=O/'section_cache'/cache_tag;cache_dir.mkdir(parents=True,exist_ok=True)
intervals=sorted([p['bounds'] for p in parts]);gaps=[];end=intervals[0][1]
for a,b in intervals[1:]:
 if a>end+1e-4:gaps.append([end,a])
 end=max(end,b)
class MissingSection(RuntimeError):pass

def section(x):
 k=round(float(x),8)
 if k in cache:return cache[k]
 cp=cache_dir/f'{k:.8f}.pickle'
 if cp.exists():
  with cp.open('rb') as f:r=pickle.load(f)
  cache[k]=r;return r
 clouds=[];wiredata=[]; names=[];wiremeta=[];edge_diag=[]
 bp=baseline_cache/f'{k:.8f}.pickle'
 baseline_loaded=bp.exists()
 if baseline_loaded:
  with bp.open('rb') as f:br=pickle.load(f)
  clouds=[br['points']];wiredata=list(br['wires']);names=list(br['names']);wiremeta=list(br['raw']);edge_diag=list(br['edge_diagnostics'])
 # Report actual x and evaluated inward-limit plane separately; never contract bounds.
 xx=min(max(x,lo+0.002),hi-0.002)
 for p in parts:
  if baseline_loaded and not p['name'].startswith('HATCH:'):continue
  if not p['bounds'][0]+1e-5<xx<p['bounds'][1]-1e-5:continue
  s=p['shape'];names.append(p['name'])
  if isinstance(s,trimesh.Trimesh):
   cut=s.section(plane_origin=[0,0,xx],plane_normal=[0,0,1])
   if cut is not None:
    clouds.append(cut.vertices[:,:2])
    for q in cut.discrete:
     if np.linalg.norm(q[0]-q[-1])<2e-4:
      wiredata.append(q[:,:2]);wiremeta.append({'source':p['name'],'exact_perimeter_mm':None,'method':'source triangle-plane intersection'})
  else:
   op=BRepAlgoAPI_Section(s.wrapped,gp_Pln(gp_Pnt(0,0,xx),gp_Dir(0,0,1)),False);op.Build()
   if not op.IsDone():raise RuntimeError(f'Section operation failed {p["name"]} x={xx}')
   edges=cq.Shape.cast(op.Shape()).Edges()
   for e in edges:
    arr,diag=sample_edge(e);clouds.append(arr[:,:2]);edge_diag.append(dict(diag,source=p['name']))
   for w in cq.Wire.combine(edges,tol=1e-4):
    if w.IsClosed():
     arr,meta=sample_wire(w);wiredata.append(arr);wiremeta.append(dict(meta,source=p['name'],method='ordered edge-local parameter samples'))
 if not clouds:raise MissingSection(f'No registered physical section at x={x}; unresolved connection is NOT invented')
 points=np.vstack(clouds)
 hull=ConvexHull(points);poly=points[hull.vertices];P=Polygon(poly)
 raw=[]
 for w,meta in zip(wiredata,wiremeta):
  if len(w)>2:
   q=Polygon(w);raw.append(dict(meta,area_mm2=float(q.area),perimeter_mm=float(q.length),valid=bool(q.is_valid)))
 r={'x':float(x),'evaluated_x':float(xx),'poly':poly,'raw':raw,'names':names,'width':float(np.ptp(poly[:,0])),'height':float(np.ptp(poly[:,1])),'area':float(P.area),'perimeter':float(P.length),'points':points,'wires':wiredata,'edge_diagnostics':edge_diag}
 with cp.open('wb') as f:pickle.dump(r,f,protocol=5)
 cache[k]=r;return r

def ring(poly,n):
 # Ray/hull intersection at common polar angles about polygon centroid: stable registration.
 c=np.array(Polygon(poly).centroid.coords[0]);v=poly-c; e=np.roll(v,-1,axis=0)-v
 theta=np.arange(n)*2*np.pi/n;u=np.column_stack([np.cos(theta),np.sin(theta)])
 out=[]
 for d in u:
  den=d[0]*e[:,1]-d[1]*e[:,0]; ok=np.abs(den)>1e-12
  t=np.full(len(e),np.inf);q=np.full(len(e),np.inf)
  t[ok]=(v[ok,0]*e[ok,1]-v[ok,1]*e[ok,0])/den[ok]
  q[ok]=(v[ok,0]*d[1]-v[ok,1]*d[0])/den[ok]
  good=(t>=0)&(q>=-1e-8)&(q<=1+1e-8);out.append(c+d*np.min(t[good]))
 return np.array(out)

def loft(xs,n):
 rings=np.array([ring(section(x)['poly'],n)for x in xs]);v=np.concatenate([np.broadcast_to(np.array(xs)[:,None,None],(len(xs),n,1)),rings],axis=2)
 a=v[:-1];b=np.roll(v[:-1],-1,axis=1);c=np.roll(v[1:],-1,axis=1);d=v[1:]
 tile=(np.linalg.norm(np.cross(b-a,c-a),axis=2).sum(axis=1)+np.linalg.norm(np.cross(c-a,d-a),axis=2).sum(axis=1))/2
 # Keep both measured gap lips; refuse to count an unregistered connection as material.
 unknown=np.array([any(x0<g1 and x1>g0 for g0,g1 in gaps) for x0,x1 in zip(xs[:-1],xs[1:])])
 return float(tile[~unknown].sum()),v,float(tile[unknown].sum())

# Regular native-datum and nose-relative 50mm grids, plus nose and aft endpoint.
xs=sorted(set([lo,hi]+list(np.arange(np.ceil(lo/50)*50,hi,50))+list(lo+np.arange(50,hi-lo,50))))
rows=[]
for x in xs:
 r=section(x);rows.append({'aircraft_x_mm':x,'x_from_nose_mm':x-lo,'width_mm':r['width'],'height_mm':r['height'],'convex_envelope_perimeter_mm':r['perimeter'],'convex_envelope_area_mm2':r['area'],'method':'section-edge convex exterior envelope','sources':';'.join(r['names']),'raw_closed_loop_count':len(r['raw']),'largest_raw_loop_area_mm2':max([z['area_mm2']for z in r['raw']],default=0)})
with (O/'cross_sections_50mm.csv').open('w')as f:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
conv=[]
# Boundary-adjacent stations preserve all physical longitudinal extents and abrupt
# shoulders, including both sides of the unresolved nose connector. No invented rings.
limits=[lo,hi]+[b+offset for p in parts for b,offset in [(p['bounds'][0],.002),(p['bounds'][1],-.002)]]
for dx,n in [(10,128),(5,128),(2.5,128),(10,256),(5,256),(2.5,256)]:
 grid=np.unique(np.r_[np.arange(lo,hi,dx),limits]);grid=np.array([x for x in grid if x in [lo,hi] or any(p['bounds'][0]+1e-5<x<p['bounds'][1]-1e-5 for p in parts)])
 a,v,bridge=loft(grid,n);conv.append({'dx_mm':dx,'angular_vertices':n,'lateral_envelope_area_mm2':a,'unregistered_gap_bridge_sensitivity_mm2':bridge,'conditional_with_straight_gap_bridge_mm2':a+bridge,'section_count':len(grid)})
 (O/'convergence_checkpoint.json').write_text(json.dumps(conv,indent=2))
 print('convergence',conv[-1],flush=True)
# Save all genuine closed section loops separately from simplified exterior envelope.
loops=[{'aircraft_x_mm':x,'source':section(x)['names'],'closed_section_loops_yz_mm':[w.tolist()for w in section(x)['wires']],'envelope_yz_mm':section(x)['poly'].tolist(),'loop_metrics':section(x)['raw']}for x in xs]
(O/'section_loops.json').write_text(json.dumps(loops,indent=2))
np.savez_compressed(O/'envelope_loft.npz',vertices_aircraft_mm=v)
# Hardware physical parts, excluding modifiers and guide assembly tool.
hw=[]
hardware_cache={}
if (BASELINE/'hardware.json').exists() and (BASELINE/'results.json').exists():
 previous=json.loads((BASELINE/'results.json').read_text())
 for h in json.loads((BASELINE/'hardware.json').read_text()):
  if previous['source_hashes'].get(h['source'])==sha(h['source']) and h['silhouette_tessellation_tolerance_mm']==.12:
   hardware_cache[h['part']]=h
for name,a in A.items():
 if not any(k in name for k in ['SKIDS','BOOM MOUNT 1','BOOM MOUNT 2','MOTOR MOUNT']):continue
 p=a['parts'][0];sources[a['source']]=sha(a['source']);assert sources[a['source']]==a['sha256']
 if name in hardware_cache:
  h=hardware_cache[name]
  assert h['body']==p['body'] and h['source']==a['source'] and np.allclose(h['native_bounds_mm'],p['bounds'])
  hw.append(h);continue
 s=cq.importers.importStep(a['source']).solids().vals()[p['body']-1];b=np.array(p['bounds'])
 projected={}
 verts,faces=s.tessellate(.12);verts=np.array([q.toTuple()for q in verts]);faces=np.array(faces)
 from shapely.ops import unary_union
 for axis,inds in [('frontal_yz',[0,1]),('side_xz',[2,1]),('top_xy',[2,0])]:
  triangles=[Polygon(t)for t in verts[faces][:,:,inds] if abs(np.cross(t[1]-t[0],t[2]-t[0]))>1e-10]
  projected[axis+'_mm2']=float(unary_union(triangles).area)
 hw.append({'part':name,'source':a['source'],'body':p['body'],'native_bounds_mm':b.tolist(),'dimensions_aircraft_xyz_mm':(b[1]-b[0])[[2,0,1]].tolist(),'projected_physical_silhouette_areas':projected,'silhouette_tessellation_tolerance_mm':.12,'installation':D['hardware']['skids'] if 'SKIDS'in name else D['hardware']['pusher_mount'] if '19x19'in name else D['hardware']['boom_mount_pair']['placements'] if name.startswith('BOOM') else {'installed_transform':None,'native_bounds_are_not_installed_motor_stations':True}})
for h in hw:
 h['projection_frame']='native XYZ remapped to aircraft ZXY; no installation transform applied to silhouette'
 h['interpretation']='physical-part native-axis projection, NOT net installed drag area'
 h['source_sha256']=sources[h['source']]
(O/'hardware.json').write_text(json.dumps(hw,indent=2))
with(O/'hardware_dimensions.csv').open('w')as f:
 keys=['part','length_x_mm','width_y_mm','height_z_mm','frontal_silhouette_mm2','side_silhouette_mm2','top_silhouette_mm2'];w=csv.writer(f);w.writerow(keys)
 for h in hw:w.writerow([h['part']]+h['dimensions_aircraft_xyz_mm']+list(h['projected_physical_silhouette_areas'].values()))
(O/'hardware.csv').write_text((O/'hardware_dimensions.csv').read_text())
reinforcement=D['nose_interface']['reinforcement_source_check']
sources[reinforcement['source']]=sha(reinforcement['source']);assert sources[reinforcement['source']]==reinforcement['sha256']
# Diagnostic images.
fig,axes=plt.subplots(4,5,figsize=(17,13));
for ax,r in zip(axes.flat,[section(x)for x in np.arange(-300,651,50)]):
 for q in r['wires']:ax.plot(q[:,0],q[:,1],color='grey',lw=.6)
 q=np.vstack([r['poly'],r['poly'][0]]);ax.plot(q[:,0],q[:,1],'r-',lw=1);ax.set_title(f"x={r['x']:g} mm");ax.set_aspect('equal');ax.grid(alpha=.2)
fig.suptitle('STEP section loops / FUS4 mesh (grey); convexified exterior envelope (red)');fig.tight_layout();fig.savefig(O/'section_diagnostics.png',dpi=160);plt.close(fig)
fig,axs=plt.subplots(2,1,figsize=(12,7));rr=[section(x)for x in np.arange(lo+.002,hi-.002,5)];xx=np.array([r['x']for r in rr]);
for ax,dim,col in [(axs[0],0,'y'),(axs[1],1,'z')]:
 ax.plot(xx,[r['poly'][:,dim].max()for r in rr]);ax.plot(xx,[r['poly'][:,dim].min()for r in rr]);ax.set_ylabel(col+' mm');ax.grid();ax.set_aspect('equal')
axs[1].set_xlabel('aircraft x = native Z (mm; no wing-LE datum subtraction)');fig.tight_layout();fig.savefig(O/'envelope_profiles.png',dpi=180);plt.close(fig)
R={'scope':'NO CFD / no flightworthiness claim','datum':{'aircraft_xyz':'native Z,X,Y; origin common STEP zero, not wing root LE','nose_aircraft_x_mm':lo,'fuselage_aft_x_mm':hi,'length_mm':hi-lo},'exterior_method':'Convex hull of real planar section edge samples; holes/cavity loops never subtracted or counted as extra surfaces. Complete hatches measured; remaining open slots bridged, local concavities convexified. Includes integral FUS6 ventral feature; not exact manufactured outer skin. Unregistered nose gap excluded from primary area; separate straight-bridge sensitivity only.','wetted_area_envelope_m2':conv[-1]['lateral_envelope_area_mm2']/1e6,'convergence':conv,'exclusions':['all slicer modifiers','interior walls, ribs, holes and segment end caps','guide assembly tool','wings and tails','FIN TIP VTOL separate part','motor/propeller unspecified','hardware from fuselage area; tabulated separately'],'installed_exposed_area_status':'isolated closed exterior fuselage envelope estimate; wing-root/tail/skid buried contact patches NOT subtracted, complete original hatch solids included; do not call exact exposed wetted area','end_caps':'Not added: aft pusher mating annulus/face and forward tiny .002mm truncated tip excluded.','boom_guide_cases':D['hardware']['boom_guide'],'motor_unknowns':D['hardware']['motor_mount_pair'],'source_hashes':sources,'sources_unchanged':all(sha(p)==h for p,h in sources.items()),'checks':{'positive_sections':all(r['convex_envelope_area_mm2']>0 for r in rows),'row_count':len(rows),'grid_every_50_native':all(any(abs(r['aircraft_x_mm']-x)<1e-7 for r in rows) for x in np.arange(-300,651,50)),'grid_every_50_from_nose':all(any(abs(r['x_from_nose_mm']-x)<1e-7 for r in rows)for x in np.arange(50,hi-lo,50))}}
R['convergence_last_axial_relative_change']=abs(conv[-1]['lateral_envelope_area_mm2']/conv[-2]['lateral_envelope_area_mm2']-1)
R['convergence_last_angular_relative_change']=abs(conv[-1]['lateral_envelope_area_mm2']/conv[2]['lateral_envelope_area_mm2']-1)
R['exterior_method']='Convex hull of measured section samples; holes, cavities, residual hatch seams and slots bridged, local concavities convexified. All physical part extents retained with boundary-adjacent stations. The unresolved nose connection has NO fabricated section rings and NO area in the primary estimate; straight bridge sensitivity given separately.'
R['unresolved_nose_connection']={'intervals_aircraft_x_mm':gaps,'physical_feature':'partial 3mm nose connection reinforcement; XY registration unresolved','primary_area_excludes_unregistered_connection':True,'conditional_straight_bridge_sensitivity_m2':conv[-1]['unregistered_gap_bridge_sensitivity_mm2']/1e6,'conditional_envelope_with_bridge_m2':conv[-1]['conditional_with_straight_gap_bridge_mm2']/1e6}
R['installed_exposed_area_status']='Isolated convex exterior-envelope estimate of registered fuselage portions only, NOT exact exposed wetted area. Unregistered nose connection omitted from primary area and separately bounded by straight-bridge sensitivity. Wing-root/tail/skid buried contacts NOT subtracted. All four original complete hatch solids included at feature-verified native identity.'
R['nose_interface_evidence']=D['nose_interface']
R['extraction_scope_note']='FUS2 and FUS6 files contain MODIFIER in filename, but only upstream-selected physical body 1 is used; actual slicer modifier bodies excluded. Integral FUS6 ventral extent retained. Separate FIN TIP VTOL not modeled.'
R['end_caps']='No forward finite end face, aft mating face, internal segment caps or gap-facing end caps added. Global limit sections evaluated 0.002mm inward, plotted at true physical bounds; no claim of sharp/zero-area nose tip.'
R['physical_part_bounds_aircraft_x_mm']={p['name']:p['bounds'] for p in parts}
R['hardware_projection_warning']='Native-axis physical-part silhouettes only; not net installed projected area, blockage, exposed wetted area, or installed drag.'
diags=[dict(d,aircraft_x_mm=r['x']) for r in cache.values() for d in r['edge_diagnostics']]
R['sampling']={'method':'individual edge native-parameter adaptive tessellation; wire explorer ordering; no arc-length inverse','checked_chord_deviation_tolerance_mm':TOL_MM,'max_chord_mm':MAX_CHORD_MM,'join_tolerance_mm':1e-4,'max_observed_checked_deviation_mm':max(d['max_checked_chord_deviation_mm'] for d in diags),'section_cache_directory':str(cache_dir),'diagnosis':'CadQuery w.positions() invokes GCPnts_AbscissaPoint on composite wires and can fail inversion; edge parameter Value evaluation avoids inversion without dropping edges.'}
(O/'sampling_diagnostics.json').write_text(json.dumps(diags,indent=2))
np.savez_compressed(O/'envelope_loft.npz',vertices_aircraft_mm=v,segment_is_unregistered_gap=np.array([any(x0<g1 and x1>g0 for g0,g1 in gaps) for x0,x1 in zip(grid[:-1],grid[1:])]))
assert R['sources_unchanged']and all(R['checks'].values())
R['hatches']={'count':4,'placement_receipt':str(HATCH/'placement.json'),'pose':'feature-verified native identity; nominal clearance retained','rear_interface_limit':'FUS4 mesh curved lip nominal fit checked; full rear tongue seating/penetration not certified'}
R['baseline_envelope_area_m2']=baseline_results['wetted_area_envelope_m2']
R['hatch_inclusive_minus_baseline_envelope_area_m2']=R['wetted_area_envelope_m2']-R['baseline_envelope_area_m2']
(O/'results.json').write_text(json.dumps(R,indent=2));print(json.dumps({k:R[k]for k in ['datum','wetted_area_envelope_m2','checks','convergence_last_axial_relative_change','convergence_last_angular_relative_change']},indent=2))

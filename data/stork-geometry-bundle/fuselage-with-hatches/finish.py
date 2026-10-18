"""Task-local raw-curve, open skin-arc, nonconvex diagnostics and verification.
No joining across open hatch seams, material islands or the unregistered nose gap.
"""
from pathlib import Path
import json,csv,hashlib,pickle,sys,shutil
import numpy as np
O=Path(__file__).resolve().parent
namespace={'__file__':str(O/'extract.py'),'__name__':'extraction_definitions'}
exec((O/'extract.py').read_text().split('# Regular native-datum')[0],namespace)
globals().update({k:v for k,v in namespace.items() if not k.startswith('__')})
from shapely.ops import unary_union
from shapely.geometry import Polygon,MultiPolygon
from shapely.validation import explain_validity
from OCP.BRepTools import BRepTools
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
xs=[float(r['aircraft_x_mm']) for r in csv.DictReader((O/'cross_sections_50mm.csv').open())]
assert len(xs)>20
patch_shape=cq.importers.importStep(str(HATCH/'external_skin_patches.step')).val()
assert len(patch_shape.Faces())==10
raw=[]; all_edges=[]; comparison=[]; nonconvex=[]; skin=[]
for x in sorted(set(xs+[-80.])):
 r=section(x);xx=r['evaluated_x']; curves=[];exterior_arcs=[]
 for p in parts:
  if not p['bounds'][0]+1e-5<xx<p['bounds'][1]-1e-5:continue
  s=p['shape']
  if isinstance(s,trimesh.Trimesh):
   cut=s.section(plane_origin=[0,0,xx],plane_normal=[0,0,1])
   if cut is not None:
    for i,entity in enumerate(cut.entities):
     q=np.array(entity.discrete(cut.vertices))
     curves.append({'source':p['name'],'edge_index':i,'method':'actual source triangle-plane polyline','points_aircraft_xyz_mm':q[:,[2,0,1]].tolist(),'closed':bool(np.linalg.norm(q[0]-q[-1])<1e-5)})
  else:
   op=BRepAlgoAPI_Section(s.wrapped,gp_Pln(gp_Pnt(0,0,xx),gp_Dir(0,0,1)),False);op.Build();assert op.IsDone()
   for i,e in enumerate(cq.Shape.cast(op.Shape()).Edges()):
    q,d=sample_edge(e);all_edges.append(e)
    curves.append({'source':p['name'],'edge_index':i,'method':'actual BRep-plane edge; native-parameter samples','points_aircraft_xyz_mm':q[:,[2,0,1]].tolist(),'exact_edge_length_mm':float(e.Length()),'sampling':d,'closed':bool(np.linalg.norm(q[0]-q[-1])<1e-5)})
 op=BRepAlgoAPI_Section(patch_shape.wrapped,gp_Pln(gp_Pnt(0,0,xx),gp_Dir(0,0,1)),False);op.Build();assert op.IsDone()
 for i,e in enumerate(cq.Shape.cast(op.Shape()).Edges()):
  q,d=sample_edge(e);exterior_arcs.append({'patch_edge_index':i,'points_aircraft_xyz_mm':q[:,[2,0,1]].tolist(),'exact_length_mm':float(e.Length())})
 skin.append({'aircraft_x_mm':x,'observed_original_main_hatch_skin_arcs':exterior_arcs,'closure_added':False})
 raw.append({'aircraft_x_mm':x,'evaluated_aircraft_x_mm':xx,'curves':curves})
 # Closed material section union only. Nested loops define cavities by even/odd
 # containment. Open curves and invalid polygons stay in raw data, not repaired.
 material=[];excluded=[]
 groups={}
 for w,m in zip(r['wires'],r['raw']):
  p=Polygon(w)
  if not p.is_valid or p.area<=1e-10:
   excluded.append({'source':m['source'],'reason':'invalid/zero-area physical loop; no repair','validity_diagnosis':explain_validity(p),'max_source_wire_join_gap_mm':m.get('max_join_gap_mm'),'allowed_source_wire_join_gap_mm':m.get('allowed_join_gap_mm')});continue
  groups.setdefault(m['source'],[]).append(p)
 for name,polys in groups.items():
  depths=[sum(other.contains(p) for other in polys if other is not p) for p in polys]
  for i,p in enumerate(polys):
   if depths[i]%2==0:
    holes=[q for j,q in enumerate(polys) if depths[j]==depths[i]+1 and p.contains(q)]
    material.append(p.difference(unary_union(holes)) if holes else p)
 u=unary_union(material)
 islands=list(u.geoms) if hasattr(u,'geoms') else [u]
 contours=[{'outer_yz_mm':np.asarray(p.exterior.coords).tolist(),'cavity_loops_yz_mm':[np.asarray(i.coords).tolist() for i in p.interiors]} for p in islands if p.geom_type=='Polygon']
 nonconvex.append({'aircraft_x_mm':x,'status':'PARTIAL_INVALID_SOURCE_LOOPS_EXCLUDED' if excluded else 'ALL_CLOSED_LOOPS_INCLUDED','raw_closed_loop_count':len(r['wires']),'excluded_loop_count':len(excluded),'continuous_aerodynamic_outer_contour_reconstructed':False,'material_area_mm2':float(u.area),'all_material_boundary_length_mm':float(u.length),'disconnected_material_island_count':len(contours),'is_valid':bool(u.is_valid),'contours':contours,'excluded_invalid_loops':excluded,'meaning':'Nonconvex physical material section union, cavities retained. Not continuous aerodynamic outer skin, not wetted area. No seam bridging or closure.'})
 bp=baseline_cache/f'{round(x,8):.8f}.pickle'
 if bp.exists():
  with bp.open('rb') as f:b=pickle.load(f)
 else:
  # regression-only x=-80 is not necessarily on baseline cached grid
  old=parts[:];parts[:]=[p for p in parts if not p['name'].startswith('HATCH:')]
  namespace['cache'].pop(round(x,8),None)
  old_dir=namespace['cache_dir'];namespace['cache_dir']=O/'baseline_probe_cache';namespace['cache_dir'].mkdir(exist_ok=True)
  b=section(x)
  parts[:]=old;namespace['cache_dir']=old_dir;namespace['cache'].pop(round(x,8),None)
 comparison.append({'aircraft_x_mm':x,'baseline_width_mm':b['width'],'with_hatches_width_mm':r['width'],'delta_width_mm':r['width']-b['width'],'baseline_height_mm':b['height'],'with_hatches_height_mm':r['height'],'delta_height_mm':r['height']-b['height'],'baseline_top_mm':float(b['points'][:,1].max()),'with_hatches_top_mm':float(r['points'][:,1].max()),'delta_top_mm':float(r['points'][:,1].max()-b['points'][:,1].max()),'baseline_convex_envelope_area_mm2':b['area'],'with_hatches_convex_envelope_area_mm2':r['area'],'delta_convex_envelope_area_mm2':r['area']-b['area'],'baseline_convex_envelope_perimeter_mm':b['perimeter'],'with_hatches_convex_envelope_perimeter_mm':r['perimeter']})
for filename,data in [('raw_section_curves.json',raw),('original_hatch_skin_arcs.json',skin),('nonconvex_material_sections.json',nonconvex),('baseline_section_comparison.json',comparison)]:
 (O/filename).write_text(json.dumps(data,indent=2))
with (O/'baseline_section_comparison.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=comparison[0]);w.writeheader();w.writerows(comparison)
cq.exporters.export(cq.Compound.makeCompound(all_edges),str(O/'raw_brep_section_edges.step'))
shutil.copyfile(HATCH/'installed_hatches.step',O/'installed_hatches.step')
shutil.copyfile(HATCH/'external_skin_patches.step',O/'external_skin_patches.step')
fig,axes=plt.subplots(4,5,figsize=(18,14))
for ax,x in zip(axes.flat,np.arange(-300,651,50)):
 rr=min(raw,key=lambda z:abs(z['aircraft_x_mm']-x)); x=rr['aircraft_x_mm']; r=section(x)
 for c in rr['curves']:
  q=np.array(c['points_aircraft_xyz_mm']);ax.plot(q[:,1],q[:,2],color='tab:blue' if c['source'].startswith('HATCH:') else '.65',lw=.7)
 q=np.vstack([r['poly'],r['poly'][0]]);ax.plot(q[:,0],q[:,1],'r--',lw=.9)
 bp=baseline_cache/f'{round(x,8):.8f}.pickle'
 if bp.exists():
  with bp.open('rb') as f:b=pickle.load(f)
  q=np.vstack([b['poly'],b['poly'][0]]);ax.plot(q[:,0],q[:,1],color='green',ls=':',lw=.8)
 ax.set_title(f'x={x:.3f} mm');ax.set_aspect('equal');ax.grid(alpha=.2)
fig.suptitle('Real section curves: hatch blue / fuselage grey; convex approximations: inclusive red / baseline green')
fig.tight_layout();fig.savefig(O/'hatch_comparison_diagnostics.png',dpi=150);plt.close(fig)
fig,axes=plt.subplots(2,3,figsize=(16,9))
for ax,x in zip(axes.flat,[-150,-100,-80,0,100,250]):
 n=min(nonconvex,key=lambda z:abs(z['aircraft_x_mm']-x));a=min(skin,key=lambda z:abs(z['aircraft_x_mm']-n['aircraft_x_mm']))
 rr=min(raw,key=lambda z:abs(z['aircraft_x_mm']-n['aircraft_x_mm']))
 for curve in rr['curves']:
  q=np.array(curve['points_aircraft_xyz_mm']);ax.plot(q[:,1],q[:,2],color='.8',ls=':',lw=.7)
 for c in n['contours']:
  q=np.array(c['outer_yz_mm']);ax.plot(*q.T,color='.5',lw=.7)
  for hole in c['cavity_loops_yz_mm']:
   ax.plot(*np.array(hole).T,color='.75',lw=.5)
 for c in a['observed_original_main_hatch_skin_arcs']:
  q=np.array(c['points_aircraft_xyz_mm']);ax.plot(q[:,1],q[:,2],color='tab:blue',lw=2)
 ax.set_title(f"x={n['aircraft_x_mm']:.3f}; valid-union islands={n['disconnected_material_island_count']}; excluded loops={n['excluded_loop_count']}");ax.axis('equal');ax.grid(alpha=.2)
fig.suptitle('Nonconvex attempt: valid union grey / all raw curves dotted / untouched hatch skin arcs blue. No seam closure.')
fig.tight_layout();fig.savefig(O/'nonconvex_diagnostics.png',dpi=150);plt.close(fig)
print('Raw stations',len(raw),'BRep edges',len(all_edges),'comparison rows',len(comparison),'nonconvex',len(nonconvex),flush=True)

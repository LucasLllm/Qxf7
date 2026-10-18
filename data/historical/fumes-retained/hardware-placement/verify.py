"""Independent process: reimport serialized metre OBJ and native approximation STEP.
Exact arithmetic pertains to dyadic OBJ coordinate triangles, not physical hardware or OCC CAD tolerances.
"""
from pathlib import Path
import sys,json,hashlib,time
import numpy as np,trimesh,cadquery as cq
O=Path(__file__).resolve().parent;R=O.parents[1]
sys.path.insert(0,str(R/'cfd-exterior-v1/surface-qualification'))
from exact_screen import Screen,regressions
from OCP.BRepBndLib import BRepBndLib
from OCP.Bnd import Bnd_Box
D=json.loads((O/'RESULTS.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def objwrite(p,m):
 with p.open('w') as f:
  f.write('# STANDARD STORK INSTALLED HARDWARE ONLY / CFD APPROXIMATE / METRES\n')
  for v in m.vertices:f.write('v '+' '.join(format(float(x),'.17g') for x in v)+'\n')
  for t in m.faces:f.write('f '+' '.join(str(int(x)+1) for x in t)+'\n')
def topo(m):
 v,inv=np.unique(m.vertices,axis=0,return_inverse=True);f=inv[m.faces];w=trimesh.Trimesh(v,f,process=False)
 ed=np.vstack([f[:,[0,1]],f[:,[1,2]],f[:,[2,0]]]);_,counts=np.unique(np.sort(ed,axis=1),axis=0,return_counts=True)
 # Vertex links each form one simple connected cycle, excluding pinched manifold vertices.
 links=[[] for _ in v]
 for a,b,c in f:links[a].append((b,c));links[b].append((c,a));links[c].append((a,b))
 badlinks=[]
 for i,es in enumerate(links):
  adj={}
  for a,b in es:adj.setdefault(int(a),set()).add(int(b));adj.setdefault(int(b),set()).add(int(a))
  seen=set();todo=[next(iter(adj))]
  while todo:
   a=todo.pop()
   if a in seen:continue
   seen.add(a);todo+=list(adj[a]-seen)
  if any(len(x)!=2 for x in adj.values()) or len(seen)!=len(adj):badlinks.append(i)
 assert np.all(counts==2) and w.is_watertight and w.is_winding_consistent and not badlinks and w.volume>0
 assert np.all(w.area_faces>0)
 return w,{'vertices':len(v),'faces':len(f),'edges':len(counts),'edge_incidence_two':bool(np.all(counts==2)),'winding_consistent':bool(w.is_winding_consistent),'bad_vertex_link_ids':badlinks,'euler_number':int(w.euler_number),'surface_shell_count':len(w.split(only_watertight=False)),'volume_m3':float(w.volume),'area_m2':float(w.area),'zero_area_faces':0}
def exact(m):
 s=Screen(m);res=s.run(limit=500000)
 # Independently enumerate inclusive-AABB overlap count via vectorized brute force, not rtree.
 count=0
 for i in range(len(s.f)-1):count+=int(np.count_nonzero(np.all(s.lo[i]<=s.hi[i+1:],axis=1)&np.all(s.hi[i]>=s.lo[i+1:],axis=1)))
 assert count==res['aabb_candidate_pairs'];res['independent_bruteforce_candidate_count']=count
 res['passes']=not res['forbidden_pairs'];assert res['passes'],res['forbidden_pairs'][:15]
 return res
assert regressions();records=[];meshes={};native={}
for r in D['components']:
 assert sha(r['obj'])==r['obj_sha256'] and sha(r['step'])==r['step_sha256']
 m=trimesh.load_mesh(r['obj'],process=False,maintain_order=True);m,t=topo(m);s=cq.importers.importStep(r['step']).val();assert s.isValid() and len(s.Solids())==1
 b=Bnd_Box();BRepBndLib.AddOptimal_s(s.wrapped,b,False,False);bounds=np.array(b.Get()).reshape(2,3)*.001
 bd=float(np.max(np.abs(m.bounds-bounds)));vd=abs(m.volume*1e9-s.Volume())/s.Volume();assert bd<.00008 and vd<.005,(r['name'],bd,vd)
 e=exact(m);records.append({'name':r['name'],'obj_sha256':sha(r['obj']),'step_sha256':sha(r['step']),'topology':t,'exact_triangle_intersections':e,'step_valid':True,'step_solid_count':1,'cad_mesh_bounds_max_delta_m':bd,'cad_mesh_relative_volume_delta':vd})
 meshes[r['name']]=m;native[r['name']]=s;print(r['name'],'exact pairs',e['aabb_candidate_pairs'],'forbidden',len(e['forbidden_pairs']),'Euler',t['euler_number'],flush=True)
base_names=D['baseline_installed_names'];base=trimesh.util.concatenate([meshes[n] for n in base_names]);p=O/'Stork-standard-installed-motors-booms-CFD-APPROXIMATE-m.obj';objwrite(p,base)
ps=O/'Stork-standard-installed-motors-booms-CFD-APPROXIMATE.step';cq.exporters.export(cq.Compound.makeCompound([native[n] for n in base_names]),str(ps))
b=trimesh.load_mesh(p,process=False,maintain_order=True);b,t=topo(b);ex=exact(b);assert t['surface_shell_count']==7
combined={'obj':str(p),'obj_sha256':sha(p),'obj_units':'m','step':str(ps),'step_sha256':sha(ps),'step_units':'mm','installed_names':base_names,'topology':t,'exact_triangle_intersections':ex,'scope':'7 hardware bodies ONLY; no parent airframe or props'}
ss=cq.importers.importStep(str(ps)).val();assert ss.isValid() and len(ss.Solids())==7;combined['step_valid']=True;combined['step_solid_count']=7
# Independent all 21 BRep pairs after serialized STEP roundtrip.
pairs=[]
for i,a in enumerate(base_names):
 for bname in base_names[i+1:]:
  c=native[a].intersect(native[bname]);pairs.append({'a':a,'b':bname,'common_volume_mm3':c.Volume(),'common_faces':len(c.Faces())})
assert all(abs(x['common_volume_mm3'])<1e-7 for x in pairs)
baseline=json.loads((O/'INPUT_BASELINE.json').read_text());preserved=all(sha(p)==h for p,h in baseline.items());assert preserved
receipt={'status':'PASS_COMPONENTS_AND_HARDWARE_BASELINE_ONLY','regression_controls_pass':True,'exact_predicate_source':str(R/'cfd-exterior-v1/surface-qualification/exact_screen.py'),'exact_predicate_source_sha256':sha(R/'cfd-exterior-v1/surface-qualification/exact_screen.py'),'components':records,'installed_baseline':combined,'independent_CAD_baseline_pairs':pairs,'source_preserved':preserved,'limits':'Exact triangle predicates bind serialized float64 metre OBJ; shared simplex allowed. Native CAD Boolean checks use OCC tolerance. No complete printed-airframe contact or fluid/solver release.'}
(O/'VERIFICATION.json').write_text(json.dumps(receipt,indent=2));D['status']=receipt['status'];D['installed_baseline']=combined;(O/'RESULTS.json').write_text(json.dumps(D,indent=2));print('PASS',len(records),'component pairs; baseline7 shells; exact global candidates',ex['aabb_candidate_pairs'],flush=True)

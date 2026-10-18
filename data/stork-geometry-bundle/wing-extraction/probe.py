from pathlib import Path
import json,numpy as np,cadquery as cq,trimesh
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.gp import gp_Pln,gp_Pnt,gp_Dir
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
D=Path(__file__).resolve().parent;P=D.parent
J=json.loads((P/'wing_assembly.json').read_text()); C={c['component']:c for c in J['components']}; cache={}
def loops(name,y):
 c=C[name];T=np.array(c['native_to_assembly_native_4x4']);src=c['source'];out=[]
 if src['format']=='STEP':
  key=(src['path'],c['features'].get('physical_solid_1_based',1))
  if key not in cache:cache[key]=cq.importers.importStep(key[0]).solids().vals()[key[1]-1]
  op=BRepAlgoAPI_Section(cache[key].wrapped,gp_Pln(gp_Pnt(-y,0,0),gp_Dir(1,0,0)),False);op.Approximation(True);op.Build()
  edges=cq.Shape.cast(op.Shape()).Edges()
  for w in cq.Wire.combine(edges,tol=1e-5):
   pts=[]
   # sample ordered wire via positionAt gives arc length parameter
   n=max(200,int(w.Length()/.04));pts=np.array([w.positionAt(float(t)).toTuple() for t in np.linspace(0,1,n)])
   pts=pts@T[:3,:3].T+T[:3,3];out.append(pts[:,[2,1]])
 else:
  key=name
  if key not in cache:
   m=trimesh.load_mesh(src['path'],process=False);m.apply_transform(T);cache[key]=m
  s=cache[key].section(plane_origin=[y,0,0],plane_normal=[1,0,0]);out=[] if s is None else [l[:,[2,1]] for l in s.discrete]
 return out
if __name__=='__main__':
 fig,axs=plt.subplots(5,2,figsize=(16,17))
 for ax,y in zip(axs.flat,[92.05,260.1,318.05,440,450,500,600,729,730.05,800]):
  for name,c in C.items():
   if c['bounds_native_mm'][0][0]<y<c['bounds_native_mm'][1][0]:
    ls=loops(name,y);print(y,name,[(len(l),np.linalg.norm(l[0]-l[-1]),l.min(0).tolist(),l.max(0).tolist()) for l in ls],flush=True)
    for l in ls:ax.plot(l[:,0],l[:,1],label=name)
  ax.set_title(str(y));ax.axis('equal');ax.grid();ax.legend(fontsize=6)
 fig.tight_layout();fig.savefig(D/'probe.png',dpi=130)

from pathlib import Path
import json,numpy as np,cadquery as cq,trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
D=Path(__file__).resolve().parent;B=D.parent
p=json.loads((B/'tail-feature-work/placements.json').read_text());raw=json.loads((B/'tail-feature-work/raw_features.json').read_text())
n=np.array(raw['step']['FUS 6 VTOL MODIFIER.STEP'][0]['faces'][44]['normal'])[[2,0,1]]
a=np.array([1.,0,0]);a-=n*np.dot(a,n);a/=np.linalg.norm(a);u=np.cross(a,n)
root=np.array(raw['step']['FUS 6 VTOL MODIFIER.STEP'][0]['faces'][44]['plane_point'])[[2,0,1]];s0=root@n
print('basis',n,a,u,'s0',s0)
meshes=[]
for i in range(1,4):
 name=f'V TAIL {i} R.STL';m=trimesh.load(p['source_hashes'][name]['path'],force='mesh');m.vertices+=np.array([0,-3.703521516,0]) if i==1 else np.zeros(3);m.vertices=m.vertices[:,[2,0,1]];meshes.append(m)
sol=cq.importers.importStep(p['source_hashes']['RUDDER L.STEP']['path']).solids().vals()
assert len(sol)==2
for b in sol:
 v,f=b.tessellate(.015,.08);v=np.array([x.toTuple() for x in v]);v[:,0]*=-1;v=v[:,[2,0,1]];meshes.append(trimesh.Trimesh(vertices=v,faces=f,process=True))
for i,m in enumerate(meshes):
 m.export(D/f'component_{i}.ply');v=m.vertices;print('component',i,'s',np.min(v@n)-s0,np.max(v@n)-s0,'aft',np.min(v@a),np.max(v@a),'up',np.min(v@u),np.max(v@u))
fig,axs=plt.subplots(2,1,figsize=(12,10))
for i,m in enumerate(meshes):
 v=m.vertices;axs[0].scatter(v@a,v@n-s0,s=.1,label=str(i));axs[1].scatter(v@a,v@u,s=.1,label=str(i))
for ax in axs:ax.legend();ax.set_aspect('equal');ax.grid()
fig.savefig(D/'geometry_inspection.png',dpi=180)
for s in [0.1,1,10,50,100,150,200,230,250,260]:
 print('SECTION',s)
 for i,m in enumerate(meshes):
  q=m.section(plane_origin=n*(s0+s),plane_normal=n)
  if q is not None:
   loops=q.discrete;print(i,[(len(l),np.round([min(l@a),max(l@a),min(l@u),max(l@u)],4).tolist()) for l in loops])
(D/'basis.json').write_text(json.dumps({'span':n.tolist(),'aft':a.tolist(),'up':u.tolist(),'s0':s0},indent=2))

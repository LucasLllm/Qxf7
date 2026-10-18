from pathlib import Path
import csv,json,hashlib
import numpy as np
import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface
import trimesh
D=Path(__file__).resolve().parent
rows=list(csv.DictReader((D.parent/'source-format-audit/cad_inventory.csv').open()));by={r['filename']:r for r in rows}
result={'step':{},'stl':{}}
for name,inds in [('WING 1.1 L VTOL MODIFIER.STEP',[2]),('WING 1.2 L VTOL MODIFIER.STEP',[1]),('AILERON L.STEP',[1,2]),('WINGTIP L.STEP',[1]),('FUS3.STEP',[1]),('FUS ROOT L.STEP',[1]),('WING ROOT L.STEP',[1])]:
 r=by[name];assert hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()==r['sha256']
 ss=cq.importers.importStep(r['path']).solids().vals();fs=[]
 for idx in inds:
  for n,f in enumerate(ss[idx-1].Faces(),1):
   a=BRepAdaptor_Surface(f.wrapped);bb=f.BoundingBox();record={'solid':idx,'face':n,'type':f.geomType(),'bounds':[[bb.xmin,bb.ymin,bb.zmin],[bb.xmax,bb.ymax,bb.zmax]]}
   if f.geomType()=='CYLINDER':
    c=a.Cylinder();record.update(radius=c.Radius(),axis=list(c.Axis().Direction().Coord()),origin=list(c.Location().Coord()));fs.append(record)
   elif f.geomType()=='PLANE':
    p=a.Plane();record.update(normal=list(p.Axis().Direction().Coord()),origin=list(p.Location().Coord()));
    if abs(p.Axis().Direction().X())>.99:fs.append(record)
 result['step'][name]=fs
 print('STEP',name,json.dumps(fs),flush=True)
for name,xx in [('WING 1.1 R VTOL.STL',100),('WING 1.2 R VTOL.STL',280),('WING 2 R.STL',400),('WING 3 R.STL',600),('WINGTIP 3 R.STL',740),('AIILERON 1 R.STL',500),('AILERON 2 R.STL',650)]:
 r=by[name];m=trimesh.load_mesh(r['path'],process=False);sec=m.section(plane_origin=[xx,0,0],plane_normal=[1,0,0]);ls=[]
 if sec is not None:
  for loop in sec.discrete:
   pts=loop[:,1:];A=np.column_stack([2*pts[:,0],2*pts[:,1],np.ones(len(pts))]);v=np.linalg.lstsq(A,np.sum(pts*pts,axis=1),rcond=None)[0];rad=np.sqrt(max(0,v[2]+v[0]**2+v[1]**2));err=np.sqrt(np.mean((np.linalg.norm(pts-v[:2],axis=1)-rad)**2));ls.append({'points':len(pts),'bounds_yz':[pts.min(axis=0).tolist(),pts.max(axis=0).tolist()],'circle_yz':v[:2].tolist(),'radius':rad,'circle_rms_mm':err,'closed':bool(np.linalg.norm(loop[0]-loop[-1])<.001)})
 result['stl'][name]={'station_native_x':xx,'loops':ls}
 print('STL',name,json.dumps(ls),flush=True)
(D/'wing_feature_inspection.json').write_text(json.dumps(result,indent=2)+'\n')

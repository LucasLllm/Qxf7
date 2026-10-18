from pathlib import Path
import json,csv,hashlib
import cadquery as cq
from OCP.BRepAdaptor import BRepAdaptor_Surface
ROOT=Path('/Users/lucasliu/.hermes/profiles/fumes')
OUT=ROOT/'notes/stork-development/stork-aero-geometry/hatch-feature-work'
INV=ROOT/'notes/stork-development/source-format-audit/cad_inventory.csv'
def bounds(s):
 b=s.BoundingBox();return [[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]]
def xyz(p):return [p.X(),p.Y(),p.Z()]
def features(s):
 out=[]
 for i,f in enumerate(s.Faces(),1):
  a=BRepAdaptor_Surface(f.wrapped); typ=f.geomType();r={'face':i,'type':typ,'area':f.Area(),'center':f.Center().toTuple(),'bounds':bounds(f),'orientation':str(f.wrapped.Orientation())}
  if typ=='CYLINDER':
   c=a.Cylinder();r.update(location=xyz(c.Location()),axis=xyz(c.Axis().Direction()),radius=c.Radius())
  elif typ=='PLANE':
   p=a.Plane();r.update(location=xyz(p.Location()),normal=xyz(p.Axis().Direction()))
  out.append(r)
 return out
if __name__=='__main__':
 rows=list(csv.DictReader(INV.open())); data={}
 for name in ['HATCH FRONT.STEP','HATCH MIDDLE.STEP','FUS 1 VTOL.STEP','FUS 2 VTOL MODIFIER.STEP','FUS3.STEP']:
  r=next(r for r in rows if r['filename']==name);p=Path(r['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'];ss=cq.importers.importStep(str(p)).solids().vals()
  data[name]={'source':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'solids':[{'body':i,'bounds':bounds(s),'volume':s.Volume(),'valid':s.isValid(),'features':features(s)} for i,s in enumerate(ss,1)]}
 (OUT/'features.json').write_text(json.dumps(data,separators=(',',':')))
 for name,d in data.items():
  print('\n',name)
  for s in d['solids']:
   print('BODY',s['body'],s['bounds'])
   for f in s['features']:
    if f['type']=='CYLINDER': print(f['face'],'cyl',round(f['radius'],4),[round(v,4) for v in f['location']],[round(v,4) for v in f['axis']], 'center', [round(v,4) for v in f['center']])

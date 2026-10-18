from investigate import *
import numpy as np
D=json.loads((OUT/'features.json').read_text())
for n in ['HATCH FRONT.STEP','HATCH MIDDLE.STEP']:
 ss=cq.importers.importStep(D[n]['source']).solids().vals()
 for k,s in enumerate(ss,1):
  print(n,k)
  for i,f in enumerate(s.Faces(),1):
   if f.geomType()=='BSPLINE' and f.Area()>500:
    print(i,'bounds',np.round(bounds(f),3).tolist(),'normal',f.normalAt().toTuple())
# Direct BRep intersection and face distances
for h,k,b in [('HATCH FRONT.STEP',1,'FUS 1 VTOL.STEP'),('HATCH FRONT.STEP',2,'FUS 2 VTOL MODIFIER.STEP'),('HATCH MIDDLE.STEP',1,'FUS3.STEP'),('HATCH MIDDLE.STEP',2,'FUS3.STEP')]:
 a=cq.importers.importStep(D[h]['source']).solids().vals()[k-1];s=cq.importers.importStep(D[b]['source']).solids().vals()[0]
 print('pair',h,k,b,'distance',a.distance(s),'overlap',a.intersect(s).Volume())

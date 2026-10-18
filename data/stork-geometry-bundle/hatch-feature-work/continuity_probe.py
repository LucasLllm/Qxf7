from investigate import *
from OCP.BRep import BRep_Tool
from OCP.GeomAPI import GeomAPI_ProjectPointOnSurf
from OCP.gp import gp_Pnt
import numpy as np
D=json.loads((OUT/'features.json').read_text())
for hn,hb,hf,bn,bf in [('HATCH MIDDLE.STEP',1,54,'FUS3.STEP',109),('HATCH MIDDLE.STEP',1,53,'FUS3.STEP',110),('HATCH FRONT.STEP',1,39,'FUS 1 VTOL.STEP',78),('HATCH FRONT.STEP',1,38,'FUS 1 VTOL.STEP',79)]:
 h=cq.importers.importStep(D[hn]['source']).solids().vals()[hb-1].Faces()[hf-1];f=cq.importers.importStep(D[bn]['source']).solids().vals()[0].Faces()[bf-1];surf=BRep_Tool.Surface_s(f.wrapped)
 vs,_=h.tessellate(2);pts=vs[::max(1,len(vs)//30)];ds=[]
 for p in pts:
  proj=GeomAPI_ProjectPointOnSurf(gp_Pnt(*p.toTuple()),surf)
  ds.append(proj.LowerDistance())
 print(hn,hb,hf,bn,bf,'n',len(ds),'dist',min(ds),max(ds),np.median(ds))

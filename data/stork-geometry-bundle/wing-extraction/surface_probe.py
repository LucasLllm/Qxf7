from probe import *
from OCP.BRep import BRep_Tool
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
for name in ['right_wing_1p1','right_wing_1p2','right_aileron_1','right_aileron_2','right_wing_root_plate','right_fuselage_root_plate']:
 c=C[name];s=cq.importers.importStep(c['source']['path']).solids().vals()[c['features'].get('physical_solid_1_based',1)-1]
 print(name)
 for i,f in enumerate(s.Faces()):
  if f.geomType()=='BSPLINE' and f.Area()>500:
   surf=BRep_Tool.Surface_s(f.wrapped);natural=cq.Face(BRepBuilderAPI_MakeFace(surf,1e-7).Face());b=natural.BoundingBox();print(i+1, f.Area(),surf.Bounds(),[b.xmin,b.xmax,b.ymin,b.ymax,b.zmin,b.zmax])
   y={'right_wing_1p1':260.156955,'right_wing_1p2':280,'right_aileron_1':500,'right_aileron_2':600,'right_wing_root_plate':93,'right_fuselage_root_plate':86}[name]
   op=BRepAlgoAPI_Section(natural.wrapped,gp_Pln(gp_Pnt(-y,0,0),gp_Dir(1,0,0)),False);op.Approximation(True);op.Build()
   for k,e in enumerate(cq.Shape.cast(op.Shape()).Edges()):
    p=np.array([e.positionAt(float(t)).toTuple() for t in np.linspace(0,1,1000)])[:,[2,1]];np.savetxt(D/f'natural_{name}_{i+1}_{k}.csv',p,delimiter=',');print('section',p.min(0),p.max(0))

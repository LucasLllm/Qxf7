from probe import *
from OCP.BRep import BRep_Tool
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from shapely.geometry import Polygon
c=C['right_wing_1p1'];s=cq.importers.importStep(c['source']['path']).solids().vals()[1];f=max([f for f in s.Faces() if f.geomType()=='BSPLINE'],key=lambda f:f.Area());natural=cq.Face(BRepBuilderAPI_MakeFace(BRep_Tool.Surface_s(f.wrapped),1e-7).Face())
def parent_loop(y):
 op=BRepAlgoAPI_Section(natural.wrapped,gp_Pln(gp_Pnt(-y,0,0),gp_Dir(1,0,0)),False);op.Approximation(True);op.Build();es=cq.Shape.cast(op.Shape()).Edges();pts=[]
 for e in es:
  n=max(500,int(e.Length()/.025));p=np.array([e.positionAt(float(t)).toTuple() for t in np.linspace(0,1,n)])[:,[2,1]];pts.append(p)
 p=max(pts,key=len);return np.vstack([p,p[0]])
def outer(ls):
 closed=[l for l in ls if np.linalg.norm(l[0]-l[-1])<.05];return max(closed,key=lambda l:Polygon(l).area)
def env(ps,x):
 u=np.full(len(x),-np.inf);l=np.full(len(x),np.inf)
 for p in ps:
  for a,b in zip(p[:-1],p[1:]):
   if abs(b[0]-a[0])<1e-12:continue
   m=(x>=min(a[0],b[0])-1e-9)&(x<=max(a[0],b[0])+1e-9);z=a[1]+(x[m]-a[0])*(b[1]-a[1])/(b[0]-a[0]);u[m]=np.maximum(u[m],z);l[m]=np.minimum(l[m],z)
 return u,l
if __name__=='__main__':
 for y in [92.05,250,260.156955,280,318.05,400,450,500,550,600,700,730.05,750,780,800,809,810.2]:
  par=parent_loop(y);x=np.linspace(par[:,0].min()+.1,par[:,0].max()-.1,2000);pu,pl=env([par],x);ps=[]
  for name,c in C.items():
   if 'plate' not in name and c['bounds_native_mm'][0][0]<y<c['bounds_native_mm'][1][0]:ps.append(outer(loops(name,y)))
  u,l=env(ps,x);m=np.isfinite(u)&np.isfinite(l);print(y,'rms upper lower',np.sqrt(np.mean((u[m]-pu[m])**2)),np.sqrt(np.mean((l[m]-pl[m])**2)),'max',np.max(np.abs(u[m]-pu[m])),np.max(np.abs(l[m]-pl[m])),'bounds parent',par.min(0),par.max(0),flush=True)

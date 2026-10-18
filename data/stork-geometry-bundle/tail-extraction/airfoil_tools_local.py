"""Shared traceable airfoil analysis. No invocation extracts aircraft stations before gate."""
import numpy as np
from shapely.geometry import Polygon

def outer_loops(mesh,origin,normal):
 s=mesh.section(plane_origin=origin,plane_normal=normal)
 return [] if s is None else list(s.discrete)

def envelope_from_loops(loops,axis_aft,axis_up,n=3001):
 """Select largest physical outer loop per component; envelope does not use internal loops."""
 selected=[]
 for group in loops:
  candidates=[]
  for xyz in group:
   p=np.column_stack((np.asarray(xyz)@axis_aft,np.asarray(xyz)@axis_up))
   if len(p)>3 and np.linalg.norm(p[0]-p[-1])<.02:
    poly=Polygon(p)
    if poly.area>.00001:candidates.append((poly.area,p))
  if candidates:selected.append(max(candidates,key=lambda v:v[0])[1])
 if not selected:raise ValueError('no closed exterior loop')
 xmin=min(p[:,0].min() for p in selected);xmax=max(p[:,0].max() for p in selected)
 x=xmin+(xmax-xmin)*(1-np.cos(np.linspace(0,np.pi,n)))/2
 upper=np.full(n,-np.inf);lower=np.full(n,np.inf)
 for p in selected:
  for a,b in zip(p[:-1],p[1:]):
   if abs(b[0]-a[0])<1e-10:continue
   lo=min(a[0],b[0]);hi=max(a[0],b[0]);mask=(x>=lo-1e-9)&(x<=hi+1e-9)
   yy=a[1]+(x[mask]-a[0])*(b[1]-a[1])/(b[0]-a[0]);upper[mask]=np.maximum(upper[mask],yy);lower[mask]=np.minimum(lower[mask],yy)
 finite=np.isfinite(upper)&np.isfinite(lower)
 if finite.sum()<100:raise ValueError('insufficient outer envelope')
 # Empty hinge gaps only: linear outer-skin bridge between adjacent existing samples.
 upper=np.interp(x,x[finite],upper[finite]);lower=np.interp(x,x[finite],lower[finite])
 return x,upper,lower,{'selected_components':len(selected),'missing_x_samples_bridged':int((~finite).sum()),'outer_loop_selection':'largest closed planar loop per participating physical component, by enclosed area; internal loops excluded'}

def normalize_envelope(x,upper,lower,hinge_x=None,hinge_bridge_halfwidth_mm=4.):
 x=np.asarray(x);u=np.array(upper,copy=True);l=np.array(lower,copy=True)
 bridge=None
 if hinge_x is not None and x[0]+hinge_bridge_halfwidth_mm<hinge_x<x[-1]-hinge_bridge_halfwidth_mm:
  lo=hinge_x-hinge_bridge_halfwidth_mm;hi=hinge_x+hinge_bridge_halfwidth_mm;mask=(x>lo)&(x<hi)
  for a in [u,l]:a[mask]=np.interp(x[mask],[lo,hi],np.interp([lo,hi],x,a))
  bridge={'hinge_center_aft_mm':float(hinge_x),'outer_skin_bridge_aft_limits_mm':[float(lo),float(hi)],'method':'replace hinge/pocket region with straight upper and lower outer-skin bridges; manufacturing gaps not aerodynamic surface'}
 te=np.array([x[-1],(u[-1]+l[-1])/2]);front=x<x[0]+.15*(x[-1]-x[0]);nose=np.vstack((np.column_stack([x[front],u[front]]),np.column_stack([x[front],l[front]])));le=nose[np.argmax(np.linalg.norm(nose-te,axis=1))];vec=te-le;c=np.linalg.norm(vec);ex=vec/c;ez=np.array([-ex[1],ex[0]])
 pu=np.column_stack([x,u])-le;pl=np.column_stack([x,l])-le
 xu=pu@ex/c;yu=pu@ez/c;xl=pl@ex/c;yl=pl@ez/c
 # The extreme aft coordinate defines a reproducible physical LE; small nose overhang
 # after rotation is preserved in raw loop diagnostic, but normalized envelopes interpolate x/c 0..1.
 def interp(xx,yy,grid):
  order=np.argsort(xx);xx=xx[order];yy=yy[order];ux,ii=np.unique(xx,return_index=True);return np.interp(grid,ux,yy[ii])
 grid=(1-np.cos(np.linspace(0,np.pi,2001)))/2
 un=interp(xu,yu,grid);ln=interp(xl,yl,grid);th=un-ln;cam=(un+ln)/2
 gu=(1-np.cos(np.linspace(0,np.pi,70)))/2;gl=(1-np.cos(np.linspace(0,np.pi,71)))/2
 dat=np.vstack((np.column_stack([gu[::-1],interp(xu,yu,gu)[::-1]]),np.column_stack([gl[1:],interp(xl,yl,gl)[1:]])))
 assert dat.shape==(140,2)
 it=int(np.argmax(th));ic=int(np.argmax(np.abs(cam)))
 out={'chord_mm':float(c),'leading_edge_aft_mm':float(le[0]),'leading_edge_up_mm':float(le[1]),'trailing_edge_aft_mm':float(te[0]),'trailing_edge_up_mm':float(te[1]),'incidence_LE_up_deg':float(-np.degrees(np.arctan2(vec[1],vec[0]))),'max_thickness_over_chord':float(th[it]),'max_thickness_x_over_chord':float(grid[it]),'max_camber_over_chord':float(cam[ic]),'max_camber_x_over_chord':float(grid[ic]),'TE_thickness_mm':float((un[-1]-ln[-1])*c),'TE_thickness_over_chord':float(un[-1]-ln[-1]),'normalization':'LE to TE-midpoint chord, x/c=0..1; positive up; upper TE->LE then lower LE->TE; 140 total cosine points (70 upper, 71 lower before shared-LE removal)','hinge_bridge':bridge}
 return out,dat,(grid,un,ln)

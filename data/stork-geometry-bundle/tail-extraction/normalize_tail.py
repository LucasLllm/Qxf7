"""Tail-specific normalization: retain genuine finite, slightly oblique TE caps.
The read-only shared helper's max-aft envelope collapses these caps to one corner.
This implementation works on verified exterior-loop vertices and documents projection.
"""
import numpy as np

def normalize_tail(x,upper,lower,groups,hinge_x=None,hinge_bridge_halfwidth_mm=5.):
 x=np.asarray(x);up=upper.copy();low=lower.copy();bridge=None
 if hinge_x is not None and x[0]+hinge_bridge_halfwidth_mm<hinge_x<x[-1]-hinge_bridge_halfwidth_mm:
  limits=[hinge_x-hinge_bridge_halfwidth_mm,hinge_x+hinge_bridge_halfwidth_mm]
  # If a linkage/end-slot creates disconnected exterior islands, extend closure
  # past both gap lips before sampling the skin. An aftmost corner of a lip is
  # not a legitimate upper/lower skin anchor (it collapses that envelope).
  intervals=sorted((float(q[:,0].min()),float(q[:,0].max())) for q in groups)
  covered=intervals[0][1];gaps=[]
  for start,end in intervals[1:]:
   if start>covered+.02 and covered>x[0]+.55*(x[-1]-x[0]):
    gaps.append([covered,start]);limits[0]=min(limits[0],covered-1.);limits[1]=max(limits[1],start+1.)
   covered=max(covered,end)
  mask=(x>limits[0])&(x<limits[1])
  for y in [up,low]:y[mask]=np.interp(x[mask],limits,np.interp(limits,x,y))
  bridge={'hinge_center_aft_mm':float(hinge_x),'outer_skin_bridge_aft_limits_mm':limits,'disconnected_exterior_gaps_mm':gaps,'method':'straight upper/lower skin bridges; hx +/- nominal halfwidth, expanded to 1mm past disconnected exterior gap lips; no manufactured pocket surfaces retained'}
 # Identify actual aft closing edge (possibly split by triangle tessellation).
 # An edge within .2 mm of global aftmost extent and predominantly section-up
 # belongs to the finite TE cap. If none exists, retain a sharp TE, not a guessed cap.
 cap=[]
 for q in groups:
  for A,B in zip(q[:-1],q[1:]):
   dv=B-A
   if min(A[0],B[0])>x[-1]-.2 and abs(dv[0])<.2*abs(dv[1]) and abs(dv[1])>1e-8:cap.extend([A,B])
 if cap:
  cap=np.asarray(cap);tu=cap[np.argmax(cap[:,1])];tl=cap[np.argmin(cap[:,1])]
 else:tu=np.array([x[-1],up[-1]]);tl=np.array([x[-1],low[-1]])
 te=(tu+tl)/2
 nose=np.vstack([q[q[:,0]<x[0]+.15*(x[-1]-x[0])] for q in groups]);le=nose[np.argmax(np.linalg.norm(nose-te,axis=1))]
 vec=te-le;c=np.linalg.norm(vec);ex=vec/c;ez=np.array([-ex[1],ex[0]])
 def curve(y,end):
  keep=x<end[0]-1e-8
  p=np.vstack((np.column_stack([x[keep],y[keep]]),end))
  xx=(p-le)@ex/c;yy=(p-le)@ez/c
  # Finite TE endpoints are projected along chord onto x/c=1. This preserves
  # their separation normal to chord without mistaking one corner for TE midpoint.
  xx[-1]=1.
  order=np.argsort(xx);xx=xx[order];yy=yy[order];ux,idx=np.unique(xx,return_index=True)
  return lambda grid:np.interp(grid,ux,yy[idx])
 fu=curve(up,tu);fl=curve(low,tl)
 grid=(1-np.cos(np.linspace(0,np.pi,2001)))/2;un=fu(grid);ln=fl(grid)
 # A common exact LE prevents tiny sampling gaps between the two Selig branches.
 un[0]=ln[0]=0.
 gu=(1-np.cos(np.linspace(0,np.pi,70)))/2;gl=(1-np.cos(np.linspace(0,np.pi,71)))/2
 yu=fu(gu);yl=fl(gl);yu[0]=yl[0]=0
 dat=np.vstack([np.c_[gu[::-1],yu[::-1]],np.c_[gl[1:],yl[1:]]]);assert dat.shape==(140,2)
 th=un-ln;cam=(un+ln)/2;it=int(np.argmax(th));ic=int(np.argmax(abs(cam)))
 m={'chord_mm':float(c),'leading_edge_aft_mm':float(le[0]),'leading_edge_up_mm':float(le[1]),'trailing_edge_aft_mm':float(te[0]),'trailing_edge_up_mm':float(te[1]),'incidence_LE_up_deg':float(-np.degrees(np.arctan2(vec[1],vec[0]))),'max_thickness_over_chord':float(th[it]),'max_thickness_x_over_chord':float(grid[it]),'max_camber_over_chord':float(cam[ic]),'max_camber_x_over_chord':float(grid[ic]),'TE_thickness_mm':float((tu-tl)@ez),'TE_thickness_over_chord':float((tu-tl)@ez/c),'TE_cap_length_mm':float(np.linalg.norm(tu-tl)),'TE_endpoints_section_mm':[tu.tolist(),tl.tolist()],'normalization':'raw outer-loop farthest nose from genuine TE-cap midpoint; LE->TE chord; physical TE endpoints projected parallel chord to x/c=1, preserving normal thickness; upper TE->LE then lower LE->TE, 70+71 cosine points minus shared LE = 140','hinge_bridge':bridge}
 return m,dat,(grid,un,ln)

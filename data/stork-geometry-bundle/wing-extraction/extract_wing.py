"""Reproducible wing extraction; all writes confined to this script's directory.
Run: research-venv/bin/python -B extract_wing.py
Original trimmed STEP used for diagnostics; its own natural BSpline support restores
machining cuts, never an external airfoil or fitted airfoil family.
"""
from compare import *
import hashlib,csv,sys,platform
from scipy.optimize import minimize_scalar
from shapely.geometry import LineString
from scipy.integrate import trapezoid
OUT=D; (OUT/'dat').mkdir(exist_ok=True);(OUT/'plots').mkdir(exist_ok=True);(OUT/'raw').mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
inputs=[P/'wing_assembly.json',P/'extraction_authorization.json',P/'reference-assembly/assembly_manifest.json',P/'inspect_wing_features.py',P.parent/'source-format-audit/cad_inventory.csv']+list({c['source']['path'] for c in C.values()})
pre={str(p):sha(p) for p in inputs}
for c in C.values():assert pre[c['source']['path']]==c['source']['sha256']
assert json.loads((P/'extraction_authorization.json').read_text())['status'].startswith('AUTHORIZED')
def hx(y):return 162.67953136229752+(-y+459.9065677731474)*.0029812966971660923/.9999810723120438
def hz(y):return -.003003173542296539+(-y+459.9065677731474)*(-.005382089525323084)/.9999810723120438
def groups(y,plate=None):
 ns=[plate] if plate else [n for n,c in C.items() if 'plate' not in n and c['bounds_native_mm'][0][0]+1e-6<y<c['bounds_native_mm'][1][0]-1e-6]
 gs=[];audit=[]
 for n in ns:
  ls=loops(n,y);p=outer(ls);a=Polygon(p).area
  # Reject every separate internal loop by containment, not only its area.
  poly=Polygon(p).buffer(.03);contained=[bool(poly.covers(Polygon(l).representative_point())) for l in ls if l is not p]
  assert all(contained),(n,y,'non-nested section loops')
  gs.append(p);audit.append({'component':n,'format':C[n]['source']['format'],'outer_area_mm2':a,'outer_points':len(p),'internal_loops_ignored':len(ls)-1,'all_other_loops_nested':all(contained)})
 return gs,audit

def normalize(p):
 # TE face is the straight closure of upper/lower skin at maximum aft.
 xmax=p[:,0].max();cand=p[p[:,0]>xmax-.04];te=np.array([xmax,.5*(cand[:,1].min()+cand[:,1].max())]);front=p[p[:,0]<p[:,0].min()+.1*np.ptp(p[:,0])];le=front[np.argmax(np.linalg.norm(front-te,axis=1))]
 for _ in range(4):
  ex=(te-le)/np.linalg.norm(te-le);le=front[np.argmin(front@ex)]
 c=np.linalg.norm(te-le);ex=(te-le)/c;ez=np.array([-ex[1],ex[0]]);q=np.column_stack(((p-le)@ex/c,(p-le)@ez/c))
 # Reparameterize finite TE on a perpendicular plane x/c=1; retain transverse endpoint offsets.
 k=np.argmax(p[:,0]);near=(p[:,0]>xmax-.04);q[near,0]=1
 g=(1-np.cos(np.linspace(0,np.pi,4001)))/2;u,l=env([q],g)
 finite=np.isfinite(u)&np.isfinite(l);assert finite.sum()>3990
 u=np.interp(g,g[finite],u[finite]);l=np.interp(g,g[finite],l[finite]);u[0]=l[0]=0
 gu=(1-np.cos(np.linspace(0,np.pi,70)))/2;gl=(1-np.cos(np.linspace(0,np.pi,71)))/2
 dat=np.vstack([np.column_stack([gu[::-1],np.interp(gu[::-1],g,u)]),np.column_stack([gl[1:],np.interp(gl[1:],g,l)])]);dat[69]=0
 t=u-l;cam=(u+l)/2;it=np.argmax(t);ic=np.argmax(np.abs(cam))
 meta={'chord_mm':float(c),'LE_aft_mm':float(le[0]),'LE_up_mm':float(le[1]),'TE_aft_mm':float(te[0]),'TE_up_mm':float(te[1]),'incidence_LE_up_deg':float(-np.degrees(np.arctan2(ex[1],ex[0]))),'max_t_c':float(t[it]),'max_t_x_c':float(g[it]),'max_camber_c':float(cam[ic]),'max_camber_x_c':float(g[ic]),'TE_thickness_mm':float(t[-1]*c),'TE_thickness_c':float(t[-1]),'quarterchord_aft_mm':float(le[0]+.25*(te[0]-le[0])),'quarterchord_up_mm':float(le[1]+.25*(te[1]-le[1]))}
 # Actual 140-point interpolation error, excluding declared TE reprojection band.
 du=np.interp(g,dat[:70,0][::-1],dat[:70,1][::-1]);dl=np.interp(g,np.r_[0,dat[70:,0]],np.r_[0,dat[70:,1]])
 rec=np.r_[du-u,dl-l]*c;poly=Polygon(dat);line=LineString(np.vstack([dat,dat[0]]))
 check={'points':len(dat),'finite':bool(np.isfinite(dat).all()),'LE_origin':bool(np.all(dat[69]==0)),'upper_TE_to_LE':bool(np.all(np.diff(dat[:70,0])<0)),'lower_LE_to_TE':bool(np.all(np.diff(dat[69:,0])>0)),'x_range':[float(dat[:,0].min()),float(dat[:,0].max())],'TE_x_one':bool(dat[0,0]==dat[-1,0]==1),'non_self_intersecting':bool(line.is_simple and poly.is_valid),'nonnegative_thickness':bool(t.min()>-1e-8),'reconstruction_140_vs_dense_max_mm':float(np.max(np.abs(rec))),'reconstruction_140_vs_dense_rms_mm':float(np.sqrt(np.mean(rec**2))),'TE_reprojection_max_aft_shift_mm':float(.04+abs(ex[1])*.6)}
 assert all(check[k] for k in ['finite','LE_origin','upper_TE_to_LE','lower_LE_to_TE','TE_x_one','non_self_intersecting','nonnegative_thickness'])
 return meta,dat,(g,u,l),check

def get_section(y,plate=None,save=False,tag=''):
 gs,audit=groups(y,plate);raw=np.vstack(gs)
 if plate:
  contour=gs[0];repair={'method':'original trimmed STEP exterior; nested holes ignored','replaced_sample_fraction':0.}
 elif y<=318:
  contour=parent_loop(y);repair={'method':'original physical-body outer BSpline supporting surface section, trims removed only to recover design skin across machining cuts; exact source surface, not a fitted profile','replaced_sample_fraction':None}
 else:
  xmin=min(p[:,0].min() for p in gs);xmax=max(p[:,0].max() for p in gs);x=np.linspace(xmin,xmax,5001);u,l=env(gs,x);missing=~(np.isfinite(u)&np.isfinite(l));replu=missing.copy();repll=missing.copy()
  if y<730:
   pp=parent_loop(y);pu,pl=env([pp],x);valid=np.isfinite(pu)&np.isfinite(pl)
   # Only inward manufacturing cutouts and known hinge zone; outside skins never fitted to loft.
   replu|=valid&(u<pu-.05);repll|=valid&(l>pl+.05)
   if 449.79<y<730:
    hinge=(x>hx(y)-4)&(x<hx(y)+5);replu|=hinge&valid;repll|=hinge&valid
   u[replu&valid]=pu[replu&valid];l[repll&valid]=pl[repll&valid]
  good=np.isfinite(u)&np.isfinite(l);u=np.interp(x,x[good],u[good]);l=np.interp(x,x[good],l[good]);contour=np.vstack([np.column_stack([x,u]),np.column_stack([x[::-1],l[::-1]]),[x[0],u[0]]])
  repair={'method':'original STL fixed-wing and original STEP movable outer skin; inward machining cuts and hinge arc replaced by original inboard STEP underlying loft only where y<730. No loft substitution on curved tip.','upper_replaced_fraction':float(replu.mean()),'lower_replaced_fraction':float(repll.mean()),'missing_samples':int(missing.sum()),'hinge_limits_aft_mm':[hx(y)-4,hx(y)+5] if 449.79<y<730 else None,'max_raw_inward_cut_mm':float(max(np.max(np.where(np.isfinite(u),0,0)),0))}
  if y<730:
   ru,rl=env(gs,x);m=np.isfinite(ru)&np.isfinite(rl)&np.isfinite(pu)&np.isfinite(pl);repair['max_raw_inward_cut_mm']=float(max(np.max(pu[m]-ru[m]),np.max(rl[m]-pl[m])))
 meta,dat,dense,check=normalize(contour);meta.update(station_y_mm=y,section_id=tag,source_audit=audit,skin_recovery=repair,section_class='local aircraft-y plane; curved-tip oblique diagnostic, NOT certified local normal airfoil' if y>735 else 'aircraft-y constant section')
 if save:
  np.savez_compressed(OUT/'raw'/f'{tag}.npz',contour_aft_up_mm=contour,**{f'physical_outer_{i}':p for i,p in enumerate(gs)},dense_x_c=dense[0],upper_y_c=dense[1],lower_y_c=dense[2])
  np.savetxt(OUT/'dat'/f'{tag}.dat',dat,fmt='%.10f',header=f'Stork {tag} y={y:.6f} mm; saved-pose/design-skin recovery',comments='')
  fig,ax=plt.subplots(2,1,figsize=(11,6));
  for p in gs:ax[0].plot(p[:,0],p[:,1],alpha=.5,lw=.8)
  ax[0].plot(contour[:,0],contour[:,1],'k--',lw=.9,label='recovered outer skin');ax[0].plot([meta['LE_aft_mm'],meta['TE_aft_mm']],[meta['LE_up_mm'],meta['TE_up_mm']],'r:',label='chord');ax[0].legend(fontsize=7);ax[0].axis('equal');ax[0].set(xlabel='Aircraft x / native Z (mm aft)',ylabel='Aircraft z / native Y (mm up)',title=f'{tag}, y={y:.5f} mm')
  ax[1].plot(dat[:,0],dat[:,1],'.-',ms=2);ax[1].axis('equal');ax[1].set(xlabel='x/c',ylabel='z/c',title=f'140 cosine points; chord {meta["chord_mm"]:.3f} mm; incidence {meta["incidence_LE_up_deg"]:.4f} deg')
  for a in ax:a.grid(alpha=.3)
  fig.tight_layout();fig.savefig(OUT/'plots'/f'{tag}.png',dpi=140);plt.close(fig)
 return meta,dat,dense,check

# Neutral investigation independently tests saved pose against the source uncut design loft.
neutral=[]
for y in [470,500,550,600,650,700,720]:
 name='right_aileron_1' if y<589.6 else 'right_aileron_2';p=outer(loops(name,y));pp=parent_loop(y);xx=np.linspace(hx(y)+8,p[:,0].max()-.5,180);u,l=env([p],xx);xp=np.linspace(pp[:,0].min()+.05,pp[:,0].max()-.05,4000);pu,pl=env([pp],xp);pivot=np.array([hx(y),hz(y)]);a=np.vstack([np.column_stack([xx,u]),np.column_stack([xx,l])]);upper=np.arange(len(a))<len(xx)
 def resid(deg):
  t=np.radians(deg);r=np.array([[np.cos(t),-np.sin(t)],[np.sin(t),np.cos(t)]]);q=(a-pivot)@r.T+pivot;target=np.where(upper,np.interp(q[:,0],xp,pu),np.interp(q[:,0],xp,pl));return q[:,1]-target
 opt=minimize_scalar(lambda t:np.mean(resid(t)**2),bounds=(-5,5),method='bounded',options={'xatol':1e-8});neutral.append({'station_y_mm':y,'best_correction_TE_up_deg':float(opt.x),'saved_pose_vs_design_rms_mm':float(np.sqrt(np.mean(resid(0)**2))),'best_fit_rms_mm':float(np.sqrt(opt.fun)),'saved_pose_vs_design_max_mm':float(np.max(np.abs(resid(0)))),'method':'2D section rotation about analytically intersected STEP hinge; aft skins 8mm behind hinge through TE-0.5mm; +/-5deg search; untrimmed original wing BSpline design loft target'})
(OUT/'neutral_investigation.json').write_text(json.dumps({'certified_neutral':False,'conclusion':'Geometric saved-pose/design-loft agreement quantified, not mechanical rigging or flight-neutral certification. Section-plane angle fit ignores <0.36deg hinge skew; no rotation applied to extraction.','samples':neutral},indent=2))

stations=[('fuselage_junction',88.02,'right_fuselage_root_plate'),('root_plate_in',89.98,'right_fuselage_root_plate'),('root_plate_out',90.02,'right_wing_root_plate'),('wing_root',92.02,None),('root_plate_end',91.98,'right_wing_root_plate'),('inner_clean',200,None),('joint_1p1_in',260.13695513675854,None),('joint_1p1_out',260.17695513675854,None),('joint_1p2_in',317.98,None),('joint_1p2_out',318.02,None),('aileron_start_in',449.78,None),('aileron_start_out',449.82,None),('servo_pocket',500,None),('joint_2_in',523.98,None),('joint_2_out',524.02,None),('aileron_joint_in',589.58,None),('aileron_joint_out',589.62,None),('outer_clean',650,None),('aileron_end_in',729.38,None),('aileron_end_out',729.42,None),('tip_root_in',729.98,None),('tip_root_out',730.02,None),('curved_tip_750',750,None),('curved_tip_780',780,None),('near_tip_800',800,None),('near_tip_809',809,None),('near_tip_810p25',810.25,None)]
results=[];checks={};profiles={}
for tag,y,plate in stations:
 print('SECTION',tag,y,flush=True);m,dat,dense,ch=get_section(y,plate,True,tag);results.append(m);checks[tag]=ch;profiles[tag]=dense
base=next(m for m in results if m['section_id']=='wing_root');bg,bu,bl=profiles['wing_root']
for m in results:
 g,u,l=profiles[m['section_id']];diff=np.r_[u-bu,l-bl];m['twist_LE_up_relative_root_deg']=m['incidence_LE_up_deg']-base['incidence_LE_up_deg'];m['shape_vs_root_rms_c']=float(np.sqrt(np.mean(diff**2)));m['shape_vs_root_max_c']=float(np.max(np.abs(diff)));m['shape_vs_root_rms_mm_at_local_chord']=m['shape_vs_root_rms_c']*m['chord_mm']
(OUT/'sections.json').write_text(json.dumps(results,indent=2));keys=[k for k,v in results[0].items() if isinstance(v,(str,int,float))]
with (OUT/'sections.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows([{k:m[k] for k in keys} for m in results])
# Panel rates use clean section endpoints; separate actual winglet curvature from flat-panel dihedral.
rates=[]
for label,a,b in [('inner',97.1,240),('inner_1p2',270,310),('panel2',330,440),('panel3',600,720),('tip_root',730.02,735),('curved_tip',750,800)]:
 ma=get_section(a)[0];mb=get_section(b)[0];dy=b-a;rates.append({'panel':label,'y_start_mm':a,'y_end_mm':b,'LE_sweep_aft_deg':float(np.degrees(np.arctan2(mb['LE_aft_mm']-ma['LE_aft_mm'],dy))),'quarterchord_sweep_aft_deg':float(np.degrees(np.arctan2(mb['quarterchord_aft_mm']-ma['quarterchord_aft_mm'],dy))),'LE_dihedral_deg':float(np.degrees(np.arctan2(mb['LE_up_mm']-ma['LE_up_mm'],dy))),'quarterchord_dihedral_deg':float(np.degrees(np.arctan2(mb['quarterchord_up_mm']-ma['quarterchord_up_mm'],dy))),'incidence_change_deg':mb['incidence_LE_up_deg']-ma['incidence_LE_up_deg']})
(OUT/'panel_rates.json').write_text(json.dumps(rates,indent=2))
# Projected planform integration: no airfoil reconstruction needed. Use section extreme x
# (all nested holes irrelevant). source BSpline for inboard, primary original STL elsewhere.
plan=[]
ys=np.unique(np.r_[np.arange(92.02,810.25,3),[260.136955,260.176955,317.98,318.02,449.78,449.82,523.98,524.02,589.58,589.62,729.38,729.42,729.98,730.02,810.25]])
for i,y in enumerate(ys):
 if y<=318:p=parent_loop(y);xmin=p[:,0].min();xmax=p[:,0].max();leup=p[p[:,0].argmin(),1];teup=.5*(p[0,1]+p[-2,1])
 else:
  ps,_=groups(y);xmin=min(p[:,0].min() for p in ps);xmax=max(p[:,0].max() for p in ps);lepoint=min([p[p[:,0].argmin()] for p in ps],key=lambda p:p[0]);leup=lepoint[1];tep=max(ps,key=lambda p:p[:,0].max());q=tep[tep[:,0]>xmax-.05];teup=.5*(q[:,1].min()+q[:,1].max())
 plan.append([float(y),float(xmin),float(xmax),float(leup),float(teup)])
 if i%40==0:print('PLANFORM',i,len(ys),flush=True)
p=np.array(plan);np.savetxt(OUT/'planform_samples.csv',p,delimiter=',',header='y_mm,LE_extreme_aft_mm,TE_extreme_aft_mm,LE_extreme_up_mm,TE_mid_up_mm',comments='')
def mac(a):
 y=a[:,0];c=a[:,2]-a[:,1];area=trapezoid(c,y);mac=trapezoid(c*c,y)/area;qc=trapezoid((a[:,1]+.25*c)*c,y)/area;zqc=trapezoid((.75*a[:,3]+.25*a[:,4])*c,y)/area
 return {'both_sides_projected_area_dm2':float(2*area/1e4),'projected_MAC_mm':float(mac),'MAC_LE_aft_mm':float(qc-.25*mac),'quarterchord_aft_mm':float(qc),'area_weighted_quarterchord_up_mm':float(zqc),'right_MAC_area_weighted_y_mm':float(trapezoid(y*c,y)/area),'integration':'trapezoidal aircraft-xy projection; x-extreme chord, not chord-line norm; curved tip included as projected planform only'}
gross=np.vstack([np.r_[0,p[0,1:]],np.r_[92.,p[0,1:]],p]);geometry={'datum':'Untranslated common STEP origin. Aircraft x=native Z aft, y=native X right after component transform, z=native Y up. Not root-LE origin. Angles LE-up positive = -atan2(TEup-LEup,TEaft-LEaft).','exposed_root_y_mm':92.,'right_outer_y_mm':810.2703247070312,'span_mm':1620.5406494140625,'exposed':mac(p),'gross_with_declared_centerline_continuation':mac(gross),'gross_convention':'Artificial rectangular continuation of y=92.02 root x-extreme chord to centerline; not hidden-wing evidence. Right wing mirrored to left, not independently measured left geometry. Root plates not additionally counted.','integration_end_missing_mm':810.2703247070312-810.25,'MAC_convergence_6mm_vs_3mm':{'exposed_6mm':mac(p[::2])},'true_tip_airfoil':None,'true_tip_reason':'Curved upturned STL winglet ends on an outer cap at y=810.2703; no finite conventional span-normal aerodynamic tip foil is certified. Near-tip constant-y sections are oblique diagnostics only.','physical_winglet_camber_incidence':None}
(OUT/'wing_geometry.json').write_text(json.dumps(geometry,indent=2))
post={str(p):sha(p) for p in inputs};assert pre==post
verification={'all_original_input_hashes_unchanged':pre==post,'inputs_sha256':pre,'sections':checks,'all_section_tests_passed':True,'python':sys.version,'platform':platform.platform(),'numpy':np.__version__,'cadquery':cq.__version__,'trimesh':trimesh.__version__,'notes':['Source reconstruction test is 140-point polyline versus recovered dense section; physical raw loops also retained in NPZ and plots. Differences due to explicit hole/hinge recovery are not hidden in interpolation tolerance.','STEP natural supporting wing surface extends to y=810 but outer physical STEP does not: beyond318 loft only repairs known manufacturing cuts/hinge and provides neutral target, never replaces measured outside skin wholesale.','140 coordinates: upper70 TE->LE, lower70 excluding shared LE; lower underlying grid71. Cosine clustering on each side. Finite TE perpendicular reprojection declared.']}
(OUT/'verification.json').write_text(json.dumps(verification,indent=2));print('COMPLETE',json.dumps(geometry),flush=True)

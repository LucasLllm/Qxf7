"""Original-source tail geometry. All writes constrained to this script's directory.
Run: /Users/lucasliu/.hermes/profiles/fumes/research-venv/bin/python -B extract_tail.py
No invented foil, no geometry rotation to force neutrality. Aircraft axes x aft,y right,z up.
"""
from pathlib import Path
import json,csv,hashlib
import numpy as np
import cadquery as cq
import trimesh
from shapely.geometry import Polygon
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from normalize_tail import normalize_tail
D=Path(__file__).resolve().parent;B=D.parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
placements=B/'tail-feature-work/placements.json';features=B/'tail-feature-work/raw_features.json'
p=json.loads(placements.read_text());raw=json.loads(features.read_text())
names=[f'V TAIL {i} R.STL' for i in range(1,4)]+['RUDDER L.STEP','FUS 6 VTOL MODIFIER.STEP']
receipt={name:dict(p['source_hashes'][name]) for name in names}
for name,r in receipt.items():
 r['before_sha256']=sha(r['path']);assert r['sha256']==r['before_sha256'],name
aux=[placements,features,B/'extraction_authorization.json',B/'airfoil_tools.py',D/'airfoil_tools_local.py',D/'normalize_tail.py',Path(__file__)]
auxreceipt={str(q):sha(q) for q in aux}
assert sha(B/'airfoil_tools.py')==sha(D/'airfoil_tools_local.py')
face=next(f for f in raw['step']['FUS 6 VTOL MODIFIER.STEP'][0]['faces'] if f['index']==44)
n=np.array(face['normal'])[[2,0,1]];n/=np.linalg.norm(n)
a=np.array([1.,0,0]);a-=n*np.dot(a,n);a/=np.linalg.norm(a);u=np.cross(a,n)
root_plane=np.array(face['plane_point'])[[2,0,1]];s0=float(root_plane@n)
meshes=[]
for i in range(1,4):
 m=trimesh.load(receipt[f'V TAIL {i} R.STL']['path'],force='mesh')
 if i==1:m.vertices+=np.array([0,-3.703521516,0])
 m.vertices=m.vertices[:,[2,0,1]];meshes.append(m)
solids=cq.importers.importStep(receipt['RUDDER L.STEP']['path']).solids().vals();assert len(solids)==2
for solid in solids:
 vertices,faces=solid.tessellate(.008,.05);v=np.array([x.toTuple() for x in vertices]);v[:,0]*=-1
 meshes.append(trimesh.Trimesh(vertices=v[:,[2,0,1]],faces=faces,process=True))
span_max=max(float(np.max(m.vertices@n)-s0) for m in meshes)
fin_onset=float(np.min(meshes[2].vertices@n)-s0)
hp=np.array(p['hinge_axis_right']['point'])[[2,0,1]];hd=np.array(p['hinge_axis_right']['direction'])[[2,0,1]]
def hinge_at(s):return hp+hd*((s0+s-hp@n)/(hd@n))
def section(s):
 groups=[];meta=[]
 for k,m in enumerate(meshes):
  path=m.section(plane_origin=n*(s0+s),plane_normal=n)
  if path is None:continue
  candidates=[]
  for xyz in path.discrete:
   q=np.column_stack((xyz@a,xyz@u))
   if len(q)<4 or np.linalg.norm(q[0]-q[-1])>.03:continue
   poly=Polygon(q)
   if not poly.is_valid:poly=poly.buffer(0)
   if poly.area>1e-5:candidates.append((q,poly))
  # Keep every non-nested exterior loop, including genuinely disconnected control skin
  # fragments at linkage slots. Nested circular bores/shell cavities are not exterior.
  keep=[]
  for i,(q,poly) in enumerate(candidates):
   if not any(j!=i and other.area>poly.area and other.buffer(.00001).covers(poly) for j,(_,other) in enumerate(candidates)):keep.append(q)
  groups.extend(keep);meta.append({'component_index':k,'closed_loops':len(candidates),'exterior_loops':len(keep)})
 if not groups:raise ValueError(f'No exterior {s}')
 return groups,meta

def envelope(groups,N=2001):
 lo=min(q[:,0].min() for q in groups);hi=max(q[:,0].max() for q in groups)
 x=lo+(hi-lo)*(1-np.cos(np.linspace(0,np.pi,N)))/2
 upper=np.full(N,-np.inf);lower=np.full(N,np.inf)
 for q in groups:
  for A,C in zip(q[:-1],q[1:]):
   if abs(C[0]-A[0])<1e-10:continue
   mask=(x>=min(A[0],C[0])-1e-8)&(x<=max(A[0],C[0])+1e-8)
   y=A[1]+(x[mask]-A[0])*(C[1]-A[1])/(C[0]-A[0])
   upper[mask]=np.maximum(upper[mask],y);lower[mask]=np.minimum(lower[mask],y)
 good=np.isfinite(upper)&np.isfinite(lower)
 upper=np.interp(x,x[good],upper[good]);lower=np.interp(x,x[good],lower[good])
 return x,upper,lower,int((~good).sum())

def get(s,bridge=True):
 groups,meta=section(s);x,up,low,gaps=envelope(groups)
 hx=float(hinge_at(s)@a)
 metrics,dat,norm=normalize_tail(x,up,low,groups,hinge_x=hx if bridge else None,hinge_bridge_halfwidth_mm=5.)
 le=np.array([metrics['leading_edge_aft_mm'],metrics['leading_edge_up_mm']]);te=np.array([metrics['trailing_edge_aft_mm'],metrics['trailing_edge_up_mm']])
 xyz=lambda q:a*q[0]+u*q[1]+n*(s0+s)
 metrics.update(span_station_from_root_plane_mm=float(s),leading_edge_aircraft_mm=xyz(le).tolist(),trailing_edge_aircraft_mm=xyz(te).tolist(),quarter_chord_aircraft_mm=xyz(.75*le+.25*te).tolist(),projected_chord_mm=float(te[0]-le[0]),incidence_aircraft_LE_up_deg=float(-np.degrees(np.arctan2((xyz(te)-xyz(le))[2],(xyz(te)-xyz(le))[0]))),raw_missing_x_samples=gaps,exterior_selection=meta)
 return metrics,dat,norm,(groups,x,up,low)

profile_stations={'root':.61,'midspan':120.,'outer_regular':220.,'fin_transition':240.,'tip_fin_near_cap':270.}
profiles={};fig,axs=plt.subplots(len(profile_stations),2,figsize=(14,3*len(profile_stations)))
neutral=[]
for row,(label,s) in enumerate(profile_stations.items()):
 m,dat,(grid,un,ln),(groups,x,up,low)=get(s)
 valid=s<fin_onset
 m.update(label=label,conventional_foil_status='resolved full fixed+rudder section' if valid else 'actual fin contour only; not a conventional tip airfoil')
 np.savetxt(D/f'{label}_140cosineSelig.dat',dat,fmt='%.10f',header=f'Stork tail {label}, s={s} mm; saved STEP pose; '+('fixed+rudder skin with nominal 10mm hinge closure' if valid else 'FIN CONTOUR NOT CONVENTIONAL AIRFOIL'),comments='')
 with (D/f'{label}_raw_section_loops.csv').open('w') as f:
  writer=csv.writer(f);writer.writerow(['loop_id','section_aft_mm','section_up_mm','aircraft_x_mm','aircraft_y_mm','aircraft_z_mm'])
  for loop_id,q in enumerate(groups):
   for pt in q:writer.writerow([loop_id,*pt,*(a*pt[0]+u*pt[1]+n*(s0+s))])
 for i,q in enumerate(groups):axs[row,0].plot(q[:,0],q[:,1],lw=.7,label=f'exterior {i}')
 # reconstructed bridges in source section coordinates
 for key in ['leading_edge','trailing_edge']:
  axs[row,0].scatter(m[f'{key}_aft_mm'],m[f'{key}_up_mm'],s=12)
 if m['hinge_bridge']:
  limits=m['hinge_bridge']['outer_skin_bridge_aft_limits_mm']
  for y in [up,low]:axs[row,0].plot(limits,np.interp(limits,x,y),'r--',lw=1.5)
 axs[row,0].set_title(f'{label}: s={s}mm; raw source exteriors + red hinge closure');axs[row,0].set_aspect('equal');axs[row,0].grid()
 axs[row,1].plot(grid,un);axs[row,1].plot(grid,ln);axs[row,1].plot(grid,(un+ln)/2,'k--',lw=.8);axs[row,1].set_title('normalized geometry' if valid else 'normalized fin contour ONLY');axs[row,1].set_aspect('equal');axs[row,1].grid()
 profiles[label]=m
 # Independently quantify source control pose. Two regression lines in section plane:
 # fixed skin midline at 15..60% total chord; rudder midline hx+12 to TE-3.
 if valid:
  mid=(up+low)/2;lo=x[0];c=x[-1]-lo;hx=float(hinge_at(s)@a)
  mf=(x>lo+.15*c)&(x<lo+.6*c);mr=(x>hx+12)&(x<x[-1]-3)
  pf=np.polyfit(x[mf],mid[mf],1);pr=np.polyfit(x[mr],mid[mr],1)
  relative=float(np.degrees(np.arctan(pr[0])-np.arctan(pf[0])))
  neutral.append({'station_mm':s,'fixed_midline_angle_up_deg':float(np.degrees(np.arctan(pf[0]))),'rudder_midline_angle_up_deg':float(np.degrees(np.arctan(pr[0]))),'rudder_minus_fixed_midline_deg':relative,'fixed_fit_RMS_mm':float(np.sqrt(np.mean((np.polyval(pf,x[mf])-mid[mf])**2))),'rudder_fit_RMS_mm':float(np.sqrt(np.mean((np.polyval(pr,x[mr])-mid[mr])**2))),'TE_offset_from_fixed_midline_mm':float(m['trailing_edge_up_mm']-np.polyval(pf,m['trailing_edge_aft_mm']))})
fig.tight_layout();fig.savefig(D/'section_diagnostics.png',dpi=180);plt.close(fig)

# Root LE: directly measured fixed skin at 0.05 mm, extrapolated linearly 0.05mm
# to actual mounting plane. Complete root profile is at .61mm because control starts .6mm.
def near_root_LE(s):
 groups,_=section(s)
 target=np.array([profiles['root']['trailing_edge_aft_mm'],profiles['root']['trailing_edge_up_mm']])
 points=np.vstack(groups);nose=points[points[:,0]<points[:,0].min()+20]
 q=nose[np.argmax(np.linalg.norm(nose-target,axis=1))]
 return a*q[0]+u*q[1]+n*(s0+s)
r1=near_root_LE(.05);r2=near_root_LE(.15)
rootLE=r1-.5*(r2-r1)

# Dense integration in physical root-normal coordinate; tip fin included as measured.
# First .6mm lacks rudder due source root clearance: strip .0..61 uses extrapolation
# of actual .61/1mm complete profiles for the nominal aerodynamic closure only.
stations=np.unique(np.r_[np.linspace(.61,span_max-.02,281),119.49212255-.02,119.49212255+.02,fin_onset-.02,fin_onset+.02,243.7551-.02,243.7551+.02,[220.,240.,270.]])
rows=[]
for j,s in enumerate(stations):
 try:
  m,*_=get(float(s));rows.append(m)
 except Exception as e:raise RuntimeError(f'station {s}: {e}')
 if j%25==0:print('integrated stations',j,len(stations),flush=True)
# Zero chord at actual fin extreme is degenerate, not an invented normalized foil.
ss=np.array([0.]+[m['span_station_from_root_plane_mm'] for m in rows]+[span_max])
cc=np.array([rows[0]['projected_chord_mm']]+[m['projected_chord_mm'] for m in rows]+[0.])
qc=np.array([rows[0]['quarter_chord_aircraft_mm']]+[m['quarter_chord_aircraft_mm'] for m in rows]+[rows[-1]['quarter_chord_aircraft_mm']])
chord_vectors=np.array([np.array(rows[0]['trailing_edge_aircraft_mm'])-rows[0]['leading_edge_aircraft_mm']]+[np.array(m['trailing_edge_aircraft_mm'])-m['leading_edge_aircraft_mm'] for m in rows]+[np.zeros(3)])
# shift first QC to root rather than retaining station .61
qc[0]-=n*.61
trap=np.trapezoid

def integral(mask):
 s=ss[mask];c=cc[mask];Q=qc[mask];V=chord_vectors[mask];area=float(trap(c,s));mac=float(trap(c*c,s)/area);qcm=trap(Q*c[:,None],s,axis=0)/area
 avgvec=trap(V*c[:,None],s,axis=0)/area;length=np.linalg.norm(V,axis=1)
 return {'projected_one_panel_area_mm2':area,'MAC_projected_mm':mac,'MAC_3D_chord_length_weighted_mm':float(trap(length*length,s)/trap(length,s)),'area_weighted_MAC_chord_vector_aircraft_mm':avgvec.tolist(),'area_weighted_quarter_chord_aircraft_mm':qcm.tolist(),'effective_MAC_LE_aircraft_mm':(qcm-.25*avgvec).tolist(),'area_centroid_span_station_mm':float(trap(s*c,s)/area),'definition':'c = LE-to-TE projected on section aft unit a; MAC=integral(c^2 ds)/area; 3D QC=integral(QC(s)*c ds)/area; MAC vector=integral(chord_vector*c ds)/area, effective LE=QC-.25vector; geometric not aerodynamic center; physical root-normal ds; saved control pose'}
full=integral(np.ones(len(ss),bool));regular=integral(ss<fin_onset)
# Integration refinement audit: compare every-other station, endpoints retained.
idx=np.unique(np.r_[np.arange(0,len(ss),2),len(ss)-1]);coarse=integral(np.isin(np.arange(len(ss)),idx))

# hinge closure sensitivity of required metrics at regular stations
sensitivity=[]
for label in ['root','midspan','outer_regular']:
 s=profile_stations[label];groups,meta=section(s);x,up,low,_=envelope(groups)
 for half in [3.,4.,5.,6.]:
  m,_,_=normalize_tail(x,up,low,groups,float(hinge_at(s)@a),half)
  sensitivity.append(dict(label=label,hinge_halfwidth_mm=half,max_t_c=m['max_thickness_over_chord'],max_camber_c=m['max_camber_over_chord']))

fig,axs=plt.subplots(2,2,figsize=(13,10))
for i,m in enumerate(meshes):
 v=m.vertices;step=max(1,len(v)//20000);v=v[::step];axs[0,0].scatter(v@a,v@n-s0,s=.2,label=f'component {i}')
axs[0,0].plot([m['leading_edge_aft_mm'] for m in rows],stations,'k-',lw=1)
axs[0,0].plot([m['trailing_edge_aft_mm'] for m in rows],stations,'k-',lw=1)
axs[0,0].axhline(fin_onset,c='red',ls='--',label='fin begins');axs[0,0].set_aspect('equal');axs[0,0].legend(fontsize=7);axs[0,0].set_xlabel('section aft coordinate / mm');axs[0,0].set_ylabel('root-normal span s / mm')
axs[0,1].plot(stations,[m['chord_mm'] for m in rows]);axs[0,1].set_ylabel('chord / mm')
axs[1,0].plot(stations,[m['max_thickness_over_chord'] for m in rows]);axs[1,0].set_ylabel('max geometric thickness/chord')
axs[1,1].plot(stations,[m['incidence_LE_up_deg'] for m in rows]);axs[1,1].set_ylabel('local section incidence LE-up / deg')
for ax in axs.flat:ax.grid();
for ax in [axs[0,1],axs[1,0],axs[1,1]]:ax.axvline(fin_onset,c='red',ls='--');ax.set_xlabel('s / mm; fin region is not a conventional foil')
fig.tight_layout();fig.savefig(D/'planform_diagnostics.png',dpi=180);plt.close(fig)

out={'units':'mm, degrees; ratios dimensionless','coordinate_system':'aircraft x aft=native Z; y right=native X; z up=native Y; common STEP datum unchanged','source_assembly':{'fixed_right_panel1_translation_native_mm':[0,-3.703521516,0],'fixed_right_2_3':'identity','rudder':'both genuine STEP solids unchanged on left, reflected native X=0 for right; no control rotation','STEP_tessellation':{'linear_tolerance_mm':.008,'angular_tolerance_rad':.05},'left_panel':'mirror right aircraft y=0, not independently fitted left STLs'},'basis':{'span_root_plane_normal_aircraft':n.tolist(),'aft_in_section_aircraft':a.tolist(),'up_in_section_aircraft':u.tolist(),'root_plane_equation_n_dot_xyz_mm':s0,'definition':'physical mount-plane normal, not global aircraft-y sections; full 3D n retained including aft component','dihedral_cant_above_horizontal_deg':float(np.degrees(np.arctan2(n[2],n[1]))),'cant_from_vertical_deg':float(np.degrees(np.arctan2(n[1],n[2]))),'span_axis_elevation_3D_deg':float(np.degrees(np.arcsin(n[2]))),'span_axis_aft_sweep_deg':float(np.degrees(np.arcsin(n[0]))),'normal_span_root_to_fin_extreme_mm':span_max,'fin_starts_s_mm':fin_onset},'root_LE_aircraft_mm':rootLE.tolist(),'root_LE_method':'fixed-skin LE at s=.05 and .15 linearly extrapolated .05 mm to mounting plane; independent of absent rudder root clearance','profiles':profiles,'true_tip':{'s_mm':span_max,'conventional_airfoil':None,'chord_incidence_tc_camber_TE':None,'reason':'geometric fin extreme degenerates and is not a conventional finite-chord airfoil; do not substitute a NACA or other conventional foil','near_tip_actual_fin_dat':'tip_fin_near_cap_140cosineSelig.dat at s=270mm, real fin contour only'},'planform_full_including_fin':full,'planform_regular_before_fin_sample_truncation':regular,'integration_convergence':{'fine_station_count':len(ss),'coarse_station_count':len(idx),'area_fine_minus_coarse_mm2':full['projected_one_panel_area_mm2']-coarse['projected_one_panel_area_mm2'],'MAC_fine_minus_coarse_mm':full['MAC_projected_mm']-coarse['MAC_projected_mm']},'neutral':{'true_zero_relative_agreed_neutral_contour_deg':None,'status':'UNKNOWN: no agreed neutral target contour/hinge angle/transmitter calibration provided; coaxial hinge and smooth saved pose do not prove it','source_STEP_rotation_applied_deg':0.,'source_pose_geometric_diagnostics':neutral,'diagnostic_definition':'linear fits of raw upper/lower-envelope midpoint: fixed 15..60% total section aft chord; rudder hinge+12mm to TE-3mm. Relative slope is not commanded/aerodynamic-neutral certification; fixed camber and fitting windows matter'},'hinge_closure':{'method':'straight upper and lower bridges nominally hx-5 to hx+5 mm, expanded to 1mm past disconnected exterior gap lips where present; actual per-station limits recorded; all nonnested physical exterior loops retained, nested cavities removed','width_sensitivity':sensitivity,'not_a_solid_boolean':'outer skin aerodynamic section reconstruction, not CAD union or watertight CFD boundary'},'limitations':['Root complete profile at .61mm, 0.01mm outboard of STEP rudder root; actual mounting-plane root LE separately reported.','First .61mm planform strip uses constant complete-profile chord and QC translated spanwise to root; nominal clearance closure, not extra source material.','Full-planform MAC is a geometric projected-area measure including the real fin; do not treat fin-tip contours as conventional foil sections.','Section local incidence is relative projected aircraft aft axis in physical plane. Aircraft x-z chord pitch also separately reported.','Only fixed STL exists, so tessellation and skin interpolation are part of uncertainty; reported precision is not CAD exactness.','No geometric-neutral target supplied: source pose is measured without rotating to a guessed zero.','Bilateral position from mirror y=0; no wing-tail arms computed here.']}
(D/'tail_geometry.json').write_text(json.dumps(out,indent=2,allow_nan=False))
flatkeys=['label','span_station_from_root_plane_mm','chord_mm','projected_chord_mm','incidence_LE_up_deg','incidence_aircraft_LE_up_deg','max_thickness_over_chord','max_thickness_x_over_chord','max_camber_over_chord','max_camber_x_over_chord','TE_thickness_mm','TE_thickness_over_chord']
with (D/'profile_summary.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=flatkeys+['LE_x_mm','LE_y_mm','LE_z_mm','conventional_foil_status']);w.writeheader()
 for m in profiles.values():w.writerow({**{k:m[k] for k in flatkeys},**dict(zip(['LE_x_mm','LE_y_mm','LE_z_mm'],m['leading_edge_aircraft_mm'])),'conventional_foil_status':m['conventional_foil_status']})
with (D/'spanwise_geometry.csv').open('w') as f:
 keys=flatkeys[1:]+['LE_x_mm','LE_y_mm','LE_z_mm','QC_x_mm','QC_y_mm','QC_z_mm','region'];w=csv.DictWriter(f,fieldnames=keys);w.writeheader()
 for m in rows:w.writerow({**{k:m[k] for k in flatkeys[1:]},**dict(zip(['LE_x_mm','LE_y_mm','LE_z_mm'],m['leading_edge_aircraft_mm'])),**dict(zip(['QC_x_mm','QC_y_mm','QC_z_mm'],m['quarter_chord_aircraft_mm'])),'region':'regular fixed+rudder' if m['span_station_from_root_plane_mm']<fin_onset else 'fin/nonconventional'})
for name,r in receipt.items():r['after_sha256']=sha(r['path']);r['unchanged']=r['after_sha256']==r['before_sha256'];assert r['unchanged']
assert all(sha(q)==h for q,h in auxreceipt.items())
(D/'source_hash_verification.json').write_text(json.dumps({'all_original_inputs_unchanged':True,'sources':receipt,'read_only_reference_and_script_sha256':auxreceipt,'shared_helper_verified_identical_to_own_copy':True},indent=2))
print(json.dumps({'root_LE_aircraft_mm':rootLE.tolist(),'full_planform':full,'neutral':out['neutral'],'span_max_mm':span_max,'cant_deg':out['basis']['dihedral_cant_above_horizontal_deg']},indent=2),flush=True)

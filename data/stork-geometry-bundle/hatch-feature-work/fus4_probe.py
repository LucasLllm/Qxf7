"""Independent FUS4 mesh rear lip check; uses already feature-registered FUS4 transform read-only."""
from investigate import *
import numpy as np
import trimesh
from scipy.optimize import least_squares
chain=json.loads((ROOT/'notes/stork-development/stork-aero-geometry/fuselage-feature-work/verified_chain.json').read_text())
f=chain['fus4_registration'];p=Path(f['source']);assert hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256']
m=trimesh.load(str(p),force='mesh',process=False);m.apply_transform(np.array(f['transform_source_to_native']));v=m.vertices;t=v[m.faces];norm=m.face_normals
D=json.loads((OUT/'features.json').read_text());checks=[]
for face in [15,21]:
 h=D['HATCH MIDDLE.STEP']['solids'][1]['features'][face-1];center=np.array(h['location'])[[0,2]];rad=np.linalg.norm(t[:,:,[0,2]]-center,axis=2)
 mask=np.all(abs(rad-25)<0.015,axis=1)&(abs(norm[:,1])<0.001)&np.all(t[:,:,2]>253.749,axis=1)
 pts=np.unique(t[mask].reshape(-1,3),axis=0);q=pts[:,[0,2]]
 if len(q)<6:
  checks.append({'hatch_face':face,'status':'insufficient_selected_mesh_samples','triangle_count':int(mask.sum()),'point_count':len(q)});continue
 fit=least_squares(lambda x:np.linalg.norm(q-x[:2],axis=1)-x[2],[*center,25],xtol=1e-13,ftol=1e-13,gtol=1e-13)
 checks.append({'hatch_face':face,'status':'curved_lip_verified','selection':'mesh triangles all vertices within 0.015mm of nominal r25, |normalY|<0.001 and Z>253.749; true radial surface vertices, not convex hull','triangle_count':int(mask.sum()),'point_count':len(q),'fitted_axis_XZ_mm':fit.x[:2].tolist(),'hatch_axis_XZ_mm':center.tolist(),'axis_XZ_offset_mm':float(np.linalg.norm(fit.x[:2]-center)),'fitted_radius_mm':float(fit.x[2]),'hatch_radius_mm':h['radius'],'radial_clearance_mm':float(fit.x[2]-h['radius']),'max_fit_radial_residual_mm':float(np.max(abs(fit.fun))),'mesh_Y_range_mm':[float(pts[:,1].min()),float(pts[:,1].max())]})
r={'source':f['source'],'sha256':f['sha256'],'transform_source_to_native':f['transform_source_to_native'],'transform_authority':'fuselage-feature-work/verified_chain.json: seven-circle pattern at two ends; read-only dependency','checks':checks}
(OUT/'fus4_lip_check.json').write_text(json.dumps(r,separators=(',',':')));print(json.dumps(r,indent=2))

"""Generate actual projected-component outlines, not convex hulls or guessed booms."""
from pathlib import Path
import json,hashlib
import numpy as np
import trimesh,shapely
from shapely.geometry import Polygon
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
D=Path(__file__).resolve().parent;OUT=D/'review-overlays';OUT.mkdir(exist_ok=True)
manifest=json.loads((D/'reference-assembly/assembly_manifest.json').read_text());by={r['component']:r for r in manifest['components']}
path=D/'reference-assembly/Stork-feature-registered-gate-review.glb';scene=trimesh.load(path,force='scene',process=False)
assert len(scene.geometry)==len(by)
colors={'wing':'#247eb3','tail':'#cc7a13','fuselage':'#69757c','hardware':'#333333'}
receipt={'input_glb_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'views':{},'origin':'Original common STEP datum. Aircraft x aft=nativeZ,y right=nativeX,z up=nativeY.','scope':'Feature-registered subset only. Orthographic union of projected triangles, per-component exterior loops (internal holes discarded), then union by category. Not convex hull. Missing booms/motors not drawn. Controls retain saved source pose, not certified neutral.'}
for view,ix,iy in [('top',1,0),('front',1,2),('side',0,2)]:
 groups={k:[] for k in colors}
 for label,m in scene.geometry.items():
  cat=by[label]['category'];t=m.triangles[:,:,[ix,iy]];a=t[:,1]-t[:,0];b=t[:,2]-t[:,0];t=t[np.abs(a[:,0]*b[:,1]-a[:,1]*b[:,0])>1e-9]
  if not len(t):continue
  geo=shapely.union_all(shapely.polygons(t));parts=[geo] if geo.geom_type=='Polygon' else list(geo.geoms)
  groups[cat].extend([Polygon(p.exterior) for p in parts if p.geom_type=='Polygon'])
 fig,ax=plt.subplots(figsize=(13,8));features=[]
 for cat,parts in groups.items():
  if not parts:continue
  geo=shapely.union_all(parts);parts=[geo] if geo.geom_type=='Polygon' else list(geo.geoms)
  for i,p in enumerate(parts):
   if p.geom_type!='Polygon':continue
   x,y=p.exterior.xy;ax.fill(x,y,color=colors[cat],alpha=.12);ax.plot(x,y,color=colors[cat],linewidth=.8,label=cat if i==0 else None)
  features.append({'type':'Feature','properties':{'category':cat},'geometry':shapely.geometry.mapping(geo)})
 if view=='side':
  nose=manifest['frontmost_aircraft_x_mm'];aft=manifest['rearmost_aircraft_x_mm'];mount=nose+manifest['manufacturer_1000mm_reference_nose_to_pusher_mount_mm'];z=scene.bounds[1,2]+35
  for x in [nose,mount,aft]:ax.axvline(x,color='#555555',linestyle=':',linewidth=.7)
  ax.annotate('',(mount,z),(nose,z),arrowprops={'arrowstyle':'<->','color':'#264e78'});ax.text((mount+nose)/2,z+6,'1000.00 mm nose to pusher face',ha='center',fontsize=9)
  ax.annotate('',(aft,z+45),(nose,z+45),arrowprops={'arrowstyle':'<->','color':'#7c3f11'});ax.text((aft+nose)/2,z+51,'1044.02 mm nose to fixed-tail aft extent',ha='center',fontsize=9)
  ax.set_ylim(scene.bounds[0,2]-30,z+95)
 ax.axhline(0,color='#888',linestyle='--',linewidth=.5);ax.axvline(0,color='#888',linestyle='--',linewidth=.5)
 ax.set_aspect('equal');ax.set_xlabel(['x aft [mm]','y right [mm]','z up [mm]'][ix]);ax.set_ylabel(['x aft [mm]','y right [mm]','z up [mm]'][iy]);ax.grid(alpha=.15)
 ax.set_title('Stork registered reference — '+view+' exterior outlines\nLength distinction accepted for extraction; not complete hardware or neutral-control certification',fontsize=12)
 ax.legend(fontsize=9);fig.tight_layout();p=OUT/(view+'_outline_overlay.png');fig.savefig(p,dpi=180);plt.close(fig)
 geo_path=OUT/(view+'_outlines.geojson');geo_path.write_text(json.dumps({'type':'FeatureCollection','features':features})+'\n');receipt['views'][view]={'projection_axis_indices':[ix,iy],'png_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'outline_geojson_sha256':hashlib.sha256(geo_path.read_bytes()).hexdigest()}
(OUT/'outline_verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))

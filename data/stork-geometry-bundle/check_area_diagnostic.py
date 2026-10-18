"""Independent numerical area check and scoped source-integrity verification."""
from pathlib import Path
import csv,json,hashlib
import numpy as np
import shapely
from shapely.geometry import Polygon, MultiPolygon, LineString
import trimesh
D=Path(__file__).resolve().parent
rows=list(csv.DictReader((D.parent/'source-format-audit/cad_inventory.csv').open()))
info=json.loads((D/'area_geometry_diagnostic.json').read_text())
polys=[]
for r in info['parts']:
 m=trimesh.load_mesh(r['path'],process=False)
 t=np.asarray(m.triangles)[:,:,[0,2]]
 a=t[:,1]-t[:,0];b=t[:,2]-t[:,0];t=t[np.abs(a[:,0]*b[:,1]-a[:,1]*b[:,0])>1e-9]
 g=shapely.union_all(shapely.polygons(t));sub=list(g.geoms) if isinstance(g,MultiPolygon) else [g]
 polys.extend(Polygon(p.exterior) for p in sub if isinstance(p,Polygon))
u=shapely.union_all(polys)
# Independent integration of intersection lengths: no polygon area used inside the integrator.
integrals=[]
for step in [1.,.5,.25]:
 xs=np.arange(u.bounds[0]+step/2,u.bounds[2],step)
 val=2*sum(u.intersection(LineString([(float(x),-1000),(float(x),1000)])).length for x in xs)*step/10000
 integrals.append({'step_mm':step,'both_wings_area_dm2':val,'difference_from_polygon_area_dm2':val-info['both_exposed_panels_projected_dm2']})
assert abs(integrals[-1]['difference_from_polygon_area_dm2'])<.01
# Known-area control for the triangle-union method.
tri=np.array([[[0.,0.],[100.,0.],[100.,200.]],[[0.,0.],[100.,200.],[0.,200.]]])
assert abs(shapely.union_all(shapely.polygons(tri)).area-20000)<1e-8
for r in rows:assert hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()==r['sha256']
base=next(r for r in rows if r['filename']=='WING 1 R.STL')
m=trimesh.load_mesh(base['path'],process=False);t=np.asarray(m.triangles)[:,:,[0,2]];a=t[:,1]-t[:,0];b=t[:,2]-t[:,0];t=t[np.abs(a[:,0]*b[:,1]-a[:,1]*b[:,0])>1e-9]
g=shapely.union_all(shapely.polygons(t));sub=list(g.geoms) if isinstance(g,MultiPolygon) else [g];base_area=shapely.union_all([Polygon(p.exterior) for p in sub if isinstance(p,Polygon)]).area/10000
vtol_inner=sum(r['outer_silhouette_mm2'] for r in info['parts'] if r['filename'].startswith('WING 1.'))/10000
result={'independent_section_integration':integrals,'triangle_rectangle_control':'PASS: 20000 mm2','inventory_hash_checks':len(rows),'base_WING1_right_projected_area_dm2':base_area,'VTOL_1p1_plus_1p2_right_projected_area_dm2':vtol_inner,'VTOL_vs_base_inner_area_percent':100*(vtol_inner/base_area-1),'limits':'Independent integration checks numerical area extraction only, not installed geometry or neutral control placement.'}
(D/'area_diagnostic_checks.json').write_text(json.dumps(result,indent=2)+'\n')
assert json.loads((D/'area_diagnostic_checks.json').read_text())==result
print(json.dumps(result,indent=2))

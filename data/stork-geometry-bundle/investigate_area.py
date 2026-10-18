"""Read-only source investigation; writes only beside this script. Not a verified assembly."""
from pathlib import Path
import csv, hashlib, json, re
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import requests
from bs4 import BeautifulSoup
import pymupdf
import trimesh
import shapely
from shapely.geometry import Polygon, MultiPolygon

OUT=Path(__file__).resolve().parent
ROOT=OUT.parent.parent.parent.parent
AUDIT=OUT.parent/'source-format-audit/cad_inventory.csv'
assert AUDIT.exists(), AUDIT
rows=list(csv.DictReader(AUDIT.open()))
byname={r['filename']:r for r in rows}
SOURCES=OUT/'area-discrepancy-sources'
SOURCES.mkdir(exist_ok=True)
urls=[
 ('intro-2023','https://flightory.com/2023/04/03/stork-introducing-new-fpv-aircraft-design/'),
 ('current-stork','https://flightory.com/product/stork/'),
 ('current-vtol','https://flightory.com/product/stork-vtol-pack/'),
 ('manual-2023','https://flightory.com/wp-content/uploads/2023/04/STORK-MANUAL-V1.pdf'),
 ('manual-current-base','https://flightory.com/wp-content/uploads/2026/04/STORK-USER-MANUAL.pdf'),
 ('manual-current-vtol','https://flightory.com/wp-content/uploads/2026/04/STORK-USER-MANUAL-VTOL.pdf')]
def fetch(pair):
 name,url=pair
 try:
  r=requests.get(url,timeout=40);r.raise_for_status()
  suffix='.pdf' if url.endswith('.pdf') else '.html'
  path=SOURCES/(name+suffix);path.write_bytes(r.content)
  result={'name':name,'url':url,'final_url':r.url,'http_status':r.status_code,'path':str(path),'sha256':hashlib.sha256(r.content).hexdigest(),'retrieved_utc':r.headers.get('Date'),'bytes':len(r.content)}
  if suffix=='.pdf':
   with pymupdf.open(path) as doc:
    pages=[]
    for i,p in enumerate(doc):
     t=p.get_text()
     if any(x in t.lower() for x in ['wing area','aspect ratio','wing geometry']):pages.append({'page':i+1,'text':t})
    result['relevant_pages']=pages
  else:
   soup=BeautifulSoup(r.text,'html.parser');t=soup.get_text(' ',strip=True)
   (SOURCES/(name+'.txt')).write_text(t)
   result['relevant_excerpts']=[t[max(0,m.start()-100):m.end()+220] for m in re.finditer(r'(?i)wing.{0,10}area|31.{0,8}dm|24.{0,8}dm|aspect ratio|1620|1600|2023|2026',t)]
   result['manual_links']=sorted(set(a.get('href') for a in soup.select('a[href]') if '.pdf' in a.get('href','')))
  return result
 except Exception as e:return {'name':name,'url':url,'error':str(e)}
with ThreadPoolExecutor(max_workers=3) as pool:web=list(pool.map(fetch,urls))
(OUT/'area_sources.json').write_text(json.dumps(web,indent=2))
print('WEB',json.dumps([{k:r.get(k) for k in ['name','http_status','error','relevant_pages','relevant_excerpts']} for r in web],indent=2),flush=True)

names=['WING 1.1 R VTOL.STL','WING 1.2 R VTOL.STL','WING 2 R.STL','WING 3 R.STL','WINGTIP 3 R.STL','AIILERON 1 R.STL','AILERON 2 R.STL']
shapes={};partdata=[]
for name in names:
 r=byname[name];p=Path(r['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256']
 mesh=trimesh.load_mesh(p,process=False)
 # Native X is spanwise, native Z is chordwise. Use supplied right-side coordinates, no transforms.
 tri=np.asarray(mesh.triangles)[:,:,[0,2]]
 delta1=tri[:,1]-tri[:,0]; delta2=tri[:,2]-tri[:,0]
 twice=np.abs(delta1[:,0]*delta2[:,1]-delta1[:,1]*delta2[:,0])
 tri=tri[twice>1e-9]
 projected=shapely.union_all(shapely.polygons(tri))
 # Fill silhouette interior holes; retain concave exterior, never convex-hull the panel.
 polys=list(projected.geoms) if isinstance(projected,MultiPolygon) else [projected]
 silhouette=shapely.union_all([Polygon(g.exterior) for g in polys if isinstance(g,Polygon)])
 shapes[name]=silhouette
 partdata.append({'filename':name,'path':str(p),'sha256':r['sha256'],'native_bounds_mm':mesh.bounds.tolist(),'triangle_projection_union_mm2':projected.area,'outer_silhouette_mm2':silhouette.area,'triangle_count':len(mesh.faces)})
 print('PART',name,'area dm2',silhouette.area/10000,flush=True)
wing=shapely.union_all(list(shapes.values()))
fixed=shapely.union_all([v for k,v in shapes.items() if 'ILERON' not in k])
# Alternative estimation includes centerline carry-through as a rectangular strip, NOT source geometry.
# Use a section just beyond the inboard joint rather than triangle extrema at one isolated vertex.
from shapely.geometry import LineString
spanroot=92.
cross=wing.intersection(LineString([(spanroot+0.1,-1000),(spanroot+0.1,1000)]))
b=cross.bounds;chord=b[3]-b[1]
exposed=2*wing.area/10000
center=2*spanroot*chord/10000
summary={'status':'native_right_component_projection_diagnostic_NOT_verified_assembly',
 'method':'Union all nondegenerate source STL triangles projected into native X/Z; fill interior silhouette holes, preserve concave outer outlines. Right-side files used without any transforms. Both wings assumed mirrored only for diagnostic. Includes both ailerons at their supplied coordinates. Native span/chord orientation inferred from part dimensions and coherent adjacent right-side boundaries; not verified by complete spar/hinge mating.',
 'area_units':'dm2','parts':partdata,'right_outline_bounds_span_chord_mm':list(wing.bounds),'diagnostic_mirrored_span_mm':2*wing.bounds[2],
 'both_exposed_panels_projected_dm2':exposed,'both_exposed_fixed_only_dm2':2*fixed.area/10000,
 'root_chord_at_native_span_92p1_mm':chord,'centerline_extension_ASSUMPTION':'Rectangular extension of diagnostic chord at span 92.1 mm inward to centerline, mirrored; not manufacturer CAD or confirmed root chord. Gross area depends on carry-through convention.',
 'centerline_extension_dm2':center,'gross_with_assumed_centerline_extension_dm2':exposed+center,
 'reference_consistency':{'current_span_1p62m_AR_for_31dm2':1.62**2/.31,'current_span_1p62m_AR_for_24dm2':1.62**2/.24,'current_span_1p62m_area_from_AR8p3_dm2':1.62**2/8.3*100,'old_span_1p6m_AR_for_24dm2':1.6**2/.24,'current_1400_to_3100g_loading_at_31dm2':[1400/31,3100/31],'current_1400_to_3100g_loading_at_24dm2':[1400/24,3100/24]},
 'limits':['No feature-based assembly or span/length/area gate certification.','No incidence/dihedral correction: native coordinate projection only.','Projected silhouette area is not wetted area.','Centerline extension is an explicit diagnostic assumption, not measured hidden wing.','No original manufacturing geometry modified.']}
(OUT/'area_geometry_diagnostic.json').write_text(json.dumps(summary,indent=2))
# Inspectable diagnostic, never label as verified aircraft assembly overlay.
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
fig,ax=plt.subplots(figsize=(11,4))
for name,g in shapes.items():
 for p in (list(g.geoms) if isinstance(g,MultiPolygon) else [g]):
  x,y=p.exterior.xy;ax.fill(x,y,alpha=.35,label=name)
ax.set_aspect('equal');ax.set_xlabel('Native X (spanwise), mm');ax.set_ylabel('Native Z (chordwise), mm');ax.set_title('Diagnostic: supplied right-wing STL projections, NOT verified assembly');ax.legend(fontsize=7,ncol=2);fig.tight_layout();fig.savefig(OUT/'area_projection_diagnostic.png',dpi=160);plt.close(fig)
for r in rows:assert hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()==r['sha256']
for r in web:
 if 'path' in r:assert hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()==r['sha256']
assert json.loads((OUT/'area_geometry_diagnostic.json').read_text())==summary
assert len((OUT/'area_projection_diagnostic.png').read_bytes())>1000
print('RESULT',json.dumps({k:v for k,v in summary.items() if k!='parts'},indent=2))
print('PASS: original 108 hashes unchanged; fetched captures and diagnostic JSON read back.')

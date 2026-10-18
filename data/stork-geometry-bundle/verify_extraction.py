"""Independent exported profile validation. Does not certify control neutral or flightworthiness."""
from pathlib import Path
import json,csv,hashlib
import numpy as np
D=Path(__file__).resolve().parent

def check_dat(path):
 lines=path.read_text().splitlines();a=np.loadtxt(lines[1:]);assert a.shape==(140,2),('pointcount',a.shape)
 assert np.isfinite(a).all(),'nonfinite'
 gu=(1-np.cos(np.linspace(0,np.pi,70)))/2;gl=(1-np.cos(np.linspace(0,np.pi,71)))/2
 expected=np.r_[gu[::-1],gl[1:]]
 # Supports either branch receiving 70/71 points, but never claims equal cosine grids on both.
 gu2=(1-np.cos(np.linspace(0,np.pi,71)))/2;gl2=(1-np.cos(np.linspace(0,np.pi,70)))/2
 expected2=np.r_[gu2[::-1],gl2[1:]]
 err=min(np.max(np.abs(a[:,0]-expected)),np.max(np.abs(a[:,0]-expected2)))
 assert err<1e-7,('not140 shared-LE cosine grid',err)
 i=int(np.argmin(a[:,0]));assert abs(a[0,0]-1)<1e-7 and abs(a[-1,0]-1)<1e-7
 assert abs(a[i,0])<1e-7,'LE x not0'
 assert np.all(np.diff(a[:i+1,0])<=1e-8) and np.all(np.diff(a[i:,0])>=-1e-8),'branch order'
 x=np.linspace(.005,.995,1001);u=np.interp(x,a[:i+1,0][::-1],a[:i+1,1][::-1]);l=np.interp(x,a[i:,0],a[i:,1]);th=u-l
 assert th.min()>-1e-5,('crossing surfaces',th.min())
 assert th.max()>0 and th.max()<.7,'thickness bound'
 return {'path':str(path.relative_to(D)) if path.is_relative_to(D) else str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'coordinate_count':len(a),'max_cosine_grid_error':float(err),'LE_y_over_chord':float(a[i,1]),'TE_midpoint_y_over_chord':float((a[0,1]+a[-1,1])/2),'minimum_sampled_thickness_over_chord':float(th.min()),'maximum_sampled_thickness_over_chord':float(th.max()),'pass':True}

def run():
 rows=list(csv.DictReader((D.parent/'source-format-audit/cad_inventory.csv').open()));mismatches=[]
 for r in rows:
  if hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()!=r['sha256']:mismatches.append(r['filename'])
 profiles=[]
 for directory in ['wing-extraction','tail-extraction']:
  for p in sorted((D/directory).rglob('*.dat')):
   try:profiles.append(check_dat(p))
   except (AssertionError,ValueError) as e:profiles.append({'path':str(p.relative_to(D)),'pass':False,'failure':str(e)})
 expected=sum(len(list(csv.DictReader((D/p).open()))) for p in ['wing-extraction/sections.csv','tail-extraction/profile_summary.csv'])
 assert len(profiles)==expected,('CSV/profile count mismatch',len(profiles),expected)
 j={'original_source_hash_checks':len(rows),'source_mismatches':mismatches,'exported_profiles_checked':len(profiles),'profiles':profiles,'profile_validation_pass':bool(profiles) and all(p['pass'] for p in profiles),'original_sources_unchanged':not mismatches,'qualification':'These checks validate file format, sampling, gross contour sanity and source preservation only. They do not independently establish installed pose/control neutral/flightworthiness.'}
 (D/'extraction_verification.json').write_text(json.dumps(j,indent=2)+'\n');print(json.dumps({k:v for k,v in j.items() if k!='profiles'},indent=2))
 if mismatches or not j['profile_validation_pass']:raise SystemExit(1)
if __name__=='__main__':run()

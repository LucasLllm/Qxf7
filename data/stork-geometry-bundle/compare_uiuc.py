"""Reproducible UIUC shape comparison; no design/airfoil identification claims.
Default builds the official archive corpus. --profiles searches existing extracted .dat files.
"""
from pathlib import Path
import zipfile,json,hashlib,csv,argparse
import numpy as np
D=Path(__file__).resolve().parent
G=np.linspace(0,1,1001)
def parse_points(text):
 rows=[]
 for line in text.splitlines():
  p=line.replace(',',' ').split()
  if len(p)!=2:continue
  try:a,b=map(float,p)
  except ValueError:continue
  if np.isfinite(a+b):rows.append([a,b])
 a=np.asarray(rows,float)
 if a.ndim!=2 or len(a)<15:raise ValueError('fewer than15 coordinate rows')
 if np.any(np.abs(a)>5):raise ValueError('count row or nonunit/multielement data')
 return a

def surfaces(a,already_normalized=False):
 a=np.asarray(a,float);leidx=int(np.argmin(a[:,0]))
 if leidx<3 or leidx>len(a)-4:raise ValueError('not a single Selig TE-LE-TE contour')
 le=a[leidx];te=(a[0]+a[-1])/2;vec=te-le;c=np.linalg.norm(vec)
 if c<.1 or c>2:raise ValueError('implausible chord')
 ex=vec/c;ez=np.array([-ex[1],ex[0]]);p=np.column_stack(((a-le)@ex/c,(a-le)@ez/c))
 branches=[p[:leidx+1][::-1],p[leidx:]]
 out=[]
 for q in branches:
  if np.min(np.diff(q[:,0]))<-.025:raise ValueError('nonmonotonic branch or multielement')
  if q[:,0].max()<.97 or q[:,0].min()>.005:raise ValueError('incomplete chord coverage')
  order=np.argsort(q[:,0]);x,y=q[order].T;ux,ii=np.unique(x,return_index=True);out.append(np.interp(G,ux,y[ii]))
 u,l=out if np.mean(out[0]-out[1])>=0 else out[::-1]
 if np.min(u-l)<-.002:raise ValueError('crossing/invalid contour')
 if np.max(u-l)>.65:raise ValueError('too thick/multielement')
 return u,l

def rms(a,b):
 return float(100*np.sqrt(np.trapezoid(((a[0]-b[0])**2+(a[1]-b[1])**2)/2,G)))

def build():
 src=D/'uiuc-sources';r=json.loads((src/'source_receipt.json').read_text());path=src/'coord_seligFmt.zip';assert hashlib.sha256(path.read_bytes()).hexdigest()==r['archive_sha256']
 z=zipfile.ZipFile(path);names=[];uu=[];ll=[];excluded=[]
 for n in z.namelist():
  if not n.lower().endswith('.dat'):continue
  try:a=parse_points(z.read(n).decode('utf-8',errors='replace'));u,l=surfaces(a)
  except (ValueError,IndexError) as e:excluded.append({'member':n,'reason':str(e)});continue
  names.append(n);uu.append(u);ll.append(l)
 out=D/'uiuc-comparison';out.mkdir(exist_ok=True)
 np.savez_compressed(out/'corpus.npz',grid=G,names=np.array(names),upper=np.array(uu),lower=np.array(ll))
 receipt={'archive_sha256':r['archive_sha256'],'accepted_profiles':len(names),'excluded_profiles':len(excluded),'exclusions':excluded,'metric':'RMS ordinate deviation percent chord:100*sqrt(integral_0^1((upper1-upper2)^2+(lower1-lower2)^2)/2 dx),1001 uniform chord stations,trapezoidal integration. Independent LE/TE-midpoint chord alignment, no thickness/camber fitting. Maximum deviation also reported.','scope':r['scope'],'source_index_url':r['index_url'],'source_archive_url':r['archive_url'],'identification_claim':False}
 (out/'corpus_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print('CORPUS',len(names),'accepted;',len(excluded),'excluded');return receipt

def match(profile_paths):
 out=D/'uiuc-comparison';z=np.load(out/'corpus.npz');un=z['upper'];ln=z['lower'];names=z['names'];assert np.array_equal(G,z['grid']);rows=[];errors=[];spanpairs=[];profiles={}
 for p in profile_paths:
  if p.stem.startswith(('curved_tip','near_tip')) or p.stem in ['fuselage_junction','root_plate_in','root_plate_out','aileron_start_in','aileron_start_out','aileron_end_out','tip_root_in']:
   errors.append({'profile':str(p.relative_to(D)),'reason':'Oblique winglet diagnostic or mechanical-plate/clearance cut; not ranked as a conventional aerodynamic section.'});continue
  if p.parent.name=='tail-extraction' and ('fin_transition' in p.stem or 'tip_fin' in p.stem):
   errors.append({'profile':str(p.relative_to(D)),'reason':'Actual nonconventional fin contour; intentionally not ranked as a conventional airfoil.'});continue
  try:surf=surfaces(parse_points(p.read_text()))
  except (ValueError,IndexError) as e:errors.append({'profile':str(p.relative_to(D)),'reason':str(e)});continue
  profiles[str(p.relative_to(D))]=surf
  sq=((un-surf[0])**2+(ln-surf[1])**2)/2;scores=100*np.sqrt(np.trapezoid(sq,G,axis=1));best=np.argsort(scores)[:5]
  for rank,i in enumerate(best,1):rows.append({'profile':str(p.relative_to(D)),'rank':rank,'uiuc_member':str(names[i]),'rms_ordinate_deviation_percent_chord':float(scores[i]),'max_ordinate_deviation_percent_chord':float(100*max(np.max(np.abs(un[i]-surf[0])),np.max(np.abs(ln[i]-surf[1]))))})
 with (out/'uiuc_matches.csv').open('w',newline='') as h:
  field=['profile','rank','uiuc_member','rms_ordinate_deviation_percent_chord','max_ordinate_deviation_percent_chord'];w=csv.DictWriter(h,fieldnames=field);w.writeheader();w.writerows(rows)
 for a,sa in profiles.items():
  for b,sb in profiles.items():
   if a>=b or a.split('/')[0]!=b.split('/')[0]:continue
   spanpairs.append({'profile_1':a,'profile_2':b,'rms_ordinate_deviation_percent_chord':rms(sa,sb),'max_ordinate_deviation_percent_chord':float(100*max(np.max(np.abs(sa[0]-sb[0])),np.max(np.abs(sa[1]-sb[1]))))})
 with (out/'normalized_section_deviations.csv').open('w',newline='') as h:
  w=csv.DictWriter(h,fieldnames=['profile_1','profile_2','rms_ordinate_deviation_percent_chord','max_ordinate_deviation_percent_chord']);w.writeheader();w.writerows(spanpairs)
 receipt={'matched_profiles':len(profiles),'match_rows':len(rows),'top_candidates_per_profile':5,'excluded_extracted_profiles':errors,'pairwise_same_component_family_comparisons':len(spanpairs),'corpus_npz_sha256':hashlib.sha256((out/'corpus.npz').read_bytes()).hexdigest(),'caution':'Closest in this finite archive under stated metric, not proof of intended/manufacturer airfoil. Archive postrelease updates omitted. Shape-only comparisons remove chord/placement/twist.'}
 (out/'match_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--profiles',action='store_true');a=ap.parse_args()
 if not a.profiles:build()
 else:match(sorted([p for directory in ['wing-extraction','tail-extraction'] for p in (D/directory).rglob('*.dat')]))

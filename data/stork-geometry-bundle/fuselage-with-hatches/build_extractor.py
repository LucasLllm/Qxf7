from pathlib import Path
import json
O=Path(__file__).resolve().parent
B=O.parent/'fuselage-extraction'
s=(B/'extract.py').read_text()
s=s.replace('from parameter_sampler import',f'sys.path.insert(0,{str(B)!r})\nfrom parameter_sampler import')
s=s.replace('This closes hollow shells, holes, canopy/open slots and convexifies local concavity.','Includes complete feature-verified hatch solids; convexifies cavities and remaining seams/concavity.')
insert='''
BASELINE=O.parent/'fuselage-extraction'
HATCH=O.parent/'hatch-feature-work'
baseline_results=json.loads((BASELINE/'results.json').read_text())
baseline_cache=Path(baseline_results['sampling']['section_cache_directory'])
placement=json.loads((HATCH/'placement.json').read_text())
manifest=json.loads((HATCH/'manifest.json').read_text())
for filename,h in manifest.items():
 assert sha(HATCH/filename)==h,(filename,'hatch manifest mismatch')
 sources[str(HATCH/filename)]=h
for src in placement['sources'].values():
 assert sha(src['path'])==src['sha256']
 sources[src['path']]=src['sha256']
for filename in ['extract.py','parameter_sampler.py','hardware.json','results.json']:
 sources[str(BASELINE/filename)]=sha(BASELINE/filename)
for path,h in baseline_results['source_hashes'].items():
 assert sha(path)==h
 sources[path]=h
hatch_solids=cq.importers.importStep(str(HATCH/'installed_hatches.step')).solids().vals()
assert len(hatch_solids)==4 and all(s.isValid() for s in hatch_solids)
for i,(s,receipt) in enumerate(zip(hatch_solids,placement['placements'])):
 assert abs(s.Volume()-receipt['volume_mm3'])<.01
 assert len(s.Faces())==receipt['face_count']
 b=s.BoundingBox()
 parts.append(dict(name=f"HATCH:{receipt['source']}:body{receipt['body_one_based']}",shape=s,bounds=[b.zmin,b.zmax]))
'''
s=s.replace('lo=min(p[',insert+'\nlo=min(p[',1)
s=s.replace("sha(O/'parameter_sampler.py')", "sha(BASELINE/'parameter_sampler.py')")
s=s.replace(" clouds=[];wiredata=[]; names=[];wiremeta=[];edge_diag=[]",''' clouds=[];wiredata=[]; names=[];wiremeta=[];edge_diag=[]
 bp=baseline_cache/f'{k:.8f}.pickle'
 baseline_loaded=bp.exists()
 if baseline_loaded:
  with bp.open('rb') as f:br=pickle.load(f)
  clouds=[br['points']];wiredata=list(br['wires']);names=list(br['names']);wiremeta=list(br['raw']);edge_diag=list(br['edge_diagnostics'])''')
s=s.replace(" for p in parts:\n  if not", " for p in parts:\n  if baseline_loaded and not p['name'].startswith('HATCH:'):continue\n  if not",1)
s=s.replace("if (O/'hardware.json').exists() and (O/'results.json').exists():", "if (BASELINE/'hardware.json').exists() and (BASELINE/'results.json').exists():")
s=s.replace("previous=json.loads((O/'results.json').read_text())", "previous=json.loads((BASELINE/'results.json').read_text())")
s=s.replace("json.loads((O/'hardware.json').read_text())", "json.loads((BASELINE/'hardware.json').read_text())")
s=s.replace("'outside_perimeter_mm':r['perimeter'],'outside_area_mm2':r['area']", "'convex_envelope_perimeter_mm':r['perimeter'],'convex_envelope_area_mm2':r['area']")
s=s.replace("r['outside_area_mm2']", "r['convex_envelope_area_mm2']")
s=s.replace('canopy installed closure assumed; do not call exact exposed wetted area','complete original hatch solids included; do not call exact exposed wetted area')
s=s.replace('canopy installed closure assumed, not a separately measured canopy solid.','all four original complete hatch solids included at feature-verified native identity.')
s=s.replace('Canopy installed closure assumed, not a separately measured canopy solid.','All four original complete hatch solids included at feature-verified native identity.')
s=s.replace('holes, cavities, canopy and slots bridged','holes, cavities, residual hatch seams and slots bridged')
s=s.replace('Open canopy/slots bridged','Complete hatches measured; remaining open slots bridged')
s=s.replace('Nose-to-FUS1 3mm reinforcement exterior linearly interpolated; XY registration unresolved.','Unregistered nose gap excluded from primary area; separate straight-bridge sensitivity only.')
s=s.replace("(O/'results.json').write_text", "R['hatches']={'count':4,'placement_receipt':str(HATCH/'placement.json'),'pose':'feature-verified native identity; nominal clearance retained','rear_interface_limit':'FUS4 mesh curved lip nominal fit checked; full rear tongue seating/penetration not certified'}\nR['baseline_envelope_area_m2']=baseline_results['wetted_area_envelope_m2']\nR['hatch_inclusive_minus_baseline_envelope_area_m2']=R['wetted_area_envelope_m2']-R['baseline_envelope_area_m2']\n(O/'results.json').write_text")
(O/'extract.py').write_text(s)
print('Created',O/'extract.py')

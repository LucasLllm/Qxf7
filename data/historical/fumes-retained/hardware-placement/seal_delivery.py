from pathlib import Path
import json,hashlib,datetime
O=Path(__file__).resolve().parent;R=O.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,d):(O/n).write_text(json.dumps(d,indent=2))
d=json.loads((O/'RESULTS.json').read_text());v=json.loads((O/'VERIFICATION.json').read_text());old=json.loads((R/'cfd-exterior-v1/hardware/RESULTS.json').read_text());byname={x['name']:x for x in old['outputs']}
place=[]
for r in d['components']:
 if r['name'] not in d['baseline_installed_names']:continue
 if 'mount_instance_index' in r:
  n=r['name'].removesuffix('_CFD_APPROXIMATE');idx=byname[n]['replaces_instance_index'];source={'retained_motor_record':n,'mount_instance_index':r['mount_instance_index']}
 else:idx=83 if r['side']=='R' else 90;source={'retained_boom_record':'tube_'+r['side']+'_outer_walls','side':r['side']}
 place.append({'name':r['name'],'obj':r['obj'],'obj_units':'m','obj_sha256':sha(r['obj']),'step':r['step'],'step_units':'mm','step_sha256':sha(r['step']),'legacy_proxy_instance_to_remove':idx,'transform_already_applied':True,'local_to_aircraft_mm':r['local_to_aircraft_mm'],'local_to_aircraft_m':r['local_to_aircraft_m'],**source})
save('PLACEMENT_AND_SUBSTITUTIONS.json',{'configuration':d['configuration'],'axes':d['axes'],'baseline':place,'combined':d['installed_baseline'],'integration_policy':'Replace legacy proxies; do not append duplicate local definitions/variants; preserve printed mounting parts. Hardware-only exact checks do not qualify merged airframe contact interfaces.'})
research=json.loads((O/'RESEARCH_RECEIPTS.json').read_text());recs=research['records'];ledger=[]
for r in recs:
 if any(x in r['requested_url'] for x in ['goods-1057','p00234','1638150063356533.jpg','913747b78f.jpg','hobbyrc.co.uk/t-motor-f90']):
  ledger.append({k:r[k] for k in ['requested_url','final_url','status','path','sha256','bytes','retrieved_utc'] if k in r})
save('SOURCE_AND_APPROXIMATION.json',{'actual_sources':ledger,'drawing_link_discovery_confirmed':all(any('1638150063356533.jpg' in u for u in r.get('images',[])) for r in recs if 'goods-1057' in r['requested_url']) and all(any('913747b78f.jpg' in u for u in r.get('images',[])) for r in recs if 'p00234' in r['requested_url']),'native_vendor_CAD_recovered':False,'source_dimensions_mm':{'F90':{'max_diameter':33.4,'seat_to_tip':34.7,'seat_to_shoulder':19.7,'shaft_nominal_M5_diameter':5,'mount_pitch_circle':19,'mount_count':4,'mount_thread':'M3'},'Avenger2812V5':{'max_diameter':33.9,'seat_to_tip':44.05,'tip_to_rear_bell':37.6,'tip_to_prop_shoulder':17,'derived_seat_to_rear_bell':44.05-37.6,'derived_seat_to_shoulder':44.05-17,'shaft_nominal_M5_diameter':5}},'assumed_parameters_mm':{'F90':{'base_diameter':24,'base_thickness':3,'neck_diameter':14,'rear_bell_offset':6.2,'full_bell_ending':18.2,'shoulder_diameter':29},'Avenger2812V5':{'base_diameter':25,'base_thickness':3.4,'neck_diameter':14,'full_bell_ending':25.5,'shoulder_diameter':30},'boom_baseline':{'circular_bore_diameter':8,'minimum_side_wall':1,'cable_cut_length':24,'cable_cut_width':5,'cable_cut_center_x':-112.46047687230817,'end_faces':'open bore / annular material end rings'}},'source_manual_policy':'Reuse retained readiness-review REPORT and retained p36 image; no restart of manual datum derivation','explicit_limitations':d['approximation_limits'],'measured_serialized_mesh_vs_STEP':{'max_bounds_difference_m':max(x['cad_mesh_bounds_max_delta_m'] for x in v['components']),'max_relative_volume_difference':max(x['cad_mesh_relative_volume_delta'] for x in v['components'])},'physical_hardware_error_bound':None,'search_outcome':'Relevant manufacturer pages/drawings accessible; no CAD links; Google interstitials, Bing unrelated results. F100 incidental page excluded from model evidence.'})
# Additional retained original manual source preservation, not a new manual reconstruction.
baseline=json.loads((O/'INPUT_BASELINE.json').read_text());ev=json.loads((R/'cfd-corrections-v1/hardware/EVIDENCE.json').read_text())
for r in ev['inputs']:
 if r['path'].endswith(('.pdf','/bh-913747b78f.jpg')):
  assert sha(r['path'])==r['sha256'];baseline[r['path']]=r['sha256']
save('INPUT_BASELINE.json',baseline);assert all(sha(p)==h for p,h in baseline.items())
# Final binding excludes this receipt itself; verify its entire recorded map immediately.
files={str(p.relative_to(O)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(O.rglob('*')) if p.is_file() and p.name!='FINAL_RECEIPT.json' and '__pycache__' not in p.parts}
save('FINAL_RECEIPT.json',{'status':'FINAL_FILES_HASH_VERIFIED','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'root':str(O),'files':files,'preserved_inputs':baseline,'verification_status':v['status'],'installed_baseline_obj_sha256':d['installed_baseline']['obj_sha256'],'scope':'17 pairs and hardware-only baseline, approximate geometry; full parent remains unmodified'})
receipt=json.loads((O/'FINAL_RECEIPT.json').read_text());assert all(sha(O/p)==r['sha256'] and (O/p).stat().st_size==r['bytes'] for p,r in receipt['files'].items());print('FINAL',len(files),'hash-bound files; preserved inputs',len(baseline));print('Pusher shoulder X mm',-663.7491136436045-(44.05-17));print('Placements',[(x['name'],x['legacy_proxy_instance_to_remove']) for x in place])

"""Independent integrated-delivery checks; --bundle validates every shipped byte."""
from pathlib import Path
import json,csv,hashlib,math,sys,zipfile
import numpy as np
D=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
load=lambda p:json.loads((D/p).read_text())

def verify_bundle():
 p=D/'stork-aero-extraction-review.zip'
 with zipfile.ZipFile(p) as z:
  assert z.testzip() is None
  names=z.namelist();assert len(names)==len(set(names))
  assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in names)
  m=json.loads(z.read('BUNDLE_HASHES.json'))
  assert set(names)==set(m)|{'BUNDLE_HASHES.json'}
  assert all(hashlib.sha256(z.read(n)).hexdigest()==h for n,h in m.items())
  assert len([n for n in names if n.endswith('.dat')])==32
  assert not any(n.lower().endswith(('.step','.stp','.stl')) for n in names)
  assert json.loads(z.read('delivery_verification.json'))['status']=='PASS'
 r=load('bundle_receipt.json');assert sha(p)==r['sha256'] and p.stat().st_size==r['bytes']
 print(json.dumps({'bundle_status':'PASS','every_member_hash_verified':True,'members':len(names),'bytes':p.stat().st_size,'sha256':sha(p)},indent=2))

def verify_workspace():
 checks={}
 def check(n,v):
  assert v,n
  checks[n]=True
 r=load('integration_receipt.json');rows=list(csv.DictReader((D/'geometry_table.csv').open()))
 check('integration_inputs_still_hash_match',all(sha(D/p)==h for p,h in r['inputs_sha256'].items()))
 check('geometry_table_hash_and_rowcount',sha(D/'geometry_table.csv')==r['geometry_table_sha256'] and len(rows)==r['rows'])
 check('all_components_integrated',{'wing','tail','fuselage','hardware','wing_tail','qualification','airframe'} <= {q['component'] for q in rows})
 check('numeric_values_finite',all(q['status']=='UNKNOWN' or math.isfinite(float(q['value'])) for q in rows))
 unknown=[q for q in rows if q['status']=='UNKNOWN']
 check('unknowns_blank_not_zero',len(unknown)>=6 and all(q['value']=='' for q in unknown))
 for s in ['aileron_start_in','aileron_end_out','tip_root_in']:
  q=[q for q in rows if q['component']=='wing' and q['station']==s]
  check('clearance_non_airfoil_'+s,bool(q) and all(x['status']=='TRUNCATED_CLEARANCE_DIAGNOSTIC_NOT_AIRFOIL' for x in q))
 v=load('extraction_verification.json')
 check('32_profiles_and_108_unchanged_source_checks',v['exported_profiles_checked']==32 and v['original_source_hash_checks']==108 and v['profile_validation_pass'] and v['original_sources_unchanged'])
 for p in v['profiles']:
  check('profile_hash_'+p['path'],sha(D/p['path'])==p['sha256'])
 fm=load('fuselage-with-hatches/manifest.json')
 check('final_fuselage_manifest_all_artifacts',all(sha(D/'fuselage-with-hatches'/p)==h for p,h in fm.items()))
 deps=load('fuselage-with-hatches/read_only_dependency_hashes.json')
 check('read_only_dependencies_unchanged',all(sha(p)==h for p,h in deps.items()))
 tv=load('tail-extraction/verification.json')
 check('tail_artifact_receipt',tv['status']=='PASS' and all(sha(D/'tail-extraction'/p)==v['sha256'] for p,v in tv['final_artifacts'].items()))
 fv=load('fuselage-with-hatches/verification.json');f=load('fuselage-with-hatches/results.json')
 check('32_fuselage_checks_and_raw_counts',fv['check_count']==32 and all(fv['checks'].values()) and fv['metrics']['raw_station_count']==42 and fv['metrics']['raw_curve_count']==1056)
 check('actual_exposed_wetted_area_explicitly_unknown',f['actual_exposed_wetted_area_m2'] is None)
 m=f['exact_matched_grid_comparison']
 check('matched_grid_difference_arithmetic',abs(m['hatch_inclusive_same_grid_convex_envelope_m2']-m['baseline_hatch_augmented_grid_convex_envelope_m2']-m['matched_grid_hatch_increase_m2'])<1e-12 and m['same_axial_grid'])
 frame=load('coordinate_frame.json');M=np.array(frame['native_to_aircraft_homogeneous'])
 check('frame_right_handed_permutation_no_translation',np.array_equal(M@np.array([1,2,3,1]),[3,1,2,1]) and abs(np.linalg.det(M[:3,:3])-1)<1e-12)
 check('nose_datum_matches_extractor',frame['nose_aircraft_x_mm']==f['datum']['nose_aircraft_x_mm'])
 w=load('wing-extraction/wing_geometry.json');t=load('tail-extraction/tail_geometry.json');arms=load('moment_arms.json')
 for name in ['exposed','gross_with_declared_centerline_continuation']:
  expected=t['planform_full_including_fin']['area_weighted_quarter_chord_aircraft_mm'][0]-w[name]['quarterchord_aft_mm']
  check('common_frame_arm_'+name,abs(arms[name]['longitudinal_arm_mm']-expected)<1e-10)
 u=load('uiuc-comparison/match_receipt.json')
 matches=list(csv.DictReader((D/'uiuc-comparison/uiuc_matches.csv').open()))
 names={Path(q['profile']).stem for q in matches}
 check('UIUC_count_and_clearance_exclusions',u['matched_profiles']==18 and len(u['excluded_extracted_profiles'])==14 and not(names & {'aileron_start_in','aileron_end_out','tip_root_in'}))
 for name in ['top','front','side']:
  check('orthographic_'+name,(D/'review-overlays'/f'{name}_outline_overlay.png').stat().st_size>0)
 report=(D/'EXTRACTION_REPORT.md').read_text()
 check('report_preserves_qualifications',all(s in report for s in ['1044.02','4.402%','NOT exact exposed','not a CG arm','31.212','Unknown installed']))
 result={'status':'PASS','check_count':len(checks),'checks':checks,'geometry_rows':len(rows),'fuselage_manifest_members':len(fm),'dependency_hash_checks':len(deps),'tail_manifest_members':len(tv['final_artifacts']),'geometry_table_sha256':sha(D/'geometry_table.csv'),'report_sha256':sha(D/'EXTRACTION_REPORT.md'),'scope':'Integrated numerical/receipt consistency only, not complete installation or flightworthiness.'}
 (D/'delivery_verification.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2))

if __name__=='__main__':
 if '--bundle' in sys.argv:verify_bundle()
 else:verify_workspace()

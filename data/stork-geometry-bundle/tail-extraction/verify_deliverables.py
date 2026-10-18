"""Verify final saved evidence; writes only to this file's own directory."""
from pathlib import Path
import json,hashlib,subprocess,sys
import numpy as np
D=Path(__file__).resolve().parent
result=subprocess.run([sys.executable,'-B',str(D/'test_tail.py')],cwd=D,text=True,capture_output=True)
(D/'tests.log').write_text(result.stdout+result.stderr)
assert result.returncode==0,'Regression or artifact tests failed; see tests.log'
j=json.loads((D/'tail_geometry.json').read_text())
receipt=json.loads((D/'source_hash_verification.json').read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert all(sha(r['path'])==r['sha256']==r['before_sha256']==r['after_sha256'] for r in receipt['sources'].values())
assert all(sha(p)==h for p,h in receipt['read_only_reference_and_script_sha256'].items())
profile_counts={}
for label,m in j['profiles'].items():
 p=D/f'{label}_140cosineSelig.dat';dat=np.loadtxt(p,skiprows=1);assert dat.shape==(140,2)
 profile_counts[label]=len(dat)
 assert abs((dat[0,1]-dat[-1,1])*m['chord_mm']-m['TE_thickness_mm'])<2e-7
np.testing.assert_allclose(np.array(j['planform_full_including_fin']['effective_MAC_LE_aircraft_mm'])+.25*np.array(j['planform_full_including_fin']['area_weighted_MAC_chord_vector_aircraft_mm']),j['planform_full_including_fin']['area_weighted_quarter_chord_aircraft_mm'],atol=1e-10)
files={p.name:{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(D.iterdir()) if p.is_file() and p.name!='verification.json'}
v={'status':'PASS','executed_regression_tests':6,'test_process_returncode':result.returncode,'all_five_original_CAD_hashes_match_pre_post_and_upstream':True,'production_script_and_references_hashes_match_execution_receipt':True,'all_profile_coordinate_counts':profile_counts,'finite_TE_caps_preserved':True,'MAC_vector_QC_LE_identity_verified':True,'aerodynamic_true_zero_unknown_preserved':j['neutral']['true_zero_relative_agreed_neutral_contour_deg'] is None,'degenerate_tip_conventional_foil_unknown_preserved':j['true_tip']['conventional_airfoil'] is None,'final_artifacts':files}
(D/'verification.json').write_text(json.dumps(v,indent=2))
print(json.dumps({k:v[k] for k in v if k!='final_artifacts'},indent=2));print('Final artifacts hashed:',len(files))

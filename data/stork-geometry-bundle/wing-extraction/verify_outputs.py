"""Read-only independent final artifact validator; no CAD/profile regeneration."""
from pathlib import Path
import hashlib,json
import numpy as np
from scipy.integrate import trapezoid
D=Path(__file__).resolve().parent
v=json.loads((D/'verification.json').read_text());g=json.loads((D/'wing_geometry.json').read_text());s=json.loads((D/'station_diagnostics.json').read_text())
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for k in ('inputs_sha256','retained_artifact_sha256'):
    for p,h in v[k].items():assert sha(p)==h,(k,p)
for p,h in v['outputs_sha256'].items():assert sha(D/p)==h,p
assert v['retained_profile_count']==27 and len(list((D/'dat').glob('*.dat')))==27
assert v['all_original_input_hashes_unchanged'] and v['retained_artifacts_unchanged']
p=np.loadtxt(D/'planform_samples.csv',delimiter=',',skiprows=1)
assert np.isfinite(p).all() and np.all(np.diff(p[:,0])>0)
y=p[:,0];c=p[:,2]-p[:,1];A=trapezoid(c,y);mac=trapezoid(c*c,y)/A;qc=trapezoid((p[:,1]+c/4)*c,y)/A
for key,value in [('both_sides_projected_area_dm2',2*A/1e4),('projected_MAC_mm',mac),('quarterchord_aft_mm',qc)]:assert abs(g['exposed'][key]-value)<1e-9,key
# Independent final refinement bounds for both reference and physical envelopes.
for kind in ('exposed','gross','physical_outer_envelope_exposed'):
    a,b=[q[kind] for q in g['convergence'][-2:]]
    assert abs(a['both_sides_projected_area_dm2']-b['both_sides_projected_area_dm2'])<.01
    assert abs(a['projected_MAC_mm']-b['projected_MAC_mm'])<.1
    assert abs(a['quarterchord_aft_mm']-b['quarterchord_aft_mm'])<.1
flags=[q for q in s['stations'] if q.get('flag')]
assert {q['section_id'] for q in flags}=={'aileron_start_in','aileron_end_out','tip_root_in'}
for q in flags:
    assert q['missing_aft_domain_relative_design_mm']>35
    assert q['nearest_cleaner_retained_section'] is not None
assert len(s['tessellation_refinement_checks'])==4
assert all(q['passed_lt_0p01mm'] for q in s['tessellation_refinement_checks'])
assert len(s['dense_STEP_tessellation_fallbacks'])>0
assert not g['neutral_certified'] and not v['all_profiles_aerodynamically_certified']
print('PASS: original/retained/output SHA256, 27 profiles, independent area/MAC/qc integration, all three convergence conventions, 3 clearance flags, 4 tessellation checks')
print('Dense STEP fallback stations:',len(s['dense_STEP_tessellation_fallbacks']))
print('Tessellation refinement max extrema delta mm:',max(q['extrema_max_delta_mm'] for q in s['tessellation_refinement_checks']))
print('Output directory:',D)

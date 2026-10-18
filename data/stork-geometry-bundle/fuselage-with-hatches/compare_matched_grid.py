"""Isolate hatch effect using exactly the same augmented axial grid on both models."""
from pathlib import Path
import json
import numpy as np
O=Path(__file__).resolve().parent
ns={'__file__':str(O/'extract.py')}
exec((O/'extract.py').read_text().split('# Regular native-datum')[0],ns)
ns['parts'][:]=[p for p in ns['parts'] if not p['name'].startswith('HATCH:')]
ns['cache']={};ns['cache_dir']=O/'baseline_augmented_grid_cache';ns['cache_dir'].mkdir(exist_ok=True)
v=np.load(O/'envelope_loft.npz')['vertices_aircraft_mm'];grid=v[:,0,0]
a,bv,bridge=ns['loft'](grid,v.shape[1])
R=json.loads((O/'results.json').read_text());primary=R['wetted_area_envelope_m2']
result={'status':'PASS','same_axial_grid':True,'same_angular_vertices':int(v.shape[1]),'same_section_count':len(grid),'baseline_original_grid_convex_envelope_m2':R['baseline_envelope_area_m2'],'baseline_hatch_augmented_grid_convex_envelope_m2':a/1e6,'hatch_inclusive_same_grid_convex_envelope_m2':primary,'matched_grid_hatch_increase_m2':primary-a/1e6,'matched_grid_hatch_increase_percent':100*(primary/(a/1e6)-1),'baseline_grid_only_change_m2':a/1e6-R['baseline_envelope_area_m2'],'baseline_nose_bridge_sensitivity_m2':bridge/1e6,'scope':'Only the convex envelope model; not exact section outer contour or exposed wetted area. Nose gap excluded from both primary values.'}
np.savez_compressed(O/'baseline_matched_grid_loft.npz',vertices_aircraft_mm=bv,segment_is_unregistered_gap=np.load(O/'envelope_loft.npz')['segment_is_unregistered_gap'])
(O/'matched_grid_comparison.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

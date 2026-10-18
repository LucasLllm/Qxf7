"""Independent saved-artifact/source verification; writes only this directory."""
from pathlib import Path
import json,csv,hashlib,sys
import numpy as np
import cadquery as cq
from OCP.BRepTools import BRepTools
O=Path(__file__).resolve().parent;B=O.parent/'fuselage-extraction';H=O.parent/'hatch-feature-work'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
R=json.loads((O/'results.json').read_text());P=json.loads((H/'placement.json').read_text())
checks={};metrics={}
def check(name,condition):
 checks[name]=bool(condition)
 assert checks[name],name
check('all_source_hashes_unchanged',all(sha(p)==h for p,h in R['source_hashes'].items()))
check('hatch_full_manifest_verified',all(sha(H/p)==h for p,h in json.loads((H/'manifest.json').read_text()).items()))
check('all_feature_constraints_rank6_identity',all(np.array_equal(np.array(p['source_to_native']),np.eye(4)) and p['constraint_jacobian_rank']==6 and not p['remaining_continuous_DoF'] for p in P['placements']))
solids=cq.importers.importStep(str(O/'installed_hatches.step')).solids().vals()
check('four_reloaded_valid_complete_hatch_solids',len(solids)==4 and all(s.isValid() for s in solids))
check('installed_hatch_export_byte_identical',sha(O/'installed_hatches.step')==sha(H/'installed_hatches.step'))
check('ten_reloaded_skin_faces',len(cq.importers.importStep(str(O/'external_skin_patches.step')).val().Faces())==10)
volume_errors=[];bound_errors=[]
for s,receipt in zip(solids,P['placements']):
 original_path=P['sources'][receipt['source']]['path']
 original=cq.importers.importStep(original_path).solids().vals()[receipt['body_one_based']-1]
 BRepTools.Clean_s(s.wrapped);BRepTools.Clean_s(original.wrapped)
 def bb(t):
  b=t.BoundingBox();return np.array([b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax])
 bound_errors.append(float(np.max(np.abs(bb(s)-bb(original)))))
 volume_errors.append(abs(s.Volume()-original.Volume()))
 check('complete_faces_'+receipt['source']+str(receipt['body_one_based']),len(s.Faces())==len(original.Faces()))
check('identity_bounds_match_original_1e-5mm',max(bound_errors)<1e-5)
check('identity_volumes_match_original_0.01mm3',max(volume_errors)<.01)
metrics.update(max_identity_bound_error_mm=max(bound_errors),max_identity_volume_error_mm3=max(volume_errors))
raw=json.loads((O/'raw_section_curves.json').read_text());xs=np.array([r['aircraft_x_mm'] for r in raw]);lo=R['datum']['nose_aircraft_x_mm'];hi=R['datum']['fuselage_aft_x_mm']
check('native_datum_50mm_grid',all(np.min(abs(xs-x))<1e-7 for x in np.arange(np.ceil(lo/50)*50,hi,50)))
check('nose_relative_50mm_grid',all(np.min(abs(xs-x))<1e-7 for x in lo+np.arange(50,hi-lo,50)))
check('true_endpoints_saved',np.min(abs(xs-lo))<1e-7 and np.min(abs(xs-hi))<1e-7)
curves=[c for r in raw for c in r['curves']]
check('raw_curves_finite',all(np.isfinite(c['points_aircraft_xyz_mm']).all() for c in curves))
check('all_four_hatches_in_raw_curves',len({c['source'] for c in curves if c['source'].startswith('HATCH:')})==4)
metric_error=[]
rows=list(csv.DictReader((O/'cross_sections_50mm.csv').open()))
for row in rows:
 rr=min(raw,key=lambda r:abs(r['aircraft_x_mm']-float(row['aircraft_x_mm'])))
 points=np.vstack([c['points_aircraft_xyz_mm'] for c in rr['curves']])
 metric_error.extend([abs(np.ptp(points[:,1])-float(row['width_mm'])),abs(np.ptp(points[:,2])-float(row['height_mm']))])
check('raw_curves_reproduce_reported_dimensions_0.03mm',max(metric_error)<.03)
metrics['max_raw_dimensions_error_mm']=max(metric_error)
npz=np.load(O/'envelope_loft.npz');v=npz['vertices_aircraft_mm'];mask=npz['segment_is_unregistered_gap']
a=v[:-1];b=np.roll(a,-1,axis=1);c=np.roll(v[1:],-1,axis=1);d=v[1:]
areas=(np.linalg.norm(np.cross(b-a,c-a),axis=2).sum(axis=1)+np.linalg.norm(np.cross(c-a,d-a),axis=2).sum(axis=1))/2
area=float(areas[~mask].sum()/1e6);bridge=float(areas[mask].sum()/1e6)
check('saved_loft_area_independently_recomputed',abs(area-R['wetted_area_envelope_m2'])<1e-12)
check('gap_sensitivity_independently_recomputed',abs(bridge-R['unresolved_nose_connection']['conditional_straight_bridge_sensitivity_m2'])<1e-12)
check('nose_gap_segments_excluded',bool(mask.any()) and R['unresolved_nose_connection']['primary_area_excludes_unregistered_connection'])
check('loft_finite',np.isfinite(v).all())
check('six_convergence_cases',len(R['convergence'])==6 and len({(c['dx_mm'],c['angular_vertices']) for c in R['convergence']})==6)
metrics.update(independent_primary_convex_envelope_m2=area,independent_gap_bridge_sensitivity_m2=bridge,raw_station_count=len(raw),raw_curve_count=len(curves))
comparison=json.loads((O/'baseline_section_comparison.json').read_text())
r80=min(comparison,key=lambda c:abs(c['aircraft_x_mm']+80))
check('verified_minus80_top_rise_regression',abs(r80['aircraft_x_mm']+80)<1e-8 and abs(r80['delta_top_mm']-47.57348)<.001)
check('inclusive_convex_area_not_decreased',all(c['delta_convex_envelope_area_mm2']>=-1e-6 for c in comparison))
metrics['minus80_top_rise_mm']=r80['delta_top_mm']
nonconvex=json.loads((O/'nonconvex_material_sections.json').read_text());skin=json.loads((O/'original_hatch_skin_arcs.json').read_text())
check('valid_nonconvex_subsets_and_open_skin_arcs_no_synthetic_closure',all(n['is_valid'] and not n['continuous_aerodynamic_outer_contour_reconstructed'] for n in nonconvex) and all(not s['closure_added'] for s in skin))
check('raw_step_reload_edges_nonempty',len(cq.importers.importStep(str(O/'raw_brep_section_edges.step')).val().Edges())>0)
check('sampler_regression_suite_passed',json.loads((O/'tolerance_validation.json').read_text())['status']=='PASS')
matched=json.loads((O/'matched_grid_comparison.json').read_text());baseline_npz=np.load(O/'baseline_matched_grid_loft.npz');bv=baseline_npz['vertices_aircraft_mm'];bm=baseline_npz['segment_is_unregistered_gap']
ba=bv[:-1];bb=np.roll(ba,-1,axis=1);bc=np.roll(bv[1:],-1,axis=1);bd=bv[1:]
bareas=(np.linalg.norm(np.cross(bb-ba,bc-ba),axis=2).sum(axis=1)+np.linalg.norm(np.cross(bc-ba,bd-ba),axis=2).sum(axis=1))/2
check('matched_baseline_exact_same_grid',np.array_equal(bv[:,:,0],v[:,:,0]) and np.array_equal(bm,mask) and bv.shape==v.shape)
check('matched_baseline_area_recomputed',abs(float(bareas[~bm].sum()/1e6)-matched['baseline_hatch_augmented_grid_convex_envelope_m2'])<1e-12)
check('matched_grid_hatch_difference_recomputed',abs(area-float(bareas[~bm].sum()/1e6)-matched['matched_grid_hatch_increase_m2'])<1e-12)
metrics['matched_grid_hatch_increase_m2']=matched['matched_grid_hatch_increase_m2']
metrics['nonconvex_all_closed_loops_included_station_count']=sum(n['excluded_loop_count']==0 for n in nonconvex)
metrics['nonconvex_partial_station_count']=sum(n['excluded_loop_count']>0 for n in nonconvex)
metrics['nonconvex_empty_valid_union_station_count']=sum(not n['contours'] for n in nonconvex)
# Bind actual read-only baseline caches as dependencies after measurements.
cache_dir=Path(json.loads((B/'results.json').read_text())['sampling']['section_cache_directory'])
deps={str(p):sha(p) for p in cache_dir.glob('*.pickle')}
deps.update(R['source_hashes'])
(O/'read_only_dependency_hashes.json').write_text(json.dumps(deps,indent=2))
check('dependency_hashes_rechecked',all(sha(p)==h for p,h in deps.items()))
metrics['baseline_cache_files_hash_bound']=len(list(cache_dir.glob('*.pickle')))
verification={'status':'PASS','checks':checks,'check_count':len(checks),'metrics':metrics,'limitations':['Convex loft area is not actual section outer contour or exact exposed wetted area.','Nonconvex material section union preserves cavities/islands, not a continuous aerodynamic skin. Original hatch skin arcs remain open; no closure invented.','Rear FUS4 complete tongue seating/penetration not certified.']}
(O/'verification.json').write_text(json.dumps(verification,indent=2))
print(json.dumps(verification,indent=2))

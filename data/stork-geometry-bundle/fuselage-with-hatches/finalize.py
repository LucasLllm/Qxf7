"""Finalize wording, usable index and final self-excluding artifact receipt."""
from pathlib import Path
import json,hashlib
O=Path(__file__).resolve().parent
R=json.loads((O/'results.json').read_text());V=json.loads((O/'verification.json').read_text());T=json.loads((O/'tolerance_validation.json').read_text())
C=json.loads((O/'baseline_section_comparison.json').read_text())
N=json.loads((O/'nonconvex_material_sections.json').read_text())
coverage={'station_count':len(N),'all_closed_loops_included_station_count':sum(n['excluded_loop_count']==0 for n in N),'partial_invalid_loop_station_count':sum(n['excluded_loop_count']>0 for n in N),'empty_valid_union_station_count':sum(not n['contours'] for n in N),'excluded_invalid_loop_count':sum(n['excluded_loop_count'] for n in N),'continuous_aerodynamic_outer_contour_reconstructed':False,'interpretation':'A partial diagnostic only. Empty/partial unions do NOT indicate absent source material; all original curves retained. No repair or seam closure.'}
(O/'nonconvex_section_coverage.json').write_text(json.dumps(coverage,indent=2))
R['convex_lateral_envelope_area_m2']=R['wetted_area_envelope_m2']
R['actual_exposed_wetted_area_m2']=None
R['actual_continuous_section_outer_contour_status']='Not reconstructed across physical seam clearance, disconnected material islands, or unregistered nose gap. Real raw curves and measured open external hatch skin arcs saved; no invented closure.'
R['legacy_field_warning']='wetted_area_envelope_m2 is retained for baseline schema compatibility only; it means convex lateral section-envelope loft approximation, NOT exact exposed wetted area.'
R['nonconvex_diagnostic']={'method':'Per-source valid closed-loop even/odd nesting, then planar union; retain cavities and disconnected islands, do not repair invalid loops or bridge open edges.','artifact':'nonconvex_material_sections.json','meaning':'Physical material section union diagnostic, not certified continuous aerodynamic outer skin. Open original outer hatch skin arcs are separately retained.','wetted_area_inferred':False}
R['nonconvex_diagnostic']['coverage']=coverage
R['raw_sections']={'raw_curve_file':'raw_section_curves.json','exact_brep_edges':'raw_brep_section_edges.step','exact_brep_step_frame':'native XYZ; section coordinate is native Z. JSON points are aircraft XYZ. installed_hatches.step and external_skin_patches.step also remain native XYZ.','aircraft_xyz':'native Z,X,Y at common STEP zero','every_50mm_native_and_nose_relative':True,'extra_regression_station_mm':-80.0}
R['matched_resolution_comparison']={'baseline_convex_lateral_envelope_m2':R['baseline_envelope_area_m2'],'hatch_inclusive_convex_lateral_envelope_m2':R['wetted_area_envelope_m2'],'difference_m2':R['hatch_inclusive_minus_baseline_envelope_area_m2'],'relative_increase_percent':100*(R['wetted_area_envelope_m2']/R['baseline_envelope_area_m2']-1),'dx_mm':2.5,'angular_vertices':256,'comparison_is_same_model_same_grid_resolution':True,'warning':'Hatch endpoint-adjacent stations are additionally retained, so section counts differ. This is model sensitivity, not exact skin-area gain.'}
M=json.loads((O/'matched_grid_comparison.json').read_text())
R['exact_matched_grid_comparison']=M
R['verification_file']='verification.json';R['sampler_refinement_validation']='tolerance_validation.json'
(O/'results.json').write_text(json.dumps(R,indent=2))
gap=R['unresolved_nose_connection'];r80=min(C,key=lambda z:abs(z['aircraft_x_mm']+80))
readme=f'''# Hatch-inclusive fuselage extraction — executed and verified

## Outcome

All **four complete original physical hatch solids** are included at their **feature-verified native identity**. These are not an assumed canopy closure: `hatch-feature-work/placement.json` is verified against its complete manifest and source hashes, all four constraint ranks are 6, and the local installed STEP is byte-identical to the hash-bound parent export. It reloads as four valid complete solids. Tongues, bores, latches and real nominal clearances are retained. No original or sibling worker files were written.

Aircraft `(x,y,z) = (native Z,native X,native Y)` in mm at the common STEP origin. **No wing-LE subtraction**. Physical axial bounds **{R['datum']['nose_aircraft_x_mm']:.9f} to {R['datum']['fuselage_aft_x_mm']:.9f} mm**, length **{R['datum']['length_mm']:.9f} mm**. True endpoint stations are retained, with global limit cuts evaluated 0.002 mm inward and that evaluated plane recorded; finite end faces are not invented.

## Matched-resolution envelope comparison

| Quantity | Value |
|---|---:|
| Baseline, no hatch CAD: convex lateral envelope | {R['baseline_envelope_area_m2']:.12f} m² |
| Four real hatches included: convex lateral envelope | {R['wetted_area_envelope_m2']:.12f} m² |
| Difference within this envelope model | {R['hatch_inclusive_minus_baseline_envelope_area_m2']:.12f} m² |
| Relative increase | {R['matched_resolution_comparison']['relative_increase_percent']:.6f}% |
| Unregistered nose straight-bridge sensitivity, separately | {gap['conditional_straight_bridge_sensitivity_m2']:.12f} m² |
| Conditional model including that straight bridge | {gap['conditional_envelope_with_bridge_m2']:.12f} m² |

Both original-resolution comparisons use 2.5 mm axial / 256 angular-vertex loft resolution, retaining part endpoint-adjacent stations (the hatch-inclusive case adds hatch boundaries). To isolate that small grid effect, `compare_matched_grid.py` also reruns the **baseline on exactly the same 419-section axial grid** as the hatch-inclusive case:

- Same-grid baseline envelope: **{M['baseline_hatch_augmented_grid_convex_envelope_m2']:.12f} m²**.
- Same-grid hatch-only model increase: **{M['matched_grid_hatch_increase_m2']:.12f} m² ({M['matched_grid_hatch_increase_percent']:.6f}%)**.
- Baseline grid-only difference: **{M['baseline_grid_only_change_m2']:.12f} m²**.

Both saved lofts and their common gap mask are independently re-triangulated in verification. The six full dx=10/5/2.5 mm × N=128/256 cases are in `results.json`. Last axial change **{100*R['convergence_last_axial_relative_change']:.6f}%**, angular change **{100*R['convergence_last_angular_relative_change']:.6f}%**: these are discretization sensitivities within an approximation, **not uncertainty bounds or a claim of full convergence**.

The unresolved nose interval **{gap['intervals_aircraft_x_mm']} mm** has **no fabricated rings and contributes no area to the primary estimate**. Only the separately labeled hypothetical straight-bridge sensitivity crosses it. Finite nose/aft and gap-facing end caps are omitted. Buried wing/tail/skid contact patches are not subtracted. Hardware is excluded from fuselage area and its validated baseline cache is reused read-only; native-axis physical-part silhouettes are not installed drag/blockage areas. Integral FUS6 ventral geometry remains included; the separate fin-tip, wings/tails, unspecified motor/propeller and modifier bodies remain excluded.

**A convex section envelope is not the actual section outer contour, and its loft is not exact exposed wetted area.** It convexifies remaining slots, concavity and real hatch seam clearances, ignores cavities as extra skin, and does not establish watertightness. `actual_exposed_wetted_area_m2` is explicitly null. The old `wetted_area_envelope_m2` key is compatibility-only and has the same approximate meaning. The 10-face hatch patch subset area is **not** added to any envelope area.

## Actual curves and nonconvex attempt

- `cross_sections_50mm.csv`: **41 stations**, both common-native-datum and nose-relative 50 mm grids plus true endpoints; width/height from real section extrema; perimeter and area explicitly named **convex_envelope**, not actual outer skin.
- `raw_section_curves.json`: **{V['metrics']['raw_station_count']} stations** including extra x=−80 mm regression; every individual actual BRep-plane edge (ordered native-parameter samples with edge/source IDs and exact edge lengths) and actual mesh-plane polylines, including open curves. Aircraft XYZ is saved for every point. `raw_brep_section_edges.step` preserves corresponding actual smooth edge geometry **in native XYZ** (its section coordinate is native Z); mesh sections stay source triangle intersections in JSON. `installed_hatches.step` and `external_skin_patches.step` likewise stay in native XYZ. JSON point arrays and loft vertices are aircraft XYZ.
- `section_loops.json`: genuine closed source section loops and exact wire perimeter metadata separately from the convex envelopes. No raw-loop perimeter is labeled as exposed skin.
- `original_hatch_skin_arcs.json`: actual intersections with the ten **untouched original main outer hatch BSpline faces**, intentionally open where appropriate. No artificial closing edge is added. `external_skin_patches.step` is the unchanged parent patch export.
- `nonconvex_material_sections.json`: reproducible nonconvex union of valid closed physical material sections, with even/odd nested cavity subtraction per source. Cavities, disconnected islands and seams are retained. Invalid/zero-area loops are explicitly excluded from this diagnostic, never repaired or removed from the raw curves. Coverage: **{coverage['all_closed_loops_included_station_count']}/{coverage['station_count']} stations** have all closed loops included; **{coverage['partial_invalid_loop_station_count']} stations are partial**, and **{coverage['empty_valid_union_station_count']} have no valid-union polygon**. Those empty/partial unions do not mean absent source material. Source-tolerance-scale self-intersections in sampled loops are retained diagnostically; they are not silently repaired. See `nonconvex_section_coverage.json`. This is a **partial material-boundary diagnostic**, not a unique continuous aerodynamic outer skin. Open source edges cannot support a full closed exterior reconstruction without additional seam/skin choices; that unsupported closure is deliberately not invented. No nonconvex wetted-area estimate is asserted.
- `baseline_section_comparison.csv` / `.json`: actual width, height and section top changes plus separately named convex area/perimeter comparison. At x=−80 mm, the full registered baseline vs four-hatch section top increase is **{r80['delta_top_mm']:.9f} mm** (matching independently verified hatch evidence).

## Verification and limitations

`verification.json`: **{V['check_count']} checks PASS**. This includes original and evidence hashes, four-solid and ten-face reloads, original per-body face counts/volumes/bounds, raw curve dimensions, grids/endpoints, −80 mm regression, reloaded section-edge STEP, independent saved-loft triangulation and gap mask, and hash-bound read-only baseline caches. Maximum native identity bound difference **{V['metrics']['max_identity_bound_error_mm']:.6g} mm**; maximum volume difference **{V['metrics']['max_identity_volume_error_mm3']:.6g} mm³**. Raw widths/heights agree to **{V['metrics']['max_raw_dimensions_error_mm']:.6g} mm**.

`tests.log` and `tolerance_validation.json`: nine real stations (including the original failing arc-length-inversion plane) independently resampled at 0.0025 mm checked deviation / 0.35 mm maximum chord, plus periodic-circle and missing-gap regressions. Maximum convex-area relative change **{T['max_refined_relative_area_change']:.6g}**, maximum dimension change **{T['max_refined_dimension_change_mm']:.6g} mm**. Edge-native parameter evaluation reuses the finished baseline sampler without modifying it; checked chord probes are not a certified global Hausdorff guarantee.

Nominal placement is feature-verified, not a zero-clearance manufactured fit. Rear FUS4 curved-lip mesh nominal fit is supported by its receipt; **full rear tongue trimmed-plane seating and mesh/solid penetration remain uncertified**. No CFD or flightworthiness claim.

## Files / reproduce

All files in this directory are task-local. `build_extractor.py` derives `extract.py` from the finished baseline read-only, redirects hardware/cache reads appropriately and adds receipt-verified complete hatches. The extraction imports baseline `parameter_sampler.py` read-only. Commands (run with the fumes research interpreter and `-B` to avoid sibling bytecode writes):

```sh
/Users/lucasliu/.hermes/profiles/fumes/research-venv/bin/python -B {O}/build_extractor.py
/Users/lucasliu/.hermes/profiles/fumes/research-venv/bin/python -B {O}/extract.py
/Users/lucasliu/.hermes/profiles/fumes/research-venv/bin/python -B {O}/finish.py
/Users/lucasliu/.hermes/profiles/fumes/research-venv/bin/python -B {O}/test_extraction.py
/Users/lucasliu/.hermes/profiles/fumes/research-venv/bin/python -B {O}/verify.py
/Users/lucasliu/.hermes/profiles/fumes/research-venv/bin/python -B {O}/finalize.py
```

Diagnostic images: `hatch_comparison_diagnostics.png` (real hatch blue, fuselage grey, inclusive convex red, baseline convex green), `nonconvex_diagnostics.png` (material boundaries and original open skin arcs), `section_diagnostics.png`, `envelope_profiles.png`. `envelope_loft.npz` includes the explicit unresolved-gap segment mask. `read_only_dependency_hashes.json` binds baseline cache and all source dependencies. `manifest.json` binds all settled local artifacts except itself and its verification receipt; `manifest_verification.json` records the actual final recheck. Regenerate those receipts only after all writes/processes are complete.
'''
(O/'README.md').write_text(readme)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
# Exclude finalizer's potentially still-open redirect log. Manifest verifier is separate.
excluded={'manifest.json','manifest_verification.json','finalize.log'}
files={str(p.relative_to(O)):sha(p) for p in sorted(O.rglob('*')) if p.is_file() and p.name not in excluded}
(O/'manifest.json').write_text(json.dumps(files,indent=2))
verified=all(sha(O/p)==h for p,h in files.items())
deps=json.loads((O/'read_only_dependency_hashes.json').read_text());unchanged=all(sha(Path(p))==h for p,h in deps.items())
assert verified and unchanged
receipt={'status':'PASS','local_artifact_count':len(files),'dependency_count':len(deps),'local_hashes_verified':verified,'read_only_dependency_hashes_verified':unchanged,'manifest_sha256':sha(O/'manifest.json')}
(O/'manifest_verification.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt,indent=2))

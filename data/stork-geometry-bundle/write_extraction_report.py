"""Render the checked derived geometry review; no new CAD transformations."""
from pathlib import Path
import json,csv
D=Path(__file__).resolve().parent
load=lambda p:json.loads((D/p).read_text())
w=load('wing-extraction/wing_geometry.json');t=load('tail-extraction/tail_geometry.json')
f=load('fuselage-with-hatches/results.json');a=load('moment_arms.json');v=load('extraction_verification.json')
assert v['profile_validation_pass'] and v['original_sources_unchanged']
m=f['exact_matched_grid_comparison'];fv=load('fuselage-with-hatches/verification.json')
u=load('uiuc-comparison/match_receipt.json')
lines=['# Stork aerodynamic geometry — checked provisional engineering dataset','',
'## Scope and status','',
'The extraction/review deliverables are integrated. This is NOT a complete installed-aircraft model, an aerodynamic performance prediction or a flightworthiness finding. Manufacturing CAD remained unchanged. No CFD, hardware deployment or physical tests were performed. Unknown installed positions and control neutral remain unknown.','',
'Aircraft axes: **x aft, y right, z up**, common STEP datum; native mapping `(x,y,z)=(Z,X,Y)`. These are not nose-relative or wing-LE-relative coordinates unless explicitly labeled.','',
'## Selected geometric results','',
'| Quantity | Value | Convention |','|---|---:|---|',
f"| Span | {w['span_mm']:.2f} mm | Feature-registered mirrored wing |",
'| Nose to pusher mounting face | 1000.00 mm | Separate reference, not overall length |',
'| Nose to rearmost fixed-tail geometry | 1044.02 mm | Original +4.402% length-gate failure retained |']
for name,label in [('exposed','Exposed reference envelope'),('gross_with_declared_centerline_continuation','Gross reference envelope'),('physical_outer_envelope_exposed','Physical exposed chord envelope')]:
 q=w[name]
 lines += [f"| {label}: area | {q['both_sides_projected_area_dm2']:.3f} dm² | Aircraft-xy projection |",f"| {label}: MAC | {q['projected_MAC_mm']:.2f} mm | Geometric convention, not aerodynamic centre |"]
lines += [f"| Physical occupied wing projection | {w['physical_occupied_projection_both_sides_dm2']:.3f} dm² | Preserves disjoint chordwise projection intervals |"]
for name in ['exposed','gross_with_declared_centerline_continuation']:
 lines += [f"| Wing-to-tail longitudinal arm: {name} | {a[name]['longitudinal_arm_mm']:.2f} mm | Bilateral geometric quarter-chord x difference; not a CG arm |"]
lines += [f"| V-tail cant | {t['basis']['dihedral_cant_above_horizontal_deg']:.3f}° | y-z projection; full 3D basis retained |",f"| Tail root chord | {t['profiles']['root']['chord_mm']:.2f} mm | Complete profile .61 mm from mount plane |",f"| Hatch-inclusive fuselage convex lateral envelope | {f['convex_lateral_envelope_area_m2']:.4f} m² | NOT exact exposed wetted area; unregistered nose gap omitted |",f"| Same-grid hatchless baseline envelope | {m['baseline_hatch_augmented_grid_convex_envelope_m2']:.4f} m² | Identical {m['same_section_count']}-station axial grid |",f"| Hatch-induced envelope-model increase | {m['matched_grid_hatch_increase_m2']:.5f} m² ({m['matched_grid_hatch_increase_percent']:.3f}%) | Model sensitivity, not added actual skin area |",f"| Hypothetical nose-gap straight bridge | {f['unresolved_nose_connection']['conditional_straight_bridge_sensitivity_m2']:.6f} m² | Separately reported; excluded from primary estimate |"]
lines += ['', '## Wing area and profile interpretation','',
'The exposed/gross reference envelopes use original inboard design support plus physical outboard extrema. Gross additionally extrapolates a rectangular centre carry-through: this is not hidden physical wing CAD. Physical exterior-envelope area and gap-preserving occupied projection are separate outputs. Historical coarse 31.212 dm² is retained in the earlier gate record; the refined gross convention is reported above. The published 31 dm² reference and historical 24 dm² reference remain distinct.','',
'All 27 wing and five tail Selig profiles contain exactly 140 chord-normalized cosine-spaced coordinates. Not all are usable conventional airfoils: clearance, winglet and fin diagnostics are explicitly qualified. Three truncated wing cuts (`aileron_start_in`, `aileron_end_out`, `tip_root_in`) carry non-airfoil status in the integrated table. Saved control pose is not independently established aerodynamic neutral.','',
'Dense wing integration detected incomplete exact kernel intersections. At 49 stations an audited watertight tessellation of the same physical STEP solid was used; refinement and extrema checks are retained. No replacement solid was substituted.','',
'## Hatch-inclusive fuselage evidence','',
'Four complete real hatch solids are installed at feature-recovered native identity with rank-6 constraints, rather than merely trusting saved coordinates. Exact original hatch skin arcs and individual source section curves are preserved, including open curves; no unsupported continuous outer skin is invented.','',
f"There are 41 tabulated endpoint/50-mm stations across common-datum and nose-relative grids, plus the x=-80 mm regression: {fv['metrics']['raw_station_count']} raw stations and {fv['metrics']['raw_curve_count']} actual curves. The -80 mm top rise is {fv['metrics']['minus80_top_rise_mm']:.5f} mm.",'',
f"The nonconvex material-union diagnostic is partial: {fv['metrics']['nonconvex_all_closed_loops_included_station_count']} stations include all closed loops, {fv['metrics']['nonconvex_partial_station_count']} have excluded invalid sampled loops, and {fv['metrics']['nonconvex_empty_valid_union_station_count']} have no valid-union polygon. Empty/partial unions do not imply absent material. These diagnostics are not a reconstructed aerodynamic skin.",'',
f"Envelope axial refinement changed area by {100*f['convergence_last_axial_relative_change']:.3f}%; angular refinement by {100*f['convergence_last_angular_relative_change']:.3f}%. These are model discretization sensitivities, not a physical uncertainty bound or proof of full convergence. Exact exposed wetted area is explicitly unknown.",'',
'## Verification and comparisons','',
f"- {v['original_source_hash_checks']} original source hashes checked, with no changes; {v['exported_profiles_checked']} exported profiles pass independent format/cosine-grid/contour checks.",
'- Root regression suite: 15 passing tests. Tail suite: six passing tests. Wing dense-section regressions and independent area/MAC/quarter-chord verifier passed.',
f"- Hatch-inclusive verifier: {fv['check_count']} checks passed, including reloaded solids/skin faces, independent loft triangulation, nose-gap masking and exactly matched baseline grid. Nine real-section sampler refinement regressions are retained.",
f"- UIUC: {u['matched_profiles']} extracted sections ranked; {len(u['excluded_extracted_profiles'])} excluded. Numerical shape similarity is not intended-airfoil identification or performance evidence.",
'- Original >2% overall-length gate failure remains preserved. Continued extraction was explicitly authorized; this did not turn the failed gate into a pass.','',
'## Reading and reproducing the delivery','',
'Use `geometry_table.csv` for long-form quantities, units, status and source paths. Read `EXTRACTION_LIMITATIONS.md` and the leaf READMEs before simulation. `BUNDLE_HASHES.json` is the portable review-bundle content authority; leaf manifests describe the full retained workspace and may reference heavy files intentionally not shipped. Source CAD, caches and large exact section-edge STEP remain in the retained licensed workspace. Portable raw section JSON and diagnostics are included. Reproduction requires that workspace and the recorded dependencies, not just this ZIP.','',
(D/'EXTRACTION_LIMITATIONS.md').read_text()]
(D/'EXTRACTION_REPORT.md').write_text('\n'.join(lines)+'\n')
print('Wrote checked provisional geometry report')

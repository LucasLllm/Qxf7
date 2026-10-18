# Hatch-inclusive fuselage extraction — executed and verified

## Outcome

All **four complete original physical hatch solids** are included at their **feature-verified native identity**. These are not an assumed canopy closure: `hatch-feature-work/placement.json` is verified against its complete manifest and source hashes, all four constraint ranks are 6, and the local installed STEP is byte-identical to the hash-bound parent export. It reloads as four valid complete solids. Tongues, bores, latches and real nominal clearances are retained. No original or sibling worker files were written.

Aircraft `(x,y,z) = (native Z,native X,native Y)` in mm at the common STEP origin. **No wing-LE subtraction**. Physical axial bounds **-336.250886456 to 657.549775411 mm**, length **993.800661868 mm**. True endpoint stations are retained, with global limit cuts evaluated 0.002 mm inward and that evaluated plane recorded; finite end faces are not invented.

## Matched-resolution envelope comparison

| Quantity | Value |
|---|---:|
| Baseline, no hatch CAD: convex lateral envelope | 0.364478143001 m² |
| Four real hatches included: convex lateral envelope | 0.382499929239 m² |
| Difference within this envelope model | 0.018021786238 m² |
| Relative increase | 4.944545% |
| Unregistered nose straight-bridge sensitivity, separately | 0.000974524697 m² |
| Conditional model including that straight bridge | 0.383474453936 m² |

Both original-resolution comparisons use 2.5 mm axial / 256 angular-vertex loft resolution, retaining part endpoint-adjacent stations (the hatch-inclusive case adds hatch boundaries). To isolate that small grid effect, `compare_matched_grid.py` also reruns the **baseline on exactly the same 419-section axial grid** as the hatch-inclusive case:

- Same-grid baseline envelope: **0.364593780084 m²**.
- Same-grid hatch-only model increase: **0.017906149155 m² (4.911260%)**.
- Baseline grid-only difference: **0.000115637083 m²**.

Both saved lofts and their common gap mask are independently re-triangulated in verification. The six full dx=10/5/2.5 mm × N=128/256 cases are in `results.json`. Last axial change **0.884878%**, angular change **0.113703%**: these are discretization sensitivities within an approximation, **not uncertainty bounds or a claim of full convergence**.

The unresolved nose interval **[[-249.25088625639518, -246.25088645639661]] mm** has **no fabricated rings and contributes no area to the primary estimate**. Only the separately labeled hypothetical straight-bridge sensitivity crosses it. Finite nose/aft and gap-facing end caps are omitted. Buried wing/tail/skid contact patches are not subtracted. Hardware is excluded from fuselage area and its validated baseline cache is reused read-only; native-axis physical-part silhouettes are not installed drag/blockage areas. Integral FUS6 ventral geometry remains included; the separate fin-tip, wings/tails, unspecified motor/propeller and modifier bodies remain excluded.

**A convex section envelope is not the actual section outer contour, and its loft is not exact exposed wetted area.** It convexifies remaining slots, concavity and real hatch seam clearances, ignores cavities as extra skin, and does not establish watertightness. `actual_exposed_wetted_area_m2` is explicitly null. The old `wetted_area_envelope_m2` key is compatibility-only and has the same approximate meaning. The 10-face hatch patch subset area is **not** added to any envelope area.

## Actual curves and nonconvex attempt

- `cross_sections_50mm.csv`: **41 stations**, both common-native-datum and nose-relative 50 mm grids plus true endpoints; width/height from real section extrema; perimeter and area explicitly named **convex_envelope**, not actual outer skin.
- `raw_section_curves.json`: **42 stations** including extra x=−80 mm regression; every individual actual BRep-plane edge (ordered native-parameter samples with edge/source IDs and exact edge lengths) and actual mesh-plane polylines, including open curves. Aircraft XYZ is saved for every point. `raw_brep_section_edges.step` preserves corresponding actual smooth edge geometry **in native XYZ** (its section coordinate is native Z); mesh sections stay source triangle intersections in JSON. `installed_hatches.step` and `external_skin_patches.step` likewise stay in native XYZ. JSON point arrays and loft vertices are aircraft XYZ.
- `section_loops.json`: genuine closed source section loops and exact wire perimeter metadata separately from the convex envelopes. No raw-loop perimeter is labeled as exposed skin.
- `original_hatch_skin_arcs.json`: actual intersections with the ten **untouched original main outer hatch BSpline faces**, intentionally open where appropriate. No artificial closing edge is added. `external_skin_patches.step` is the unchanged parent patch export.
- `nonconvex_material_sections.json`: reproducible nonconvex union of valid closed physical material sections, with even/odd nested cavity subtraction per source. Cavities, disconnected islands and seams are retained. Invalid/zero-area loops are explicitly excluded from this diagnostic, never repaired or removed from the raw curves. Coverage: **7/42 stations** have all closed loops included; **35 stations are partial**, and **13 have no valid-union polygon**. Those empty/partial unions do not mean absent source material. Source-tolerance-scale self-intersections in sampled loops are retained diagnostically; they are not silently repaired. See `nonconvex_section_coverage.json`. This is a **partial material-boundary diagnostic**, not a unique continuous aerodynamic outer skin. Open source edges cannot support a full closed exterior reconstruction without additional seam/skin choices; that unsupported closure is deliberately not invented. No nonconvex wetted-area estimate is asserted.
- `baseline_section_comparison.csv` / `.json`: actual width, height and section top changes plus separately named convex area/perimeter comparison. At x=−80 mm, the full registered baseline vs four-hatch section top increase is **47.573479616 mm** (matching independently verified hatch evidence).

## Verification and limitations

`verification.json`: **32 checks PASS**. This includes original and evidence hashes, four-solid and ten-face reloads, original per-body face counts/volumes/bounds, raw curve dimensions, grids/endpoints, −80 mm regression, reloaded section-edge STEP, independent saved-loft triangulation and gap mask, and hash-bound read-only baseline caches. Maximum native identity bound difference **9.12337e-11 mm**; maximum volume difference **0.00197717 mm³**. Raw widths/heights agree to **2.84217e-14 mm**.

`tests.log` and `tolerance_validation.json`: nine real stations (including the original failing arc-length-inversion plane) independently resampled at 0.0025 mm checked deviation / 0.35 mm maximum chord, plus periodic-circle and missing-gap regressions. Maximum convex-area relative change **1.58154e-05**, maximum dimension change **0.00063712 mm**. Edge-native parameter evaluation reuses the finished baseline sampler without modifying it; checked chord probes are not a certified global Hausdorff guarantee.

Nominal placement is feature-verified, not a zero-clearance manufactured fit. Rear FUS4 curved-lip mesh nominal fit is supported by its receipt; **full rear tongue trimmed-plane seating and mesh/solid penetration remain uncertified**. No CFD or flightworthiness claim.

## Files / reproduce

All files in this directory are task-local. `build_extractor.py` derives `extract.py` from the finished baseline read-only, redirects hardware/cache reads appropriately and adds receipt-verified complete hatches. The extraction imports baseline `parameter_sampler.py` read-only. Commands (run with the fumes research interpreter and `-B` to avoid sibling bytecode writes):

```sh
/Users/lucasliu/.hermes/profiles/fumes/research-venv/bin/python -B /Users/lucasliu/.hermes/profiles/fumes/notes/stork-development/stork-aero-geometry/fuselage-with-hatches/build_extractor.py
/Users/lucasliu/.hermes/profiles/fumes/research-venv/bin/python -B /Users/lucasliu/.hermes/profiles/fumes/notes/stork-development/stork-aero-geometry/fuselage-with-hatches/extract.py
/Users/lucasliu/.hermes/profiles/fumes/research-venv/bin/python -B /Users/lucasliu/.hermes/profiles/fumes/notes/stork-development/stork-aero-geometry/fuselage-with-hatches/finish.py
/Users/lucasliu/.hermes/profiles/fumes/research-venv/bin/python -B /Users/lucasliu/.hermes/profiles/fumes/notes/stork-development/stork-aero-geometry/fuselage-with-hatches/test_extraction.py
/Users/lucasliu/.hermes/profiles/fumes/research-venv/bin/python -B /Users/lucasliu/.hermes/profiles/fumes/notes/stork-development/stork-aero-geometry/fuselage-with-hatches/verify.py
/Users/lucasliu/.hermes/profiles/fumes/research-venv/bin/python -B /Users/lucasliu/.hermes/profiles/fumes/notes/stork-development/stork-aero-geometry/fuselage-with-hatches/finalize.py
```

Diagnostic images: `hatch_comparison_diagnostics.png` (real hatch blue, fuselage grey, inclusive convex red, baseline convex green), `nonconvex_diagnostics.png` (material boundaries and original open skin arcs), `section_diagnostics.png`, `envelope_profiles.png`. `envelope_loft.npz` includes the explicit unresolved-gap segment mask. `read_only_dependency_hashes.json` binds baseline cache and all source dependencies. `manifest.json` binds all settled local artifacts except itself and its verification receipt; `manifest_verification.json` records the actual final recheck. Regenerate those receipts only after all writes/processes are complete.

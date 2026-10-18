# Stork aerodynamic geometry — checked provisional engineering dataset

## Scope and status

The extraction/review deliverables are integrated. This is NOT a complete installed-aircraft model, an aerodynamic performance prediction or a flightworthiness finding. Manufacturing CAD remained unchanged. No CFD, hardware deployment or physical tests were performed. Unknown installed positions and control neutral remain unknown.

Aircraft axes: **x aft, y right, z up**, common STEP datum; native mapping `(x,y,z)=(Z,X,Y)`. These are not nose-relative or wing-LE-relative coordinates unless explicitly labeled.

## Selected geometric results

| Quantity | Value | Convention |
|---|---:|---|
| Span | 1620.54 mm | Feature-registered mirrored wing |
| Nose to pusher mounting face | 1000.00 mm | Separate reference, not overall length |
| Nose to rearmost fixed-tail geometry | 1044.02 mm | Original +4.402% length-gate failure retained |
| Exposed reference envelope: area | 27.159 dm² | Aircraft-xy projection |
| Exposed reference envelope: MAC | 191.78 mm | Geometric convention, not aerodynamic centre |
| Gross reference envelope: area | 31.245 dm² | Aircraft-xy projection |
| Gross reference envelope: MAC | 195.74 mm | Geometric convention, not aerodynamic centre |
| Physical exposed chord envelope: area | 27.127 dm² | Aircraft-xy projection |
| Physical exposed chord envelope: MAC | 191.53 mm | Geometric convention, not aerodynamic centre |
| Physical occupied wing projection | 27.121 dm² | Preserves disjoint chordwise projection intervals |
| Wing-to-tail longitudinal arm: exposed | 504.16 mm | Bilateral geometric quarter-chord x difference; not a CG arm |
| Wing-to-tail longitudinal arm: gross_with_declared_centerline_continuation | 505.51 mm | Bilateral geometric quarter-chord x difference; not a CG arm |
| V-tail cant | 35.093° | y-z projection; full 3D basis retained |
| Tail root chord | 162.29 mm | Complete profile .61 mm from mount plane |
| Hatch-inclusive fuselage convex lateral envelope | 0.3825 m² | NOT exact exposed wetted area; unregistered nose gap omitted |
| Same-grid hatchless baseline envelope | 0.3646 m² | Identical 419-station axial grid |
| Hatch-induced envelope-model increase | 0.01791 m² (4.911%) | Model sensitivity, not added actual skin area |
| Hypothetical nose-gap straight bridge | 0.000975 m² | Separately reported; excluded from primary estimate |

## Wing area and profile interpretation

The exposed/gross reference envelopes use original inboard design support plus physical outboard extrema. Gross additionally extrapolates a rectangular centre carry-through: this is not hidden physical wing CAD. Physical exterior-envelope area and gap-preserving occupied projection are separate outputs. Historical coarse 31.212 dm² is retained in the earlier gate record; the refined gross convention is reported above. The published 31 dm² reference and historical 24 dm² reference remain distinct.

All 27 wing and five tail Selig profiles contain exactly 140 chord-normalized cosine-spaced coordinates. Not all are usable conventional airfoils: clearance, winglet and fin diagnostics are explicitly qualified. Three truncated wing cuts (`aileron_start_in`, `aileron_end_out`, `tip_root_in`) carry non-airfoil status in the integrated table. Saved control pose is not independently established aerodynamic neutral.

Dense wing integration detected incomplete exact kernel intersections. At 49 stations an audited watertight tessellation of the same physical STEP solid was used; refinement and extrema checks are retained. No replacement solid was substituted.

## Hatch-inclusive fuselage evidence

Four complete real hatch solids are installed at feature-recovered native identity with rank-6 constraints, rather than merely trusting saved coordinates. Exact original hatch skin arcs and individual source section curves are preserved, including open curves; no unsupported continuous outer skin is invented.

There are 41 tabulated endpoint/50-mm stations across common-datum and nose-relative grids, plus the x=-80 mm regression: 42 raw stations and 1056 actual curves. The -80 mm top rise is 47.57348 mm.

The nonconvex material-union diagnostic is partial: 7 stations include all closed loops, 35 have excluded invalid sampled loops, and 13 have no valid-union polygon. Empty/partial unions do not imply absent material. These diagnostics are not a reconstructed aerodynamic skin.

Envelope axial refinement changed area by 0.885%; angular refinement by 0.114%. These are model discretization sensitivities, not a physical uncertainty bound or proof of full convergence. Exact exposed wetted area is explicitly unknown.

## Verification and comparisons

- 108 original source hashes checked, with no changes; 32 exported profiles pass independent format/cosine-grid/contour checks.
- Root regression suite: 15 passing tests. Tail suite: six passing tests. Wing dense-section regressions and independent area/MAC/quarter-chord verifier passed.
- Hatch-inclusive verifier: 32 checks passed, including reloaded solids/skin faces, independent loft triangulation, nose-gap masking and exactly matched baseline grid. Nine real-section sampler refinement regressions are retained.
- UIUC: 18 extracted sections ranked; 14 excluded. Numerical shape similarity is not intended-airfoil identification or performance evidence.
- Original >2% overall-length gate failure remains preserved. Continued extraction was explicitly authorized; this did not turn the failed gate into a pass.

## Reading and reproducing the delivery

Use `geometry_table.csv` for long-form quantities, units, status and source paths. Read `EXTRACTION_LIMITATIONS.md` and the leaf READMEs before simulation. `BUNDLE_HASHES.json` is the portable review-bundle content authority; leaf manifests describe the full retained workspace and may reference heavy files intentionally not shipped. Source CAD, caches and large exact section-edge STEP remain in the retained licensed workspace. Portable raw section JSON and diagnostics are included. Reproduction requires that workspace and the recorded dependencies, not just this ZIP.

## Qualification and interpretation

- All profiles use the retained source control pose. Wing design-loft and tail midline diagnostics quantify geometric alignment, but do not establish calibrated/commanded 0° neutral.
- The32 Selig files each contain140 cosine-spaced coordinates. Conventional airfoils are not invented for the upturned winglet/fin extremes; near-tip oblique/fin contours are diagnostic geometry. Mechanical-clearance cuts can be truncated and must not be used as representative flight sections.
- Hinge gaps are bridged explicitly on the outer skin; internal bores are excluded. This is aerodynamic section reconstruction, not modification or watertight union of manufacturing CAD.
- Fuselage raw section curves are actual source intersections; tabulated convex-envelope perimeter/area and the lateral envelope loft are approximations, NOT actual continuous outer contours or exact exposed wetted area. All four feature-registered complete hatches are included. Open original hatch skin arcs remain open. Nonconvex material unions are partial at35 of42 raw stations;13 have no valid-union polygon, not absent material. The unregistered nose connection contributes no primary area; its hypothetical bridge sensitivity is separate. No end caps or buried-contact corrections are included. Hardware silhouettes are isolated-part projections, not installed drag/blockage areas. Boom-end/motor installation and full rear FUS4 hatch-tongue seating/penetration remain unresolved.
- Gross wing area/MAC includes a declared rectangular root continuation to aircraft centreline; this is not evidence of hidden wing CAD. Exposed and gross conventions remain separate. Geometric quarter-chord arms are neither CG arms nor aerodynamic-centre locations.
- UIUC matches are ranked shape similarities in1661 accepted archived profiles, not identification. Fourteen mechanical/oblique/fin cuts are excluded; see uiuc-comparison/README.md.
- Source and export checks, convergence, and15 software tests validate limited numerical properties, not assembly completeness, manufacturing tolerances or flightworthiness. Saved decimal precision is not physical accuracy. Fixed-tail STL discretization remains an uncertainty.

## Dataset map

- `geometry_table.csv`: long-form values, units, status, definitions and evidence paths; UNKNOWN blanks are not zero.
- `wing-extraction/` and `tail-extraction/`: station metrics,140-point profiles, raw section diagnostics, frame/pose investigations and convergence.
- `fuselage-with-hatches/`: current hatch-inclusive50mm sections/envelope estimate; `hatch-feature-work/`: nominal-pose feature evidence. Earlier `fuselage-extraction/` is a hatch-omitting baseline, not the final skin.
- `review-overlays/`: annotated actual projected top/front/side outlines of the45-component reference subset; not complete motor/boom installation.
- `uiuc-comparison/`: closest-shape rankings, normalized between-station deviations and comparison plots.
- `moment_arms.json`, `coordinate_frame.json`, `extraction_verification.json`, `integration_receipt.json`: conventions and verifiable receipts.

Reproduction scripts require the retained licensed CAD/manual workspace and research-venv dependencies. The review bundle does not redistribute original vendor CAD or establish redistribution rights.


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

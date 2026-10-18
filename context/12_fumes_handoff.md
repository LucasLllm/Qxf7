# 12 Fumes retained-context reconciliation

This is an evidence-backed supplement requested by Lucas for the Claude Code migration. It is NOT a simulation run, flight release, purchasing decision or silent replacement of unresolved requirements. Read this before the older syntheses and prompts. The imported source records are under `data/hardware/fumes-import/`; `IMPORT_MANIFEST.json` binds every copied file to its original absolute path and SHA-256. No manufacturing CAD, toolpath or credentials were imported.

## Evidence precedence and scope

Use Lucas's latest explicit decisions, then checked artifacts with their stated scope, then historical syntheses. A newer summary is not automatically stronger evidence. Preserve disagreements. The local `context/reference/preliminary-design-report-2026-10.md` is a snapshot, not proof of the live Google Doc's current content. The retained Fumes context records authorized later removal of the 7 kg / 2.4 m anchor and a 190 km design commitment. Do not restore those as requirements from older tables. No external document was edited during this reconciliation.

Confirmed in the retained project record:
- ONE final scaled-up modified Stork, fixed 4+1, no tilting motors; no second demonstrator is implicitly authorized.
- 95 km one-way with 750 g GROSS cargo, including medical packaging and insulation, battery swap at endpoints. These are simultaneous mission targets, not achieved performance. Do not turn them into guaranteed winter capability.
- Final scale factor, span, mass and hardware are not frozen. Standard-size Phase A is an analytical benchmark of the same project, not a second build.
- Latest Lucas clarification: omit budget from active requirements for now; assess performance feasibility first and revisit cost afterward. Do not use historical monetary figures to constrain or grade PhaseA. Raw historical snapshots are retained as history, not current budget instructions.
- Latest Lucas clarification: modified QxF7 cruise target is≥70km/h (engineering airspeed, not a promise of groundspeed in wind). Measure standard Stork performance first, without forcing its optimum to that speed. Simultaneous95km/750g/−30°C capability is not established by this clarification; final weather envelope remains future work, not a PhaseA blocker. Known/forecast icing is excluded.
- School adult build support exists. Reported school tools: xTool P3 cutter, xTool F2 Ultra marking laser, Bantam desktop mill, Bambu P2S and X2D printers. Exact capabilities and physical process setup are unverified. This is not bulk-print permission.

## Actual sliced printed masses: no longer missing

`data/hardware/slicer_weights.csv` is now populated with all 58 definitions / 82 installed pieces. Exact source filenames, typos, quantities and per-piece masses are preserved. The original empty template was saved in `fumes-import/original-slicer_weights-template.csv`.

| Material | Installed pieces | Predicted installed g |
|---|---:|---:|
| Bambu ASA Aero | 35 | 695.665882 |
| Bambu PC | 31 | 207.550815 |
| Bambu PETG Basic | 16 | 62.425759 |
| Total | 82 | 965.642456 |

Provenance: uncalibrated verified slicer estimates at original 100% scale, not weighed parts. See copied `PRINTED_MASS_REPORT.md`, `PART_MASS_RESULTS.csv`, `PRINTED_MASS_COMPLETION_VERIFICATION.json` and all 58 per-definition parent verification receipts under `fumes-import/evidence/`. Import rechecked each receipt against the existing release hashes. This is not a fresh re-slice or rerun of physical/process validation.

Reference: P2S, standard-flow 0.4 mm nozzle, 0.20 mm layers; manual-specific bed poses and regional reinforcement modifiers. Permanently approved 100% -> 99% GRID substitution; other infill patterns remain unchanged. ASA Aero reduced extrusion is already included: use raw filament density once, never another foamed-density or flow multiplier. Exclude support/brim/purge, jigs, unused variants and reinforcement modifier bodies from installed mass. The known header volume-label issue was independently checked as numeric mm3 despite a cm3 label in affected logs.

CSV `walls`/`infill_pct` are declared GLOBAL recipe descriptors, not a complete effective recipe. STEP modifiers can change them locally. `HISTORICAL_RECIPE_PROPOSAL.csv` and `HISTORICAL_RECIPE_APPROVAL.json` are frozen proposal-era records with stale flags (including slicing_run=false); they do not overrule the subsequent completed slice receipts. Do not rerun them as production jobs. Recipe columns are supplementary; mass columns are transferred directly from the released results.

The total excludes carbon, adhesives/finish, fasteners, wiring, electronics, propulsion, finished battery and gross cargo. It is not dry equipped mass or AUW. Cold/strength/process qualification remains open.

## Predicted printed centroids exist, but whole-aircraft CG does not

`fumes-import/mass-closure/predicted-print-centroids.json` contains 58 definitions / 82 installed positions, reconstructed from commanded material deposition and source/3MF/assembly transforms. Its printed subset is 965.6418116396289 g. The tiny numerical difference from the released mass CSV is a separate reconstruction/precision difference, not a second mass to add or a new physical weighing. Use the released CSV for the mass ledger and retain the centroid reconstruction separately.

IMPORTANT FRAME: centroids use existing assembly axes +X FORWARD, +Y LEFT, +Z UP. The aerodynamic extraction uses x AFT, y RIGHT, z UP. Both origins require registration; DO NOT paste centroid values into the aero-frame x_cg_mm fields or presume a sign flip alone registers origins. The printed-subset centroid is not aircraft CG. Hardware proxy midpoints are not COMs. The normalized mass CSV therefore keeps all CG cells blank.

See mass-closure/REPORT.md for the method, limitations and historical 647-check receipt. Whole-aircraft mass/CG, physical wing-root LE datum and qualified CG interval remain null/open. No physical balance or powered operation occurred.

## Hardware: historical reference selection, not a frozen scaled-aircraft BOM

`fumes-import/NO_PAYLOAD_RANGE_SPEC.md` supersedes the older 6S headline recommendation FOR THE STANDARD-SIZE UNLOADED RANGE STUDY ONLY:
- 4S common bus; BrotherHobby Avenger2812 V5 910KV; 10x6 two-blade cruise class; Lumenier51A cruise mass reference.
- Four T-Motor F90 1300KV; 7-inch two-blade lift class.
- Professionally assembled 4S3P Molicel P50B, 15Ah, 14.4V nominal / 16.8V full, 216Wh nominal; finished target <=927g including pack-side leads/connector. This is a CUSTOM-PACK DESIGN TARGET, not an acquired product, measured mass, qualified current rating or procurement approval.
- Existing SpeedyBeeF405Wing / four ES08MAII / M10Q / R24 mass references, not final firmware/current/cold-qualified installation. M10Q exact historical variant is EOL; do not substitute a replacement without accounting its interfaces/mass.
- Initial cruise study point 60km/h, investigate 50-70; actual range optimum is unknown. Do not apply QxF7 >=70 aspiration to the stock benchmark as a calibration pass/fail.

Exact prop SKU/hub/rotation, whole-pack current/sag/thermal qualification, CG, harness/protection/cooling, replacement component availability and final scaled hardware remain unresolved. No purchase, supplier contact, installation deployment, arming or flight is authorized.

RESOLVED BY SCOPE — latest Lucas clarification: PhaseA measures the STANDARD Stork using ONE4-in-1 lift ESC. Keep the retained18.5g VeloxV50A4-in-1 mass reference for that modeled baseline; exact product inclusion/current/cooling specifications retain their evidence limits. Historical prose about four separate controllers does not override this baseline. For the modified QxF7, separate ESCs are a possible future reliability trade, NOT selected. Do not revise PhaseA mass to four standalone units or ask Lucas to choose final-aircraft ESCs before stock performance work. Separate ESCs do not automatically prevent total propulsion loss: shared battery, distribution, FC and wiring remain common-cause paths.

`hardware.yaml` is intentionally not silently filled as a final configuration. A machine-readable non-operative reference is added separately as `standard_stork_reference.json`. The 6S SkyVolt finished-pack alternative remains historical research, not the current 4S headline; it is not a drop-in battery swap (prop/ESC/mass differ). Original study sources are retained, not deleted.

## Reuse installed accounting, do not add blanket overhead twice

Copied `nonprinted-installation/installed_bom.json` and REPORT.md separate published masses, calculated carbon and unmeasured allocations. Latest original-size 4S reconciliation cases:
- Dry equipped planning masses: 1889.525454 / 2056.725454 / 2467.171822g, before battery and cargo.
- These are planning cases, not measured weights or confidence bounds. Higher case includes 15% printed-mass sensitivity.
- At target927g pack, central no-cargo physical estimate2983.725454g; keep100g UNUSED growth separately (planning total3083.725454g), not as installed ballast or a spent reserve.
- Nominal full-manual carbon inventory290.262998g is calculated with assumed bores/profile/density, not measured net installed carbon. Two500mm booms alone are NOT the whole spar/tube inventory. The second10mm tube role and actual cuts remain open.
- Published reference avionics94g; common unmeasured installation191.2/336.4/579g; optional complete airspeed stack15/22/30g. Factory wires/antennas/FC BEC/current sensing are credited; do not add them again.
- 3100g is a vendor stock planning reference, not certified structural MTOW. A failed mass screen is not proof that an aircraft is physically impossible.
- Cold-weather/heating equipment, FPV, independent telemetry and powered cargo release are NOT covered by the dry baseline and may not be set to zero merely because unknown.

GROSS-CARGO CONFLICT: older mass studies use NET payload and include restraint/packaging in installation allowances. Current mission750g is GROSS. Define exact packaging/restraint membership before combining them; do not count cargo packaging in BOTH750g and airframe allowances. Aircraft reusable hold-downs may be distinct. Raw copied records preserve their original scope; they are not additive input tables.

Historical sensitivity examples (18-40km one way and7-15km return radius for unloaded216Wh cases) are assumption-led old model outputs, NOT new simulation results, calibration targets, dispatch limits or predictions for the final95km/750g aircraft. The old7kg/2.4m/580Wh studies are not selected design values.

## Geometry qualifications for Claude Code

The checked bundle remains byte-for-byte unchanged by this import. Distinguish extractor data from later modeling interpretations in context/05 and reference/qxf7-stork-baseline-geometry.md:
- `coordinate_frame.json` uses common original STEP zero, NOT an established physical wing-root LE origin. A fitted clean-wing centreline LE intercept near0 does not itself register the manual's physical CG datum. CG x=47mm can be a provisional model case, not a verified assembled CG or qualified interval.
- Keep1000mm nose-to-pusher face and1044.020mm registered tail extent separately. Original overall-length gate remains failed at+4.402%. Extraction was authorized to continue; vendor length-definition intent was not independently proven. Do not rewrite the failure as a passed check.
- Saved-source control pose is not independently certified aerodynamic or commanded neutral. Airfoil similarity is not proof of neutral incidence/deflection.
- Local V-tail incidence versus aircraft projection: implement explicit 3D chord/span vectors and the chosen solver's convention. The local -0.82deg and aircraft-projection+2.88deg are different definitions; do not substitute one blindly or discard a stored geometric projection as an error. A symmetric NACA0010 is a MODEL SUBSTITUTE, not identification of the manufactured section.
- Gross area31.245148dm2 and exposed-reference27.159434dm2 differ deliberately. Gross includes a rectangular centre continuation and a hybrid reference envelope; an extrapolated linear trapezoid is another model, not exactly the same geometry. Validate the actual modeled Sref/MAC/arm, not only coefficients normalized by a prescribed Sref.
- Convex lateral envelope0.382499929239m2 is NOT exact exposed wetted area, and convexification is NOT a proven upper bound on corrugated/concave physical skin surface area. Preserve raw open/disconnected curves; don't invent closure. Use an explicitly uncertain drag surrogate.
- Tip/fin/mechanical cuts remain diagnostic, not validated standard section polars. UIUC matches are geometric similarity, not proof of intended foil or aerodynamic performance.

## CFD and simulator readiness: don't restart or overclaim

Retained `notes/stork-development/cfd-exterior-v1/README.md` (copied as CFD_EXTERIOR_STATUS.md) records an existing standard-size AIRFRAME-ONLY exterior. Latest checked sealed-r4 is topologically cleaned but NOT production released/intersection-qualified; independent screen selects621faces, not621proven penetrations. Complete installed hardware and rotor representations remain unresolved. No volume mesh or CFD solve was performed. Different frame: metres,+X forward,+Y left,+Z up. Do not use it as a qualified whole-aircraft solver boundary or treat the early45-component review assembly as all82prints plus real hardware.

Existing eCalc/simulator/API/forward-prop research is under the Fumes source workspace; inspect retained references before repeating broad research. Manufacturer static thrust charts, APC computed maps and UIUC measured wind-on data have different evidence classes. Motor Kv/Rm/I0 or efficiency maps missing from the record remain null; do not invent them. Exact tool installations/licenses/API functionality need a live check if/when simulation setup is authorized, not a capability claim from this handoff.

## Independent geometry cross-check follow-up

A second read-only audit confirmed that the tail angle issue is a CONVENTION issue, not a bad raw angle. The roughly4.9dm² cos²(cant) pitch-equivalent tail area is a legitimate first-order model quantity: bilateral panel-plane area7.344666dm², horizontal projection6.00958dm², pitch-equivalent4.91717dm². State the plane; do not apply another projection when the3D solver already models cant. These are not extracted aerodynamic derivatives.

One definite numerical error was found and corrected in the geometry reference: the omitted tip beyond y=800mm contributes0.206448dm² bilateral (0.66074% of gross reference area), not<0.5%. Parent independently recomputed this from wing-extraction/planform_samples.csv using piecewise-linear integration of reference_envelope_width_mm. This does not mean the whole simplified model is accurate to that percentage.

The near-zero fitted centreline LE makes x=47mm a plausible declared CG case; it is NOT evidence of a uniquely resolved physical manual-root datum. Likewise, the length distinction was accepted for continued extraction, but that did not pass the original gate or independently prove vendor convention.

## Method corrections / release limits

In context/06 step4, D*V is thrust/useful aerodynamic power, NOT shaft power. With propeller efficiency eta_prop: P_shaft=D*V/eta_prop; P_batt=D*V/(eta_prop*eta_motor*eta_ESC)+P_aux. Do not divide by propeller efficiency twice. Thermal management/heating is separate.

Published vendor statements and unlike builder aircraft are plausibility/comparison evidence, not enough to validate exact model accuracy bands or force a particular trim result. Do not force-fit unknown drag, CG or incidence until targets match. VLM does not independently prove stall, CLmax, cold capability, safe CG or flightworthiness. Tool outputs are predictions conditioned on declared inputs.

Regulation, specimen classification, school/license permissions and current prices are not re-verified by this local-context audit. Historical regulatory summaries are not operation-specific authorization. Do not publish/upload/push this folder, contact others, purchase components or deploy changes without Lucas's approval. Even private git is not an automatic license grant; review bundled manual text/derived materials before publication.

## Next step

Read `docs/CONTEXT_CONFLICTS.md`, resolve Lucas's actual decisions, and use local evidence rather than asking him to retype available masses. Then choose and label Phase A cases (published/vendor comparator versus this heavier all-Bambu reference). Do NOT start a simulation simply because an old prompt says to proceed; this task only audits/transfers context.

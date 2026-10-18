# Original-size Stork: aircraft-specific conditional range analysis

## Decision summary
The geometry-derived model and sourced forward-flight propeller map yield central one-way estimates of **21.1–38.9 km**, depending on surface and stopped lift-prop assumptions. Treat the rough/crossflow case as a conservative **scenario**, not a proven lower bound. Do not plan around the optimistic case without establishing its physical conditions. The design selection remains provisional; this analysis is not flight qualification or permission to conduct long-distance operations.

| Scenario | Best tested speed (km/h) | Battery power (W) | Conditional one-way range (km) |
|---|---:|---:|---:|
| smooth / aligned | 54 | 168.3 | 38.9 |
| smooth / crossflow | 50 | 207.4 | 29.2 |
| rough / aligned | 50 | 221.2 | 27.4 |
| rough / crossflow | 50 | 286.5 | 21.1 |

Only50–70km/h was investigated. Best at50km/h means the lower tested boundary, not a proven global optimum or safe minimum speed. Some high-drag central electrical points are rejected; missing curve segments are intentional, not achieved performance.

## Configuration and mission
- Original geometry; no payload; planned physical mass2.9837kg. The100g growth allowance is unspent, not installed. Growth-stress aero rerun remains outstanding.
- Cruise: BrotherHobby Avenger2812V5 910KV, APC10x6E LP10060E two-blade;4S.
- Lift: four F901300KV and7-inch two-blade props. The retained F90 specification lists5–6S; sufficient4S hover/transition performance has NOT been demonstrated. The assumed VTOL energy allocation must not conceal this gate.
- Battery: custom4S3P P50B15Ah,216Wh nominal,927g finished planning target. Finished pack mass, construction and discharge behavior are unverified.
- Central energy:194.4Wh assumed usable minus43.2Wh reserve minus30Wh departure/transition/arrival =121.2Wh cruise. Includes15W auxiliary load and assumed97% ESC efficiency.
- Still air, straight one-way cruise distance. Not a delivery radius, four-event landing/relaunch mission, cold-weather guarantee, or demonstrated endurance.

## Geometry and aerodynamic method
Source extraction recovered40 physical exterior contour DATs, source hashes and retained assembly transforms. Source-derived span1.62054m; exposed projected wing union area0.271218m²; V-tail projected area0.073325m²; fitted cant35.1069°. These CAD measurements are not measurements of the built aircraft. The exposed wing reference differs from the vendor0.31m² figure; reference definitions must not be mixed.

Actual fixed/control parts were reconstructed into assembled profiles. Short hinge gaps were explicitly sealed, and pocket/hinge interruptions were bridged in a separately saved idealization for smooth-airfoil analysis. Raw geometry remains separate. No generic NACA substitution was used; manufacturer S3021 declaration is retained as documentary context, not substituted for actual source contours.

AeroSandbox VLM supplies inviscid forces. Reynolds-dependent NeuralFoil section tables supply profile drag and section moments. Strip lift is mapped to the positive-slope prestall branch; clipping is recorded. Numerical acceptance requires lift residual below0.05N, pitch residual below0.01Nm, less than1% area outside the section prestall branch and weighted NeuralFoil confidence at least0.8. These are computational screens, not physical stall margins or calibrated accuracy measures.

Working CG maps the manual47mm aft-of-root-LE instruction into retained CAD coordinates: X_ASB0.0514433m. It is not weighed balance. Trim adjusts equivalent tail incidence; this is NOT a verified elevator-deflection mapping. Control travel/authority, CG tolerance, thrust-line moment and fuselage/hardware aerodynamic moments remain unverified or omitted.

Component buildup separately estimates fuselage, booms, gear, mounts, motor cans and stopped lift blades. Documentary F90 diameter33.4mm supersedes the earlier28mm proxy. Exposed motor height remains assumed25mm; listed34.7mm overall motor dimension is not an exposed-can measurement. Remaining boom exposure, pusher dimensions, blade cross-section, blockage/form/interference coefficients and surface-transition conditions are engineering assumptions. Smooth uses n_crit9/natural transition; rough uses n_crit1/forced5%-chord transition plus larger component allowances. These scenarios are not measured roughness effects or statistical bounds.

Windmilling is NOT quantified. Horizontal lift rotors see principally edgewise cruise flow; an axial actuator-disk drag formula would be inappropriate here. Stopped alignment is a hypothetical physical state, not a capability established by an ESC setting.

Mesh-convergence runs were requested in the assembled solver, but final numerical readback/acceptance was not completed after the earlier approval block. The44-row sweep uses mesh(2,3). Do not describe discretization independence as established. The latest component-only correction preserves inviscid/viscous trim results and recomputes additive parasite drag; older convergence artifacts are not the final component revision.

## Propulsion and battery evidence
APC manufacturer COMPUTED map PER3_10x6E.dat, versionv2022-0915, simulation2022-09-22, is bounded without extrapolation. This is not a measured propeller map. At4N required thrust,50/60/70km/h correspond to approximately7062/7678/8346rpm and81.2/95.2/110.2W shaft power. Complete bracket coverage matters:1N at70km/h is rejected.

Motor electrical power uses an explicitly uncalibrated equivalent-DC model. Resistance factors0.5/1/2 and conflicting10/14V idle references produce six convention sensitivities. Bench input/RPM data have no torque and cannot calibrate shaft efficiency. Bus current, motor voltage and15000rpm screens reject unsupported points; timed catalog ratings do not establish continuous thermal capability. Voltage checks12/14.4/16.8V are operating-point screens, not integration through a SOC-dependent discharge.

The P50B chart digitization gives approximately184.1Wh pack-equivalent down to3.0V/cell, or200.7Wh to2.6V/cell, under its ambiguous source test condition. Caption and tab label conflict. These integrals are diagnostics, NOT approved cutoff settings or qualified usable flight energy. The central194.4Wh assumption and85/90/95% sweep are retained explicitly as assumptions; reserve is separate. Cold, aging, sag, wiring losses and low-SOC relaunch are not qualified.

APC hub bore6.35mm versus motor M5 requires verified5mm centering, clamping, nut/thread engagement and clearance; exact included ring compatibility remains open. No installation is qualified by this report.

## Executed verification
- Geometry:4 current tests passed after correcting a missing exported documentary field; includes actual-source reconstruction and source hashes.
- Propulsion:6 tests passed after the final idle-loss correction; offline build rerun succeeded.
- Parent reconstruction/mission/coupling:9 tests passed.
- Saved mission sweep:64,152 entries; 48,600 entries with reported range independently passed energy/distance, voltage-admission and RPM checks.
- Four-panel plot visually inspected for legibility and conditional labeling.

Tests establish calculation mechanics and evidence consistency, not aerodynamic truth. The earlier delegate's isolated-part full-aircraft adapter was incomplete; the delivered assembled-source pathway supersedes it. Do not run the old adapter and treat its output as this report.

The still-air14.4V scenario endpoints across ALL tested speeds and modeled assumptions are13.1–48.8km. These endpoints mix speed and assumption changes; they are not a confidence interval for optimized range and do not capture all model-form error.

## Targeted validation, not another selection loop
1. Qualified human review:4S lift thrust/transition margin, actual mass/CG, control authority, prop retention and electrical/thermal limits. No motors armed or hardware deployed here.
2. Establish stopped-prop behavior/orientation. Do not assume motor braking fixes blade azimuth.
3. Professional pack characterization at expected loads and temperatures, with reserve and loaded-voltage margin separately defined. Do not lower battery protections to reach a modeled energy target.
4. Controlled, supervised cruise-power measurements at a small set of approved speeds, after flightworthiness/regulatory review. Compare measured pack power to the saved curves; use measured deviations to calibrate drag/loss terms.
5. Close mesh/CG/growth stress studies and explicit gap/body/thrust-line uncertainty before presenting a narrow accuracy claim.

Propellers removed for configuration and non-thrust bench work; restrained propeller tests require qualified supervision, exclusion zones, electrical protection and defined stop conditions. Nothing in this artifact authorizes flight, BVLOS delivery, purchases or safety-interlock changes.

## Artifacts and reproduction
`ASSEMBLED_AERO.json/.csv`, `MISSION_SWEEP.csv`, `MISSION_SUMMARY.json`, `COMPONENT_REVISION.json`, plots, source captures and code remain in this analysis directory. Use the aero-venv for `assembled_solver.py`, `update_component_drag.py`, `run_mission.py`; source extraction needs research-venv and the original source paths. The ZIP is a results/implementation archive, NOT a standalone CAD-source or solver-environment distribution. Provenance hashes are in FINAL_VERIFICATION.json.

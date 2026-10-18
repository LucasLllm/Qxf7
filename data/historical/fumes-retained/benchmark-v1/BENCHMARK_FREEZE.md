# Standard Stork / Flightony benchmark freeze v1

**Frozen:** documentary identity, published claims, reference conventions and evidence hashes.
**Not frozen as fact:** exact as-flown hardware/build, measurement conditions, validated model and CFD production settings.
**Scope:** stock-size Stork only. No scale-up, purchases, vendor contact, CAD changes or new aerodynamic simulation.

## Frozen benchmark
| Item | Reference | Status |
|---|---|---|
| Primary | Operator, 4S4P Samsung 50E, 288 Wh nominal, ~2.9 kg total AUW, ~1.2 kg pack | Published; payload inclusion unresolved |
| Secondary | Explorer, 4S3P Samsung 50E, 216 Wh nominal, ~2.7 kg total AUW | Published; pack mass/payload inclusion unresolved |
| Airframe | 1.62 m span, 1.00 m length, 0.31 m2 published wing area; LW-PLA/carbon, fixed 4+1 V-tail | Area convention and as-built source equivalence unresolved |
| Cruise | BH Avenger 2812 V5 910KV, APC 10x6E, Lumenier 51A BLHeli32 | Published hardware identity; installed efficiency unresolved |
| Lift | Four F90 1300KV, Velox V50A 4-in-1, four 7-inch props, 2 CW/2 CCW | Exact props and actual voltage qualification unresolved |
| Reference conditions | Still air, 15 C / 101325 Pa / 1.225 kg/m3, 54 and 60 km/h AIRSPEED | Adopted analysis convention, not recovered test weather |
| Power/range | Total battery-terminal power; one-way total path; one takeoff/final landing | Adopted reporting convention; vendor boundary unresolved |

## Claims to compare (not guaranteed performance)
| ID | Claim | Value |
|---|---|---|
| C01 | cruise_power | [80, 110] W |
| C02 | hover_power | 300 W |
| C03 | Operator_range_scenario | 130 km |
| C04 | Operator_range_scenario | 118 km |
| C05 | Operator_range_scenario | 104 km |
| C06 | Explorer_range | [70, 85] km |
| C07 | nominal_cruise_speed | [54, 60] km/h |
| C08 | Operator_payload_capacity | 200 g |
| C09 | Explorer_payload_capacity | 500 g |

The performance scenarios quote 2.0 / 2.2 / 2.5 Wh/km and approximately 130 / 118 / 104 km. Operator sales page separately says 100–130 km. Keep both source wordings; do not collapse scenarios into one exact simultaneous payload/range claim.

## Files actually present
All 104 retained extracted vendor files matched the prior audit hashes (32 STEP, 70 STL, 2 wiring PDFs). Separate base/VTOL mechanical manuals and prior geometry/propulsion/battery evidence are present and hashed.
The old vendor ZIP containers are unavailable. This does not erase the retained source files, but prevents fresh container/completeness revalidation. STEP coverage is partial. The showcase contains illustrative hardware; its successful export does not qualify a fluid-domain mesh.
The retained APC 10x6E data header identifies computed simulation data. Current APC retrieval was blocked; retained computed data remain available. Neither constitutes measured exact installed propulsion.

## Every open input and its recommended treatment

### U01 — Vendor/build version and source equivalence
**Unresolved:** Flightony build revision, modifications versus Flightory packs, and exact as-tested BOM are not established.
**Recommendation:** Use the hash-frozen supplied standard packs as our source-based stock representation; request build-revision confirmation before calling it an exact Flightony replica.
**Gate:** Source-based analysis may proceed; exact vendor match blocked.

### U02 — Installed CFD geometry and reference definitions
**Unresolved:** Complete native STEP coverage is absent. Tail root placement, root leading-edge datum, exposed boom lengths, actual motor/shaft/prop geometry, gear detail, openings, hinge gaps and assembled exterior quality remain unqualified; published 0.31 m2 is not a recovered area convention.
**Recommendation:** Reuse original STEP where supported and original STL elsewhere. Audit placements against geometry/manuals; qualify the exterior fluid boundary without erasing real gaps. Replace illustrative hardware with sourced geometry. Retain published area as a documentary reference and separately report measured exposed area.
**Gate:** Whole-aircraft CFD release blocked until selected geometry and approximations are verified.

### U03 — Actual mass, payload inclusion, mass distribution and inertia
**Unresolved:** Published approximate 2.9/2.7 kg AUWs do not establish whether 200/500 g cargo is included. Actual pack, printed-part and equipment masses, cargo location and inertia are not measured.
**Recommendation:** Freeze 2.9 kg Operator and 2.7 kg Explorer total-mass reference cases with cargo inclusion null. Keep unloaded/loaded interpretations separate, not mixed into the nominal cases. Obtain mass breakdown or weigh an exact build; derive uncertainty and inertia from qualified distributions. Explorer 2.7+0.5=3.2 kg would exceed the published 3.1 kg range if AUW excludes cargo; flag, do not assert MTOW.
**Gate:** Fixed-total-mass aero studies allowed; payload claims and dynamics require resolution.

### U04 — CG, trim, controls and allowed CG envelope
**Unresolved:** Installed 3D CG, documentary datum mapping, permitted CG envelope, cruise trim/control deflections, incidences and actuator characteristics are not qualified.
**Recommendation:** Use source/manual geometry to resolve datum and surfaces first. Solve force/moment-balanced cruise with explicitly conditional CG cases; obtain vendor/measured CG and control limits. Do not adopt an old working CG as a measurement or release an invented safe CG range.
**Gate:** Trimmed exact-match prediction blocked; conditional CG/trim sensitivity allowed.

### U05 — Surface condition and manufacturing variation
**Unresolved:** Flightony print profile, foaming ratio, paint/coating, seams, roughness and dimensional tolerances are not specified.
**Recommendation:** Benchmark the vendor LW-PLA/carbon exterior, not the final project Bambu lineup. Run labelled smooth/printed/rough sensitivities supported by plausible bounds; seek build photos and measured surface/shape information. Do not call these statistical confidence bounds.
**Gate:** Conditional drag prediction allowed; tight accuracy claim blocked.

### U06 — Exact lift propellers and thrust/power maps
**Unresolved:** Seven-inch diameter and CW/CCW pairing do not identify manufacturer, SKU, pitch, blade geometry or exact installed F90/prop/ESC maps.
**Recommendation:** Ask Flightony for prop SKU/pitch and test data on the actual bus. Do not choose a convenient 7-inch prop and label it exact. If unavailable, use separately named candidate sensitivities and seek supervised calibrated lift tests.
**Gate:** Exact hover, VTOL phase energy and blade-resolved lift simulation blocked.

### U07 — Lift-rotor state during cruise
**Unresolved:** Stopped/freewheeling/braked state, actual stop angles and controller behaviour are unknown.
**Recommendation:** Retain aligned and crossflow stopped-rotor sensitivity cases; add windmilling only with an appropriate model. Use logs/video or configuration evidence to select the representative state. Never count omission of rotors as an aircraft result.
**Gate:** Conditional cruise bounds allowed; single exact drag figure blocked.

### U08 — Voltage architecture and ESC settings/compatibility
**Unresolved:** Actual lift bus, any boost/regulation, BMS path, ESC variants, timing/PWM/braking, calibration and continuous thermal/current limits are unknown. F90 documented 5-6S rating versus advertised 4S pack remains an unresolved qualification gap.
**Recommendation:** Request the installed electrical schematic/settings and evidence at the actual voltage. Freeze the advertised 4S pack without substituting a 6S design. Analyse low-voltage sensitivity but do not qualify operation from KV or model feasibility alone.
**Gate:** Exact propulsion prediction and physical operation qualification blocked.

### U09 — Cruise prop/motor/ESC electrical map
**Unresolved:** Exact installed forward-flight electrical efficiency, motor constants/losses, ESC losses, wiring drop, prop installation and continuous thermal duty are not measured. Retained APC 10x6E map is manufacturer COMPUTED data, not wind-tunnel validation.
**Recommendation:** Use retained hash-pinned APC computed advance-ratio map only in-domain; calibrate motor/ESC against exact-hardware evidence. Preserve previous motor-loss and 97% ESC assumptions as legacy assumptions, not new measured inputs. Obtain blade geometry only if powered/blade-resolved CFD is warranted.
**Gate:** Conditional cruise coupling allowed; measured efficiency claim blocked.

### U10 — Avionics and auxiliary loads
**Unresolved:** Actual FC/GPS/RX/servo, DJI O3, Pi Zero 2W and LTE operating loads, regulators and duty cycles are unknown; telemetry-ready does not establish all options installed/active.
**Recommendation:** Keep core and optional avionics separate. Preserve the old 15 W allowance as one named sensitivity only; obtain rail/terminal measurements or component evidence and run camera/LTE on-off cases without guessing installed status.
**Gate:** Exact total-battery-power comparison blocked; explicit-load sensitivities allowed.

### U11 — Pack/BMS usable energy and landing reserve
**Unresolved:** Exact BMS, interconnects, finished pack resistance, cutoff/load curves, cell revision/age/state of health, temperature and delivered Wh are unknown. The retained Samsung document is a dealer-hosted tentative revision, not qualification of this pack. Explorer finished pack mass is unquoted.
**Recommendation:** Freeze Samsung 50E 4S4P/4S3P nominal 288/216 Wh only as catalogue values. Keep 10% nominal reserve as seller accounting, not guaranteed usable energy. Build a load/temperature-aware pack model from exact evidence and maintain landing power/voltage feasibility. Keep proportional 900 g Explorer mass labelled legacy assumption until sourced.
**Gate:** Seller arithmetic allowed; validated endurance and physical pack safety blocked.

### U12 — Operating environment and speed definition
**Unresolved:** Vendor altitude, temperature, density, wind/turbulence and airspeed-versus-groundspeed basis are not provided.
**Recommendation:** Adopt a reproducible still-air reference at standard sea-level atmosphere: 15 C, 101325 Pa, rho 1.225 kg/m3; no icing. Reference speeds 54 and 60 km/h are AIRSPEED. Mark this as our convention, not recovered Flightony weather. Add conditions once sourced; cold/rough weather remain separate studies.
**Gate:** Reference calculations allowed; historical flight-condition match blocked.

### U13 — Mission boundary and vendor claim accounting
**Unresolved:** Range versus radius, phase boundaries, VTOL-inclusive Wh/km, reserve/cutoff, current-meter boundary and payload/speed pairing are not fully established; performance page says estimated scenarios alongside flight-testing language.
**Recommendation:** Freeze range as one-way total path for this comparison, not delivery radius. Compare steady cruise battery-terminal power separately from mission energy. Preserve both vendor scenario arithmetic and complete phase accounting. Do not subtract VTOL energy twice if quoted Wh/km already includes it; do not force the models to agree.
**Gate:** Documentary claims frozen; definitive claim verdict conditional on definitions.

### U14 — Autopilot and transition model
**Unresolved:** ArduPlane release/parameter set, controller laws, lift/cruise schedule, transition times/altitudes, aerodynamic derivatives, inertia and actuator dynamics are not available.
**Recommendation:** Defer custom six-DOF/SITL until aerodynamic/electrical model is checked. Keep seller 60/30/30/60-second phases as illustrative accounting only, not a validated trajectory. Request parameter files/logs before reproducing actual transitions.
**Gate:** Full matched dynamic mission simulation blocked; steady studies can proceed.

### U15 — Validation data and measurement uncertainty
**Unresolved:** No independently calibrated exact-build power/airspeed/hover logs, pack discharges or installed drag measurements have been established. Raw sensor calibration, repetitions and independent holdout data are unavailable.
**Recommendation:** Prefer existing vendor logs or access to a matching aircraft before constructing a second standard Stork. Request raw logs, setup/weather, sensor calibration and ending reserve. Separate calibration and held-out validation. Human-approved supervised tests only if required; no long-range flight presumed authorized.
**Gate:** Prediction possible; independently validated performance and numerical accuracy percentage blocked.

### U16 — CFD runtime, model choices and release criteria
**Unresolved:** Earlier OpenFOAM runtime failed; a working solver is not established. Turbulence/transition treatment, surface meshes, domain/near-wall settings, discretization, convergence criteria and model-form uncertainty are not frozen.
**Recommendation:** Verify runtime on a known case, then a small Stork pilot; retain solver/version and pilot cost. Freeze mesh/domain/wall and discretization criteria before production, using force/moment stability and refinement evidence; distinguish numerical from input/model-form uncertainty. Do not choose arbitrary settings and call them highest accuracy.
**Gate:** Production whole-aircraft CFD blocked until implementation verification; research and geometry audit allowed.

## Accounting separation
Exact arithmetic from the approximate published phase powers/times is 13.333333 Wh, versus 13.4 Wh obtained by summing individually rounded displayed entries. These are calculations from claims, not measurements.
288 Wh less 10% nominal reserve is 259.20 Wh; subtracting these phases separately leaves 245.866667 Wh. Do not also subtract them when comparing an already VTOL-inclusive mission Wh/km figure.
Cruise power and total-mission Wh/km are different metrics. A still-air reference cannot directly validate a vendor scenario described as windy/heavier without matching its conditions.

## Proceed / hold
**Ready now:** source/placement audit, resolving datum/CG conventions, sensitivity definitions and a verified solver pilot once the runtime works.
**Not ready:** a fully matched high-accuracy whole-aircraft production run, exact hover/transition energy, validated endurance, or a promised percentage accuracy.
**Lucas:** no new aircraft dimensions or motor choice are needed. If available, provide exact Flightony build/prop information or existing raw logs. Otherwise, the next user decision is whether to authorize requesting that evidence from Flightony; no contact has been made.

## Change control / validation
Unknowns remain null in BENCHMARK.json. Recommendations are not frozen measurements. Preserve v1; new evidence produces v2 with explicit change log and reruns. Never fit coefficients to the target claim. Calibrate only against physical data and retain independent validation points. Qualified human review is required for safety-critical hardware and tests.

SOURCE_MANIFEST.json binds all source bytes. VERIFICATION.json independently records the final readback/hash/schema checks; these checks verify artifacts, not aircraft performance.

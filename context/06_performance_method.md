# 06 Performance-estimation method (agreed 2026-10-17)

## Principle
No single program turns STL/STEP + a parts list into flight specs. Performance comes from a short chain, and each tool supplies one link. **Establish a defensible standard-Stork baseline first.** Explain its disagreements with the retained model and with published claims, then scale to QxF7. Published figures are documentary or third-party comparison points, not matched measurements; true calibration needs measured flight or bench data.

## The chain
1. **Mass and weight W**: use released per-part predicted mass × installed quantity, add the itemized installed hardware ledger once, then W=m*g in newtons. Mass entries alone do not supply positions/CG. Keep unknown installations, sensitivity and UNUSED growth separate; do not add a blanket5–15% on top of already-accounted allowances. See context/12 for58released masses and separately framed print centroids.
2. **Lift coefficient needed**: C_L = W / (½ ρ V² S). S = 0.3125 m² (gross). ρ at +15 °C = 1.225, at −30 °C ≈ 1.45 kg/m³ (+18%).
3. **Drag polar** C_D(C_L) of the *whole trimmed aircraft*:
   - wing + tail induced and profile drag, trim, stability → Flow5/XFLR5 (or a scripted VLM equivalent);
   - fuselage, booms, stopped lift props, lift motors, skids, pusher mount, excrescences → OpenVSP Parasite Drag (or a component build-up in code), added to Flow5 as "extra drag".
4. **Power to fly**: useful thrust power P_thrust = D·V; shaft power P_shaft = D·V/η_prop; battery power P_batt = D·V/(η_prop · η_motor · η_ESC) + P_aux. Apply prop efficiency once. Propeller efficiency at forward speed from APC performance data / UIUC propeller database; motor from Kv, Rm, I0; cross-check with eCalc propCalc.
5. **Hover/transition energy**: hover power from eCalc xcopterCalc and/or momentum theory P = T^1.5 / (FM·√(2ρA)) with FM ≈ 0.6–0.7, cross-checked against T-Motor F90 + 7" test data; × hover/transition time per leg.
6. **Mission energy**: usable = rated Wh × usable fraction (≈0.8–0.9) × cold derating × aging; cruise energy = usable − hover − reserve; endurance = cruise energy / P_batt; range = V × endurance.

Sweep V to get the **power-required curve** and read off:
- stall speed (C_L = C_Lmax, 3D, trimmed),
- best-endurance speed (min power),
- best-range speed (min energy per km, i.e. min P/V including η(V); shift faster in headwind),
- max level speed (P_required = P_available from the pusher at full throttle),
- climb rate = excess power / W,
- hover thrust margin = max lift thrust / W (want ≥ 1.5–2 for control authority),
- static margin and trim (from the aero model),
- endurance and range per mission profile, payload and temperature.

## Tool decisions (researched 2026-10-17)
| Tool | Verdict | Why |
|---|---|---|
| **XFLR5 / Flow5** (Flow5 = XFLR5 v7; API still experimental through end of 2026) | **Use** (GUI, by Lucas/Mario) | Low-Re airfoil polars (XFoil), VLM/panel, trim, neutral point, static margin. Inviscid panel: does not do fuselage friction drag |
| **OpenVSP + VSPAERO** | **Use** | Parametric geometry, Parasite Drag tool (skin friction × form factor + excrescences), whole-aircraft drag, STEP export |
| **eCalc** (propCalc, xcopterCalc) | **Use** (cross-check) | Drive-system model with temperature/elevation input, claims ±15%. Models propulsion only, not airframe |
| Python mission model | **Use** | Combines everything; reruns instantly for scaling, battery, payload, temperature |
| SIMNET (simnet.aero) | Optional cross-check | Parametric web tool (Typhon engine, lifting-line), quadplane tutorial, $15–45/month (education pricing). Cannot import CAD; black box |
| AirShaper | Later, only if student credits | Cloud CFD, accepts STL/STEP, per-component forces; €990/yr for 25 credits (Basic), €2,990/yr for 100 credits (Regular: 10 credits per run). Good for VTOL drag increment (with vs without booms/props). Low-Re wing drag less trustworthy than XFoil |
| ANSYS (student) | Later | Overkill now; cell-limited; useful for targeted fuselage/boom drag and FEA on mount load paths |
| MATLAB | Skip for now | Student toolboxes cheap, but VTOL examples are control-oriented (tilt-rotor), not performance |
| JSBSim | Skip | Needs aero tables from the tools above; quadplane JSBSim models are painful in ArduPilot |
| RCAIDE | Not needed yet | Powerful open-source Python design/mission tool, but weight methods target full-size aircraft |
| ArduPilot SITL | Later | Built-in quadplane sim for rehearsing transitions/missions, not for spec prediction |

**Scripted equivalents for Claude Code** (automation and cross-check of the GUI work; verify each installs and runs on macOS before relying on it): XFoil binary or NeuralFoil for 2D polars; AeroSandbox (VLM, AeroBuildup) and/or AVL for 3D; OpenVSP's Python API (ships with OpenVSP) for parasite drag; plain NumPy for the mission model. GUI Flow5 results by the team and scripted results should agree; disagreements are findings.

## Reynolds numbers and polars
- Re = V·c/ν. Wing chords 230 → 120 mm, tail 162 → 115 mm (fin tip 33). Speeds 10–25 m/s. ν ≈ 1.46e-5 m²/s at +15 °C, ≈ 1.07e-5 at −30 °C (Re ~1.35× higher in winter).
- Wing polars Re ≈ 50k–400k; tail 40k–250k. Ncrit 9 (smooth) **plus Ncrit 5 sensitivity** (printed LW-PLA/ASA is not a smooth surface; seams).
- Low-Re laminar separation bubbles dominate wing drag at ~150k; XFoil handles this better than general RANS.

## Comparison points for the standard Stork VTOL (NOT matched calibration measurements)
None of these is a matched measurement of this build. Classify each one and do not force-fit to it (Lucas, 2026-10-18).

| Comparison point | Value | Class | Caveat |
|---|---|---|---|
| Pitching moment at 0° AoA with CG set | "virtually no pitching moment" | documentary (manual p.5) | A moment statement about undefined CFD conditions is not proof of trimmed flight at α = 0°. |
| Peak efficiency AoA | 0–3° | documentary (manual p.5) | Reference axis and conditions undefined. |
| Optimal cruise speed | 50–70 km/h | documentary (manual, product page) | A band, not a measured optimum. |
| Prototype cruise | "< 50% throttle", 4S, 10×6 | documentary (manual p.13) | Transmitter throttle % does not give power, RPM or PWM duty without the control mapping. |
| Cruise power / energy | 80–110 W; 2.0–2.5 Wh/km (incl. VTOL) | third-party vendor claim (Flightony) | Appears calculated; AUW/payload inclusion unresolved. |
| Effective L/D × η | ~5–6 (real 4+1 builds); Stork v1 3.6 | unlike-aircraft plausibility band | Different aircraft, props, mass; not an accuracy target. |
| Static stability | NP aft of CG | physical requirement | The VLM does not validate a safe CG. |

If a model falls outside these bands, explain why component by component; do not tune uncertain inputs to close the gap.

## Sensitivities to always report
- Stopped lift-prop alignment (aligned vs random vs crosswise): 10–35% cruise power effect in builder data.
- Ncrit 9 vs 5.
- Temperature +20 °C vs −30 °C (density up, battery capacity and voltage down).
- AUW sweep (1.8 → 3.1 kg) and payload.
- Fuselage drag ±20% is a provisional sensitivity choice, not a validated error band. Convex envelope is not exact wetted area and is not a proven upper bound on corrugated/concave physical skin area.
- Hover time per leg (60–180 s).

## Accuracy to expect
Historical planning aspirations were ±20–25% raw, ±10–15% calibrated, ±5% with flight evidence. These are NOT established accuracy/confidence bounds. Accuracy requires comparable held-out measurements and uncertainty accounting. Vendor/unlike-builder matches are plausibility checks, not validation of this exact build. Do not force-fit uncertain CG/incidence/drag to targets; VLM does not validate CLmax, stall or safe CG.

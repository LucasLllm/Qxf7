# Prompt 2: Phase A, performance of the standard Stork VTOL by simulation

> **Before this older prompt:** Read `context/12_fumes_handoff.md` and `docs/CONTEXT_CONFLICTS.md`. Released slicing/installed-mass/historical4S evidence is now imported. Use explicit solver-frame registration for CG/incidence, preserve the failed original length gate and do not call convex surface a wetted-area upper bound. Vendor/builders are comparator evidence, not enough to establish accuracy bands. Latest Lucas clarification: omit budget, use ONE4-in-1 lift ESC for standard-Stork PhaseA, and keep≥70km/h as the modifiedQxF7 cruise target—not a forced stock optimum. Separate ESCs are undecided for the modified aircraft. Resolve cargo packaging only when modeling loaded cases; do not block unloaded PhaseA on final-aircraft decisions. This migration audit itself does NOT authorize running this prompt, installing software or uploading files.

## Goal
Produce a **calibrated, reproducible performance estimate of the standard Flightory Stork VTOL** (4+1 quadplane, as designed: 1620 mm span, S3021, V-tail) from its verified geometry, using a scripted pipeline that a person can rerun and that cross-checks the Flow5/XFLR5 + OpenVSP GUI work Lucas and Mario will do in parallel. This is the calibration case; QxF7 scaling (Phase B) comes later and must reuse the same code.

Answer, with conditions and uncertainty attached:
1. Drag polar of the trimmed aircraft (C_L, C_D, L/D vs α and vs V), with a drag breakdown by component.
2. Power-required curve and the speeds: stall, best endurance, best range, max level (if pusher data allows), and the 50–70 km/h "optimal" band check.
3. Hover power and thrust margin on the lift system.
4. Energy per km in cruise (Wh/km) and endurance/range for defined mission profiles.
5. Sensitivities: AUW, payload, temperature (+20 °C vs −30 °C), stopped-prop drag, surface roughness (Ncrit), fuselage drag uncertainty, hover time.
6. A comparison against every calibration target, explaining each miss.

## Inputs
- Geometry: `data/stork-geometry-bundle/` via `context/05_cad_geometry_extraction.md` (use its "Flow5 / XFLR5 input summary"; respect the traps listed in `CLAUDE.md`).
- Aircraft data: `context/04_stork_baseline_aircraft.md` (official vs third-party vs builder).
- Hardware: `data/hardware/hardware.yaml` + `slicer_weights.csv` if filled. **If not filled, use Flightory's recommended hardware** (pusher BrotherHobby 2812 910 KV with 10×6 on 4S; lift T-Motor F90 1300 KV with 7" two-blade; 4S Li-ion) and treat AUW as a sweep 1.8–3.1 kg with a reference case of **2.9 kg** (Flightony's AUW, third-party). Say which case every result uses.
- Method and calibration targets: `context/06_performance_method.md`.

## Work plan (stop and report at each ★)

**A0. Environment.** Venv, pinned versions in `docs/ENVIRONMENT.md`. Create `docs/DECISIONS.md` and log every modelling choice and why.

**A1. Geometry module.** `src/qxf7perf/geometry.py` loads the bundle and builds a clean parametric description: wing (two linear sections 0→730 mm plus tip panel), V-tail (35.1°, −0.82°), fuselage stations, booms (2 × 10×10×500 mm square tubes), skids, lift motors and stopped props, pusher mount. Include a uniform `scale` parameter and independent span/chord parameters for Phase B. Unit tests reproduce span, Sref, MAC, AR, tail area and tail arm within 1% of `context/05`. Plot top/front/side views and overlay them on the bundle's review outlines.

**A2. Airfoil polars.** S3021 (UIUC coordinates; also compare the extracted `inner_clean.dat`, which has a 1 mm printed trailing edge) and NACA 0010 for the tail. Re 30k–500k, α −6° to +16°, Ncrit 9 and 5. Use XFoil if it runs reliably; otherwise NeuralFoil; ideally both, compared on a few points. Save polars as CSV with metadata.

**A3. Wing + tail aero.** VLM (AeroSandbox and/or AVL) of wing + V-tail with the real incidences and washout. Outputs: CL_α, CL_max (trimmed, from the strip/section approach; state the method), Cm_α, neutral point, static margin at CG x = 47 mm, trim α and elevator (ruddervator) deflection vs C_L, induced drag/Oswald e. Profile drag from the polars at local Re. ★ Report the trim check: does Cm ≈ 0 near α ≈ 0° at CG 47 mm? Is peak L/D between 0° and 3°? If not, find out why before continuing (incidence, CG, tail volume, decalage).

**A4. Parasite drag build-up.** Component build-up (skin friction with laminar/turbulent split × form factor × interference, plus excrescences): fuselage (from the 50 mm cross-sections; note the convex envelope over-estimates wetted area), booms, 4 lift motors, 4 stopped props (aligned with the booms vs random vs crosswise as three cases), skids, pusher mount, servo horns/hinges, seams. Use OpenVSP Parasite Drag if available and cross-check with the hand build-up; state every form factor and its source. Report CD0 by component, in drag counts and as a % of the total.

**A5. Propulsion.** Pusher: prop efficiency vs advance ratio from APC performance data (or UIUC propeller database) for the documented prop, combined with a motor model (Kv, Rm, I0) and ESC losses → η_total(V, thrust). Lift: hover power from manufacturer test data for T-Motor F90 1300 KV + 7" if obtainable, else momentum theory with FM 0.6–0.7, with a ±range. Record every data source (URL + date) in `data/propulsion/README.md`. ★ Report max level speed, the throttle needed at cruise on 4S, and compare with the manual's "< 50% throttle on 4S with 10×6".

**A6. Battery and mission model.** Energy model with usable fraction, voltage sag vs current, temperature derating (+20 °C and −30 °C, with a stated cold-capacity assumption), aging, reserve, hover + transition time per leg (60/120/180 s), climb to cruise altitude (120 m AGL), detour factor. Missions to report:
   - M1 "endurance": take-off, cruise at best-endurance speed to reserve, land.
   - M2 "range, one-way": take-off, cruise at best-range speed, land; 20% reserve.
   - M3 "service leg": 0 / 200 / 500 g payload, 10 km and 30 km legs at 70 km/h (19.4 m/s).
   Each at +20 °C/no wind and −30 °C/7 m/s headwind.

**A7. Calibration and validation.** Table: target | source | model value | Δ | pass/fail | explanation. Targets: trim ≈ 0° at CG 47 mm; peak L/D at 0–3°; optimal speed 50–70 km/h; < 50% throttle on 4S; Stork v1 1.21 Wh/km at 1.6 kg (fixed-wing, loiter; run a no-VTOL-hardware variant to compare, but treat it as a loose check only: v1 was an earlier airframe, ~24 dm² wing per Flightory's 2021 blog, not the v2 geometry in the bundle); builder L/D·η ≈ 5–6 for 4+1 builds; Flightony 2.0–2.5 Wh/km at ~2.9 kg (third-party). Explain whether the evidence supports the ~1.5–1.8 Wh/km builder-derived estimate or Flightony's 2.0–2.5, and what that implies for the earlier QxF7 energy model in `context/07` (believed 1.5–2× too optimistic).

**A8. Independent check.** Have a separate subagent that has not seen your code re-derive the headline numbers (CD0, best-range speed, cruise power, Wh/km at 2.9 kg) by hand calculation from the inputs only. Report agreement; investigate any difference > 10%.

**A9. Report.** `reports/2026-xx-xx_stork-vtol-phaseA.md` for Lucas and Mario: method, assumptions table (with provenance), results tables and plots (polar, L/D, power-required with available power, Wh/km vs speed, range vs AUW, sensitivity tornado), calibration table, limitations, and a short "what this means for QxF7" section **without choosing a size** (just how the calibrated numbers change the earlier assumptions). Include a Flow5 cross-check checklist: the exact inputs they should enter in the GUI and the numbers they should expect to see, so the GUI and scripted results can be compared.

## Rules
- Follow `CLAUDE.md`. Provenance on every number; conditions on every range figure.
- Prefer measured/published data over generic models; when you must assume, give a range and propagate it.
- Don't silently tune parameters to hit calibration targets. If you adjust something (e.g. a form factor or Ncrit), log it in `docs/DECISIONS.md` with the reason and show results before and after.
- Commit after each step with a clear message. Runs go to `runs/<date>_<name>/`, never overwritten.
- Ask me only for things that are genuinely my decision or that you cannot find (e.g. my chosen hardware). Otherwise make the reasonable call, log it, continue.
- At each ★, stop and send me a short status: what you did, the key numbers, anything surprising, and what's next.

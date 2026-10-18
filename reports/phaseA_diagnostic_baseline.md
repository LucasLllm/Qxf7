# Standard Stork VTOL: Phase A diagnostic baseline (2026-10-18)

For Lucas and Mario. This is a **model** of the standard 1.62 m Stork VTOL. Nothing here is measured or flight-qualified. Run: `runs/2026-10-18_phaseA_diagnostic/`, reproduced by `.venv/bin/python scripts/run_phaseA_diagnostic.py`. Decisions: `docs/DECISIONS.md`. Uncertainty classes: `docs/UNCERTAINTY_REGISTER.md`.

**Conditions for every number below unless stated otherwise:**
- Air and flight: 15 °C, 101325 Pa, rho = 1.225 kg/m³, still air, straight and level, unloaded (no cargo).
- CG: case A, x = 47 mm. Lift props stopped and **aligned** fore-aft. Central parasite assumptions.
- Pusher: APC 10x6E (manufacturer-computed map), Avenger 2812 910KV (uncalibrated catalog model), ESC 0.97, auxiliary load 15 W.
- Battery: 4S 216 Wh nominal; a design target, not a measured pack.

## 1. Headline: what the model says

| Quantity | 2.98 kg all-Bambu central | 2.9 kg vendor comparator | Source |
|---|---|---|---|
| Best-range airspeed | 50–55 km/h (13.9–15.3 m/s); curve flat (1.855 vs 1.859 Wh/km) | 50 km/h | model |
| Minimum-power airspeed | ≤ 45 km/h (grid edge; not established) | ≤ 45 km/h | model |
| Cruise battery power at 50 / 60 / 70 km/h | 93 / 115 / 149 W | 91 / 114 / 148 W | model |
| Energy per km at 50 / 60 / 70 km/h (cruise only) | 1.86 / 1.92 / 2.12 Wh/km | 1.83 / 1.90 / 2.11 Wh/km | model |
| Airframe L/D at 50 / 60 / 70 km/h | 10.4 / 9.1 / 7.6 | 10.3 / 9.0 / 7.5 | model |
| Propeller / motor efficiency at 60 km/h | 0.70 / 0.79 | same | model (manufacturer map, catalog motor) |
| Trim alpha / equivalent tail incidence change at 60 km/h | +3.0° / −4.0° | +2.8° / −3.8° | model |
| Static margin, CG A (B) | 22 % (19 %) MAC, fuselage-moment band 19–26 % (17–24 %) | — | model |
| Hover battery power (conditional screening) | 580–780 W; ~11 Wh per 60 s | 555–750 W | model + manufacturer 6S proxy |

**One-at-a-time sensitivities on cruise battery power** (60 km/h, 2.98 kg; `sensitivities.csv`):

| Change | Effect |
|---|---|
| Parasite low / high | −16 % / +32 % |
| Props crossflow | +18 % |
| Forced transition at 5 % chord | +9 % |
| Motor R ×2 | +8 % |
| Motor I0 referenced to 14 V | +5 % |
| Auxiliary load ±5 W | ±4 % |
| CG B, mesh (4,8), NeuralFoil section moments, Ncrit 5, no fuselage moment | < 1 % each |

The band is driven by the parasite items and the stopped props, which are exactly the items no evidence pins down.

## 2. Why the retained Fumes model got ~2× more drag

The ladder starts from the prior model's own reported 54 km/h, 2.98 kg point and changes one thing at a time (`ladder.csv`). Propulsion and accounting are identical in every row. The prior propulsion chain is reproduced exactly: 5.48 N gives 168.3 W.

| Step | Drag (N) | Battery (W) | Wh/km | Δ drag |
|---|---|---|---|---|
| 0 Prior model, as reported | 5.48 | 168.3 | 3.12 | — |
| 1 Same choices, re-implemented (raw fin, no centre section, mesh (2,3), NeuralFoil section moments, CG 51.4 mm) | 5.28 | 162.8 | 3.01 | −0.20 (implementation/section differences) |
| 2 Equivalent fin, tail area restored | 5.35 | 164.5 | 3.05 | +0.06 |
| **3 Wing continued across the fuselage** | **4.44** | **139.7** | **2.59** | **−0.91** |
| 4 Mesh (6,12), gross Sref | 4.47 | 140.5 | 2.60 | +0.03 |
| 5 VLM camber moment | 4.47 | 140.6 | 2.60 | 0.00 |
| 6 CG A (47 mm) | 4.50 | 141.2 | 2.62 | +0.02 |
| **7 Fresh component build-up (replaces prior parasite 3.02 N)** | **2.97** | **100.9** | **1.87** | **−1.53** |

Two causes explain 97 % of the gap:

1. **Induced drag, −0.91 N.**
   - The prior VLM had no wing between y = ±92 mm, so each half-wing shed a strong inboard tip vortex. Its implied span efficiency was e ≈ 0.40.
   - A real fuselage carries lift across that gap. With the centre continuation the VLM gives near-field e ≈ 1.0. The independent lifting line gives e = 0.986 for the same planform.
   - The same gap also drove the prior trim to α ≈ 9° with a −11° tail incidence change. In that range the raw V-tail fin stations make the AeroSandbox VLM numerically singular (lift jumps to hundreds of N at slightly larger rotations; `docs/ENVIRONMENT.md`).
2. **Parasite build-up, −1.53 N.** The main differences are bounding-box frontal areas used where extracted silhouettes exist:

| Item at 54 km/h | Prior (N) | Fresh central (N) | Why |
|---|---|---|---|
| Main skids | 1.29 | 0.24 | Prior: 240×80 mm bounding box × 0.4 blockage ≈ 7700 mm². Fresh: extracted silhouette 1560 mm², Cd 1.1 |
| Motor + boom mounts | 0.47 | 0.22 | Same bounding-box effect; fresh uses isolated silhouettes × 0.6 installed exposure |
| Stopped props (aligned) | 0.32 | 0.11 | Prior: blade length × thickness × Cd 1.2. Fresh: aligned blades see section + twist only (assumption) |
| Lift motors | 0.56 | 0.44 | Short-cylinder Cd 0.8 vs 1.1 |
| Fuselage | 0.26 | 0.32 | Fresh adds roughness/interference factors |
| Booms, pusher motor, excrescences | 0.13 | 0.17 | Fresh adds an excrescence allowance |
| **Total** | **3.02** | **1.50** | |

Neither column is measured. The fresh values are handbook-range assumptions on extracted dimensions (`drag_buildup.py`, low/central/high). The prior's bounding-box areas overstate the extracted skid silhouette about 5×; that is a geometry error, not a matter of opinion.

## 3. Independent checks (rule 6)

| Check | Result | Independence |
|---|---|---|
| Hand method: own lifting line (e, CLα) + NeuralFoil section cd at MAC + same parasite build-up, vs VLM strip model | −3.0 % total drag at 60 and 70 km/h, both masses (`hand_check.csv`) | Independent induced/profile method; shares NeuralFoil and the parasite build-up |
| CLα: VLM whole aircraft 5.09/rad vs lifting line wing-alone 4.94/rad | consistent (VLM includes tail) | independent |
| Mesh (4,8) vs (6,12) | lift ±1 %, induced drag ±3 %, cruise power −0.1 % | numerical |
| Propulsion chain vs prior model | 168.28 W reproduced to 0.05 W | implementation reproduction, NOT independent physics |
| Hover: momentum theory (FM 0.65) vs T-Motor 6S bench interpolation | 665 vs 621–633 W at 2.98 kg (≈ 5 %) | independent, but bench is 6S with different props |

No physics-independent check of the parasite build-up exists. That build-up is the dominant uncertainty, and only measured or CFD component drag (or flight power) can close it.

## 4. Comparison with published claims (not calibration)

| Comparison point | Class | Model result | Reading |
|---|---|---|---|
| Optimal cruise 50–70 km/h | official (manual) | best range 50–55 km/h; power rises 60 % from 50 to 70 km/h | consistent with the lower half of the band |
| Peak efficiency at 0–3° AoA | official | trim α 1.2–3.0° at 60–70 km/h; 4.3–6.0° at 50–55 km/h (body x-axis) | reference axis undefined in the manual; not a pass/fail |
| "Virtually no pitching moment at 0° AoA" with CG set | official | saved-pose tail needs −4° (60 km/h) to −6° (50 km/h) equivalent incidence to trim at CG A | **Disagrees** unless ruddervator neutral differs from the saved pose or CG is further aft. Static margin ≈ 22 % MAC at CG A is large; open item |
| Cruise < 50 % throttle on 4S 10×6 | official | ideal PWM duty 0.54–0.61 at 50–60 km/h at 14.4 V (0.46–0.52 at 16.8 V) | throttle-to-duty mapping unknown; not comparable |
| Cruise power 80–110 W at 54–60 km/h | third-party (Flightony) | 91–114 W at 50–60 km/h, 2.9 kg | overlaps the claim; mass/payload inclusion unresolved |
| 2.0–2.5 Wh/km including VTOL | third-party | 1.83–1.90 Wh/km cruise-only; adding 2 × 60 s hover (≈ 22 Wh) over 100 km gives ≈ 2.05–2.1 Wh/km | plausible as a whole-mission figure |
| Hover ≈ 300 W | third-party | ideal induced power alone is 307 W at 2.9 kg; battery 555–750 W | **contradicted by momentum theory** |
| Effective L/D·η ≈ 5–6 (unlike 4+1 builders) | builder plausibility | m·g·V/P_batt = 4.2–4.4 at 50–60 km/h | below the band; different aircraft, so not a target |
| Prior Fumes model 3.1 Wh/km | model (historical) | 1.87 Wh/km at the same point | explained in §2 |

## 5. Range: aerodynamic demand vs mission accounting

Same aerodynamics, 2.98 kg, 216 Wh nominal, still air. Only the accounting differs (`missions.csv`).

| Accounting (explicit) | Cruise energy | 50 km/h | 60 km/h | 70 km/h |
|---|---|---|---|---|
| All nominal energy to cruise (reference only, not achievable) | 216 Wh | 116 km | 113 km | 102 km |
| Flightony-like: 90 % of nominal, no VTOL deduction | 194.4 Wh | 105 km | 101 km | 92 km |
| Prior Fumes: 90 % usable − 20 % nominal reserve − 30 Wh VTOL | 121.2 Wh | 65 km | 63 km | 57 km |

None of these is achieved performance or an operating range. Excluded throughout:
- wind, aging and cold (each a separate multiplier, not applied);
- transition energy beyond the allocation shown;
- qualified pack discharge. The prior P50B chart integration gives 184–201 Wh to 3.0/2.6 V per cell under ambiguous test labels.

The prior-accounting row is the only one with a reserve.

**No qualified operational range is stated.** Lift capability on 4S is unsupported: T-Motor rates the F90 1300KV for 5–6S, the manual says the lift system was primarily tested on 4S, and no 4S/7-inch data exist. The VTOL energy rows are conditional screening only.

## 6. Hover (conditional screening, Lucas answer 3)

At 2.98 kg (thrust 29.3 N, 4 × 7-inch discs, 0.0993 m², disc loading 295 N/m²):

| Level | Value |
|---|---|
| Ideal induced power | 321 W |
| Shaft power, FM 0.75 / 0.65 / 0.55 | 428 / 494 / 583 W |
| Battery power (motor 0.80, ESC 0.95, aux 15 W) | 578 / 665 / 783 W |
| T-Motor 6S bench proxy, motor input | 621–633 W |
| Energy per 60 / 120 / 180 s | 10–13 / 19–26 / 29–39 Wh |

Not established:
- available thrust at 4S and thrust/weight margin;
- per-motor current (≈ 46 A total from a 14.4 V bus, ≈ 11–13 A per motor) against ESC and motor thermal limits;
- control margin;
- download on the wing beneath the rotors;
- transition power.

## 7. Supported / assumed / unresolved / measurement-dependent

- **Supported:** extracted geometry and reference values; tail angle convention (3D normal check); propulsion arithmetic given its inputs; a prior-model discrepancy dominated by two specific modelling choices; the Flightony 300 W hover claim being impossible at 2.9 kg.
- **Assumed:** every parasite coefficient and exposure factor; stopped-prop orientation drag; centre-section carry-over; equivalent fin; fuselage moment; ESC/aux; usable energy; momentum-theory FM.
- **Unresolved:**
  - CG datum (A vs B) and z_cg; control neutral and trim deflection;
  - fuselage wetted area (0.3825 m² not reproduced from the coarse table);
  - motor R/I0 conventions; 4S lift capability; payload inclusion in vendor AUW; thrust-line moment; CLmax/stall.
- **Measurement-dependent:** cruise power at 2–3 speeds (closes the parasite band); prop-orientation A/B test; 4S F90 thrust-stand data; weighed mass/CG; pack discharge at flight loads and temperatures.

## 8. Recommended next steps (none started)

1. **Parasite band (largest lever):** one targeted check of the skid/motor/mount drag (OpenVSP parasite tool or a small CFD of the approximate hardware set), before scaling.
2. **Trim:** quantify ruddervator effectiveness (chord fraction, hinge geometry from CAD) to turn the equivalent −4° to −6° into a deflection, and test whether the manual's 0° statement implies a different neutral or CG.
3. **4S lift evidence:** a thrust-stand sheet for F90 + chosen 7-inch prop at 4S is the gate for any hover margin or operational range.
4. **Then Phase B:** scale using this baseline's component structure, carrying the uncertainty bands rather than one number.

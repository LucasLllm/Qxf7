# 02 Requirements and why they are what they are

All values are the team's own targets and estimates ("Fumes Technologies analysis, Oct 2026"), not measured results. Full reasoning: `reference/preliminary-design-report-2026-10.md` (Success criteria section) and `reference/qxf7-success-criteria-sources.md`.

## Payload: 750 g gross
- Gross = samples + UN3373 triple packaging + insulated (phase-change) box.
- Chosen by a **natural-breakpoint analysis**: a catalogue of 16 clinic deliveries, each scored (frequency/week × value). Coverage of weighted value: **15 / 61 / 90 / 91 / 97 / 98 / 100 %** at **0.3 / 0.5 / 0.75 / 1 / 1.5 / 2 / 3 kg**. The big jump is at 750 g (a full daily specimen batch fits); after that the curve flattens.
- Typical daily batch packed for winter ≈ **0.7 kg**: ~100 g blood tubes, 180 g urine containers, 100 g UN3373 packaging, **350 g thermal box** (estimate). Peak batch ≈ 1.2–1.3 kg (split into two flights).
- Thermal box estimate: 15×10×10 cm, 25 mm foam (k ≈ 0.025) → U ≈ 1 W/m²K; at ΔT = 50 K about 4 W loss ≈ 14 kJ/h → ~70 g phase-change material at 200 kJ/kg, doubled for margin.
- Specimens are ~60% of weighted value (32 of 52.7 points). STAT (urgent) value was revised down (Saskatchewan HEAR study: 89.4% of chest-pain cases evacuated regardless of troponin), so the mission is a **scheduled same-day batch run**, urgent flights a bonus.
- Biggest uncertainty: the insulated box mass. If it is 500 g instead of 350 g, a day's batch needs ~1 kg. The team plans to build and cold-test the box first.
- History: started at 0.5–1 kg (Goals), then 1.0 kg, then 500 g medications-only was considered, then fixed at **750 g**.

## Range: 95 km one way
- One way, straight line between two pads, **battery swap at each end**. The drone replaces only the unreliable segment of a trip (relay concept, e.g. Manawan → Saint-Michel-des-Saints CLSC → road).
- Chosen from 70 Canadian routes, then a Quebec-only ranking on six criteria (gap severity, demand, time saved, feasibility, range margin, adoption readiness; max 45; Manawan 39, Wemotaci 35). Routes reachable within 20 / 50 / 75 / 95 km: **4 / 7 / 14 / 16**. 95 km specifically adds **Wemotaci → La Tuque (91.5 km)**.
- History: 30 km radius (Goals) → 30–40 km legs → 80 km leg / 180 km still-air → 50 km leg (after correcting cruise power and adding VTOL energy) → **95 km** (Lucas judged the coverage curve flattens near 90–100 km; Claude flagged that a 95 km *winter* leg is physically implausible at this size class; see `07_prior_estimates_and_models.md`).
- The report explicitly says: *we will size the scaled aircraft for the 95 km one-way mission with the 750 g payload under explicitly defined conditions and reserves; wind and temperature limits will be set separately; long legs wait for suitable weather or use a battery-swap stop.*

### Still-air equivalent of a 95 km route (illustrative, from the report)
| Factor | Multiplier | Calm, mild day | Worst winter day (−30 °C, 25 km/h headwind) |
|---|---|---|---|
| Straight-line route | — | 95 km | 95 km |
| Detour (airspace, towns, terrain) | ×1.10 | 105 | 105 |
| Headwind 25 km/h at 70 km/h cruise, V/(V−w) | ×1.56 (winter only) | — | 163 |
| Cold dense air (ρ +18% at −30 °C) | ×1.07 (winter only) | — | 175 |
| Cold battery (pre-heated, ~10% less) | ×1.10 (winter only) | — | 193 |
| Reserve | ×1.25 | 131 | 241 |
| Take-off, landing, one go-around (hover 5–7× cruise power, ~3 min/leg) | +17 to 20 km | 148 | 261 |
| Usable battery (90% DoD) | ÷0.90 | 164 | 290 |
| Battery aging (85% capacity) | ÷0.85 | 193 | 341 |
| **Still-air range needed** | ×2.0 / ×3.6 | **≈190 km** | **≈340 km** |

The report states the 340 km case is not reachable by an electric drone this size and that these figures are illustrative equivalents, not a sizing requirement. Flying faster reduces the headwind penalty (at 100 km/h a 25 km/h wind costs ×1.34).

## Cruise speed: ≥ 70 km/h
- Latest Lucas clarification: retain ≥70km/h as the modified QxF7 cruise-speed target. This is airspeed for engineering modeling unless a future mission definition specifies groundspeed. It is NOT a demand that the standard Stork achieve its best efficiency at≥70km/h; PhaseA measures stock performance and its actual optimum. This clarification does not establish simultaneous full-mission capability at−30°C.
- So samples reach the lab within its hours, and to cope with northern winds of 30–40 km/h. The stock Stork's best efficiency is ~55–60 km/h; QxF7's bigger wing should be shaped for ≥70 km/h.
- Headwind multiplier comparison: 57/(57−25) ≈ 1.78 for the Stork vs 70/(70−25) = 1.56 for QxF7.
- An earlier analysis considered a 26 m/s (94 km/h) design cruise and found it costs ~13 km of winter range (39 vs 52 km at 7 kg); treated as a dash capability instead.

## Winter: down to −30 °C
- Normal winter operation with warmed batteries. Lucas does **not** want −30 °C as the headline differentiator (rare where they plan to fly); the goal is dependable operation in a defined, validated cold envelope.
- **Icing is out of scope**: no flight in known or forecast icing.
- Héma-Québec's transport boxes must handle −30 to +40 °C, independently validating the payload-box spec.
- No electric fixed-wing VTOL found publishes an operating limit below −20 °C; peer-reviewed Li-ion UAV work saw failure below about −25 °C unheated.

## Other criteria (from the report)
| Criterion | Target |
|---|---|
| Take-off and landing | Vertical, small pad |
| Cargo temperature | Samples kept in lab-required range |
| Safety | Return home or land safely on signal or power loss (BVLOS requirement) |
| Turnaround | Battery swap in a few minutes |
| Budget | Deferred by Lucas; no active cost cap/target in the performance study. Revisit after performance checks. |
| Approval | Transport Canada rules |

## What this means for the simulation work
- Every quoted range must state **airspeed, temperature, payload, AUW, reserve and energy accounting** (hover/transition energy separate; DoD, aging and reserve not double-counted).
- Report results for at least two conditions: **+20 °C ISA-ish, no wind** and **−30 °C** (ρ ≈ 1.45 kg/m³ at sea level), with and without a headwind case.

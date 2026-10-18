# Uncertainty register: standard Stork Phase A diagnostic baseline

Status classes: **S** = supported by checked evidence (within its stated scope) · **A** = assumption (declared value or band) · **U** = unresolved (evidence conflicts or is missing) · **M** = measurement-dependent (only bench/flight data can settle it).
The "effect" column gives the quantified sensitivity from `runs/2026-10-18_phaseA_diagnostic/sensitivities.csv` where available. Bands are declared sensitivities, not confidence intervals.

## Geometry and mass
| Item | Class | Basis / value | Effect on cruise power | Closes with |
|---|---|---|---|---|
| Span, gross Sref, MAC, wing chord/LE | S | Bundle; independent re-check agrees within 0.02 % | — | — |
| Wing twist distribution | S (stations) / A (joint averaging ±0.065°) | Measured stations; piecewise by panel | Small (not separately run) | — |
| Wing centre continuation through fuselage | A | Gross convention; real body lift carry-over unknown | Removing it roughly doubles VLM induced drag (ladder step 3) | Body-in-panel / CFD |
| V-tail fin cap | A | Equivalent trapezoid preserving area + QC | Not quantified | Panel/CFD with real fin |
| V-tail incidence convention | S | 3D normal check: −0.82° surface pitch | — | — |
| Control neutral (ruddervators/ailerons) | U | Saved pose aligned, not certified | Trim requires an equivalent −5° to −6° tail incidence change | Neutral/throw measurement |
| Fuselage wetted area | U | Convex envelope 0.3825 m², not exact, not a bound; coarse-table reproduction fails (0.364 m²) | ±10 % Swet inside the parasite band | Dense evidence / CAD skin |
| CG x | U | Case A 47.0 mm vs B 51.4 mm (datum ambiguity); z_cg unknown | See sensitivities (CG B) | Weighed aircraft |
| Mass 2.98 kg all-Bambu | A/M | Ledger central (slicer predictions + vendor masses + allowances), no cargo | Power ∝ ~m^1.5 at fixed CL | Weighing |
| Vendor 2.7/2.9 kg | U | Third-party; payload inclusion in AUW unresolved | Comparator only | — |

## Aerodynamics
| Item | Class | Basis / value | Effect | Closes with |
|---|---|---|---|---|
| Wing/tail profile drag | A | NeuralFoil, Ncrit 9 free transition (smooth) | Ncrit 5 / forced 5 % chord: see sensitivities | Surface/roughness tests, flight |
| Induced drag | S (method cross-check) / A | VLM near-field (6,12); lifting-line e cross-check | Mesh (4,8): within 3 % | — |
| Trim drag / tail load | A | Equivalent tail incidence; CG cases | CG case A vs B | Flight trim data |
| Fuselage pitching moment | A | Raymer K_fus 0.011 ±50 % | NP shift (stability.csv) | Panel/CFD, flight |
| Stall / CL_max | U | Not predicted (VLM is attached-flow; NeuralFoil pre-stall branch only) | — | Flight |
| Fuselage drag | A | Cf(Re)·Raymer FF·Q·Swet, Q 1.0–1.3, roughness ×1.0–1.3 | 0.25–0.52 N at 54 km/h | Measured/CFD |
| Skid, mount, motor, boom drag | A | Handbook Cd on isolated silhouettes × exposure | Main contributors to the low–high parasite band | Measured/CFD with hardware |
| Stopped lift-prop drag | A/M | Aligned vs crossflow plate model; windmilling not modelled | Crossflow adds ~0.6 N central at 54 km/h | Flight A/B test of prop orientation |
| Excrescences (horns, antennas, vents, pitot) | A | 1000 mm² equivalent × Cd 0.3–1.0 | 0.03–0.14 N | Inspection/measurement |
| Cooling flow / leakage | U | Not modelled | — | — |

## Propulsion and energy
| Item | Class | Basis / value | Effect | Closes with |
|---|---|---|---|---|
| APC 10x6E map | A (manufacturer-computed) | Vortex-theory map, not measured; pusher in fuselage wake not modelled | Not quantified | Static/wind-on prop test |
| Motor loss model | U | Catalog R 0.072 Ω (phase convention unclear), I0 1.17 A at 10 or 14 V | R ×0.5/×2 and I0 at 14 V: see sensitivities | Bench test with torque |
| ESC efficiency, aux load | A | 0.97, 15 W | ±0.02, ±5 W: see sensitivities | Bench measurement |
| Thrust-line/pitch coupling | U | Thrust assumed along the flight path; pitch moment omitted | — | — |
| Usable energy of 216 Wh pack | A/M | Conventions 100/90 %; prior P50B chart integration 184–201 Wh (ambiguous test labels) | Directly proportional to range | Pack characterisation |
| Pack mass ≤ 927 g | A | Design target, not a product | Mass case | Built pack |
| Cold (−30 °C) | U | Not run for range; density effect only would raise parasite power | — | Cold pack + flight |

## VTOL
| Item | Class | Basis / value | Effect | Closes with |
|---|---|---|---|---|
| Hover power | A (screening) | Momentum theory FM 0.55–0.75 → ~580–780 W battery at 2.98 kg; 6S bench proxy ~620–630 W | 60–180 s → ~10–39 Wh per hover phase | 4S F90 + prop test |
| Lift capability on 4S (thrust margin, current, thermal, control) | U | T-Motor rates 5–6S; manual says primarily tested on 4S; no 4S data | Blocks any qualified hover margin or operational range | 4S thrust stand test |
| Transition energy | U | Not modelled | — | Flight logs |
| Flightony "~300 W hover" | contradicted | Below ideal induced power at 2.9 kg (307 W) | — | — |

# 04 The baseline aircraft: Flightory Stork VTOL

Three tiers of evidence, never mix them up:
1. **Official (Flightory manuals v2)**: design data, trustworthy. Text in `reference/stork-manual-v2-text.txt` and `reference/stork-vtol-manual-v2-text.txt`.
2. **Third-party vendor (Flightony)**: appear **calculated, not flight-tested**. Label as such every time.
3. **Independent builders (ArduPilot Discourse)**: real logged flights on similar, not identical, aircraft.

## 1. Official Flightory data (manual v2, both manuals give the same table)
| Item | Value |
|---|---|
| Layout | High-wing pusher, V-tail; with VTOL Pack a 4+1 quadplane |
| Wingspan | 1620 mm |
| Wing area | **31 dm²** (an older 2021 blog post said 24 dm²; that is outdated, do not use) |
| Length | 1000 mm (verified = nose to pusher-mount face; see `05`) |
| Centre of gravity | **47 mm behind the leading edge at the wing root** |
| AUW | 1400–3100 g (manual); VTOL product page 1800–3100 g |
| Optimal cruise speed | 50–70 km/h |
| Airfoil | Selig **S3021** |
| Root chord / MAC | 230 mm / 195 mm |
| Aspect ratio | 8.3 |
| Wing loading | 45–100 g/dm² |
| Aerodynamic claim | "When the CG is properly set, the aircraft maintains longitudinal stability and produces virtually no pitching moment at a zero-degree angle of attack. Peak aerodynamic efficiency occurs between 0° and 3° AoA, aligning with typical cruising conditions." (manual p.5; CFD plots p.6–7) |
| Battery bay | 220 mm long, 80 mm high, 65–80 mm wide |
| Payload bay | 205 × 65 × 80 mm, shared with electronics |
| Skids | PC, tested to 3000 g take-off weight (VTOL manual p.29) |
| Cold-weather rating | None published |

### Recommended propulsion and electronics
| Item | Value |
|---|---|
| Lift motors | 4 × **T-Motor F90 1300 KV**, **7 in two-blade** props; 19×19 mm mount; "primarily tested on 4S", can run up to 6S |
| Lift booms | **2 × 10×10×500 mm square carbon tubes** (one per side, front + rear motor on each); boom-mount guide positions the tube at **150 mm from one end** (VTOL manual p.34–35); exact fore/aft installed position not yet resolved in CAD |
| Pusher | 28XX class; e.g. **BrotherHobby Avenger 2812 V5 910 KV** |
| Pusher props / power | 6S with 9453 (tri or two-blade): up to ~3.8 kg thrust, ~1280 W, ~50 A (60 A ESC). **4S with 10×6 two-blade**: ~2 kg thrust, 35–40 A ESC |
| Prototype test | **Cruise throttle below 50% on 4S with 10×6 prop** (manual p.13). This is a documentary comparison point; without the throttle mapping it does not give power, RPM or duty. |
| ESCs | 4-in-1 lift ESC (e.g. Velox V50A) + separate pusher ESC (e.g. Lumenier 51A BLHeli32) |
| Battery | 4S–6S Li-ion or LiPo |
| FC | SpeedyBee F405 Wing (or any MAVLink FC); ArduPilot QuadPlane 4+1 param file in Flightory Discord #free-files |
| GPS / RX / servos | Matek M10Q; Matek R24-D ELRS; 4 × EMAX ES08 MAII |
| Carbon | 10 and 8 mm × 1 m spars, two 10×10×500 booms, smaller spars and hinges |
| Print | LW-PLA or LW-ASA single wall for airframe; PC/PETG strong parts; fuselage 3–6% gyroid, wings 2–4% lateral lattice; 220 mm bed, 0.4 mm nozzle |

## 2. Flightony (third-party vendor, Beverly Hills) published numbers
**Label: third-party, optimal conditions, appear calculated** (range = usable Wh ÷ Wh/km exactly; their 2.2 Wh/km at 2.9 kg normalizes to exactly the Stork v1 figure, so likely scaled from it).
| Tier | Battery | AUW | Payload | Range |
|---|---|---|---|---|
| Explorer (US$4,995) | 4S3P Samsung 50E, 216 Wh, ~900 g | ~2.7 kg | up to 500 g | 70–85 km |
| Operator (US$7,495) | 4S4P Samsung INR21700-50E, 14.4 V, 20 Ah, 288 Wh (259 usable), ~1.2 kg | ~2.9 kg | 200 g | 100–130 km |

Also claimed: cruise 54–60 km/h; **2.0–2.5 Wh/km**; 80–110 W cruise; cruise current target 5–7 A on 4S; "about 300 W hover" (flagged earlier as physically implausible for a ~2.9 kg quadplane on 7" props: momentum theory gives well above that); APC 10×6E pusher; Velox V50A + Lumenier 51A. Implied dry weight (airframe + electronics, no battery/payload) ≈ **1.3–1.5 kg**. Internal contradictions: "100 km delivery radius" vs 100 km total range; "100 km one-way" on another page.

## 3. Independent builder flight data (unlike-aircraft plausibility evidence, not accuracy targets)
| Build | Config | AUW | Battery | Measured |
|---|---|---|---|---|
| Vince Hogg "Kite" | Printed 4+1 | not published | Li-ion | 2.0 Wh/km early; **2.5 Wh/km on a 100 km flight at 17 m/s**; **1.9 Wh/km at 18 m/s** after lift-prop alignment |
| Vince Hogg tilt-tri | 1.7 m, printed ASA | 3.7 kg | 4S4P 21700, 18 Ah | 6.5 A @17 m/s, 11.5 A @20 m/s, 16 A @23 m/s; max ~26–29 m/s |
| Michail Belov | 4+1 | 5.5 kg | 40×18650 (2.1 kg), ~12% worn | **195 W at 65 km/h** (13×10 on 560 KV); 110 km in 107 min in ~30 km/h wind, landed 3.2 V/cell |
| Tsung Xu v0.1 | 4+1, 1.2 m | 2.5 kg (1.8 empty) | 4S 8 Ah | early build; v0.2 claims ~3 h / 130 mi |
| **Flightory Stork v1** | fixed wing, no VTOL; earlier airframe (~24 dm² wing per 2021 blog, not v2) | **1.6 kg** | 4S 3.7 Ah | **1.21 Wh/km in loiter** (official) |

Normalized effective **(L/D × η) = m·g / (energy per metre)**: Vince tilt-tri @17 m/s ≈ 6.3; Belov 4+1 @65 km/h ≈ 5.0; Vince @20 m/s ≈ 4.4; Stork v1 loiter ≈ 3.6; Flightony claim ≈ 3.6. Real 4+1 builds land around **5–6**, which would put a ~2.9 kg Stork VTOL near **1.5–1.8 Wh/km in clean cruise** (estimate).

Lessons from these builders:
- **Stopped lift props are the biggest controllable loss**: Vince saw a **35% spread** in Wh/km depending on where the four dead props stopped, and **26% lower power** after adding an alignment system (ratchet disc + modified AM32 firmware). Belov estimated 14–22%, measured 10–12% with front props crosswise. Model this explicitly as a sensitivity.
- Wind inflates Wh/km on out-and-back flights; plan on power at airspeed and apply wind separately.
- Gusty air makes autothrottle hunt; winter ops will sit at the worse end.
- If the pusher fails at range, hover-only fly-back is only ~7–10 km.

Sources: discuss.ardupilot.org threads "100km on Printed VTOL" (/t/142115), "Cruise efficiency on a 4+1" (/t/143352), "Propeller alignment for improved efficiency in a quad VTOL" (/t/143624), "The VTOL compromise" (/t/130198); tsungxu.com; flightony.com/stork-vtol/specs.

## 4. Why the stock Stork falls short of QxF7 (from the report)
| Criterion | Target | Stock Stork VTOL | Verdict |
|---|---|---|---|
| Payload | 750 g packed | 200 g at full range; 500 g with smaller battery (Flightony) | Short |
| Still-air range | ~190 km carrying 750 g | 104–130 km carrying 200 g, best case (Flightony) | Short |
| Cruise speed | ≥ 70 km/h | 54–60 km/h for best efficiency | Short |
| Payload bay | Fits insulated box | 205 × 65 × 80 mm shared | Too small |
| Winter | −30 °C with warmed batteries | No data | Unknown |
| VTOL | Small pad | Yes | Met |
| Manufacturing | Printed construction | Yes | Budget assessment deferred; no cost pass/fail for this study |

## 5. License (blocking issue for operations, not for analysis)
Flightory license: "personal, non-commercial purposes"; "commercial or institutional use … strictly prohibited", covering companies, organizations, schools, universities, research institutions and **built aircraft**; modifications allowed for personal use only; commercial license by contacting Flightory. Scaling does not appear to escape the derivative restriction. **Keep vendor CAD out of any public repository.**

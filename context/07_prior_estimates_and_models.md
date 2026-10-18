# 07 Prior estimates and models (treat as hypotheses to test)

These come from earlier Claude analyses in the project chats. The code (`qxf7_energy_model.py`, `routes.py`, `analysis*.py`) and the report `QxF7 range with VTOL energy.md` lived in a previous cloud session and are **not available**. Only the numbers below survive. All are **estimates**, and the model was later judged **likely 1.5–2× too optimistic**.

## Generic energy model (chat "VTOL drone optimal range", 2026-10-10/11)
- Baseline scaled aircraft: **7.0 kg, wing area 0.70 m², 15-inch props**, CD0 = 0.025, overall propulsive η = 0.55, packaged Li-ion ≈ 230 Wh/kg (placeholder), empty-weight fraction placeholders 0.33–0.43, practical battery-mass fraction tops out around **50%**.
- ISA still-air consumption at 7 kg: **2.88 Wh/km at 17.5 m/s (best range)**, **4.26 Wh/km at 26 m/s**.
- Earlier error caught by Lucas: cruise power had been assumed ~200 W; corrected to a realistic **400–460 W** class (for the larger aircraft at higher speed). VTOL hover/transition energy was initially missing and then added.
- Winter factor stack used: detour ×1.10; headwind 7 m/s (P90 component from Sept-Îles December mean 4.5 m/s at 10 m, extrapolated to 100 m) → ×V/(V−7) = 1.368 at 26 m/s, 1.667 at 17.5 m/s; cold dense air ×1.143 at 26 m/s (×1.053 at 17.5); cold battery ×1.10; plus reserve, DoD, aging, VTOL.

### Max leg that closes on mass (that model)
| Case | MTOW ≤ 7 kg | ≤ 8 | ≤ 10 | ≤ 12 | ≤ 15 |
|---|---|---|---|---|---|
| Winter, best-range speed | **52 km** | 55 | 61 | 65 | 69 |
| Winter, 26 m/s | 39 | 42 | 46 | 48 | 51 |
| Fair weather, best-range speed | **105 km** | 113 | 124 | 132 | 140 |
| Fair weather, 26 m/s | 69 | 74 | 80 | 85 | 90 |

- A 50 km winter leg closed at ~**6.6 kg / ~545–580 Wh**. Quebec population covered per kg of MTOW peaked at 50 km.
- Fair weather (+15 °C, no wind, best-range speed): 50 km takes 3.6 kg, 100 km takes 6.5 kg, closure up to ~150 km.
- "Ideal day" (20 °C, no wind) max range of the 7 kg / 580 Wh aircraft: model ~175 km.

## Reality check against the Stork (same chat)
Using Wh/km ≈ m·g / (3.6 · L/D · η):

| | Mass | Wh/km | Wh/km per kg | Implied L/D·η |
|---|---|---|---|---|
| Stock Stork VTOL (2.0–2.5 Wh/km at ~3 kg) | ~3 kg | 2.0–2.5 | 0.67–0.83 | ~3.3–4.1 |
| Model, 7 kg at best-range speed | 7 kg | 2.82 | 0.40 | ~6.8 |
| Model, 7 kg at 26 m/s | 7 kg | 4.26 | 0.61 | ~4.5 |

The model assumed the scaled airframe is ~1.7–2× more efficient per kg than the real Stork VTOL. Scaling helps only ~10–20% (higher Re, bigger props). Revised (Stork-anchored) for 7 kg / 580 Wh:

| Scenario | Model | Stork-based, no scale credit | Stork-based, +15% |
|---|---|---|---|
| Cruise energy | 2.8 Wh/km | 4.7–5.8 Wh/km | 4.0–5.0 Wh/km |
| Ideal, 20 °C, no wind | ~175 km | **~85–105 km** | ~100–125 km |
| Winter design leg (−30 °C, 7 m/s headwind, all reserves) | 50 km | **~25–31 km** | ~29–36 km |

Caveat: the Stork 2.0–2.5 Wh/km figure is Flightony's (third-party, likely calculated) and may include VTOL phases; builder data (L/D·η ≈ 5–6) sits between the two. **Resolving this discrepancy is one of the main purposes of the simulation work.**

## Earlier rough sizing (chat "Drone market research and range")
Assumptions airframe+VTOL+avionics ~2 kg, 1 kg payload, L/D ~10, η 0.55, 65 km/h, ~25 Wh for two hover phases, 230 Wh/kg: 100 km still-air → ~240 Wh, ~4 kg AUW; 100 km real winter mission → ~400–450 Wh, ~5–5.5 kg. Stated ±30%.

## Report-level statements to stay consistent with
- No scale factor, span or mass has been chosen. Do not present any of the numbers above as the design.
- 95 km on the map ≈ 190 km still-air on a calm day, ≈ 340 km on the worst winter day (illustrative).

# 08 Benchmarks for sanity checks

Manufacturer figures unless stated. Full sourcing in `reference/qxf7-competitor-landscape.md`.

| Aircraft | Type / power | MTOW | Payload | Range / endurance | Cruise | Min temp (published / claimed) |
|---|---|---|---|---|---|---|
| **DeltaQuad Pro #CARGO** | Quadplane, electric | 6.2 kg | 1.2 kg | 100 km at 1 kg | 60–65 km/h | −20 °C |
| **Avy Aera** | 4+1 quadplane, electric, 1 kWh | 19.5 kg | 3 kg (2 kg w/ parachute) | 100 km standard (80–100) | 83 km/h | 0 °C (rated 0–40 °C per avy.eu; fact-check 2026-10-11) |
| **Aviant** (2021 fleet) | Fixed-wing VTOL, 2.6 m span | ~13 kg w/ batteries | ~1 kg (later 1.3–3 kg) | ~160 km; 124 km longest flight | up to 100 km/h | −26 °C flown (claim); third-party −15 °C |
| **Wingcopter 198** | Tilt-rotor, electric | ~25 kg | 4.7 kg | ~92–94 km (≈75 km at 5 kg) | 90 km/h | 0 °C (2021 sheet) |
| **Zipline P1** | Fixed wing, catapult, electric | — | ~1.8 kg | 80 km service radius | 101 km/h | not published |
| **Rigitech Eiger** | FW-VTOL, electric | — | 3 kg | 100 km (~80 at full load) | — | 0 °C rated, tested −7 °C |
| **Delair DT46** | FW-VTOL, electric | 25 kg (VTOL) | ≤ 5 kg | 3.5 h, >150 km flown | — | −10 °C |
| **Sky-Drones SkyLane 350** | FW-VTOL, electric | 35 kg | ≤ 10 kg | 2 h at 10 kg | 22 m/s | −20 °C |
| **Volatus Canary** | Multirotor | — | 4.5 kg | 20 km | ~80 km/h | tested −35 °C |
| **Waterloo WARG "Icarus"** | 4+1 quadplane (student) | ≤ 8 kg | — | — | — | — |
| **Stork VTOL (Flightony, calculated)** | 4+1 | 2.7–2.9 kg | 0.2–0.5 kg | 70–130 km | 54–60 km/h | — |

## Useful rules of thumb from these
- Payload / MTOW: Zipline P1 ~9%, Avy ~15%, Wingcopter ~19%, DeltaQuad ~19%; QxF7 targets ~11% (earlier estimate at ~7 kg).
- Every electric VTOL with a published cold rating stops between 0 and −20 °C.
- NTNU icing simulation: a 0.533 m prop's thrust turned negative after ~162 s in continuous-maximum icing at −5 °C; small props likely ice faster (untested extrapolation).
- Jämtland (Aviant, 2021): battery cooling problem below −20 °C, solved by insulating packs and limiting fuselage airflow; payload box held ≥ +2.5 °C for 70 min.

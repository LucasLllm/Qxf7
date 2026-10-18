# Independent Samsung 50E / Flightony battery and hover audit

## Verdict
- Flightony's **4S4P 20 Ah / 288 Wh** is arithmetically consistent with a **retail 5.0 Ah class** cell, not the discovered Samsung specification's guaranteed capacity. Using Samsung's standard minimum gives **19.6 Ah / 282.24 Wh**; the specified 1C rated minimum gives **19.012 Ah / 273.7728 Wh**. These Wh figures are nominal-voltage bookkeeping estimates, **not measured discharge energies or guaranteed deliverable Wh**.
- **39.2 A** is exactly four times Samsung's **9.8 A/cell continuous maximum**, assuming equal parallel sharing. It is a cell-rating sum, **not certification that the assembled pack safely supplies 39.2 A**.
- **~1,200 g** pack mass is plausible but unverified: 16 cells at Samsung's **69 g maximum** total **1,104 g**, leaving **96 g** for interconnects, insulation, wiring, connectors, protection and packaging if all cells are at that maximum. Actual cells may weigh less; 1,104 g is not a measured pack mass.
- **~300 W hover** is below the ideal out-of-ground-effect momentum-theory induced-power requirement for four 7-inch disks at either specified mass: **307.460 W at 2.9 kg; 339.808 W at 3.1 kg**, before real aerodynamic or electrical losses. Thus it is not supported as a steady, still-air, out-of-ground-effect electrical hover figure at these exact masses/disks. The approximation and unspecified test conditions prevent treating this as a measured real-power prediction or universally disproving every interpretation of '~300 W'.
- **4S3P 70–85 km** is a website claim, not independently verified flight performance. No raw aircraft flight logs, discharge trace, installed propulsion test or finished-pack thermal characterization was found in the pages reviewed. No P50B substitution or invented discharge curve was used.

## Sources and provenance
All source URLs below were actually fetched (HTTP 200), archived locally, and indexed with retrieval time and SHA-256 in `battery_sources.json`.

| Handle | Source | Evidentiary status |
|---|---|---|
| `battery_samsung_50e` | https://cdn.shopify.com/s/files/1/0721/2761/1190/files/samsung_50E.pdf?v=1715096646 | Samsung SDI-branded manufacturer specification **dealer-hosted by IMR Batteries**, not an SDI-origin download. Cover: **Tentative, version 0.2, date of application 2017/12/19**; revision history v0.2 dated 2017-12-07. Latest production revision and supplier authenticity remain to be confirmed. |
| `battery_imr_listing` | https://www.imrbatteries.com/products/samsung-50e-21700-5000mah-9-8a-battery | Actual product page from which the above PDF link was discovered. Retail evidence, not manufacturer authority. |
| `battery_flightony_specs` | https://flightony.com/stork-vtol/specs | Seller claims: fixed 4+1 QuadPlane; four T-Motor F90 1300KV lift motors; four 7-inch lift props; ~300 W hover; 4S4P 20 Ah, 288 Wh, 39.2 A, ~1,200 g; AUW range 1,800–3,100 g; 4S3P range 70–85 km. |
| `battery_flightony_performance` | https://flightony.com/stork-vtol/performance | Seller labels data as flight-tested, gives 300 W takeoff/landing, 80–110 W cruise, 259 Wh with 10% reserve; no raw log or measurement method on reviewed page. |
| `battery_flightony_home` | https://flightony.com | Seller states 2,900 g AUW, 16 Samsung 50E cells, 288 Wh, 200 g payload for 4S4P / 500 g for 4S3P. Hover table does not explicitly associate 300 W with a documented measured mass. |

No currently authoritative SDI-hosted 50E PDF was obtained. Search engines produced blocked or irrelevant results; an attempted Samsung SDI cylindrical-product route returned 404. These failures are not proof that such a document does not exist. Dealer-hosted specification accepted with the above limitations.

## Manufacturer-document readback
PDF page numbers here are physical PDF pages (printed page number is one lower after the cover).

- **PDF p.3, §3:** standard discharge capacity ≥4,900 mAh after 0.5C charge to 4.2 V / 98 mA termination, discharge at 0.2C = 980 mA to 2.5 V at room temperature; **1C = 4,900 mA**. Rated discharge capacity ≥4,753 mAh at 1C to 2.5 V. Nominal voltage **3.6 V**, charge voltage **4.2 V**.
- **PDF p.3, §3.9:** **9,800 mA for continuous discharge; 14,700 mA not for continuous discharge**. The latter is not a validated transient allowance for any unspecified duration or temperature.
- **PDF p.3:** cell weight **69 g max**. **PDF p.4:** charge surface temperature **0–45°C**, discharge **−20–60°C**; over-temperature protection should not exceed 60°C at the hottest cell surface.
- **PDF p.7, §7.6:** relative discharge capacity 100% at 0.2C, 97% at 1C, 95% at 2C under the specified test. This is a capacity table, **not a voltage-versus-time or energy trace**. Do not infer real pack Wh from it without measured voltage integration.
- **PDF pp.13,17–19:** continuous discharge below the maximum; cell-block voltage monitoring, current/temperature protections, welded rather than directly soldered cells and short-circuit protection. Finished-pack validation remains required.
- Document discrepancy: **PDF p.3** lists diameter max **20.25 mm**, while the **outline figure on PDF p.5** says max **21.25 mm with sleeve**, height max 70.80 mm. The document is tentative; use the drawing only as a provisional packaging reference and resolve with the current supplier specification before release.

## Executed battery arithmetic
Calculated by `battery_calculations.py` with the requested research interpreter; full machine-readable output in `battery_calculations.json`.

| Quantity | 4S4P (16 cells) | 4S3P (12 cells) |
|---|---:|---:|
| Nominal / fully charged voltage | 14.4 / 16.8 V | 14.4 / 16.8 V |
| Retail 5.0 Ah class pack capacity | 20.0 Ah | 15.0 Ah |
| Standard-minimum pack capacity | 19.6 Ah | 14.7 Ah |
| 1C rated-minimum pack capacity | 19.012 Ah | 14.259 Ah |
| Retail-class nominal energy estimate | 288.0 Wh | 216.0 Wh |
| Standard-minimum × nominal-voltage estimate | 282.24 Wh | 211.68 Wh |
| 1C rated-minimum × nominal-voltage estimate | 273.7728 Wh | 205.3296 Wh |
| 90% of retail-class estimate | 259.2 Wh | 194.4 Wh |
| 90% of standard-minimum estimate | 254.016 Wh | 190.512 Wh |
| 90% of 1C rated-minimum estimate | 246.39552 Wh | 184.79664 Wh |
| Cell-only mass at 69 g/cell maximum | 1,104 g | 828 g |
| Equal-sharing cell continuous-rating sum | 39.2 A | 29.4 A |
| Cell current at claimed 300 W / 14.4 V | 5.2083 A | 6.9444 A |
| Cell current at claimed 300 W / 10.0 V | 7.5 A | 10.0 A |

300 W at 14.4 V means **20.8333 A pack current**; at 10.0 V it means **30 A**. The 10.0 V case is only an arithmetic illustration at four times the cell test cutoff; it is **not a recommended operating voltage**. It shows that constant-power 4S3P operation could exceed 9.8 A/cell near depletion even before current imbalance, other loads or transients. Protection cutoff should be above the manufacturer's boundary with allowance for sag and aircraft control margin. If 300 W denotes shaft rather than pack input, current calculations must include motor/ESC loss and auxiliaries.

Removing one cell per series group reduces cell-only maximum-mass sum by **276 g**; it does not establish actual pack or aircraft mass difference. At 194.4 Wh (retail-class 90% estimate), 70–85 km implies **2.7771–2.2871 Wh/km** if that energy budget covers the entire mission. That is only a bookkeeping implication; takeoff, landing, reserve, speed, wind, payload and delivered pack Wh must be measured to validate range.

## Ideal-hover lower-bound calculation
Assume four equal, non-overlapping 7-inch lift disks, steady hover in still air **out of ground effect**, thrust equal to aircraft weight, uniform ideal actuator disks, no additional vertical thrust from the horizontal pusher. Use **ρ = 1.225 kg/m³**, **g = 9.80665 m/s²**, diameter **D = 0.1778 m**.

`A = 4π(D/2)² = 0.0993146659031 m²`

`T = mg; vi = sqrt(T/(2ρA)); Pideal = T vi = T^(3/2)/sqrt(2ρA)`

| AUW | Weight/thrust | Ideal induced velocity | Ideal induced power | 300 W below ideal by |
|---|---:|---:|---:|---:|
| 2.9 kg | 28.439285 N | 10.811093 m/s | **307.459754 W** | 7.459754 W |
| 3.1 kg | 30.400615 N | 11.177674 m/s | **339.808172 W** | 39.808172 W |

Ideal/300 W ratios are **1.024866** and **1.132694** respectively. Even a lossless drive at a 300 W electrical input would not reach these ideal out-of-ground-effect values. Real rotor profile/swirl losses, nonuniform inflow, airframe interference, motor/ESC losses and auxiliary demand generally add input power; **no efficiency number is assumed and no actual hover wattage is asserted**. Ground effect, environmental density, true mass, diameter, measurement averaging and whether power denotes electrical or shaft input must be specified when comparing a test to this model. This calculation does not validate climb or transition power.

## Evidence needed before engineering acceptance
Obtain the current cell/lot specification; weigh finished packs; measure cell sharing, pack voltage sag and hottest-cell temperature through representative duty cycles and minimum allowed SOC; validate interconnect/connector/protection ratings and cutoff behavior. Measure installed four-rotor thrust and **pack-input power** across voltage with the actual props, motors, ESCs and airframe, then supply raw hover/transition and full-mission logs tied to mass, payload, weather and reserves. Until then, battery arithmetic is checked, but safe pack current, usable energy, range and hover performance remain unverified.

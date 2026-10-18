# Original Stork: manual-compatible range reference

**Selection:** Four T-Motor F90 1300KV / 7-inch two-blade lift props; BrotherHobby Avenger2812 V5 910KV / 10x6 two-blade cruise; common4S supply. Manual-listed Velox V50A original lift ESC, Lumenier51A BLHeli32 cruise ESC, SpeedyBee F405 Wing, Matek M10Q GPS+compass, four EMAX ES08MAII servos and Matek R24-D ELRS. Exact prop model/pitch/handedness and live-model availability remain unresolved. These are source recommendations, not final compatibility qualification.

**Range-first battery research reference:** professionally engineered4S3P P45B high-power Li-ion,13.5Ah typical,194.4Wh nominal,920–1000g assumed finished mass;960g calculation point. No finished product endorsed by the manual or admitted here.4S2P9Ah and published4S5000 LiPo remain comparisons. Manual allows both chemistries and4–6S, and reports primarily4S prototype lift testing and4S10x6 cruise below50% throttle. That does not demonstrate this13.5Ah combination or its optimality.6S is explicitly permitted for BOTH lift and cruise: VTOL p13 allows the same F90 lift hardware up to6S; p11 specifies BH2812/9453 on6S and a60A6S-capable cruise ESC.4S selection here is not evidence of superior range versus matched6S.10x6 is the4S example, not an automatic6S prop match.

## Estimated reference specs

Original1.62m span /0.31m² area /1m length. Published cruise50–70km/h; published AUW1.4–3.1kg is not our structural certification. Numerical range below assumes1950g dry equipped, zero cargo,20% nominal-energy reserve,10Wh total VTOL/transition budget and15W avionics, no heating. Larger battery increases mass and lowers payload headroom.

| Battery | Nominal Wh | Assumed AUW kg | Max dry g, zero cargo +100g growth | Max dry g,500g cargo +100g growth |
|---|---:|---:|---:|---:|
| 4S5000 LiPo reference | 74.0 | 2.398 | 2552 | 2052 |
| 4S2P P45B reference | 129.6 | 2.600 | 2350 | 1850 |
| 4S3P P45B range research reference | 194.4 | 2.910 | 2040 | 1540 |

## Conditional still-air60km/h estimates

| Battery | Working pack W / cruise min / total path km | Higher drag/loss pack W / cruise min / total path km |
|---|---|---|
| 4S5000 LiPo reference | 144 / 21 / 21 | 276 / 11 / 11 |
| 4S2P P45B reference | 146 / 38 / 38 | 280 / 20 / 20 |
| 4S3P P45B range research reference | 151 / 58 / 58 | 286 / 30 / 30 |

These are sensitivity outputs, not confidence intervals, endurance ratings, safe range or flightworthiness. Ideal symmetrical return radius is half total path only; wind, route, extra landing/relaunch, reserve and regulation change it. Delivered/lighter return not modeled.50/70kmh rows retained in RESULTS.json; no proven best-range speed, stall or top speed.10Wh VTOL allowance is assumed, not hover evidence.

## Why this selection

4S10x6 is the manual-described efficiency-oriented stock option; F90 and BH2812 are its named exact windings, not winners of an exhaustive motor comparison.3P has the largest retained high-power4S P45B reference compatible with3100g under the chosen1950g dry sensitivity and100g growth allowance.4P at1270g would exceed that budget. This is conditional mass screening, not a global optimum. If actual dry mass/desired cargo is higher, reduce battery capacity or revisit the stock objective.

## Remaining gates and next steps

1. Reconcile complete stock installed mass/CG using retained print prediction and actual hardware. Do not reuse older1693g central allowance as established mass. Preserve original geometry/material requirements.
2. Lock exact7-inch two-blade CW/CCW props and10x6 cruise product, hub, retention and full4S duty maps. Manual dimensions do not certify adapter or mount compatibility. F90 retailer5–6S wording versus manual4S test evidence stays a documented source distinction.
3. Obtain qualified finished4S3P pack mass, enclosure dimensions, pulse/continuous current, cooling, connector/lead protection and low-SOC landing/relaunch evidence. P45B45A/cell has80°C cutoff context;3P135A arithmetic is NOT an aircraft safe rating. No amateur pack-build instructions or current approval.
4. Check power distribution for total lift+cruise+avionics demand. Manual ESC labels do not certify combined bus current. Retain separate cruise ESC; specify capacitor, regulated supply, sensing, harnesses, fault protection, balance charger and approved battery handling.
5. Verify ArduPlane/QuadPlane support for exact FC revision, motor/servo output allocation, GPS/compass and failsafes; manual Mavlink wording alone is not VTOL firmware qualification. GPS example may be EOL. Optional FPV adds mass/power; none assumed here.
6. Analysis/simulation, props-off configuration and approved supervised subsystem tests with pass/fail and stop thresholds precede any flight. Measure thrust/power/RPM/temperature and actual cruiseWh/km before endorsing range. No deployments/energization/flights authorized.

## Provenance and verification

Both supplied original PDFs inspected; VTOL pp5,8,11–13; base pp13–14. P45B public datasheet and existing published LiPo evidence retained. SOURCE paths/hashes and numerical assumptions in RESULTS.json. Arithmetic/source assertions verify bookkeeping, not flight safety. No purchasing, CAD mutation, original-file overwrite or hardware action.

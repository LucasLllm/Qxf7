# Independent Flightony Stork configuration check

Generated UTC: 2026-10-10T01:38:30.338620+00:00

## Conclusion
The unchanged previous hybrid model does not reproduce the seller's headline ranges at its advertised masses. This is a model discrepancy, not proof that their flight results are false. The largest exposed weakness in our model is empirical drag for landing-gear and mounting hardware. The ~300W hover assertion is more seriously inconsistent with ideal free-air hover at the advertised2.9kg/7-inch configuration. No flightworthiness or legal-operational conclusions follow.

## Provenance and unbiased procedure
- Retrieved live seller specifications, performance, Operator and Explorer pages (HTTP200); copied in this folder with hashes in SELLER_SOURCES.json.
- Operator advertised AUW2.9kg, Explorer2.7kg. The seller does not clarify whether these masses include the rated cargo; we model those total masses without inventing that distinction.
- Same source-derived reconstructed/idealized Stork profiles, VLM trim, NeuralFoil strip drag, component buildup, APC10x6E forward map and BrotherHobby2812V5/910KV conditional electrical model as before. No aerodynamic coefficients fitted to seller range/power.
- Nominal Samsung50E energy288Wh/216Wh admitted for the primary like-for-like comparison. This is optimistic nominal accounting, not integrated measured50E discharge energy. Loaded pack-terminal voltage checked at12,14.4,16.8V; inadequate points never treated as achievable.
- Reserve is10% ONCE, unlike the older more conservative accounting; included seller's stated VTOL/transition energy13.333Wh. Remaining cruise energy245.867Wh/181.067Wh. We also report the old30Wh mission allowance separately. Neither allowance proves hover/transition capability.
- Central losses: previous motor resistance convention1x, idle reference10V, ESC97%, auxiliaries15W assumed. Results for other motor conventions retained in CSV/JSON. Seller DJI O3/Pi/LTE installation has not had measured auxiliary consumption;15W is not a vendor-specific verified value.
- Sweep50–70km/h every2km/h, smooth/rough surfaces and stopped aligned/crossflow lift props. Windmilling not included. Still-air one-way distance, not delivery radius.

## Battery and published-spec checks
| Quantity | Seller | Independent check |
|---|---|---|
|4S4P energy|288Wh|Correct arithmetic for16 x5Ah x3.6V; not guaranteed usable energy|
|10% reserve|259Wh available|259.2Wh before VTOL/transition;245.87Wh after seller13.33Wh allowance|
|4S4P current|39.2A|4 x9.8A cell rating; whole-pack BMS, conductors, thermal behavior still unqualified|
|Cell capacity|5000mAh|Retail nominal class; mirrored Samsung tentativev0.2 specifies minimum4900mAh at0.2C,4753mAh at1C|
|4S4P conservative nominal-capacity arithmetic|20Ah288Wh|4900mAh basis:19.6Ah282.24Wh; minimum capacity x nominal voltage still not measuredWh|
|Pack mass|~1200g|16 x69g max cell mass=1104g leaves96g for connections, insulation, BMS and packaging; plausible, not weighed|
|Aspect ratio|8.3|Using listed1.62m and0.31m² gives8.466; small published-dimension discrepancy|
|Airfoil|S3021|Original Flightory manual also declaresS3021; simulation uses source-derived profiles rather than replacing them with a generic name|
|Cruise speed|optimal54–60km/h|Our best tested50–70 band is52km/h for smooth-aligned4S4P;50km/h for3P/other cases, a band-edge result not global optimum|
|Cargo capability|200g/500g|No independent structural, CG or installed-weight qualification; do not assume ranges achieved with full cargo|
|4S3P max current|not stated|29.4A cell-rating sum, not completed pack qualification|

## Same-model results at54km/h
This is the best tested point within their54–60km/h cruise band for all tabulated cases. Total battery-terminal power includes15W auxiliary allowance. Range uses nominal energy,10% reserve and seller13.33Wh noncruise budget.
|Configuration|Surface / stopped lift props|PowerW|Wh/km|Range km (seller allowance)|Range km (30Wh allowance)|
|---|---|---:|---:|---:|---:|
|4S4P2.9kg|smooth aligned|165.3|3.06|80.3|74.9|
|4S4P2.9kg|smooth crossflow|226.6|4.20|58.6|54.6|
|4S4P2.9kg|rough aligned|242.3|4.49|54.8|51.1|
|4S4P2.9kg|rough crossflow|323.3|5.99|41.1|38.3|
|4S3P2.7kg|smooth aligned|158.6|2.94|61.7|56.0|
|4S3P2.7kg|smooth crossflow|219.0|4.06|44.6|40.5|
|4S3P2.7kg|rough aligned|234.8|4.35|41.6|37.8|
|4S3P2.7kg|rough crossflow|314.9|5.83|31.0|28.2|

Seller comparison:4S4P104–130km,4S3P70–85km,cruise80–110W,efficiency2.0–2.5Wh/km. Our smooth-aligned4S4P rises from165.3W at54km/h to191.2W at60km/h. No claimed matched measured result is available.

## Why this is not a verdict against their range
At2.9kg/54km/h the modeled induced drag1.770N plus profile0.580N is2.350N. Modeled remaining parasite drag3.024N gives total5.374N. Gear1.286N and mounts0.465N are32.6% of total: these use bounding-envelope areas, blockage and assumed pressure coefficients, not resolved airflow or measured drag. This proxy can overestimate actual streamlined/partially shielded structures; interference can also be underestimated.

Omission sensitivity tests (NOT feasible replacement aircraft predictions):
|Diagnostic at2.9kg54km/h|BatteryW|Conditional range km|
|---|---:|---:|
|remove gear mount proxy only|117.4|113.1|
|lifting surfaces only|86.1|154.2|

Removing gear/mount drag ONLY moves165.3W to117.4W and80.3km to113.1km. The aircraft still physically has those parts; this is not a justification to delete their drag. It demonstrates that the unvalidated empirical drag model can account for much of the disagreement. Removing ALL non-lifting-surface drag gives86.1W: not a whole-aircraft result.

## Hover physics check
In calm free-air hover, ideal actuator-disk momentum theory gives P_ideal = T^(3/2)/sqrt(2*rho*A), with T=mg, A=4*pi*(0.1778/2)^2, rho=1.225kg/m³ and g=9.80665m/s². Four equal separate disks; no ground effect, forward-flight wing lift or obstruction; real motor/ESC and blade-profile losses are absent.
|Total mass|IDEAL rotor induced power|
|---|---:|
|2.7kg|276.2W|
|2.9kg|307.5W|
|3.1kg|339.8W|

At2.9kg, ~300W electrical input is below the ideal307.5W rotor requirement. The approximation/rounding alone is not the central issue: real losses should make the electrical demand appreciably HIGHER. Illustrative assumptions figure-of-merit0.65–0.80 and motor+ESC efficiency0.85–0.90 give427–556W. These efficiency assumptions are not measured F90 performance. Different mass, larger props, ground effect or a different definition of power could explain a seller number; none should be silently assumed. Retained F90 manufacturer material lists5–6S;4S hover capability remains a hardware qualification gap. No motor was energized.

## Seller energy-budget consistency
Their range table is approximately259Wh divided by2.0/2.2/2.5Wh/km. If those efficiencies already average the complete mission, that arithmetic is consistent. If they mean cruise-only efficiency, the13.33Wh takeoff/transitions/landing must also be deducted, giving122.9km at2.0Wh/km and98.3km at2.5Wh/km rather than129.6/103.7km. The definitions are insufficiently explicit.
Cruise power80–110W at54km/h corresponds to1.48–2.04Wh/km; at60km/h1.33–1.83Wh/km, before any separately excluded auxiliaries.2.0–2.5Wh/km corresponds to108–135W at54km/h. Their listed100km mission, including13.33Wh noncruise, implies1.61–2.17Wh/km with80–110W cruise; not the same scope as every listed headline.
130km at54km/h with seller13.33Wh noncruise and10% reserve requires about102.1W total cruise battery power;104km requires127.7W. These are achievable-power requirements from energy accounting, not aerodynamic confirmation.

## Mass sensitivity relevant to our build
Operator AUW2.9kg minus1.2kg pack implies1.7kg for everything else if the stated AUW is unloaded. Our prior planned dry mass is2.0567kg,356.7g more. A1.2kg pack would make our aircraft3.2567kg with no payload, above the3.1kg documentary planning screen. This does not prove their lighter aircraft is impossible: materials, print settings, equipment and payload inclusion differ. Do not import their AUW into our bill of materials.
At our dry mass plus1.2kg4P pack, smooth-aligned54km/h gives179.8W and73.8km using seller reserve/mission allowances. For3P, a proportional900g pack is an ASSUMPTION, not a seller weighing; total2.9567kg gives167.3W58.4km.

## Numerical checks and remaining limits
- 220 aerodynamic rows,3960 propulsion/loss cases,12951 accounting assertions;5 pure-accounting tests passed. Unsupported count0; voltage-infeasible rows remain marked and have no achieved range.
- Original input files unchanged, verified by before/after SHA256. Saved CSV/JSON contain the actual executed outputs, not synthetic seller data.
- Fresh60km/h mesh checks at2.9kg/2.7kg:2x3,3x4,4x5 resolutions.2.9kg total drag5.8162/5.9147/5.9318N;3x4→4x5 changes total drag~0.29% and lifting-surface drag~0.78%. This improves numerical evidence at THESE points only; same-method comparison retains2x3. Not a complete trim/CG/convergence acceptance or experimental validation.
- Working CG and equivalent V-tail trim retained. Installed CG/control authority, body/thrust-line moments, trim at low speed, hinge/cavity drag, lift-prop stopping and continuous thermal behavior remain unqualified.
- The older tentative Samsung mirrored datasheet is evidence for published cell characteristics, not certification of the seller's specific cell lot or finished battery.50E discharge/sag/temperature dependence and low-SOC hover capability are not established by nominalWh arithmetic.
- Seller labels performance as flight tested but the inspected public pages do not supply downloadable raw flight logs, instrument calibration, ambient conditions, exact AUW/CG/prop orientation or power-channel definitions. We cannot independently reproduce their claimed flight measurements from those pages.

## Evidence needed to resolve the discrepancy
Request a representative ArduPilot BIN log (batteryV/current, airspeed, GPS/wind estimate, throttle/RPM, flight modes, duration), current-sensor calibration, exact flight mass/CG/payload, battery dischargedWh, prop stopping orientation and hover power/mass. Independently measured installed cruise power will adjudicate the drag model far better than selecting whichever estimate sounds preferable.

## Source links
- https://www.flightony.com/stork-vtol/specs
- https://www.flightony.com/stork-vtol/performance
- https://www.flightony.com/configure/extended-range
- https://www.flightony.com/configure/standard
- Mirrored Samsung tentativev0.2 datasheet: https://cdn.shopify.com/s/files/1/0721/2761/1190/files/samsung_50E.pdf?v=1715096646
- https://www.imrbatteries.com/products/samsung-50e-21700-5000mah-9-8a-battery
- APC map and manufacturer motor-source provenance: previous aircraft-specific-analysis/propulsion/PROPULSION.json (retained, unchanged).

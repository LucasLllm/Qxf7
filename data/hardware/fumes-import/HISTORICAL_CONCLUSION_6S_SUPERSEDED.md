# Stock Stork range-selection conclusion

## Recommendation and decision boundary
**Use 6S2P P50B as the leading source-backed, high-energy finished-pack candidate for an unloaded standard-size reference; retain 4S3P P50B as the equal-energy comparator. Neither is a proven cruise-range winner or an approved flight configuration. Do not purchase/freeze the final package from this study alone.**

Why this candidate: a finished 6S2P SkyVolt catalog variant declares 10 Ah,216 Wh,868±3 g and156×66×43 mm. It has source-backed packaging rather than an unquoted custom-pack mass. Six series cells reduce common-bus current relative to an equal-energy4S3P pack at the same electrical power. The F90 manufacturer rates the1300KV motor for5–6S, while the Stork manual documents4S use and a6S alternative. These are practical integration reasons, NOT evidence of superior cruise Wh/km. Complete-pack current/thermal QA remains open.

**The stock/current-material aircraft is not a substantiated solution to Lucas's original500 g–1 kg, long-radius delivery goal.** Treat unloaded only as a reference, not a replacement requirement, and preserve the one-final-aircraft decision. The published1.4–3.1kg AUW range is used here as the requested stock planning screen—not a measured structural limit or certification.

## Reference package (not an order list)
|Subsystem|Reference or candidate|Status|
|---|---|---|
|Airframe|Original unscaled Stork fixed4+1, current all-Bambu print/material plan|Geometry/material estimates; no measured finished mass/weather qualification|
|Lift|Four T-Motor F901300KV; manual7-inch lift-prop class; four VeloxV5050A ESCs|Specific prop identity/handedness, installed mount/harness and exact low-SOC thrust still need closure|
|Cruise motor|BrotherHobby Avenger2812V5910KV CW|Manual candidate; correct rotation/threading/prop installation still must be checked|
|4S comparator|10×6 two-blade/manual class; Lumenier51A cruise ESC|Manual4S prototype recommendation; no independent exact forward-flight map|
|6S candidate|9453/manual cruise-prop family; VGOOD60A reference ESC|Exact two-/three-blade identity unresolved: BH's published9453F chart is a folding TRI-blade test, not proof for a two-blade candidate. VGOOD source mass58.1g is used; command/thermal/installed fit not qualified|
|High-energy finished pack|SkyVolt6S2P P50B10Ah,216Wh,868±3g,156×66×43mm|Catalog variant verified, not factory QA, traceability or measured continuous-current approval|
|Controls/avionics mass reference|Existing SpeedyBeeF405Wing / fourES08MAII / M10Q / R24 ledger plus assumed pitot/sensing allowances|Existing baseline only; actual firmware, interfaces, distribution protection and install are not frozen|

**No fully selected or qualified complete flight BOM exists yet.** Generic prop families and wiring/servo geometry cannot be silently converted into exact validated products.

## Installed mass reconciliation
Read `mass_reconciliation.json` for every term and source hash. Printed mass comes from the current58-native-part/82-print-instance mass CSV, not the older assumed1.95kg dry total. All values below are PLANNING, not scales measurements.

|4S dry-mass case|Mass before battery/cargo|
|---|---:|
|Lower installation allowance|1.890kg|
|Central|2.057kg|
|High, including15% printed-mass uplift and high installation allowances|2.467kg|

A separate100g unused growth allowance is retained in the mass screen, rather than being spent on a battery. It is not a battery-energy reserve.

The central4S case leaves about943g for battery when unloaded,443g with500g cargo, and no allowance for1kg cargo while retaining100g growth. The model rejects overweight cases before displaying their range.

The modeled6S package replaces the7.5g4S cruise ESC with the source58.1gVGOOD unit: +50.6g. The6S prop mass is deliberately held at the existing20.1g proxy, not asserted measured; it remains an open term. This yields about2.107kg central6S dry. With868g pack: about2.975kg physical reference and3.075kg after reserving100g growth. Using871g upper quoted pack mass requires measured complete6S dry mass **≤2.129kg**, leaving only about22g beyond the central estimate after the100g reserve. The high-mass case rejects this pack. Added winter/weather equipment is not included.

For the documented lighter Orryx4S2P P45B pack556±3g, the corresponding measured4S dry ceiling is2.441kg unloaded, but only1.941kg with500g cargo. Its advertised90A continuous/120A10-second rating is a vendor claim; neither the timed peak nor cell arithmetic establishes aircraft approval.

A custom4S3P P50B pack uses the same12cells/216Wh as6S2P. Its finished mass is not quoted/verified.902/927/952g are sensitivities, not catalog products, and the cell maximum-mass sum is not a pack minimum-mass bound.

## Geometry precheck actually performed
Reran the existing native-source/archive/manifest hash and placement verification (`GEOMETRY_PROVENANCE_TEST.txt`). Checked the quoted catalog boxes against those preserved native-body/access envelopes:
- SkyVolt156×66×43mm is a subset of the previously checked173×70×51mm flat envelope at the inherited source pad location.
- Orryx152×44×44mm is a subset of the previously checked161×46×50mm envelope.
- The same120mm straight vertical bare-envelope hatch sweep is a subset as well.

See `catalog_envelope_precheck.json`. This is mathematical subset reuse of prior nine-body native Boolean/access checks—not a fresh full assembly Boolean calculation or physical insertion test. Unchecked leads, connectors, bends, insulation, straps, sensors, cooling and manufacturing tolerances can still prevent installation. Actual pack COM and final aircraft CG are unknown; the inherited working CG plane is not a released flight limit.

## What the performance evidence does and does not say
The manual reports flying the4S2812V5910KV/10×6 configuration and recommends it for range/endurance. The independent BrotherHobby image was read directly: its2812V5910KV chart uses6S and **Folding9453F tri-blade**, static thrust/current/RPM, with no forward airspeed, no paired4S10×6 run and no shaft-torque measurement. Its watts are electrical volts×amps, not shaft power.

APC has genuine computed10×6E forward-airflow data, but it is a computational prop map—not an exact BH motor efficiency map, nor an independently matched6S9453 comparison. Therefore a unique best-range cruise package cannot be identified from the available evidence. Fixed cruise efficiency is intentionally equal for all voltage cases in this study; small modeled mass differences are not a motor/prop ranking.

F90 thrust interpolation uses its catalog GF7042 test, with exact candidate prop correspondence still open. At the3.1kg reference, the model estimates about637W hover including15W auxiliaries.90seconds is about15.9Wh before installation/wind/climb.10Wh is not a suitable heavy-stock allowance. Low-voltage/current calculations are sensitivities, not measured low-SOC capability; check cell thermal cutoffs versus finished-pack limits and actual timed current profiles.

## Executed illustrative mission sensitivity—not a range promise
Ran2,916 saved cases covering three dry-mass allowances, nine pack/mass references,0/500/1000g payload,50/60/70km/h, two explicit assumed drag/efficiency cases, steady signed0/10km/h wind and three VTOL-energy budgets. Some pack entries are explicitly unquoted planning sensitivities. No case is marked qualified.

Warm nominal energy budget:0.9 battery usability minus0.2 nominal reserve =0.7nominalWh before VTOL. Main discussion uses30Wh for one departure+arrival and60Wh for a delivery-stop+return reference with four VTOL events. The20/40 and40/80Wh budgets are sensitivities, not validation. Cold capacity loss, real discharge curves, unknown installation drag and operational weather are NOT closed.

At60km/h, central unloaded216Wh references illustrate roughly **18–40km one-way cruise distance**, and **7–15km equal-leg radius** with the60Wh four-event budget, depending on assumed drag/efficiency. These are similar for equal-energy4S3P and6S2P and cannot establish a voltage winner. The exact results are in `mission_sensitivity.csv`; do not use them as dispatch limits.

Even the largest saved illustrative equal-leg radius was only about22.1km, with lower assumed dry mass,50km/h, the favorable assumed aero case and40Wh VTOL budget, and NO cargo. That optimistic sensitivity is not evidence for30km out/30km back. Low-speed stall margin and safe cruise airspeed remain unverified. Every1kg-payload case in the current bounded screen is mass-rejected. A500g reference can fit only some lighter cases/packs, not the central large-range-pack configurations.

## Verification and hard gates before a final choice
- Six existing optimization-model unit tests and ten return-budget/saved-case tests pass. These check mass gating, null rejected ranges, energy conservation, wind signs, source mass sums and false qualification flags—not flightworthiness.
- Parent independently checked all six cruise-fetch SHA256 values, all six battery-fetch hashes, and existing native geometry/source/archive hashes. Manufacturer-image prop identity was inspected directly.
- Existing/manual4S versus6S data are not a paired forward-flight comparison. Do not claim the research found an aerodynamic optimum.

The next meaningful validation is **human-controlled mass/fit/current evidence**, not another speculative combination search:
1. Calibrate the intended material/slicer mass prediction using representative printed parts; reconcile every known installed component and remaining allowance. Do not order a large pack solely from the central total.
2. Obtain a professional builder's written finished-pack envelope, mass boundary, cell traceability, current/thermal qualification and safety documentation; actual availability/prices/QA remain open. No purchase/contact authorized.
3. Confirm full native/physical wiring/strap/connector/thermal clearance, measured battery COM and human-reviewed assembled CG.
4. After qualified review, define supervised warm/low-SOC/cold electrical and lift tests with exclusion zones and stop criteria. Remove propellers for configuration and non-thrust bench work. The assistant must not energize/arm/deploy hardware.
5. To choose the actual range winner, measure comparable forward-flight electrical demand at matched mass/airspeed for4S10×6 versus a specifically identified6S9453 alternative. Analysis/simulation/static thrust cannot prove flightworthiness.

**Decision:** high-energy candidate identified and bounded comparison concluded; final winning complete setup remains gated by evidence that online research cannot supply. If the final requirement remains comfortable1kg payload and a30km delivery radius with return, the current stock/current-material configuration must change or those requirements must change; this report does not authorize either change.

## Traceable research artifacts
- `cruise/REPORT.md`, `cruise/EVIDENCE.json`: primary manual pages, BH manufacturer imagery, APC documentation/map, ESC source and HTTP/hash records.
- `battery/REPORT.md`, `battery/FETCHES.json`: six bounded primary/catalog fetches; exact variants, contradictory listing metadata, ratings versus complete-pack qualification, and P60C watch-list evidence. P60C is not rejected because its datasheet is gated; its finished pack, verified datasheet/current and supply are not established here.
- `mass_sources.json`, `mass_reconciliation.json`: live existing mass references plus source-hashed print inventory and estimates.
- `catalog_envelope_precheck.json`, `GEOMETRY_PROVENANCE_TEST.txt`: conditional native-envelope reuse and actual verification output.
- `mission_sensitivity.csv`, `MISSION_METADATA.json`, `run_mission_sensitivity.py`, `FINAL_MODEL_TESTS.txt`, `FINAL_SAVED_CASE_TESTS.txt`: executable calculations and test evidence.

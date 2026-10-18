# Standard Stork — no-payload range design selection

## Scope and decision
Lucas explicitly asks to establish maximum-range/no-payload specs for standard Stork. This is the current optimization case, not abandonment of longer-term delivery goals. Select the manual-recommended 4S/10x6 cruise configuration with a professionally assembled high-drain 4S3P P50B battery as the engineering baseline. This supersedes the prior 6S2P headline recommendation for this design case. Selection is based on manual range/endurance guidance, equal nominal energy and lighter reference cruise ESC—not a measured global optimum.

## Selected design specification
- Original 1620mm-span Stork, fixed 4+1 VTOL; unchanged current material/geometry plan.
- Payload: 0g for this study.
- Cruise motor: BrotherHobby Avenger2812 V5 910KV.
- Cruise prop specification: 10x6 inch two-blade, manual-recommended 4S class. Exact product/hub remains a BOM detail; no invented exact prototype brand or paired efficiency map.
- Cruise ESC baseline: manual-example Lumenier51A BLHeli32, 4S; retain the existing installed mass reference rather than changing to an unweighed ESC.
- Lift: four T-Motor F90 1300KV, manual 7-inch two-blade prop class, four existing 50A lift-controller mass references. Do not silently substitute a lighter 4-in-1 in the mass estimate.
- Battery design: professional 4S3P Molicel P50B, 15Ah,14.4V nominal,16.8V full charge,216Wh nominal; finished target mass <=927g, including pack leads and connector under the same boundary as the ledger. This is a custom-pack requirement, not an already-verified commercial product or complete-pack current rating.
- Avionics: retain existing SpeedyBeeF405Wing, four ES08MAII servos, M10Q/R24 baseline and existing sensing/wiring allowances. Firmware/deployment unchanged.
- Initial cruise design point:60km/h; investigate50–70km/h for best distance per usable Wh. Actual optimum speed is not established by the manual speed band alone.

## Budget and performance
Using central4S dry2056.7g and target pack927g gives2983.7g estimated takeoff mass, or3083.7g including100g UNUSED growth allowance. Against3100g stock planning ceiling, central pack allowance is943.3g. Do not spend the unused100g growth allowance. High dry-mass case does not satisfy this specification; mass control is an acceptance condition, not a claim that every build will fit.
Existing central unloaded216Wh sensitivities at60km/h give roughly18–40km one-way with30Wh VTOL budget and70% nominal energy allocated before VTOL. This is not a measured range or a claim of30km delivery radius and return. Report confidence as design selection rather than aerodynamic proof.

## Remaining ordinary development checks
Confirm professional pack finished mass/current and interfaces; finalize exact props/hubs and CG; calibrate mass estimates; verify safe supervised electrical/flight behavior. These checks do not postpone this design selection. No purchase, manufacturer contact, configuration deployment, motor arming or flight is authorized or performed.

Sources: existing cruise/REPORT.md and EVIDENCE.json; battery/REPORT.md; mass_reconciliation.json; mission_sensitivity.csv; CONCLUSION.md. Existing source evidence and old conclusion are preserved for traceability.

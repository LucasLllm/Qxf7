# Stock Stork fixed 4+1 — nonprinted installed-mass ledger

## Outcome and integration contract

**Source-linked accounting completed; actual installed mass remains unmeasured and null.** This is one stock-size reference aircraft, not a purchasing or flight-ready BOM. Published component weights, calculated nominal tubes and unmeasured installation allocations are kept separate. No printed masses/placeholders are present.

- Baseline published nonpropulsion component subtotal: **94g** (4 servos48 + FC/PDB/BEC stack35 + GNSS/compass8 + receiver/antennas3).
- Full VTOL-manual carbon inventory, under the explicitly assumed bores/density below: **290.263g nominal calculated**, NOT a published/actual tube mass.
- Common unmeasured installation allowances: **191.2 / 336.4 / 579.0g**, low/central/high. These are editable planning cases, not tolerances or probability bounds.
- Additional unrepresented ESC accessory allocations are architecture-specific; factory motor and ESC leads are not charged again as extension wire.
- Optional complete airspeed installation adds **15 / 22 / 30g**, of which only3.5g is a published board mass. Baseline excludes it.
- Excluded: printed structure, finished battery, net500/1000g cargo, separate growth reserve, FPV, independent telemetry radio, powered cargo release, winter enclosure/insulation/heater. Receiver telemetry and factory antennas ARE included. Aircraft straps and cargo packaging/restraints ARE included; do not add them a second time.

Use `installed_bom.json` → `scenario_joins` as the nonprinted planning input, joining existing `../hardware/hardware_inputs.json`. Do **not** add its propulsion subtotal to `accounted_nonprinted_excluding_battery_cargo_g` again. Do not also add old carbon271g, hardware45g, glue45g or wiring150g. Actual final aircraft mass cannot be emitted until the missing installed evidence and printed masses are closed.

## Original source verification

Both public manual URLs returned HTTP200 and were SHA256 byte-identical to the supplied PDFs:
- [Base manual](https://flightory.com/wp-content/uploads/2026/04/STORK-USER-MANUAL.pdf): `2ac98e62612d26fea8b2f47fabb52f37425afbf73ff9123c3a933d2bff5939c5`.
- [VTOL manual](https://flightory.com/wp-content/uploads/2026/04/STORK-USER-MANUAL-VTOL.pdf): `600d8f6aed1552213c6757cfb38053602ff6bc3c1433c3e5ec2fb98cd6ff4bbd`.

`manual_inventory_evidence.json` preserves local/source identities, hashes and extracted page text. PDF page numbers below are one-based PDF pages. VTOL p7 says its equipment list includes the base items; changed quantities REPLACE, not supplement, base quantities. VTOL p41 says remaining assembly follows the base manual.

## Carbon stock: manual dimensions versus assumed mass geometry

VTOL p9 supplies outer size, length and quantity. It supplies **no bore, wall thickness, density or net mass**. Base p47–49 and p52–54 explain wing and tail reinforcement/hinge installation; base p57 identifies one10mm and one8mm main spar. VTOL p34 explicitly calls for10×10×500mm booms. VTOL p30 says the4mm fin tube is cut to suit; p9 lists95mm. The ledger retains the full listed95mm, not an invented trim.

|Manual carbon stock|Qty|Listed length each mm|Assumed circular bore mm|Nominal aggregate g at1.6g/cm³|
|---|---:|---:|---:|---:|
|10mm round|2|1000|8|90.478|
|8mm round main/secondary spar|1|1000|6|35.186|
|6mm wing reinforcement|2|500|4|25.133|
|3mm aileron hinge|2|500|1|10.053|
|8mm V-tail spar|2|155|6|10.908|
|6mm V-tail spar|2|265|4|13.320|
|3mm ruddervator hinge|2|265|1|5.328|
|10×10mm square-outside boom|2|500|7|98.425|
|4mm fin reinforcement|1|95|2|1.433|
|**Full inventory:9 specifications /16 pieces**||||**290.263**|

Round formula: `qty × L_mm × π/4 × (OD_mm² − ID_mm²) ÷1000 × density_g/cm³`.
Square-outside/circular-bore formula: `qty × L_mm × (side_mm² − π/4 × bore_mm²) ÷1000 × density_g/cm³`.

Nominal1.6g/cm³ is an engineering assumption, not a manual or manufacturer claim. Full listed lengths are retained: no offcut, bore opening or cutout mass credit; glue is separate. Hinges are modeled hollow, although base narrative also uses the word “rod”: actual supplied construction remains unresolved. VTOL p10 strongly recommends a circular inner boom profile and warns against fully square thin-wall tubes, especially ≤1mm; an ordinary10×10×1mm fully-square tube is NOT substituted here.

**Important correction to earlier carbon accounting:** with the stated7mm boom bore and1.6g/cm³ density, full inventory is290.263g, not approximately271g. The old approximately271g is reproduced at an **8mm** circular boom bore:271.413g. `tube_sensitivity.json` explicitly recalculates density1.3/1.5/1.6 and bore8/7/6mm; these are sensitivity cases, not validated bounds.

**Unresolved second10mm tube:** VTOL p9 lists TWO10×1000mm round tubes; base p12 and p57 identify only ONE10mm main spar plus ONE8mm spar. No assembly location for the second10mm was established in the bounded manual read. Conservative full VTOL list remains included. At the nominal geometry, omitting one10mm tube would reduce mass by45.239g, giving245.024g, but is **not authorized as a finalized installed inventory**. Resolve against kit/assembly documentation before deleting it.

## Mechanical inventory and nonprinted assembly allocations

Manual VTOL p9: **35 M3 inserts (OD5×height5mm),12 M3×6,7 M3×10,20 M3×8,4 control horns,4 pushrods,4 servo extensions,2 Velcro straps**. Base15 inserts/3 M3×10 are not added again. VTOL p38 calls for motor attachment screws, then separate M3×8 mount fastening; p40 uses M3×8 boom fastening. Base p56 specifies cruise motor attachment screws supplied with the motor or suitable8–12mm screws.

`installed_bom.json` and CSV retain per-unit low/central/high allocations, quantities, source page and explicit scope. These masses are **not published at the cited manual URLs**; the manuals support quantities/installation only.

|Unmeasured group|Low g|Central g|High g|Boundary|
|---|---:|---:|---:|---|
|Fasteners/linkages/arms/prop hardware|56.2|84.4|124.2|35 inserts;39 listed airframe/clamp screws; planning20 additional motor screws;4 pushrod/horn/clevis assemblies;4 servo hardware sets; non-folding prop nuts/adapters|
|Cured adhesives and finish|25|55|110|Retained CA15/25/45, epoxy8/15/25, hotglue2/5/10, optional finish0/10/30; not bottle/stick purchase masses|
|Aircraft mounts, battery straps, cargo restraint/packaging|25|50|95|Aircraft straps/tape/foam/ties10/20/35 plus cargo restraint/padding15/30/60; excludes net cargo and pack enclosure|
|Incremental wiring/connectors/junction materials|85|143|240.8|Detailed residual routing below; excluded factory-wire lengths never added again|
|Unrepresented GNSS/FC accessories|0|4|9|Positive accessory mass outside8g/35g only; cable/microSD inclusion unresolved|
|**Common total**|**191.2**|**336.4**|**579.0**|No ESC accessory uncertainty or optional airspeed in this total|

Motor4-screw count is an explicit20-screw planning assumption, not a guaranteed supplied count. The20 M3×8 listed clamp screws are not silently treated as the entire motor+clamp inventory. Reconcile actual hardware counts. Servo arm and motor accessory mass inclusion remains unknown: only positive unrepresented hardware is allocated, never whole accessory bags/spares.

Four control-surface horns and pushrods are manual facts, but their diameters/lengths/materials and clevis model are user-selected (base p51/p55); numerical mass allocation is not a verified linkage specification. Prop-nut material/shaft fit remains unclosed in the prior hardware report. In6S cases this ledger's prop-hardware allowance covers the FOUR lift positions only: the unknown complete folding cruise assembly already includes folding hub/fasteners and stays a separate unknown, not hidden here.

## Avionics and power boundaries

|Reference and verified source|Published mass|Installed boundary / limits|
|---|---:|---|
|[EMAX ES08MA II](https://shop.emaxmodel.com/products/emax-es08ma-ii-12g-mini-metal-gear-analog-servo-for-rc-model-robot-pwm-servo), [primary specification image](https://cdn.shopify.com/s/files/1/0469/7358/3518/t/3/assets/EMX-SV-0275-DES-1.jpg?v=1598527259)|12g each ×4=48g|Image says12g,23×11.5×24mm,4.8–6.0V. Factory lead treated as included; arms/screws unspecified and conditional incremental allowance retained. Not a servo load/fit/cold qualification.|
|[SpeedyBee F405 Wing complete reference](https://www.unmannedtechshop.co.uk/products/speedybee-f405-wing-app-fixed-wing-flight-controller)|35g with USB extender|Original FC/PDB/wireless stack; integrated3 BECs plus battery/current sensing included. No second flight power module, PDB, BEC or current sensor added. Retain USB extender conservatively; cable/microSD inclusion remains uncertain.|
|[Matek M10Q-5883](https://www.mateksys.com/?portfolio=m10q-5883)|8g|GNSS+QMC5883L compass+ceramic patch antenna; no second GNSS antenna. Supplied20cm6-wire cable inclusion unspecified; small conditional accessory allowance. **EOL and counterfeit warning**, so historical reference, not a procurement selection.|
|[Matek ELRS-R24-D](https://www.mateksys.com/?portfolio=elrs-r24)|3g **with2 antennas**|Both antennas explicitly counted already; no antenna/pigtail mass added. CRSF RX, onboard link telemetry; no independent airborne telemetry modem or ground transmitter mass.|
|[Optional Matek ASPD-4525](https://www.mateksys.com/?portfolio=aspd-4525)|3.5g sensor board|Published board-only boundary. Pitot,40cm silicone tube,20cm JST-GH cable and nonprinted fixation receive11.5/18.5/26.5g incremental allowance; complete optional15/22/30g.|

All five component-page source URLs returned HTTP200; exact mass strings are asserted by the executable verification. The servo specification image was read visually, not inferred from a photograph. The initially attempted primary FC URL returned404 and is retained as **failed discovery only**, never used for its specifications; the prior verified retailer URL is used instead.

FC retailer specifications:7–36V input; FC5.2V2.4A continuous/3A peak; servo BEC default4.9V4.5A continuous/5.5A peak, selectable6V or7.2V; VTX default9V1.8A continuous/2.3A peak. **7.2V is outside this selected servo's4.8–6.0V specification.** Integrated PDB/current-sensor reference90A continuous/215A peak does not establish safe simultaneous aircraft-current routing. Five motor outputs/four servo outputs are required, with firmware/protocol/grouping not validated here. The4S Razor ESCs are OPTO/no BEC: FC integral BECs are the reference supply. V-Good ESC BEC outputs must not be assumed compatible in parallel with FC regulators. No energized hardware/configuration operation was performed.

## VTOL harness and ESC leads: no double counting

Manual VTOL p38–39 routes motor leads through each boom, recommends3.5mm bullet connectors at motor leads and another interface at wing roots, then final links into the ESC. Reference routing assumes inboard ESCs for all three candidate joins; moving individual ESCs onto booms requires replacing this route allowance, not retaining it unchanged.

- **12 residual phase extensions**, aggregate45/70/110g allocation: only NEW conductor length after credited F90 factory3×230mm leads per motor and any ESC factory phase leads. No exact route/gauge/ampacity claimed. BrotherHobby cruise250mm factory leads also credited.
- **24 mating bullet pairs** (4 motors×3 phases×2 interfaces =48 individual contacts),12/18/28.8g. This is a chosen two-interface realization of the recommended modular system, not a mandatory connector count.
- Four added servo extension assemblies8/14/24g; factory servo leads are not added.
- Additional data extensions3/6/12g; exclude cables in FC/GNSS/accessory mass already accounted, and exclude optional airspeed harness.
- Aircraft-side battery connector4/7/12g (XT60 orEC5); pack-side connector/leads already belong to published finished pack.
- New aircraft battery-feed extension5/10/18g; incremental distribution/cruise links3/8/18g; solder/heatshrink/insulation5/10/18g. No second PDB/BEC board, whole factory ESC lead set or pack leads.

**ESC factory-accessory uncertainty is a single exclusive row per architecture**, not duplicated in generic wiring/capacitor rows:

|Existing propulsion candidate|Extra unrepresented ESC accessories low/central/high g|Boundary|
|---|---:|---|
|4S current-listing:5 Razor45|0/15/30|Furnished power/signal wires, caps and heatsinks only to extent NOT represented by quoted3g each. Motor-wire residual requirement belongs to phase extensions.|
|6S light catalogue:ELITE4-in-1 + V-Good cruise|0/6/12|ELITE heatsinks already27g; cable and supplied35V1000µF cap inclusion unresolved. V-Good factory wires already58.1g.|
|6S heavy:5 V-Good standalone|0/5/10|No factory ESC power/phase/signal lead mass added. Only additional caps unrepresented by58.1g; cap presence/value/mass not verified.|

Zero low ESC-accessory allocation means an optimistic **quoted-mass inclusion credit**, not permission to omit required capacitors/wiring/cooling. This accounting intentionally leaves accessory inclusion open. Before substituting actual weighed assemblies, identify and credit represented accessories; never add the whole factory lead or capacitor again. Cap voltage/ESR/value/location and transient/cooling qualification are electrical blockers, not solved by these grams.

## Joins to prior propulsion research

No motor/battery comparisons were repeated. Existing motor/prop/ESC item masses and exact candidate BOMs are read from the parent hardware JSON, with its SHA256 recorded. Values below include their **propulsion component subtotal once**,94g avionics,290.263g nominal full-list tubes and appropriate assembly allowances. They exclude batteries, printed structure, cargo and growth reserve.

|Candidate|Low accounted g|Central accounted g|High accounted g|Additional unknown|
|---|---:|---:|---:|---|
|4S current-listing|896.663|1056.863|1314.463|Installed inclusion/routing/assembly closure|
|6S light ESC catalogue|935.763|1086.963|1335.563|**Complete folding cruise prop assembly** + installation closure|
|6S heavy ESC available listing|1141.163|1291.363|1538.963|**Complete folding cruise prop assembly** + installation closure|

These are **accounted planning sums**, NOT complete measured nonprinted installation. Both6S actual installed totals remain null because folding assembly mass is unknown; all three actual installed totals remain null because unmeasured assembly/inclusion boundaries remain. Optional airspeed increment remains separate; optional FPV is unselected and not zero-mass equipment. Ground radio/goggles/chargers, printed jigs/guides, unused tubes/screws, bottle glue and manufacturing waste do not fly.

## Remaining blockers and deliverables

1. Resolve second10mm tube necessity/location, actual bores/material density, trimmed installed lengths and hollow-versus-solid hinges. Tube model is neither strength nor fit evidence.
2. Reconcile actual fastener quantities/materials and servo/motor accessory weighing conventions; unselected pushrod/horn/clevis lengths remain unknown.
3. Resolve ESC cable/cap/heatsink inclusion; measure residual routed wires, selected connector halves and retained solder/insulation. Current/gauge/thermal review remains open.
4. Qualify integrated FC/PDB/BEC routing for simultaneous loads and servo peaks; do not parallel ESC BECs. GNSS replacement for EOL reference is unselected.
5. Weigh cured glue/finish and retained mounting/packaging/restraint installation. Cargo CG/load restraint and any delivery mechanism remain unqualified.
6. Prior6S folding assembly mass, exact lift current/thrust and all mechanical/electrical compatibility blockers remain open. −20°C equipment/qualification and CAD10,000 landed cost are not established.

Files: `installed_bom.json` (machine-readable categories, quantities, source links, per-unit/group allowances and scenario joins), `installed_bom.csv` (auditable flat inventory), `tube_sensitivity.json`, `manual_inventory_evidence.json`, `evidence/*.json`, `collect_sources.py`, `build_bom.py`, `verification.json`, this report. Only this output directory was written.

Reproduce from `/Users/lucasliu/.hermes/profiles/fumes`:

```
research-venv/bin/python notes/stork-development/performance-scenarios/nonprinted-installation/collect_sources.py
research-venv/bin/python notes/stork-development/performance-scenarios/nonprinted-installation/build_bom.py
```

The second command exercises real assertions for component masses, manual URL/hash identity, inventory/formulas, scenario joins, allocation ordering and preserved unknowns. `verification.json` records passing output and artifact SHA256s. No purchase/contact/credentials/CAD/physical hardware/print/upload action occurred.

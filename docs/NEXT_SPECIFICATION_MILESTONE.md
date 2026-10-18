# Next milestone: from the stock diagnostic model to provisional QxF7 specifications

## Scope and authority
Lucas requested examination of the completed Claude Code work, public publication, and a path to final specifications. This is Fumes's recommended engineering work order, not a record that the work below has already run, a selected aircraft configuration, or physical-test approval. Preserve prior results; do not tune the model to advertised performance.

Confirmed design direction: ONE scaled-up modified Stork; fixed four-lift-plus-one-cruise propulsion, no tilt; 95 km one-way and 750 g GROSS cargo together; >=70 km/h cruise airspeed. Cargo includes packaging/insulation. Battery swaps at endpoints. Budget is deferred. Scale, span, AUW, hardware and numerical growth/acceptance margins remain unselected. All-Bambu filament lineup is selected, not mechanically/environmentally qualified. Cold capability remains a separate unresolved envelope; do not claim -30 C capability from a mild-air calculation. No icing qualification.

## What is actually complete
- Stock geometry/mass/evidence import, provenance records, project environment and diagnostic model.
- Stored stock run, low/central/high parasite sensitivities, aligned/crossflow stopped-prop cases, historical-model attribution ladder, partial complementary aerodynamic check and conditional hover screening.
- Fumes independently reran all 15 tests and the transfer verifier (197 original geometry files unchanged), then reproduced the production-mesh stock central 60 km/h point: drag 3.2099318461 N; battery demand 115.1498962508 W; trim converged; no clipped strip-polar area. This is reproduction of the same model, not independent physical validation.
- Fumes verified public GitHub main equals 989f33cacb7cf11d21a45c78e76500806d77055d after Claude pushed the existing five commits. New files created after that verification are not covered by this publication receipt.

## 1. Bounded Phase A closure, not an endless calibration project
1. Keep the centre-wing carry-over correction explicitly a body-interference modelling assumption. Independent lifting line supports the induced-drag trend but shares assumptions and does not measure actual body lift.
2. Reconcile the physical-root CG case with the released LE: 4.5451658918 + 47 = 51.5451658918 mm. The implemented historical B case is 51.4433 mm. The ~0.102 mm difference is minor; label it a retained historical case or correct it with a new version, not a measured CG.
3. Explain why ladder trim omits the fuselage moment used in the headline sweep. Report a matched final comparison or identify that distinction clearly. The 54 km/h hand-check CSV currently has no VLM comparison because 54 is absent from the sweep grid; compute it explicitly if claiming comparison at that speed.
4. Enforce runtime result gates, not merely successful optimization: force/moment residual tolerances, polar range/confidence, map-domain validity, positive energy and adequate bus voltage/current. Add tests including deliberately rejected cases. A feasible_voltage flag that is not propagated into mission acceptance is insufficient.
5. Treat the quoted ~300 W hover claim as inconsistent with the exact assumed mass/disc area, not universally impossible: ideal power is ~307 W at 2.9 kg, so rounding, mass and geometry context matter. At 2.98 kg the stored ideal is ~321 W; practical battery demand is substantially higher.
6. Resolve the coarse-versus-dense fuselage envelope mismatch from retained section grids, integration definitions and hatch inclusion before launching another CAD extraction or treating a coarse reintegration as authoritative. Exact exposed wetted area remains unknown.

No requirement to make an unmeasured model match vendor claims before beginning provisional sizing.

## 2. Implement coupled loaded sizing (the next main deliverable)
Parameterize the model instead of multiplying stock range or using a single geometric scale law.

For each candidate, iterate to mass closure:
- printed shell mass from actual wall/process assumptions; rigid parts, reinforcement, joints and adhesives separately;
- spar/boom/landing structural sizing and allocations; do not blindly scale every part mass by scale^3;
- gross 0.750 kg cargo once, installed avionics/wiring/retention/thermal hardware;
- finished-pack energy AND mass, cruise motor/prop/ESC mass, lift motor/prop/ESC mass;
- explicit unused growth margin, reported separately from installed mass;
- lift/drag/trim demand at >=70 km/h and updated Reynolds numbers;
- cruise prop map operating point, motor/ESC losses and end-of-discharge voltage/current margins;
- VTOL and transition energy allowances, arrival reserve, headwind and capacity/aging sensitivity.

A larger battery increases mass, which changes both cruise and hover demand. Iterate until residuals meet declared numerical tolerances. Report nonconvergence and infeasible candidates; do not erase them.

Run a coarse, explainable candidate envelope over scale/wing area and finished-pack capacity/topology, then refine near the useful frontier. All candidate ranges, engineering margins and atmosphere/wind/reserve assumptions must be labelled analyst-proposed, not silently promoted to Lucas requirements. Keep one final airframe decision; do not introduce an expendable stock build as a prerequisite.

Outputs: machine-readable candidate table, assumption/provenance file, infeasibility reasons, sensitivity bands and a ranked short list with a recommended provisional design point. At minimum report span, wing area, installed mass, growth-loaded planning mass, wing loading, payload allowance, nominal/usable/reserved Wh, pack mass/topology, cruise W/Wh/km, predicted mission energy, conditional hover power, and unresolved thrust/trim/structure gates. Do not report a falsely precise final scale factor.

## 3. Targeted evidence work alongside sizing
- Parasite drag: prioritize skid/mount/motor geometry, installed exposure and stopped-prop behaviour because these dominate uncertainty. A second empirical build-up can check bookkeeping; OpenVSP parasite estimates alone do not qualify bluff-body interference. Use a narrowly scoped CFD study only with a documented question, mesh/domain convergence and appropriate comparison. Do not make installing every tool a prerequisite.
- Controls: map actual ruddervator hinge geometry and chord fraction to symmetric pitch deflection, then assess trim/control authority across loading/CG cases. Whole-tail incidence is not control deflection. Preserve neutral uncertainty; include thrust-line moments.
- Lift: select evidence-backed motor/prop/voltage candidates for the scaled design. Missing stock F90/4S data blocks a qualified stock-hover claim, not all provisional QxF7 sizing or alternative voltage choices. Propose any bench tests for human approval; never energize hardware autonomously.
- Structure/manufacturing: check spar/boom loads, wing bending/torsion, joints, motor mounts, printability, repeatable material mass and cargo/pack access. Static analytical checks are not flutter or flightworthiness qualification.

## 4. Freeze specifications in two distinct stages
**Provisional engineering specification:** select a recommended candidate based on coupled analysis with conservative cases and explicit evidence gaps. Include exact component candidates, dimensional layout, mass/power budget, CG/placement targets, interfaces, BOM, risks and acceptance tests. Human review is required for safety-critical choices. This selection can precede measured qualification.

**Build/flight-qualified specification:** revise against measured printed/installed mass, physical CG, finished-pack discharge, motor/prop thrust/current/thermal tests, structural/control integration and supervised incremental flight results. No simulation or software test proves flightworthiness or Transport Canada operational permission.

The final mission-specification claim remains conditional until the corresponding evidence exists; operational approvals and severe-cold qualification are separate deliverables.

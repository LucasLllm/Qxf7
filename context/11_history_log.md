# 11 History log: every project conversation, in order

Each entry is one claude.ai chat in the "VTOL fixed wing drone" project. Dates are when the chat was last updated.

## 2026-10-03: Project created
Goals doc: "VTOL fixed wing drone with 3D-printed parts, carry comfortably 500 g–1 kg payload, operate in winter for long/medium-range missions, at least 30 km radius, as fast as possible. Find a model/guide (paid or open source) to start with, then modify." (`reference/Goals.md`)

## ~2026-10-04 to 10-08: "Best VTOL model recommendations"
- Compared Flightory Stork VTOL, Stallion VTOL, Super Stingray VTOL, Moose. Recommended the **Stork VTOL** (4+1, V-tail, STL/STEP, highest energy capacity and aspect ratio). Lucas challenged it several times with the uploaded manuals; conclusion held (Stingray battery capped ~150 Wh, flying wing CG-sensitive).
- Lucas **bought the Stork + VTOL Pack**.
- Claude retracted figures it had stated with false confidence (288 Wh, 104–130 km, 2.9 kg, 1.6 kg empty) because they traced to Flightony, an unverified third-party seller.
- Explored Aviant, Ribbit, UBC/Stellat'en, Avy, Wingcopter, Swoop Aero, UAF, WeRobotics. Differentiation: rural/northern + winter + combination of features.
- A-tail and wireless charging discussed and not adopted for phase 1 (battery swaps). Goal reframed: **maximum winter range at a safe minimum cruise speed (70–80+ km/h)**.
- Decided: winter/low-temperature resistance first; LW-ASA instead of LW-PLA, PC for high-load parts; separate lift ESCs. Proposed design mission at the time: 1 kg, 50 km radius, −30 °C, 40 km/h wind.

## 2026-10-10: "VTOL drone specs simulation"
- Lucas: parts weighed via Bambu CLI, filaments chosen per part, battery and motors chosen; wants accurate range/max/optimal speed.
- Pipeline proposed: analytical model (XFLR5/OpenVSP drag polar, APC/UIUC prop data, eCalc), optional sim (JSBSim/SITL/RealFlight), calibration tests. Accuracy bands ±20–25% raw, ±10–15% calibrated, ±5% with flights.
- Found real builder data (Vince Hogg, Michail Belov, Tsung Xu) and the stopped-prop alignment effect (26–35%). Flightony numbers flagged as calculated, 300 W hover implausible. Flightory license limitation noted.

## 2026-10-10: "Drone market research and range"
- Problem space: nurse-run clinics in roadless communities. 30 km fits Lower North Shore, not Nunavik. One-way range formula with headwind. BVLOS 5 NM aerodrome buffer.
- Lucas asked how much payload is really needed, pushing for a natural-breakpoint analysis without route assumptions.

## 2026-10-10: "Medical delivery drone payload capacity"
- Research gave 1.0 kg, then Lucas narrowed to **750 g gross**. STAT value revised down; mission = scheduled same-day batch. Non-medical: water bacteriology samples strongest. Restaurant food delivery argued against; Aviant's food pivot doesn't transfer to low-density routes.

## 2026-10-11: "VTOL drone optimal range"
- 70 routes, then Quebec-only. Recommendation moved 80 km leg → 50 km leg after Lucas caught a cruise-power error (~200 W → 400–460 W) and missing VTOL energy. Ideal-day ~175 km (model). Lucas's Stork Wh/km figure showed the model ~1.5–2× optimistic. Lucas judged coverage flattens near 90–100 km and **committed to 95 km** (Quebec only). Ranked routes: Manawan → Saint-Michel-des-Saints top, Wemotaci → La Tuque second; Isle-aux-Grues ↔ Montmagny as test site.

## 2026-10-11: "Drone project competitor research"
- Four parallel research agents; ~10k-word report (`reference/qxf7-competitor-landscape.md`). Critical flags: CORRIDAIR holds Manawan; DT46 flight was in France; Flightory license excludes organizations. Payload ratio discussion (QxF7 ~11% comparable to peers).

## 2026-10-11/12: "QxF7 Drone pre-build report"
- Built the 18-page Google Doc report (`reference/preliminary-design-report-2026-10.md`). Lucas's explicit corrections: no route rankings in the report; don't headline −30 °C; competitor profiles as prose; label third-party specs; he edited range to 95 km, removed price/licence sentences, removed "Why we chose the Stork", removed the ~7 kg / 2.4 m size estimate, switched to Times New Roman. Full fact-check pass (`reference/qxf7-factcheck-2026-10-11.md`).

## 2026-10-12: "Healthcare worker outreach strategy"
- Deep research → outreach plan (`reference/qxf7-healthcare-outreach-plan.md`): Wemotaci council first, Vertiko before Manawan, Chaudière-Appalaches BPOI for Isle-aux-Grues; TCPS2 line; French templates; 12-week timeline; winter range rules out Wemotaci year-round.

## 2026-10-17 morning: "Zipline profitability and failure"
- Is the idea profitable? Answer: only as a service sold to health-system buyers on routes where the drone clearly wins. Zipline Ghana lessons: unpaid bills, political turnover, only 10% of deliveries to hard-to-reach areas and 4% emergencies. Lessons: fly only clear-win routes, report emergency/remote metrics, single-payer risk, expect "why not in-house?".

## 2026-10-13 → 10-17: This conversation (simulation tooling and geometry)
1. Simulation pipeline: slicer mass/CG → XFLR5/Flow5 or OpenVSP → eCalc → mission model → optional SITL → approximate FEA/load test.
2. ANSYS: overkill now; later for targeted drag/FEA.
3. STL → CFD geometry: rebuild lifting surfaces parametrically (OpenVSP) from slices; clean OML for fuselage.
4. STEP files help (exact NURBS) if genuine; hybrid STEP-for-CFD, OpenVSP-for-iteration.
5. Researched SIMNET, MATLAB, JSBSim, eCalc, RCAIDE, SITL, Flow5, AirShaper; recommended stack in `06`. **Use the standard Stork as the calibration case.**
6. Lucas chose **Flow5/XFLR5 + OpenVSP**. First step: extract geometry from STEP. Fuselage handled by OpenVSP parasite drag (+ Flow5 for stability).
7. CAD inventory by the Mac agent (`reference/cad-inventory-summary-2026-10-17.md`), then a geometry extraction bundle (`data/stork-geometry-bundle/`).
8. Bundle review: validated against manual (31 dm², MAC 195, root 230, S3021, CG 47 mm). Length "failure" accepted as convention. Tail +2.88° artifact identified. Correction: the 24 dm² figure Claude had used came from an old blog; 31 dm² is right. Baseline saved as `reference/qxf7-stork-baseline-geometry.md`.
9. Decided to move the work into Claude Code with this context pack.

## Fumes retained-source import audit
Lucas requested comparison and supplementation for the Claude Code migration. Added context/12, docs/CONTEXT_CONFLICTS.md,58sliced-part definitions/82installed pieces,58release-matched parent receipts, historical4S selection, installed mass accounting and separately framed predicted print centroids. Existing geometry and mission/hardware YAML remain unchanged. No simulation, tool installation, publication or physical action. Check docs/fumes-context-verification.json for the actual import verification. Earlier narrative claims of parts being “weighed”, length passing by convention, or neutral/CG being proven must be read with the source qualifications.

## Latest Lucas clarification — baseline versus final aircraft
- Budget omitted from active study; evaluate performance first, revisit cost afterward. Historical monetary targets are not current constraints.
- ModifiedQxF7 cruise target≥70km/h; standard Stork performance is to be measured, not force-fit to this target. Airspeed is the declared modeling interpretation. Full mission in severe cold is not established.
- Standard Stork PhaseA: ONE4-in-1 lift ESC, retaining the existing mass reference. Separate ESCs on modifiedQxF7 remain an undecided possibility; this supersedes older separate-ESC decisions for the stock baseline only. Shared power/control paths mean separate ESCs are not inherently full propulsion redundancy.
- No simulation or hardware operation is performed by this context reconciliation.

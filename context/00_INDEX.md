# Context index: read in this order

This folder holds everything known about the QxF7 project as of **2026-10-17**. It was compiled from the claude.ai project "VTOL fixed wing drone": its docs, memory notes, the Stork manuals, the CAD extraction bundle, and every project conversation from 2026-10-03 to 2026-10-17.

Files 01–11 are historical syntheses for a fresh engineer or agent. Files in `reference/` are source snapshots (the geometry reference now carries an audit qualification banner). Read `12_fumes_handoff.md` and `../docs/CONTEXT_CONFLICTS.md` FIRST. Prefer Lucas's latest explicit decisions and checked artifacts with their stated scope; an older source snapshot does not overrule a later decision or turn an assumption into a measurement. Preserve and flag disagreements.

| File | What it covers | Read when |
|---|---|---|
| `01_project_overview.md` | Team, mission, status, what has and hasn't been decided | Always first |
| `02_requirements.md` | Payload 750 g, 95 km one-way, ≥70 km/h, −30 °C, with the reasoning and still-air factor stack | Before any sizing or mission math |
| `03_routes_operations_regulation.md` | Candidate routes and distances, winter-range consequences, outreach status, Transport Canada rules | When defining mission profiles |
| `04_stork_baseline_aircraft.md` | Flightory Stork / Stork VTOL official specs, recommended hardware, third-party (Flightony) numbers, real builder flight data, license problem | Before modelling the baseline aircraft |
| `05_cad_geometry_extraction.md` | The verified geometry bundle in `data/stork-geometry-bundle/`: validation, wing/tail tables, conventions, traps | Before touching any geometry |
| `06_performance_method.md` | The agreed simulation pipeline, tool choices and why, equations, calibration targets | Before writing analysis code |
| `07_prior_estimates_and_models.md` | Earlier energy-model results (52/105 km, 580 Wh, 7 kg etc.) and why they are suspected too optimistic | When sanity-checking results |
| `08_benchmarks.md` | Comparable aircraft numbers for sanity checks (DeltaQuad, Avy, Aviant, Wingcopter…) | When judging whether a result is plausible |
| `09_open_questions_risks.md` | Unknowns, missing inputs, risks | Before claiming anything is final |
| `10_working_style.md` | How Lucas wants Claude to communicate and work | Always |
| `11_history_log.md` | Chronological log of every project conversation and decision | When you need to know why something was decided |

## Retained-source supplement (read first)

- `12_fumes_handoff.md`: slicing, mass, hardware, CG, CFD and geometry qualifications from checked Fumes artifacts.
- `../docs/CONTEXT_CONFLICTS.md`: discrepancies and genuine decisions for Lucas.
- `../data/hardware/fumes-import/IMPORT_MANIFEST.json`: copied-source paths and hashes.

## reference/ (original source snapshots; see qualification banners)

| File | Origin |
|---|---|
| `Goals.md` | The project's original goal statement (2026-10-03) |
| `preliminary-design-report-2026-10.md` | Full text of the team's Preliminary Project Report (Google Doc), including all tables |
| `qxf7-stork-baseline-geometry.md` | Verified geometry baseline for Flow5 (2026-10-17) |
| `qxf7-success-criteria-sources.md` | Sources/notes behind the requirements section |
| `qxf7-design-sources.md` | Sources/notes behind the design section |
| `qxf7-factcheck-2026-10-11.md` | Fact-check corrections log |
| `qxf7-report-sources.md` | Report reference list |
| `qxf7-competitor-landscape.md` | Full competitor research report (~10k words) |
| `qxf7-healthcare-outreach-plan.md` | Full healthcare outreach plan |
| `cad-inventory-summary-2026-10-17.md` | The CAD file inventory (STL/STEP audit) |
| `stork-manual-v2-text.txt` | Text extraction of Flightory's Stork User Manual v2 |
| `stork-vtol-manual-v2-text.txt` | Text extraction of Flightory's Stork VTOL User Manual v2 |

## data/

| Path | What |
|---|---|
| `data/stork-geometry-bundle/` | The verified CAD extraction bundle (197 files): airfoil `.dat`s, `geometry_table.csv`, wing/tail/fuselage sections, reports. Start with its `EXTRACTION_REPORT.md` |
| `data/hardware/` | Released slicing masses and historical standard-size hardware/installed-mass evidence now imported; final hardware remains unfrozen. Read `12_fumes_handoff.md` and `../docs/CONTEXT_CONFLICTS.md` |

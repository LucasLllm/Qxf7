# CLAUDE.md: QxF7 performance repo

> **Retained-source audit:** Read `context/12_fumes_handoff.md` and `docs/CONTEXT_CONFLICTS.md` FIRST. They qualify the older geometry interpretation and add released slicing evidence, historical hardware/installation ledgers and predicted print centroids. Latest Lucas clarification: omit budget for now; final QxF7 targets≥70km/h cruise. PhaseA models standard Stork with ONE4-in-1 lift ESC; separate ESCs for QxF7 are only a future option. Final severe-cold envelope remains unvalidated, not a blocker to stock performance assessment. This context-import task does not authorize starting simulations, purchasing or publishing.

## What this repo is
Performance estimation for **QxF7**, Fumes Technologies' 3D-printed electric 4+1 quadplane (scaled Flightory Stork VTOL) for scheduled lab-specimen delivery to remote Quebec clinics. Team: Lucas Liu and Mario Pacheco Senda (students). Nothing is built yet.

**Current phase:** simulate and calibrate the **standard Stork VTOL** (Phase A). Scaling to QxF7 (Phase B) comes only after Phase A matches published/builder data.

## Read first
`context/00_INDEX.md`, then `01`, `02`, `04`, `05`, `06`, `07`, `10` at minimum before writing analysis code. The geometry is in `data/stork-geometry-bundle/` (start with its `EXTRACTION_REPORT.md`).

## Non-negotiable rules
1. **Label every number's provenance**: `official` (Flightory manual), `third-party` (Flightony: calculated, not flown), `builder` (ArduPilot Discourse logs), `model` (our computation), `assumption`. Never mix them silently. Report tables carry a source column.
2. **Every range/endurance figure states its conditions**: airspeed, AUW, payload, temperature/density, wind, reserve, usable fraction, aging, hover/transition time. Don't double-count DoD, reserve and aging.
3. **Don't invent decisions.** Scale factor, span, MTOW and routes are not chosen. A historical standard-size4S reference, installed-mass ledger and58sliced part definitions now exist in `data/hardware/`; final scaled hardware is NOT frozen. Read context/12: the standard-Stork4-in-1 lift-ESC baseline is now confirmed as a modeling choice. Resolve gross-cargo packaging accounting only for loaded cases; it does not block unloaded PhaseA. Use manufacturer hardware for a separately labeled published/vendor comparison case, not as a silent replacement of the all-Bambu reference.
4. **Geometry qualifications** (`context/12`, then `05`): gross reference area31.245148dm² is hybrid, not the exposed projection. V-tail local and aircraft-projection angles have different definitions; use explicit3D vectors and solver conventions, not an unconditional sign/number substitution. STEPzero is NOT a verified physical wing-root LE/CG datum; x=47mm is only a provisional model case pending registration. Saved control pose is not independently certified neutral. Preserve diagnostic/truncated sections separately and the original failed length gate. Convex envelope is not exact wetted area or a proved upper bound.
5. **Calibrate before you extrapolate.** Phase A must hit the calibration targets in `context/06` or explain the miss.
6. **Independent check** for headline results: a second method (hand calculation, different tool, or published data) must agree within stated tolerance before the number goes in a report.
7. **License/publication:** keep vendor CAD/manual PDFs/toolpaths local and out of git. A private repo is not an automatic license grant; review existing manual text extractions and derived artifacts before any publication/upload. No remote creation or push without Lucas's approval. Preserve originals read-only.
8. Units: SI/metric (m, m/s with km/h in parentheses, kg, N, W, Wh, °C).

## Communication with Lucas
Direct and technically precise; tables over prose; flag estimates vs sourced facts; expect pushback and re-derive rather than defend (`context/10_working_style.md`). Ask only when a decision is genuinely his.

## Machine
macOS (Mac Mini, user `lucasliu`). Another agent workspace with the original CAD and notes lives at `/Users/lucasliu/.hermes/profiles/fumes/` (read-only for this repo; never modify source CAD). Python 3 with a project venv. Install tools as needed and record exact versions in `docs/ENVIRONMENT.md`.

## Repo layout (create as needed)
```
context/        project knowledge (read-only unless Lucas asks)
data/           geometry bundle, hardware inputs, downloaded prop/motor data (with source URLs)
src/qxf7perf/   python package: geometry, airfoils, aero, drag, propulsion, battery, mission
runs/           dated run outputs (csv/json/png), never overwritten
reports/        markdown reports for Lucas/Mario, each with assumptions + sources
tests/          unit tests incl. hand-calculation checks
docs/           ENVIRONMENT.md, DECISIONS.md (log every modelling decision + why)
```

## Git
Commit in small steps with clear messages. Never commit vendor CAD/PDFs, large caches or secrets.

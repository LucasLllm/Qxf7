# 01 Project overview

## Who
- **Fumes Technologies**: Lucas Liu and Mario Pacheco Senda, two students in Quebec (Lucas is in the Gatineau area). Non-profit for now; may become a company later.
- Preparing a **Preliminary Project Report** for their teachers (Google Doc, 18 pages, full text in `reference/preliminary-design-report-2026-10.md`).
- Lucas runs a Mac Mini as an always-on machine (macOS user `lucasliu`). Another agent workspace exists on it at `/Users/lucasliu/.hermes/profiles/fumes/` (the CAD inventory and geometry extraction were produced there, e.g. `notes/stork-development/source-format-audit/`).

## What
**QxF7**: a 3D-printed, fully electric **4+1 quadplane** (4 lift motors + 1 pusher, V-tail), built by **scaling up the Flightory Stork VTOL**, for **scheduled same-day lab-specimen runs** (and secondary medication delivery) between remote nurse-run clinics in Quebec and hospital labs.

Project goal sentence (from the report): *"Our goal is to move medical supplies and lab samples between remote Canadian communities and the hospitals that serve them faster and more reliably, all year round, winter included."*

## Status (2026-10-17)
- **Nothing is built.** Planning and design only.
- Files bought: Flightory **Stork** (US$29.99) + **Stork VTOL Pack** (US$12.99): all STL, STEP for key parts.
- Per Lucas: slicer weight estimates exist for the printed parts (Bambu CLI), filaments are chosen per part, and a battery and motors are chosen. **These specifics are not in Claude's records** and must be obtained from Lucas or the Mac (see `09_open_questions_risks.md`).
- A verified geometry extraction of the standard Stork VTOL exists (`data/stork-geometry-bundle/`, summarized in `05_cad_geometry_extraction.md`).

## Fixed requirements (details in `02_requirements.md`)
| Requirement | Value |
|---|---|
| Payload | **750 g gross** (samples + UN3373 triple packaging + insulated box) |
| Range | **~95 km one way**, straight line between pads, fresh battery at each end |
| Cruise speed | **≥ 70 km/h** |
| Winter | Normal winter ops down to **−30 °C** with warmed batteries; icing excluded from scope |
| Take-off/landing | Vertical from a small pad |
| Budget | Deferred; establish performance feasibility first. No active monetary constraint for this study. |
| Approval | Transport Canada compliant |

## Key decisions so far
1. **Layout:** 4+1 quadplane with V-tail (nothing tilts; two independent propulsion systems; ArduPilot QuadPlane support).
2. **Base airframe:** Flightory Stork VTOL, chosen over Stallion, Super Stingray, Moose.
3. **Scale it up:** firm decision, but **scale factor, span and mass are not chosen**. They are to be derived from the 95 km / 750 g requirement plus mass and energy budgets. The report deliberately states no size or mass.
4. **Materials:** winter focus; LW-ASA instead of LW-PLA for light parts was discussed, PC for high-load parts; separate lift ESCs (instead of a 4-in-1) were recommended.
5. **Range over speed:** "maximum winter range at a safe minimum cruise speed" (≥70 km/h) replaced the original "as fast as possible".
6. **Performance-estimation approach (2026-10-17):** first estimate the **standard Stork VTOL** via simulation and calibrate against Flightory's published numbers and real builder data; only then scale to QxF7. Tools: **Flow5/XFLR5 + OpenVSP + eCalc + a Python mission model** (see `06_performance_method.md`).

## The immediate task
Get a simulation-based performance estimate (drag polar, power-required curve, stall/best-endurance/best-range/max speed, hover power, endurance and range for mission profiles, at +20 °C and −30 °C) of the **standard Stork VTOL**, calibrated against known data. The exact brief is `prompts/02_performance_simulation.md`.

## Role model and context
- **Aviant** (Norway, student-founded, electric fixed-wing VTOL, hospital blood samples 120 km in 2021) is the model the team wants to follow; it later drifted to consumer food delivery for revenue.
- **CORRIDAIR** (Vertiko Mobilité + Jaunt/AIRO) already holds the Manawan corridor politically; QxF7 should position as complementary.
- **Flightory license:** personal, non-commercial only; explicitly excludes organizations, schools and research institutions, including built aircraft. Unresolved; a commercial/institutional license or a clean-sheet airframe will be needed before operating for clinics.

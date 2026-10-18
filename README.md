# qxf7-performance

Simulation-based performance estimates for **QxF7** (Fumes Technologies), starting with the standard Flightory Stork VTOL as the calibration case.

## Retained-source reconciliation
Read **`context/12_fumes_handoff.md`** and **`docs/CONTEXT_CONFLICTS.md`** before older summaries.58released print definitions/82installed pieces,58parent receipts, mass accounting, predicted print centroids and a historical4S reference are now imported under `data/hardware/`. Run `python3 scripts/verify_fumes_context.py` to verify transfer integrity. No simulation has been run.

## Setup (once)
1. **Only after Lucas explicitly approves publishing and the license/material review is complete**, create a private GitHub repo (`qxf7-performance`). The following commands are historical setup instructions, NOT permission to run them:
   ```bash
   cd qxf7-performance
   git init && git add . && git commit -m "Initial context pack and geometry bundle"
   gh repo create qxf7-performance --private --source=. --push
   ```
2. Read the populated `data/hardware/slicer_weights.csv` and NON-OPERATIVE `standard_stork_reference.json`. `hardware.yaml` is intentionally unfrozen. Resolve `docs/CONTEXT_CONFLICTS.md`; do not ask Lucas to re-enter available masses.
3. Open Claude Code in this folder and paste `prompts/01_onboarding.md`.
4. When it has reported back, paste `prompts/02_performance_simulation.md`.

## What's here
- `CLAUDE.md`: standing rules Claude Code loads automatically.
- `context/`: everything known about the project (start at `context/00_INDEX.md`).
- `data/stork-geometry-bundle/`: verified wing/tail/fuselage geometry of the standard Stork VTOL extracted from the CAD.
- `data/hardware/`: released predicted slicer masses, historical hardware/mass ledgers, source receipts and the intentionally unfrozen hardware template.
- `prompts/`: the two prompts to give Claude Code.

## Not in this repo (on purpose)
Original Flightory STL/STEP files and the PDF manuals (license: personal, non-commercial). They stay on your Mac; text extractions of the manuals are in `context/reference/`.

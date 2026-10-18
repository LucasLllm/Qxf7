# Prompt 1: Onboarding (paste into Claude Code first)

> **Before this older prompt:** Read `context/12_fumes_handoff.md` and `docs/CONTEXT_CONFLICTS.md`. Released slicing/installed-mass/historical4S evidence is now imported. Use explicit solver-frame registration for CG/incidence, preserve the failed original length gate and do not call convex surface a wetted-area upper bound. Vendor/builders are comparator evidence, not enough to establish accuracy bands. Latest Lucas clarification: omit budget, use ONE4-in-1 lift ESC for standard-Stork PhaseA, and keep≥70km/h as the modifiedQxF7 cruise target—not a forced stock optimum. Separate ESCs are undecided for the modified aircraft. Resolve cargo packaging only when modeling loaded cases; do not block unloaded PhaseA on final-aircraft decisions. This migration audit itself does NOT authorize running this prompt, installing software or uploading files.

You are joining an existing engineering project mid-stream. Before doing any work, load the full project context and prove you understand it. Do not write analysis code in this step.

1. Read `CLAUDE.md`, then every file in `context/` in the order given by `context/00_INDEX.md` (01 → 11). Then skim the files in `context/reference/` enough to know what each contains; read `reference/preliminary-design-report-2026-10.md` and `reference/qxf7-stork-baseline-geometry.md` fully.
2. Open `data/stork-geometry-bundle/` and read `EXTRACTION_REPORT.md`, `EXTRACTION_LIMITATIONS.md`, `GATE_REVIEW.md` and `assembly_notes.md`. Load `geometry_table.csv`, `wing-extraction/sections.csv`, `tail-extraction/profile_summary.csv` and `fuselage-with-hatches/cross_sections_50mm.csv` and independently re-check these numbers (write a small throwaway script; don't commit it):
   - span ≈ 1620.5 mm, gross wing area ≈ 31.25 dm², MAC ≈ 195.7 mm;
   - linear fit of clean wing stations (y 88–730 mm): chord(0) ≈ 230.2 mm, LE x(0) ≈ 0, incidence(0) ≈ 2.52°, incidence(730) ≈ 0.69°;
   - V-tail cant ≈ 35.1°, local incidence ≈ −0.82°, total projected area ≈ 7.34 dm²;
   - wing→tail quarter-chord arm ≈ 505 mm.
   Report any disagreement larger than 1%.
3. Check what is missing for Phase A: look in `data/hardware/` and, read-only, in `/Users/lucasliu/.hermes/profiles/fumes/` (especially `notes/stork-development/`) for the chosen battery, motors, props, ESCs, filaments and Bambu slicer weights. List what you found, with file paths. Do **not** modify anything under `.hermes`.
4. Check the local toolchain and report what is installed or installable on this Mac: Python version, numpy/scipy/pandas/matplotlib, XFoil (binary) and/or NeuralFoil, AeroSandbox, AVL, OpenVSP with its Python API, and whether Flow5/XFLR5 is installed (GUI; Lucas may run it himself). Install nothing yet; just report and propose a setup.
5. Then reply to me with:
   - a 10–15 line summary of the project, the requirements, and the current phase in your own words;
   - the verification table from step 2 (value, your check, Δ%);
   - the missing-inputs list from step 3 and the exact questions you need me to answer;
   - the toolchain report and your proposed setup (a venv plus a `docs/ENVIRONMENT.md`);
   - anything in the context that looks inconsistent, outdated or wrong. I want pushback, not agreement.

Keep every number labelled by provenance (official / third-party / builder / model / assumption).

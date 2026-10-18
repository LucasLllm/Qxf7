# Current status — extraction authorized with distinct length references

Lucas explicitly approved: **“Yes, continue extraction.”** See `extraction_authorization.json`. Use **1000.000 mm nose-to-pusher mounting face** and **1044.020 mm nose-to-rearmost fixed tail** as distinct envelopes; do not rescale or reposition geometry to force a match. The original +4.402% overall-length gate failure remains in `GATE_REVIEW.md` and `reference_gate.json` as audit history, not an unanswered approval request.

The **45-component feature-registered review assembly** remains a partial reference subset, not a complete installed VTOL. Its historical span **1620.541 mm** and coarse gross reference area **31.2115 dm²** passed their reference comparisons. Extraction is now integrated in `EXTRACTION_REPORT.md` and `geometry_table.csv`: **32 profiles,1,017 geometry rows**, wing/tail angles and geometric arms, real hatch-inclusive fuselage sections, hardware dimensions and reviewed orthographic views. Final refined gross reference area **31.245148 dm²** is distinct from both the coarse historical estimate and physical occupied projection. `fuselage-with-hatches/` is authoritative for current fuselage outputs; earlier `fuselage-extraction/` is a hatch-omitting baseline. Current common-frame origin is unchanged STEP zero, not the historical proposed root-LE origin. Motor/boom-end placement, aerodynamic control neutral, exact exposed wetted area and full rear FUS4 hatch-tongue qualification remain unresolved. No flightworthiness or complete installed-aircraft claim follows. Sources remain read-only. See `delivery_verification.json` and `bundle_receipt.json` for actual final receipts.

## Historical wing-area checkpoint (superseded assembly status)


**The previous pre-assembly reference blocker below is superseded.** See `AREA_DISCREPANCY.md` for fresh primary-source captures, CAD projection measurements and independent checks. Flightory's 2023 introduction genuinely lists 24 dm²; both current manuals list 31 dm². The current CAD diagnostic supports approximately 31 dm² gross area, but it is not a verified assembly. The conflict alone does not block feature-based assembly or measurement against the user's original target. No complete assembly, installed-angle extraction or assembled validation gate has been performed.

The following initial blocker record is retained as historical evidence, not current guidance:

---

# Stork VTOL aero geometry — validation reference blocker

## Status
**BLOCKED BEFORE ASSEMBLY — reference conflict, not a measured geometry failure.**

All 108 source/manual hashes match `cad_inventory.csv`. Prior provisional assembly transforms were not used as placement authority. No source geometry was changed, converted or moved.

## Verified reference conflict
Both retained Flightory manuals, printed **page 5**, explicitly state:

| Quantity | Requested target | Published Flightory value | Assembly measurement |
|---|---:|---:|---|
| Wingspan | 1620 mm | 1620 mm | unknown — not assembled |
| Overall length | approximately 1000 mm | 1000 mm | unknown — not assembled |
| Wing area | approximately 24 dm² | **31 dm²** | unknown — reference blocked |

- Base manual: `/Users/lucasliu/.hermes/profiles/fumes/notes/stork-development/material-selection/base-manual-source.pdf`
- VTOL manual: `/Users/lucasliu/.hermes/profiles/fumes/notes/vtail-4plus1-catalogue/evidence/STORK-USER-MANUAL-VTOL.pdf`

Published area exceeds the requested reference by **29.166667%**, calculated as `100 × (31 − 24) / 24`. This compares **reference values**, not measured aircraft geometry.

The ±2% intervals do not overlap:
- Requested 24 dm²: **23.52–24.48 dm²**.
- Published 31 dm²: **30.38–31.62 dm²**.

No evidence establishes that 24 dm² represents exposed area, an alternative wing, or another area definition. Those explanations are not guessed. Page 5 does not define the exact area-integration convention; measured planform convention must be documented even if 31 dm² is selected.

## Required decision
Resolve the controlling wing-area reference before feature-based assembly and extraction:
1. Authorize **31 dm²**, explicitly published by Flightory; or
2. Retain **24 dm²**, with its intended area definition/reference.

The >2% measured-geometry gate has **not** been claimed to pass or fail. No assembly dimensions have been measured. Work is paused at a prerequisite reference conflict, not because an unmeasured aircraft failed validation.

## Configuration retained for continuation
- Aircraft axes: x aft, y right, z up. Origin is **not yet established**; intended root-leading-edge/centerline origin will follow verified feature placement.
- Use VTOL WING 1.1/1.2, not base WING 1.
- Use VTOL FUS1/2/5/6 plus shared base FUS3 and STL-only FUS4.
- Exclude all slicer modifiers using audited hash-bound physical-body selectors.
- Original alignment pins/holes, spar/hinge axes and rear fuselage features must establish placement, not provisional assembly transforms.
- Booms are **square**, nominal 10 × 10 × 500 mm, not circular-diameter tubes. VTOL pp.34–37 supplies guide arrangement; p.35 gives a 150 mm tube-end-to-guide-side datum. Installed coordinates and wall thickness remain unknown here.

## Deliverable status
Only this blocker report and `reference_gate.json` are produced. No station table, airfoil files or assembled-outline images are fabricated. Angles, tail arms, station metrics, fuselage sections, wetted area and hardware positions remain **unknown — not yet measured**. Exact source text and hashes, reference values and explicit null measurements appear in `reference_gate.json`.

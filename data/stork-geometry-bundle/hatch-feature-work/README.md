# Original STEP hatch placement — verified nominal source-native pose

## Outcome and coordinate frame
Both original files contain **two physical hatch solids**; all four belong in the installed fuselage skin. These are not slicer modifiers. `FUS 2 VTOL MODIFIER.STEP` body **1** is the physical fuselage; body 2 is excluded. Sources were selected from `source-format-audit/cad_inventory.csv`, hashes matched that authority, and retained CAD is unchanged.

**All four recovered source-to-native transforms are the 4×4 identity**, now supported by mating geometry, not merely saved/native identity. Units mm. Aircraft rotation, before a separately established aircraft-datum translation, is `(x,y,z)=(nativeZ,nativeX,nativeY)`. No guessed wing-origin translation is introduced. Each nominal-pose constraint Jacobian has rank 6 and no remaining continuous nominal DoF; actual clearance/play is not a certified manufacturing tolerance.

## Evidence, not bounding-box registration
- **Front body 1 → FUS1:** eight matching tongue/fillet axes with radii 1→1.4 and 2→2.4 mm, plus bilateral curved lips 29.6→30 mm. Independent tongue-plane and lateral ledge gaps are **0.4 mm**.
- **Front body 2 → front body 1/FUS2:** three shared radius-1 alignment-bore axes and their split plane at native Z **−111.250886356 mm**. Bilateral lip radii **39.6→40** and **24.6→25 mm** independently check FUS2. Lower ledges and front end gap are **0.4 mm**. These are bores for omitted joining pins, not fictitious solid male pins.
- **Middle body 1 → FUS3:** bilateral radius **24.6→25 mm** lip axes and **0.4 mm** side/end clearances. Parallel native-Y axes alone leave Y translation; this is resolved by the **original common outer BSpline skin** (not by assuming source identity). Samples project onto original FUS3 skin support surfaces with maximum **0.000217 mm** residual for this body. The explicit point anchor is in JSON. Latch supporting-plane offsets of 0.3 mm are **not direct seating clearances**: the trimmed faces are disjoint. They are not used to solve placement.
- **Middle body 2 → middle body 1/FUS3:** three shared radius-1 bore axes and split plane at native Z **149.149113644 mm**; independent lip **99.6→100 mm** checks FUS3.
- **Middle body 2 rear → FUS4:** independent mesh check uses the existing seven-circle/two-end verified FUS4 transform. Left/right radius-25 arc fits give radial clearance about **0.4052 mm**, axis XZ errors **0.00561 / 0.00560 mm**, maximum radial fit residual **0.01146 mm**. This is mesh-resolution evidence, not an exact STEP mate. Full rear tongue trimmed-plane seating and mesh/solid penetration remain uncertified; no nominal pose DoF remains because the front split joint plus FUS3 lip already fix the pose.

All selected axis offsets are below 1e−5 mm (actual maximum about 4.74e−12 mm). Ten external skin face-pair continuity checks, restricted to overlapping longitudinal source ranges, have maximum sampled projection residual **0.000517 mm**. Projection is onto each adjacent *original untrimmed BSpline support surface*, not onto a synthesized envelope and not a claim that the trimmed faces overlap. This verifies shared source-skin continuity; finite samples are not a global surface-equality proof.

Five overlapping hatch/FUS1–3 BRep pairs have **zero intersection volume** and actual whole-solid minimum clearances **0.398684–0.399957 mm**. Exact face identities, fitted transforms before tolerance snapping, residuals, face support-plane gaps versus trimmed distances, source bounds, source hashes and after-processing checks are in `placement.json`.

## Deliverables for extraction
- `installed_hatches.step`: **four unchanged complete physical BRep solids** in recovered installed native coordinates. Retains all original tongue, bore and latch geometry. Use this with physical fuselage sources for real sections; do not convex-close missing hatch regions.
- `external_skin_patches.step`: **ten untouched main outer BSpline faces**, selected by source body/face IDs below. Area **54739.089334 mm²** is only this patch subset, **not total fuselage wetted area**. Recesses and small cutout sidewalls are not counted here; complete solids retain them.
- `exact_skin_sections.step`: original patch/plane intersection curves at 14 transverse native-Z stations. They intentionally remain open top-patch curves; no artificial bottom or seam closure.
- `features.json`: compact full per-solid face inventory for the two hatches and three smooth mate files, including excluded modifier-body geometry for inspection.
- `placement.json`: compact primary receipt, all transforms, constraints, hashes, bounding changes, measured clearances, section bounds and residual samples.
- `fus4_lip_check.json`: independent source-hash-bound rear mesh lip evidence.

| Source | Physical body | Main external face IDs (1-based) |
|---|---:|---|
| HATCH FRONT.STEP | 1 | 38, 39 |
| HATCH FRONT.STEP | 2 | 11, 44, 66, 67 |
| HATCH MIDDLE.STEP | 1 | 53, 54 |
| HATCH MIDDLE.STEP | 2 | 39, 40 |

IDs refer to `cq.importers.importStep(path).solids().vals()[body-1].Faces()[face-1]` for the hash-bound original source, **not** re-export traversal. Exact volume, face count and bounds provide additional selectors. All hatch-local bounds remain unchanged under the recovered identity. Against the deliberately limited FUS1/2/3 baseline, adding hatches increases native-Y maximum by **0.065609987 mm** and native-Z maximum by **54.571733592 mm** (the latter extends beyond FUS3, not beyond the complete fuselage). Actual local section-top changes are substantial: at native Z −160/−80/110 mm, top rises **40.82947 / 47.57348 / 15.46124 mm**. Baseline maxima include existing internal features; these numbers are section AABB changes, not areas. Z250/270 baseline is explicitly null because smooth FUS4 is unavailable here. No whole-aircraft extent claim.

## Reproduce
Only this output directory is written. The complete commands are:

```sh
/Users/lucasliu/.hermes/profiles/fumes/research-venv/bin/python -B /Users/lucasliu/.hermes/profiles/fumes/notes/stork-development/stork-aero-geometry/hatch-feature-work/investigate.py
/Users/lucasliu/.hermes/profiles/fumes/research-venv/bin/python -B /Users/lucasliu/.hermes/profiles/fumes/notes/stork-development/stork-aero-geometry/hatch-feature-work/fus4_probe.py
/Users/lucasliu/.hermes/profiles/fumes/research-venv/bin/python -B /Users/lucasliu/.hermes/profiles/fumes/notes/stork-development/stork-aero-geometry/hatch-feature-work/resolve.py
```

`resolve.py` asserts all four constraint ranks, axis residuals, seam-plane residuals, finite skin-continuity checks, zero hatch/FUS1–3 intersection volume, STEP reload validity, four complete solids, ten skin faces and bound serialization agreement <1e−5 mm. The actual clean-cache serialization bound difference is ~2.15e−11 mm. Diagnostic tessellation caches are explicitly removed before measuring BRep bounds: cached tessellation had initially changed reported bounds; no tolerance relaxation is retained. STEP byte hashes may change on rerun because of exporter metadata; the new receipt binds the actual generated files.

`probe.py` and `continuity_probe.py` retain the exploratory checks. Neither `fuselage-extraction/` nor any original CAD was modified. No convex hull, replacement cap, scaling, mesh-as-smooth substitution, or vented-STL substitution was used.

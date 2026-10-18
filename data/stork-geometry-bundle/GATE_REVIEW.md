# Stork feature-registered assembly: measured-dimension gate

## Status: STOP — overall length exceeds 2% tolerance

This is a source-CAD geometry check, not physical measurement, aircraft qualification, or flightworthiness evidence. Original manufacturing geometry was not modified. No downstream aerodynamic station extraction was performed.

| Quantity | CAD measurement | Reference | Difference | Gate |
|---|---:|---:|---:|---|
| Span | 1620.541 mm | 1620 mm | +0.033% | Pass |
| Gross wing reference area | 31.2115 dm² | 31 dm² | +0.682% | Pass, with stated convention |
| Registered airframe overall length | 1044.020 mm | 1000 mm | +4.402% | **Fail** |

## Why the length differs

The registered nose front to the 19×19 pusher mount rear face measures 1000.000 mm. The installed fixed tail tip extends farther aft; nose to that tip measures 1044.020 mm. Tail/fuselage placement is established by mating geometry, not adjusted to hit a target dimension.

This strongly suggests the published 1000 mm describes the nose/pusher envelope rather than the outermost tail envelope. The intended vendor convention is not independently documented, so it does not justify silently replacing the overall-length acceptance check. Final equipped length remains unknown; omitted hardware cannot reduce the already failing registered extent.

## Actual assembly deliverable

`reference-assembly/Stork-feature-registered-gate-review.glb` contains **45 individually named components**. This is a tessellated review assembly, **not original STEP/native CAD**, not a completed production assembly, and not a completed aerodynamic surface. Its JSON manifest preserves original source paths, hashes, selected physical STEP bodies, transformations, bounds, and feature-evidence references.

- VTOL wing-root parts: physical bodies only; modifier volumes excluded.
- Wing panels: front/rear spar axes and panel butt faces register the parts. Individually shifted STL print heights were removed through bore-center fits.
- Wing tip: original STL used. Differently posed smooth STEP is not passed off as a proven equivalent.
- Fuselage: pin patterns/axes, interface planes, and registered STL-only FUS 4 connect the chain.
- Tail: three root pin axes plus its mating plane register the inner panel; corresponding panel-end features register subsequent sections.
- Ruddervators: both real smooth STEP segments retained, in source-saved zero pose with no added hinge rotations. Hinge alignment verified; **aerodynamic neutral/commanded 0° is not established**.
- Opposite outer-wing/fixed-tail geometry: explicit symmetry construction from registered geometry, not independently verified left-print STL placement.
- Skid, 19×19 pusher reference mount, and four complete wing boom-clamp pairs: mating-feature placement, with authored clearances retained. Pusher mount is reference geometry, not a new hardware purchase/selection.

## Area convention

Gross area is the projected outer-wing silhouette including controls in saved-source pose, plus rectangular root-region centerline continuation. Hidden centerline area is a reference-area extrapolation, not physical CAD. Root plates are not separately added, avoiding overlap. Hinge-gap skin reconstruction and aerodynamic-neutral confirmation have not occurred before the gate.

## Explicitly unfinished / omitted

- Lift-motor clamp pairs have coherent relative geometry, but installation along the tubes remains unresolved. No arbitrary motor positions were inserted.
- Nominal 10×10×500 mm tubes: p.35's 150 mm guide reference is understood, but fore/aft assignment remains unresolved. No guessed installed tube geometry is included.
- Motors, propellers, electronics, fasteners, and all small covers/retainers are incomplete.
- Front 3 mm reinforcement interface is retained as a gap; full reinforcement XY placement is not solved.
- No airfoil stations, incidence/dihedral release, UIUC matching, fuselage station table, or wetted-area estimate was produced. UIUC coordinates were downloaded with provenance for later comparison only.

## Coordinates

Millimetres; x aft = source Z, y right = source X, z up = source Y. Origin is the common source STEP datum, not a claimed wing-root LE origin. Fuselage pin-chain and main-spar mating features establish relative alignment. Datum translation does not change these dimensional gate results.

## Verification

- All **108** inventory source/manual SHA-256 checks pass: no changed originals.
- Exported GLB reloaded successfully: **45/45** named geometries.
- Reloaded bounds match manifest within **0.0002 mm**. This is serialization consistency, not manufacturing accuracy.
- Top/front/side review PNGs generated; side view marks 1000 mm and 1020 mm from the nose. These are projected vertex overlays including internal geometry, not reconstructed outer aerodynamic skins.
- Airfoil helper tests: **3 passed** using synthetic analytical fixtures; these are software tests, not extracted aircraft results.

## Recommendation requiring gate adjudication

Keep source geometry unchanged. Retain **1000 mm as the demonstrated nose-to-pusher reference** and use **1044.020 mm as measured registered-airframe overall reference**, then continue aerodynamic work only once Lucas accepts that distinction. Do not shorten the tail, rescale the aircraft, or label the original overall-length gate passed.

## Reproduction and evidence

Interpreter: `/Users/lucasliu/.hermes/profiles/fumes/research-venv/bin/python -B`.

- `inspect_wing_features.py` → analytic STEP spar axes and STL bore sections.
- `assemble_wing.py` → physical-part wing placement, seam checks and area receipt.
- `tail-feature-work/README.md`, `placements.json`, and registration scripts → tail planes/axes and rudder pose evidence.
- `fuselage-feature-work/RESULTS.md`, `verified_chain.json`, and registration scripts → fuselage, FUS 4 and hardware evidence.
- `assemble_reference_gate.py` → combined assembly, measured gate, GLB reload, source hashes, review PNGs.

The parent script exits successfully when it produces a valid **failure receipt**. Geometry acceptance is `reference_gate.json.status`, not the process exit status.

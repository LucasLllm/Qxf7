# Standard Stork — CFD APPROXIMATE installed motors and booms

**Completed, independently verified hardware-only derivative.** Four T-Motor F90 lift motors, one BrotherHobby Avenger 2812 V5 pusher, and two circular-bore square booms. This is the original standard Stork, **not** the enlarged mission aircraft. All writes are confined to this directory; retained manual/datum work and parent airframe were not modified.

## Deliverables and integration

- `Stork-standard-installed-motors-booms-CFD-APPROXIMATE-m.obj`: **metres**, +X forward / +Y left / +Z up, already installed. **7 closed material surface shells, 6,330 triangles.** No airframe, propellers, disks, bolts or wires.
- Matching `.step`: **millimetres**, seven valid native OpenCascade approximation solids. These are generated parametric BReps, **not vendor-supplied native CAD**.
- `components/`: 17 OBJ/STEP pairs: two local motor definitions, five installed motors, two baseline booms, eight alternative boom surfaces. Do **not** add local definitions or alternative booms to the baseline.
- `RESULTS.json` and `PLACEMENT_AND_SUBSTITUTIONS.json`: paths, hashes, per-component metadata and full proper rigid placement matrices in both metre and millimetre conventions. Installed files have transforms applied; do not apply again.
- `VERIFICATION.json`: independent-process STEP/OBJ reimport, exact-coordinate manifold topology, exact triangle intersections, independent inclusive-AABB candidate counts, controls and preservation evidence.
- `CAD_BASELINE_INTERSECTIONS.json` and `CAD_MOUNT_INTERSECTIONS.json`: native BRep diagnostics; distinct from exact dyadic mesh tests.
- `RESEARCH_RECEIPTS.json`, `SOURCE_AND_APPROXIMATION.json`, `sources/`: actual HTTP responses, timestamps, content hashes, source-vs-assumption ledger and saved actual pages/drawings. `FINAL_RECEIPT.json` binds final files.

Use this as a **hardware replacement set**, not an automatically Boolean-integrated complete-aircraft exterior. Parent owns airframe integration/contact qualification. Source motor bases/boom ends touch printed mounting surfaces nominally; interface overlaps, inaccessible coincident surfaces and mesh conformity must be addressed at assembly integration. No full-parent-airframe exact test or CFD solution was performed here.

## Authentic source search, bounded outcome

Manufacturer product pages and dimensioned drawings were successfully refreshed, HTTP200:

1. T-Motor F90 family product: https://www.tmotorhobby.com/goods-1057-T-MOTORHOBBY+F90+28065+Long+Range+Motor+-+1300KV1500KV1950KV.html
   - Drawing **discovered in that actual product page**: https://www.tmotorhobby.com/images/20211129/1638150063356533.jpg
   - Documents maximum Ø33.4 mm, seat-to-tip 34.7 mm, seat-to-prop-side shoulder 19.7 mm, M5 shaft and four M3 holes on Ø19 pattern. Family includes1300KV; exact installed mechanical revision remains unconfirmed.
2. BrotherHobby Avenger2812V5 910KV: https://www.brotherhobby.com/avenger-2812-v5-910kv-motorcw-p00234p1.html
   - Drawing **discovered in that actual product page**: https://ueeshop.ly200-cdn.com/u_file/UPAI/UPAI594/2410/photo/913747b78f.jpg
   - Documents maximum Ø33.90 mm, seat-to-tip44.05 mm, tip-to-rear-bell37.60 mm, tip-to-prop-side-bell17 mm and M5. Thus seat-to-rear-bell6.45 and seat-to-shoulder27.05 mm. Separate Ø19/four-M3 and Ø23/three-M3 patterns remain functionally unassigned.
3. Retained-discovered F90 retailer https://www.hobbyrc.co.uk/t-motor-f90-brushless-long-range-motors was also accessible.

Neither relevant manufacturer page nor retailer exposed CAD/download links. Two Google CAD queries returned retry interstitials; two Bing fallback queries returned unrelated results despite HTTP200. No authentic accessible motor CAD was recovered within this bounded search. This is **not evidence that no CAD exists anywhere**. An unrelated F100 page was fetched during retained-link discovery and is explicitly not a source for the F90 geometry. No guessed CAD URLs, credentials, purchases or vendor contact.

## Model definitions — deliberate approximation, not occupancy cylinders

Both motors have an axisymmetric stepped mounting base, reduced neck, maximum-diameter bell, tapered shoulder and smooth Ø5 shaft. Nominal documented axial landmarks and maximum diameter are preserved. This is a closed-material, external-drag simplification; original vent/open-stator topology is **not** recovered.

| Parameter | F90 | Avenger2812V5 | Provenance |
|---|---:|---:|---|
| Maximum bell diameter mm |33.4|33.9|Manufacturer drawing|
| Seat-to-tip mm |34.7|44.05|Drawing|
| Seat-to-prop-side shoulder mm |19.7|27.05|Drawing/derived|
| Seat-to-rear bell mm |6.2|6.45|**F90 assumed**, Avenger drawing-derived|
| Base diameter mm |24|25|**Assumed**|
| Base thickness mm |3|3.4|**Assumed**|
| Neck diameter mm |14|14|**Assumed**|
| Full-diameter bell ending mm |18.2|25.5|**Assumed**|
| Shoulder diameter mm |29|30|**Assumed**|
| Shaft diameter mm |5|5|M5 nominal, smooth-thread approximation|

Profile radii/axial stations are saved explicitly in `RESULTS.json`. Mounting bores, vents, thread helix, stator/winding roughness, nut/washer/prop hub, rear shaft clip, wire exits and screws are omitted. Motor roll is unobservable in this axisymmetric model. Suggested base/taper sensitivities in results are **proposals, not exported alternatives or proven physical error bounds**. Maximum-diameter gross v1 cylinders were not silently promoted into exact drag geometry.

### Installation reused, not reinterpreted

F90 source nominal flush-seat planes, exact retained transforms and −Z shaft directions are unchanged: rear X=−340 mm, front X≈210 mm; seat Z=−18.05914554846532 mm; front/rear each retain their original side-specific Y values near ±260.156955 mm. Shaft tips Z=−52.75914554846532 mm; shoulders Z=−37.75914554846532 mm.

Pusher nominal seat X=−663.7491136436045 mm, Y=0, Z=−25 mm; shaft−X. Tip X=−707.7991136436045 mm; shoulder X=−690.7991136436045 mm. Printed19×19 mount retained. No propeller plane inferred. F90 asymmetric fourth source mounting hole is unchanged in the parent; no fastening-fit claim.

### Boom baseline and actual exported sensitivity alternatives

Nominal outer section10×10 mm, length500 mm, X=−315…185 mm, center Z=−9.059145548465365 mm. Right Y=−260.1569551367584, left Y=260.15695486324154. Reuses original end-stop/guide resolution. No guide/tooling exported.

**Baseline per side:** circular boreØ8 mm, open axial ends with annular material end faces; assumed24×5 mm underside cable opening centered X=−112.46047687230817 mm near retained guide-station midpoint. The opening removes the **single−Z wall** into the bore. Retained VTOLp10 recommends a circular inner profile but gives no bore diameter; p36 requires a single-wall underside cable opening but gives no exact dimensions here. Bore diameter, wall, cut center and cut dimensions are **assumptions**, not recovered installed measurements. Baseline minimum side wall1 mm is a modeling choice, not the warned-about square-bore construction.

Four alternatives per side, **mutually exclusive**:
- Circular boreØ6 mm, min side wall2 mm, same assumed open cable cut.
- Circular boreØ9 mm, min side wall0.5 mm, same cut. Geometric sensitivity only, not a strength/procurement recommendation.
- Circular boreØ8 mm, open axial ends, cable opening assumed flush taped/epoxy-sealed.
- Fully sealed square exterior, enclosed bore/cavity ignored for external flow. This is a **fluid-boundary exterior idealization**, not a physically solid carbon tube.

All tube material surfaces are closed/watertight even when the **fluid** can enter open ends/bore/window. Open-bore/cable-cut shells have Euler−2; taped cut/open-bore shells Euler0; fully sealed square exteriors Euler2. None is a naked four-wall shell. Physical end caps, tape thickness/roughness, wire routing and measured cut geometry remain unavailable. Variant differences explore model dependence, not guaranteed brackets on real drag.

## Executed verification

`research-venv/bin/python .../hardware-research-motors/build.py` and `verify.py` both completed **exit0**. Independent verification:

- All17 component pairs reimported. Every STEP valid/single-solid, every metre OBJ closed, consistently oriented, positive-volume, nondegenerate, all exact-coordinate edge incidences2 and all vertex links one connected cycle. No tolerance-based topology welding.
- **All triangles** of every component checked using retained integer dyadic plane predicates and rational intersection clipping. Shared mesh simplex permitted; **zero forbidden intersections**. Each full inclusive-AABB candidate count independently matched vectorized brute-force enumeration.
- Installed hardware baseline independently serialized/reloaded: seven shells,3,171 exact-coordinate vertices,9,495 edges,6,330 faces; **65,657 full inclusive-AABB candidate pairs, zero forbidden intersections**; Euler6. Controls passed.
- Native baseline7 bodies checked in all21 BRep pairs; zero positive-volume overlap. These are **OCC tolerance-based native CAD diagnostics**, not exact arithmetic claims.
- All16 original positioned boom clamp halves and five original primary motor mounts checked against baseline hardware by native BRep common: zero positive-volume overlap. Does not certify bolts, mechanical contact, manufacturing fit, all other printed parts or whole-parent-airframe intersections.
- STEP-to-mesh bounds max deviation across exports≈0.0211 mm; max relative volume deviation≈0.002901. These are measured tessellation differences, not limits on approximation-to-real-hardware error.
- Meshing requested absolute0.06 mm and angular0.2 rad. Local tessellation vertices canonicalized on a1e−9 mm grid **before** proper placement, only to coalesce CAD seam samples; displacement recorded per component. OBJ uses17 significant digits. No parent/source vertices changed.
- All preserved input-source hashes verified unchanged after execution. Exact predicate source path/hash retained, no shared helper modified.

**Release scope:** documented, user-authorized approximate hardware components with exact serialized-triangle qualification. Not exact vendor hardware, complete installed-aircraft readiness, physical fit, thermal/cooling accuracy, rotor modeling, solved drag or flight safety.

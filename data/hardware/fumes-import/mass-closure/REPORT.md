# Mass inclusions and centroid closure — bounded first release

## Result
**Predicted printed-part mass properties established; complete installed-aircraft mass and CG remain OPEN.** No Fusion model, hardware, original Step3 outputs or delivered Step3 ZIP were changed.

- 58 printed definitions / 82 installed positions processed with no omitted-part errors.
- Predicted printed subtotal: **965.64181164 g**, consistent with independently reconstructed commanded model extrusion.
- Printed-subset centroid: **[-137.33850, -0.23483, -13.14826] mm** in the existing assembly frame (+X forward, +Y left, +Z up).
- That coordinate is relative to the existing assembly origin, NOT wing-root leading edge and NOT whole-aircraft CG.
- 67 inclusion/scope rows and 45 existing hardware proxy locations retained. Hardware envelope midpoints are explicitly NOT assigned as mass centroids.
- Four unit tests pass; 647 independent source/read-back checks pass. These are software consistency checks, not physical corroboration.

## Method and limitations
The new parser reconstructs positive commanded model extrusion and integrates its path first moments. Linear moves use segment means; XY circular moves use exact arc means, not chord midpoints. Z is offset by half the slicer's declared layer height under a uniform-bead cross-section approximation. E-only, Custom/startup, support/brim/purge and similar excluded features do not enter the print model. No second flow-ratio or foam correction is applied.

Actual retained model commands were also checked for M221/volumetric/firmware-retraction/explicit arc-center overrides: the inspected override inventory is M221 S100 once per selected file, with no listed M200/G10/G11/G90.1/G91.1 commands. This observation is specific to this release, not general G-code support.

Centroids are mapped from actual G-code plate space through the retained 3MF normal-component and build-item transforms, then source geometry and recorded assembly transforms. Source registration is checked bidirectionally against mesh vertices, not accepted from a pose matrix alone. Preserved reflections in source-to-CAD correspondences are not silently converted into proper rotations.

These are **predictions**, conditional on selected slicing, raw density, uniform deposited cross-section, layer-height interpretation and the provisional recorded assembly placement. Uncalibrated foaming/shrinkage, bridges, pressure advance, combined unretraction, cleanup, adhesive, finish and measured process variation are not established physical mass properties. No hardware COM or whole-aircraft CG is inferred.

## Inclusion boundaries closed at accounting level
- Factory motor wires already in quoted motor mass are credited; only extra retained route length is incremental.
- Four standalone lift ESCs OR one four-channel board; plus one cruise ESC. Same-SKU quantities aggregate.
- Finished pack counted once; factory pack leads/connector/enclosure not added again. Cell-built pack estimates remain hypothetical assemblies.
- Receiver factory antennas and documented FC stack/GNSS antenna credits retained.
- Packaging/restraint is outside NET cargo. Delivery-return and retained-payload return remain separate.
- No purchased spares, carbon offcuts, PLA tooling, adhesive containers or charging equipment in installed mass.
- Source-unknown accessories remain null. Legacy ESC accessory apportionments do not become per-device specifications or validated bounds.

**Correction captured in the overlay:** old aircraft-side connector allowance says EC5 for 6S, but registered `6s4000` has XT90. Exact mating-half selection must follow each pack, not series count.

Read-only source reviews identified exact supplied accessory inventories for Razor45, ELITE60 and both Tekko boards. Direct source excerpts corroborate listed cables/capacitors/heatsinks/grommets, but not their separate masses or inclusion in the quoted board weights. Supplied does not mean installed: alternative cable lengths are not automatically both counted. Detailed review records: `cache/delegation/subagent-summary-{0,1}-20261009_084959_*.txt`.

## Still needed for complete analytical closure
1. Exact installation configuration/variants and complete retained accessory inventories; no raw registry tuple is qualified.
2. Candidate-specific incremental lead lengths, gauges, connector halves, capacitors/protection and mounting inventory. Avoid overlap with credited factory equipment.
3. Installed carbon cuts, actual bore/profile evidence and all tube roles; full purchased stock is not proven installed material.
4. Mass/centroid models or measurements for complete hardware assemblies, with declared evidence class. Uniform box midpoints cannot substitute silently.
5. Map the manual's physical wing-root leading-edge datum into the assembly frame, and establish an allowable CG range through appropriate engineering review. The manual gives a **47 mm reference point**, not a qualified range.
6. Establish feasible retained pack and payload placement, including clearance/access, wiring bend radius and restraint. The manual's nominal compartment dimensions are not a usable installation envelope.
7. Decide required weather/cold, delivery and optional avionics equipment. These do not become zero merely because the old baseline omitted them. Keep uncommitted growth reserve separate from physical installed mass.

Physical closure additionally requires actual component/assembly weighing and assembled balance checks, with hardware unpowered and propellers removed where applicable. Nothing here authorizes energizing or flight.

## Would a simulator help?
**A mass-properties calculator or CAD mass model is useful now. A flight simulator does not discover unknown masses or mass centroids from appearance.** For supplied inputs it can compute COM and explore pack/cargo shifts; later aerodynamic/stability analysis assesses acceptable CG, and controls simulation assesses the consequences. These are different questions.

The governing first-moment relation is `r_COM = sum(m_i * r_i) / sum(m_i)` with consistent units. Unknown component COMs, scope and mass bounds must be retained, not filled with defaults. Unknown mass with an unknown location cannot produce a defensible finite CG interval.

## Reproduce in the existing Fumes profile workspace
The overlay references retained local source files; it is not a standalone copy of all geometry and toolpaths.

```sh
research-venv/bin/python -B notes/stork-development/performance-scenarios/mass-closure/test_centroid_model.py
research-venv/bin/python -B notes/stork-development/performance-scenarios/mass-closure/build_print_centroids.py
research-venv/bin/python -B notes/stork-development/performance-scenarios/mass-closure/build_closure.py
research-venv/bin/python -B notes/stork-development/performance-scenarios/mass-closure/verify_closure.py
```

Artifact status is `predicted_print_subset_only`; G3 remains **OPEN**. This release makes concrete analytical progress, but does not claim complete inclusion or physical/flight qualification.

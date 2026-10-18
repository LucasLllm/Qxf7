# 05 CAD geometry extraction (standard Stork VTOL)

> **Qualification correction:** See [12_fumes_handoff.md](12_fumes_handoff.md), especially “Geometry qualifications”. STEP zero is not a verified physical wing-root LE/CG datum; neutral is not independently certified; the convex lateral envelope is not a proven wetted-area upper bound; the original length gate remains failed. Values/solver substitutions below retain their distinct definitions and must not be promoted to validated inputs.

Source: `data/stork-geometry-bundle/` (197 files), produced by another agent on Lucas's Mac from the original Flightory STEP/STL files. It was reviewed and checked against the manual on 2026-10-17. Original vendor CAD is **not** in this repo; it stays on the Mac.

Start inside the bundle with `EXTRACTION_REPORT.md`, then `EXTRACTION_LIMITATIONS.md`, `GATE_REVIEW.md`, `assembly_notes.md`. Long-form values with units, status and evidence paths are in `geometry_table.csv` (1,017 rows; blank UNKNOWN ≠ zero).

## How the geometry was produced
- File inventory (`reference/cad-inventory-summary-2026-10-17.md`): Base pack 54 STL / 18 STEP; VTOL pack 16 STL / 14 STEP. All 32 STEP files are genuine B-rep (27 with B-spline surfaces), none faceted.
- STEP-only where available: VTOL WING 1.1/1.2, wingtip, ailerons, ruddervators, several fuselage sections. **STL-only**: WING 2, WING 3, all fixed V-tail panels, FUS 4.
- Slicer **modifier bodies** inside some STEP files (FUS 2/6, WING 1.1/1.2) were excluded.
- A **feature-registered assembly**: parts mated via pin patterns, spar axes, butt faces and mating planes, not by eye and not scaled to hit targets. 45 named components in a review GLB (not shipped).
- 108 source hashes verified unchanged.

## Validation against Flightory's manual
| Quantity | Extracted | Manual | Δ |
|---|---|---|---|
| Span | 1620.5 mm | 1620 mm | +0.03% |
| Wing area, gross (to centreline) | 31.25 dm² | 31 dm² | +0.8% |
| MAC | 195.7 mm | 195 mm | +0.4% |
| Root chord at centreline (linear fit) | 230.2 mm | 230 mm | +0.1% |
| Aspect ratio b²/S | 8.40 | 8.3 | +1.2% |
| Airfoil | S3021 is the closest UIUC match at every clean wing station (rms < 0.3% c) | S3021 | ✓ |
| Nose → pusher-mount face | 1000.0 mm | "Length 1000 mm" | ✓ |
| Nose → V-tail tip | 1044.0 mm | — | — |

**Length gate: FAILED (+4.402%) and preserved as failed.** Nose → pusher-mount face measures 1000.0 mm and nose → rearmost fixed tail 1044.02 mm. Lucas authorized continued extraction with these two distinct references; that authorization does not turn the gate into a pass, and the vendor's length convention is not independently proven. Tail placement came from mating features, not from fitting a target. Do not rescale anything.

## Coordinate frame
- Millimetres. **x aft, y right, z up.** Native mapping: aircraft (x,y,z) = native STEP (Z,X,Y).
- Origin = common STEP zero, **not a verified physical datum**. A linear fit of the clean wing stations extrapolates the LE to x = 0.00, z ≈ 0 at y = 0, but the physical wing root (y ≈ 92 mm) has its LE at x = 4.44 mm. Nose at x = −336.25 mm.
- The manual CG ("47 mm behind the leading edge at the wing root") therefore has two model readings: **case A x = 47.0 mm** (centreline-extrapolated LE; 13.7% MAC) and **case B x = 51.4 mm** (physical root LE; the retained prior model). Both are provisional model cases, not a weighed or safe CG (docs/DECISIONS.md D-06).

## Wing (per side)
From y = 0 to 730 mm chord and LE are linear to < 0.11 mm. **Twist is NOT linear:** it is piecewise-linear by printed panel (about −0.0020°/mm inboard and −0.0037°/mm on panel 2), with a real +0.13° step at the y = 318 mm joint. A single straight-line fit misses some stations by up to 0.17°. The table below is a qualified two-section simplification. Solver models should use the measured stations (`src/qxf7perf/geometry.py`, D-02). Incidence(0) is 2.49–2.52° depending on which stations are fitted; the measured incidence at y = 730 mm is 0.62°.

| Quantity | y = 0 (centreline, extrapolated) | y = 730 mm |
|---|---|---|
| Chord | 230.2 mm | 166.9 mm |
| LE x | 0.0 | 36.1 mm |
| LE z | 0 | 0 |
| Incidence (LE up vs body x), 2-point fit through inner_clean/outer_clean | 2.52° | 0.69° (measured 0.62°) |

- LE sweep 2.83°; main-panel dihedral 0°; washout ~1.6–1.9° (piecewise, see above).
- Upturned curved tip 730 → ~810 mm: at y 800, chord 119.6, LE x 84.1, z 18.7 (~15° effective dihedral over that panel); at y 809, chord 84.7, LE x 120.1, z 24.7. Sections beyond 730 mm are **oblique diagnostic cuts, not certified airfoils**.
- Profiles are S3021-like everywhere: t/c 9.73–9.82%, camber 2.91–2.95%, TE thickness ≈ 1.0 mm (printed).
- Ailerons in the saved pose are in line with the airfoil (shape deviation < 0.1% c). This is geometric alignment, **not certified aerodynamic or commanded neutral**.
- **Do not use** these truncated mechanical-clearance cuts as airfoils: `aileron_start_in`, `aileron_end_out`, `tip_root_in` (t/c ≈ 12.6–12.9% and odd incidences are artifacts).
- Per-station data: `wing-extraction/sections.csv`; profiles: `wing-extraction/dat/*.dat` (Selig format, 140 cosine-spaced points).
- Gross vs exposed areas: gross 31.245 dm² (MAC 195.74) includes a declared rectangular centreline carry-through; exposed 27.16 dm² (MAC 191.78). Use **gross** as Sref (matches manual).
- Area-weighted geometric quarter-chord: x = 69.0 mm (gross).

## V-tail (per panel)
- Cant (dihedral) **35.1°**; span-axis aft sweep 6.2°.
- Root LE at x = 492.1, y = ±44.0, z = +9.1 mm (root sits on the fuselage mount plane, not the centreline).
- **Local incidence −0.82°**, constant along span. The bundle also lists "incidence_aircraft_LE_up_deg = +2.88°". That is a different, legitimate definition: the x–z projection of a chord that is swept 6.2° inside the canted panel plane. It is not the surface's angle to the freestream. Explicit 3D check (2026-10-18): the surface normal built from the bundle chord and LE vectors has n_x = −0.0143, i.e. the surface is pitched −0.82° to +x. AeroSandbox `twist = −0.82°` about the dihedral span axis reproduces this. Use explicit 3D vectors and the solver's convention; do not substitute one number for the other (D-04).
- Section is symmetric, ~10.4% thick (closest UIUC: N12, NACA 0010); camber ≈ 0, so ruddervators in saved pose are aligned with the fixed tail.
- Panel-plane area 3.67 dm² per panel, **7.34 dm² total** (horizontal projection 6.01 dm²; first-order pitch-equivalent 7.34·cos²Γ ≈ 4.92 dm²). State the plane, and don't project again inside a 3D solver that already models the cant.

| Panel span s (mm, normal to root plane) | Chord (mm) | LE x offset from root LE (mm) | Note |
|---|---|---|---|
| 0.6 | 162.3 | 0 | root, merged fixed + ruddervator |
| 120 | 142.0 | 44.0 | |
| 220 | 124.9 | 80.9 | |
| 240 | 115.2 | 94.5 | fin starts (s ≈ 230) |
| 270 | 33.3 | 181.9 | fin tip, not a conventional airfoil |

- Tail arm: wing → tail area-weighted quarter-chord **505.5 mm in x** (gross), tail QC 77 mm above wing QC. Pitch-equivalent tail volume ≈ 0.41.
- Files: `tail-extraction/tail_geometry.json`, `profile_summary.csv`, `*_140cosineSelig.dat`.

## Fuselage
- 41 stations every 50 mm in `fuselage-with-hatches/cross_sections_50mm.csv` (columns: aircraft_x_mm, x_from_nose_mm, width_mm, height_mm, convex_envelope_perimeter_mm, convex_envelope_area_mm2, …). Hatches included.
- Rough shape: nose point at x −336; ~100×94 mm by x −250; ~130×130 mm at x −36; widest ~176 mm across the wing-root region (x 50–200, includes root fairings); tapering to ~90×85 mm by x 500; tail-mount region at x ~560 is taller (fin/tail mount); ~58×51 mm at x 650.
- Convex lateral envelope area ≈ **0.3825 m²** (hatch-inclusive, 419-station calculation in results.json). It is **neither exact wetted area nor a proven upper bound** (convexification does not bound a corrugated/concave skin). Hatchless baseline 0.365 m². A trapezoid over the shipped 50 mm table gives 0.364 m² and does not reproduce 0.3825 m²; this is unresolved pending the dense evidence (`data/historical/fumes-retained/fuselage-dense/`).
- Hardware silhouettes (isolated parts, not installed drag areas) in `hardware_dimensions.csv`: main skids (240 mm wide, 80 mm tall; frontal 1560 mm²), motor mounts, boom mounts, pusher mount 19×19.

## Unresolved (none blocks a first performance estimate)
- **Lift-motor / boom position along the tubes**: affects boom drag bookkeeping and CG location. Use the manual CG; model booms as 10×10 mm square tubes, 500 mm long, one per side, at the lift-arm mounts in the wing, with motors near the tube ends (verify against VTOL manual p.34–37).
- Exact exposed wetted area (convex envelope is fine to start).
- Rear FUS 4 hatch-tongue seating.
- Motors, props, electronics, fasteners not modelled.

## Flow5 / XFLR5 input summary (simplified; the scripted Phase A model uses measured stations)
- Wing: two-section simplification. y 0: chord 230.2, offset 0, twist 2.52°, S3021. y 730: chord 166.9, offset 36.1, twist 0.69°, S3021. Add a tip panel to ~y 800 projected (≈ 802.5 developed), chord 119.6, offset 84.1, dihedral ~15°, twist ~0.7°. Tilt 0 (twist carries incidence).
- V-tail: elevator object with 35.1° dihedral, twist −0.82° at all sections, root LE at x 492, z 9; sections from the table above (span measured along the panel). Starting the panels at the centreline instead of y = ±44 is an acceptable simplification (area and arm preserved); state it.
- Foils: S3021 (UIUC) for the wing; NACA 0010 for the tail.
- Point mass at AUW with **CG case A x = 47 mm** (and case B 51.4 mm as a sensitivity).
- First-pass fuselage: leave out of the panel model; add its drag (from OpenVSP or a build-up) as extra drag. Add it as a body later for stability.

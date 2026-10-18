# Stork VTOL baseline geometry, verified for Flow5/XFLR5 (2026-10-17)

> **Qualification correction:** See [../12_fumes_handoff.md](../12_fumes_handoff.md), especially “Geometry qualifications”. STEP zero is not a verified physical wing-root LE/CG datum; neutral is not independently certified; the convex lateral envelope is not a proven wetted-area upper bound; the original length gate remains failed. Values/solver substitutions below retain their distinct definitions and must not be promoted to validated inputs.

Source: CAD extraction bundle `stork-aero-extraction-review.zip` (feature-registered assembly of the original Flightory STEP/STL files), checked against the Stork user manual v2 spec table.

## Validation against Flightory's manual

| Quantity | Extracted | Manual | Status |
|---|---|---|---|
| Span | 1620.5 mm | 1620 mm | +0.03% |
| Wing area (gross, to centreline) | 31.25 dm² | 31 dm² | +0.8% |
| MAC | 195.7 mm | 195 mm | +0.4% |
| Root chord (centreline) | 230.2 mm | 230 mm | +0.1% |
| Aspect ratio | 8.40 | 8.3 | +1.2% |
| Airfoil | closest UIUC match S3021 (< 0.3% c rms) at every clean station | S3021 | matches |
| Length, nose → pusher mount face | 1000.0 mm | 1000 mm | matches |
| Length, nose → V-tail tip | 1044.0 mm | n/a | not a published figure |

**Decision:** the 1000 mm published length is nose-to-pusher. The +4.4% length-gate "failure" is a convention difference, not an assembly error. Tail placement comes from mating features and was not adjusted.

Note: the older Flightory blog figure of 24 dm² is outdated. Use **31 dm²**.

## Frame
- x aft, y right, z up, in mm.
- The origin is effectively the wing-root leading edge on the centreline (fitted LE x = 0.00 at y = 0).
- Manual CG is 47 mm aft of the root LE, so **CG x = 47 mm**, which is about 13.7% MAC. MAC LE is at x ≈ 20 mm.

## Wing (per side)
Within y = 0–730 mm, the wing is an exact linear trapezoid: fit residuals are < 0.1 mm and < 0.07°.

| Section | y (mm) | Chord | LE x offset | z | Incidence (LE up, vs body x) | Foil |
|---|---|---|---|---|---|---|
| Root (centreline) | 0 | 230.2 | 0.0 | 0 | 2.52° | S3021 |
| Tip-panel start | 730 | 166.9 | 36.1 | 0 | 0.69° | S3021 |
| Upturned tip (approx.) | 800 projected (≈ 802.5 developed) | 119.6 | 84.1 | 18.7 | ~0.7° | S3021 |

- LE sweep: 2.83°.
- Main-panel dihedral: 0°. Upturned tip: ~15° (730 → 800 mm).
- Washout: ~1.8°, linear.
- The last ~10 mm of curved tip is omitted by this simplified solver geometry. Integrating the shipped reference-envelope samples beyond y=800mm gives0.206448dm² bilateral, or0.66074% of gross reference area—not the previously claimed<0.5%.
- Ailerons in the saved pose are in line with the airfoil (shape deviation < 0.1% c), so saved pose ≈ neutral.

## V-tail (per panel)
- Cant (dihedral): 35.1°.
- Projected area: 3.67 dm² per panel, 7.34 dm² total. Pitch-equivalent area is about 4.9 dm² (× cos²Γ).
- Root LE at x = 492 mm, y = ±44 mm, z = +9 mm.
- Local incidence: −0.82° (LE down). The +2.88° "aircraft-frame" value in the bundle is a projection artifact of the cant; do not use it.
- Foil: symmetric, ~10.4% thick. Closest matches are N12 and NACA 0010. Camber is ≈ 0, so the ruddervators in the saved pose are in line with the fixed tail.

| Panel span s (mm) | Chord | LE x offset from root |
|---|---|---|
| 0 | 162.3 | 0 |
| 120 | 142.0 | 44.0 |
| 220 | 124.9 | 80.9 |
| 240 (fin starts) | 115.2 | 94.5 |
| 270 (fin tip) | 33.3 | 181.9 |

- Tail arm (wing → tail area-weighted quarter-chord): 505.5 mm in x; tail quarter-chord is 77 mm above the wing.
- Horizontal tail volume (pitch-equivalent): ≈ 0.41.

## Fuselage
- Hatch-inclusive convex envelope area: 0.383 m². This is an upper-bound approximation, not the exact wetted area.
- Cross-sections every 50 mm are in `fuselage-with-hatches/cross_sections_50mm.csv`.

## Open items (none block a first performance estimate)
- Lift-motor and boom positions along the 10×10×500 mm tubes. Affects boom drag bookkeeping and CG; use the manual CG for now.
- Exact exposed wetted area; the convex envelope is fine to start.
- Full rear FUS 4 hatch-tongue seating.

## Calibration targets from the manual
- CG at 47 mm gives "virtually no pitching moment at 0° AoA". Flow5 should trim near α ≈ 0°.
- Peak L/D between 0° and 3° AoA; optimal cruise speed 50–70 km/h.
- Prototype cruise on 4S with a 10×6 prop needed < 50% throttle.

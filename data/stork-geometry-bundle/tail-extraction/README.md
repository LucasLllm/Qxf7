# Executed original-source V-tail extraction

**Primary result:** `tail_geometry.json`; flat selected profiles in `profile_summary.csv`; dense station results in `spanwise_geometry.csv`. All geometry is in mm and degrees, not meters. Aircraft axes are **x aft = native Z, y right = native X, z up = native Y**, with the original common STEP datum retained. Left-side positions follow by changing aircraft y sign.

## Results for parent integration

- Physical root-plane-normal cant in the transverse y-z projection: **35.09268273° above horizontal**, or 54.90731727° from vertical. Its full 3D normal includes an aft component; inspect the explicit orthonormal section basis in JSON. These are physical mount-plane-normal sections, **not global-y cuts**.
- Right tail mounting-plane LE: **(492.085236, 43.971510, 9.071411) mm**. This uses observed fixed-skin nose points at s=.05 and .15 mm, with only .05 mm extrapolation to the root plane. Parent can compute wing–tail reference arms in the same datum.
- Full one-panel projected planform including genuine fin: **36,723.3311 mm²**. Projected geometric MAC **139.121105 mm**; chord-length-weighted 3D MAC **139.135485 mm**.
- Full-planform area-weighted 3D quarter-chord: **(574.548349, 138.414306, 76.650917) mm**. Equivalent mean-chord LE: **(539.969647, 141.761213, 78.391378) mm**. This is a geometric reference, **not an asserted aerodynamic center**.
- Fine integration: 292 stations including endpoints; alternate-point integration differs by **4.96144 mm² in area and −0.01651 mm in projected MAC**. This is discretization sensitivity, not an overall CAD uncertainty bound.
- Physical extreme at **s=272.254806 mm**; fin source first appears at **s=229.801191 mm**. The actual extreme degenerates: **no conventional tip airfoil, incidence, t/c or camber is asserted there**.

| Selected section | s mm | chord mm | local LE-up incidence ° | aircraft x-z LE-up pitch ° | max t/c | thickness x/c | signed max-absolute camber/c | camber x/c | TE normal thickness mm |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Near-root complete section | .61 | 162.288779 | -.823968 | 2.881248 | .10419205 | .29567546 | -.00026216 | .87660954 | .99999993 |
| Midspan | 120 | 141.960153 | -.823920 | 2.881286 | .10459379 | .30431317 | .00005592 | .00000987 | .99998569 |
| Outer regular, before fin | 220 | 124.912419 | -.821935 | 2.882916 | .10503848 | .30142605 | .00010213 | .92089677 | .99997390 |

The complete root profile is at **s=.61 mm**, .01 mm beyond the real rudder root at s=.6 mm. A complete fixed-plus-rudder contour does not physically exist exactly at the mounting plane. We do not silently extend the STEP control into this clearance. For nominal planform integration only, the first .61 mm strip uses the nearest complete chord and a span-translated quarter-chord. The actual root LE is separately reported above.

## Saved smooth-rudder pose versus true zero

Both genuine `RUDDER L.STEP` solids are imported, kept unrotated, and reflected across native X=0 for the right. **Source-pose rotation applied = 0°.**

At s=.61/120/220 mm, raw-envelope rudder midline minus fixed-skin midline slopes are **+.05146°, +.02101°, +.05428°**. Genuine **TE-cap midpoint** offsets from the extrapolated fixed midline are only **+.02280, +.02110, +.01736 mm**. Fixed midline fit RMS is .00108–.00157 mm; rudder fit RMS .000084–.01050 mm. The saved pose is therefore consistent with a nearly smooth, nearly symmetric continuation under this stated geometric diagnostic; it is not a certified aerodynamic/transmitter neutral.

**True zero relative to an agreed target remains UNKNOWN/null.** No numerical agreed neutral target contour, commanded angle, or linkage calibration was supplied. Hinge coaxiality and small fitted geometric residuals cannot establish that uniquely. No guessed correction was applied.

## Source geometry and section reconstruction

- Original fixed `V TAIL 1/2/3 R.STL` files are read-only. Panel 1 alone receives native translation (0, −3.703521516, 0) mm; panels 2/3 remain identity, as feature-resolved upstream.
- Both genuine smooth rudder solids are tessellated directly from original STEP with linear tolerance .008 mm and angular tolerance .05 rad. No rudder STL or illustrative GLB substitutes for these solids.
- Exact physical root plane is taken from the feature receipt for FUS6 VTOL physical solid 1 face 44; the original FUS6 STEP hash is checked too. Root plane normal is retained in all three dimensions.
- Keep all nonnested closed exterior loops per physical component, including genuinely disconnected control-skin fragments. Nested bores, cavities, and shell interiors are excluded. Saved `*_raw_section_loops.csv` retain selected raw loops in section and aircraft coordinates.
- Merge outer skins with straight upper/lower bridges nominally **hinge projected coordinate ±5 mm**. If a linkage/end-slot leaves disconnected exterior islands, extend to **1 mm past both gap lips**; actual limits and source gaps are saved per selected profile. For example s=240 mm closure is 623.859651–638.884958 mm, not an undocumented gap fill. This is an aerodynamic section closure, not a boolean solid or CFD-ready watertight boundary.
- 140-point Selig files have 70 upper cosine points TE→LE plus 71 lower points LE→TE before removing duplicate LE (140 total). The two cosine branches have different point counts; do not mistake them for 70+70 independent grids.
- Physical finite, slightly oblique TE caps are preserved: chord ends at the **cap midpoint**. TE endpoints are projected parallel to the chord onto x/c=1, preserving chord-normal thickness. Raw endpoint coordinates and cap lengths are retained in JSON.

### Important shared-helper issue found and locally corrected

`airfoil_tools.py` was copied byte-identically to `airfoil_tools_local.py` and its hash verified, but its normalization is **not used**: the maximum-aft-envelope method takes one corner of an oblique 1 mm TE cap as a sharp TE, returning zero TE thickness and a spurious approximately .5 mm midpoint bias. `normalize_tail.py` uses actual exterior TE-cap segments and midpoint instead. Regression checks explicitly preserve the genuine approximately 1 mm TE. The shared helper was **not modified**, so parallel agents should independently check finite-TE treatment.

## Profiles and fin caveat

- `root_140cosineSelig.dat`: actual near-root complete skin at s=.61 mm.
- `midspan_140cosineSelig.dat`: s=120 mm.
- `outer_regular_140cosineSelig.dat`: s=220 mm, suitable regular-section comparison outside root clearance and before fin.
- `fin_transition_140cosineSelig.dat`: actual s=240 mm geometry with documented gap closure; **not a conventional tip-airfoil claim**.
- `tip_fin_near_cap_140cosineSelig.dat`: actual s=270 mm fin contour; **not the degenerate extreme and not a replacement conventional foil**. Its geometric metrics are present but labeled nonconventional.
- Exact extreme conventional quantities are null in `true_tip`. No NACA, UIUC or other substitute foil was invented.

`section_diagnostics.png` overlays source exteriors and closure lines with normalized geometry; `planform_diagnostics.png` shows source planform, reconstructed chords, t/c and incidence, explicitly marking fin onset. `geometry_inspection.png` and `component_*.ply` are initial inspection artifacts (.015 mm rudder tessellation); production `extract_tail.py` always rebuilds from original sources at .008 mm.

## Reproduction and verification

From this directory:

```sh
/Users/lucasliu/.hermes/profiles/fumes/research-venv/bin/python -B extract_tail.py > extraction.log 2>&1
/Users/lucasliu/.hermes/profiles/fumes/research-venv/bin/python -B verify_deliverables.py
```

`source_hash_verification.json` checks five original CAD inputs before/after plus read-only references, own normalizer and executed production script. `tests.log` records executed regression/artifact tests. `verification.json` records final assertions and hashes of saved artifacts. Extraction authorization is respected; historical failed gate is not used to block current approved extraction. All writes remain inside this assigned directory.

Precision shown is reproducibility, not native-CAD exactness. Fixed geometry exists only as STL; section interpolation, closure width, root clearance and fin topology are explicit qualifications. No flightworthiness, stability derivative, aerodynamic center, control authority or wing–tail-arm result is asserted here.

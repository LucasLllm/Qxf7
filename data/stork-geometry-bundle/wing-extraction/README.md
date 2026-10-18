# Wing extraction — dense-stage repair and completion

## Reproduce

Use absolute paths (the shell's current directory may be shared with other agents):

```sh
/Users/lucasliu/.hermes/profiles/fumes/research-venv/bin/python -B /Users/lucasliu/.hermes/profiles/fumes/notes/stork-development/stork-aero-geometry/wing-extraction/test_resume_planform.py
/Users/lucasliu/.hermes/profiles/fumes/research-venv/bin/python -B /Users/lucasliu/.hermes/profiles/fumes/notes/stork-development/stork-aero-geometry/wing-extraction/resume_planform.py
/Users/lucasliu/.hermes/profiles/fumes/research-venv/bin/python -B /Users/lucasliu/.hermes/profiles/fumes/notes/stork-development/stork-aero-geometry/wing-extraction/verify_outputs.py
```

**Do not rerun `extract_wing.py` to resume.** Its original failure log and strict profile checks are deliberately preserved. The resume script AST-loads only its import and function-definition nodes, not the top-level neutral/profile/panel batches. All 27 existing DAT profiles, raw NPZs, plots, sections tables, neutral investigation, and panel rates are reused and SHA-256 checked for retention. CAD/source files and parent-owned geometry/report/UIUC exports are not written. Only this directory receives new outputs.

## Root cause and regression

At y=563.02 mm `right_aileron_1` genuinely has two separate exterior section loops plus an internal hole. The original largest-loop-only function asserted that every other loop was nested, treating a legitimate mechanical island as an error. That strict function remains unchanged for profile diagnostics. The new dense-planform path classifies nesting by full polygon containment and unions **all** nonnested exteriors. It never uses a convex hull or joins islands. The regression test verifies this real station succeeds, retains both exterior loops and extrema, and the original strict `groups()` still raises.

Sampled STEP closure spurs can yield zero-area self-intersections, including on the nested hole at the failing station. `make_valid` is permitted only with a relative area change below 1e-6; no geometry with a nontrivial change is silently accepted. Outer-extrema equality between the source loops and the union is asserted. STEP wires are sampled on their own curve parameters at at least 2,000 points / nominal 0.01 mm average sampling density; this avoids thousands of separate expensive arc-length inversions. This is **not** a guaranteed local step bound for nonuniform parameters. Comparison against the retained original arc-length sampler at y=92.02, 200, 317.98, 449.78, 563.02, 729.42 showed maximum x/z-extrema difference below 0.0001 mm. No original helper is patched.

## Deliverables and conventions

- `wing_geometry.json`: exposed and gross reference-envelope area, projected MAC, MAC LE and area-weighted quarter-chord coordinates; physical-envelope and physical occupied-projection comparisons; matched-grid convergence and omissions.
- `planform_samples.csv`: reference-envelope samples. At y<=318, uses the original untrimmed STEP BSpline design support. At y>318, uses measured physical union extrema. This hybrid reference is explicitly not a claim that all of its area is physical skin.
- `physical_planform_samples.csv`: physical exterior union extrema everywhere and width of its actual chordwise projected intervals. Chordwise gaps are excluded from occupied width, not silently reconstructed.
- `station_diagnostics.json`: retained station-versus-design comparisons and control-clearance warnings, plus every sampled station with multiple exterior loops.
- `verification.json`: original input hashes before/after, retained artifact hashes, freshly measured profile numeric/format checks, convergence status and output hashes. Numeric passing is not aerodynamic/neutral certification.
- `resume.log`: dense-stage execution; `dense_checkpoint.json`: samples keyed by script and original input hashes. Cache prevents losing a completed dense scan when resuming. It is not a substitute for source validation.
- `test_resume_planform.py`, `resume_planform.py`: regression and independent guarded dense-only runner.

All coordinates use the common untranslated source assembly datum: aircraft x=native Z aft, y=transformed native X right, z=native Y up. The right wing is mirrored for bilateral quantities; the left is not independently measured. Root nominal y=92 mm; center continuation is an **artificial rectangular continuation** of the first inboard reference section at y=92.0001 to y=0. No hidden-wing evidence or additional plate area is implied. Exposed integration excludes the center continuation. Gross and exposed areas are both bilateral.

For envelope chord c=xmax-xmin, A_half=integral(c dy), MAC=integral(c² dy)/A_half, x_qc=integral((xmin+c/4)c dy)/A_half, and MAC_LE=x_qc-MAC/4. Reported right-side y is the area centroid, not a unique station at which chord=MAC. Reported z_qc is a chord-extrema proxy, not a skin-area centroid. These are projected planform quantities, not 3D chord norms, wetted area, or lifting-surface aerodynamic-center calculations. A disjoint occupied projection does not receive an invented aerodynamic MAC.

Matched 3, 1.5 and 0.75 mm grids use the same endpoints and two-sided probes at component/control boundaries; they do not use a misleading `p[::2]` decimation with different endpoints. Last refinement acceptance: area change <0.01 dm²; MAC and quarter-chord aft change <0.1 mm. Tiny 0.0001-mm root/tip slivers are omitted; a conservative area bound is recorded. Spanwise quadrature convergence does not certify CAD discretization or physical aerodynamic validity.

## Completed results

Final matched-grid run: 984 stations at nominal 0.75 mm (plus boundary probes).

| Reference-envelope convention | Bilateral projected area (dm²) | Projected MAC (mm) | Quarter-chord aft (mm) |
|---|---:|---:|---:|
| Exposed | 27.159434 | 191.778346 | 70.386449 |
| Gross, declared rectangular center continuation | 31.245148 | 195.736690 | 69.035543 |

The physical-only envelope area is 27.126748 dm²; physical occupied-projection area is 27.120784 dm². Final 1.5→0.75 mm reference changes: 0.0054253 dm² area, 0.0245786 mm MAC, 0.0156547 mm quarter-chord aft. These pass the declared quadrature tolerances. All 27 retained profiles pass the fresh numeric/format checks; CAD input hashes and retained artifact hashes are unchanged.

The measured design-support chord at `aileron_start_in` is **191.190222 mm**, not 197 mm; retained 145.461231 mm is deficient by 45.728991 mm. The cleaner section 0.04 mm outboard (`aileron_start_out`) is 191.185619 mm. Other flagged cuts compare 129.980772 vs 166.972358 mm at y=729.42, and 129.949815 vs 166.923901 mm at y=729.98. The diagnostics separately identify absent aft domain beyond the physical TE extreme. An `unoccupied_x_gap_mm` of zero only means no hole *within* those shortened physical extrema; it is not evidence of aft skin being present.

## Additional CAD-kernel intersection failure

The denser scan exposed a second real source-processing problem: at y≈693.5 the exact STEP intersection of `right_aileron_2` drops its main skin curves, returning a hinge hole and an **open** ~1-mm TE segment. Neither blindly closing that segment nor accepting the remaining closed hole is legitimate. Movable STEP components are therefore independently cross-checked against their own physical-solid tessellation (0.0025-mm chordal tolerance, 0.05-radian angular tolerance). Open/incomplete exact intersections fall back only to a **watertight** tessellation of that same source physical solid, preserving closed physical loops and their union. This is not design-loft filling. The direct STEP intersection stays primary where complete. The original nonmovable inboard STEP uses exact closed section loops; its CAD triangulation is not globally watertight, so it is explicitly not used for this fallback.

Every dense fallback is listed in `station_diagnostics.json`, with exact-vs-mesh extrema discrepancy. Four independent movable-section checks at y=563.02, 650, 693.5001, and 700 compare 0.0025 and 0.00125 mm tessellations and require extrema change <0.01 mm. The regression test also checks the previously broken y=693.5001 section. All original strict profile helpers remain untouched.

## Critical retained-profile limitations

The legacy `sections.csv`/`sections.json` are retained **unchanged**, including their older generic `section_class` labels. Read the new station diagnostics before using them aerodynamically. Their `chord_mm` can be the normalized chord of a **truncated control-clearance contour**, not a local aerodynamic chord. The DAT may be numerically well formed even when its contour ends at a manufacturing cut. Their original skin recovery can replace inward cuts only within the x-domain of retained physical extrema and therefore cannot recover a missing aft domain at an aileron clearance. No missing skin is newly invented here.

Specifically inspect `aileron_start_in` (y=449.78, retained chord ~145.46 mm), `aileron_end_out` (y=729.42, ~129.98 mm), and `tip_root_in` (y=729.98, ~129.95 mm). Each is compared to the actual underlying source-support chord and the nearest cleaner retained section. The often-mentioned "~197 mm" design expectation at aileron start must be checked against the source, not inserted as a target. The script records measured support values and differences.

Near-tip sections (y>735) are oblique constant-aircraft-y diagnostics on a curved upturned tip, not certified normal airfoils. Neutral remains geometrically investigated but **not certified**; this repair does not adjust control pose. The original recovery methods, replacement fractions, raw physical loops, finite trailing-edge reprojection, and 140-point interpolation errors remain available in retained sections/NPZ/plots and verification.

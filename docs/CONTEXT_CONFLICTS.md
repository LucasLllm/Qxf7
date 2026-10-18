# Context discrepancies and decisions for Lucas

The import has NOT changed hardware.yaml, the geometry bundle or simulation source. Existing simulation prompts retain their historical case assumptions with a new superseding qualification banner; no mission configuration has been frozen. Corrected documentation is not an aircraft validation. Evidence and full qualifications: ../context/12_fumes_handoff.md.

## Decision status — latest Lucas clarification supersedes historical conflicts

| ID | Disagreement | Retained evidence / recommendation | Decision |
|---|---|---|---|
| D1 | Budget figures in historical contexts differ. | Lucas asks to omit budget for now and establish feasibility through performance checks; revisit cost afterward. No active monetary target/cap is imposed by this study. Historical source snapshots are retained, not operative constraints. | RESOLVED — budget deferred |
| D2 | Cruise target and simultaneous severe-cold mission scope. | Lucas confirms≥70km/h cruise target for modifiedQxF7. Interpret as engineering airspeed pending any explicit groundspeed requirement. Measure standard Stork performance without forcing its optimum to70km/h. This does not confirm simultaneous95km/750g/−30°C capability. | SPEED CONFIRMED; final weather envelope deferred, not a stock-study blocker |
| D3 | Separate lift ESCs versus one4-in-1. | Lucas confirms ONE4-in-1 for the standard-Stork performance baseline; retain the ledger’s18.5g mass reference. Separate ESCs for modifiedQxF7 are a possible future trade, not selected. Exact component qualification remains separate from baseline architecture choice. | RESOLVED for PhaseA; final-aircraft architecture undecided |
| D4 | Old mass studies say NET payload and include packaging/restraint allocations; current750g mission cargo is GROSS including packaging/insulation. | Preserve gross-cargo definition. Separate aircraft hold-downs from cargo-carried packaging and remove any double count before a loaded simulation. No unsupported gram allocation is chosen. | OPEN — item-level mass-accounting decision, not a reason to ask Lucas to retype known masses |

## Resolved by actual evidence / scope distinction (no repeat question needed)

| Finding | Action / interpretation |
|---|---|
| slicer_weights.csv was empty; context/09 listed masses as missing | Imported58released definitions /82installed pieces /965.642456g predicted model material. Copied all58 parent receipts and matched their release hashes. Not physical weights. |
| context/04 treated hardware as wholly unknown | Historical standard-size4S/216Wh reference exists; final scaled hardware is still unknown. Kept hardware.yaml unfrozen; added standard_stork_reference.json and copied original selection. |
| possible6S versus4S confusion in retained docs | 4S doc explicitly supersedes6S headline for stock unloaded-range study; it does not settle final scaled aircraft. Older6S report preserved as historical. |
| context/09 said whole-aircraft CG unknown | Correct. Printed-subset predicted centroids exist; different axes/origin, not a whole-aircraft CG or registered aero-frame CG. Imported separately, left CSV CG cells blank. |
| proposed100%grid and historicalapproval slicing_run=false versus completed slices | Later receipts supersede proposal-era flags. Approved grid99; keep regional modifiers; do not rescale ASA mass for foaming twice. |
| 7kg/2.4m from old design studies | Superseded anchors, not selected final dimensions/AUW. No scale frozen. PhaseA remains stock analytical reference, not a second airframe build. |
| 190km return versus current95km one way | Retained latest report edit removes190km as a design commitment.95km with endpoint swap does not demonstrate190km on one pack. Local report copy is historical snapshot; live Google Doc not re-audited. |
| whole-aircraft ledger versus arbitrary overhead factor | Imported installed-BOM/source reconciliation. Do not double-add factory wiring, optional equipment, carbon, or unused growth. Cold equipment is not included. |
| geometry synthesis treated STEP0 as physical LE, neutral pose as proven, convex envelope as wetted-area upper bound, length gate as reconciled pass | Documented corrections in context/12 and geometry-file warning banners. No raw geometry was changed. Provisional CG/airfoil/neutral cases are model assumptions. |
| performance-method D*V labeled shaft power | Corrected to useful thrust power; shaft power divides by prop efficiency. Avoid applying prop efficiency twice. |
| CFD/simulation context absent | Added retained CFD exterior status: cleaned but not qualified; no production volume mesh/CFD solve; hardware exterior incomplete. No tools installed or simulation run in this audit. |

## Independent geometry follow-up

Second review confirmed the tail4.9dm² pitch-equivalent-area estimate is legitimate first-order modeling, not an arithmetic error. Its panel-plane and horizontal areas must be distinguished. A definite tip-omission error was independently recomputed:0.66074% of gross reference area beyond y800mm, not<0.5%; corrected the reference. CG47mm remains a plausible provisional interpretation, not a uniquely registered manual datum. No additional user decision is needed for these documentation corrections.

## Verification and authority

Run `python3 scripts/verify_fumes_context.py` from the project root. It checks import hashes,58evidence hashes,CSV quantities/masses,empty CG cells,original protected files and unchanged geometry,relative entry-point links, and distinguishes modified documentation from original inputs. A passing import check validates transfer/integrity only, not simulation accuracy or flightworthiness. This is an IMPORT-TIME baseline check, not a permanent prohibition on Lucas-approved future changes: an intentional later hardware/input change will require a new documented audit baseline, not suppressing the failed check. The five regression tests in `tests/test_context_transfer.py` separately exercise valid import and tampered mass/quantity/CG/membership rejection.

`docs/fumes-context-before.json` records original project file hashes before the import. Source workspace files were read only. No git initialization, commit, upload, publication, purchase, supplier contact or physical operation occurred.

# Latest checked exterior: sealed-r4 — NOT production released

Lucas approved the recommended CFD default: bonded static seams sealed, intended cooling openings and control clearances retained. This is a modeling assumption, not an as-built observation.

The current **airframe-only** OBJ is `sealed-r4/Stork-airframe-exterior-m.obj`, in metres (+X forward, +Y left, +Z up). It is a tessellated derivative of the standard-size source aircraft, not native CAD and not the enlarged final aircraft.

- Exact-coordinate topology: zero boundary edges, nonmanifold edges, duplicate faces and zero-area triangles. Consistent winding. Independent reimport PASS.
- 1,202,012 triangles. 82 source airframe instances; old 45 illustrative hardware instances excluded.
- 132 original source-identity checks and seven corrected-pose coordinate checks PASS.
- Five declared bonded static interfaces use existing material cross-sections at +/-0.01 mm; sectional hole loops retained rather than bulkhead-filling the core passage. Other gaps are not globally filled.
- 34 exactly coincident opposite-winding faces cancelled. Numerical simplification requested at 0.0000001 mm. This is not a certified CAD-deviation bound.
- After cleanup, the final OBJ uses **one aerodynamic wall group**. Unique per-face source labels are not retained through the numerical cleanup; the grouped upstream assembly and earlier candidates remain available for provenance.
- Independent MeshLab final screen selects **621 faces**. Selected-face counts are not proven penetration counts. The final surface is **not intersection-qualified**. Global pair qualification is a separate ongoing evidence workstream.
- Complete installed exterior hardware, exact lift propellers and cruise rotor representation remain unresolved. This is not a whole-flight-configuration CFD boundary.
- No volume mesh, flow solve, flightworthiness claim, or physical test.

Five helper tests pass, including closed-cavity filtering, inaccessible material island filtering, disconnected surfaces, through-opening preservation, and both seam-sealing modes retaining an open core passage in a synthetic tube fixture. These do not prove all actual aircraft cooling/control openings correct.

Earlier candidates below failed release gates and are diagnostic only.

---
# Stork CFD exterior build — checked checkpoint

## Scope and release status
Lucas authorized building the production CFD exterior. The retained geometry currently represents the standard nominal 1.62 m Stork, not the enlarged final aircraft. Original sources and earlier derivatives are preserved.

**PRODUCTION RELEASE: BLOCKED.** A real exterior diagnostic OBJ has been exported, independently read back and independently self-intersection screened. It must not be used as a qualified whole-aircraft solver boundary.

## Executed work
- `assembly/exterior-classification.json`: corrected 127-instance assembly and derived OBJ components; roles, exact transforms and source hashes retained. Legacy illustrative hardware remains classified, not accepted as physical evidence.
- `VERIFICATION_assembly.json` and `VERIFICATION_r0.json`: independent checks passed for all 127 derived hashes, 132 original source-reference hashes and exact vertex-coordinate agreement for seven placement corrections.
- `r0/Stork-airframe-exterior-UNQUALIFIED-m.obj`: 82 source-backed native/STL airframe parts, excluding the 45 legacy illustrative hardware instances. Coordinates are metres, X forward, Y left, Z up; OBJ groups retain originating part names.
- `r0/RESULTS.json`, `UNION_DIAGNOSTICS.json`, `NONMANIFOLD_CONTACTS.json`, `INPUTS.json`: Boolean construction, signed-shell cavity exclusion and enclosed-island exclusion actually executed. The extraction retained 17 boundary shells, excluded 155 negative-volume cavity shells and two enclosed material islands. This classification does NOT itself establish a meshing-ready fluid domain.
- Four extraction regression tests pass, including sealed cavity exclusion, inaccessible material-island exclusion and preservation of a finite through-opening. Red/green tests were executed before the relevant implementation.
- `hardware/RESULTS.json`: original-datum motor occupancy envelopes, source-backed front-mount seating corrections and nominal tube wall surfaces. All 26 STEP/OBJ output hashes independently verified in `hardware/VERIFIED_EXPORT_HASHES.json`. These are not exact motor drag surfaces, closed tube solids or released rotor transforms. They have not been silently added to the primary exterior.

## Failed qualification gates — retained, not hidden
The R0 OBJ has 1,193,700 triangles. Independent coordinate-based readback reports:
- Boundary edges: 0.
- Zero-area triangles: 0.
- Nonmanifold edges: 367.
- Duplicate faces: 17.
- Winding consistency: pass.
- Independent MeshLab self-intersection selection: **639 selected faces**, with positive/negative control tests passing. Selected faces are not a count of distinct physical defects.

Affected nonmanifold source regions are recorded explicitly: FUS 1/2/3/5/6, wing 1.1/1.2 segments and rudder segments. A topologically closed Manifold3D result can still contain coordinate-coincident sheets and contacts unsuitable for the common CFD surface; library construction success is not the release gate.

An explicitly separated numerical-precision experiment (`r0_precision`, 0.0001 mm) did not remove the 367 nonmanifold edges or 17 duplicate faces and introduced zero-area faces/boundary edges. **That variant is rejected.** R0 used a 0.0000001 mm post-union simplification; both the pre-cleanup and post-cleanup topology are recorded. Neither is production released.

## Remaining physical-model definitions
- Static assembly seam and tube-end sealing policy; retain intended cooling/control openings unless a documented CFD idealization says otherwise.
- Exact installed lift-propeller SKU/pitch and blade geometry; stopped/braked/windmilling/active state and azimuth.
- APC 10x6E cruise blade geometry and propeller adapter/seat details, or a separately defined actuator model (not a solid disk pretending to be hardware).
- Qualified motor/boom exposed surfaces and native-envelope versus physical-print differences.
- Control neutral/trimmed pose, fastening seats and travel clearance. Current modeled control pose is retained, not independently declared neutral.
- Whole-surface nonmanifold/coincident-contact resolution, repeat self-intersection screen, domain/connectivity and meshing checks.

## Ongoing delegated work at checkpoint creation
`surface-qualification/` contains a bounded independent investigation of the eight flagged local meshes. Do not consume speculative intermediate replacements. Require a completed `RESULTS.json` plus independent verification before any rebuilt revision uses them.

## Reproduction
Use `/Users/lucasliu/.hermes/profiles/fumes/research-venv/bin/python` in this directory:

```
python test_exterior.py
python assembly/build_classification.py
python build_exterior.py r0
python verify_exterior.py r0
python screen_exterior.py r0
```

The generator exports failed geometry only under an `UNQUALIFIED` filename and preserves a failed status. A successful verifier execution means the artifact/provenance and reported failures were reproduced; it does not turn a failed geometry gate into a pass. Production geometry release is separate from CFD solution verification, physical tests and flightworthiness.

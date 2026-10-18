Inventory complete — source files unchanged
Inspected both original extracted packs and retained manuals:
Source	STL	STEP	PDFs
Base Stork	54	18	3
VTOL Pack	16	14	3
Total	70	32	6
The PDFs include four retained manual copies and two pack wiring diagrams. No .stp, .3mf, .obj, .igs or .iges files were found inside the two original pack directories. Generated CFD/assembly exports are excluded from these source-pack counts.
All 32 STEP files opened successfully and have valid B-rep topology:
27 contain actual B-spline surfaces.
5 use analytic surfaces, such as planes and cylinders.
None was identified as an STL-style faceted STEP.
Only the inventory CSV and report were created. Final verification passed 212 source/copy hash checks, with no changes detected.
A) Main findings by component
The attached report contains the complete grouped table and every-file details. This is the condensed aero-relevant summary:
Component	Part	STL?	STEP?	STEP quality	Outer skin?	Notes
Wing—inner	Base WING 1	L/R	Left design	Smooth B-rep	Yes	37 faces; one B-spline surface
Wing—inner	VTOL WING 1.1 / 1.2	L/R	Left designs	Smooth B-rep	Yes	Each STEP also contains a slicer modifier
Wing—inner/intermediate	WING 2	L/R	No	n.a.	Yes	STL-only
Wing—outer	WING 3	L/R	No	n.a.	Yes	STL-only
Wing—tip	WINGTIP 3	L/R	Nominal counterpart	Smooth B-rep	Yes	STEP/STL equivalence unresolved
Wing—aileron	Segments 1 / 2	L/R	Both segments in one left-design file	Smooth B-rep	Yes	Two genuine physical bodies
V-tail—fixed	V TAIL 1 / 2 / 3	L/R	No	n.a.	Yes	All fixed-tail panels STL-only
V-tail—ruddervator	Segments 1 / 2	L/R	Both segments in one left-design file	Smooth B-rep	Yes	Not the fixed-tail skin
Fuselage—nose	Standard / gimbal / clean alternatives	Standard + gimbal	All three	Smooth B-rep	Yes	NOSE CLEAN is STEP-only
Fuselage—base	FUS 1–6	Yes	3 and 6 only	Smooth B-rep where supplied	Yes	Base 1/2/4/5 lack STEP
Fuselage—VTOL	Modified 1/2/5/6; shared 3/4	Yes	1/2/3/5/6	Smooth B-rep	Yes	FUS 4 remains STL-only
VTOL mounts	Boom mounts 1/2; motor mounts 1/2	Yes	Yes	Smooth/analytic B-rep	Exposed hardware	Not the carbon boom tubes
Landing skid	MAIN SKIDS VTOL	Yes	Yes	Smooth B-rep	Yes	Available in both formats
Pusher motor mount	19×16 / 19×19	Yes	Yes	Smooth B-rep	Exposure depends on installation	Both alternatives present
Hatch/cover	Front/middle hatches; servo covers	Yes	Yes	Smooth/analytic B-rep	Yes	Vented STL variants need separate treatment
Internal structure	Roots, bay plates, battery pads, fasteners, locks	Yes	Mixed	See inventory	Mostly internal	Guide is an assembly jig, not installed structure
Important STEP-body selection warning
These are not files where every body represents aircraft material:
STEP file	Physical body¹	Other bodies
Base FUS6 MODIFIER	3	Slicer modifiers
VTOL FUS 2 MODIFIER	1	Slicer modifier
VTOL FUS 6 MODIFIER	1	Slicer modifiers
VTOL WING 1.1 MODIFIER	2	Slicer modifier
VTOL WING 1.2 MODIFIER	1	Slicer modifier
¹ One-based solid traversal indices for the inspected, hash-recorded files. Per-body bounds are included to verify selection.
B) Deliverables
The CSV includes 108 file records with absolute paths, native-axis bounding boxes in millimetres, units checks, side designation, component group, skin role, counterpart paths, STEP face/solid counts, surface types and internal-feature evidence.
MEDIA:/Users/lucasliu/.hermes/profiles/fumes/notes/stork-development/source-format-audit/cad_inventory.csv
The full report includes the grouped summary, all individual file details, STEP body tables, readiness assessment and manual references:
MEDIA:/Users/lucasliu/.hermes/profiles/fumes/notes/stork-development/source-format-audit/CAD_INVENTORY.md
C) Readiness for aero extraction
Wing: not full-span STEP-ready. Panels 2 and 3 must be measured from STL. The tip has smooth STEP, but its nominal STL pairing has an approximately 0.18 mm sampled p95 discrepancy, plus a left-label/native-coordinate ambiguity. It is not marked as an exact pair.
V-tail: fixed surfaces must be measured from STL. Smooth STEP exists for the movable ruddervator segments only.
Fuselage: partial STEP coverage. The VTOL configuration has substantially better coverage than the base pack, but FUS 4 still requires STL.
VTOL mounts and skids: both formats available. The actual carbon boom tubes have no original CAD file; the manual specifies nominal purchased tubes.
STEP availability does not mean a ready airfoil contour: bores, pockets, hinge details, modifier bodies and interior loops must be distinguished from the aerodynamic exterior.
D) Positioning evidence found
Useful manual references include:
Base pp.37–38: fuselage alignment-pin holes and assembly.
Base pp.47–49: wing/aileron/tip alignment using carbon tubes.
Base pp.52–54: fixed-tail and ruddervator assembly.
Base p.57: wings slide onto the fuselage’s main spar tubes.
VTOL p.31: WING 1.1 and 1.2 replace base WING 1.
VTOL pp.34–37: boom-positioning guide. Page 35 explicitly specifies 150 mm from a tube end to one side of the guide.
Existing project-derived assemblies and transformation manifests were also found and identified in the report. They include provisional and illustrative placements, so they are not treated as manufacturer assembly authority.
Wing incidence, exact installed V-tail angle and wing-to-tail reference distance remain unknown. No values were guessed.
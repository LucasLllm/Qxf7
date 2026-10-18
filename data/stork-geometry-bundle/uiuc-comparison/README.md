# UIUC shape comparisons

`uiuc_matches.csv` lists five closest profiles for each of 18 retained aerodynamic-section candidates, from 1661 accepted profiles in the official archived Selig-format corpus. `corpus_receipt.json` records source URLs, hash, four exclusions and the mathematical metric. Post-release UIUC updates are not included.

Ranking uses chord-normalized upper/lower ordinate RMS integrated uniformly over x/c; no thickness or camber fitting. Maximum ordinate error is also reported. These are **shape-only comparisons**, not manufacturer-airfoil identification, drag estimates or flightworthiness evidence.

All 32 extracted profiles remain available. Fourteen mechanical-clearance/plate cuts, oblique winglet diagnostics and nonconventional tail-fin contours are deliberately excluded from conventional-airfoil ranking; see `match_receipt.json`. Remaining joint cuts can still reflect real local manufacturing geometry. Do not infer spanwise aerodynamic changes without inspecting raw-section plots and gap-closure definitions.

`normalized_section_deviations.csv` compares normalized shapes within each component family. Placement, chord, incidence and twist are removed; local section planes are defined in the wing/tail reports.

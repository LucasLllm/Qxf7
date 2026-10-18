# Environment

Recorded 2026-10-18. Machine: Mac Mini, macOS 26.6.2, arm64.

## Python (project-local, `.venv/`, not committed)
- Created with `uv 0.11.19`: `uv venv --python 3.11 .venv` (CPython 3.11.15, uv-managed).
- Installed: `uv pip install numpy scipy pandas matplotlib aerosandbox neuralfoil pyyaml pytest`.
- Exact resolved set: `requirements.lock` (`uv pip freeze`). Key versions: aerosandbox 4.2.10, neuralfoil 0.3.3,
  casadi 3.8.1, numpy 2.4.6, scipy 1.17.1, pandas 3.0.6, matplotlib 3.11.2, pytest 9.1.1.
- Rebuild: `uv venv --python 3.11 .venv && uv pip install --python .venv/bin/python -r requirements.lock`.
- The Fumes `aero-venv` (same key versions) was used only as a compatibility reference; it was not modified.

## Smoke tests run before relying on the tools (2026-10-18)
| Check | Result | Reference |
|---|---|---|
| NeuralFoil NACA0012, Re 1e6, alpha 0 | Cd 0.00535 | ~0.0054 (published smooth-section data) |
| NeuralFoil S3021 (UIUC), Re 2e5, alpha 0/2/4 | CL 0.36/0.55/0.75, Cd 0.0093-0.0111, confidence >= 0.98 | plausibility only |
| AeroSandbox VLM rectangular AR 8, NACA0010, 5 deg | CL 0.409, CDi = CL^2/(pi AR) within 1.5 % | Helmbold CL ~0.43 |
| AeroSandbox VLM cambered S3021 AR 8, alpha 0 | CL 0.200 | thin-airfoil ~0.20 for 2.9 % camber |
| Own lifting line, elliptic wing | e = 1.000, CL_alpha within 0.1 % of 2 pi AR/(AR+2) | analytic |
| APC 10x6E parser | identical to prior processed table (max diff 6e-13) | reproduction, not independent |

## Known numerical limitation
AeroSandbox 4.2.10 VLM becomes singular for the raw V-tail fin-cap stations when the tail is rotated beyond
about -5 deg (lift jumps to hundreds of newtons). The project geometry replaces the fin cap with an
area/quarter-chord-preserving trapezoid (docs/DECISIONS.md D-03). Very fine meshes (12x16 and above) were not
used: one blew up on the earlier geometry and others exhausted memory/time. Production mesh (6,12); (4,8) is
reported as a sensitivity (lift within 1 %, induced drag within 3 %).

## Not installed (deferred per Lucas, 2026-10-18)
- XFoil, AVL: no Homebrew formula; would need gfortran (`brew install gcc`) and official sources. Add when a
  defined comparison needs them.
- OpenVSP: deferred until a specific geometry/drag task needs it.
- Flow5/XFLR5: not installed; scripted tools first.

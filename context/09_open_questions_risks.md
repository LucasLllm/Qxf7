# 09 Open questions, missing inputs and risks

> **Evidence update:** Read `12_fumes_handoff.md` and `../docs/CONTEXT_CONFLICTS.md` first.58released print masses/82pieces and historical4S/installed accounting are now present. Whole-aircraft CG and final scaled hardware remain unknown. Questions below predate that import; do not ask Lucas to re-enter available evidence.

## Inputs status (updated 2026-10-18)
1. Hardware reference (historical standard-size 4S): `data/hardware/standard_stork_reference.json`. Final scaled hardware is not chosen; `hardware.yaml` is intentionally unfrozen.
2. Slicer masses: populated (`data/hardware/slicer_weights.csv`; predicted, not weighed).
3. Pusher prop: APC 10×6E manufacturer-computed map imported (`data/historical/fumes-retained/prior-model/propulsion/data/`). Not measured.
4. **Still missing:** F90 1300KV + 7-inch performance at 4S (only T-Motor 6S bench data exist; T-Motor rates the motor 5–6S while the Stork manual says the lift system was primarily tested on 4S), the exact lift-prop SKU, whole-aircraft CG, measured component drag, and a qualified pack discharge model.
5. Installed boom/lift-motor position: approximate placement exists (`data/historical/fumes-retained/hardware-placement/`); not verified.

## Technical unknowns
- Real Stork VTOL Wh/km: Flightony's 2.0–2.5 is third-party and likely calculated; unlike-builder data suggest ~1.5–1.8 in clean cruise; the retained Fumes model gave 3.1. The Phase A diagnostic explains these component by component (`reports/`). Only flight measurement can settle it.
- Stopped lift-prop drag (10–35% of cruise power in builder data).
- Printed-surface roughness and seams (Ncrit, transition).
- Cold battery behaviour of the chosen cells; heating/insulation mass and power.
- The insulated payload box mass (350 g assumed; 500 g would push the payload toward 1 kg).
- Whether a 95 km leg closes at any reasonable mass in winter (earlier analysis: no at ~7 kg; fair weather yes).
- Hover power and thrust margin at the scaled mass.

## Programme risks (from the research)
- **Flightory license** forbids organizational/school/research and built-aircraft use. Needs a commercial license or a clean-sheet airframe before operating.
- **Cold (−30 °C)** is the biggest technical risk; icing likely a bigger practical limiter than dry cold; icing excluded from scope.
- **Funding / payer**: most programmes died when pilot money ran out (Moose Cree, CAELUS, Malawi, Nepal, Zipline Ghana). A health-system payer must be named early.
- **Regulation**: clinic-end landings near aerodromes need PVD/SFOC; UN3373 = dangerous goods; Level 1 Complex pilot must be 18+.
- **CORRIDAIR** holds Manawan; approach as collaborator only.
- **Reliability**: Aviant's Røros pilot cancelled 38 of 84 flights (wind, fog, 4G).

## Unverified facts (do not state as fact)
- Whether Manawan's Masko-Siwin sends samples to CHDL; where Wemotaci specimens go (presumably La Tuque → Trois-Rivières).
- Whether 750 g covers a "typical batch" (team assumption).
- 70 km/h cruise and 95 km range are design targets; an 80 km leg leaves ~16% margin and no headwind reserve.
- See `reference/qxf7-factcheck-2026-10-11.md` and the outreach plan's "Verify these before sending anything" for the full list.

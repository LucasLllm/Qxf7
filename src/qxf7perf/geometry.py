"""Standard Stork VTOL geometry for the solver, built from data/stork-geometry-bundle.

Frame: metres, x aft, y right, z up, origin = common STEP zero (NOT a verified physical datum).
Every simplification is declared in WING_STATION_RULES / TAIL_STATIONS_MM and in docs/DECISIONS.md.
"""
from dataclasses import dataclass, field
from pathlib import Path
import csv
import json

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
BUNDLE = ROOT / "data" / "stork-geometry-bundle"

# Wing stations used as solver cross-sections (right side, mirrored).
# Joint pairs (_in/_out, 0.04 mm apart) are averaged into one station: a real incidence step of up to
# 0.13 deg at y=318 mm (both sides consistent with neighbouring panel twist rates in panel_rates.json)
# is represented by its mean (+/-0.065 deg). Truncated mechanical cuts are never used.
WING_STATION_RULES = [
    ("wing_root",),
    ("inner_clean",),
    ("joint_1p1_in", "joint_1p1_out"),
    ("joint_1p2_in", "joint_1p2_out"),
    ("aileron_start_out",),          # aileron_start_in is a truncated clearance cut
    ("servo_pocket",),
    ("joint_2_in", "joint_2_out"),
    ("aileron_joint_in", "aileron_joint_out"),
    ("outer_clean",),
    ("aileron_end_in", "tip_root_out"),  # aileron_end_out / tip_root_in are truncated cuts
    ("curved_tip_750",),            # oblique diagnostic cut: planform/twist only, outer_clean foil used
    ("curved_tip_780",),
    ("near_tip_800",),
    ("near_tip_809",),
]
EXCLUDED_WING_SECTIONS = {"aileron_start_in", "aileron_end_out", "tip_root_in", "near_tip_810p25"}
INBOARD_FOIL, OUTBOARD_FOIL = "inner_clean", "outer_clean"
FOIL_SWITCH_Y_MM = 449.0  # inner_clean profile inboard of the aileron start, outer_clean outboard
TAIL_STATIONS_MM = [0.61, 58.8, 117.0, 173.3, 212.1, 229.8]
# The fin cap (s > 229.8 mm: chord 122 -> 0 mm while the LE runs ~130 mm aft) folds into degenerate
# VLM panels and makes the solve singular. It is replaced by ONE equivalent trapezoid tip at the
# s=270.3 mm LE y/z that preserves fin area (3912.75 mm^2/panel) and area-weighted quarter-chord x
# (627.62 mm). The fin's true shape/aerodynamics are not represented.
FIN_TIP_S_MM = 270.29
TAIL_STATIONS_RAW_MM = TAIL_STATIONS_MM + [245.1, 264.5, 270.3]  # prior-model-like raw fin (diagnostic)
FIN_AREA_MM2 = 3912.7535
FIN_QC_X_MM = 627.624
TAIL_FOIL_FILE = "root_140cosineSelig.dat"  # extracted symmetric section (closest UIUC: N12 / NACA0010)


@dataclass
class Section:
    y: float        # m (wing: aircraft y; tail: 3D LE position used)
    x_le: float
    z_le: float
    chord: float
    twist_deg: float
    foil: str       # path to Selig .dat
    source: str


@dataclass
class StorkGeometry:
    wing: list = field(default_factory=list)
    tail: list = field(default_factory=list)          # right panel, LE 3D points
    s_ref_gross: float = 0.0
    mac_gross: float = 0.0
    span: float = 0.0
    s_ref_exposed: float = 0.0
    mac_exposed: float = 0.0
    wing_qc_x_gross: float = 0.0
    tail_area_both_panels: float = 0.0
    nose_x: float = 0.0
    meta: dict = field(default_factory=dict)


def _rows(path):
    with open(path) as f:
        return list(csv.DictReader(f))


def _gt(component, station, quantity):
    for r in _rows(BUNDLE / "geometry_table.csv"):
        if r["component"] == component and r["station"] == station and r["quantity"] == quantity:
            return float(r["value"])
    raise KeyError((component, station, quantity))


def load(center_section: bool = True, tail_mode: str = "equivalent") -> StorkGeometry:
    """tail_mode="raw" reproduces the prior model's raw fin stations (numerically singular when the tail
    is rotated beyond about -5 deg; diagnostic use only). center_section=True adds a y=0 section copying wing_root (the bundle's declared gross
    convention: rectangular continuation of the first inboard section to the centreline)."""
    secs = {r["section_id"]: r for r in _rows(BUNDLE / "wing-extraction" / "sections.csv")}
    dat = BUNDLE / "wing-extraction" / "dat"
    g = StorkGeometry()
    for ids in WING_STATION_RULES:
        rs = [secs[i] for i in ids]
        avg = lambda k: sum(float(r[k]) for r in rs) / len(rs)
        y = avg("station_y_mm")
        foil = INBOARD_FOIL if y < FOIL_SWITCH_Y_MM else OUTBOARD_FOIL
        g.wing.append(Section(y / 1e3, avg("LE_aft_mm") / 1e3, avg("LE_up_mm") / 1e3, avg("chord_mm") / 1e3,
                              avg("incidence_LE_up_deg"), str(dat / f"{foil}.dat"), "+".join(ids)))
    if center_section:
        r0 = g.wing[0]
        g.wing.insert(0, Section(0.0, r0.x_le, r0.z_le, r0.chord, r0.twist_deg, r0.foil,
                                 "centreline continuation of wing_root (declared gross convention)"))
    tail_rows = _rows(BUNDLE / "tail-extraction" / "spanwise_geometry.csv")
    for s_target in (TAIL_STATIONS_MM if tail_mode == "equivalent" else TAIL_STATIONS_RAW_MM):
        r = min(tail_rows, key=lambda r: abs(float(r["span_station_from_root_plane_mm"]) - s_target))
        g.tail.append(Section(float(r["LE_y_mm"]) / 1e3, float(r["LE_x_mm"]) / 1e3, float(r["LE_z_mm"]) / 1e3,
                              float(r["chord_mm"]) / 1e3, float(r["incidence_LE_up_deg"]),
                              str(BUNDLE / "tail-extraction" / TAIL_FOIL_FILE),
                              f"s={float(r['span_station_from_root_plane_mm']):.2f}mm {r['region']}"))
    g.tail_area_both_panels = 7.344666e-2  # bundle panel-plane bilateral area (context/12)
    if tail_mode == "equivalent":
        g.tail.append(_equivalent_fin_tip(g.tail[-1], tail_rows))
        _scale_tail_to_area(g)
    gross, exposed = "gross_with_declared_centerline_continuation", "exposed"
    g.s_ref_gross = _gt("wing", gross, "both_sides_projected_area_dm2") / 100
    g.mac_gross = _gt("wing", gross, "projected_MAC_mm") / 1e3
    g.s_ref_exposed = _gt("wing", exposed, "both_sides_projected_area_dm2") / 100
    g.mac_exposed = _gt("wing", exposed, "projected_MAC_mm") / 1e3
    wg = json.loads((BUNDLE / "wing-extraction" / "wing_geometry.json").read_text())
    g.span = wg["span_mm"] / 1e3
    g.wing_qc_x_gross = wg[gross]["quarterchord_aft_mm"] / 1e3
    g.nose_x = json.loads((BUNDLE / "coordinate_frame.json").read_text())["nose_aircraft_x_mm"] / 1e3
    g.meta |= {"frame": "m, x aft, y right, z up, origin common STEP zero (not a physical datum)",
              "center_section": center_section,
              "wing_tip_last_station_y_mm": g.wing[-1].y * 1e3,
              "tail_note": "tail twist = bundle local incidence; equals the surface-normal pitch angle to +x "
                           "(n_x=-0.0143 -> -0.82 deg). Aircraft x-z projection +2.88 deg is NOT used."}
    return g


def tail_solver_area(sections) -> float:
    """Bilateral area as AeroSandbox meshes it: chord treated as streamwise, span = LE distance in y-z."""
    a = 0.0
    for s0, s1 in zip(sections[:-1], sections[1:]):
        a += 0.5 * (s0.chord + s1.chord) * np.hypot(s1.y - s0.y, s1.z_le - s0.z_le)
    return 2 * a


def _scale_tail_to_area(g):
    """Bundle chords are normal to a span axis skewed 6.2 deg in the panel plane, and the LE path in
    y-z is shorter than the span-axis distance, so the solver area is ~6% low. Scale all tail chords by
    one factor to the bundle panel-plane area, keeping each section's quarter-chord x fixed (declared)."""
    k = g.tail_area_both_panels / tail_solver_area(g.tail)
    for s in g.tail:
        s.x_le = s.x_le + 0.25 * s.chord * (1 - k)
        s.chord = s.chord * k
    g.meta["tail_chord_scale"] = k


def _equivalent_fin_tip(root: Section, tail_rows) -> Section:
    r = min(tail_rows, key=lambda r: abs(float(r["span_station_from_root_plane_mm"]) - FIN_TIP_S_MM))
    s0 = TAIL_STATIONS_MM[-1]
    h = FIN_TIP_S_MM - s0
    c0 = root.chord * 1e3
    ct = 2 * FIN_AREA_MM2 / h - c0
    # LE linear from x0 to x1 over h; area-weighted QC x is linear in x1 -> solve directly.
    s = np.linspace(0, h, 401)
    c = c0 + (ct - c0) * s / h
    w = c / np.trapezoid(c, s)
    base = np.trapezoid(w * (root.x_le * 1e3 + c / 4), s)      # with x1 = x0
    slope = np.trapezoid(w * s / h, s)                          # d(QC_x)/d(x1 - x0)
    x1 = root.x_le * 1e3 + (FIN_QC_X_MM - base) / slope
    return Section(float(r["LE_y_mm"]) / 1e3, x1 / 1e3, float(r["LE_z_mm"]) / 1e3, ct / 1e3, root.twist_deg,
                   root.foil, f"equivalent fin tip s={FIN_TIP_S_MM}mm (area+QC preserving, declared)")


# Declared CG cases (aero frame). The manual says 47 mm aft of the wing-root LE; which LE is unresolved.
CG_CASES_X = {
    "A_centreline_LE_plus_47": 0.047,          # fitted centreline LE x = 0.000 m
    "B_physical_root_LE_plus_47": 0.0514433,   # LE at physical wing root (y~92 mm) x = 4.44 mm; prior model
}

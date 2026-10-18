"""Hand-calculation and reproduction checks for the Phase A modules."""
import math

import numpy as np
import pandas as pd
import pytest

from qxf7perf import drag_buildup as B, geometry as G, hover as H, lifting_line as LL, mission as M
from qxf7perf.atmosphere import G0, air
from qxf7perf.propulsion import PropMap, DCMotor, cruise_battery_power, ROOT


def test_air_density_hand_values():
    assert air(15).rho == pytest.approx(101325 / (287.05 * 288.15), rel=1e-12)
    assert air(15).rho == pytest.approx(1.2250, abs=2e-4)
    assert air(-30).rho == pytest.approx(1.4517, abs=5e-4)          # context/06: ~1.45
    assert air(15).nu == pytest.approx(1.46e-5, rel=0.01)


def test_lifting_line_elliptic_and_rectangular():
    y = np.linspace(0, 1, 400)
    c = 0.25 * np.sqrt(np.clip(1 - y**2, 0, None))
    r = LL.wing_summary(y, c, 0 * y, 0 * y, np.full_like(y, 2 * np.pi), 2.0)
    AR = 4 / (np.pi / 4 * 2 * 0.25)
    assert r["e_at_4deg"] == pytest.approx(1.0, abs=1e-3)
    assert r["CL_alpha_per_rad"] == pytest.approx(2 * np.pi * AR / (AR + 2), rel=2e-3)
    y = np.linspace(0, 4, 200)
    r = LL.wing_summary(y, np.ones_like(y), 0 * y, 0 * y, np.full_like(y, 2 * np.pi), 8)
    assert 0.92 < r["e_at_4deg"] < 0.95                               # Glauert rectangular AR 8


def test_apc_parser_matches_prior_processed_table_and_point():
    p = PropMap()
    f = pd.read_csv(ROOT / "data/historical/fumes-retained/prior-model/propulsion/data/apc-forward.csv")
    for rpm in p.rpms:
        b, sub = p.blocks[rpm], f[f.rpm == rpm]
        assert np.allclose(np.interp(sub.airspeed_mps, b[:, 0], b[:, 1]), sub.thrust_N, atol=1e-9)
    op = p.operating_point(60 / 3.6, 4.0)
    assert op["rpm"] == pytest.approx(7678, abs=1) and op["shaft_W"] == pytest.approx(95.2, abs=0.1)
    assert p.operating_point(60 / 3.6, 1e3) is None                   # no extrapolation


def test_motor_model_energy_balance():
    el = DCMotor().electrical(8000, 120.0)
    I, Vm = el["I_A"], el["V_motor"]
    P0 = 1.17 * (10 - 0.072 * 1.17)
    assert Vm * I == pytest.approx(120 + P0 + 0.072 * I**2, rel=1e-9)


def test_prior_propulsion_chain_reproduced():
    pw = cruise_battery_power(15.0, 5.481958979510404, PropMap(), DCMotor())
    assert pw["P_batt_W"] == pytest.approx(168.277, abs=0.05)         # prior MISSION_SUMMARY smooth/aligned


def test_hover_momentum_hand_calc():
    r = H.hover_power(2.9837, 1.225, FM=1.0, eta_motor=1.0, eta_esc=1.0, aux_W=0.0)
    T = 2.9837 * G0
    A = 4 * math.pi * 0.0889**2
    assert r["P_ideal_induced_W"] == pytest.approx(T**1.5 / math.sqrt(2 * 1.225 * A), rel=1e-12)
    assert r["P_ideal_induced_W"] == pytest.approx(321, abs=1)


def test_accounting_deducts_each_item_once():
    acc = M.Accounting("t", usable_fraction=0.9, reserve_fraction=0.2, vtol_Wh=30.0)
    assert acc.cruise_Wh(216) == pytest.approx(216 * 0.9 - 43.2 - 30)  # = 121.2 Wh, prior model value
    assert M.range_km(168.2772647917544, 15.0, 121.2) == pytest.approx(38.89, abs=0.01)


def test_geometry_reference_and_tail_area():
    g = G.load()
    assert g.s_ref_gross == pytest.approx(0.31245148, rel=1e-6)
    assert G.tail_solver_area(g.tail) == pytest.approx(0.07344666, rel=1e-6)
    assert g.wing[0].y == 0.0 and g.wing[1].source == "wing_root"
    assert not any(G.EXCLUDED_WING_SECTIONS & set(s.source.split("+")) for s in g.wing)
    assert G.CG_CASES_X["B_physical_root_LE_plus_47"] - G.CG_CASES_X["A_centreline_LE_plus_47"] == pytest.approx(0.00444, abs=1e-5)


def test_equivalent_fin_preserves_area_and_quarter_chord():
    g = G.load()
    root, tip = g.tail[-2], g.tail[-1]
    k = g.meta["tail_chord_scale"]
    s = np.linspace(0, G.FIN_TIP_S_MM - G.TAIL_STATIONS_MM[-1], 401)
    c = (root.chord + (tip.chord - root.chord) * s / s[-1]) / k * 1e3
    x = (root.x_le + 0.25 * root.chord) * 1e3 - c / 4 + (tip.x_le + 0.25 * tip.chord - root.x_le - 0.25 * root.chord) * 1e3 * s / s[-1]
    assert np.trapezoid(c, s) == pytest.approx(G.FIN_AREA_MM2, rel=1e-3)
    assert np.trapezoid(c * (x + c / 4), s) / np.trapezoid(c, s) == pytest.approx(G.FIN_QC_X_MM, abs=0.5)


def test_raymer_form_factor_and_friction():
    assert B.cf_turbulent(1e6) == pytest.approx(0.455 / 6**2.58, rel=1e-12)
    f = 1.0 / 0.1445
    assert 1 + 60 / f**3 + f / 400 == pytest.approx(1.199, abs=1e-3)

"""Phase A diagnostic baseline for the standard Stork VTOL (unloaded, mild air, still air).

Produces runs/<date>_phaseA_diagnostic/: ladder.csv, sweep.csv, sensitivities.csv, stability.csv,
hand_check.csv, hover.csv, missions.csv, summary.json and plots. Never overwrites an existing run dir.
Run: .venv/bin/python scripts/run_phaseA_diagnostic.py
"""
import json
import sys
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import aerosandbox as asb

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from qxf7perf import aero as A, drag_buildup as B, geometry as G, hover as H, lifting_line as LL  # noqa: E402
from qxf7perf import mission as M, propulsion as P  # noqa: E402
from qxf7perf.atmosphere import G0, air  # noqa: E402

OUT = ROOT / "runs" / f"{date.today().isoformat()}_phaseA_diagnostic"
AIR = air(15.0, 101325.0)
MESH = (6, 12)
CG_A, CG_B = G.CG_CASES_X["A_centreline_LE_plus_47"], G.CG_CASES_X["B_physical_root_LE_plus_47"]
MASSES = {  # kg, provenance
    "flightony_explorer_2.7": (2.7, "third-party published AUW (payload inclusion unresolved)"),
    "flightony_operator_2.9": (2.9, "third-party published AUW (payload inclusion unresolved)"),
    "all_bambu_central_2.984": (2.9837, "model ledger: dry central 2056.7 g + 927 g pack target, no cargo"),
    "all_bambu_growth_3.084": (3.0837, "model ledger + 100 g UNUSED growth (planning stress case)"),
}
NOMINAL_WH = 216.0
PROP, MOTOR = P.PropMap(), P.DCMotor()
K_FUS = {"low": 0.0055, "central": 0.011, "high": 0.0165}  # Raymer fig. 16.14 read at ~40% body length, +/-50%


def fuselage_dM_per_deg(q, case="central"):
    """Munk-type destabilising fuselage moment slope (N m / deg), Raymer eq. 16.25 form."""
    W_f, L_f = 0.15, 1.0  # representative width (m, 130-176 mm range) and length (m)
    g = G.load()
    return K_FUS[case] * W_f**2 * L_f / (g.mac_gross * g.s_ref_gross) * q * g.s_ref_gross * g.mac_gross


def drag_total(e, V, case="central", props="aligned"):
    par = B.buildup(V, AIR.nu, AIR.rho, case, props)
    return e["Di_N"] + e["Dp_wing_N"] + e["Dp_tail_N"] + par["D_total_N"], par


def power(V, D, motor=MOTOR, **kw):
    return P.cruise_battery_power(V, D, PROP, motor, **kw)


def trim_row(g, V, m, cg, opts, guess):
    e = A.trim(g, AIR, V, m, cg, opts, guess=guess, extra_M_per_alpha=fuselage_dM_per_deg(0.5 * AIR.rho * V**2))
    return e


def ladder():
    """Prior-model reproduction -> fresh baseline, one change at a time, 54 km/h, 2.9837 kg."""
    V, m = 54 / 3.6, 2.9837
    prior = pd.read_csv(ROOT / "data/historical/fumes-retained/prior-model/ASSEMBLED_AERO.csv")
    pr = prior[(prior.speed_kmh == 54) & (prior.surface == "smooth") & (prior.prop_orientation == "aligned")].iloc[0]
    rows = [{"step": "0 prior model as reported", "alpha": pr.alpha_deg, "tail_delta": pr.equivalent_tail_incidence_adjust_deg,
             "Di": pr.induced_N, "Dp": pr.profile_N, "parasite": pr.parasite_N, "D": pr.drag_N}]
    P0 = dict(center_section=False, s_ref="exposed", mesh=(2, 3), section_moment="neuralfoil")
    steps = [
        ("1 reproduce prior choices (raw fin, no centre, (2,3), NF Cm, CG 51.4)", G.load(False, "raw"), A.AeroOptions(**P0), CG_B, (9.4, -11)),
        ("2 + equivalent fin, tail area restored", G.load(False), A.AeroOptions(**P0), CG_B, (5, -3)),
        ("3 + centreline wing continuation", G.load(True), A.AeroOptions(**{**P0, "center_section": True}), CG_B, (5, -3)),
        ("4 + mesh (6,12), gross Sref", G.load(True), A.AeroOptions(mesh=MESH, section_moment="neuralfoil"), CG_B, (5, -3)),
        ("5 + VLM camber moment", G.load(True), A.AeroOptions(mesh=MESH), CG_B, (5, -3)),
        ("6 + CG A (47 mm, centreline LE datum)", G.load(True), A.AeroOptions(mesh=MESH), CG_A, (5, -3)),
    ]
    for name, g, o, cg, guess in steps:
        e = A.trim(g, AIR, V, m, cg, o, guess=guess)
        rows.append({"step": name, "alpha": e["alpha_deg"], "tail_delta": e["tail_delta_deg"], "Di": e["Di_N"],
                     "Dp": e["Dp_wing_N"] + e["Dp_tail_N"], "parasite": pr.parasite_N, "converged": e["trim_converged"]})
    last = rows[-1]
    par = B.buildup(V, AIR.nu, AIR.rho, "central", "aligned")
    rows.append({**last, "step": "7 + fresh component build-up (central, aligned props)", "parasite": par["D_total_N"]})
    acc = M.CONVENTIONS[2]
    for r in rows:
        r["D"] = r["Di"] + r["Dp"] + r["parasite"]
        pw = power(V, r["D"])
        r["P_batt_W"] = pw["P_batt_W"]
        r["Wh_per_km"] = M.wh_per_km(pw["P_batt_W"], V)
        r["range_km_prior_accounting"] = M.range_km(pw["P_batt_W"], V, acc.cruise_Wh(NOMINAL_WH))
        r["range_km_all_216Wh"] = M.range_km(pw["P_batt_W"], V, NOMINAL_WH)
    return pd.DataFrame(rows), par, pr


def sweep():
    g = G.load(True)
    o = A.AeroOptions(mesh=MESH)
    rows = []
    for key, (m, prov) in MASSES.items():
        guess = (8.0, -6.0)
        for kmh in range(45, 85, 5):
            V = kmh / 3.6
            e = trim_row(g, V, m, CG_A, o, guess)
            guess = (e["alpha_deg"], e["tail_delta_deg"])
            base = {"mass_case": key, "mass_kg": m, "mass_provenance": prov, "speed_kmh": kmh,
                    "alpha_deg": e["alpha_deg"], "tail_delta_deg": e["tail_delta_deg"], "CL": e["CL"],
                    "Di_N": e["Di_N"], "Dp_wing_N": e["Dp_wing_N"], "Dp_tail_N": e["Dp_tail_N"],
                    "L_tail_N": e["L_tail_N"], "trim_converged": e["trim_converged"],
                    "nf_min_conf": e["nf_min_conf"], "clipped_area_frac": e["clipped_area_frac"]}
            for case in B.CASES:
                for props in ("aligned", "crossflow"):
                    D, par = drag_total(e, V, case, props)
                    pw = power(V, D)
                    rows.append({**base, "parasite_case": case, "props": props, "parasite_N": par["D_total_N"],
                                 "D_N": D, "L_over_D": m * G0 / D,
                                 "P_batt_W": pw["P_batt_W"] if pw else np.nan,
                                 "shaft_W": pw["shaft_W"] if pw else np.nan, "eta_prop": pw["eta_prop"] if pw else np.nan,
                                 "eta_motor": pw["eta_motor"] if pw else np.nan, "duty_at_14.4V": pw["duty_at_bus"] if pw else np.nan,
                                 "Wh_per_km": M.wh_per_km(pw["P_batt_W"], V) if pw else np.nan})
            print(key, kmh, round(e["alpha_deg"], 2), flush=True)
    return pd.DataFrame(rows)


def sensitivities():
    """One-at-a-time deviations from the central case at 60 km/h, 2.9837 kg, CG A, aligned props."""
    V, m = 60 / 3.6, 2.9837
    g = G.load(True)
    base_o = A.AeroOptions(mesh=MESH)
    rows = []

    def add(name, e=None, D=None, pw=None):
        e = e or ref_e
        D = D if D is not None else drag_total(e, V)[0]
        pw = pw or power(V, D)
        rows.append({"case": name, "alpha_deg": e["alpha_deg"], "tail_delta_deg": e["tail_delta_deg"], "D_N": D,
                     "P_batt_W": pw["P_batt_W"], "Wh_per_km": M.wh_per_km(pw["P_batt_W"], V)})

    ref_e = trim_row(g, V, m, CG_A, base_o, (5, -5))
    add("central")
    add("CG B 51.4 mm", trim_row(g, V, m, CG_B, base_o, (5, -5)))
    add("mesh (4,8)", trim_row(g, V, m, CG_A, A.AeroOptions(mesh=(4, 8)), (5, -5)))
    add("NeuralFoil section Cm", trim_row(g, V, m, CG_A, A.AeroOptions(mesh=MESH, section_moment="neuralfoil"), (5, -5)))
    add("Ncrit 5 (rougher free stream/surface)", trim_row(g, V, m, CG_A, A.AeroOptions(mesh=MESH, n_crit=5), (5, -5)))
    add("forced transition 5% chord", trim_row(g, V, m, CG_A, A.AeroOptions(mesh=MESH, xtr=0.05), (5, -5)))
    add("no fuselage moment correction", A.trim(g, AIR, V, m, CG_A, base_o, guess=(5, -5)))
    for c in ("low", "high"):
        add(f"parasite {c}", D=drag_total(ref_e, V, c)[0])
    add("props crossflow (central parasite)", D=drag_total(ref_e, V, "central", "crossflow")[0])
    D0 = drag_total(ref_e, V)[0]
    for k in (0.5, 2.0):
        add(f"motor R x{k}", pw=power(V, D0, motor=P.DCMotor(R=0.072 * k)))
    add("motor I0 reference 14 V", pw=power(V, D0, motor=P.DCMotor(I0_ref_V=14.0)))
    for eta in (0.95, 0.99):
        add(f"ESC efficiency {eta}", pw=power(V, D0, eta_esc=eta))
    for aux in (10.0, 20.0):
        add(f"aux load {aux:.0f} W", pw=power(V, D0, aux_W=aux))
    df = pd.DataFrame(rows)
    df["dP_pct"] = 100 * (df.P_batt_W / df.P_batt_W.iloc[0] - 1)
    return df


def stability():
    g = G.load(True)
    rows = []
    V = 60 / 3.6
    q = 0.5 * AIR.rho * V**2
    for cgname, cg in (("A 47.0", CG_A), ("B 51.4", CG_B)):
        for fus in ("none", "low", "central", "high"):
            x = 0.0 if fus == "none" else fuselage_dM_per_deg(q, fus)
            r = A.neutral_point(g, AIR, V, cg, A.AeroOptions(mesh=MESH), alpha=4.0, tail_delta=-5.0, extra_M_per_alpha=x)
            rows.append({"cg": cgname, "fuselage_moment": fus, "x_np_mm": 1e3 * r["x_np"],
                         "static_margin_pct_mac": 100 * r["static_margin_frac_mac"], "CL_alpha_per_rad": r["CL_alpha_per_rad"]})
    return pd.DataFrame(rows)


def hand_check(sweep_df):
    """Second method: lifting-line span efficiency + NeuralFoil section drag at MAC + same parasite build-up."""
    g = G.load(True)
    y = np.array([s.y for s in g.wing if s.y <= 0.7297])  # planar part; tip panel folded into area via S_ref
    c = np.array([s.chord for s in g.wing if s.y <= 0.7297])
    tw = np.array([s.twist_deg for s in g.wing if s.y <= 0.7297])
    y = np.append(y, g.span / 2)
    c = np.append(c, 0.12)
    tw = np.append(tw, 0.9)
    rows = []
    for kmh in (54, 60, 70):
        V = kmh / 3.6
        Re = V * g.mac_gross / AIR.nu
        af = asb.Airfoil(coordinates=g.wing[2].foil)
        al = np.linspace(-2, 4, 13)
        d = af.get_aero_from_neuralfoil(alpha=al, Re=Re, model_size="large")
        a0 = np.polyfit(np.radians(al), d["CL"], 1)
        alpha0 = -np.degrees(a0[1] / a0[0])
        ll = LL.wing_summary(y, c, tw, np.full_like(y, alpha0), np.full_like(y, a0[0]), g.span)
        for mkey in ("all_bambu_central_2.984", "flightony_operator_2.9"):
            m = MASSES[mkey][0]
            q = 0.5 * AIR.rho * V**2
            CL = m * G0 / (q * g.s_ref_gross)
            AR = g.span**2 / g.s_ref_gross
            Di = q * g.s_ref_gross * CL**2 / (np.pi * AR * ll["e_at_4deg"])
            cd_w = float(np.interp(CL, np.ravel(d["CL"]), np.ravel(d["CD"])))
            Dp_w = q * g.s_ref_gross * cd_w
            tail_cd = float(np.ravel(asb.Airfoil(coordinates=g.tail[0].foil).get_aero_from_neuralfoil(
                alpha=0, Re=V * 0.14 / AIR.nu, model_size="large")["CD"])[0])
            Dp_t = q * g.tail_area_both_panels * tail_cd
            par = B.buildup(V, AIR.nu, AIR.rho)["D_total_N"]
            D = Di + Dp_w + Dp_t + par
            s = sweep_df[(sweep_df.mass_case == mkey) & (sweep_df.speed_kmh == kmh) & (sweep_df.parasite_case == "central")
                         & (sweep_df.props == "aligned")]
            vlm_D = float(s.D_N.iloc[0]) if len(s) else np.nan
            rows.append({"speed_kmh": kmh, "mass_case": mkey, "CL": CL, "e_LLT": ll["e_at_4deg"],
                         "CLalpha_LLT": ll["CL_alpha_per_rad"], "Di_hand_N": Di, "Dp_wing_hand_N": Dp_w,
                         "Dp_tail_hand_N": Dp_t, "parasite_N": par, "D_hand_N": D, "D_vlm_N": vlm_D,
                         "diff_pct": 100 * (D / vlm_D - 1)})
    return pd.DataFrame(rows)


def hover_table():
    rows = []
    for key, (m, _) in MASSES.items():
        for FM in (0.55, 0.65, 0.75):
            r = H.hover_power(m, AIR.rho, FM=FM)
            rows.append({"mass_case": key, "method": f"momentum FM={FM}", **r})
        per = m * 1000 / 4
        rows.append({"mass_case": key, "method": "T-Motor 6S bench HQ7040x3 (motor input, proxy)",
                     "P_batt_W": 4 * H.bench_interpolation_6S(per, H.F90_HQ7040x3_6S)})
        rows.append({"mass_case": key, "method": "T-Motor 6S bench GF7042 (motor input, proxy)",
                     "P_batt_W": 4 * H.bench_interpolation_6S(per, H.F90_GF7042_6S)})
    df = pd.DataFrame(rows)
    for t in (60, 120, 180):
        df[f"Wh_per_{t}s"] = df.P_batt_W * t / 3600
    return df


def missions(sweep_df):
    rows = []
    c = sweep_df[(sweep_df.parasite_case == "central") & (sweep_df.props == "aligned")]
    for mkey, grp in c.groupby("mass_case"):
        grp = grp.dropna(subset=["Wh_per_km"])
        best = grp.loc[grp.Wh_per_km.idxmin()]
        minp = grp.loc[grp.P_batt_W.idxmin()]
        for kmh in (54, int(best.speed_kmh), 60, 70):
            r = grp[grp.speed_kmh == kmh]
            if r.empty:
                continue
            r = r.iloc[0]
            for acc in M.CONVENTIONS:
                rows.append({"mass_case": mkey, "speed_kmh": kmh, "best_range_speed_kmh": best.speed_kmh,
                             "min_power_speed_kmh": minp.speed_kmh, "P_batt_W": r.P_batt_W, "Wh_per_km": r.Wh_per_km,
                             "accounting": acc.name, "cruise_Wh": acc.cruise_Wh(NOMINAL_WH),
                             "range_km": M.range_km(r.P_batt_W, kmh / 3.6, acc.cruise_Wh(NOMINAL_WH))})
    return pd.DataFrame(rows)


def plots(sweep_df, lad):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    colors = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
    plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "font.size": 9})
    fig, ax = plt.subplots(figsize=(7, 4.2))
    c = sweep_df[(sweep_df.props == "aligned")]
    for col, (mkey, grp) in zip(colors, c.groupby("mass_case", sort=False)):
        mid = grp[grp.parasite_case == "central"]
        lo = grp[grp.parasite_case == "low"].P_batt_W.values
        hi = grp[grp.parasite_case == "high"].P_batt_W.values
        ax.plot(mid.speed_kmh, mid.P_batt_W, color=col, lw=2, label=f"{mkey} kg")
        ax.fill_between(mid.speed_kmh, lo, hi, color=col, alpha=0.10, lw=0)
    ax.axhspan(80, 110, color="#888888", alpha=0.12, lw=0)
    ax.text(46, 112, "Flightony claim 80-110 W (third-party)", fontsize=8, color="#52514e")
    ax.set_xlabel("Airspeed (km/h)")
    ax.set_ylabel("Battery power, cruise (W)")
    ax.set_title("Standard Stork: modelled cruise battery power (aligned stopped props)\n"
                 "line = central parasite; band = low-high parasite assumptions (not a confidence interval)", fontsize=9)
    ax.grid(alpha=0.25, lw=0.5)
    ax.legend(frameon=False, fontsize=8)
    fig.tight_layout()
    fig.savefig(OUT / "power_required.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 3.6))
    show = lad.iloc[[0, len(lad) - 1]]
    comps = [("Di", "induced"), ("Dp", "wing+tail profile"), ("parasite", "parasite build-up")]
    left = np.zeros(len(show))
    for col, (k, lab) in zip(colors, comps):
        ax.barh(["prior model (reported)", "fresh baseline"], show[k].values, left=left, color=col, label=lab,
                edgecolor="white", linewidth=2)
        left += show[k].values
    for i, v in enumerate(left):
        ax.text(v + 0.05, i, f"{v:.2f} N", va="center", fontsize=8)
    ax.set_xlabel("Drag at 54 km/h, 2.984 kg (N)")
    ax.legend(frameon=False, fontsize=8, ncol=3, loc="lower right", bbox_to_anchor=(1, 1.02))
    ax.grid(axis="x", alpha=0.25, lw=0.5)
    fig.tight_layout()
    fig.savefig(OUT / "drag_prior_vs_fresh.png", dpi=150)
    plt.close(fig)


def main():
    if OUT.exists():
        sys.exit(f"{OUT} exists; runs are never overwritten")
    OUT.mkdir(parents=True)
    lad, par54, prior_row = ladder()
    lad.to_csv(OUT / "ladder.csv", index=False)
    print(lad.round(3).to_string(), flush=True)
    sw = sweep()
    sw.to_csv(OUT / "sweep.csv", index=False)
    sens = sensitivities()
    sens.to_csv(OUT / "sensitivities.csv", index=False)
    stab = stability()
    stab.to_csv(OUT / "stability.csv", index=False)
    hc = hand_check(sw)
    hc.to_csv(OUT / "hand_check.csv", index=False)
    hv = hover_table()
    hv.to_csv(OUT / "hover.csv", index=False)
    ms = missions(sw)
    ms.to_csv(OUT / "missions.csv", index=False)
    pd.DataFrame(par54["items"]).to_csv(OUT / "parasite_items_54kmh.csv", index=False)
    plots(sw, lad)
    g = G.load(True)
    summary = {"air": AIR.__dict__, "mesh": MESH, "cg_cases_m": G.CG_CASES_X, "geometry_meta": g.meta,
               "nominal_Wh": NOMINAL_WH, "masses": MASSES, "accounting": [a.__dict__ for a in M.CONVENTIONS],
               "propulsion": {"prop": "APC 10x6E manufacturer-computed map", "motor": MOTOR.__dict__,
                              "eta_esc": 0.97, "aux_W": 15.0, "thrust_line": "along flight path (assumption)"}}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1, default=str))
    for name, df in (("SENSITIVITIES", sens), ("STABILITY", stab), ("HAND CHECK", hc), ("MISSIONS", ms)):
        print(f"\n{name}\n", df.round(3).to_string(), flush=True)


if __name__ == "__main__":
    main()

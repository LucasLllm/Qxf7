"""Wing + V-tail aerodynamics: AeroSandbox VLM (inviscid lift, induced drag, moments) plus
NeuralFoil strip profile drag at the VLM local lift coefficient. Fuselage/hardware drag is NOT
here (see drag_buildup.py); fuselage pitching moment is a separate analytical correction.

Switches exist so the retained prior model's choices can be reproduced one at a time
(exposed reference area, no centre section, CG datum, coarse mesh, NeuralFoil section moments).
"""
from dataclasses import dataclass
import copy

import numpy as np
import aerosandbox as asb
from scipy.optimize import root

from .atmosphere import Air, G0


@dataclass
class AeroOptions:
    center_section: bool = True     # gross convention; prior model: False
    s_ref: str = "gross"            # "gross" | "exposed" (prior model: exposed)
    mesh: tuple = (4, 8)            # (spanwise per section pair, chordwise); prior model: (2, 3)
    n_crit: float = 9.0
    xtr: float = 1.0                # forced transition x/c (1.0 = free)
    section_moment: str = "vlm"     # "vlm" (camber line in VLM) | "neuralfoil" (prior model)


def build_airplane(g, cg_x, opts: AeroOptions, tail_delta_deg=0.0):
    wing = asb.Wing(name="wing", symmetric=True, xsecs=[
        asb.WingXSec(xyz_le=[s.x_le, s.y, s.z_le], chord=s.chord, twist=s.twist_deg,
                     airfoil=_foil(s.foil)) for s in g.wing if opts.center_section or s.y > 0])
    tail = asb.Wing(name="vtail", symmetric=True, xsecs=[
        asb.WingXSec(xyz_le=[s.x_le, s.y, s.z_le], chord=s.chord, twist=s.twist_deg + tail_delta_deg,
                     airfoil=_foil(s.foil)) for s in g.tail])
    s_ref = g.s_ref_gross if opts.s_ref == "gross" else g.s_ref_exposed
    c_ref = g.mac_gross if opts.s_ref == "gross" else g.mac_exposed
    return asb.Airplane(name="Stork VTOL wing+V-tail", xyz_ref=[cg_x, 0, 0], wings=[wing, tail],
                        s_ref=s_ref, c_ref=c_ref, b_ref=g.span)


_FOILS = {}


def _foil(path):
    if path not in _FOILS:
        _FOILS[path] = asb.Airfoil(name=path.rsplit("/", 1)[-1], coordinates=path)
    return _FOILS[path]


class StripPolars:
    """NeuralFoil polars for every VLM spanwise strip (foil, Re fixed per speed)."""

    ALPHA = np.linspace(-10, 14, 97)

    def __init__(self, airplane, air: Air, V, opts: AeroOptions):
        ns, nc = opts.mesh
        self.tables, self.family = [], []
        for w in airplane.wings:
            ws = w.subdivide_sections(ratio=ns)
            strips = list(zip(ws.xsecs[:-1], ws.xsecs[1:]))
            if w.symmetric:  # VLM meshes the mirrored side as well; same polars
                strips = strips + strips
            for a, b in strips:
                c = 0.5 * (a.chord + b.chord)
                af = a.airfoil if a.airfoil is b.airfoil else a.airfoil.blend_with_another_airfoil(b.airfoil, 0.5)
                d = af.get_aero_from_neuralfoil(alpha=self.ALPHA, Re=V * c / air.nu, model_size="large",
                                                n_crit=opts.n_crit, xtr_upper=opts.xtr, xtr_lower=opts.xtr)
                cl = np.asarray(d["CL"]).ravel()
                i0 = int(np.argmin(abs(self.ALPHA - 2)))
                lo = hi = i0  # monotonic pre-stall branch around alpha ~ 2 deg
                while lo > 0 and cl[lo - 1] < cl[lo]:
                    lo -= 1
                while hi < len(cl) - 1 and cl[hi + 1] > cl[hi]:
                    hi += 1
                sl = slice(lo, hi + 1)
                self.tables.append({k: np.asarray(d[k]).ravel()[sl] for k in ("CL", "CD", "CM", "analysis_confidence")})
                self.family.append(w.name)
        self.family = np.array(self.family)

    def lookup(self, cls):
        out = {"CD": [], "CM": [], "conf": [], "clipped": []}
        for cl, t in zip(cls, self.tables):
            out["clipped"].append(bool(cl < t["CL"][0] or cl > t["CL"][-1]))
            out["CD"].append(np.interp(cl, t["CL"], t["CD"]))
            out["CM"].append(np.interp(cl, t["CL"], t["CM"]))
            out["conf"].append(np.interp(cl, t["CL"], t["analysis_confidence"]))
        return {k: np.array(v) for k, v in out.items()}


_POLAR_CACHE = {}


def polars_for(g, air: Air, V, opts: AeroOptions):
    """StripPolars depend on geometry layout, speed, viscosity and transition settings only."""
    key = (len(g.wing), len(g.tail), round(g.tail[-1].chord, 6), round(V, 6), round(air.nu, 12),
           opts.n_crit, opts.xtr, opts.center_section, opts.mesh)
    if key not in _POLAR_CACHE:
        _POLAR_CACHE[key] = StripPolars(build_airplane(g, 0.0, opts), air, V, opts)
    return _POLAR_CACHE[key]


def evaluate(g, air: Air, V, alpha, cg_x, opts: AeroOptions, tail_delta_deg=0.0, polars=None):
    """One VLM + strip-profile evaluation. Forces in N, moments about (cg_x, 0, 0)."""
    plane = build_airplane(g, cg_x, opts, tail_delta_deg)
    ns, nc = opts.mesh
    vlm = asb.VortexLatticeMethod(plane, asb.OperatingPoint(atmosphere=None, velocity=V, alpha=alpha),
                                  spanwise_resolution=ns, chordwise_resolution=nc)
    # AeroSandbox uses its own ISA atmosphere unless overridden; impose our density explicitly.
    vlm.op_point = asb.OperatingPoint(atmosphere=_Atmo(air), velocity=V, alpha=alpha)
    r = vlm.run()
    q = 0.5 * air.rho * V**2
    polars = polars or polars_for(g, air, V, opts)
    F = vlm.forces_geometry.reshape(-1, nc, 3)
    area = vlm.areas.reshape(-1, nc).sum(axis=1)
    n = vlm.normal_directions.reshape(-1, nc, 3).mean(axis=1)
    n /= np.linalg.norm(n, axis=1)[:, None]
    cl_strip = (F.sum(axis=1) * n).sum(axis=1) / (q * area)
    lk = polars.lookup(cl_strip)
    flow = np.asarray(vlm.steady_freestream_direction).ravel()
    le = (0.5 * (vlm.front_left_vertices + vlm.front_right_vertices)).reshape(-1, nc, 3)[:, 0, :]
    te = (0.5 * (vlm.back_left_vertices + vlm.back_right_vertices)).reshape(-1, nc, 3)[:, -1, :]
    qc = 0.75 * le + 0.25 * te
    chord = np.linalg.norm(te - le, axis=1)
    D_prof_strip = q * area * lk["CD"]
    m_prof = float(np.cross(qc - [cg_x, 0, 0], D_prof_strip[:, None] * flow[None, :]).sum(axis=0)[1])
    M = float(r["m_b"])
    if opts.section_moment == "neuralfoil":
        span_dir = vlm.vortex_bound_leg.reshape(-1, nc, 3).sum(axis=1)
        span_dir /= np.linalg.norm(span_dir, axis=1)[:, None]
        m_local = np.cross(vlm.vortex_centers.reshape(-1, nc, 3) - qc[:, None, :], F).sum(axis=(0, 1))[1]
        M = M - float(m_local) + float(np.sum(q * area * chord * lk["CM"] * span_dir[:, 1]))
    is_tail = polars.family == "vtail"
    return {
        "alpha_deg": alpha, "tail_delta_deg": tail_delta_deg, "L_N": float(r["L"]),
        "Di_N": float(r["D"]), "Dp_wing_N": float(D_prof_strip[~is_tail].sum()),
        "Dp_tail_N": float(D_prof_strip[is_tail].sum()), "M_Nm": M + m_prof,
        "CL": float(r["L"]) / (q * plane.s_ref), "q_Pa": q, "s_ref": plane.s_ref, "c_ref": plane.c_ref,
        "L_tail_N": float(F[is_tail][..., 2].sum()),
        "nf_min_conf": float(lk["conf"].min()),
        "clipped_area_frac": float(area[lk["clipped"]].sum() / area.sum()),
        "cl_strip_max_wing": float(cl_strip[~is_tail].max()),
    }


class _Atmo(asb.Atmosphere):
    """Pin AeroSandbox's atmosphere to our density/viscosity."""

    def __init__(self, air: Air):
        super().__init__(altitude=0.0)
        self._air = air

    def density(self):
        return self._air.rho

    def dynamic_viscosity(self):
        return self._air.mu

    def temperature(self):
        return self._air.T_C + 273.15

    def pressure(self):
        return self._air.p_Pa


def trim(g, air, V, mass_kg, cg_x, opts: AeroOptions, guess=(2.0, 0.0), extra_M_per_alpha=0.0):
    """Solve alpha and equivalent tail-incidence change for L = W and M_cg = 0.
    extra_M_per_alpha: analytical fuselage moment slope (N m / deg) added to the VLM moment.
    The tail change is an EQUIVALENT whole-surface incidence, not a verified ruddervator mapping."""
    W = mass_kg * G0
    polars = polars_for(g, air, V, opts)
    cache = {}

    def f(x):
        e = evaluate(g, air, V, x[0], cg_x, opts, x[1], polars)
        cache["e"] = e
        M = e["M_Nm"] + extra_M_per_alpha * x[0]
        return [(e["L_N"] - W) / W, M / (W * e["c_ref"])]

    sol = root(f, np.array(guess), tol=1e-8)
    e = cache["e"] if np.allclose([cache["e"]["alpha_deg"], cache["e"]["tail_delta_deg"]], sol.x) else \
        evaluate(g, air, V, sol.x[0], cg_x, opts, sol.x[1], polars)
    e.update({"trim_converged": bool(sol.success), "W_N": W, "V": V, "mass_kg": mass_kg, "cg_x": cg_x})
    return e


def neutral_point(g, air, V, cg_x, opts: AeroOptions, alpha=2.0, tail_delta=0.0, extra_M_per_alpha=0.0):
    """Stick-fixed NP from dCm/dCL by central difference (+/-0.5 deg)."""
    polars = polars_for(g, air, V, opts)
    e1 = evaluate(g, air, V, alpha - 0.5, cg_x, opts, tail_delta, polars)
    e2 = evaluate(g, air, V, alpha + 0.5, cg_x, opts, tail_delta, polars)
    dM = (e2["M_Nm"] - e1["M_Nm"]) + extra_M_per_alpha * 1.0
    dL = e2["L_N"] - e1["L_N"]
    x_np = cg_x - dM / dL  # moment about cg = (x_np - cg) * L sign: nose-up positive, x aft
    return {"x_np": x_np, "CL_alpha_per_rad": (e2["CL"] - e1["CL"]) / np.radians(1.0),
            "static_margin_frac_mac": (x_np - cg_x) / e1["c_ref"]}

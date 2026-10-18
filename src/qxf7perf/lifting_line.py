"""Independent check: classical Prandtl lifting line (Glauert Fourier series, planar, unswept).

Inputs are the projected planform chord c(y), geometric twist i(y) and section zero-lift angle /
lift slope. Gives wing-alone CL_alpha, zero-lift angle and span efficiency e = CL^2/(pi AR CDi).
Ignores sweep, dihedral, tail and fuselage: it checks the VLM wing, not the whole aircraft.
"""
import numpy as np


def solve(y_half, chord, twist_deg, alpha0_deg, a0_per_rad, span, alpha_deg, n=60):
    """Return CL, CDi, e, and the Fourier coefficients for wing angle alpha_deg (body axis)."""
    b = span
    theta = np.linspace(0, np.pi, n + 2)[1:-1]         # collocation (exclude tips)
    yy = -0.5 * b * np.cos(theta)
    ya = np.abs(yy)
    c = np.interp(ya, y_half, chord)
    tw = np.radians(np.interp(ya, y_half, twist_deg))
    a0z = np.radians(np.interp(ya, y_half, alpha0_deg))
    a0 = np.interp(ya, y_half, a0_per_rad)
    k = np.arange(1, n + 1)
    M = (4 * b / (a0[:, None] * c[:, None])) * np.sin(np.outer(theta, k)) \
        + k[None, :] * np.sin(np.outer(theta, k)) / np.sin(theta)[:, None]
    rhs = np.radians(alpha_deg) + tw - a0z
    A = np.linalg.solve(M, rhs)
    S = 2 * np.trapezoid(chord, y_half)
    AR = b**2 / S
    CL = np.pi * AR * A[0]
    delta = np.sum(k[1:] * (A[1:] / A[0]) ** 2) if A[0] != 0 else 0.0
    CDi = np.pi * AR * np.sum(k * A**2)
    return {"CL": CL, "CDi": CDi, "e": 1 / (1 + delta), "AR": AR, "S": S}


def wing_summary(y_half, chord, twist_deg, alpha0_deg, a0_per_rad, span):
    r1 = solve(y_half, chord, twist_deg, alpha0_deg, a0_per_rad, span, 0.0)
    r2 = solve(y_half, chord, twist_deg, alpha0_deg, a0_per_rad, span, 4.0)
    CLa = (r2["CL"] - r1["CL"]) / np.radians(4.0)
    return {"CL_alpha_per_rad": CLa, "alpha_zero_lift_deg": -np.degrees(r1["CL"] / CLa),
            "e_at_4deg": r2["e"], "AR": r2["AR"], "S": r2["S"]}

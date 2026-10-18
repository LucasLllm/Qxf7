"""Conditional hover screening by momentum theory. NOT evidence the selected F90/7-inch/4S system can
hover the aircraft: available thrust, current, thermal limits and control margin need separate data
(only 6S manufacturer bench data exist; T-Motor rates the F90 1300KV for 5-6S, the Stork manual says
the lift system was primarily tested on 4S)."""
import numpy as np

from .atmosphere import G0


def hover_power(mass_kg, rho, n_rotors=4, diameter_m=0.1778, FM=0.65, eta_motor=0.80, eta_esc=0.95,
                aux_W=15.0, thrust_factor=1.0):
    """Three distinct levels, all for steady out-of-ground-effect hover.
    thrust_factor > 1 allows for interference/download on the wing below the rotors (assumption)."""
    T = mass_kg * G0 * thrust_factor
    A = n_rotors * np.pi * (diameter_m / 2) ** 2
    P_ideal = T**1.5 / np.sqrt(2 * rho * A)
    P_shaft = P_ideal / FM
    P_batt = P_shaft / (eta_motor * eta_esc) + aux_W
    return {"thrust_N": T, "disk_area_m2": A, "disk_loading_N_m2": T / A,
            "P_ideal_induced_W": P_ideal, "P_shaft_W": P_shaft, "P_batt_W": P_batt,
            "FM": FM, "eta_motor": eta_motor, "eta_esc": eta_esc}


def bench_interpolation_6S(thrust_per_motor_g, table):
    """Electrical input power per motor interpolated from T-Motor 6S bench rows [(g, W), ...].
    6S data applied at another voltage is a screening proxy only."""
    g = np.array([r[0] for r in table])
    W = np.array([r[1] for r in table])
    return float(np.interp(thrust_per_motor_g, g, W))


# T-Motor F90 1300KV manufacturer bench, ~24 V (6S), HQ 7040x3 (via retained lift-research/findings.md)
F90_HQ7040x3_6S = [(0, 0.0), (353, 52.0), (948, 213.0), (1586, 493.0), (2361, 1059.0)]
F90_GF7042_6S = [(0, 0.0), (836, 174.0), (2117, 971.0)]

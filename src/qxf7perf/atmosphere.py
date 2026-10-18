"""Dry-air properties at a given temperature and pressure (ideal gas + Sutherland viscosity)."""
from dataclasses import dataclass

R_AIR = 287.05  # J/(kg K)
G0 = 9.80665    # m/s^2


@dataclass(frozen=True)
class Air:
    T_C: float
    p_Pa: float
    rho: float   # kg/m^3
    mu: float    # Pa s
    nu: float    # m^2/s


def air(T_C: float = 15.0, p_Pa: float = 101325.0) -> Air:
    T = T_C + 273.15
    rho = p_Pa / (R_AIR * T)
    mu = 1.458e-6 * T**1.5 / (T + 110.4)  # Sutherland
    return Air(T_C, p_Pa, rho, mu, mu / rho)

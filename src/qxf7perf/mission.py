"""Mission energy accounting with explicit, non-overlapping deductions.

Aerodynamic demand (battery power at an airspeed) and mission-budget penalties are kept separate so a
disagreement can be attributed to one or the other. Each convention names exactly which deductions it
applies; none is applied twice.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Accounting:
    name: str
    usable_fraction: float      # of nominal energy (DoD / cutoff); applied once
    reserve_fraction: float     # of nominal energy, held back; applied once
    vtol_Wh: float              # departure + transitions + arrival, deducted once
    aging_factor: float = 1.0   # capacity retention; 1.0 = new pack
    note: str = ""

    def cruise_Wh(self, nominal_Wh):
        return nominal_Wh * self.usable_fraction * self.aging_factor - nominal_Wh * self.reserve_fraction - self.vtol_Wh


CONVENTIONS = [
    Accounting("all_nominal_to_cruise", 1.0, 0.0, 0.0, note="upper reference only; not achievable"),
    Accounting("flightony_like", 0.9, 0.0, 0.0,
               note="Flightony: 90% of nominal ('10% reserve') / Wh/km with VTOL folded into Wh/km"),
    Accounting("prior_fumes", 0.9, 0.2, 30.0,
               note="prior model: 90% usable, 20% nominal reserve, 30 Wh VTOL (all assumptions)"),
]


def range_km(P_batt_W, V_mps, cruise_Wh, wind_mps=0.0):
    """Still-air (or steady headwind<0 / tailwind>0) straight-leg distance on cruise_Wh."""
    if cruise_Wh <= 0 or V_mps + wind_mps <= 0:
        return 0.0
    hours = cruise_Wh / P_batt_W
    return hours * (V_mps + wind_mps) * 3.6


def wh_per_km(P_batt_W, V_mps):
    return P_batt_W / (V_mps * 3.6)

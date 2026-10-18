"""Cruise propulsion: APC 10x6E map (MANUFACTURER-COMPUTED vortex-theory data, not measured) and an
UNCALIBRATED equivalent-DC motor model for the BrotherHobby Avenger 2812 V5 910KV (catalog constants).

Map: data/historical/fumes-retained/prior-model/propulsion/data/PER3_10x6E.DOM.dat
(APC v2022-0915, simulation date 2022-09-22). No extrapolation outside the map.
"""
from dataclasses import dataclass
from pathlib import Path
import re

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
APC_10X6E = ROOT / "data/historical/fumes-retained/prior-model/propulsion/data/PER3_10x6E.DOM.dat"
MPH = 0.44704


def read_apc(path=APC_10X6E):
    """Return {rpm: array[[V_mps, thrust_N, shaft_W, torque_Nm], ...]} from a PER3 file."""
    blocks, rpm = {}, None
    for line in Path(path).read_text(errors="ignore").splitlines():
        m = re.search(r"PROP RPM\s*=\s*(\d+)", line)
        if m:
            rpm = int(m.group(1))
            blocks[rpm] = []
            continue
        parts = line.split()
        if rpm is None or len(parts) < 11:
            continue
        try:
            vals = [float(p) for p in parts[:11]]
        except ValueError:
            continue
        # cols: V(mph) J Pe Ct Cp PWR(hp) Q(in-lbf) T(lbf) PWR(W) Q(N-m) T(N)
        blocks[rpm].append([vals[0] * MPH, vals[10], vals[8], vals[9]])
    return {k: np.array(v) for k, v in blocks.items() if v}


class PropMap:
    def __init__(self, path=APC_10X6E):
        self.blocks = read_apc(path)
        self.rpms = np.array(sorted(self.blocks))

    def at(self, V):
        """Thrust and shaft power vs RPM at airspeed V (rows where V is inside each block's range)."""
        out = []
        for r in self.rpms:
            b = self.blocks[r]
            if b[0, 0] <= V <= b[-1, 0]:
                out.append((r, np.interp(V, b[:, 0], b[:, 1]), np.interp(V, b[:, 0], b[:, 2])))
        return np.array(out)

    def operating_point(self, V, thrust_N):
        """RPM and shaft power for required thrust at V; None if outside the map (no extrapolation)."""
        t = self.at(V)
        ok = t[:, 1] > 0
        t = t[ok]
        if len(t) < 2 or not (t[0, 1] <= thrust_N <= t[-1, 1]):
            return None
        rpm = float(np.interp(thrust_N, t[:, 1], t[:, 0]))
        P = float(np.interp(thrust_N, t[:, 1], t[:, 2]))
        return {"rpm": rpm, "shaft_W": P, "eta_prop": thrust_N * V / P}


@dataclass
class DCMotor:
    """Catalog constants (vendor): Kv 910 rpm/V, R 0.072 ohm, I0 1.17 A. Conventions unresolved:
    R may be phase-phase or per-phase (sensitivity 0.5x/2x); I0 reference voltage given as 10 V and 14 V."""
    kv: float = 910.0
    R: float = 0.072
    I0: float = 1.17
    I0_ref_V: float = 10.0

    def electrical(self, rpm, shaft_W):
        w = rpm * 2 * np.pi / 60
        kt = 60 / (2 * np.pi * self.kv)
        E = rpm / self.kv
        P0 = self.I0 * (self.I0_ref_V - self.R * self.I0)       # constant no-load loss hypothesis
        I = (shaft_W + P0) / E
        Vm = E + I * self.R
        return {"I_A": I, "V_motor": Vm, "P_elec_W": Vm * I, "eta_motor": shaft_W / (Vm * I),
                "torque_Nm": shaft_W / w, "kt": kt}


def cruise_battery_power(V, drag_N, prop: PropMap, motor: DCMotor, eta_esc=0.97, aux_W=15.0, V_bus=14.4):
    """Battery power to fly at V with thrust = drag (thrust line assumed along flight path)."""
    op = prop.operating_point(V, drag_N)
    if op is None:
        return None
    el = motor.electrical(op["rpm"], op["shaft_W"])
    P_batt = el["P_elec_W"] / eta_esc + aux_W
    duty = el["V_motor"] / V_bus
    return {**op, **el, "P_thrust_W": drag_N * V, "P_batt_W": P_batt, "duty_at_bus": duty,
            "feasible_voltage": el["V_motor"] <= V_bus}

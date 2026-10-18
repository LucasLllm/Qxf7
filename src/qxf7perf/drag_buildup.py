"""Component parasite-drag build-up for items NOT in the VLM/NeuralFoil wing+tail model.

Every coefficient is an ASSUMPTION from handbook ranges (Hoerner, Fluid-Dynamic Drag, 1965; Raymer,
Aircraft Design: A Conceptual Approach, 6th ed., ch. 12), applied to extracted CAD dimensions.
low / central / high are a declared sensitivity band, NOT a confidence interval.
Hardware silhouettes are isolated-part projections (bundle hardware_dimensions.csv), not installed
blockage; an installed-exposure factor is applied and declared.
"""
from dataclasses import dataclass

import numpy as np

CASES = ("low", "central", "high")


def cf_turbulent(Re):
    """Flat-plate fully turbulent skin friction (Prandtl-Schlichting, incompressible)."""
    return 0.455 / np.log10(Re) ** 2.58


@dataclass
class Item:
    name: str
    note: str

    def CdA(self, V, nu, case):  # m^2
        raise NotImplementedError


@dataclass
class Fuselage(Item):
    """Skin friction x form factor x interference on the hatch-inclusive convex lateral envelope
    (0.3825 m2, NOT exact wetted area and not a proven bound)."""
    S_wet: float = 0.38249992923878123
    length: float = 1.0          # nose to pusher-mount face, m
    d_eq: float = 0.1445         # sqrt(4 A_max / pi), A_max = 16400 mm2 (convex envelope)

    def CdA(self, V, nu, case):
        f = self.length / self.d_eq
        FF = 1 + 60 / f**3 + f / 400                       # Raymer eq. 12.31
        swet = {"low": 0.9, "central": 1.0, "high": 1.1}[case] * self.S_wet
        Q = {"low": 1.0, "central": 1.05, "high": 1.3}[case]          # interference (high wing, root fairings)
        rough = {"low": 1.0, "central": 1.1, "high": 1.3}[case]       # printed seams/hatch gaps on Cf
        return cf_turbulent(V * self.length / nu) * rough * FF * Q * swet


@dataclass
class Booms(Item):
    """Two 10x10x500 mm square carbon tubes aligned with the flow; friction + blunt end pressure.
    Ends partly covered by motor mounts (counted there)."""
    count: int = 2
    side: float = 0.010
    length: float = 0.5

    def CdA(self, V, nu, case):
        exposed = {"low": 0.6, "central": 0.8, "high": 1.0}[case]       # fraction outside the wing
        Cd_end = {"low": 0.5, "central": 0.8, "high": 1.0}[case]        # blunt fore/aft ends, frontal basis
        fric = cf_turbulent(V * self.length / nu) * 4 * self.side * self.length * exposed
        return self.count * (fric + Cd_end * self.side**2)


@dataclass
class Bluff(Item):
    """Bluff hardware: Cd (frontal basis) x isolated frontal silhouette x installed-exposure factor."""
    frontal_m2: float = 0.0
    Cd: tuple = (0.8, 1.0, 1.2)
    exposure: tuple = (0.6, 0.8, 1.0)

    def CdA(self, V, nu, case):
        i = CASES.index(case)
        return self.Cd[i] * self.frontal_m2 * self.exposure[i]


@dataclass
class StoppedProps(Item):
    """Four stopped 7-inch two-blade lift props. 'aligned' = blades fore-aft (flow along blade span:
    sees section + twist only); 'crossflow' = blades spanwise (inclined twisted plate, ~15-25 deg pitch).
    Windmilling NOT modelled. Builder data put the orientation effect at 10-35 % of cruise power."""
    orientation: str = "aligned"
    count: int = 4
    diameter: float = 0.1778
    mean_chord: float = 0.018

    def CdA(self, V, nu, case):
        plan = self.diameter * self.mean_chord                 # both blades, one prop
        if self.orientation == "aligned":
            per = {"low": 0.03, "central": 0.06, "high": 0.12}[case] * plan   # sections + twist + hub
        else:
            per = {"low": 0.25, "central": 0.4, "high": 0.6}[case] * plan     # inclined-plate CD on planform
        return self.count * per


def standard_stork_items(prop_orientation="aligned"):
    return [
        Fuselage("fuselage", "convex envelope Swet x Cf x Raymer FF x Q"),
        Booms("booms", "2 x 10x10x500 square tubes"),
        Bluff("main skids", "extracted isolated frontal 1560 mm2; strut-like bluff body",
              frontal_m2=1560.4e-6, Cd=(0.8, 1.1, 1.4), exposure=(1.0, 1.0, 1.2)),
        Bluff("lift-motor + boom mounts (16 printed parts)",
              "isolated frontals 4x(323+217+182+111) mm2 = 3332 mm2; overlap with booms/motors/wing",
              frontal_m2=3332e-6, Cd=(0.6, 0.8, 1.0), exposure=(0.4, 0.6, 1.0)),
        Bluff("lift motors (4 x F90)", "can 33.4 mm dia x 25-34.7 mm exposed; short cylinder in crossflow",
              frontal_m2=4 * 0.0334 * 0.030, Cd=(0.6, 0.8, 1.1), exposure=(0.83, 1.0, 1.16)),
        Bluff("pusher motor", "33.9 mm dia can, mostly in fuselage wake", frontal_m2=0.0339 * 0.030,
              Cd=(0.2, 0.5, 0.9)),
        StoppedProps("stopped lift props", f"{prop_orientation}", orientation=prop_orientation),
        Bluff("control horns/pushrods/antennas/pitot/vents",
              "unmodelled excrescences: equivalent frontal allowance (assumption)",
              frontal_m2=1.0e-3, Cd=(0.3, 0.6, 1.0)),
    ]


def buildup(V, nu, rho, case="central", prop_orientation="aligned"):
    q = 0.5 * rho * V**2
    rows = [(it.name, it.CdA(V, nu, case), it.note) for it in standard_stork_items(prop_orientation)]
    return {"items": [{"name": n, "CdA_m2": c, "D_N": q * c, "note": t} for n, c, t in rows],
            "CdA_total_m2": sum(c for _, c, _ in rows), "D_total_N": q * sum(c for _, c, _ in rows)}

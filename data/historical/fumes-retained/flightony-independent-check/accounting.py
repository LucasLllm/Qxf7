"""Pure accounting checks independent of seller power/range assertions."""
import math

def pack_energy(series, parallel, capacity_ah=5., nominal_cell_v=3.6):
    if series<=0 or parallel<=0 or capacity_ah<=0 or nominal_cell_v<=0:
        raise ValueError('positive pack inputs required')
    return series*parallel*capacity_ah*nominal_cell_v

def cruise_budget(nominal_wh, reserve_fraction, mission_wh):
    if nominal_wh<=0 or not 0<=reserve_fraction<1 or mission_wh<0:
        raise ValueError('invalid energy budget')
    budget=nominal_wh*(1-reserve_fraction)-mission_wh
    if budget<=0: raise ValueError('no cruise energy')
    return budget

def range_km(energy_wh,power_w,speed_kmh):
    if min(energy_wh,power_w,speed_kmh)<=0 or not all(map(math.isfinite,[energy_wh,power_w,speed_kmh])):
        raise ValueError('positive finite quantities required')
    return energy_wh/power_w*speed_kmh

def ideal_hover_w(mass_kg,rotors=4,diameter_m=.1778,rho=1.225,g=9.80665):
    if min(mass_kg,rotors,diameter_m,rho,g)<=0: raise ValueError('positive inputs required')
    area=rotors*math.pi*(diameter_m/2)**2
    return (mass_kg*g)**1.5/math.sqrt(2*rho*area)

"""Energy accounting for supplied AIRCRAFT-SPECIFIC power curves.
No aerodynamic coefficients, motor efficiencies or usable energy are inferred here.
"""
import math

def mission_range(*,airspeed_mps,power_w,usable_wh,reserve_wh,vtol_wh,tailwind_mps=0):
    vals=[airspeed_mps,power_w,usable_wh,reserve_wh,vtol_wh,tailwind_mps]
    if not all(math.isfinite(x) for x in vals):raise ValueError('finite inputs required')
    if airspeed_mps<=0 or power_w<=0 or min(usable_wh,reserve_wh,vtol_wh)<0:raise ValueError('invalid speed, power or energy')
    ground_mps=airspeed_mps+tailwind_mps
    if ground_mps<=0:raise ValueError('nonforward groundspeed')
    cruise_wh=max(0,usable_wh-reserve_wh-vtol_wh)
    wh_per_km=power_w/(ground_mps*3.6)
    return dict(cruise_wh=cruise_wh,wh_per_km=wh_per_km,range_km=cruise_wh/wh_per_km,groundspeed_mps=ground_mps)

def range_curve(speed_power_pairs,**mission_inputs):
    return [dict(airspeed_mps=v,power_w=p,**mission_range(airspeed_mps=v,power_w=p,**mission_inputs)) for v,p in speed_power_pairs]


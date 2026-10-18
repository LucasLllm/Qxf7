"""Join solved aerodynamic rows to sourced APC map and conditional motor model.
No wing polar or synthetic drag is generated here. See each child's evidence.
"""
from pathlib import Path
import importlib.util
import sys
from mission import mission_range
ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('stork_propulsion',ROOT/'propulsion/model.py')
propulsion=importlib.util.module_from_spec(spec);spec.loader.exec_module(propulsion)

def couple(*,airspeed_kmh,drag_n,voltage_v,usable_wh,reserve_wh,vtol_wh,tailwind_kmh=0,auxiliary_w=15,esc_efficiency=0.97):
    """Loss-convention envelope. Caller supplies aerodynamic validity.
    ESC efficiency is an explicit planning assumption, not measured specification.
    Return invalid voltage cases without presenting them as achieved range.
    """
    if not 0<esc_efficiency<=1 or auxiliary_w<0:raise ValueError('invalid losses')
    point=propulsion.evaluate(drag_n,airspeed_kmh/3.6,voltage_v)
    rows=[]
    for c in point['motor_cases']:
        r=dict(**c,rpm=point['rpm'],shaft_w=point['shaft_W'],drag_n=drag_n,airspeed_kmh=airspeed_kmh,
               voltage_v=voltage_v,esc_efficiency=esc_efficiency,auxiliary_w=auxiliary_w)
        power=c['electrical_W']/esc_efficiency+auxiliary_w
        r['battery_terminal_power_w']=power
        r['status']='conditional_feasible' if c['voltage_feasible'] else 'voltage_infeasible'
        r['range_km']=None
        if c['voltage_feasible']:
            r.update(mission_range(airspeed_mps=airspeed_kmh/3.6,power_w=power,usable_wh=usable_wh,
                 reserve_wh=reserve_wh,vtol_wh=vtol_wh,tailwind_mps=tailwind_kmh/3.6))
        rows.append(r)
    return rows

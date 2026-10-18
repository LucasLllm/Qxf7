"""Run conditional mission envelope from ACTUALLY SOLVED assembled aero rows."""
from pathlib import Path
from itertools import product
from functools import lru_cache
import json,csv,math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import couple
ROOT=Path(__file__).resolve().parent

def main():
    aero=json.loads((ROOT/'ASSEMBLED_AERO.json').read_text());inputs=json.loads((ROOT/'MISSION_INPUTS.json').read_text())
    assert len(aero)==44,'refuse incomplete aerodynamic sweep'
    assert all(r['trim_numerically_closed'] for r in aero),'refuse failed trims'
    couple.propulsion.evaluate=lru_cache(maxsize=None)(couple.propulsion.evaluate)
    rows=[];failed=[]
    for a in aero:
        if not a['usable_for_conditional_range']:
            failed.append({'speed_kmh':a['speed_kmh'],'surface':a['surface'],'orientation':a['prop_orientation'],'reason':'aerodynamic validity screen'});continue
        for ef,vtol,wind,esc,volt in product(inputs['usable_energy_fraction_sensitivity'],inputs['vtol_departure_arrival_wh_sensitivity'],inputs['tailwind_kmh_sensitivity'],inputs['esc_efficiency_sensitivity'],inputs['loaded_voltage_v_checks']):
            try:
                cases=couple.couple(airspeed_kmh=a['speed_kmh'],drag_n=a['drag_N'],voltage_v=volt,usable_wh=216*ef,reserve_wh=inputs['reserve_wh'],vtol_wh=vtol,tailwind_kmh=wind,auxiliary_w=inputs['auxiliary_power_w'],esc_efficiency=esc)
                for c in cases:
                    c.update(surface=a['surface'],prop_orientation=a['prop_orientation'],energy_fraction=ef,vtol_wh=vtol,tailwind_kmh=wind,prestall_area_fraction=a['NF_outside_prestall_area_fraction'],esc_assumed_efficiency=esc)
                    bus=c['battery_terminal_power_w']/volt
                    c['esc_bus_current_screen_A']=bus
                    if bus>51:c['status']='exceeds_ESC_nameplate_screen';c['range_km']=None
                    rows.append(c)
            except couple.propulsion.DomainError as e:
                failed.append({'speed_kmh':a['speed_kmh'],'surface':a['surface'],'orientation':a['prop_orientation'],'reason':str(e)})
    assert rows,'no supported propulsion cases'
    with (ROOT/'MISSION_SWEEP.csv').open('w')as f:
        fields=sorted(set().union(*(r.keys()for r in rows)));w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)
    (ROOT/'UNSUPPORTED_CASES.json').write_text(json.dumps(failed,indent=2))
    central=[r for r in rows if r['resistance_factor']==1 and r['idle_reference_V']==10 and r['voltage_v']==14.4 and r['energy_fraction']==.9 and r['vtol_wh']==30 and r['tailwind_kmh']==0 and r['esc_efficiency']==.97]
    grouped={}
    for surface,orientation in product(['smooth','rough'],['aligned','crossflow']):
        c=[r for r in central if r['surface']==surface and r['prop_orientation']==orientation and r['range_km'] is not None]
        if c:grouped[surface+'_'+orientation]={'optimum':max(c,key=lambda r:r['range_km']),'at60':next(r for r in c if r['airspeed_kmh']==60)}
    valid=[r for r in rows if r['range_km'] is not None]
    nominal=[r for r in valid if r['voltage_v']==14.4 and r['tailwind_kmh']==0]
    summary={'case_count':len(rows),'valid_electrical_case_count':len(valid),'unsupported_count':len(failed),'central':grouped,'still_air_sensitivity_range_km':[min(r['range_km']for r in nominal),max(r['range_km']for r in nominal)],'range_kind':'Conditional one-way cruise distance after reserve and assumed departure/arrival allocation; NOT delivery authorization, return radius or measured range','central_energy_wh':194.4,'central_reserve_wh':43.2,'central_vtol_wh':30,'central_cruise_wh':121.2,'central_wind_kmh':0,'uncertainty_kind':'Scenario endpoints; NOT confidence interval','windmilling_mode':'Not quantified: horizontal lift rotor sees primarily edgewise cruise flow; do not apply axial actuator-disk drag formula','mass_growth':'100g unspent margin is not included in physical mass; rerun aero required for growth stress'}
    (ROOT/'MISSION_SUMMARY.json').write_text(json.dumps(summary,indent=2))
    fig,axs=plt.subplots(2,2,figsize=(13,9))
    for label,v in grouped.items():
        c=sorted([r for r in central if r['surface']+'_'+r['prop_orientation']==label and r['range_km'] is not None],key=lambda r:r['airspeed_kmh'])
        s=[r['airspeed_kmh']for r in c]
        axs[0,0].plot(s,[r['drag_n']for r in c],label=label)
        axs[0,1].plot(s,[r['battery_terminal_power_w']for r in c],label=label)
        axs[1,0].plot(s,[r['wh_per_km']for r in c],label=label)
        axs[1,1].plot(s,[r['range_km']for r in c],label=label)
    for ax,title,y in zip(axs.flat,['Solved drag','Conditional battery power','Energy per kilometre','Conditional one-way range'],['Drag (N)','Power (W)','Wh/km','Range (km)']):
        ax.set(title=title,xlabel='Airspeed (km/h)',ylabel=y);ax.grid(alpha=.3);ax.legend(fontsize=8)
    fig.suptitle('Original no-payload Stork, 2.9837kg | idealized source sections + component drag\nAPC10x6E; BH2812 loss model; central121.2Wh for cruise; still air | NOT flight-validated',fontsize=12);fig.tight_layout();fig.savefig(ROOT/'PERFORMANCE_CURVES.png',dpi=170);plt.close(fig)
    a=next(a for a in aero if a['speed_kmh']==60 and a['surface']=='smooth' and a['prop_orientation']=='aligned')
    keys=['induced_N','profile_N','fuselage_N','booms_N','gear_N','mounts_N','lift_motors_N','pusher_motor_N','lift_props_N'];fig,ax=plt.subplots(figsize=(10,5));ax.barh([k.removesuffix('_N')for k in keys],[a[k]for k in keys]);ax.set(xlabel='Drag (N)',title='60km/h drag buildup | geometry-derived proxies, not CFD measurements');ax.grid(axis='x',alpha=.3);fig.tight_layout();fig.savefig(ROOT/'DRAG_BREAKDOWN.png',dpi=170);plt.close(fig)
    print(json.dumps({'cases':len(rows),'central_optima':{k:dict(speed=v['optimum']['airspeed_kmh'],range_km=v['optimum']['range_km'],power_w=v['optimum']['battery_terminal_power_w'])for k,v in grouped.items()},'still_air_sensitivity_range_km':summary['still_air_sensitivity_range_km']},indent=2))
if __name__=='__main__':main()

"""Frozen prior hybrid method applied to seller masses; never fitted to their claims.
Original solver/geometry/prop inputs read-only. New outputs confined to this folder.
"""
from pathlib import Path
from functools import lru_cache
import sys,json,csv,hashlib,copy
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from accounting import pack_energy,cruise_budget,range_km,ideal_hover_w
OUT=Path(__file__).resolve().parent
BASE=OUT.parent/'performance-scenarios/original-manual-range/aircraft-specific-analysis'
sys.path.insert(0,str(BASE))
import assembled_solver as assembled
import couple
assembled.solver.build_airplane=assembled.build
couple.propulsion.evaluate=lru_cache(maxsize=None)(couple.propulsion.evaluate)

SCENARIOS=[
 {'name':'seller_4S4P','mass':2.9,'parallel':4,'mass_basis':'seller Operator advertised AUW; payload inclusion unspecified'},
 {'name':'seller_4S3P','mass':2.7,'parallel':3,'mass_basis':'seller Explorer advertised AUW; payload inclusion unspecified'},
 {'name':'stock_3p1kg','mass':3.1,'parallel':4,'mass_basis':'documentary top mass sensitivity, NOT qualified MTOW'},
 {'name':'our_dry_4S4P','mass':3.2567,'parallel':4,'mass_basis':'prior dry mass2056.7g + seller pack1200g, no cargo; different material/installation'},
 {'name':'our_dry_4S3P','mass':2.9567,'parallel':3,'mass_basis':'prior dry mass2056.7g + assumed proportional900g pack, no cargo; NOT seller pack mass'}]

def main():
 g=json.loads((BASE/'geometry/GEOMETRY.json').read_text())
 cg=json.loads((BASE/'VERIFIED_CONFIG.json').read_text())['cg_ASB_aft_right_up_m']
 watched=[BASE/'assembled_solver.py',BASE/'aero/solver.py',BASE/'propulsion/model.py',BASE/'propulsion/data/PER3_10x6E.DOM.dat',BASE/'geometry/GEOMETRY.json',BASE/'idealized-sections/SECTIONS.json',BASE/'VERIFIED_CONFIG.json']
 hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}
 (OUT/'INPUTS.json').write_text(json.dumps({'scenarios':SCENARIOS,'source_hashes':hashes,'method':'unaltered previous AeroSandbox VLM+NeuralFoil+component buildup; same mesh2,3','auxiliary_W':15,'esc_efficiency':.97,'loaded_voltage_checks':[12.,14.4,16.8],'seller_noncruise_wh':40/3,'mission_allowance_kind':'seller13.333Wh budget questionable hover; separately30Wh previous planning allowance; neither validated','energy_policy':'10% reserve once; nominal50E energy only, no inferred measured discharge energy','wind_kmh':0,'battery_losses':'50E discharge curve not integrated; nominal energy optimistic assumption'},indent=2))
 aero=[]; rows=[]; failures=[]; diagnostics=[]; conv=[]
 for sc in SCENARIOS:
  for surface in ['smooth','rough']:
   initial=(2.,0.)
   for speed in range(50,71,2):
    a=assembled.solver.solve_point(g,BASE/'geometry',speed,mass=sc['mass'],mesh=(2,3),working_cg=tuple(cg),surface=surface,initial=initial)
    initial=(a['alpha_deg'],a['equivalent_tail_incidence_adjust_deg'])
    admitted=a['trim_numerically_closed'] and a['NF_outside_prestall_area_fraction']<.01 and a['NF_area_weighted_confidence']>=.8
    print(sc['name'],surface,speed,'trim',a['trim_numerically_closed'],'D',a['drag_N'],flush=True)
    for orientation in ['aligned','crossflow']:
     b=copy.deepcopy(a); b.update(assembled.solver.component_drag(g,speed/3.6,orientation,surface));b['prop_orientation']=orientation
     b['drag_N']=b['induced_N']+b['profile_N']+b['parasite_N'];b['aero_power_W']=b['drag_N']*speed/3.6;b['scenario']=sc['name'];b['admitted']=admitted;aero.append(b)
     if not admitted:failures.append({'scenario':sc['name'],'speed':speed,'surface':surface,'orientation':orientation,'reason':'aero validity screen'});continue
     for volts in [12.,14.4,16.8]:
      try:
       cs=couple.couple(airspeed_kmh=speed,drag_n=b['drag_N'],voltage_v=volts,usable_wh=pack_energy(4,sc['parallel']),reserve_wh=pack_energy(4,sc['parallel'])*.1,vtol_wh=0,auxiliary_w=15,esc_efficiency=.97)
       for c in cs:
        c.update(scenario=sc['name'],surface=surface,orientation=orientation,mass_kg=sc['mass'],nominal_wh=pack_energy(4,sc['parallel']))
        for key,wh in [('cruise_only',0),('seller_vtol',40/3),('previous_allowance',30)]:
         c['range_'+key+'_km']=range_km(cruise_budget(c['nominal_wh'],.1,wh),c['battery_terminal_power_w'],speed) if c['voltage_feasible'] else None
        rows.append(c)
      except couple.propulsion.DomainError as e:
       failures.append({'scenario':sc['name'],'speed':speed,'surface':surface,'orientation':orientation,'reason':str(e)})
     if surface=='smooth' and orientation=='aligned' and speed in [54,60] and sc['name'].startswith('seller'):
      for label,drag in [('remove_gear_mount_proxy_only',b['drag_N']-b['gear_N']-b['mounts_N']),('lifting_surfaces_only',b['induced_N']+b['profile_N'])]:
       try:
        d=couple.couple(airspeed_kmh=speed,drag_n=drag,voltage_v=14.4,usable_wh=pack_energy(4,sc['parallel']),reserve_wh=pack_energy(4,sc['parallel'])*.1,vtol_wh=40/3)
        c=next(c for c in d if c['resistance_factor']==1 and c['idle_reference_V']==10)
        diagnostics.append(dict(scenario=sc['name'],speed=speed,label=label,power_w=c['battery_terminal_power_w'],range_km=c['range_km'],drag_n=drag,interpretation='omission diagnostic, NOT an aircraft result or credible lower confidence bound'))
       except couple.propulsion.DomainError as e:diagnostics.append(dict(scenario=sc['name'],speed=speed,label=label,error=str(e)))
   (OUT/'AERO.json').write_text(json.dumps(aero,indent=2))
 for sc in SCENARIOS[:2]:
  for mesh in [(2,3),(3,4),(4,5)]:
   a=assembled.solver.solve_point(g,BASE/'geometry',60,mass=sc['mass'],mesh=mesh,working_cg=tuple(cg),surface='smooth',prop_orientation='aligned')
   a['scenario']=sc['name'];conv.append(a)
 (OUT/'CONVERGENCE.json').write_text(json.dumps(conv,indent=2))
 (OUT/'RESULTS.json').write_text(json.dumps(rows,indent=2));(OUT/'DIAGNOSTICS.json').write_text(json.dumps(diagnostics,indent=2));(OUT/'UNSUPPORTED.json').write_text(json.dumps(failures,indent=2))
 with (OUT/'RESULTS.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=sorted(set().union(*(r.keys() for r in rows))));w.writeheader();w.writerows(rows)
 central=[r for r in rows if r['resistance_factor']==1 and r['idle_reference_V']==10 and r['voltage_v']==14.4 and r['voltage_feasible']]
 summary={}
 for sc in SCENARIOS:
  summary[sc['name']]={}
  for surface in ['smooth','rough']:
   for orientation in ['aligned','crossflow']:
    c=[r for r in central if r['scenario']==sc['name'] and r['surface']==surface and r['orientation']==orientation]
    if c:
     subset=[r for r in c if 54<=r['airspeed_kmh']<=60]
     summary[sc['name']][surface+'_'+orientation]={'best_tested_50_70':min(c,key=lambda r:r['wh_per_km']),'best_tested_54_60':min(subset,key=lambda r:r['wh_per_km']),'at54':next(r for r in c if r['airspeed_kmh']==54),'at60':next(r for r in c if r['airspeed_kmh']==60)}
 checks=0
 for r in rows:
  assert r['battery_terminal_power_w']>=r['shaft_w'];checks+=1
  for key,wh in [('cruise_only',0),('seller_vtol',40/3),('previous_allowance',30)]:
   rr=r['range_'+key+'_km']
   if rr is not None:
    assert r['voltage_feasible']
    assert abs(rr*r['battery_terminal_power_w']/r['airspeed_kmh']-(r['nominal_wh']*.9-wh))<1e-8;checks+=1
 for p,h in hashes.items(): assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
 (OUT/'SUMMARY.json').write_text(json.dumps(summary,indent=2))
 verification={'aero_points':len(aero),'electrical_cases':len(rows),'unsupported_count':len(failures),'accounting_checks':checks,'original_inputs_unchanged':True,'hover_ideal_W':{str(m):ideal_hover_w(m) for m in [2.7,2.9,3.1]},'AR_nominal':1.62**2/.31,'seller_takeoff_transition_arrival_wh':40/3}
 (OUT/'VERIFICATION.json').write_text(json.dumps(verification,indent=2))
 fig,axs=plt.subplots(1,3,figsize=(15,4.8))
 for name in ['seller_4S4P','seller_4S3P']:
  for ori in ['aligned','crossflow']:
   c=sorted([r for r in central if r['scenario']==name and r['surface']=='smooth' and r['orientation']==ori],key=lambda r:r['airspeed_kmh'])
   for ax,key in zip(axs,['battery_terminal_power_w','wh_per_km','range_seller_vtol_km']):ax.plot([r['airspeed_kmh'] for r in c],[r[key] for r in c],label=name+' '+ori)
 for ax,y in zip(axs,['Total battery power (W)','Wh/km','Conditional distance (km)']):ax.set(xlabel='Airspeed (km/h)',ylabel=y);ax.grid(alpha=.3);ax.legend(fontsize=7)
 axs[0].axhspan(80,110,color='grey',alpha=.2,label='Seller claimed cruise power')
 fig.suptitle('Flightony advertised masses | SAME prior hybrid model, NOT flight validation\nNominal50E energy,10% reserve once,seller13.33Wh mission budget;15W auxiliary assumption');fig.tight_layout();fig.savefig(OUT/'COMPARISON.png',dpi=160);plt.close(fig)
 print(json.dumps(verification,indent=2))
if __name__=='__main__':main()

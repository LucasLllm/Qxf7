"""Offline reproducible artifact builder; import has no side effects."""
from pathlib import Path
import json,csv,hashlib,importlib.util,math
from PIL import Image
ROOT=Path(__file__).resolve().parent


def digitize():
    """Orange-line center, original 2240x1040 manufacturer raster.

    Calibrated chart grid: x=145 at 0Ah, x=2143 at 5.2Ah;
    y=150 at 4.2V, y=918 at 2.2V. No inferred endpoints.
    """
    im=Image.open(ROOT/'data/p50b-1C.png').convert('RGB')
    if im.size!=(2240,1040):raise ValueError('unexpected chart dimensions')
    rows=[]
    for x in range(145,2144):
        ys=[y for y in range(140,920) if (lambda c:c[0]>220 and 50<c[1]<160 and c[2]<60)(im.getpixel((x,y)))]
        if ys:
            y=(min(ys)+max(ys))/2
            rows.append(((x-145)*5.2/(2143-145),4.2-(y-150)*2/(918-150)))
    return rows


def build():
    spec=importlib.util.spec_from_file_location('bounded_propulsion',ROOT/'model.py')
    model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)
    curve=digitize()
    with (ROOT/'data/p50b-1C-digitized.csv').open('w') as f:
        writer=csv.writer(f);writer.writerow(['discharged_Ah','loaded_cell_V']);writer.writerows(curve)
    prop=model.Propeller()
    with (ROOT/'data/apc-forward.csv').open('w') as f:
        writer=csv.writer(f);writer.writerow(['rpm','airspeed_mps','thrust_N','shaft_W'])
        for rpm,rows in prop.blocks.items():
            for row in rows:writer.writerow([rpm,*row])
    examples=[]
    for kph in (50,60,70):
        for thrust in (1,2,4,8):
            try:
                result=model.evaluate(thrust,kph/3.6,14.4)
                cases=result['motor_cases']
                result.update(electrical_W_sensitivity=[min(c['electrical_W'] for c in cases),max(c['electrical_W'] for c in cases)])
            except model.DomainError as e:result=dict(thrust_N=thrust,airspeed_mps=kph/3.6,error=str(e))
            examples.append(result)
    # Bench has only bus input and RPM, not torque. Infer possible shaft power
    # for each convention under ideal PWM, allowing all bench input to motor.
    # It is an upper bound under each assumed DC convention, not calibration.
    bench=json.loads((ROOT/'data/bh2812-bench.json').read_text())
    diagnostic=[]
    for row in bench:
        emf=row['rpm']/910;p=row['input_W'];cases=[]
        for factor in (0.5,1,2):
            r=0.072*factor
            current=2*p/(emf+math.sqrt(emf*emf+4*r*p))
            for ref in (10,14):
                no_load=(ref-1.17*r)*1.17
                shaft=emf*current-no_load
                cases.append(dict(effective_R_ohm=r,idle_reference_V=ref,
                    equivalent_motor_A=current,shaft_upper_bound_W=shaft,
                    required_motor_V=emf+r*current,
                    admissible=shaft>=0 and emf+r*current<=row['voltage_V']))
        diagnostic.append(dict(rpm=row['rpm'],bench_electrical_W=p,cases=cases))
    (ROOT/'data/bench-loss-consistency.json').write_text(json.dumps(diagnostic,indent=2)+'\n')
    source_urls={
        'apc-index.DOM.html':'https://www.apcprop.com/technical-information/performance-data/?v=5435c69ed3bc',
        'apc-product.DOM.html':'https://www.apcprop.com/product/10x6e/?v=5435c69ed3bc',
        'apc-product.DOM.txt':'https://www.apcprop.com/product/10x6e/?v=5435c69ed3bc',
        'PER3_10x6E.DOM.dat':'https://www.apcprop.com/files/PER3_10x6E.dat',
        'bh2812-test.jpg':'https://ueeshop.ly200-cdn.com/u_file/UPAI/UPAI594/2410/photo/d92fe20edf.jpg',
        'bh2812-bench.json':'https://ueeshop.ly200-cdn.com/u_file/UPAI/UPAI594/2410/photo/d92fe20edf.jpg',
        'p50b-marketing.cached.html':'https://www.molicel.com/inr-21700-p50b/',
        'apc-rpm.cached.txt':'https://www.apcprop.com/technical-information/rpm-limits/'}
    source_manifest=[]
    for name,url in source_urls.items():
        p=ROOT/'data'/name
        source_manifest.append(dict(path=str(p.relative_to(ROOT)),url=url,sha256=hashlib.sha256(p.read_bytes()).hexdigest(),capture='cached' if 'cached' in name or name.startswith('bh') else 'browser DOM'))
    source_manifest+=json.loads((ROOT/'SOURCES.json').read_text())
    low=model.integrate_curve(curve,3.0)*12
    wide=model.integrate_curve(curve,2.6)*12
    out=dict(schema_version=1,scenario=dict(payload_g=0,central_mass_g=2983.7,baseline='stock 4S BH2812 V5 910KV / 10x6 two-blade'),
        selected_prop=dict(model='APC 10x6E',sku='LP10060E',blades=2,selection='exact analyst-selected modeled candidate; not proven manual prototype',performance_kind='APC computed vortex-theory map; not measurement',simulation_date='2022-09-22',version='v2022-0915',map='data/PER3_10x6E.DOM.dat',suggested_max_rpm=15000,
            hub=dict(diameter_mm=0.80*25.4,thickness_mm=0.39*25.4,bore_mm=25.4/4,ring_set='LPAR06E included',motor_thread='M5',requires='5mm centering interface/ring; sufficient nut thread engagement and prop clamping; verify exact supplied ring IDs, shaft shoulder, washer/nut and rotation clearance',installation_qualified=False),catalog_mass_g=0.71*28.349523125),
        motor=dict(model='BrotherHobby Avenger 2812 V5 910KV',kv_rpm_per_V=910,catalog_resistance_ohm=0.072,idle_current_A=1.17,idle_reference_conflict_V=[10,14],effective_R_sensitivities_ohm=[0.036,0.072,0.144],torque_constant_Nm_per_A=60/(2*math.pi*910),method='Equivalent DC: E=rpm/Kv; P0=(Vref-R*I0)*I0; Im=(Pshaft+P0)/E; Pe=Pshaft+P0+R*Im^2; Vm=E+R*Im; ideal PWM bus current Pe/Vloaded.',calibrated=False,excludes=['ESC losses','wiring','battery internal losses','auxiliary loads','temperature drift','speed-dependent iron/windage beyond constant no-load power hypothesis'],uncertainty='R factors are assumed convention sensitivities, not proven phase-to-line conversion or confidence bounds; idle reference is contradictory. Bench has no torque, so only admissibility/upper-shaft consistency checks, not loss fitting.'),
        battery=dict(cell='Molicel INR-21700-P50B',series=4,parallel=3,cells=12,typical_capacity_Ah=15,nominal_voltage_V=14.4,full_voltage_V=16.8,nominal_Wh=216,cell_max_mass_g=71,cell_only_max_mass_sum_g=852,qualified_mission_usable_Wh=None,reserve_Wh=None,
            curve_diagnostic=dict(source='data/p50b-1C.png',digitization='data/p50b-1C-digitized.csv',sample_count=len(curve),captured_capacity_range_Ah=[curve[0][0],curve[-1][0]],captured_V_end=curve[-1][1],label='manufacturer 1C tab / alt text',condition_conflict='Caption instead says 1A/120s with 10A/10s pulses to 2.5V. No unambiguous constant-current/temperature raw trace. Cannot transfer to arbitrary flight load.',pack_equivalent_Wh_to_3V=low,pack_equivalent_Wh_to_2_6V=wide,meaning='12 times plotted cell integral only; illustrative 3.0/2.6V cell cutoffs, NOT flight cutoff or qualified usable pack energy',digitization_uncertainty='grid/line approximately ±0.02V and ±0.02Ah; no manufacturer performance tolerance provided',reserve_subtracted=False)),
        api=dict(module='model.py',call='evaluate(thrust_N, airspeed_mps, loaded_voltage_V)',prop_only='Propeller().solve(thrust_N, airspeed_mps)',energy='integrate_curve(curve, cutoff_V); energy_budget(source_usable_Wh, reserve_Wh, noncruise_Wh)',failure='DomainError outside supported brackets; electrical cases include voltage_feasible flag; reject infeasible cases',units='SI except rpm, Ah, Wh',import_safe=True,no_extrapolation=True,density='native APC dimensional map density; no altitude rescaling provided',unsupported_example='1N at70km/h: minimum complete RPM bracket starts at1.272N'),examples=examples,source_manifest=source_manifest,new_fetch_attempts=8)
    (ROOT/'PROPULSION.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    return out

if __name__=='__main__':
    out=build()
    print(json.dumps(out['battery']['curve_diagnostic'],indent=2))
    for r in out['examples']:
        print(round(r['airspeed_mps']*3.6),r['thrust_N'],r.get('rpm'),r.get('shaft_W'),r.get('electrical_W_sensitivity'),r.get('error'))

import math, json
from pathlib import Path
rho, g, diameter, rotors = 1.225, 9.80665, 7 * 0.0254, 4
area = rotors * math.pi * (diameter / 2) ** 2
out = {'assumptions': {'rho_kg_m3': rho, 'g_m_s2': g, 'diameter_m': diameter, 'lift_rotors': rotors, 'total_disk_area_m2': area}, 'packs': {}, 'hover': []}
for p in (4, 3):
    out['packs'][f'4S{p}P'] = {'cells': 4*p, 'nominal_voltage_V': 14.4, 'full_charge_V': 16.8, 'retail_class_capacity_Ah': p*5.0, 'standard_min_capacity_Ah': p*4.9, 'rated_1C_min_capacity_Ah': p*4.753, 'retail_class_Wh_estimate': 4*p*5*3.6, 'standard_min_Wh_estimate': 4*p*4.9*3.6, 'rated_1C_min_Wh_estimate': 4*p*4.753*3.6, 'cell_only_max_g': 4*p*69, 'cell_sum_CDR_A': p*9.8, 'at_300W_14_4V_pack_A': 300/14.4, 'at_300W_14_4V_cell_A': 300/14.4/p, 'at_300W_10V_pack_A': 300/10, 'at_300W_10V_cell_A': 300/10/p, 'retail_class_90pct_Wh': 4*p*5*3.6*0.9, 'standard_min_90pct_Wh': 4*p*4.9*3.6*0.9, 'rated_1C_min_90pct_Wh': 4*p*4.753*3.6*0.9}
for m in (2.9,3.1):
    thrust = m*g
    vi = math.sqrt(thrust/(2*rho*area))
    power = thrust*vi
    out['hover'].append({'mass_kg':m,'thrust_N':thrust,'induced_velocity_m_s':vi,'ideal_induced_power_W':power,'300W_minus_ideal_W':300-power,'300W_to_ideal_ratio':300/power,'ideal_to_300W_ratio':power/300})
out['4S3P_range_implied_Wh_km_retail90pct'] = {'70km':194.4/70,'85km':194.4/85}
Path(__file__).with_name('battery_calculations.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))

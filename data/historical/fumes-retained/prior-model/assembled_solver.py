"""Assembled SOURCE section model with stated sealed-hinge approximation.
Reuse trim solver; do NOT use its independently isolated print-part airfoils.
"""
from pathlib import Path
import json,sys
import numpy as np
import aerosandbox as asb
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'aero'))
import solver

def build(g,geometry_root,tail_adjust_deg=0.,working_cg=None):
    p=ROOT/'idealized-sections/SECTIONS.json'
    if not p.exists() or not g:raise ValueError('complete assembled sections and source geometry required')
    sections=json.loads(p.read_text());prior=json.loads((ROOT.parent.parent/'range-first/geometry-placement/wing-evidence/wing-results.json').read_text())
    groups={}
    for r in sections:groups.setdefault((r['family'],r['side']),[]).append(r)
    wings=[];audit=[]
    for (family,side),rows in groups.items():
        rows=sorted(rows,key=lambda r:abs(r['station_m']));xsecs=[]
        if family=='wing':
            # Integration seam probes are NOT valid VLM panel boundaries (near-duplicate
            # span locations create singular/sliver panels). Use separated source stations.
            selected=[92.001,100.,150.,200.,250.,300.,400.,500.,600.,700.,760.,790.,800.,805.]
            plan=[r for r in prior['sections'] if np.sign(r['y_mm'])==side and any(abs(abs(r['y_mm'])-y)<1e-6 for y in selected)]
            plan=sorted(plan,key=lambda r:abs(r['y_mm']))
            for r in plan:
                nearest=min(rows,key=lambda a:abs(abs(a['station_m'])-abs(r['y_mm'])/1000))
                le=np.asarray(r['LE_xyz_mm'])/1000;te=np.asarray(r['TE_xyz_mm'])/1000
                chord=float(np.linalg.norm((le-te)[[0,2]]))
                incidence=float(np.degrees(np.arctan2(le[2]-te[2],le[0]-te[0])))
                xsecs.append(asb.WingXSec(xyz_le=(le*np.array([-1,-1,1])).tolist(),chord=chord,twist=incidence,airfoil=solver.load_contour(ROOT/nearest['file'])))
        else:
            # Actual canted tail sections. Endpoint extrapolation explicitly limited20mm.
            frame=np.asarray(rows[0]['section_frame_rows']);parts={part for r in rows for part in r['parts']}
            comps=[c for c in g['components'] if c['name'] in parts]
            from itertools import product
            points=np.concatenate([np.array(list(product(*zip(*c['bounds_m']))))for c in comps])
            spans=points@frame[1];lo=max(float(min(spans)),abs(rows[0]['station_m'])-.020);hi=min(float(max(spans)),abs(rows[-1]['station_m'])+.020)
            stations=[(abs(r['station_m']),r)for r in rows]
            if lo<stations[0][0]:stations.insert(0,(lo,rows[0]))
            if hi>stations[-1][0]:stations.append((hi,rows[-1]))
            for span,r in stations:
                le=np.array([r['LE_local_xz_m'][0],span,r['LE_local_xz_m'][1]])@frame
                xsecs.append(asb.WingXSec(xyz_le=(le*np.array([-1,-1,1])).tolist(),chord=r['chord_m'],twist=r['incidence_deg']+tail_adjust_deg,airfoil=solver.load_contour(ROOT/r['file'])))
        if xsecs[-1].xyz_le[1]<xsecs[0].xyz_le[1]:xsecs=xsecs[::-1]
        w=asb.Wing(name=f'{family}:assembled:{side}',xsecs=xsecs,symmetric=False);wings.append(w)
        audit.append({'family':family,'side':side,'area_m2':float(w.area()),'profile_method':'source envelope with explicitly sealed short hinge gaps','profile_fit_max_chord':max(r['fit_max_chord'] for r in rows),'profile_confidence_min':min(r['analysis_confidence'] for r in rows)})
    cg=working_cg or json.loads((ROOT/'VERIFIED_CONFIG.json').read_text())['cg_ASB_aft_right_up_m']
    area=g['wing']['exposed_projected_union_area_m2'];span=g['wing']['span_m']
    plane=asb.Airplane(name='Stork assembled source profiles; sealed-hinge planning model',xyz_ref=cg,wings=wings,s_ref=area,b_ref=span,c_ref=area/span)
    return plane,dict(surface_audit=audit,wing_reference_area_m2=area,wing_modeled_area_m2=sum(float(w.area())for w in wings if w.name.startswith('wing')),workingCG_ASB_m=cg,center_bridge=False,hinge_sealing_approximation=True)

def main():
    import csv
    g=json.loads((ROOT/'geometry/GEOMETRY.json').read_text());cg=json.loads((ROOT/'VERIFIED_CONFIG.json').read_text())['cg_ASB_aft_right_up_m']
    solver.build_airplane=build
    plane,meta=build(g,ROOT/'geometry',working_cg=cg)
    (ROOT/'ASSEMBLED_AERO_METADATA.json').write_text(json.dumps(meta,indent=2))
    rows=[]
    for surface,orientation in [('smooth','aligned'),('rough','aligned'),('smooth','crossflow'),('rough','crossflow')]:
        initial=(2.,0.)
        for speed in range(50,71,2):
            r=solver.solve_point(g,ROOT/'geometry',speed,mesh=(2,3),working_cg=tuple(cg),surface=surface,prop_orientation=orientation,initial=initial)
            initial=(r['alpha_deg'],r['equivalent_tail_incidence_adjust_deg'])
            # Never accept clipped prestall strips as a calibrated polar.
            r['usable_for_conditional_range']=r['trim_numerically_closed'] and r['NF_outside_prestall_area_fraction']<.01 and r['NF_area_weighted_confidence']>=.8
            rows.append(r);(ROOT/'ASSEMBLED_AERO.json').write_text(json.dumps(rows,indent=2))
            print(surface,orientation,speed,r['drag_N'],r['NF_area_weighted_confidence'],r['usable_for_conditional_range'],flush=True)
    conv=[]
    for mesh in [(2,3),(3,4),(4,5)]:
        r=solver.solve_point(g,ROOT/'geometry',60,mesh=mesh,working_cg=tuple(cg));conv.append(r)
    (ROOT/'ASSEMBLED_CONVERGENCE.json').write_text(json.dumps(conv,indent=2))
    with (ROOT/'ASSEMBLED_AERO.csv').open('w')as f:
        fields=[k for k,v in rows[0].items() if isinstance(v,(int,float,str,bool))];w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
if __name__=='__main__':main()

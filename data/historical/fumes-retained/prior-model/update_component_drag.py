"""Recompute component drag only after documentary motor-diameter correction.
Does not rerun lifting-surface trim or alter convergence evidence. The implemented
trim omits body/thrust-line moments, so changed component drag does not enter trim.
"""
from pathlib import Path
import json,csv,hashlib,sys
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'aero'))
import solver

def main():
    p=ROOT/'ASSEMBLED_AERO.json'
    original=p.read_bytes()
    archive=ROOT/'ASSEMBLED_AERO_BEFORE_F90_CORRECTION.json'
    if not archive.exists():archive.write_bytes(original)
    rows=json.loads(original);g=json.loads((ROOT/'geometry/GEOMETRY.json').read_text())
    for r in rows:
        r.update(solver.component_drag(g,r['speed_mps'],r['prop_orientation'],r['surface']))
        r['drag_N']=r['induced_N']+r['profile_N']+r['parasite_N']
        r['aero_power_W']=r['drag_N']*r['speed_mps']
        r['CD']=r['drag_N']/(.5*solver.ASSUMPTIONS['rho_kg_m3']*r['speed_mps']**2*g['wing']['exposed_projected_union_area_m2'])
        r['L_D']=r['mass_kg']*9.80665/r['drag_N']
        r['component_revision']='F90 documentary33.4mm diameter; exposed height25mm still assumed'
    p.write_text(json.dumps(rows,indent=2,allow_nan=False))
    with (ROOT/'ASSEMBLED_AERO.csv').open('w') as f:
        fields=[k for k,v in rows[0].items() if isinstance(v,(int,float,str,bool))]
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)
    audit={'rows':len(rows),'prior_sha256':hashlib.sha256(original).hexdigest(),'new_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'assumptions':solver.ASSUMPTIONS,'trim_rerun':False,'reason':'component drag additive; parasite pitch moment omitted in current model','convergence_artifact_status':'older component revision; final convergence readback not completed'}
    (ROOT/'COMPONENT_REVISION.json').write_text(json.dumps(audit,indent=2))
    print('Updated component drag in',len(rows),'solved aerodynamic rows; preserved old revision.')
if __name__=='__main__':main()

"""Documented aerodynamic idealization, NOT original source geometry.
Keep source profiles intact. Bridge servo-pocket/hinge interruptions for single-
airfoil NeuralFoil baseline; add separate discontinuity drag allowance in mission.
"""
from pathlib import Path
import json,numpy as np
import aerosandbox as asb
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parent

def main():
    rows=json.loads((ROOT/'assembled-sections/SECTIONS.json').read_text());out=ROOT/'idealized-sections';out.mkdir(exist_ok=True)
    new=[]
    for r in rows:
        xy=np.loadtxt(ROOT/r['file'],skiprows=1);n=(len(xy)+1)//2
        upper=xy[:n].copy();lower=xy[n:].copy()
        masks=[]
        if r['family']=='tail' and r['source_parts']>1:masks=[(.60,.80)]
        elif r['family']=='wing' and r['source_parts']>1:
            masks=[(.65,.79)]
            if abs(abs(r['station_m'])-.5)<.001:masks.append((.245,.55))
        for branch in [upper,lower]:
            for a,b in masks:
                bad=(branch[:,0]>a)&(branch[:,0]<b);order=np.argsort(branch[~bad,0]);src=branch[~bad][order]
                branch[bad,1]=np.interp(branch[bad,0],src[:,0],src[:,1])
        xy=np.vstack([upper,lower]);label=Path(r['file']).stem+'_'+r['family']+'_'+str(r['side'])+'_'+str(abs(r['station_m']));path=out/(label+'.dat');np.savetxt(path,xy,header=label,comments='',fmt='%.10f')
        af=asb.Airfoil(name=label,coordinates=xy).normalize();fit=af.to_kulfan_airfoil();dense=fit.to_airfoil(n_coordinates_per_side=1500);dist=cKDTree(dense.coordinates).query(af.coordinates)[0]
        nf=fit.get_aero_from_neuralfoil(alpha=2.,Re=200000.,model_size='large')
        new.append(dict(r,file=str(path.relative_to(ROOT)),source_assembled_dat=r['file'],idealization_masks_chord=masks,idealization='linearly bridge observed servo-pocket/hinge interruptions; no underlying CAD modification; NOT as-built drag',fit_max_chord=float(max(dist)),fit_rms_chord=float(np.sqrt(np.mean(dist**2))),analysis_confidence=float(np.asarray(nf['analysis_confidence']).ravel()[0])))
    (out/'SECTIONS.json').write_text(json.dumps(new,indent=2));print(json.dumps([{'family':r['family'],'y':r['station_m'],'maxfit':r['fit_max_chord'],'conf':r['analysis_confidence']}for r in new],indent=2))
if __name__=='__main__':main()

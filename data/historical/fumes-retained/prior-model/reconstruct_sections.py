"""Reassemble source outer contours with explicit SEALED-HINGE approximation.
NOT a new CAD design, measured hinge performance, or generic airfoil replacement.
"""
from pathlib import Path
import numpy as np

def reconstruct(contours,n=601,max_gap_fraction=.025):
    # All inputs share ORIGINAL panel-section X-forward,Z-up coordinates in mm.
    from shapely.geometry import Polygon,LineString
    from shapely.ops import unary_union
    polys=[Polygon(np.asarray(c,float)) for c in contours]
    if not polys or not all(p.is_valid for p in polys):raise ValueError('invalid source contour')
    u=unary_union(polys);xmin,zmin,xmax,zmax=u.bounds
    chord=xmax-xmin
    if chord<=0:raise ValueError('zero chord')
    allpts=np.concatenate([np.asarray(c,float) for c in contours])
    le=allpts[np.argmax(allpts[:,0])];te=allpts[np.argmin(allpts[:,0])]
    xs=np.linspace(xmin,xmax,n);upper=[];lower=[]
    for x in xs:
        cut=u.intersection(LineString([(x,zmin-chord),(x,zmax+chord)]))
        if cut.is_empty:upper.append(np.nan);lower.append(np.nan);continue
        upper.append(cut.bounds[3]);lower.append(cut.bounds[1])
    upper=np.array(upper);lower=np.array(lower);valid=np.isfinite(upper)&np.isfinite(lower)
    gaps=np.flatnonzero(~valid)
    runs=np.split(gaps,np.where(np.diff(gaps)>1)[0]+1) if len(gaps) else []
    gap=max([len(r)/(n-1) for r in runs]+[0.])
    if gap>max_gap_fraction:raise ValueError(f'large unsupported contour gap {gap:.3%}')
    if valid.sum()<20:raise ValueError('insufficient source outline')
    upper=np.interp(xs,xs[valid],upper[valid]);lower=np.interp(xs,xs[valid],lower[valid])
    xf=(xmax-xs)/chord;line=le[1]+(te[1]-le[1])*xf
    # xs runs trailing edge->leading edge; upper first, then lower reverse.
    xy=np.vstack([np.column_stack([xf,(upper-line)/chord]),np.column_stack([xf[-2::-1],((lower-line)/chord)[-2::-1]])])
    meta=dict(chord_mm=float(chord),missing_x_fraction=float((~valid).mean()),maximum_gap_fraction=float(gap),hinge_sealing_approximation=len(polys)>1,source_parts=len(polys),incidence_deg=float(np.degrees(np.arctan2(le[1]-te[1],chord))),LE_local_xz_m=(le*.001).tolist(),TE_local_xz_m=(te*.001).tolist(),method='original-coordinate outer upper/lower envelope; short hinge gaps linearly sealed; no internal ribs exported')
    return xy,meta

def main():
    import json
    root=Path(__file__).resolve().parent;g=json.loads((root/'geometry/GEOMETRY.json').read_text());out=root/'assembled-sections';out.mkdir(exist_ok=True)
    groups={}
    for r in g['airfoils']:groups.setdefault((r['family'],r['side'],r['station_m']),[]).append(r)
    rows=[]
    import aerosandbox as asb
    from scipy.spatial import cKDTree
    for key,parts in sorted(groups.items()):
        xy,meta=reconstruct([r['source_xy_outline_mm'] for r in parts]);label=f'{key[0]}_{key[1]}_{abs(key[2]):.3f}'
        path=out/(label+'.dat');np.savetxt(path,xy,header=label,comments='',fmt='%.10f')
        af=asb.Airfoil(name=label,coordinates=xy).normalize();fit=af.to_kulfan_airfoil();dense=fit.to_airfoil(n_coordinates_per_side=1500)
        dist=cKDTree(dense.coordinates).query(af.coordinates)[0]
        nf=fit.get_aero_from_neuralfoil(alpha=2.,Re=200000.,model_size='large')
        rows.append(dict(**meta,family=key[0],side=key[1],station_m=key[2],chord_m=meta['chord_mm']/1000,file=str(path.relative_to(root)),section_frame_rows=parts[0]['section_frame_rows'],parts=[r['part'] for r in parts],fit_rms_chord=float(np.sqrt(np.mean(dist**2))),fit_max_chord=float(max(dist)),analysis_confidence=float(np.asarray(nf['analysis_confidence']).ravel()[0]),max_thickness_chord=float(af.max_thickness())))
    (out/'SECTIONS.json').write_text(json.dumps(rows,indent=2));print(json.dumps({'count':len(rows),'worst_fit_max_chord':max(r['fit_max_chord'] for r in rows),'minimum_confidence':min(r['analysis_confidence']for r in rows),'rows':rows},indent=2))
if __name__=='__main__':main()

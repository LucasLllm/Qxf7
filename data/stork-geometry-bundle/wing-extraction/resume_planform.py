"""Dense-only resume. Never executes the retained profile/neutral batch.
All output paths are anchored here. Physical CAD inputs are read-only.
"""
from pathlib import Path
import ast, json, hashlib, sys, csv, platform
import numpy as np
from shapely.geometry import Polygon
from shapely.ops import unary_union
from scipy.integrate import trapezoid
D=Path(__file__).resolve().parent
# Import/function definitions only: excludes every original top-level batch,
# mkdir, authorization write, and results write. Imported compare/probe have guards.
tree=ast.parse((D/'extract_wing.py').read_text())
helper={'__file__':str(D/'extract_wing.py')}
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[]),str(D/'extract_wing.py'),'exec'),helper)
helper['OUT']=D
C=helper['C']; P=D.parent

def sampled_wire(w, step=.01):
    # Batch parameter sampling avoids repeated arc-length inversion per point.
    curve=w._geomAdaptor()
    n=max(2000,int(w.Length()/step))
    return np.array([(lambda p:(p.X(),p.Y(),p.Z()))(curve.Value(float(t))) for t in np.linspace(curve.FirstParameter(),curve.LastParameter(),n)])

step_meshes={};section_methods={}

def tessellation_loops(name,y,tolerance=.0025):
    c=C[name];key=(name,tolerance)
    if key not in step_meshes:
        solid=helper['cache'][(c['source']['path'],c['features'].get('physical_solid_1_based',1))]
        v,f=solid.tessellate(tolerance,.05)
        m=helper['trimesh'].Trimesh(vertices=np.array([p.toTuple() for p in v]),faces=np.array(f),process=True)
        m.apply_transform(np.array(c['native_to_assembly_native_4x4']))
        assert m.is_watertight,(name,'STEP tessellation not watertight')
        step_meshes[key]=m
    sec=step_meshes[key].section(plane_origin=[y,0,0],plane_normal=[1,0,0])
    assert sec is not None,(name,y,'no tessellated section')
    return [p[:,[2,1]] for p in sec.discrete]

def section_loops(name,y):
    c=C[name]
    if c['source']['format']!='STEP':
        section_methods[(name,y)]={'section_method':'original_STL_section'}
        return helper['loops'](name,y)
    cq=helper['cq'];cache=helper['cache']; key=(c['source']['path'],c['features'].get('physical_solid_1_based',1))
    if key not in cache:cache[key]=cq.importers.importStep(key[0]).solids().vals()[key[1]-1]
    op=helper['BRepAlgoAPI_Section'](cache[key].wrapped,helper['gp_Pln'](helper['gp_Pnt'](-y,0,0),helper['gp_Dir'](1,0,0)),False)
    op.Approximation(True);op.Build();T=np.array(c['native_to_assembly_native_4x4']);out=[]
    for w in cq.Wire.combine(cq.Shape.cast(op.Shape()).Edges(),tol=1e-5):
        a=sampled_wire(w);a=a@T[:3,:3].T+T[:3,3];out.append(a[:,[2,1]])
    if 'aileron' not in name and out and all(np.linalg.norm(p[0]-p[-1])<.05 for p in out):
        section_methods[(name,y)]={'section_method':'physical_STEP_exact_section','exact_vs_tessellation_extrema_max_mm':None,'fallback_reason':None}
        return out
    meshloops=tessellation_loops(name,y)
    a=np.vstack(out) if out else None;b=np.vstack(meshloops)
    delta=None if a is None else float(np.max(np.abs(np.r_[a.min(0),a.max(0)]-np.r_[b.min(0),b.max(0)])))
    fallback=not out or any(np.linalg.norm(p[0]-p[-1])>=.05 for p in out) or delta>.02
    section_methods[(name,y)]={'section_method':'physical_STEP_tessellation_0.0025mm_fallback' if fallback else 'physical_STEP_exact_section','exact_vs_tessellation_extrema_max_mm':delta,'fallback_reason':'open or missing/incomplete exact intersection' if fallback else None}
    return meshloops if fallback else out

def design_loop(y):
    op=helper['BRepAlgoAPI_Section'](helper['natural'].wrapped,helper['gp_Pln'](helper['gp_Pnt'](-y,0,0),helper['gp_Dir'](1,0,0)),False)
    op.Approximation(True);op.Build()
    pts=[sampled_wire(e)[:,[2,1]] for e in helper['cq'].Shape.cast(op.Shape()).Edges()]
    p=max(pts,key=len);return np.vstack([p,p[0]])

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def physical_section(y):
    """Union every nonnested closed component exterior, not only largest loop.
    Nested holes cannot change projection extrema/coverage. Never connect islands.
    """
    polygons=[]; audits=[]; allpoints=[]
    for name,c in C.items():
        if 'plate' in name or not c['bounds_native_mm'][0][0]+1e-7<y<c['bounds_native_mm'][1][0]-1e-7:
            continue
        ls=section_loops(name,y)
        if not ls:
            raise AssertionError((name,y,'no section loops'))
        ps=[]
        for l in ls:
            assert np.linalg.norm(l[0]-l[-1])<.05,(name,y,'open loop')
            poly=Polygon(l)
            if not poly.is_valid:
                # Ordered CAD wire sampling can leave a zero-area closure spur.
                # Topological repair only; reject any significant area change.
                from shapely import make_valid
                fixed=make_valid(poly)
                parts=[g for g in getattr(fixed,'geoms',[fixed]) if g.geom_type in ('Polygon','MultiPolygon')]
                fixed=unary_union(parts)
                assert not fixed.is_empty and abs(fixed.area-poly.area)<1e-6*max(poly.area,1),(name,y,'nontrivial invalid polygon')
                poly=fixed
            ps.append(poly)
        # Full-polygon containment, never representative-point-only testing.
        outer=[i for i,p in enumerate(ps) if not any(j!=i and q.area>p.area and q.buffer(1e-6).covers(p) for j,q in enumerate(ps))]
        polygons.extend(ps[i] for i in outer)
        allpoints.extend(ls[i] for i in outer)
        audits.append({'component':name,'loop_count':len(ls),'outer_loop_count':len(outer),'nested_holes_ignored':len(ls)-len(outer),'strict_single_outer_profile_compatible':len(outer)==1,**section_methods[(name,y)]})
    assert polygons,('empty physical station',y)
    union=unary_union(polygons)
    # Projection of union: gaps remain gaps; no hull, gap-filling, or skin inference.
    islands=list(union.geoms) if union.geom_type=='MultiPolygon' else [union]
    intervals=sorted((p.bounds[0],p.bounds[2]) for p in islands)
    merged=[]
    for a,b in intervals:
        if merged and a<=merged[-1][1]+1e-9: merged[-1][1]=max(merged[-1][1],b)
        else: merged.append([a,b])
    q=np.vstack(allpoints); xmin=float(q[:,0].min()); xmax=float(q[:,0].max())
    assert abs(union.bounds[0]-xmin)<1e-7 and abs(union.bounds[2]-xmax)<1e-7
    le=q[q[:,0].argmin()];te=q[q[:,0]>xmax-.05]
    width=sum(b-a for a,b in merged)
    return {'y':float(y),'xmin':xmin,'xmax':xmax,'leup':float(le[1]),'teup':float((te[:,1].min()+te[:,1].max())/2),'projected_occupied_width':float(width),'unoccupied_x_gap_mm':float(xmax-xmin-width),'projected_intervals':merged,'audit':audits,'all_loop_extrema_retained':True}

def metrics(a, width_column=None):
    y=a[:,0];c=a[:,2]-a[:,1] if width_column is None else a[:,width_column]
    A=trapezoid(c,y); mac=trapezoid(c*c,y)/A
    qc=trapezoid((a[:,1]+.25*(a[:,2]-a[:,1]))*c,y)/A
    return {'both_sides_projected_area_dm2':float(2*A/1e4),'projected_MAC_mm':float(mac),'MAC_LE_aft_mm':float(qc-.25*mac),'quarterchord_aft_mm':float(qc),'right_MAC_area_weighted_y_mm':float(trapezoid(y*c,y)/A),'area_weighted_quarterchord_up_mm':float(trapezoid((.75*a[:,3]+.25*a[:,4])*c,y)/A)}

def main():
    assert json.loads((P/'extraction_authorization.json').read_text())['status'].startswith('AUTHORIZED')
    inputs=[P/'wing_assembly.json',P/'extraction_authorization.json',P/'reference-assembly/assembly_manifest.json',P/'inspect_wing_features.py',P.parent/'source-format-audit/cad_inventory.csv']+[Path(p) for p in sorted({c['source']['path'] for c in C.values()})]
    pre={str(p):sha(p) for p in inputs}
    for c in C.values():assert pre[c['source']['path']]==c['source']['sha256']
    retained=[D/'sections.csv',D/'sections.json',D/'neutral_investigation.json',D/'panel_rates.json',*sorted((D/'dat').glob('*.dat')),*sorted((D/'raw').glob('*.npz')),*sorted((D/'plots').glob('*.png'))]
    keep={str(p):sha(p) for p in retained}
    root=92.; tip=max(c['bounds_native_mm'][1][0] for n,c in C.items() if 'plate' not in n)
    eps=.0001; lo=root+eps;hi=tip-eps
    cuts=[260.15695513675854,318.,449.8,524.,589.6,729.4,730.]
    cuts+= [float(c['bounds_native_mm'][i][0]) for c in C.values() for i in (0,1)]
    breaks=sorted(set(v for v in cuts if lo<v<hi))
    # Matched grids plus two-sided discontinuity probes; each refinement includes
    # identical exact endpoints and break probes. 3/1.5/.75 mm, not p[::2].
    common=np.r_[lo,hi,563.02,449.78,449.82,729.38,729.42,729.98,730.02,*[v+d for v in breaks for d in (-.001,.001) if lo<v+d<hi]]
    grids=[np.unique(np.round(np.r_[np.arange(lo,hi,h),common],9)) for h in (3.,1.5,.75)]
    ys=np.unique(np.concatenate(grids)); samples={};physical=[]; hybrid=[]
    cache_path=D/'dense_checkpoint.json'
    cache_key=sha(__file__)+hashlib.sha256(json.dumps(pre,sort_keys=True).encode()).hexdigest()
    checkpoint=json.loads(cache_path.read_text()) if cache_path.exists() else {}
    saved=checkpoint.get('samples',{}) if checkpoint.get('key')==cache_key else {}
    for i,y in enumerate(ys):
        key=str(float(y))
        if key in saved:
            r,row,refrow=saved[key]
        else:
            r=physical_section(float(y))
            row=[y,r['xmin'],r['xmax'],r['leup'],r['teup'],r['projected_occupied_width']]
            refrow=row
            if y<=318:
                p=design_loop(float(y));x0=p[:,0].min();x1=p[:,0].max();le=p[p[:,0].argmin(),1];q=p[p[:,0]>x1-.05];te=.5*(q[:,1].min()+q[:,1].max())
                refrow=[float(y),float(x0),float(x1),float(le),float(te),float(x1-x0)]
            saved[key]=[r,row,refrow]
        samples[float(y)]=r;physical.append(row);hybrid.append(refrow)
        if i%50==0:
            cache_path.write_text(json.dumps({'key':cache_key,'samples':saved}))
            print('DENSE',i,len(ys),'y',y,flush=True)
    cache_path.write_text(json.dumps({'key':cache_key,'samples':saved}))
    physical=np.array(physical);hybrid=np.array(hybrid)
    idx={float(y):i for i,y in enumerate(ys)}
    def at(a,g):return a[[idx[float(y)] for y in g]]
    convergence=[]
    for h,g in zip((3.,1.5,.75),grids):
        p=at(hybrid,g); ph=at(physical,g)
        gross=np.vstack([np.r_[0.,p[0,1:]],np.r_[root,p[0,1:]],p])
        convergence.append({'nominal_step_mm':h,'stations':len(g),'exposed':metrics(p),'gross':metrics(gross),'physical_outer_envelope_exposed':metrics(ph),'physical_occupied_projection_both_sides_dm2':float(2*trapezoid(ph[:,5],ph[:,0])/1e4)})
    last=convergence[-1];prev=convergence[-2]
    deltas={k:abs(last['exposed'][k]-prev['exposed'][k]) for k in ('both_sides_projected_area_dm2','projected_MAC_mm','quarterchord_aft_mm')}
    converged=deltas['both_sides_projected_area_dm2']<.01 and deltas['projected_MAC_mm']<.1 and deltas['quarterchord_aft_mm']<.1
    assert converged,('refine grid',deltas)
    sections=json.loads((D/'sections.json').read_text());station_diagnostics=[];profilechecks={}
    for s in sections:
        tag=s['section_id'];y=s['station_y_mm'];raw=np.load(D/'raw'/f'{tag}.npz');dat=np.loadtxt(D/'dat'/f'{tag}.dat',skiprows=1)
        gu=raw['dense_x_c'];u=raw['upper_y_c'];l=raw['lower_y_c'];poly=Polygon(dat)
        upper=np.interp(gu,dat[:70,0][::-1],dat[:70,1][::-1]);lower=np.interp(gu,np.r_[0,dat[70:,0]],np.r_[0,dat[70:,1]])
        err=np.r_[upper-u,lower-l]*s['chord_mm']
        profilechecks[tag]={'points':len(dat),'finite':bool(np.isfinite(dat).all()),'LE_origin':bool(np.all(dat[69]==0)),'upper_TE_to_LE':bool(np.all(np.diff(dat[:70,0])<0)),'lower_LE_to_TE':bool(np.all(np.diff(dat[69:,0])>0)),'TE_x_one':bool(dat[0,0]==dat[-1,0]==1),'non_self_intersecting':bool(poly.is_valid and poly.exterior.is_simple),'nonnegative_thickness':bool((u-l).min()>-1e-8),'reconstruction_max_mm':float(abs(err).max()),'reconstruction_rms_mm':float(np.sqrt(np.mean(err**2))),'aerodynamic_certification':False}
        if y<root:continue
        r=physical_section(y);d={'section_id':tag,'station_y_mm':y,'retained_contour_chord_norm_mm':s['chord_mm'],'physical_outer_extreme_projected_chord_mm':r['xmax']-r['xmin'],'unoccupied_x_gap_mm':r['unoccupied_x_gap_mm'],'strict_single_outer_profile_compatible':all(a['strict_single_outer_profile_compatible'] for a in r['audit']),'source_audit':r['audit']}
        if y<730:
            pp=design_loop(y); dm=helper['normalize'](pp)[0]
            d['underlying_design_support_chord_norm_mm']=dm['chord_mm'];d['retained_minus_design_chord_mm']=s['chord_mm']-dm['chord_mm']
            d['physical_TE_extreme_aft_mm']=r['xmax'];d['design_support_TE_aft_mm']=dm['TE_aft_mm']
            d['missing_aft_domain_relative_design_mm']=max(0.,dm['TE_aft_mm']-r['xmax'])
            d['diagnostic_note']='Zero unoccupied_x_gap refers only to intervals INSIDE retained extrema; it does not exclude absent aft skin outside that measured domain.'
            if abs(d['retained_minus_design_chord_mm'])>2:
                cleaner=min((q for q in sections if q['section_id']!=tag and abs(q['station_y_mm']-y)<5 and abs(q['chord_mm']-dm['chord_mm'])<2),key=lambda q:abs(q['station_y_mm']-y),default=None)
                d.update(flag='CONTROL_CLEARANCE_TRUNCATED_CONTOUR_NOT_LOCAL_AERODYNAMIC_CHORD',missing_skin_not_invented=True,nearest_cleaner_retained_section=None if cleaner is None else {'section_id':cleaner['section_id'],'station_y_mm':cleaner['station_y_mm'],'chord_norm_mm':cleaner['chord_mm'],'delta_y_mm':cleaner['station_y_mm']-y})
        station_diagnostics.append(d)
    for name,ch in profilechecks.items():
        assert ch['points']==140 and all(ch[k] for k in ('finite','LE_origin','upper_TE_to_LE','lower_LE_to_TE','TE_x_one','non_self_intersecting','nonnegative_thickness')),(name,ch)
    assert any(s.get('flag') for s in station_diagnostics if s['section_id']=='aileron_start_in')
    nonnested=[{'station_y_mm':r['y'],'components':[a for a in r['audit'] if a['outer_loop_count']>1]} for r in samples.values() if any(a['outer_loop_count']>1 for a in r['audit'])]
    fallback_stations=[{'station_y_mm':r['y'],'components':[a for a in r['audit'] if a['section_method'].startswith('physical_STEP_tessellation')]} for r in samples.values() if any(a['section_method'].startswith('physical_STEP_tessellation') for a in r['audit'])]
    tessellation_checks=[]
    for name,y in [('right_aileron_1',563.02),('right_aileron_2',650.),('right_aileron_2',693.5001),('right_aileron_2',700.)]:
        section_loops(name,y)
        a=np.vstack(tessellation_loops(name,y,.0025));b=np.vstack(tessellation_loops(name,y,.00125))
        delta=float(np.max(np.abs(np.r_[a.min(0),a.max(0)]-np.r_[b.min(0),b.max(0)])))
        assert delta<.01,(name,y,'tessellation refine',delta)
        tessellation_checks.append({'component':name,'station_y_mm':y,'tolerances_mm':[.0025,.00125],'extrema_max_delta_mm':delta,'passed_lt_0p01mm':True})
    geometry={'datum':'Untranslated common STEP origin: aircraft x=native Z aft, y=transformed native X right, z=native Y up. Right mirrored to left; left not independently measured.','exposed_root_y_mm':root,'right_outer_y_mm':tip,'span_mm':2*tip,'integrated_y_limits_mm':[lo,hi],'exposed':last['exposed'],'gross_with_declared_centerline_continuation':last['gross'],'gross_convention':'Artificial rectangular continuation of first inboard design-support envelope at y=92.0001 to centerline y=0; exposed root nominal y=92. No hidden-wing evidence. No plates added. Bilateral symmetry assumed.','planform_convention':'Reference envelope only: original untrimmed STEP BSpline support at y<=318; physical closed-loop union extrema at y>318. x-extreme projected chord, not chord-line norm. Includes empty chordwise gaps inside extrema by explicit envelope convention, NOT evidence of skin. MAC=int(c^2 dy)/int(c dy), x_qc=int((xmin+c/4)c dy)/int(c dy); MAC_LE=x_qc-MAC/4. y is area centroid, not unique location where local chord equals MAC. z_qc uses extrema midpoint proxy, not skin-area centroid.','physical_outer_envelope_exposed':last['physical_outer_envelope_exposed'],'physical_occupied_projection_both_sides_dm2':last['physical_occupied_projection_both_sides_dm2'],'physical_projection_convention':'Every nonnested exterior union; chordwise projection intervals retain gaps. Nested holes ignored because projection of exterior shell is requested. Occupied projection is not skin wetted area. No aerodynamic MAC assigned to disjoint occupied intervals.','convergence':convergence,'last_refinement_absolute_deltas':deltas,'convergence_passed':converged,'end_slivers_omitted_each_mm':eps,'end_sliver_area_conservative_bound_both_sides_dm2':float(4*eps*np.max(hybrid[:,2]-hybrid[:,1])/1e4),'true_tip_airfoil':None,'true_tip_reason':'Curved upturned cap, constant-y sections oblique diagnostics; no conventional span-normal tip foil certified.','physical_winglet_camber_incidence':None,'neutral_certified':False,'station_diagnostics_file':'station_diagnostics.json'}
    np.savetxt(D/'planform_samples.csv',hybrid,delimiter=',',header='y_mm,LE_extreme_aft_mm,TE_extreme_aft_mm,LE_extreme_up_mm,TE_mid_up_mm,reference_envelope_width_mm',comments='')
    np.savetxt(D/'physical_planform_samples.csv',physical,delimiter=',',header='y_mm,LE_extreme_aft_mm,TE_extreme_aft_mm,LE_extreme_up_mm,TE_mid_up_mm,occupied_projection_width_mm',comments='')
    (D/'station_diagnostics.json').write_text(json.dumps({'stations':station_diagnostics,'dense_nonnested_stations':nonnested,'dense_STEP_tessellation_fallbacks':fallback_stations,'tessellation_refinement_checks':tessellation_checks},indent=2))
    (D/'wing_geometry.json').write_text(json.dumps(geometry,indent=2))
    post={str(p):sha(p) for p in inputs};assert pre==post
    assert keep=={str(p):sha(p) for p in retained}
    verification={'all_original_input_hashes_unchanged':pre==post,'inputs_sha256':pre,'retained_artifacts_unchanged':True,'retained_artifact_sha256':keep,'retained_profile_count':len(profilechecks),'sections':profilechecks,'all_section_numeric_format_tests_passed':True,'all_profiles_aerodynamically_certified':False,'profile_station_warnings_preserved':True,'strict_groups_unchanged':True,'dense_nonnested_station_count':len(nonnested),'convergence_passed':converged,'last_refinement_absolute_deltas':deltas,'outputs_sha256':{p.name:sha(p) for p in [D/'wing_geometry.json',D/'station_diagnostics.json',D/'planform_samples.csv',D/'physical_planform_samples.csv']},'python':sys.version,'platform':platform.platform(),'notes':['27 profiles reused, never regenerated. Numeric format passing does not certify recovered skin or aerodynamic chord.','Original extraction.log failure retained; run resume_planform.py, not extract_wing.py, to resume.','Both unoccupied physical gaps and design-support provenance remain explicit; no interpolation creates missing skin.']}
    (D/'verification.json').write_text(json.dumps(verification,indent=2))
    print('COMPLETE',json.dumps({'exposed':last['exposed'],'gross':last['gross'],'physical_occupied_area_dm2':last['physical_occupied_projection_both_sides_dm2'],'convergence_deltas':deltas,'nonnested_stations':len(nonnested),'flagged_stations':[s['section_id'] for s in station_diagnostics if s.get('flag')]}),flush=True)

if __name__=='__main__':main()

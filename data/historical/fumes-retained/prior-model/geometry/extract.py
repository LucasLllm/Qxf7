"""Read-only source extraction; all writes next to this script. Coordinates initially mm."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'deps'))
import numpy as np
from shapely.geometry import LineString, Polygon
from shapely.ops import polygonize, unary_union

def outer_contour(segments):
    # Round endpoint discrepancies only (1e-5 mm), never bridge missing geometry.
    segments=np.round(np.asarray(segments,float),5)
    lines=[LineString(s) for s in segments if np.linalg.norm(s[1]-s[0])>1e-9]
    polygons=list(polygonize(unary_union(lines)))
    if not polygons: return None,{'status':'no_closed_contour','retained_outer_contours':0}
    union=unary_union(polygons)
    components=list(union.geoms) if hasattr(union,'geoms') else [union]
    largest=max(components,key=lambda p:p.area)
    # Exterior only; all nested ribs, inner skins and holes removed explicitly.
    exterior=Polygon(largest.exterior)
    return exterior,{'status':'closed','polygonized_cells':len(polygons),'disconnected_components':len(components),'retained_outer_contours':1,'discarded_component_areas_mm2':[p.area for p in components if p!=largest],'endpoint_quantization_mm':1e-5}

import json, hashlib, importlib.util, time
import trimesh
import cadquery as cq
from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
from OCP.gp import gp_Pln, gp_Pnt, gp_Dir
from scipy.spatial import ConvexHull

ROOT=Path('/Users/lucasliu/.hermes/profiles/fumes')
OUT=Path(__file__).resolve().parent
BASE=ROOT/'notes/stork-development'
ORIG=BASE/'source-format-audit/originals'
MAN=BASE/'showcase/hybrid-v2-final/assembly-manifest.json'
PRIOR=BASE/'performance-scenarios/range-first/geometry-placement/wing-evidence/wing-results.json'
HELPER=PRIOR.parent/'measure_wing.py'
spec=importlib.util.spec_from_file_location('prior_wing',HELPER)
winghelper=importlib.util.module_from_spec(spec);spec.loader.exec_module(winghelper)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def source_mesh(row):
    p=ORIG/row['pack']/row['source_stl']
    assert sha(p)==row['source_sha256']
    mesh=trimesh.load_mesh(p,process=False)
    matrix=np.asarray(row['source_to_assembly_mm'])
    assert np.allclose(matrix[:3,:3].T@matrix[:3,:3],np.eye(3),atol=1e-9)
    mesh.vertices=winghelper.transform(mesh.vertices,matrix)
    return mesh

CAD={}
def section_segments(row,normal,distance,mesh):
    if row.get('representation')=='original_STEP_BRep':
        p=ORIG/row['pack']/row['source_step']
        assert sha(p)==row['source_step_sha256']
        if str(p) not in CAD:CAD[str(p)]=cq.importers.importStep(str(p)).solids().vals()
        body=CAD[str(p)][row['step_body_index']-1]
        assert body.isValid()
        t=np.array(row['step_to_assembly_mm']);n=t[:3,:3].T@normal
        d=distance-normal@t[:3,3];origin=n*d
        alg=BRepAlgoAPI_Section(body.wrapped,gp_Pln(gp_Pnt(*origin),gp_Dir(*n)),False);alg.Build()
        assert alg.IsDone()
        shape=cq.Shape.cast(alg.Shape());segments=[]
        for edge in shape.Edges():
            count=2 if edge.geomType()=='LINE' else max(33,int(edge.Length()/.3)+1)
            samples,parameters=edge.sample(count)
            pts=np.array([p.toTuple() for p in samples])
            if edge.IsClosed():pts=np.vstack([pts,pts[0]])
            pts=winghelper.transform(pts,t)
            segments.extend(np.stack([pts[:-1],pts[1:]],axis=1))
        return np.array(segments).reshape(-1,2,3),'original_STEP_BRep_curve_sample'
    seg=trimesh.intersections.mesh_plane(mesh,normal,normal*distance)
    return seg,'original_STL_triangle_intersection'

def normalize_airfoil(poly):
    p=np.asarray(poly.exterior.coords)[:-1]
    le=p[np.argmax(p[:,0])];te=p[np.argmin(p[:,0])]
    direction=te-le;chord=np.linalg.norm(direction)
    direction=direction/chord
    upward=np.array([direction[1],-direction[0]])
    if upward[1]<0:upward=-upward
    xy=np.column_stack([(p-le)@direction/chord,(p-le)@upward/chord])
    first=np.argmin(p[:,0]);xy=np.roll(xy,-first,axis=0)
    # TE -> upper -> LE -> lower -> TE, preserve actual single exterior.
    if xy[1:min(10,len(xy)),1].mean()<xy[-min(10,len(xy)):,1].mean():
        xy=np.vstack([xy[:1],xy[:0:-1]])
    xy=np.vstack([xy,xy[0]])
    # Similarity normalization after rotation: retain every source outline point.
    # A blunt/rounded TE can project beyond the endpoint used for the chordline.
    # Normalize the actual rotated chordwise extent rather than clipping points.
    xmin=xy[:,0].min();xspan=np.ptp(xy[:,0])
    xy[:,0]=(xy[:,0]-xmin)/xspan;xy[:,1]/=xspan
    return xy,le,te,chord*xspan

def main():
    start=time.time();rows=json.loads(MAN.read_text())['rows'];prior=json.loads(PRIOR.read_text())
    # Verify all retained wing inputs and binding to current source manifest.
    assert sha(MAN)==prior['manifest_sha256']
    for r in prior['provenance']:assert sha(Path(r['source_original_stl']))==r['source_sha256']
    physical=[r for r in rows if r.get('source_stl') and not r['name'].startswith('PROXY ')]
    meshes={r['name']:source_mesh(r) for r in physical}
    sources={str(p):{'path':str(p),'sha256':sha(p)} for p in [MAN,PRIOR,HELPER]}
    components=[]
    for r in physical:
        mesh=meshes[r['name']];bounds=mesh.bounds
        for key in ['source_stl','source_step']:
            if r.get(key):
                p=ORIG/r['pack']/r[key];sources[str(p)]={'path':str(p),'sha256':sha(p)}
        components.append({'name':r['name'],'source_stl':str(ORIG/r['pack']/r['source_stl']),
         'source_step':str(ORIG/r['pack']/r['source_step']) if r.get('source_step') else None,
         'physical_step_body_index':r.get('step_body_index'),'representation':r['representation'],
         'source_to_assembly_m':(np.array(r['source_to_assembly_mm'])*np.array([[1,1,1,.001]]*3+[[1,1,1,1]])).tolist(),
         'step_to_assembly_m':(np.array(r['step_to_assembly_mm'])*np.array([[1,1,1,.001]]*3+[[1,1,1,1]])).tolist() if r.get('step_to_assembly_mm') else None,
         'bounds_m':(bounds*.001).tolist(),'dimensions_m':(np.ptp(bounds,axis=0)*.001).tolist(),
         'placement_confidence':r['placement_basis'],
         'external_wetted_area_m2':None,'exposure_status':'not independently clipped against installed neighbors'})
    wingrows=[r for r in physical if r['name'].startswith(('WING 1.','WING 2 ','WING 3 ','WINGTIP 3 ','AIILERON ','AILERON '))]
    tailrows=[r for r in physical if r['name'].startswith(('V TAIL ','RUDEER ','RUDDER '))]
    # Fit a single canted reference plane to left panel's original transformed vertices.
    left=np.concatenate([meshes[r['name']].vertices for r in tailrows if r['name'].endswith(' L')])
    yz=left[:,1:];eigenvalues,eigenvectors=np.linalg.eigh(np.cov(yz.T));u=eigenvectors[:,-1]
    if u[0]<0:u=-u
    cant=float(np.degrees(np.arctan2(u[1],u[0])))
    tail_frames={}
    for side in [-1,1]:
        span=np.array([0,side*u[0],u[1]]);height=np.array([0,-side*u[1],u[0]])
        tail_frames[side]=np.array([[1,0,0],span,height])
    area_runs=[]
    for step in [1,.5,.25]:
        total=0.;panels=[]
        for side in [-1,1]:
            frame=tail_frames[side]
            tris=[meshes[r['name']].triangles@frame.T for r in tailrows if r['name'].endswith(' L' if side==1 else ' R')]
            a=winghelper.projected_area(tris,step);total+=a['exposed_projected_union_mm2']
            panels.append({'side':side,'area_m2':a['exposed_projected_union_mm2']*1e-6,'span_coordinate_range_m':(np.array(a['sides'][0]['y_limits_mm'])*.001).tolist()})
        area_runs.append({'step_m':step*.001,'area_m2':total*1e-6,'panels':panels})
    # Section each side in its panel frame; combine fixed/control intersections for planform,
    # but export each true closed exterior separately, never fill hinge gaps.
    stations=[];foils=[];missing=[]
    for family,selected,values in [('wing',wingrows,[100,200,280,400,500,600,700,760]),('tail',tailrows,[60,120,180,240,280])]:
      for side in [-1,1]:
        frame=np.eye(3) if family=='wing' else tail_frames[side]
        for distance in values:
            d=side*distance if family=='wing' else distance
            normal=frame[1];allpoints=[];parts=[];polyrecords=[]
            for r in selected:
                if family=='tail' and not r['name'].endswith(' L' if side==1 else ' R'):continue
                mesh=meshes[r['name']];projected=mesh.vertices@normal
                if not projected.min()<d<projected.max():continue
                seg,method=section_segments(r,normal,d,mesh)
                if not len(seg):continue
                local=seg@frame.T;points=local.reshape(-1,3);allpoints.append(points)
                parts.append(r['name'])
                poly,diag=outer_contour(local[:,:,[0,2]])
                raw_chord=np.ptp(points[:,0])
                coverage=np.ptp(np.asarray(poly.exterior.coords)[:,0])/raw_chord if poly is not None and raw_chord else 0
                native_failure=None
                if poly is None or coverage<.98:
                    native_failure={'method':method,'reason':'closed loop does not cover physical part chord; may be internal contour','outline_chord_coverage_ratio':float(coverage),'raw_chord_m':raw_chord*.001,**diag}
                    if method.startswith('original_STEP'):
                        # Original native RUDDER body has an open exterior at these planes.
                        # Physical-source fallback only; no sewing/bridging/repair of CAD.
                        seg=trimesh.intersections.mesh_plane(mesh,normal,normal*d)
                        local=seg@frame.T;points=local.reshape(-1,3)
                        poly,diag=outer_contour(local[:,:,[0,2]])
                        method='original_STL_native_outer_contour_gap_fallback'
                        raw_chord=np.ptp(points[:,0]) if len(points) else 0
                        coverage=np.ptp(np.asarray(poly.exterior.coords)[:,0])/raw_chord if poly is not None and raw_chord else 0
                        # Planform extrema reflect the physically complete source fallback.
                        allpoints[-1]=points
                if poly is None or coverage<.98:
                    missing.append({'family':family,'side':side,'station_m':d*.001,'part':r['name'],'outline_chord_coverage_ratio':float(coverage),'native_failure':native_failure,**diag});continue
                xy,le,te,chord=normalize_airfoil(poly)
                if chord<5:
                    missing.append({'family':family,'side':side,'station_m':d*.001,'part':r['name'],'reason':'profile chord below 5 mm'});continue
                label=f'{family}_{"L" if side==1 else "R"}_{distance:03d}_{r["instance_index"]:03d}'
                path=OUT/'airfoils'/label/'airfoil.dat';path.parent.mkdir(parents=True,exist_ok=True)
                np.savetxt(path,xy,header=label,comments='',fmt='%.10f')
                entry={'file':str(path.relative_to(OUT)),'family':family,'side':side,'station_m':d*.001,'part':r['name'],
                    'method':method,'profile_scope':'single physical part; not a bridged fixed/control profile',
                    'chord_m':chord*.001,'source_outline_area_mm2':poly.area,
                    'internal_contours_exported':0,'source_xy_outline_mm':np.asarray(poly.exterior.coords).tolist(),
                    'outline_chord_coverage_ratio':float(coverage),'native_failure':native_failure,
                    'section_frame_rows':frame.tolist(),'LE_local_xz_m':(le*.001).tolist(),'TE_local_xz_m':(te*.001).tolist(),
                    'incidence_deg':float(np.degrees(np.arctan2(le[1]-te[1],le[0]-te[0]))),**diag}
                foils.append(entry);polyrecords.append(entry)
            if allpoints:
                points=np.concatenate(allpoints);le=points[np.argmax(points[:,0])];te=points[np.argmin(points[:,0])]
                stations.append({'family':family,'side':side,'station_m':d*.001,'LE_local_m':(le*.001).tolist(),
                    'TE_local_m':(te*.001).tolist(),'LE_assembly_m':(le@frame*.001).tolist(),'TE_assembly_m':(te@frame*.001).tolist(),
                    'chord_envelope_m':(le[0]-te[0])*.001,'incidence_chordline_deg':float(np.degrees(np.arctan2(le[2]-te[2],le[0]-te[0]))),
                    'quarter_chord_x_m':float((.75*le[0]+.25*te[0])*.001),'parts':parts,'closed_part_profiles':len(polyrecords),
                    'combined_airfoil_file':None if len(parts)>1 else (polyrecords[0]['file'] if polyrecords else None),
                    'combined_profile_status':'separate physical contours; no gap filling' if len(parts)>1 else 'single physical part'})
    for family in ['wing','tail']:
      for side in [-1,1]:
        group=sorted([s for s in stations if s['family']==family and s['side']==side],key=lambda s:abs(s['station_m']))
        if not group:continue
        for i,s in enumerate(group):
            s['twist_relative_inboard_deg']=s['incidence_chordline_deg']-group[0]['incidence_chordline_deg']
            if i:
                ds=abs(s['station_m'])-abs(group[i-1]['station_m'])
                s['LE_sweep_aft_deg']=float(np.degrees(np.arctan2(group[i-1]['LE_local_m'][0]-s['LE_local_m'][0],ds)))
                s['quarter_chord_sweep_aft_deg']=float(np.degrees(np.arctan2(group[i-1]['quarter_chord_x_m']-s['quarter_chord_x_m'],ds)))
            else:s['LE_sweep_aft_deg']=s['quarter_chord_sweep_aft_deg']=None
    fusrows=[r for r in physical if r['name'].startswith(('FUS 1','FUS 2','FUS 3','FUS 4','FUS 5','FUS 6','HATCH FRONT','HATCH MIDDLE')) or r['name']=='NOSE']
    fv=np.concatenate([meshes[r['name']].vertices for r in fusrows]);fb=np.array([fv.min(0),fv.max(0)])
    sections=[]
    for x in np.linspace(fb[0,0]+.1,fb[1,0]-.1,151):
        pts=[];names=[]
        for r in fusrows:
            mesh=meshes[r['name']]
            if not mesh.bounds[0,0]<x<mesh.bounds[1,0]:continue
            seg,method=section_segments(r,np.array([1.,0,0]),x,mesh)
            if len(seg):pts.append(seg.reshape(-1,3)[:,1:]);names.append(r['name'])
        if not pts:continue
        p=np.concatenate(pts)
        if len(p)<3:continue
        hull=ConvexHull(p);outer=p[hull.vertices];perimeter=np.linalg.norm(np.roll(outer,-1,axis=0)-outer,axis=1).sum()
        sections.append({'x_m':x*.001,'width_m':float(np.ptp(p[:,0])*.001),'height_m':float(np.ptp(p[:,1])*.001),
                         'outer_convex_perimeter_m':perimeter*.001,'convex_section_area_m2':hull.volume*1e-6,'parts':names})
    wetted=float(np.trapezoid([s['outer_convex_perimeter_m'] for s in sections],[s['x_m'] for s in sections]))
    hardware=[c for c in components if c['name'].startswith(('BOOM MOUNT','MOTOR MOUNT','MAIN SKIDS','FIN TIP','SERVO COVER','WING BOLT','LOCK'))]
    proxies=[{'name':r['name'],'dimensions_m':(np.ptp(np.array(r['bounds_mm']),axis=0)*.001).tolist(),'basis':r['placement_basis'],'use_as_actual_geometry':False} for r in rows if r['name'].startswith(('PROXY carbon boom','PROXY lift motor','PROXY pusher motor','PROXY pushrod'))]
    motor_spec=BASE/'performance-scenarios/range-first/worst-case/source-review/f90-spec.jpg'
    assert motor_spec.exists()
    sources[str(motor_spec)]={'path':str(motor_spec),'sha256':sha(motor_spec)}
    documented_motors=[{'model':'T-Motor F90','diameter_m':.0334,'listed_height_m':.0347,'shaft_diameter_m':.004,
      'source':str(motor_spec),'basis':'visually inspected retained manufacturer specification table; KV1300/1500/1950 rows identical dimensions',
      'height_scope':'table says motor dimensions, not isolated exposed bell height; shaft inclusion unresolved',
      'exposed_can_height_m':None,'installed_choice_verified':False,'confidence':'documentary dimensions, not installed measurement'}]
    result={'schema_version':'1.0','units':{'length':'m','area':'m2','angle':'deg','airfoil_DAT':'dimensionless x/c,z/c','diagnostic_source_xy':'mm'},
      'axes':{'+X':'forward','+Y':'left','+Z':'up'},'scenario':{'mass_kg':2.9837,'growth_separate_kg':.1,'payload_kg':0,'battery':'4S3P P50B 216Wh','geometry_configuration':'retained original 1.62m Stork4+1 assembly'},
      'sources':list(sources.values()),'components':components,
      'wing':{'span_m':prior['overall_wingspan_mm']*.001,'exposed_projected_union_area_m2':prior['area_runs'][-1]['exposed_projected_union_mm2']*1e-6,
       'reference_area_released_m2':None,'hypothetical_center_bridged_area_m2':prior['hypothetical_center_bridge']['bridged_union_mm2']*1e-6,
       'center_bridge_is_source_geometry':False,'integration_refinement_delta_m2':prior['integration_refinement_delta_mm2']*1e-6,
       'collar_inclusive_area_m2':prior['optional_root_collar_inclusive_area']['exposed_projected_union_mm2']*1e-6,
       'retained_full_planform_sections_SI':[{'y_m':s['y_mm']*.001,'LE_m':(np.array(s['LE_xyz_mm'])*.001).tolist(),'TE_m':(np.array(s['TE_xyz_mm'])*.001).tolist(),'chord_m':s['chord_envelope_mm']*.001,'projected_union_chord_m':s['projected_union_chord_mm']*.001} for s in prior['sections']],
       'confidence':'source-measured; inherited placement, not flight-build validation'},
      'tail':{'projected_union_area_m2':area_runs[-1]['area_m2'],'area_runs':area_runs,'panel_cant_fit_deg':cant,
       'panel_frames':{str(k):v.tolist() for k,v in tail_frames.items()},'projected_horizontal_span_m':float(np.ptp(left[:,1])*2*.001),
       'overall_tip_y_span_m':float(2*left[:,1].max()*.001),'confidence':'provisional original-STL placement; fitted panel frame, unresolved root fit'},
      'stations':stations,'airfoils':foils,'missing_closed_contours':missing,
      'fuselage':{'bounds_m':(fb*.001).tolist(),'dimensions_m':(np.ptp(fb,axis=0)*.001).tolist(),'sections':sections,
       'wetted_area_estimate_m2':wetted,'method':'integral of convex cross-section perimeter along X; not true exposed wetted area. Includes molded rear fin envelope, bridges concavities and hatch openings, excludes taper surface correction/endcaps.',
       'actual_exposed_wetted_area_m2':None,'confidence':'source-derived engineering envelope only'},
      'external_hardware':hardware,'nominal_or_illustrative_hardware':proxies,
      'documented_motor_dimensions':documented_motors,
      'blockers':['Actual motor can/shaft and blades absent from selected native/source STL inventory: showcase motor proxies are NOT measurements.',
       'Boom 10x10x500 mm is documented nominal proxy; actual exposed length after mounts and internal wing occlusion is not released.',
       'Fixed/control gaps retained: no fabricated combined full-chord airfoil. Tail root placements provisional.',
       'Fuselage perimeter integration is convex-envelope estimate, not exact exposed wetted surface.',
       'Root LE documentary datum unresolved; reference_area_released_m2 deliberately null.'],
      'extraction_seconds':time.time()-start}
    (OUT/'GEOMETRY.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'wing':result['wing']['span_m'],'wing_area':result['wing']['exposed_projected_union_area_m2'],'tail_area':result['tail']['projected_union_area_m2'],'tail_cant':cant,'foils':len(foils),'missing':len(missing),'fuselage':result['fuselage']['dimensions_m'],'wetted_envelope':wetted,'seconds':result['extraction_seconds']}),flush=True)
    return result

if __name__=='__main__':main()

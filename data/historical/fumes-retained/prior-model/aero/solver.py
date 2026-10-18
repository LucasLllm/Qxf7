"""Aircraft-specific, source-contour-only aerodynamic analysis. SI internally."""
from pathlib import Path
import numpy as np
import aerosandbox as asb

def load_contour(path):
    if path is None or not Path(path).is_file():
        raise ValueError('actual contour DAT required; no generic substitute')
    af = asb.Airfoil(name=Path(path).stem, coordinates=str(path)).normalize()
    if len(af.coordinates) < 20 or not np.isfinite(af.coordinates).all():
        raise ValueError('actual contour has insufficient/invalid points')
    return af

def contour_diagnostics(af):
    from scipy.spatial import cKDTree
    fitted=af.to_kulfan_airfoil(n_weights_per_side=8)
    rep=fitted.to_airfoil(n_coordinates_per_side=1000)
    distances=cKDTree(rep.coordinates).query(af.coordinates)[0]
    aero=fitted.get_aero_from_neuralfoil(alpha=2.,Re=200000.,model_size='large')
    return {'point_count':len(af.coordinates),'fit_rms_chord':float(np.sqrt(np.mean(distances**2))),
            'fit_max_chord':float(np.max(distances)),
            'max_thickness_chord':float(af.max_thickness()),
            'confidence':float(np.asarray(aero['analysis_confidence']).ravel()[0]),
            'confidence_condition':{'alpha_deg':2.,'Re':200000.,'n_crit':9.},
            'kulfan_weights_per_side':8,'metric':'nearest source point to dense fitted contour; chord-normalized',
            'valid_fit':bool(np.max(distances)<=.005)}

# Engineering scenario assumptions, NOT source geometry or calibrated coefficients.
ASSUMPTIONS = {
    'rho_kg_m3':1.225, 'nu_m2_s':1.4607e-5,
    'body_form_factor_smooth':1.2, 'body_form_factor_rough':1.6,
    'interference_smooth':1.10, 'interference_rough':1.30,
    'boom_count':2, 'boom_length_m':0.5, 'boom_square_m':0.010,
    'boom_exposed_fraction':0.8, 'square_end_Cd':1.05,
    'lift_motor_count':4, 'lift_motor_diameter_m':0.0334, 'lift_motor_height_m':0.025, # diameter from F90 spec; exposed height remains assumed
    'pusher_motor_diameter_m':0.028, 'pusher_motor_height_m':0.025,
    'lift_prop_count':4, 'lift_prop_diameter_m':0.1778, # selected 7-inch lift props, NOT 10-inch cruise prop
    'lift_prop_mean_chord_m':0.018, 'lift_prop_edge_thickness_m':0.0025,
    'stopped_blade_Cd':1.2, 'hardware_pressure_Cd':1.1,
    'bbox_frontal_blockage_smooth':0.4, 'bbox_frontal_blockage_rough':0.7,
    'NF_smooth':{'n_crit':9.,'xtr_upper':1.,'xtr_lower':1.},
    'NF_rough':{'n_crit':1.,'xtr_upper':0.05,'xtr_lower':0.05},
}

def component_drag(geometry, velocity, prop_orientation, surface):
    from aerosandbox.library.aerodynamics import Cf_flat_plate, Cd_cylinder
    if velocity <= 0 or prop_orientation not in ('aligned','crossflow') or surface not in ('smooth','rough'):
        raise ValueError('invalid component drag scenario')
    a=ASSUMPTIONS; q=.5*a['rho_kg_m3']*velocity**2; nu=a['nu_m2_s']
    interference=a['interference_'+surface]
    cf=lambda length: float(Cf_flat_plate(velocity*length/nu, method='turbulent' if surface=='rough' else 'hybrid-sharpe-convex'))
    fus=geometry['fuselage']; length=max(fus['dimensions_m'])
    fuselage=q*cf(length)*fus['wetted_area_estimate_m2']*a['body_form_factor_'+surface]*interference
    d=a['boom_square_m']; L=a['boom_length_m']*a['boom_exposed_fraction']; n=a['boom_count']
    booms=q*(cf(L)*4*d*L + a['square_end_Cd']*d*d)*n*interference
    dm=a['lift_motor_diameter_m']; hm=a['lift_motor_height_m']
    motorCd=float(Cd_cylinder(velocity*dm/nu,include_mach_effects=False))
    liftmotors=q*motorCd*dm*hm*a['lift_motor_count']*interference
    dp=a['pusher_motor_diameter_m']; hp=a['pusher_motor_height_m']
    pusher=q*(cf(hp)*np.pi*dp*hp + .8*np.pi*dp**2/4)*interference
    width=a['lift_prop_edge_thickness_m'] if prop_orientation=='aligned' else a['lift_prop_mean_chord_m']
    blades=q*a['stopped_blade_Cd']*a['lift_prop_count']*a['lift_prop_diameter_m']*width*interference
    gear_area=mount_area=0.
    for c in geometry.get('external_hardware',[]):
        dims=c['dimensions_m']; frontal=dims[1]*dims[2]
        if c['name'].startswith('MAIN SKIDS'): gear_area+=frontal
        elif c['name'].startswith(('MOTOR MOUNT','BOOM MOUNT')):mount_area+=frontal
    scale=q*a['hardware_pressure_Cd']*a['bbox_frontal_blockage_'+surface]*interference
    result={'fuselage_N':fuselage,'booms_N':booms,'gear_N':scale*gear_area,
            'mounts_N':scale*mount_area,'lift_motors_N':liftmotors,'pusher_motor_N':pusher,'lift_props_N':blades}
    result['parasite_N']=sum(result.values())
    return result


def build_airplane(g, geometry_root, tail_adjust_deg=0., working_cg=None):
    """Use every physical part profile separately; never close fixed/control hinge gaps.

    Each native part is a distinct lifting surface. Between cuts, interpolate; at its
    source-bounding span endpoint use nearest actual profile (declared approximation).
    No center wing bridge is created. +X forward/+Y left is converted to ASB aft/right.
    """
    from itertools import product
    groups={}
    components={c['name']:c for c in g['components']}
    for r in g['airfoils']:
        if r['family'] not in ('wing','tail'): continue
        groups.setdefault((r['family'],r['side'],r['part']),[]).append(r)
    wings=[]; audit=[]
    for (family,side,part),records in groups.items():
        records=sorted(records,key=lambda r:abs(r['station_m']))
        frame=np.asarray(records[0]['section_frame_rows'])
        corners=np.array(list(product(*zip(*components[part]['bounds_m']))))
        projected=corners@frame[1]
        if family=='wing': projected=np.abs(projected)
        lo,hi=float(projected.min()),float(projected.max())
        if hi-lo<.005: continue
        # Tail bbox projections are envelopes, hence limit endpoint extrusion to 20 mm.
        if family=='tail':lo=max(lo,abs(records[0]['station_m'])-.02);hi=min(hi,abs(records[-1]['station_m'])+.02)
        stations=[(abs(r['station_m']),r) for r in records]
        if lo < stations[0][0]-1e-5: stations.insert(0,(lo,records[0]))
        if hi > stations[-1][0]+1e-5: stations.append((hi,records[-1]))
        if len(stations)<2: continue
        xsecs=[]
        for span,r in stations:
            local=np.array([r['LE_local_xz_m'][0],side*span if family=='wing' else span,r['LE_local_xz_m'][1]])
            xyz=(local@frame)*np.array([-1.,-1.,1.])
            # ASB twist is nose-up incidence around the section's local span direction.
            incidence=r['incidence_deg']+(tail_adjust_deg if family=='tail' else 0.)
            xsecs.append(asb.WingXSec(xyz_le=xyz.tolist(),chord=r['chord_m'],twist=incidence,
                                     airfoil=load_contour(Path(geometry_root)/r['file'])))
        # ASB mesh faces must be ordered toward +Y (right); avoid reversed lifting normals.
        if xsecs[-1].xyz_le[1] < xsecs[0].xyz_le[1]: xsecs=xsecs[::-1]
        w=asb.Wing(name=f'{family}:{part}',xsecs=xsecs,symmetric=False)
        wings.append(w)
        audit.append({'part':part,'family':family,'source_files':[r['file'] for r in records],
                      'span_envelope_m':[lo,hi],'measured_span_range_m':[abs(records[0]['station_m']),abs(records[-1]['station_m'])],
                      'endpoint_rule':'nearest measured physical part profile extruded to STL bbox span; tail capped 20mm',
                      'surface_area_m2':float(w.area())})
    if not wings or not any(w.name.startswith('tail') for w in wings):
        raise ValueError('actual contour wing AND tail geometry required')
    wing_area=g['wing']['exposed_projected_union_area_m2'];span=g['wing']['span_m']
    if working_cg is None:working_cg=[.075,0.,0.] # explicit assumption in ASB aft/right/up axes
    plane=asb.Airplane(name='retained Stork source-part surfaces',xyz_ref=working_cg,wings=wings,
                       s_ref=wing_area,b_ref=span,c_ref=wing_area/span)
    return plane,{'source_part_surfaces':audit,'modeled_surface_area_m2':float(sum(w.area() for w in wings)),
                  'workingCG_ASB_m':working_cg,'workingCG_basis':'assumed computational point, NOT released CG limit',
                  'tail_adjustment_deg':tail_adjust_deg,'center_bridge':False,'hinge_gaps_filled':False}


def solve_point(g, geometry_root, kmh, mass=2.9837, mesh=(2,4), surface='smooth',
                prop_orientation='aligned', working_cg=(.075,0.,0.), initial=(4.,0.)):
    """Trim VLM lift and pitching moment with source-derived section NeuralFoil drag.

    Tail incidence change is a required equivalent correction, NOT released control authority.
    Profile CL is matched to strip VLM normal loading, excluding spanwise force. VLM chord
    moment about each strip quarter-chord is replaced with NF CM (no double count).
    """
    import copy
    from scipy.optimize import root
    velocity=kmh/3.6; rho=ASSUMPTIONS['rho_kg_m3'];nu=ASSUMPTIONS['nu_m2_s'];q=.5*rho*velocity**2
    ns,nc=mesh; base,meta=build_airplane(g,geometry_root,working_cg=list(working_cg))
    tables=[];strip_chords=[];strip_foils=[];families=[]
    grid=np.linspace(-12.,16.,113)
    for wing in base.wings:
        w=wing.subdivide_sections(ratio=ns)
        for xa,xb in zip(w.xsecs[:-1],w.xsecs[1:]):
            c=(xa.chord+xb.chord)/2
            af=xa.airfoil.blend_with_another_airfoil(xb.airfoil,blend_fraction=.5)
            data=af.get_aero_from_neuralfoil(alpha=grid,Re=velocity*c/nu,model_size='large',
                                          **ASSUMPTIONS['NF_'+surface])
            # Select positive-slope prestall branch around zero. Clipping is reported, not concealed.
            cl=np.asarray(data['CL']).ravel();i0=int(np.argmin(abs(grid)))
            a=b=i0
            while a>0 and cl[a-1]<cl[a]: a-=1
            while b<len(grid)-1 and cl[b+1]>cl[b]: b+=1
            tables.append({'cl':cl[a:b+1], 'alpha':grid[a:b+1],
                           **{k:np.asarray(data[k]).ravel()[a:b+1] for k in ('CD','CM','analysis_confidence')}})
            strip_chords.append(c);strip_foils.append(af);families.append(wing.name.split(':')[0])
    c=np.array(strip_chords);cg=np.asarray(working_cg);last={}
    def evaluate(x):
        plane=copy.deepcopy(base)
        for wing in plane.wings:
            if wing.name.startswith('tail'):
                for xs in wing.xsecs:xs.twist+=x[1]
        vlm=asb.VortexLatticeMethod(airplane=plane,op_point=asb.OperatingPoint(velocity=velocity,alpha=x[0]),
                                   spanwise_resolution=ns,chordwise_resolution=nc)
        aero=vlm.run()
        forces=vlm.forces_geometry.reshape(-1,nc,3)
        areas=vlm.areas.reshape(-1,nc).sum(axis=1)
        centers=(.5*(vlm.front_left_vertices+vlm.front_right_vertices)).reshape(-1,nc,3)
        # Strip quarter-chord point from full LE and TE, independent of panel spacing.
        le=centers[:,0,:]
        te=(.5*(vlm.back_left_vertices+vlm.back_right_vertices)).reshape(-1,nc,3)[:,-1,:]
        qc=.75*le+.25*te
        normals=vlm.normal_directions.reshape(-1,nc,3).mean(axis=1)
        normals/=np.linalg.norm(normals,axis=1)[:,None]
        lift_strip=(forces.sum(axis=1)*normals).sum(axis=1)
        cls=lift_strip/(q*areas)
        cds=[];cms=[];confs=[];alphas=[];outside=[]
        for target,t in zip(cls,tables):
            outside.append(bool(target<t['cl'][0] or target>t['cl'][-1]))
            cds.append(float(np.interp(target,t['cl'],t['CD'])))
            cms.append(float(np.interp(target,t['cl'],t['CM'])))
            confs.append(float(np.interp(target,t['cl'],t['analysis_confidence'])))
            alphas.append(float(np.interp(target,t['cl'],t['alpha'])))
        cds=np.array(cds);cms=np.array(cms)
        spanleg=vlm.vortex_bound_leg.reshape(-1,nc,3).sum(axis=1)
        spanleg/=np.linalg.norm(spanleg,axis=1)[:,None]
        inviscid_local_moment=np.cross(vlm.vortex_centers.reshape(-1,nc,3)-qc[:,None,:],forces).sum(axis=(0,1))[1]
        NF_moment=float(np.sum(q*areas*c*cms*spanleg[:,1]))
        flow=vlm.steady_freestream_direction
        profile_forces=q*areas[:,None]*cds[:,None]*flow[None,:]
        profile_pitch=float(np.cross(qc-cg,profile_forces).sum(axis=0)[1])
        moment=float(aero['m_b'])-float(inviscid_local_moment)+NF_moment+profile_pitch
        profile=float(q*np.sum(areas*cds));induced=float(aero['D'])
        wing_profile=float(q*np.sum(areas*cds*(np.array(families)=='wing')))
        last.update({'alpha_deg':float(x[0]),'equivalent_tail_incidence_adjust_deg':float(x[1]),
                     'lift_N':float(aero['L']),'lift_residual_N':float(aero['L'])-mass*9.80665,
                     'pitch_residual_Nm':moment,'induced_N':induced,'profile_N':profile,
                     'wing_profile_N':wing_profile,'tail_profile_N':profile-wing_profile,
                     'CL':float(aero['CL']),'NF_min_confidence':float(min(confs)),
                     'NF_area_weighted_confidence':float(np.average(confs,weights=areas)),
                     'NF_outside_prestall_strips':int(sum(outside)),
                     'NF_outside_prestall_area_fraction':float(np.sum(areas*np.array(outside))/np.sum(areas)),
                     'Re_min':float(min(velocity*c/nu)),'Re_max':float(max(velocity*c/nu)),
                     'strip_count':len(areas),'panel_count':len(vlm.areas),
                     'NF_section_alpha_min_deg':float(min(alphas)),'NF_section_alpha_max_deg':float(max(alphas)),
                     'wing_lift_N':float(forces[np.array(families)=='wing',:,2].sum()),
                     'tail_lift_N':float(forces[np.array(families)=='tail',:,2].sum())})
        return [last['lift_residual_N']/max(mass*9.80665,1.),moment/(mass*9.80665*base.c_ref)]
    sol=root(evaluate,np.array(initial),tol=1e-7)
    evaluate(sol.x)
    last.update(component_drag(g,velocity,prop_orientation,surface))
    last.update({'speed_kmh':float(kmh),'speed_mps':velocity,'mass_kg':mass,'surface':surface,
                 'prop_orientation':prop_orientation,'mesh_spanwise':ns,'mesh_chordwise':nc,
                 'root_success':bool(sol.success),'root_message':str(sol.message),
                 'workingCG_ASB_m':list(working_cg)})
    last['drag_N']=last['induced_N']+last['profile_N']+last['parasite_N']
    last['aero_power_W']=last['drag_N']*velocity
    last['CD']=last['drag_N']/(q*base.s_ref)
    last['L_D']=mass*9.80665/last['drag_N']
    last['trim_numerically_closed']=bool(abs(last['lift_residual_N'])<.05 and abs(last['pitch_residual_Nm'])<.01)
    last['valid_for_release']=False
    return last


def generate_curves(g,geometry_root,speeds=range(50,71,2),masses=(2.9837,3.0837),surfaces=('smooth','rough'),mesh=(2,4)):
    import copy
    rows=[]
    for mass in masses:
        for surface in surfaces:
            initial=(4.,0.)
            for speed in speeds:
                base=solve_point(g,geometry_root,speed,mass=mass,surface=surface,mesh=mesh,initial=initial)
                initial=(base['alpha_deg'],base['equivalent_tail_incidence_adjust_deg'])
                for orientation in ('aligned','crossflow'):
                    row=copy.deepcopy(base)
                    row.update(component_drag(g,speed/3.6,orientation,surface))
                    row['prop_orientation']=orientation
                    row['drag_N']=row['induced_N']+row['profile_N']+row['parasite_N']
                    row['aero_power_W']=row['drag_N']*row['speed_mps']
                    row['L_D']=mass*9.80665/row['drag_N']
                    row['CD']=row['drag_N']/(.5*ASSUMPTIONS['rho_kg_m3']*row['speed_mps']**2*g['wing']['exposed_projected_union_area_m2'])
                    rows.append(row)
                print(f'{mass:.4f}kg {surface} {speed}km/h D={base["drag_N"]:.5f}N NF={base["NF_min_confidence"]:.4f} trim={base["trim_numerically_closed"]}',flush=True)
    return rows


def run_analysis(geometry_path,output_dir):
    import json
    out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    geometry_path=Path(geometry_path)
    if not geometry_path.is_file():
        result={'status':'blocked','blocker':f'GEOMETRY.json not yet available at {geometry_path}; source DATs alone lack bound contour chord/twist/assembly/tail schema',
                'no_generic_substitute':True,'solver_executed':False,'assumptions':ASSUMPTIONS}
        (out/'AERO.json').write_text(json.dumps(result,indent=2)+'\n')
        return result
    return execute_analysis(geometry_path,out)


def execute_analysis(geometry_path,out,speeds=range(50,71,2),masses=(2.9837,3.0837),surfaces=('smooth','rough')):
    import json,csv,hashlib,inspect,importlib.metadata
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    geometry_path=Path(geometry_path);g=json.loads(geometry_path.read_text());geo_root=geometry_path.parent
    fits=[]
    for record in g['airfoils']:
        p=geo_root/record['file']
        fits.append({'file':record['file'],'part':record['part'],'family':record['family'],
                     'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),**contour_diagnostics(load_contour(p))})
    (out/'CONTOUR_FITS.json').write_text(json.dumps(fits,indent=2,allow_nan=False)+'\n')
    convergence=[]
    for mesh in [(1,3),(2,4),(3,6)]:
        point=solve_point(g,geo_root,60.,mesh=mesh)
        convergence.append(point)
        print(f'CONVERGENCE mesh={mesh} drag={point["drag_N"]:.7f} induced={point["induced_N"]:.7f} profile={point["profile_N"]:.7f}',flush=True)
    delta={k:abs(convergence[-1][k]-convergence[-2][k])/max(abs(convergence[-1][k]),1e-9)
           for k in ('drag_N','induced_N','profile_N')}
    rows=generate_curves(g,geo_root,speeds=speeds,masses=masses,surfaces=surfaces,mesh=(3,6))
    with (out/'CURVES.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    cg_sensitivity=[solve_point(g,geo_root,60.,mesh=(3,6),working_cg=(x,0.,0.)) for x in (.055,.075,.095)]
    plane,geometry_audit=build_airplane(g,geo_root)
    body_sources=['Cf_flat_plate','Cd_cylinder','Cd_flat_plate_normal']
    import aerosandbox.library.aerodynamics as lib
    snapshots='\n\n'.join(inspect.getsource(getattr(lib,k)) for k in body_sources)
    snapshots+='\n\n'+inspect.getsource(asb.VortexLatticeMethod.run)
    snapshots+='\n\n'+inspect.getsource(asb.Airfoil.get_aero_from_neuralfoil)
    (out/'LIBRARY_FORMULAS.txt').write_text(snapshots)
    result={'schema_version':'1.0','status':'executed_unvalidated','solver_executed':True,
            'method':'AeroSandbox source-part VLM + CL-matched NeuralFoil profiles + explicit component buildup',
            'geometry_file':str(geometry_path),'geometry_sha256':hashlib.sha256(geometry_path.read_bytes()).hexdigest(),
            'versions':{k:importlib.metadata.version(k) for k in ('aerosandbox','neuralfoil','numpy','scipy')},
            'assumptions':ASSUMPTIONS,'geometry_audit':geometry_audit,
            'workingCG':{'ASB_aft_right_up_m':[.075,0.,0.],'source_forward_left_up_m':[-.075,0.,0.],
                         'basis':'declared computational assumption, not documentary datum or released CG envelope',
                         'stress_points_ASB_x_m':[.055,.075,.095]},
            'trim_model':'solve lift=weight and pitch moment=0 by alpha and equal equivalent incidence correction on both source V-tail panels; NOT demonstrated elevator authority',
            'body_pitch_moment_assumption':'parasite drag resultant acts through workingCG; no thrust/slipstream moment, propulsion trim, power-on effects or fuselage lift',
            'curve_rows':len(rows),'curves':'CURVES.csv','contour_fits':'CONTOUR_FITS.json',
            'mesh_convergence':convergence,'last_refinement_relative_deltas':delta,
            'mesh_converged_2pct':bool(max(delta.values())<.02),
            'workingCG_trim_drag_sensitivity':cg_sensitivity,
            'contours_invalid_fit_count':sum(not r['valid_fit'] for r in fits),
            'contours_min_reference_confidence':min(r['confidence'] for r in fits),
            'validity_criteria':{'fit_max_chord_lte':.005,'NF_min_confidence_gte':.9,
                                 'NF_outside_prestall_area_fraction':0.,'mesh_last_change_lte':.02,
                                 'lift_residual_abs_N_lte':.05,'pitch_residual_abs_Nm_lte':.01,
                                 'required':'measured hardware/exposure, verified coupled fixed/control profile analysis, physical control-authority and measured CG closure, calibrated drag/flight evidence'},
            'valid_for_release':False,
            'limitations':g['blockers']+[
                'Source-part endpoint extrusions are declared approximations, not aerodynamic loft certification; disconnected native pieces interact inviscidly but their real coupled boundary layer is not modeled.',
                'Aft control segments are independently normalized actual contours, not a fabricated full-chord profile; NeuralFoil validity can fail badly on these blunt leading-edge profiles.',
                'VLM assumes attached flow even when NeuralFoil flags prestall loading exceeded; CL interpolation clips and flagged rows MUST NOT support range release.',
                'Projected bbox frontal blockage, body form factor and interference are assumed scenarios, not measured coefficients; fully turbulent Cf extrapolated below its cited 5e5 lower validity on short bodies.',
                'Stopped blade edge-on/broadside projected area scenarios do not include actual pitch/azimuth, hub/shaft details, spinning/windmilling drag or restart capability.',
                'No motor/prop CAD exists for actual installed hardware; numerical parasite scenarios are explicit nominal dimensional assumptions, NOT aircraft-measured predictions.'],
            'formula_sources':[{'source':'installed AeroSandbox 4.2.10 Cf_flat_plate docstring','formula':'Cf=0.074/Re_L**0.2 turbulent; smooth blended Blasius/Schlichting','reference':'Cengel/Cimbala Table 10-4; Schlichting Boundary Layer Theory 7th ed p644'},
                              {'source':'installed VortexLatticeMethod.run','formula':'F=rho*(V cross bound-leg)*Gamma; moments=sum((r-CG) cross F)'},
                              {'source':'installed Airfoil.get_aero_from_neuralfoil and NeuralFoil package','formula':'Kulfan actual-coordinate fit, Reynolds/transition conditioned section CL/CD/CM/confidence'},
                              {'source':'installed Cd_cylinder','formula':'Re-dependent cylinder crossflow Cd, projected diameter times can height'},
                              {'source':'explicit dimensional drag definition','formula':'D=q*Cd*A; skin body D=q*Cf*Swet*FF*Q; assumed FF/Q and pressure Cd separately enumerated'}]}
    (out/'AERO.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    return result


if __name__=='__main__':
    import json
    here=Path(__file__).resolve().parent
    result=run_analysis(here.parent/'geometry/GEOMETRY.json',here)
    print(json.dumps({'status':result['status'],'curve_rows':result.get('curve_rows',0),'mesh_converged_2pct':result.get('mesh_converged_2pct')}),flush=True)


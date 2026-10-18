"""Integrate finalized leaf files; no new source geometry or pose transformations."""
from pathlib import Path
import json,csv,hashlib
import numpy as np
D=Path(__file__).resolve().parent
read=lambda p:json.loads((D/p).read_text())
required=['wing-extraction/wing_geometry.json','wing-extraction/sections.csv','tail-extraction/tail_geometry.json','tail-extraction/profile_summary.csv','fuselage-with-hatches/results.json','fuselage-with-hatches/hardware_dimensions.csv']
required += ['fuselage-with-hatches/cross_sections_50mm.csv','wing-extraction/panel_rates.json','coordinate_frame.json','extraction_authorization.json','hatch_parent_verification.json','hatch-feature-work/placement.json']
required += ['fuselage-with-hatches/verification.json','fuselage-with-hatches/manifest.json','fuselage-with-hatches/manifest_verification.json']
missing=[p for p in required if not(D/p).exists()]
if missing:raise SystemExit('Integration awaits completed outputs: '+', '.join(missing))
w=read('wing-extraction/wing_geometry.json');t=read('tail-extraction/tail_geometry.json');f=read('fuselage-with-hatches/results.json')
fm=read('fuselage-with-hatches/manifest.json')
assert all(hashlib.sha256((D/'fuselage-with-hatches'/p).read_bytes()).hexdigest()==h for p,h in fm.items()),'Fuselage final manifest mismatch'
assert read('fuselage-with-hatches/verification.json')['status']=='PASS'
assert read('fuselage-with-hatches/manifest_verification.json')['status']=='PASS'
print('Tail schema',list(t))
rows=[]
def add(component,station,quantity,value,units,status,definition,evidence):
 rows.append(dict(component=component,station=station,quantity=quantity,value='' if value is None else value,units=units,status=status,definition=definition,evidence=evidence))
def unit(k):
 if k.endswith('_count'):return 'count'
 if k.endswith('_mm_at_local_chord'):return 'mm'
 if k.endswith('_mm2'):return 'mm^2'
 if k.endswith('_m2'):return 'm^2'
 if k.endswith('_dm2'):return 'dm^2'
 if k.endswith('_mm'):return 'mm'
 if k.endswith('_deg'):return 'deg'
 if k.endswith('_c') or '_over_chord' in k:return 'chord fraction'
 return 'see source'
for component,p,idcol,status,definition in [
 ('wing','wing-extraction/sections.csv','section_id','SOURCE_POSE_SECTION','Actual constant-aircraft-y section. Joint/control-clearance cuts can be truncated/nonrepresentative; inspect raw and diagnostic overlays.'),
 ('tail','tail-extraction/profile_summary.csv','section','SOURCE_POSE_SECTION','Physical tail-root-plane-normal section; true conventional tip undefined. Fin transition/tip contours not conventional airfoils.'),
 ('fuselage','fuselage-with-hatches/cross_sections_50mm.csv','aircraft_x_mm','CONVEX_ENVELOPE_ESTIMATE','Hatch-inclusive section-edge envelope with feature-registered original hatch solids; any convexification/slot closure remains an approximation, not exact installed skin. Station is common-STEP aircraft-x mm.'),
 ('hardware','fuselage-with-hatches/hardware_dimensions.csv','part','ISOLATED_PART_GEOMETRY','Source-axis-mapped isolated part dimensions/silhouettes, not net exposed or occlusion-corrected installed drag area.')]:
 with(D/p).open()as fh:
  for i,r in enumerate(csv.DictReader(fh)):
   station=r.get(idcol,str(i))
   row_status=status; row_definition=definition
   if component=='wing' and station in {'aileron_start_in','aileron_end_out','tip_root_in'}:
    row_status='TRUNCATED_CLEARANCE_DIAGNOSTIC_NOT_AIRFOIL'
    row_definition='Retained manufacturing-clearance contour; chord and shape metrics NOT qualified local aerodynamic quantities. Compare original support and cleaner adjacent section in wing-extraction/station_diagnostics.json.'
   for k,v in r.items():
    if not v or k==idcol:continue
    try:value=float(v)
    except (ValueError,TypeError):continue
    add(component,station,k,value,unit(k),row_status,row_definition,p)
for convention in ['exposed','gross_with_declared_centerline_continuation','physical_outer_envelope_exposed']:
 for k,v in w[convention].items():
  if isinstance(v,(float,int)):
   definition='Physical exterior chord envelope, distinct from gap-preserving occupied projection.' if convention=='physical_outer_envelope_exposed' else 'Hybrid reference: inboard original design-support silhouette and outboard physical extrema. Gross adds explicit artificial rectangular centre continuation. Not wholly physical skin or measured lift.'
   add('wing',convention,k,v,unit(k),'GEOMETRIC_PLANFORM',definition,'wing-extraction/wing_geometry.json')
add('wing','physical_occupied_projection','physical_occupied_projection_both_sides_dm2',w['physical_occupied_projection_both_sides_dm2'],'dm^2','PHYSICAL_PROJECTION',w['physical_projection_convention'],'wing-extraction/wing_geometry.json')
for r in read('wing-extraction/panel_rates.json'):
 for k,v in r.items():
  if isinstance(v,(int,float)):add('wing',r['panel'],k,v,unit(k),'CLEAN_ENDPOINT_GEOMETRY','Clean-section finite differences. Sweep positive aft; dihedral depends on named chord reference; curved tip treated separately.','wing-extraction/panel_rates.json')
add('airframe','length_reference','nose_to_pusher_mm',1000.,'mm','ACCEPTED_REFERENCE','Distinct from overall fixed airframe length; no source geometry rescaled.','extraction_authorization.json')
add('airframe','length_reference','overall_fixed_airframe_mm',1044.0203247070312,'mm','MEASURED_REGISTERED_SUBSET','Feature-registered fixed-tail extremum, not motor or propeller envelope.','reference_gate.json')
add('fuselage','isolated_convex_lateral_envelope','convex_lateral_envelope_area_m2',f['convex_lateral_envelope_area_m2'],'m^2','ENVELOPE_ESTIMATE',f['installed_exposed_area_status'],'fuselage-with-hatches/results.json')
for k in ['baseline_hatch_augmented_grid_convex_envelope_m2','matched_grid_hatch_increase_m2','matched_grid_hatch_increase_percent']:
 add('fuselage','matched_grid_hatch_sensitivity',k,f['exact_matched_grid_comparison'][k],'%' if k.endswith('_percent') else 'm^2','ENVELOPE_MODEL_SENSITIVITY','Exactly matched axial/angle grid; model difference, not added physical skin area.','fuselage-with-hatches/matched_grid_comparison.json')
add('fuselage','unregistered_nose_gap','conditional_straight_bridge_sensitivity_m2',f['unresolved_nose_connection']['conditional_straight_bridge_sensitivity_m2'],'m^2','HYPOTHETICAL_SENSITIVITY_ONLY','Excluded from primary envelope. Nose registration is incomplete; no bridge is installed or inferred.','fuselage-with-hatches/results.json')
for quantity,definition in [
 ('certified_aileron_zero_deg','Saved pose closely follows original untrimmed wing design loft; commanded/rigged neutral not established.'),
 ('certified_rudder_zero_deg','Saved pose near symmetric/smooth continuation; agreed neutral target/linkage calibration unavailable.'),
 ('motor_station_x_mm','No final motors/shaft overhang and complete boom installation known.'),
 ('true_wingtip_conventional_airfoil','Actual upturned tip extreme does not define a conventional constant-y airfoil.'),
 ('true_tailtip_conventional_airfoil','Actual fin extreme does not define a conventional tail airfoil.'),
 ('exact_exposed_wetted_area_m2','Buried contact patches and remaining pieces unresolved; hatches registered, but isolated envelope is not exact exposed area.')]:
 add('qualification','unknown',quantity,None,unit(quantity),'UNKNOWN',definition,'leaf geometry/readme and source feature receipts')
# Explicit tail frame and geometric wing-to-tail lever-arm conventions.
for k,v in t['basis'].items():
 if isinstance(v,(int,float)):add('tail','mount_frame',k,v,unit(k),'FEATURE_PLANE_GEOMETRY','Physical mounting frame; not aerodynamic-centre geometry.','tail-extraction/tail_geometry.json')
for convention in ['planform_full_including_fin','planform_regular_before_fin_sample_truncation']:
 for k,v in t[convention].items():
  if isinstance(v,(int,float)):
   add('tail',convention,k,v,unit(k),'SOURCE_POSE_PLANFORM',t[convention]['definition'],'tail-extraction/tail_geometry.json')
  elif isinstance(v,list) and len(v)==3:
   for axis,value in zip('xyz',v):
    add('tail',convention,k+'_'+axis,value,'mm','SOURCE_POSE_VECTOR',t[convention]['definition'],'tail-extraction/tail_geometry.json')
from derive_arms import derive
arms=derive(w,t)
(D/'moment_arms.json').write_text(json.dumps(arms,indent=2)+'\n')
for name,q in arms.items():
 if isinstance(q,dict):
  for k in ['longitudinal_arm_mm','xz_distance_mm']:
   add('wing_tail',name,k,q[k],'mm','GEOMETRIC_LEVER_ARM',arms['definition'],'moment_arms.json')
with(D/'geometry_table.csv').open('w')as fh:
 writer=csv.DictWriter(fh,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
receipt={'rows':len(rows),'inputs_sha256':{p:hashlib.sha256((D/p).read_bytes()).hexdigest()for p in required},'geometry_table_sha256':hashlib.sha256((D/'geometry_table.csv').read_bytes()).hexdigest(),'format':'long form with units/status/definitions and source paths. Empty UNKNOWN values are not zeros.'}
(D/'integration_receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))

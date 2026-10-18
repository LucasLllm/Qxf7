"""Package checked derived outputs, excluding licensed source CAD and heavy intermediates."""
from pathlib import Path
import zipfile,json,hashlib
D=Path(__file__).resolve().parent
required=['EXTRACTION_REPORT.md','geometry_table.csv','moment_arms.json','extraction_verification.json','integration_receipt.json','delivery_verification.json']
assert all((D/p).is_file() for p in required),'Finalized outputs missing'
v=json.loads((D/'extraction_verification.json').read_text())
assert v['profile_validation_pass'] and v['original_sources_unchanged']
dv=json.loads((D/'delivery_verification.json').read_text())
assert dv['status']=='PASS'
assert hashlib.sha256((D/'geometry_table.csv').read_bytes()).hexdigest()==dv['geometry_table_sha256']
assert hashlib.sha256((D/'EXTRACTION_REPORT.md').read_bytes()).hexdigest()==dv['report_sha256']
files=[D/p for p in required]
for folder in ['wing-extraction','tail-extraction','fuselage-with-hatches','hatch-feature-work','uiuc-comparison','review-overlays']:
 files += [p for p in (D/folder).rglob('*') if p.is_file() and p.suffix.lower() in ['.dat','.csv','.png','.md','.json','.py'] and '__pycache__' not in str(p)]
files += list(D.glob('*.py'))
for name in ['assembly_notes.md','EXTRACTION_LIMITATIONS.md','extraction_authorization.json','coordinate_frame.json','execution_environment.json','reference_gate.json','GATE_REVIEW.md','hatch_parent_verification.json']:
 files.append(D/name)
files=sorted(set(files));manifest={str(p.relative_to(D)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
p=D/'stork-aero-extraction-review.zip'
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED) as z:
 for f in files:z.write(f,str(f.relative_to(D)))
 z.writestr('BUNDLE_HASHES.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(p) as z:assert z.testzip() is None
r={'path':str(p),'bytes':p.stat().st_size,'files':len(files)+1,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(D/'bundle_receipt.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))

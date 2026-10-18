from pathlib import Path
import zipfile,json,hashlib
D=Path(__file__).resolve().parent
v=json.loads((D/'extraction_verification.json').read_text());assert v['profile_validation_pass'] and v['original_sources_unchanged']
fs=[D/n for n in ['PROFILE_CHECKPOINT.md','EXTRACTION_LIMITATIONS.md','extraction_verification.json','extraction_authorization.json','reference_gate.json']]
for folder in ['wing-extraction','tail-extraction','uiuc-comparison','review-overlays']:
 fs.extend(p for p in (D/folder).rglob('*') if p.is_file() and p.suffix in ['.dat','.csv','.png','.md'] and 'notes/' not in str(p.relative_to(D)))
p=D/'stork-section-checkpoint.zip'
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED)as z:
 for f in sorted(set(fs)):z.write(f,str(f.relative_to(D)))
with zipfile.ZipFile(p)as z:assert z.testzip() is None;count=len(z.namelist())
r={'path':str(p),'files':count,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(D/'profile_checkpoint_receipt.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2))

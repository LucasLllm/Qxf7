"""Independent diagnostic of physical PRINT-PART sections, not aircraft polars."""
from pathlib import Path
import json,sys
import aerosandbox as asb
import numpy as np
from scipy.spatial import cKDTree
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'aero'))
from solver import load_contour,contour_diagnostics
paths=sorted((ROOT/'geometry/airfoils').glob('wing_R_700_*/airfoil.dat'))
assert paths,'Extracted source sections needed'
result=[]
for p in paths:
    af=load_contour(p)
    d=contour_diagnostics(af)
    d['source_dat']=str(p.relative_to(ROOT))
    d['meaning']='A closed physical print-part contour is not necessarily a complete aerodynamic airfoil; split fixed/aileron sections need interference/hinge modeling.'
    result.append(d)
(ROOT/'SECTION_FIT_AUDIT.json').write_text(json.dumps(result,indent=2))
print(json.dumps(result,indent=2))

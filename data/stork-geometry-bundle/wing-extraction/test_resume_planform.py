"""Run with research-venv/bin/python -B test_resume_planform.py."""
from pathlib import Path
import ast
D=Path(__file__).resolve().parent
ns={'__file__':str(D/'extract_wing.py')}
tree=ast.parse((D/'extract_wing.py').read_text())
exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,(ast.Import,ast.ImportFrom,ast.FunctionDef))],type_ignores=[]),str(D/'extract_wing.py'),'exec'),ns)
ns['OUT']=D
try:
    from resume_planform import physical_section
except ImportError:
    # The exact pre-fix call, deliberately reproducing its disjoint-loop failure.
    physical_section=lambda y: ns['groups'](y)
r=physical_section(563.02)
assert r['all_loop_extrema_retained']
assert any(a['outer_loop_count']>1 for a in r['audit'] if a['component']=='right_aileron_1')
assert r['xmax']>209
try:
    ns['groups'](563.02)
except AssertionError:
    pass
else:
    raise AssertionError('Profile diagnostic must stay strict')
print('PASS: real disjoint mechanical loops retained; strict profile diagnostic preserved')
# CAD section kernel drops the outer skins here, returning only a hole and an
# open TE edge. Closed physical-solid tessellation must recover the real section.
r=physical_section(693.5001)
assert r['xmax']>204
assert any(a.get('section_method','').startswith('physical_STEP_tessellation') for a in r['audit'])
print('PASS: open/incomplete exact CAD intersection detected and independently sectioned')

"""Small independent exact witness for polynomial nonzero arguments; not a Lean replay."""
from pathlib import Path
import hashlib
import json
import platform
import time
import sympy as s

start = time.monotonic()
U, r, w, t, X = s.symbols('U r w t X')
a = (1+r**6+w**6)/r**3
v = 1/r+r*w
f = X**18+X**12+(v*X-1)**6-a*X**15
fR = s.cancel(s.diff(f, X).subs(X, r))
b, c, d = t*v, t*(1-t**2)/7, 1+t**6
Delta = 27*a*a*d*d-18*a*b*c*d+4*a*c**3+4*b**3*d-b*b*c*c
cubic = (1+r**6+w**6)*U**3+t*r*(1+r*r*w)*U**2+t*r*(1-t*t)*U/7+1+t**6
point = {U: 0, r: 1, w: 1, t: 0}
values = {name: s.cancel(expr.subs(point)) for name, expr in
          [('a',a), ('v',v), ('cubic',cubic), ('fR',fR), ('Delta',Delta)]}
expected = {'a':3, 'v':2, 'cubic':1, 'fR':-3, 'Delta':243}
if values != expected:
    raise RuntimeError('Exact point values differ: '+str(values))
if s.cancel(fR-3*r**9*(r**8-3*r**2*w**6-r**2+2*w**5)) != 0:
    raise RuntimeError('Independent physical-polynomial derivative differs')
cleared = s.Poly(s.cancel(r**6*Delta), r, w, t, domain=s.QQ)
if cleared.eval({r:1,w:1,t:0}) != 243:
    raise RuntimeError('Cleared discriminant witness differs')
jac = s.det(s.Matrix([[s.diff(a,r),s.diff(a,w)], [s.diff(v,r),s.diff(v,w)]]))
if s.cancel(jac.subs({r:1,w:1})) != -3:
    raise RuntimeError('Chart Jacobian witness differs')
out = {
    'status':'PASS', 'executor':'Codex coordinator, independent SymPy exact arithmetic',
    'python':platform.python_version(), 'sympy':s.__version__,
    'source_parent':'e2182223a0395cfb758a2ee09e304eb940b7a67a',
    'formula_sources':['formal/HodgeLab/OneReflectionSkew/ChartSubstitution.lean',
                       'formal/HodgeLab/OneReflectionSkew/PhysicalSourceNormalization.lean'],
    'point':{'U':0,'r':1,'w':1,'t':0},
    'values':{key:str(value) for key,value in values.items()},
    'fR':'3*r^9*(r^8-3*r^2*w^6-r^2+2*w^5)',
    'cleared_delta_polynomial_over_Q':True, 'jacobian_at_point':'-3',
    'requirements_checked':8, 'elapsed_seconds':time.monotonic()-start,
    'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'limits':'Exact polynomial/rational identities and a point witness only. No evaluation of the entire fraction field, no Lean execution, no field/pullback construction or primitive.'
}
Path(__file__).with_name('generic-open-point.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(out))

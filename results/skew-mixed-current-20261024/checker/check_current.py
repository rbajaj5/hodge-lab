#!/usr/bin/env python3
"""Independent exact check of the proposed SECOND current, not a solution.

Uses only the pinned public connection JSON and the packet's conventions.
Does not import the proposer script or the old source/chart/rank checkers.
Run with --run: the symbolic child is forcibly bounded to 60 seconds.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time
import threading
import os
import argparse

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--connection', type=Path, default=Path(r'C:/Users/anaxe/Documents/Codex/hl-source-20261023/results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'))
parser.add_argument('--run', action='store_true')
args = parser.parse_args()
SOURCE = args.connection
EXPECTED = 'a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'

if args.run:
    began = time.monotonic()
    try:
        run = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--connection', str(SOURCE)],
                             capture_output=True, text=True, encoding='utf-8', timeout=60)
    except subprocess.TimeoutExpired as exc:
        def as_text(x):
            return x.decode('utf-8', errors='replace') if isinstance(x, bytes) else (x or '')
        (HERE / 'check-current-timeout.log').write_text(as_text(exc.stdout) + as_text(exc.stderr), encoding='utf-8')
        raise
    (HERE / 'check-current.log').write_text(run.stdout + run.stderr, encoding='utf-8')
    print(run.stdout, end='')
    print(run.stderr, end='', file=sys.stderr)
    print('Child wall seconds:', round(time.monotonic() - began, 3))
    sys.exit(run.returncode)

import sympy as S

watchdog = threading.Timer(58, lambda: os._exit(124))
watchdog.daemon = True
watchdog.start()
print('START independent current checker', flush=True)

source_bytes = SOURCE.read_bytes()
assert hashlib.sha256(source_bytes).hexdigest() == EXPECTED
raw = json.loads(source_bytes)
a, b, c, d, r, v, t = S.symbols('a b c d r v t')
gg, kk = S.symbols('g k')
e0 = S.Matrix([1, 0])
e1 = S.Matrix([0, 1])
loc = {str(z): z for z in (a, b, c, d)}
M = {z: S.Matrix([[S.sympify(x, locals=loc) for x in row]
                  for row in raw['connection'][str(z)]]) for z in (a, b, c, d)}
checks = []
controls = []

def cancel_vector(x):
    return x.applyfunc(S.cancel) if isinstance(x, S.MatrixBase) else S.cancel(x)

def check(label, expression):
    vals = list(expression) if isinstance(expression, S.MatrixBase) else [expression]
    result = [S.cancel(x) for x in vals]
    assert all(x == 0 for x in result), (label, result)
    checks.append(label)
    print('PASS:', label, flush=True)

def control(label, expression, point):
    vals = list(expression) if isinstance(expression, S.MatrixBase) else [expression]
    result = [S.cancel(x.subs(point, simultaneous=True)) for x in vals]
    assert any(x != 0 for x in result), (label, result)
    controls.append({'name': label, 'exact_defect': [str(x) for x in result]})
    print('REJECTED CONTROL:', label, result, flush=True)

# Independent exact rational-field cover derivatives avoid expression swell.
from sympy.polys.fields import field
F, rf, vf = field('r,v', S.QQ)
Af = rf**3 + rf**-3 + (vf*rf - 1)**6 / rf**15
Arf = Af.diff(rf)
rvf = -Af.diff(vf)/Arf
def DvF(expr):
    return expr.diff(vf) + rvf*expr.diff(rf)
psif = rf**-3
psivf = DvF(psif)
gf = DvF(psivf)
kf = vf*psivf-psif
assert DvF(kf)-vf*gf == 0
checks.append('fixed-a derivative of k equals v*g')
print('PASS: fixed-a derivative of k equals v*g', flush=True)
rrf = -(Af.diff(vf).diff(vf)+2*Af.diff(rf).diff(vf)*rvf+Af.diff(rf).diff(rf)*rvf**2)/Arf
assert gf-(12*rf**-5*rvf**2-3*rf**-4*rrf) == 0
checks.append('two independent constructions of g agree')
print('PASS: two independent constructions of g agree', flush=True)
A, Ar, g, k = [x.as_expr() for x in (Af, Arf, gf, kf)]
check('g is independent of t', S.diff(g, t))
check('k is independent of t', S.diff(k, t))

sub = {b: t*v, c: t*(1-t**2)/7, d: 1+t**6}
Mb = M[b].subs(sub, simultaneous=True)
Mc = M[c].subs(sub, simultaneous=True)
Md = M[d].subs(sub, simultaneous=True)
Nv = t*Mb
Nt = v*Mb + (1-3*t**2)*Mc/7 + 6*t**5*Md
delta = S.sympify(raw['Delta'], locals=loc).subs(sub, simultaneous=True)

# Partial derivatives of fluxes use exactly the checked scalar identities.
Yt = -gg*e1/(36*t)
Yv = -kk*e0/(108*a*t)
dYt = S.diff(Yt, t)
dYv = -v*gg*e0/(108*a*t)
R0 = gg*e1/(36*t**2)
divY = dYt + Nt*Yt + dYv + Nv*Yv
Ractual = R0 - divY
Rclaimed = gg*(Nt*e1 + v*e0/(3*a))/(36*t) + kk*Mb*e0/(108*a)
check('both rows of R0-div(Y) equal claimed R2', Ractual - Rclaimed)

# Regularity is certified by the reduced exact rational denominators in t.
check('Nt(0)e1 equals -v e0/(3a)', (Nt*e1).subs(t, 0) + v*e0/(3*a))
check('Delta(0) equals 27 a^2', delta.subs(t, 0) - 27*a**2)
Rregular = cancel_vector(Rclaimed)
den0 = [S.factor(S.denom(x).subs(t, 0)) for x in Rregular]
assert all(x != 0 for x in den0), den0
checks.append('both reduced residual denominators are nonzero at generic t=0')
print('PASS: both residual denominators at t=0:', den0, flush=True)
limit0 = S.simplify(Rregular.subs(t, 0))
check('explicit regular value at t=0', limit0 - gg*S.Matrix([1/(10584*a), v/(1512*a)]))

# A rational physical point with t nonzero; no floating point evidence.
basepoint = {r: S.Integer(1), v: S.Integer(2)}
ap = S.cancel(A.subs(basepoint))
gp = S.cancel(g.subs(basepoint))
kp = S.cancel(k.subs(basepoint))
point = {a: ap, v: S.Integer(2), t: S.Integer(1), gg: gp, kk: kp}
ar_point = S.cancel(Ar.subs(basepoint))
delta_point = S.cancel(delta.subs(point))
assert (ap, gp, kp, ar_point, delta_point) == (3, 42, -13, -3, 1036)
point_result = cancel_vector(Rregular.subs(point))
assert all(x != 0 for x in point_result), point_result
check('ordinary point direct flux evaluation agrees', Ractual.subs(point) - point_result)
point_zero_t = S.simplify(limit0.subs(point))
check('ordinary t=0 value on same cover point', point_zero_t - S.Matrix([S.Rational(1, 756), S.Rational(1, 54)]))

# Each mutation preserves everything else and must visibly fail.
control('flip sign of Y_t', R0 - (-dYt - Nt*Yt + dYv + Nv*Yv) - Rclaimed, point)
control('flip sign of Y_v', R0 - (dYt + Nt*Yt - dYv - Nv*Yv) - Rclaimed, point)
control('use d-M instead of pinned d+M', R0 - (dYt - Nt*Yt + dYv - Nv*Yv) - Rclaimed, point)
control('flip k_v=v*g to k_v=-v*g', R0 - (dYt + Nt*Yt - dYv + Nv*Yv) - Rclaimed, point)

report = {
    'status': 'PASS: second-current identity and generic t=0 regularity; full equation remains unsolved',
    'source': str(SOURCE), 'source_sha256': EXPECTED,
    'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    'software': {'python': sys.version, 'sympy': S.__version__},
    'conventions': 'Packet orientation, columns index input basis, connection d+M; dv/dt derivatives at fixed a; r_t=0.',
    'new_checks_only': checks, 'deliberate_sign_controls': controls,
    'g_definition': 'Dv(Dv(r**-3)), Dv=partial_v-(A_v/A_r)*partial_r',
    'k_definition': 'v*Dv(r**-3)-r**-3',
    'g_rational': str(g), 'k_rational': str(k),
    'current': {'Y_a': ['0','0'], 'Y_v': [str(x) for x in Yv], 'Y_t': [str(x) for x in Yt]},
    'residual_regular_rows': [str(x) for x in Rregular],
    'residual_denominators_at_t_zero': [str(x) for x in den0],
    'residual_at_t_zero': [str(x) for x in limit0],
    'ordinary_point': {'r': '1', 'a': str(ap), 'v': '2', 't': '1', 'A_r': str(ar_point), 'g': str(gp), 'k': str(kp), 'Delta': str(delta_point), 'residual': [str(x) for x in point_result]},
    'same_cover_point_at_t_zero_residual': [str(x) for x in point_zero_t],
    'domain': 'Rational identity in full degree-18 function field; displayed base/cover chart uses r!=0, a!=0, A_r!=0, Delta!=0. Initial flux formulas use t!=0. Residual alone extends to t=0 on this open; current still has poles there. At t=0 Delta=27 a^2.',
    'scope': 'Only a further exact current subtraction and pole removal for its residual. Residual nonzero in both rows. No full rational primitive, homogeneous certificate, all-sheet solution, or new rank/trace/chart conclusion.',
    'provenance': 'Independent checker by a parallel Codex agent. Directly parses public fqlx connection JSON pinned by benediamond packet. Does not import proposer scripts or earlier verification scripts.'
}
(HERE / 'check-current.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
print('PASS:', len(checks), 'exact identity/regularity checks;', len(controls), 'sign controls rejected', flush=True)
watchdog.cancel()

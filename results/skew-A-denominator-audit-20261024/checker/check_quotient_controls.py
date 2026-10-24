#!/usr/bin/env python3
"""New quotient-family controls only; no matrix search or old identity replay."""
from pathlib import Path
import argparse, hashlib, json, os, subprocess, sys, threading, time

HERE = Path(__file__).resolve().parent
EXPECTED_SOURCE = 'a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
p = argparse.ArgumentParser()
p.add_argument('--child', action='store_true')
p.add_argument('--connection', type=Path, default=Path('C:/Users/anaxe/Documents/Codex/hl-source-20261023/results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'))
args = p.parse_args()

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write_json(path, obj):
    path.write_bytes((json.dumps(obj, indent=2, ensure_ascii=False) + '\n').encode('utf-8'))

if not args.child:
    start = time.monotonic()
    env = dict(os.environ, PYTHONUTF8='1', PYTHONIOENCODING='utf-8')
    timeout = False
    try:
        out = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--child', '--connection', str(args.connection)], capture_output=True, env=env, timeout=60)
        stdout, stderr, code = out.stdout, out.stderr, out.returncode
    except subprocess.TimeoutExpired as ex:
        stdout, stderr, code = ex.stdout or b'', ex.stderr or b'', 124
        timeout = True
    (HERE/'quotient-controls.stdout.log').write_bytes(stdout)
    (HERE/'quotient-controls.stderr.log').write_bytes(stderr)
    receipt = {'exit_code':code, 'timeout':timeout, 'wall_seconds':time.monotonic()-start,
        'child_limit_seconds':60, 'encoding':'UTF-8, raw subprocess stream bytes preserved',
        'script_sha256':digest(Path(__file__)), 'source_sha256':digest(args.connection),
        'stdout_sha256':digest(HERE/'quotient-controls.stdout.log'),
        'stderr_sha256':digest(HERE/'quotient-controls.stderr.log')}
    if (HERE/'quotient-controls.json').exists():
        receipt['report_sha256'] = digest(HERE/'quotient-controls.json')
    write_json(HERE/'quotient-controls-receipt.json', receipt)
    sys.stdout.buffer.write(stdout)
    sys.stderr.buffer.write(stderr)
    print(json.dumps(receipt))
    sys.exit(code)

import sympy as S
watch = threading.Timer(58, lambda:os._exit(124))
watch.daemon = True
watch.start()
assert digest(args.connection) == EXPECTED_SOURCE
r, v, t = S.symbols('r v t')
coords = (r,v,t)
A = r**3 + r**-3 + (v*r-1)**6/r**15
F = S.expand(r**18 + r**12 + (v*r-1)**6)
assert S.cancel(A-F/r**15) == 0
assert S.diff(A,t) == 0

# Independent expressions: differentiate polynomial numerator/F, then compare
# with the quotient derivative formed using the original expression for A.
exponents = [(m,n,k) for m in range(-10,3) for n in range(3) for k in range(3)]
count = 0
for m,n,k in exponents:
    mon = r**m*v**n*t**k
    quotient = r**(m+15)*v**n*t**k/F
    for x in coords:
        expected = S.diff(mon,x)/A-mon*S.diff(A,x)/A**2
        assert S.cancel(S.diff(quotient,x)-expected) == 0, (m,n,k,str(x))
        count += 1
assert count == 351
print('PASS: 351 exact quotient derivative identities for all 117 monomials',flush=True)

# The constant monomial isolates the new quotient terms without a connection
# contribution. Omitting either term is a concrete nonzero failed control.
point = {r:S.Integer(1),v:S.Integer(2),t:S.Integer(1)}
controls = []
for x in (r,v):
    correct = S.diff(r**15/F,x).subs(point)
    assert correct != 0
    controls.append({'coordinate':str(x),'correct_derivative':str(correct),
                     'mutant_derivative':'0','mutation':'omit -mon*A_i/A^2'})
    print('REJECTED CONTROL:',str(x),'derivative is',correct,'rather than 0',flush=True)
assert controls[0]['correct_derivative']=='1/3'
assert controls[1]['correct_derivative']=='-2/3'

report = {
 'status':'PASS: quotient derivative controls; no finite-family solvability conclusion',
 'source_sha256':EXPECTED_SOURCE,
 'script_sha256':digest(Path(__file__)),
 'family':'Six components, each V/A; V=span_Q{r^m v^n t^k:-10<=m<=2,0<=n,k<=2}',
 'derivative_identities':count, 'monomials':len(exponents), 'negative_controls':controls,
 'A':'r^3+r^-3+(v*r-1)^6/r^15',
 'quotient_rule':'partial_i(mon/A)=(partial_i mon)/A-mon*(partial_i A)/A^2; partial_t A=0',
 'connection':'N_r=A_r M_a; N_v=A_v M_a+t M_b; N_t=v M_b+(1-3t^2)M_c/7+6t^5 M_d',
 'source':'r^-4 M_b e0/12 in the pinned packet positive orientation',
 'source_scope':'Connection bytes pinned; source and orientation reused from finished packet evidence, not re-proved here',
 'domain':'Rational identities on r*A!=0; full equation additionally uses the connection ordinary locus',
 'matrix_scope':'No exploratory matrix, determinant, rank, kernel or inconsistency computation in this check',
 'python':sys.version, 'sympy':S.__version__}
write_json(HERE/'quotient-controls.json',report)
watch.cancel()

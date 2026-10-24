"""Independently reconstruct the full declared A^-7 current matrix.

Literal integer-AST connection evaluation, reduced W7 top columns, and
exponent-lowered monomial derivatives are independent of the lead's direct
quotient construction. This process checks every entry and every sampled
domain. It computes no determinant and imports the top-only structural
restriction; no lower-pole restriction is imposed.
"""
from pathlib import Path
import ast, datetime, hashlib, json, random, sys, time
import numpy as np

started = time.monotonic()
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=False)
author = Path(sys.argv[2]).resolve()
root = Path(__file__).resolve().parents[3]
packet = root / 'results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'
pin = 'a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
if sha(packet) != pin: raise RuntimeError('Pinned literal connection changed')
data = json.loads(packet.read_text(encoding='utf-8'))
inputs = json.loads((author / 'inputs.json').read_text(encoding='utf-8'))
author_receipt = json.loads((author / 'validation.json').read_text(encoding='utf-8'))
p = 65519; seed = 2026102497; count = 2640
if inputs['prime'] != p or inputs['seed'] != seed:
    raise RuntimeError('Predeclared prime or seed differs')
if any(p % k == 0 for k in range(2, int(p**.5)+1)):
    raise RuntimeError('Modulus is not prime')

def integer(node):
    if isinstance(node, ast.Constant) and type(node.value) is int: return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub): return -integer(node.operand)
    raise RuntimeError('Nonliteral exponent in connection')

def ev(node, env):
    if isinstance(node, ast.Constant) and type(node.value) is int: return node.value % p
    if isinstance(node, ast.Name): return env[node.id] % p
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub): return -ev(node.operand, env) % p
    if not isinstance(node, ast.BinOp): raise RuntimeError('Unsupported literal source syntax')
    x = ev(node.left, env)
    if isinstance(node.op, ast.Pow): return pow(x, integer(node.right), p)
    y = ev(node.right, env)
    if isinstance(node.op, ast.Add): return (x+y) % p
    if isinstance(node.op, ast.Sub): return (x-y) % p
    if isinstance(node.op, ast.Mult): return x*y % p
    if isinstance(node.op, ast.Div): return x*pow(y, -1, p) % p
    raise RuntimeError('Unsupported source operator')

parsed = {name: [[ast.parse(x, mode='eval').body for x in row] for row in mat]
          for name, mat in data['connection'].items()}
dtree = ast.parse(data['Delta'], mode='eval').body
basis = [['h7', -1, j, m, n, k] for j in range(2)
         for m in range(-10, -5) for n in range(2) for k in range(3)]
basis += [['k7', 2, j, m, n, k] for j in range(2)
          for m in range(-10, 3) for n in range(3) for k in range(3)]
for sector in ['P6', 'P5', 'P4', 'P3', 'P2', 'P1', 'P0']:
    basis += [[sector, direction, j, m, n, k] for direction in range(3)
              for j in range(2) for m in range(-10, 3)
              for n in range(3) for k in range(3)]
if len(basis) != 5208 or inputs['basis'] != basis:
    raise RuntimeError('Wrong family, lower-sector restriction, or basis order')
if inputs['matrix_shape'] != [5280, 5209]:
    raise RuntimeError('Wrong declared matrix shape')

def evaluate(point):
    r, v, t = point; q = r*v-1
    A = (pow(r, 3, p)+pow(r, -3, p)+pow(q, 6, p)*pow(r, -15, p)) % p
    Ar = (3*r*r-3*pow(r, -4, p)+6*v*pow(q, 5, p)*pow(r, -15, p)
          -15*pow(q, 6, p)*pow(r, -16, p)) % p
    Av = 6*pow(q, 5, p)*pow(r, -14, p) % p
    c = t*(1-t*t)*pow(7, -1, p) % p; d = (1+pow(t, 6, p)) % p
    env = {'a': A, 'b': t*v % p, 'c': c, 'd': d}
    Delta = ev(dtree, env)
    if not A or not Delta: raise ValueError('Excluded A or Delta divisor')
    M = {name: [[ev(x, env) for x in row] for row in mat] for name, mat in parsed.items()}
    return A, Ar, Av, Delta, M

matrix = np.empty((5280, 5209), dtype='<u2')
rng = random.Random(seed); rebuilt_samples = []; excluded = []; controls = {}
while len(rebuilt_samples) < count:
    point = [rng.randrange(1, p) for _ in range(3)]
    try: A, Ar, Av, Delta, M = evaluate(point)
    except (ValueError, ZeroDivisionError): excluded.append(point); continue
    r, v, t = point; number = len(rebuilt_samples)
    domain = {'a': A, 'Ar': Ar, 'Av': Av, 'Delta': Delta}
    rebuilt_samples.append({'point': point, 'domain': domain})
    invA = pow(A, -1, p); Ai = [Ar, Av, 0]
    cp = (1-3*t*t)*pow(7, -1, p) % p; dp = 6*pow(t, 5, p) % p
    N = [[[Ar*M['a'][i][j] % p for j in range(2)] for i in range(2)],
         [[(Av*M['a'][i][j]+t*M['b'][i][j]) % p for j in range(2)] for i in range(2)],
         [[(v*M['b'][i][j]+cp*M['c'][i][j]+dp*M['d'][i][j]) % p for j in range(2)] for i in range(2)]]
    Tr = r*r*(pow(r, 6, p)+1) % p
    Tv = (r*(2*pow(r, 6, p)+1)*v-(3*pow(r, 6, p)+2)) % p
    ell = 3*r*(pow(r, 6, p)-1) % p
    tau = (-11*pow(r, 7, p)+24*r) % p
    if (Tr*Ar+Tv*Av-ell*A) % p: raise RuntimeError('Top tangency sample binding failed')
    direct_tau = (10*pow(r, 7, p)+3*r-7*(Tr*Ar+Tv*Av)*invA) % p
    if direct_tau != tau: raise RuntimeError('A7 quotient zero-order binding failed')
    H = [[(ell*A*M['a'][i][j]+t*Tv*M['b'][i][j]+(tau if i == j else 0)) % p
          for j in range(2)] for i in range(2)]
    for i in range(2):
        for j in range(2):
            if (Tr*N[0][i][j]+Tv*N[1][i][j]+(direct_tau if i == j else 0)-H[i][j]) % p:
                raise RuntimeError('Reduced W7 connection does not match direct connection')
    # Cache only powers; derivatives use explicitly lowered exponent triples.
    rp = {e: pow(r, e, p) for e in range(-11, 4)}
    vp = {e: pow(v, e, p) for e in range(-1, 4)}
    tp = {e: pow(t, e, p) for e in range(-1, 4)}
    scales = {'P6': A, 'P5': A*A % p, 'P4': pow(A, 3, p), 'P3': pow(A, 4, p), 'P2': pow(A, 5, p), 'P1': pow(A, 6, p), 'P0': pow(A, 7, p), 'k7': 1}
    for column, (sector, direction, j, m, n, k) in enumerate(basis):
        mon = rp[m]*vp[n]*tp[k] % p
        if sector == 'h7':
            deriv = (Tr*m*rp[m-1]*vp[n]*tp[k]+Tv*n*rp[m]*vp[n-1]*tp[k]) % p
            for i in range(2): matrix[2*number+i, column] = (H[i][j]*mon+(deriv if i == j else 0)) % p
        else:
            exponents = [m, n, k]; lower = exponents.copy(); lower[direction] -= 1
            deriv = exponents[direction]*rp[lower[0]]*vp[lower[1]]*tp[lower[2]] % p
            order = int(sector[1:]) if sector.startswith('P') else 0
            for i in range(2):
                value = N[direction][i][j]*mon+(deriv if i == j else 0)
                if i == j: value -= order*Ai[direction]*invA*mon
                matrix[2*number+i, column] = scales[sector]*value % p
    target = [pow(A, 7, p)*pow(r, -4, p)*pow(12, -1, p)*M['b'][i][0] % p for i in range(2)]
    matrix[2*number:2*number+2, -1] = target

    # Each control changes one actual representative entry. A control passes
    # only when its mutated entry differs, rather than from its label alone.
    unit = rp[-10]
    top = int(matrix[2*number, 0])
    def control(name, expected, mutated):
        delta = (int(mutated)-int(expected)) % p
        if name not in controls and delta:
            controls[name] = {'point': point, 'expected': int(expected) % p,
                              'mutated': int(mutated) % p, 'difference': delta}
    control('replace_top_7_by_6', top, top+unit*ell)
    control('omit_top_r_quotient_term', top, top+7*unit*Tr*Ar*invA)
    control('omit_top_v_quotient_term', top, top+7*unit*Tv*Av*invA)
    control('reverse_top_quotient_sign', top, top+14*unit*ell)
    for sector, order in [('P6', 6), ('P5', 5), ('P4', 4), ('P3', 3), ('P2', 2), ('P1', 1)]:
        start_column = 294+702*(6-order)
        for direction, suffix in [(0, 'r'), (1, 'v')]:
            index = start_column+direction*234
            correct = int(matrix[2*number, index])
            control('omit_'+sector+'_'+suffix+'_quotient_term', correct,
                    correct+scales[sector]*order*Ai[direction]*invA*unit)
    control('omit_Av_connection_chain', top, top-unit*Tv*Av*M['a'][0][0])
    k7_entry = int(matrix[2*number, 60])
    for name, factor in [('b', v), ('c', cp), ('d', dp)]:
        control('omit_Nt_'+name+'_term', k7_entry, k7_entry-factor*M[name][0][0]*unit)
    control('omit_source_1_over_12', target[0], 12*target[0])
    control('reverse_source_sign', target[0], -target[0])
    k7_t_entry = int(matrix[2*number, 61])
    control('omit_k7_t_derivative', k7_t_entry, k7_t_entry-unit)

if rebuilt_samples != inputs['samples']: raise RuntimeError('Independent random sample/domain sequence mismatch')
if excluded != inputs['excluded_points']: raise RuntimeError('Independent rejected-point sequence mismatch')
if len(controls) != 23: raise RuntimeError('A mutation failed to discriminate')
binary = author / 'augmented-matrix.u16.bin'
saved = binary.read_bytes()
rebuilt = matrix.tobytes(order='C')
if len(saved) != 5280*5209*2 or saved != rebuilt:
    raise RuntimeError('Full augmented binary matrix mismatch')
result = {
    'status': 'PASS_INDEPENDENT_A7_MATRIX_RECONSTRUCTION',
    'executor': 'a7_denominator_checker AI worker',
    'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'seconds': time.monotonic()-started, 'python': sys.version, 'numpy': np.__version__,
    'packet_sha256': pin, 'script_sha256': sha(Path(__file__)),
    'author_matrix_validation_sha256': sha(author/'validation.json'),
    'inputs_sha256': sha(author/'inputs.json'), 'matrix_sha256': sha(binary),
    'independently_reconstructed_bytes_sha256': hashlib.sha256(rebuilt).hexdigest(),
    'matrix_format': 'row-major little-endian unsigned 16-bit integers, no header',
    'matrix_shape': [5280, 5209], 'entries_reconstructed': int(matrix.size),
    'domain_points_checked': count, 'excluded_points_independently_reconstructed': excluded,
    'prime': p, 'seed': seed, 'mutations_detected': len(controls), 'mutations': controls,
    'structural_dependency': 'Imported top-only pole restriction and reused bounded tangent support; not reproved here.',
    'scope': 'All entries, all samples, basis order, and full source reconstructed. No determinant executed by this process. All 4914 lower parameters remain free; source coefficient convention and both output rows retained.',
}
(out/'validation.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
print(json.dumps(result, indent=2))

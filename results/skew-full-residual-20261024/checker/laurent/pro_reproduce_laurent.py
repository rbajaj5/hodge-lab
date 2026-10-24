import ast, hashlib, json, random, sys
from pathlib import Path
import numpy as np

p = 32003
path = Path(sys.argv[1])
pin = "a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d"
if hashlib.sha256(path.read_bytes()).hexdigest() != pin:
    raise RuntimeError("Connection SHA256 mismatch")
data = json.loads(path.read_text(encoding="utf-8"))

def literal(n):
    if isinstance(n, ast.Constant) and type(n.value) is int:
        return n.value
    if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
        return -literal(n.operand)
    raise RuntimeError("Noninteger exponent")

def ev(n, e):
    if isinstance(n, ast.Constant) and type(n.value) is int:
        return n.value % p
    if isinstance(n, ast.Name):
        return e[n.id] % p
    if isinstance(n, ast.UnaryOp) and isinstance(n.op, ast.USub):
        return -ev(n.operand, e) % p
    if not isinstance(n, ast.BinOp):
        raise RuntimeError("Unsupported source syntax")
    x = ev(n.left, e)
    if isinstance(n.op, ast.Pow):
        return pow(x, literal(n.right), p)
    y = ev(n.right, e)
    if isinstance(n.op, ast.Add): return (x+y) % p
    if isinstance(n.op, ast.Sub): return (x-y) % p
    if isinstance(n.op, ast.Mult): return x*y % p
    if isinstance(n.op, ast.Div): return x*pow(y, -1, p) % p
    raise RuntimeError("Unsupported operator")

tree = {
    k: [[ast.parse(z, mode="eval").body for z in row] for row in mat]
    for k, mat in data["connection"].items()
}
dtree = ast.parse(data["Delta"], mode="eval").body
basis = [
    (i, j, m, n, k)
    for i in range(3) for j in range(2)
    for m in range(-10, 3) for n in range(3) for k in range(3)
]
rng = random.Random(2026102415)
rows = []

while len(rows) < 704:
    r, v, t = [rng.randrange(1, p) for _ in range(3)]
    h = v*r-1
    A = (r**3 + pow(r, -3, p)
         + pow(h, 6, p)*pow(r, -15, p)) % p
    Ar = (3*r*r - 3*pow(r, -4, p)
          + 6*v*pow(h, 5, p)*pow(r, -15, p)
          - 15*pow(h, 6, p)*pow(r, -16, p)) % p
    Av = 6*pow(h, 5, p)*pow(r, -14, p) % p
    e = dict(a=A, b=t*v % p,
             c=t*(1-t*t)*pow(7, -1, p) % p,
             d=(1+pow(t, 6, p)) % p)
    if not A or not ev(dtree, e):
        continue
    M = {
        k: [[ev(z, e) for z in row] for row in mat]
        for k, mat in tree.items()
    }
    N = [
        [[Ar*M["a"][i][j] % p for j in range(2)]
         for i in range(2)],
        [[(Av*M["a"][i][j]+t*M["b"][i][j]) % p
          for j in range(2)] for i in range(2)],
        [[(v*M["b"][i][j]
           + ((1-3*t*t)*pow(7, -1, p) % p)*M["c"][i][j]
           + 6*pow(t, 5, p)*M["d"][i][j]) % p
          for j in range(2)] for i in range(2)]
    ]
    rr = [[], []]
    for direction, j, m, n, k in basis:
        ex = [m, n, k]
        mon = pow(r, m, p)*pow(v, n, p)*pow(t, k, p) % p
        derivative = ex[direction]*mon*pow([r, v, t][direction], -1, p) % p
        for i in range(2):
            rr[i].append(
                (N[direction][i][j]*mon
                 + (derivative if i == j else 0)) % p
            )
    for i in range(2):
        rows.append(rr[i] + [
            pow(r, -4, p)*pow(12, -1, p)*M["b"][i][0] % p
        ])

H = np.array(rows[:703], dtype=np.int64)
previous, sign = 1, 1
if 2*(p-1)**3 >= 2**63:
    raise RuntimeError("Overflow bound failed")

for k in range(702):
    nz = np.flatnonzero(H[k:, k])
    if not len(nz):
        raise RuntimeError("Singular minor")
    j = k+int(nz[0])
    if j != k:
        H[[k, j]] = H[[j, k]]
        sign = -sign
    pivot = int(H[k, k])
    H[k+1:, k+1:] = (
        (pivot*H[k+1:, k+1:]
         - H[k+1:, k, None]*H[k, k+1:])
        * pow(previous, -1, p)
    ) % p
    H[k+1:, k] = 0
    previous = pivot

det = sign*int(H[-1, -1]) % p
if det != 13884:
    raise RuntimeError("Expected determinant was not reproduced")
print(dict(prime=p, coefficient_columns=len(basis),
           minor_size=703, determinant=det))

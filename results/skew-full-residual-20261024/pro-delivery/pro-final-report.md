## Outcome

**No rational primitive was found.** This batch produced two precise exclusions of current families while retaining both compact rows and all physical derivatives:

1. **The displayed universal mixed first-jet family has no rational completion \(K\in\mathbf Q(a,v,t)^2\).**
2. **The declared 702-coefficient family of six physical Laurent flux components is inconsistent over characteristic zero.**

The triangular candidate was also tested and rejected exactly. Its initially dispatched sign error is preserved separately from the corrected calculation. None of these results excludes arbitrary rational mixed currents.

Mathematical work stopped at **11:32:59 a.m. EDT / 15:32:59 UTC on 24 October**, before the authorized deadline. Packaging and patch verification finished at **15:37:14 UTC**. No Lean, commit, push or upstream action occurred. The coordinator’s broader Goal remains open.

## Downloadable handoff

This is a **fresh, changed-file-only packet**, not a re-export of the previous ZIP.

| Artifact | Contents |
|---|---|
| :chatgpt-content-reference{index="0"}[mixed-construction.zip](sandbox:/workspace/scratch/b8974c152662/handoff-mixed-construction-20261024/mixed-construction.zip) | 1.73 MB; 107 added files, including scripts, receipts, failures, exact matrices, scoped note and reproducible figure |
| :chatgpt-content-reference{index="1"}[mixed-construction.patch](sandbox:/workspace/scratch/b8974c152662/handoff-mixed-construction-20261024/mixed-construction.patch) | Binary-safe patch against the exact parent |
| :chatgpt-content-reference{index="2"}[HANDOFF.txt](sandbox:/workspace/scratch/b8974c152662/handoff-mixed-construction-20261024/HANDOFF.txt) | Compact integration account |
| :chatgpt-content-reference{index="3"}[MANIFEST.sha256](sandbox:/workspace/scratch/b8974c152662/handoff-mixed-construction-20261024/MANIFEST.sha256) | Per-payload-file hashes |
| :chatgpt-content-reference{index="4"}[expected-tree.json](sandbox:/workspace/scratch/b8974c152662/handoff-mixed-construction-20261024/expected-tree.json) | Parent and expected staged tree |
| :chatgpt-content-reference{index="5"}[packaging-verification.json](sandbox:/workspace/scratch/b8974c152662/handoff-mixed-construction-20261024/packaging-verification.json) | ZIP, hashes, UTF-8, staged-byte and forward-application checks |
| :chatgpt-content-reference{index="6"}[SHA256SUMS.txt](sandbox:/workspace/scratch/b8974c152662/handoff-mixed-construction-20261024/SHA256SUMS.txt) | Hashes of the handoff artifacts |

```text
Exact parent:
84f294e0235c3fd4b5d4849e565536172a74329c

Expected staged tree:
6a36bc10eb2a2463a38f8c570ceccaf7ef539f5b
```

The patch was applied to a **separate temporary index initialized at that parent**, and it produced the expected tree. All ZIP member hashes and text encodings passed. README, ledger, team board, historical results and formal code are outside the patch. No old repository, cache, Git database or expanded submodule is included.

The staged whitespace check returned exit 2 **solely for Matplotlib-generated trailing spaces in SVG path data**. Its output is retained in :chatgpt-content-reference{index="7"}[staged-whitespace.log](sandbox:/workspace/scratch/b8974c152662/handoff-mixed-construction-20261024/staged-whitespace.log); I have not described that check as passing.

### Artifact SHA256s

```text
mixed-construction.zip
9441abd9f0aea4454bd98bf98c21e280ebf58d701d9fd54911b170a29432009d

mixed-construction.patch
671acb8dc9ccf86b07b8ccfca81dd79f709d435b833c01ac6749f0aec4dcacc0

MANIFEST.sha256
94a2b5ac5647eb3ff23d744dbdd5e7b7161944f2697f37ad0a9d59fffda91b31
```

## 1. Full source and coordinate convention

Everything uses the pinned compact connection, with SHA256

```text
a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d
```

The convention is the packet’s **positive source orientation**, ordered basis
\[
(e_0,e_1)=\left(\frac{dV}{z^5},\frac{V\,dV}{z^5}\right),
\]
matrix columns indexing inputs, and coefficient connection \(d+N\).

Write
\[
A(r,v)=r^3+r^{-3}+\frac{(vr-1)^6}{r^{15}},
\qquad
b=tv,\quad c=\frac{t(1-t^2)}7,\quad d=1+t^6.
\]
The base connection is
\[
N_a=M_a,\qquad N_v=tM_b,\qquad
N_t=vM_b+c'M_c+d'M_d.
\]

For a base-coordinate flux \(J=(J_a,J_v,J_t)\), the corresponding physical flux is
\[
F=(J_a-A_vJ_v,\ A_rJ_v,\ A_rJ_t).
\]
Thus the actual equation tested directly in \((r,v,t)\) is
\[
\boxed{
\sum_{i=r,v,t}(\partial_i+\widetilde N_i)F_i
=\frac{r^{-4}}{12}M_be_0,
\qquad
\widetilde N=(A_rM_a,\ A_vM_a+tM_b,\ N_t).
}
\]
This retains the \(A_vM_a\) chain term, both compact rows, the \(t\)-connection and every flux derivative. It is not a trace projection.

The identities are rational function-field statements on their stated common open. The existing regular-localization boundary is unchanged. The full source normalization and earlier \(Q/R_2\) calculation are reused inputs, not new executions. See the :chatgpt-content-reference{index="8"}[scoped mathematical note](sandbox:/workspace/scratch/b8974c152662/hodge-lab-mixed-next/notes/skew-mixed-construction-20261024.md).

## 2. Triangular candidate: sign failure preserved, corrected current rejected

For
\[
C=\frac{t(1-t^2)}7,\quad D=1+t^6,\quad
K_0=C^2-3tvD,\quad
w=CC'-2tvD',\quad q=3DC'-2CD',
\]
the **corrected** field is
\[
G_a=0,\qquad
G_v=-tvw+3aq+2vK_0,\qquad
G_t=-2tK_0.
\]
It satisfies
\[
G_vN_v+G_tN_t=
\Gamma=
\begin{pmatrix}
3tw/2&-tq\\
0&tw/2
\end{pmatrix}.
\]

The initially supplied signs
\[
G_v=-tvw+3aq-2vK_0,\qquad G_t=2tK_0
\]
failed the literal matrix check. Those sources and failures remain in the packet. They are not counted as valid identities.

Let
\[
\chi=r^{-3}-v^3/3,\qquad
R_2=\alpha\chi_{vv}+\beta(v\chi_v-\chi),
\]
where
\[
\alpha=\frac{N_te_1+ve_0/(3a)}{36t},
\qquad
\beta=\frac{M_be_0}{108a}.
\]
With
\[
\mathcal D=G_v\partial_v+G_t\partial_t,\qquad
\mathcal K=(\partial_vG_v+\partial_tG_t)I+\Gamma,
\]
the explicit tested coefficients were
\[
S=\frac{\alpha}{G_v},\qquad
T=\frac{v\beta-\mathcal DS-\mathcal KS}{G_v},
\]
and
\[
J_a=0,\quad
J_v=G_v(S\chi_v+T\chi),\quad
J_t=G_t(S\chi_v+T\chi).
\]

The full residual identity is
\[
R_2-\operatorname{Div}_NJ
=\chi\bigl(-\beta-\mathcal DT-\mathcal KT\bigr).
\]

At the allowed physical point
\[
(r,v,t,a)=(1,2,1,3),
\]
the corrected quantities are
\[
(G_v,G_t)=(-108/7,24),\qquad
\Gamma=
\begin{pmatrix}-36&12/7\\0&-12\end{pmatrix}.
\]
The exact surviving vector is
\[
\boxed{
R_2-\operatorname{Div}_NJ=
\begin{pmatrix}
-\dfrac{242298600715}{34686091188}\\[2pt]
 \dfrac{255188727685}{15416040528}
\end{pmatrix}\ne0.
}
\]

A separate AI checker obtained this through exact finite Taylor arithmetic and rejected the candidate at a second point with \(t=2\). Controls detect omitted root motion, omitted \(t\)-differentiation, omitted \(t\)-connection and transposed matrices. The author’s generic expression expansion timed out at 60 seconds; the rejection rests on the completed checker, not that interruption. :chatgpt-content-reference{index="9"}[Exact receipt](sandbox:/workspace/scratch/b8974c152662/hodge-lab-mixed-next/results/skew-mixed-construction-20261024/checker/translation-current-02/result/validation.json)

This candidate adds \(G_v^{-1}\). Its removal of \(\chi_v,\chi_{vv}\) from the survivor is **not promoted as a new exactness result or a necessary improvement over the simpler integration-by-parts baseline**.

## 3. A complete obstruction for one universal mixed family

The complementary construction tested
\[
J_a=0,\qquad
J_v=\frac{\chi_ve_1}{36t^2}-\frac{\chi M_ae_0}{36t},
\qquad
J_t=\chi K(a,v,t),
\]
with an arbitrary rational two-vector \(K\).

Put
\[
T_0=\frac{(\partial_bM_a+M_bM_a)e_0}{36}.
\]
The exact full identity is
\[
\boxed{
\operatorname{Div}_NJ-R_0
=\chi\bigl((\partial_t+N_t)K-T_0\bigr),
\qquad R_0=\frac{\chi_{vv}}{36t^2}e_1.
}
\]

For the requested \(R_2\) equation directly, subtract the already checked \(Y\):
\[
\begin{aligned}
Z_a&=0,\\
Z_v&=\frac{\chi_ve_1}{36t^2}
-\frac{\chi M_ae_0}{36t}
+\frac{(v\chi_v-\chi)e_0}{108at},\\
Z_t&=\chi K+\frac{\chi_{vv}e_1}{36t}.
\end{aligned}
\]
Then
\[
R_2-\operatorname{Div}_NZ
=\chi\bigl(T_0-(\partial_t+N_t)K\bigr).
\]

The full-matrix equation for \(K\) has **no rational solution in \(\mathbf Q(a,v,t)^2\)**:

- At a simple discriminant root, the connection residue has eigenvalues \(0,-1/3\). Since \(T_0\) has at most a double pole, \(K\) can have at most a simple discriminant pole.
- No other finite poles are possible.
- The gauge \(\operatorname{diag}(t^{-3},t^{-1})\) gives connection \(O(t^{-2})\) and target \(O(t^{-6})\). Consequently
  \[
  K=\frac{(P_0,P_1)^T}{\Delta_{\mathrm{monic}}},
  \qquad \deg P_0\le15,\quad \deg P_1\le13.
  \]
- At \((a,v)=(3,2)\), the resulting exact \(52\times30\) system has coefficient rank \(30\) and augmented rank \(31\). A separate checker rebuilt the system and an integer left-null inconsistency witness.
- The generic system is regular there, and a \(30\times30\) minor is nonzero there. Cramer’s rule forces any hypothetical generic solution to specialize regularly, closing the specialization-pole loophole.

This is a complete exclusion **of this displayed universal first-jet family**. It is not an exclusion of general physical currents, and it is distinct from the old t-only \(R_2\) calculation, which was not rerun. :chatgpt-content-reference{index="10"}[Author proof and limits](sandbox:/workspace/scratch/b8974c152662/hodge-lab-mixed-next/results/skew-mixed-construction-20261024/alternate/HANDOFF.txt) · :chatgpt-content-reference{index="11"}[Independent system certificate](sandbox:/workspace/scratch/b8974c152662/hodge-lab-mixed-next/results/skew-mixed-construction-20261024/checker/first-jet-system-02/result/validation.json)

## 4. Direct physical search: exact exclusion of the declared Laurent family

Each of the six physical flux components was independently allowed to belong to
\[
\mathcal V=
\operatorname{span}_{\mathbf Q}
\left\{
r^m v^n t^k:
-10\le m\le2,\quad 0\le n,k\le2
\right\}.
\]
There are \(117\) monomials per component, hence **702 unknown coefficients**.

This family uses the actual physical source equation above. It imposes no beta-current, fixed-\(L\), single-row or arbitrary-\(\chi\) restriction. It does impose explicit pole and degree restrictions: the current has only Laurent poles at \(r=0\), with the displayed bounded \(v,t\)-dependence.

The deterministic sample matrix has size \(762\times703\). The separate checker reconstructed all its entries from the literal JSON using different evaluation and differentiation code. It then verified
\[
\boxed{
\det(\text{first 703 augmented rows})
=13884\pmod{32003}\ne0.
}
\]

Therefore the rational augmented matrix has rank at least \(703\), with only \(702\) coefficient columns. **No current in this declared family solves the equation over \(\mathbf Q\), or after extension of the constant field.**

This inference uses a nonzero minor of the given rational matrix. It does not assume that denominators of unknown solution coefficients are prime to \(32003\). :chatgpt-content-reference{index="12"}[Independent physical certificate](sandbox:/workspace/scratch/b8974c152662/hodge-lab-mixed-next/results/skew-mixed-construction-20261024/checker/physical-laurent-01/result/validation.json)

## Plain-text fallback: reconstruct the decisive physical certificate

The following code reconstructs the minor **from the pinned connection JSON alone**. It does not need the ZIP, saved CSV, previous packet or local cache. It is also saved as :chatgpt-content-reference{index="13"}[reproduce_laurent.py](sandbox:/workspace/scratch/b8974c152662/hodge-lab-mixed-next/results/skew-mixed-construction-20261024/reproduce_laurent.py).

Run it with NumPy under the same process bound:

```sh
timeout 60s python3 -O reproduce_laurent.py \
  results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json
```

Expected result:

```text
prime=32003
coefficient_columns=702
minor_size=703
determinant=13884
```

```python
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
```

### Essential first-jet system formula

The second certificate can also be reconstructed directly from the JSON. At \(a=3,v=2\), let \(\delta\) be the monic discriminant and \(N=\delta N_t\). For
\[
K=P/\delta,
\]
the equation is
\[
\delta P'+(N-\delta'I)P=\delta^2T_0.
\]
For columns \(P=t^ke_j\), the coefficient recurrence is
\[
A_{(i,n),(j,k)}
=[t^{n-k}]N_{ij}
+(2k-n-1)[t^{n-k+1}]\delta\,\delta_{ij}.
\]
Use \(k=0,\dots,15\) for \(j=0\), and \(k=0,\dots,13\) for \(j=1\). The exact result is:

```text
shape(A) = (52, 30)
rank_Q(A) = 30
rank_Q([A | rhs]) = 31
```

The saved checker additionally supplies an integer vector \(w\) with \(wA=0\) and \(w\,\mathrm{rhs}\ne0\). The pole and Cramer arguments above are essential to extending this finite calculation to all rational \(K\) in the displayed universal family.

## Executions, visualization and remaining dependency

The principal new executions are kept separate:

| Execution | Executor | Wall time | Outcome |
|---|---|---:|---|
| Corrected triangular current, full finite-jet check | Separate AI checker | 0.817 s | Exact nonzero residual at two physical points |
| First-jet coefficient system | Complementary AI author | 1.368 s | Exact ranks \(30/31\) |
| Structured generic pole/degree certificate | Complementary AI author | 0.816 s | Rational-\(K\) bounds and scope established |
| Independent first-jet reconstruction | Separate AI checker | 1.017 s | Matrix and left-null witness verified |
| Physical Laurent search | Constructive lead | 1.471 s | \(702/703\) ranks |
| Independent physical reconstruction/minor | Separate AI checker | 1.624 s | All entries reconstructed; determinant \(13884\) |
| Plain-text export reproduction | Constructive lead | 1.426 s | Standalone verifier reproduced the determinant |

Two expanded symbolic attempts reached their 60-second limits and remain recorded as interruptions. The sign-gate failures and the checker’s initial Python implementation error are also retained. These are separate AI computations, not independent human review. Reused receipts and user-relayed external results are not included in these execution claims.

The :chatgpt-content-reference{index="14"}[final PNG](sandbox:/workspace/scratch/b8974c152662/hodge-lab-mixed-next/results/skew-mixed-construction-20261024/figure-02/result/full-residuals.png) was inspected. Its :chatgpt-content-reference{index="15"}[generator](sandbox:/workspace/scratch/b8974c152662/hodge-lab-mixed-next/results/skew-mixed-construction-20261024/render.py) reads the saved exact residuals; the accompanying receipt binds its inputs and outputs. The figure illustrates point witnesses, not generic solvability or an optimization score.

The remaining dependency is an **actual rational mixed current outside the rejected families**, checked against the full two-row source. The new generic discriminant-image compatibility relayed by the coordinator remains useful local information; it neither contradicts these scoped obstructions nor supplies global cancellation.

A concrete next finite test would allow a justified additional denominator—such as \(A(r,v)\)—in the physical Laurent family, while retaining all six fluxes and explicitly accounting for any exact kernel before interpreting modular ranks. That test was **not run** here. Scalar trace zero, local residue compatibility, source exactness, a rational primitive, global clearing and a certificate remain distinct obligations.

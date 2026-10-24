# One-reflection-skew: the bounded A-cubed mixed family is excluded

24 October 2026 EDT. **The declared full six-component family
(B+B/A+B/A²+B/A³)^6 is excluded over Q. No rational primitive was found.**
The result retains both source rows, every physical derivative and every
lower-sector coefficient. It is not a general rational-current obstruction.

Public integration parent: `2dff6afddab993a216ba3f262197ae69aeb9143a`.
Actual available isolated working checkout: `fc4f38a338b47addf62d1bf699783302285378fe`.
Current policy, team board, A2 note, recent ledger and connection were read
through the read-only GitHub connector. The cached connection was byte-equal
to the live integration-parent file, SHA256
`a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d`.
The full newer parent was not materialized; no parent-plus-payload Git tree
is claimed. The changed-file manifest is sufficient for coordinator integration.
No known failed Git proxy/direct route was retried.

Upstream dispatch pin remains `27f4bb9ad8757e5841f884d9d30124a3c97a847d`.
Completed A/A² divisor, tangent-support and source checks, Q/R2, beta, trace,
old determinants and Lean are reused evidence and were not rerun.

## Explicit family and unchanged physical source

Define

\[
B=\operatorname{span}_{\mathbf Q}\{r^m v^n t^k:
-10\le m\le2,\quad0\le n,k\le2\},
\qquad A=r^3+r^{-3}+(rv-1)^6/r^{15}.
\]

Before computation, enlarge the requested B/A³ family to the direct sum
B+B/A+B/A²+B/A³ in each of the six scalar current components. Write
F=P0+P1/A+P2/A²+P3/A³. There are2808 scalar parameters. After multiplying
an input relation by A³, its nonzero leading v-degree bands are18–20,
12–14,6–8,0–2; descending by degree proves directness. Input independence
does not by itself prove operator injectivity.

The full physical equation stays

\[
\sum_{i=r,v,t}(\partial_i+\widetilde N_i)F_i=S,
\qquad S=r^{-4}M_be_0/12,
\qquad\widetilde N=(A_rM_a,A_vM_a+tM_b,N_t),
\]
\[
b=tv,\quad c=t(1-t^2)/7,\quad d=1+t^6,
\qquad N_t=vM_b+c'M_c+d'M_d.
\]

The packet's positive orientation and ordered input columns e0,e1 are used.
Both compact output rows and all r,v,t chain terms are present. A_t=0;
the full Nt is retained. The top quotient derivative is -3A_i/A⁴ for
i=r,v. All lower quotient corrections remain. A is a chart coefficient,
distinct from protected source X0³Y0³; the unchanged target has q=1.
The established regular-localization boundary is unchanged. Scalar trace
zero is not full-source exactness or a primitive.

The ansatz permits current poles only along r=0 and A=0, with A-order≤3.
The connection/source domain also excludes Delta=0. Finite samples choose
nonzero v,t to simplify evaluation; this does not add v or t denominators to
the ansatz. No inverse A_r is used.

## Imported top-pole rule; all lower sectors remain free

The coordinator supplied the new highest-pole argument and subsequently
reported seven minimal exact checks and two controls. At generic A=0,

\[
R_a=\begin{pmatrix}0&-c/(6b)\\0&-1/3\end{pmatrix},
\qquad\det(R_a-3I)=10.
\]

The order-four coefficient is (Ra-3I)Q3, where
Q3=A_r P3_r+A_v P3_v modulo A. Thus only P3 is forced tangent. Reuse the
established bounded tangent module and support theorem to write

\[
P3=(T_rh_3,T_vh_3,k_3),\quad
T_r=r^2(r^6+1),\quad
T_v=r(2r^6+1)v-(3r^6+2).
\]

Each h3 component has30 monomials: r=-10,…,-6, v=0,1, t=0,1,2.
Each k3 component uses the117-monomial original box. Therefore the top
sector has294 parameters. **P2,P1,P0 retain all702 parameters each**:
the necessary family has2400 parameters and2106 unrestricted lower parameters.
No lower tangency and no separately applied A² projection is imposed.

Let ell=3r(r^6-1), so T(A)=ell A. Then
tau3=div(T)-3ell=r^7+12r and

\[
W_3=[T_r\partial_r+T_v\partial_v+\tau_3I+
\ell AM_a+tT_vM_b]h_3+(\partial_t+N_t)k_3.
\]

The exact scaled equation is

\[
A^3\operatorname{Div}P0+A^2\operatorname{Div}P1-AQ1
+A\operatorname{Div}P2-2Q2+W_3=A^3S.
\]

Here Div includes the full physical connection, and
Qj=A_r Pj_r+A_v Pj_v. The next pole condition couples the sectors:
(Ra-2I)Q2+W3|A=0=0. Imposing P2 tangency separately would lose allowed
cancellation. See [STRUCTURAL-DEPENDENCY.md](../results/skew-A3-denominator-20261024/STRUCTURAL-DEPENDENCY.md)
for imported versus executed evidence.

## New deterministic certificate

The [visible-before-packaging specification](../results/skew-A3-denominator-20261024/MATRIX-SPEC.md)
fixes prime32003, Python random.Random seed2026102458,1230 accepted triples,
row0 thenrow1, and columns h3,k3,P2,P1,P0 then the source. Within a sector
the order is direction where applicable, input row, r exponent, v exponent,
t exponent. The full augmented matrix has2460 rows and2401 columns.

The author used direct quotient-rule columns. The separate checker rebuilt
them from literal JSON using an integer-AST evaluator, the reduced W3,
and exponent-lowered derivatives. All5,906,460 entries and1230 domain records
agree. Its separate Bareiss determinant phase gives

\[
\boxed{\det(\text{first2401 augmented rows})=13752\pmod{32003}\ne0.}
\]

The selected row order has four inversions, so the determinant in original
first2401-row order is the same. The coefficient rank is2400 and augmented
rank2401. All evaluated denominators are units modulo the prime. Consequently
the same rational sample matrix has a nonzero augmented minor, and its2400
coefficient columns cannot span the source. This excludes any full rational
identity in the necessary family. No reduction of hypothetical solution
coefficients modulo the prime is assumed.

The imported highest-pole theorem extends the exclusion to all2808 original
parameters, including the requested B/A³ family. It also applies to homogeneous
currents. Every possible original-family kernel lies in the tested necessary
family, whose coefficient rank is full. Thus no hidden kernel or redundant
column invalidates the exclusion. A deficient modular rank gap would not
have sufficed; that case did not occur here.

## Executions and evidence boundaries

| Executor / phase | Wall time | Actual result |
| --- | ---: | --- |
| Pro constructive author: new direct-quotient search |31.726 s|2400 coefficient rank,2401 augmented rank; exit0 |
| Separate AI checker: mathematical source reconstruction |7.591 s|All5,906,460 entries and1230 domains;12 controls; exit0 |
| Same checker: Bareiss on the bound reconstructed matrix |38.935 s|Original first2401-row determinant13752; exit0 |

Both checker phases were planned separately before execution, each with its
own60-second watchdog. The second phase computes a determinant and binds the
previously reconstructed CSV by hash; it is not another source reconstruction.
No mathematical process failed or timed out and no repair was needed. All
executions use -O and explicit fail-closed exceptions. Source snapshots,
commands, versions, stdout/stderr, exits and timings are retained.

Twelve controls detect top factor3→2; missing top r/v quotient corrections;
reversed top quotient sign; missing P2 r/v corrections; missing P1 r/v
corrections; missing A_v connection chain; missing1/12; reversed source sign;
and a missing k3 t derivative. These diagnose implementation errors; the
minor establishes the finite-family exclusion.

At17:04 UTC the coordinator independently reported a local regeneration of
the decisive first2401 rows before receiving our author result:5,764,801
entries,1201 admissible points, determinant13752 using python-flint0.9.0
nmod_mat.det in4.453 seconds, with three controls. Its reported script hash
is6a67d1eb51588910446e00de480fc5e170d13b51aaa5f94316f1268113a6acbc;
reported report hash is6c2ed5fc2d425e6c3121ffd481d21b742e335fad9c29754f7bb36f497fa57cfc.
These are **coordinator-reported executions**, not this worker's counts or
files. The coordinator's later direct equality check against the delivered
CSV is IO binding, separately from that earlier mathematical regeneration.
The local algebra's7 checks+2 controls in2.109 seconds are also imported.
No independent human review is claimed.

## Reproduction, visualization and remaining scope

The raw CSV is retained for exact first2401-row comparison. Its SHA256 is
81a5ac8ee1b82bf1e5149e06fe0389c67c6371a058b70f59a84dbfbe256de17b.
The complete basis/sample input SHA256 is
ffbb8171c6480c39960a60bb63e9d974fa4924999e8e536635061f1a512cec8a.
[RUN.md](../results/skew-A3-denominator-20261024/RUN.md) gives fresh-directory
commands. No additional export-verifier replay was run after the decisive pass.

![A-cubed top-pole restriction with three unrestricted lower sectors](../results/skew-A3-denominator-20261024/figure-01/result/A3-denominator-certificate.png)

The [figure generator](../results/skew-A3-denominator-20261024/render.py) reads
the frozen new receipts and saves input/output hashes. The PNG was inspected.
It shows the actual sector restriction and certificate, not a general
rational-current obstruction or transient CI status.

Mathematical work stopped at17:04:26 UTC /13:04:26 EDT, before17:43:06 UTC.
The actual Goal is coordinator-owned; no worker Goal API activation is claimed.
No Lean, old mathematical replay, remote CI, commit, push, upstream post or
shared README/ledger/team-board edit was made. Posts30 and tally30/1/0 are
unchanged by this worker. Publication and coordinator integration are separate
from the new local evidence. The single ZIP contains only new files; no
old archive, repository/cache dump, expanded submodule or redundant patch.

The target remains open. Other numerator supports, other justified pole
divisors, higher powers and arbitrary rational or fibre-dependent currents
remain outside this exclusion. The smallest remaining constructive dependency
is a current outside the exact tested family satisfying the full two-row
identity; another bounded proposal should first respect its coupled pole
conditions. No source exactness, primitive, global clearing, homogeneous
certificate or accepted solve follows. No extra search/refinement was started.

Credit fqlx for the compact connection, benediamond for the physical cover
and earlier reductions, the coordinator's local algebra/checker workers for
the imported pole reasoning and checks, and hodge.computer contributors for
the framework. This batch is AI-assisted work for Ravi Bajaj.

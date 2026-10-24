# One-reflection-skew: the bounded A-squared sum is excluded

24 October 2026 EDT. **No rational full-source current exists in the declared
six-component family B + B/A + B/A². No general rational-primitive obstruction
or solve is claimed.**

Parent `fc4f38a338b47addf62d1bf699783302285378fe`; upstream dispatch pin
`27f4bb9ad8757e5841f884d9d30124a3c97a847d`. The immutable connection JSON has
SHA256 `a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d`.
Prior A-denominator, Q/R2, beta, source/curve/trace and t-only results are reused,
not rerun. Lean remains benched. A is the chart coefficient, not the protected
source polynomial bearing the same letter in the target record.

## Explicit enlarged family and full equation

Let B be the Q-span of r^m v^n t^k with -10≤m≤2 and 0≤n,k≤2, and

\[
A=r^3+r^{-3}+(rv-1)^6/r^{15}.
\]

Before computation, enlarge the requested B/A² sector to the direct sum
**B ⊕ B/A ⊕ B/A²**, independently for all six scalar flux components.
This is 2106 parameters. In A²P0+AP1+P2, a nonzero P0 term has leading
v-degree12–14, a nonzero P1 term6–8, and P2 has degree≤2; descending by
degree proves directness. This is independence of inputs, not an assertion
about the differential operator's kernel.

The equation remains

\[
\sum_{i=r,v,t}(\partial_i+\widetilde N_i)F_i
=r^{-4}M_be_0/12,\qquad
\widetilde N=(A_rM_a,A_vM_a+tM_b,N_t),
\]
\[
b=tv,\quad c=t(1-t^2)/7,\quad d=1+t^6,\quad
N_t=vM_b+c'M_c+d'M_d.
\]

The literal packet's positive orientation, ordered input columns and both
compact rows are retained. The physical derivatives include every chart
chain term. Top-sector quotient derivatives contain -2A_i/A³ for i=r,v;
A_t=0. P1 contains its own -A_i/A² terms. The ansatz allows poles only on
r=0 and A=0, now of A-order at most2. Sampling also avoids the connection
discriminant Δ=0. Nonzero v,t sample choices allow convenient arithmetic;
they do not introduce v or t denominators into the ansatz. A_r is not inverted.
This is not scalar trace projection; the established common-localization
boundary and distinction from the full two-row source remain in force.

## Only the highest pole is forced tangent

Write F=P0+P1/A+P2/A² and Q2=A_r P2_r+A_v P2_v. The coordinator supplied
the top-pole reasoning and separate structural review. At the generic A divisor,

\[
R_a=\begin{pmatrix}0&-c/(6b)\\0&-1/3\end{pmatrix},
\qquad\det(R_a-2I)=14/3.
\]

Thus the A^-3 coefficient (R_a-2I)Q2 forces Q2=0 modulo A. Neither the source
nor lower sectors can cancel this pole. The previously established bounded
tangent parametrization then gives

\[
P2=(T_rh_2,T_vh_2,k_2),\qquad
T_r=r^2(r^6+1),\quad
T_v=r(2r^6+1)v-(3r^6+2).
\]

Each component of h2 uses r=-10,…,-6, v=0,1, t=0,1,2; k2 has the original
box. There are60 h2 and234 k2 parameters. **All702 P1 and all702 P0
parameters remain free**, giving1698 necessary parameters. The next pole
is coupled: (R_a-I)Q1+W2|A=0=0. Imposing separate P1 tangency would be
unjustified. The later supplied refinement h2_second_row divisible by v,
which would reduce1698 to1683, is explicitly unused in this certificate.

The credited structural dependency is recorded in
[STRUCTURAL-DEPENDENCY.md](../results/skew-A2-denominator-20261024/STRUCTURAL-DEPENDENCY.md).
Its source reasoning is imported, not a fresh execution by this worker.
The old bounded tangent proof and its receipts are already in the parent.

Put ell=3r(r^6-1), so T(A)=ell A. Multiplying the full equation by A² gives

\[
W_2+A\operatorname{Div}_{\widetilde N-d\log A\,I}P1
+A^2\operatorname{Div}_{\widetilde N}P0
=A^2r^{-4}M_be_0/12,
\]
\[
W_2=\left[T_r\partial_r+T_v\partial_v+(4r^7+9r)I
+\ell AM_a+tT_vM_b\right]h_2+(\partial_t+N_t)k_2.
\]

The author generated columns by direct quotient differentiation. The separate
AI checker used this reduced operator, a restricted literal-AST evaluator
and exponent-lowered monomial derivatives. No old determinant was rerun.

## Exact exclusion and kernel accounting

With prime32003 and deterministic seed2026102432, the new sample matrix is
1758×1699 including the source column. The coefficient rank is1698 and
augmented rank1699. The separate checker reconstructed all2,986,842 entries
and all879 sample-domain records, then used modular Bareiss elimination
rather than the author's Gaussian rank search. It found

\[
\boxed{\det(\text{first1699 augmented rows})=14098\pmod{32003}\ne0.}
\]

Every sampled denominator is a unit modulo the prime. Hence this is a nonzero
minor of the corresponding fixed rational matrix. That matrix has only1698
coefficient columns, so its equation is inconsistent over Q. A rational
function identity would hold at every allowed sample, so no current in the
necessary family solves the full equation. The necessary top-pole theorem
extends the exclusion to the original2106-parameter sum, including B/A².
This argument does not require hypothetical solution coefficients to reduce
modulo32003.

There is no overlooked kernel or redundant-column caveat: a homogeneous
current in the original family obeys the same top-pole restriction. Its1698
reduced coefficients vanish by full coefficient rank. Directness of the
sectors and injectivity of the tangent parametrization identify the original
current. No rank-deficient modular gap is promoted to a rational exclusion.

Ten controls discriminate: changing the top quotient factor2 to1, omitting
either top quotient derivative, reversing its sign, omitting either P1
quotient derivative, dropping A_v M_a, omitting1/12, reversing source
orientation, and omitting a k2 t derivative. These controls are diagnostic;
the determinant supplies the finite-family exclusion.

## Executions, source recovery and limits

The author search ran under -O in11.505 seconds wall time, exit0; the separate
checker ran in16.519 seconds, exit0. Each subprocess had a60-second timeout.
No mathematical attempt failed or timed out. These are separate AI executions,
not independent human review. Scripts, snapshots, commands, versions, sample
matrix, minor row order, mutation witnesses and receipts are in
[the fresh result directory](../results/skew-A2-denominator-20261024).

Git transport first failed to reach the sandbox proxy; two bounded public
fetch routes timed out. The public GitHub connector successfully read the
exact parent. Missing objects were recovered through that read-only route,
with every blob hash, tree `fa81edd182774be771a00bf03743c8c8aa1cedbd`, and
existing commit SHA verified before the exact parent was checked out.
No new commit was created. Calculation began during that recovery using
the unchanged pinned connection bytes already cached; final source binding
to the exact parent was checked. The transport failures are retained as such,
not mathematical failures. No authentication retry loop occurred.

Mathematical work stopped at16:38:51 UTC /12:38:51 EDT, before17:17 UTC.
Subsequent verifier export and figure rendering introduce no new search.
The Goal is coordinator-owned; no Goal API is available to this worker.
No Lean, remote CI, commit, push, upstream post, shared README, ledger or
team-board edit was made. Coordinator integration and publication remain
separate from these local checks.

![Top-pole restriction, unrestricted lower sectors, and the exact certificate](../results/skew-A2-denominator-20261024/figure-02/result/A2-denominator-certificate.png)

The [reproducible figure generator](../results/skew-A2-denominator-20261024/render.py)
reads the new frozen receipts. Its final PNG was inspected. The first render
had an overlapping axis annotation and legend; that source, image and receipt
are retained, and the corrected rendering uses a fresh directory. The picture displays
the allowed sectors, necessary restriction and checked determinant; it does
not establish a general nonexistence theorem. The
[standalone plaintext verifier](../results/skew-A2-denominator-20261024/reproduce_minor.py)
needs only NumPy and the pinned connection JSON, not a saved matrix or ZIP.
See [RUN.md](../results/skew-A2-denominator-20261024/RUN.md).

The remaining obstruction is a constructive full-source current outside
this exact support/pole family. A next bounded test must change at least
one restriction, such as numerator support, an additional justified divisor,
or A-pole order. No such next search was started here. The generic coupled
order-two condition remains available for a future construction; its1683
refinement was unnecessary for this exclusion. No source exactness,
primitive, global clearing, certificate or target solve follows.

Credit fqlx for the compact connection, benediamond for the physical cover
and earlier reductions, the coordinator's algebra/checker workers for the
necessary pole reasoning, and the hodge.computer contributors for the
framework. This bounded search is AI-assisted work for Ravi Bajaj.

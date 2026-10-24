# One-reflection-skew: seventh-power denominator current search

24 October 2026. **The declared bounded six-component family through A^-7
is excluded over Q; no primitive was found.** The protected target remains
q=1, source X0^3Y0^3. A below is the separate physical chart coefficient.
Lean stayed benched; this batch is published to Hodge Lab only.

## Bounded question and pinned inputs

The actual Goal started at 18:08:45 UTC with a 45-minute research allowance,
then at most 15 minutes integration. Each mathematical process has a
60-second limit and each network operation a 45-second limit. The
[existing Pro chat](https://chatgpt.com/c/6adb94ec-665c-8325-9a4b-2b4237c63f19)
is mathematical lead; a local algebra worker derives the changed pole
identity and a separate local checker reconstructs the decisive minor.
The coordinator alone integrates shared status and the append-only ledger.

Notebook parent: `030d13b75270f6ad1a774e9c11321038fe6305e9`.
Fresh upstream: `27f4bb9ad8757e5841f884d9d30124a3c97a847d`.
The [literal connection](../results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json)
has SHA256 `a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d`.
The completed [divisor/module/support arguments](skew-A-denominator-audit-20261024.md),
[A-sixth-power result](skew-A6-denominator-audit-20261024.md), source transport,
trace, Q/R2, beta and earlier Lean results are reused within their scopes.
They were not rerun merely because the pole order changed.

The new question is whether adding A^-7 permits a bounded rational current
to cancel the actual full source. A candidate requires an exact rational
identity; a finite-family exclusion requires a valid rational inconsistency
certificate. A timeout would establish neither.

## Full source and family

Use the packet's positive orientation and compact basis
`(dV/nu^5,V dV/nu^5)`. Set

\[
A=r^3+r^{-3}+(rv-1)^6/r^{15},\qquad
(a,b,c,d)=(A,tv,t(1-t^2)/7,1+t^6).
\]

The physical divergence equation is

\[
\sum_{i=r,v,t}(\partial_i+\widetilde N_i)F_i
=S=\frac{r^{-4}}{12}M_b e_0,
\quad \widetilde N=(A_rM_a,A_vM_a+tM_b,N_t),
\quad N_t=vM_b+c'M_c+d'M_d.
\]

Both compact rows, all physical derivatives, the full t connection and
the source normalization remain present. For
`B=span_Q{r^m v^n t^k:-10<=m<=2,0<=n,k<=2}`, test

\[
F=\sum_{j=0}^{7}\frac{P_j}{A^j},\qquad P_j\in B^6.
\]

This explicitly contains the requested pure `(B/A^7)^6` family. The
coefficients are rational constants in the displayed basis, not arbitrary
rational functions. There are **5,616 original parameters**. Multiplying
by A^7 gives separate leading v-degree bands 42–44, 36–38, 30–32, 24–26,
18–20, 12–14, 6–8 and 0–2, establishing sector independence.

## Only the highest numerator is restricted

The reused generic residue is `Ra=[[0,-c/(6b)],[0,-1/3]]`.
The order-eight pole forces `(Ra-7I)Q7=0 mod A`, with
`Qj=A_r Pjr+A_v Pjv` and **det(Ra-7I)=154/3**. Thus only P7 is tangent:

\[
(P_{7,r},P_{7,v},P_{7,t})=(T_rh,T_vh,k),\quad
T_r=r^2(r^6+1),\quad T_v=r(2r^6+1)v-(3r^6+2).
\]

Each h component has r exponents -10 through -6, v degree at most one,
and t degree at most two; each k component belongs to B. This gives
60 h and 234 k coefficients. **All 4,914 lower-sector coefficients
P6 through P0 remain free**, hence 5,208 necessary parameters.

For `ell=3r(r^6-1)` and `tau7=div(T)-7ell=-11r^7+24r`, define

\[
W_7=[T_r\partial_r+T_v\partial_v+\tau_7 I
+\ell A M_a+tT_vM_b]h+(\partial_t+N_t)k.
\]

The complete scaled equation is

\[
A^7\operatorname{Div}P_0+
\sum_{j=1}^{6}\left(A^{7-j}\operatorname{Div}P_j
-jA^{6-j}Q_j\right)+W_7=A^7S.
\]

The next pole remains coupled: `(Ra-6I)Q6+W7|A=0=0`.
The earlier exclusion for P7=0 cannot restrict the lower current after
P7 changes its required source. No lower tangent condition or previous
exclusion was imposed on that changed residual.
Pole comparison uses the imported generic prime smooth A=0 divisor away
from b*Delta=0; ordinary evaluation points instead require nonzero
r, A, Delta and every literal connection denominator.

The [algebra handoff](../results/skew-A7-denominator-audit-20261024/algebra/HANDOFF.txt)
records seven new exact checks and three controls in one **2.297-second**
process. Its exact 5,616-by-5,208 injection retains every lower coefficient.
These checks do not re-prove the imported divisor and support arguments.

## Independent finite-family certificate

Before numerical results, Pro declared prime **65519**, Python
`random.Random` seed **2026102497**, successive `randrange(1,p)` draws
for r,v,t, and rejection of zeros of A, Delta or a literal denominator.
The full matrix uses 2,640 admissible points, output row 0 then 1, with
columns h7 (60), k7 (234), P6 through P0 (702 each), then positive A^7S.
Within sectors: direction where applicable, input row, increasing m,n,k.
The fixed decisive minor is the **first 5,209 rows**.

The separate local checker reconstructed all **27,133,681 decisive entries**
at **2,605 points**, before receiving Pro's matrix or numerical result:

\[
\boxed{\det=56940\pmod{65519}\ne0.}
\]

All input denominators are units modulo the prime at the integer-lifted
points. The corresponding rational augmented minor is therefore nonzero.
Only 5,208 coefficient columns are available, so those necessary evaluations
are inconsistent over Q. Together with highest-pole necessity, this excludes
the declared 5,616-parameter family and its pure B/A^7 subfamily.
Unknown rational coefficient denominators need not reduce modulo the prime;
the argument uses a nonzero rational minor, not a deficient modular rank.

The [local checker](../results/skew-A7-denominator-audit-20261024/checker/)
uses its own rational-polynomial evaluator and symbolic physical Jacobian,
and exact `flint.nmod_mat.det` from python-flint 0.9.0. Its process took
**18.563 seconds**, with three operator mutations detected and no timeout.
Report SHA256: `9ab4f9b0617984a5780e5e042f5b660bd86c4dfb0395df24e4a5a411dc655526`.
Original mathematical receipts remain frozen.

## Pro execution and artifact binding

Pro's direct quotient-rule construction produced the full 5,280-by-5,209
matrix in **25.996 seconds**. Its separate worker reconstructed all
**27,503,520 entries**, 2,640 domain/sample records, basis/rejection order
and **23 mutation controls** in **26.800 seconds**. These executions are
separate from the local decisive-minor check. Pro did not run the determinant;
that result is explicitly attributed to the local exact FLINT execution.

Mathematics closed at **18:13:01 UTC**, 4 minutes 16 seconds after Goal
activation; integration is bounded by **18:28:01 UTC**. No further search,
source replay or mathematical review followed the relevant passes.

The algebra handoff was consumed by Pro's construction, and Pro's fixed
matrix specification was consumed by the local checker. A separate
**0.453-second IO-only comparison** matched all **27,133,681 decisive
entries**, all **5,208 basis labels** and the first **2,605 sample/domain
records** against the frozen local data. The [binding addendum](../results/skew-A7-denominator-audit-20261024/checker/BINDING-ADDENDUM.md)
preserves the original pending-delivery receipts and records the downstream
use. No source, derivative or determinant was recomputed. The remaining
71 matrix rows and 35 sample records are covered by Pro's full reconstruction,
not by this local binding.

The original local control label calls the P1 column an `A^6-scaled P1
column`. Its ordinary operator factor is A^6, while the whole equation is
multiplied by A^7; the quotient correction is -A^5 A_i u. The addendum
clarifies this wording without rewriting the frozen receipt or rerunning
the correct calculation.

Pro distinguishes its cached checkout `fc4f38a` from the actual parent
`030d13b`. It read current-parent AGENTS, target board and connection through
the read-only connector. The coordinator verifies all three snapshots
against actual Git-parent bytes. No full-parent materialization or fabricated
combined Git tree is claimed. Hash checks establish file identity, not
mathematical correctness.


## Visualization and failed attempts

The [original Pro note](skew-A7-denominator-20261024.md) and
[execution packet](../results/skew-A7-denominator-20261024/) preserve all
**43 original payload files** unchanged. 28 verified binary slices
reconstruct the complete **54,599,047-byte ZIP**, SHA256
`cd00c233bae2c8a0c6f9eeaa4841073165f118456e53d4e77e54aab9dfb8a801`.
Its original manifest SHA256 is
`2e4cc096618cd7fe1053b166fabd7aeead2f88cc8d189360828e0c297a61765b`.
The small review archive omits only the matrix; the complete import omits
nothing. All part hashes, archive integrity, safe paths and complete manifest
coverage were checked. There was no download failure in this batch.

![Seventh-power family and exact finite-family certificate](../results/skew-A7-denominator-20261024/figure-01/result/A7-denominator-certificate.png)

The [generator](../results/skew-A7-denominator-20261024/render.py) reads
frozen receipts. The coordinator inspected the delivered PNG: all seven lower
bars retain 702 coefficients, only the top sector shrinks to 294, and the
minor, normalization, attribution and scope are legible without overlap.
The figure explains the finite-family certificate; it proves no general
obstruction or full-source exactness.

The unsuccessful mathematical attempt is this declared A^-7 current family.
No mathematical child timed out, and no failed Git/FLINT setup route was
retried. Two coordinator local read attempts used nonexistent paths; these
read-only lookup failures changed no artifact or mathematical claim. The
existing Pro chat received the assignment and exact handoffs through the
supported chat messaging tool. No numerical result is inferred from
coordination or packaging success.


## Limits, credit and publication

**No primitive was found; the full target remains open.** Larger numerator
supports, other divisors, higher A powers, arbitrary rational coefficients
and fibre-dependent currents lie outside this finite-family result.
No full-source exactness, global clearing, homogeneous certificate,
new Lean verification or accepted solve is claimed. Completing the bounded
Goal does not complete the larger Hodge target.

Credit fqlx for the compact connection/source, benediamond for the physical
cover and earlier reductions, and Benjamin E. Diamond and the hodge.computer
contributors for the fixed problem/framework. This is AI-assisted work
for Ravi Bajaj; separate implementations are not independent human reviews.

This batch makes no upstream post, reply, edit or PR. Posts 1–30 and the
tally remain unchanged: **30 discussion contributions, one closed
maintenance PR, zero accepted authored solves**. The latest upstream post
is still [the earlier A-squared update](https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19167075).

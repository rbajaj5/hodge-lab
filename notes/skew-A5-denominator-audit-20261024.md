# One-reflection-skew: the fifth-power denominator current search

24 October 2026. **The declared bounded six-component family through A^-5
is excluded over Q. No primitive was found.** The protected target remains
`q=1`, source `X_0^3 Y_0^3`. Here A denotes the separate physical chart
coefficient. Lean is benched; publication is Hodge Lab only.

## Run card and reused evidence

The actual Goal started at **17:38:19 UTC**, with a research deadline of
18:23:19 UTC and at most 15 minutes for integration after mathematics closes.
Individual mathematical processes have 60-second limits; network operations
have 45-second limits. The [existing Pro chat](https://chatgpt.com/c/6adb94ec-665c-8325-9a4b-2b4237c63f19)
is constructive lead. A local algebra worker derives the new highest-pole
identities, a separate local checker tests the decisive minor, and the
coordinator alone integrates the shared notebook files.

- Notebook parent: `ce22ec3a0636e9c2dbe7e90e1a36ae63f5f4b44a`.
- Fresh upstream head: `27f4bb9ad8757e5841f884d9d30124a3c97a847d`.
- Literal [connection JSON](../results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json)
  SHA256: `a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d`.
- Reused [divisor, tangent-module and support arguments](skew-A-denominator-audit-20261024.md)
  and completed [A-squared](skew-A2-denominator-audit-20261024.md),
  [A-cubed](skew-A3-denominator-audit-20261024.md) and
  [A-fourth-power](skew-A4-denominator-audit-20261024.md) results.

The question is whether adding a fifth A-pole order permits cancellation of
the actual full physical source with all bounded lower sectors retained.
A candidate requires an exact rational identity; an exclusion requires a
valid rational inconsistency certificate. A timeout establishes neither.
Completed source transport, curve, trace, Q/R2, beta and Lean checks are
reused within their original scopes rather than replayed.

## Full current and declared bounds

Use the positive packet orientation and basis `(dV/nu^5,V dV/nu^5)`. Set

\[
A=r^3+r^{-3}+(rv-1)^6/r^{15},\qquad
(a,b,c,d)=(A,tv,t(1-t^2)/7,1+t^6).
\]

The full equation is

\[
\operatorname{Div}_{\widetilde N}F
=\sum_{i=r,v,t}(\partial_i+\widetilde N_i)F_i
=S=\frac{r^{-4}}{12}M_b e_0,
\]

where `Ntilde=(A_r M_a,A_v M_a+t M_b,N_t)` and
`N_t=v M_b+c' M_c+d' M_d`. Both compact rows, all physical derivatives,
and the full t connection remain present.

Let `B=span_Q{r^m v^n t^k:-10<=m<=2,0<=n,k<=2}`. The requested pure
`(B/A^5)^6` family is explicitly enlarged to

\[
F=P_0+P_1/A+P_2/A^2+P_3/A^3+P_4/A^4+P_5/A^5,
\qquad P_j\in B^6.
\]

Coefficients in this displayed basis are constant rational numbers, not
arbitrary rational functions. There are **4,212 original parameters**.
After multiplication by A^5, the leading v-degree bands are 30–32,
24–26, 18–20, 12–14, 6–8 and 0–2, establishing sector independence.

## Fifth-order pole and coupled lower sectors

The reused generic-divisor residue is

\[
R_a=\begin{pmatrix}0&-c/(6b)\\0&-1/3\end{pmatrix}.
\]

The new order-six pole requires `(R_a-5I)Q5=0 mod A`, and
**det(R_a-5I)=80/3**. Thus only P5 is restricted to the reused bounded
tangent module:

\[
(P_{5,r},P_{5,v},P_{5,t})=(T_rh,T_vh,k),\quad
T_r=r^2(r^6+1),\quad T_v=r(2r^6+1)v-(3r^6+2).
\]

Each h component has r exponents -10 through -6, v degree at most 1,
t degree at most 2. Each k component belongs to B. This leaves 294 top
parameters and **all 3,510 lower parameters**, hence **3,804 necessary
parameters**. The pole comparison uses the generic prime smooth A=0
divisor away from b*Delta=0, under the imported divisor and support
arguments. Ordinary evaluations require nonzero r, A, Delta and all
literal connection denominators; they are not evaluations at A=0.

For `ell=3r(r^6-1)`, the new scalar term is
`tau5=div(T)-5ell=-5r^7+18r`. Define

\[
W_5=[T_r\partial_r+T_v\partial_v+(-5r^7+18r)I
+\ell A M_a+tT_vM_b]h+(\partial_t+N_t)k.
\]

With `Qj=A_r Pjr+A_v Pjv`, the complete scaled equation is

\[
\begin{aligned}
A^5\operatorname{Div}P_0
&+A^4\operatorname{Div}P_1-A^3Q_1
+A^3\operatorname{Div}P_2-2A^2Q_2\\
&+A^2\operatorname{Div}P_3-3AQ_3
+A\operatorname{Div}P_4-4Q_4+W_5=A^5S.
\end{aligned}
\]

The next pole remains coupled: `(R_a-4I)Q4+W5|A=0=0`. The old A-fourth-power
exclusion concerns P5=0. When P5 is present, the lower current must cancel
`S-Div(P5/A^5)`, a different source. No separate lower tangency condition,
old exclusion or secondary projection was imposed.

The [local algebra handoff](../results/skew-A5-denominator-audit-20261024/algebra/HANDOFF.txt)
records seven new exact identities and three mutation controls, all passed
in **2.250 seconds**, together with the 4,212 by 3,804 injection retaining
every lower coefficient. The earlier divisor and support arguments were
not re-proved by these seven checks.

## Exact finite-family certificate

Pro fixed prime **65519**, Python `random.Random` seed **2026102475**,
1,930 admissible sample triples, and the **first 3,805 rows** as the
decisive minor before exposing a numerical result. Successive
`randrange(1,p)` draws supply r,v,t; points with vanishing A, Delta or a
literal connection denominator are rejected. Output rows are compact row
0 then row 1. Coefficient columns are h5 (60), k5 (234), P4, P3, P2, P1,
P0 (702 each), followed by the positive A^5 source. Within each sector:
direction where applicable, input compact row, then increasing r,v,t exponents.

Before receiving Pro's numerical result, the separate local checker
reconstructed **14,478,025 entries** at **1,903 admissible points**. The
exact determinant of the fixed square augmented minor is

\[
\boxed{\det=31971\pmod{65519}\ne0.}
\]

All input denominators are units at the integer-lifted sample points.
Thus the corresponding rational augmented minor is nonzero, whereas
there are only 3,804 coefficient columns. The necessary evaluations are
inconsistent over Q. Combined with highest-pole necessity, this excludes
the original 4,212-parameter sum and its pure B/A^5 subfamily. The argument
does not require unknown rational coefficients to reduce modulo 65519;
it uses a nonzero rational minor. No deficient modular rank or unaccounted
kernel is used to infer an exclusion.

The [local checker](../results/skew-A5-denominator-audit-20261024/checker/)
reuses its own rational-polynomial evaluator and symbolic physical Jacobian,
with exact `flint.nmod_mat.det` from python-flint 0.9.0. Its single new
mathematical child took **11.656 seconds**, with three deliberate operator
mutations detected and explicit prime, integer-overflow and storage checks.
No process timed out. Report SHA256:
`3ead7fda7eb606548b1b12604324a781ab452fb38395f13e112cfe631c36437f`.
This execution is separate from Pro's construction; file binding is not
counted as another mathematical reconstruction.

## Pro execution, handoffs and failed attempts

Pro's direct quotient-rule construction produced the full **3,860 by 3,805**
augmented matrix in **15.374 seconds**. Its separate worker reconstructed
all **14,687,300 entries**, all **1,930 sample/domain records** and the
basis order from the literal connection and reduced W5 operator in
**13.007 seconds**, with **19 mutation controls**. These remain separate
from the local decisive-minor reconstruction. Pro did not run a determinant;
the conclusion uses the explicitly attributed local exact FLINT calculation.
No failed FLINT installation or Git transport route was retried.

Mathematics closed at **17:42:22 UTC**, four minutes three seconds after
Goal activation. The integration deadline is **17:57:22 UTC**. There is
no further search, pole refinement, source replay or mathematical review
after the decisive checks. Hash and entry comparisons establish artifact
identity; they are not additional executions of the mathematics.

The browser initially interpreted multiline typing as several submissions,
and Pro acknowledged the completed A4 batch while the A5 paragraphs were
already present. The coordinator stopped that stale acknowledgement and
submitted one consolidated A5 instruction; subsequent result handoffs
used the supported chat-message tool. Pro confirmed it consumed the full
assignment. This coordination repair is recorded separately from the
mathematical result. The new mathematical processes passed without timeout;
the unsuccessful mathematical attempt is the declared finite current family.

## Visualization and delivered evidence

The [original Pro note](skew-A5-denominator-20261024.md) and
[execution packet](../results/skew-A5-denominator-20261024/) preserve all
**42 original payload files** byte-for-byte. Fifteen downloaded binary
slices reassembled to the complete **29,475,593-byte ZIP**, SHA256
`a2d93f309397626f51f4ba43ad85218641e401dbf2d4e24dbef6c59a2934cad2`.
The original manifest SHA256 is
`449c81ba2746bf6befa76115e846dc74c31ed92737b17d6aa70f9b2229c638b1`.
The small review omitted only the matrix; the complete import has no omission.
One initial part-download action timed out after 45 seconds without a file;
one retry through the visible accessibility control succeeded. All remaining
parts succeeded. That transfer failure is separate from mathematical runs.

Pro used cached checkout `fc4f38a` and read three source/policy snapshots at
the actual integration parent `ce22ec3` through a read-only connector. The
coordinator compared all three snapshots against the actual Git parent and
checked the literal connection hash. A whole-parent reconstruction or
fabricated combined Git tree is not claimed. Hash verification establishes
file identity, not mathematical correctness.

![Fifth-power family and exact finite-family certificate](../results/skew-A5-denominator-20261024/figure-01/result/A5-denominator-certificate.png)

The [generator](../results/skew-A5-denominator-20261024/render.py) reads
frozen receipts. The coordinator inspected the PNG: counts, formulas,
attribution and limits are legible without overlap. Gray bars show the
original parameters; colored bars show that only P5 is restricted. The
figure explains this finite-family certificate; it proves no general
obstruction or full-source exactness.

The structural handoff was consumed by Pro's direct construction. Pro's
fixed specification was consumed by the separate local checker. After
delivery, a **0.829-second IO-only comparison** matched all **14,478,025
decisive entries**, all **3,804 basis labels** and the first **1,903 sample/domain
records**, with exact file-hash checks. No source, derivative or determinant
was recomputed. The [binding addendum](../results/skew-A5-denominator-audit-20261024/checker/BINDING-ADDENDUM.md)
records the result; the original pending-delivery receipts remain unchanged
as history. The other 55 rows and 27 sample records are covered by Pro's
full reconstruction, not by this local binding.

## Scope, attribution and publication

The full target remains open. Larger numerator supports, other divisors,
higher A powers, arbitrary rational coefficients and fibre-dependent
currents lie outside this finite family. No primitive, full-source
exactness, global clearing, homogeneous certificate, new Lean verification
or accepted solve is claimed. The unsuccessful mathematical attempt is
the declared A^5 family; completion of its bounded Goal does not solve
the larger Hodge target.

This batch makes no upstream post, reply, edit or PR. Posts 1–30 and the
tally remain unchanged: **30 discussion contributions, one closed
maintenance PR and zero accepted authored solves**. The latest upstream
post remains [the earlier A-squared update](https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19167075).

Credit fqlx for the compact connection and source, benediamond for the
physical cover and earlier reductions, and Benjamin E. Diamond and the
hodge.computer contributors for the fixed problem and framework. This is
AI-assisted research for Ravi Bajaj. Separate computational implementations
are not independent human reviews.

# One-reflection-skew: the bounded A-denominator sum is excluded

24 October 2026 EDT. **No rational solution exists in the declared six-component
family B⊕A^-1 B. No general primitive obstruction or solve is claimed.**

Parent `aa5a30dff2fd70994c48c484845981c141e77ef9`; upstream unchanged dispatch
pin `27f4bb9ad8757e5841f884d9d30124a3c97a847d`. The fixed source and literal
connection are unchanged. Connection SHA256:
`a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d`.
Completed Q/R2, beta, source/curve/trace, first-jet and t-only work, and the
previous Laurent exclusion, were reused rather than rerun. Lean stayed benched.

## Precisely tested family

Let

\[
B=\operatorname{span}_{\mathbf Q}\{r^m v^n t^k:
-10\le m\le2,\quad0\le n,k\le2\},
\quad A=r^3+r^{-3}+(vr-1)^6/r^{15}.
\]

All six scalar flux coefficients independently belong to **B⊕A^-1 B**.
Dividing B by A alone gives a different family, not a superset. The sum was
chosen before numerical work to allow cancellation with the old sector.
Since deg_v A=6, B∩A^-1 B=0. There are1404 independent ansatz parameters,
but this fact alone says nothing about an operator kernel.

The full physical equation is

\[
\sum_{i=r,v,t}(\partial_i+\widetilde N_i)F_i
=r^{-4}M_be_0/12,
\qquad\widetilde N=(A_rM_a,A_vM_a+tM_b,N_t),
\]
\[
b=tv,\quad c=t(1-t^2)/7,\quad d=1+t^6,
\qquad N_t=vM_b+c'M_c+d'M_d.
\]

The packet's positive orientation and input-column convention are retained.
Both compact rows and all three physical derivatives are present. Each new
quotient column contains -A_i/A² in r,v; A_t=0. Current poles are restricted
to r=0 and the newly permitted A=0. Coefficient evaluations also avoid Delta=0.
Choosing nonzero v,t for sample arithmetic adds no allowed pole to the family.
This is not a trace projection, and the regular-localization boundary is unchanged.

## Imported necessary reduction, then a new direct search

The coordinator supplied a checked leading-pole theorem. It is recorded with
its explicit algebra in [STRUCTURAL-DEPENDENCY.md](../results/skew-A-denominator-20261024/STRUCTURAL-DEPENDENCY.md).
Its reported author/checker executions are **imported evidence**, not our
execution counts. At the generic A divisor, det(Res(M_a)-I)=4/3 forces
`A_r P_r+A_v P_v=0 mod A` componentwise for any solution in the sum family.
The Laurent sector cannot cancel the denominator sector's double pole.

With numerator degree in v at most2, the necessary form is

\[
P_r=T_rh,\quad P_v=T_vh,\quad
T_r=r^2(r^6+1),\quad T_v=r(2r^6+1)v-(3r^6+2),
\]

where h is supported on r=-10,...,-6, v=0,1, t=0,1,2. There are60 h
coefficients and234 P_t coefficients. Adding the702 Laurent coefficients
leaves996 necessary parameters. This is not an arbitrary new restriction,
and not a kernel: every original-family solution must have this form.

Writing F=L+(T_rh,T_vh,P_t)/A and multiplying the equation by A gives

\[
\left[T_r\partial_r+T_v\partial_v+(7r^7+6r)I
+3r(r^6-1)AM_a+tT_vM_b\right]h
+(\partial_t+N_t)P_t+A\operatorname{Div}_{\widetilde N}L
=Ar^{-4}M_be_0/12.
\]

The author used direct quotient-rule differentiation to build the matrix.
The separate checker used this reduced tangent operator, literal-AST
evaluation, and exponent-lowered derivatives. This is a new joint search,
not a rerun of the old standalone Laurent determinant.

## Exact certificate and kernel accounting

Using prime32003 and deterministic seed2026102416, the new augmented matrix
is1056-by997. The coefficient rank is996; the augmented rank is997. The
independent checker reconstructed all1,052,832 entries and all528 domain
records, then used a different modular Bareiss elimination. Its result is

\[
\boxed{\det(\text{first997 augmented rows})=26947\pmod{32003}\ne0.}
\]

This is a nonzero minor of the fixed rational sample matrix, hence nonzero
over Q. There are only996 coefficient columns, so the reduced equation is
inconsistent over Q. The necessary pole theorem extends that exclusion to
the original1404-parameter B⊕A^-1 B family, including all six components.
No assumption is made about reducing unknown solution denominators modulo p.

Full column rank also removes the kernel issue. A homogeneous current in the
original family obeys the same necessary leading-pole restriction. Its reduced
coefficients must vanish by rank996. Thus no unaccounted operator kernel or
redundant column invalidates the exclusion. The294 denominator tangent columns
also have full rank in this same joint run; no extra pure-denominator test was run.

Seven controls detect omission of either r/v quotient term, reversed quotient
sign, omitted A_v connection chain, missing1/12, reversed source orientation,
and omitted P_t derivative. These controls do not replace the determinant.

## Executions and limits

Author search:3.127 seconds wall time, exit0. Separate checker:3.777 seconds,
exit0. Both ran under -O with explicit failure checks and60-second process
limits. No mathematical process failed or timed out in this batch. Sources,
commands, versions, finite samples, full matrix and certificate are saved in
[the result directory](../results/skew-A-denominator-20261024).
These are separate AI computations, not independent human review.

Mathematical work stopped at16:11:10 UTC /12:11:10 EDT, before the authorized
16:48:11 UTC deadline. Subsequent plaintext export reproduction and figure
rendering introduce no new search. The actual Goal belongs to the coordinator;
this worker did not activate a Goal facility. No Lean, remote CI, commit, push,
upstream publication, README, ledger or team-board edit was made here.

The [standalone verifier](../results/skew-A-denominator-20261024/reproduce_minor.py)
needs only NumPy and the pinned parent JSON. It regenerates the decisive minor
without the CSV or any old ZIP. The [run instructions](../results/skew-A-denominator-20261024/RUN.md)
separate the new executable certificate from imported structural evidence.

![Necessary pole restriction and exact joint obstruction](../results/skew-A-denominator-20261024/figure-03/result/A-denominator-certificate.png)

The [figure generator](../results/skew-A-denominator-20261024/render.py) reads
the two new frozen receipts. The inspected PNG illustrates the necessary map
and certificate; it does not prove the structural theorem or general nonexistence.
The first rendering failed on an unsupported Matplotlib math-text command;
its source, log and partial SVG are retained. The corrected rendering uses
a fresh directory. This was a presentation failure after mathematical work stopped.
The next render exposed a legend/caption overlap on inspection; the final
render moves that legend into a separate caption line. All three renders are retained.

The smallest remaining dependency is a rational full-source current outside
this exact family: for example different numerator support, higher A powers,
or another justified pole divisor. Those are not covered by this exclusion
and were not searched. No new source exactness, full primitive, fibre-exact
lift, global clearing, certificate, or target solve is claimed. Scalar trace
zero remains distinct from the full two-row source.

Credit fqlx for the compact connection, benediamond for the physical cover and
earlier reductions, the coordinator's local algebra/checker workers for the
necessary A-pole theorem, and the hodge.computer contributors for the framework.
This bounded search and its checks are AI-assisted work for Ravi Bajaj.

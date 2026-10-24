# One-reflection-skew: a new bounded full-source current search

24 October 2026 EDT. **No rational primitive was found.** This batch gives a
checked failure of one explicit mixed current, a complete obstruction for a
specified universal first-jet family, and an exact exclusion of a finite
six-component Laurent family on the actual physical base. None excludes all
rational mixed currents.

The exact notebook parent is `84f294e0235c3fd4b5d4849e565536172a74329c`; the
upstream dispatch pin is `27f4bb9ad8757e5841f884d9d30124a3c97a847d`.
The [published Q/R2 note](skew-mixed-current-20261024.md), compact source
normalization, and previous beta checks are inputs. No Lean was written or run.
The Goal is coordinator-owned; the worker has no Goal API. No commit, push,
upstream publication, README, ledger, or team-board edit was performed here.

## Source and exact operator

The source is the protected one-reflection-skew instance with q=1 and
A=X0^3Y0^3. We reuse its prior normalization, with the pinned benediamond
connection JSON SHA256
`a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d`.
Credit fqlx for the compact connection and benediamond for the simpler cover
and earlier current. New work here is AI-assisted for Ravi Bajaj.

Use the packet's positive source orientation, ordered compact basis
`(dV/z^5,V dV/z^5)`, column inputs, and coefficient connection `d+N`.
The opposite normal-last projective convention negates both source and current.
No 1/864 or other chart factor is inserted.

\[
A(r,v)=r^3+r^{-3}+(vr-1)^6/r^{15},\quad
b=tv,\quad c=t(1-t^2)/7,\quad d=1+t^6,
\]
\[
N_a=M_a,\quad N_v=tM_b,\quad N_t=vM_b+c'M_c+d'M_d.
\]
For a base-coordinate current J, its physical fluxes are
`F=(J_a-A_vJ_v,A_rJ_v,A_rJ_t)`. The physical operator is

\[
\sum_{i=r,v,t}(\partial_i+\widetilde N_i)F_i,
\qquad \widetilde N=(A_rM_a,A_vM_a+tM_b,N_t),
\]

and the full target is `r^-4 M_b e0/12`. This retains all root and transverse
derivatives. It is not a single-sheet trace. Coefficient identities live in
Q(r,v,t), on the open where their stated rational denominators are nonzero.
The common-localization boundary from the physical-curve work is unchanged.

The reused centered quantities are `chi=r^-3-v^3/3`,
`gamma=D_v^2 chi`, `kappa=vD_v chi-chi`. Thus

\[
R_2=\alpha\gamma+\beta\kappa,\quad
\alpha=(N_te_1+ve_0/(3a))/(36t),\quad
\beta=M_be_0/(108a).
\]

## 1. Explicit triangular mixed current: corrected and rejected

Let `C=t(1-t²)/7`, `D=1+t⁶`, `K=C²-3tvD`,
`w=CC'-2tvD'`, and `q=3DC'-2CD'`. The correct tangent field is

\[
G_a=0,\quad G_v=-tvw+3aq+2vK,\quad G_t=-2tK,
\]
\[
\Gamma=G_vN_v+G_tN_t=
\begin{pmatrix}3tw/2&-tq\\0&tw/2\end{pmatrix}.
\]

This combines fibre translation and scaling. The initially dispatched signs
`Gv=-tvw+3aq-2vK,Gt=2tK` were wrong; the full matrix check failed, and both
author/checker failed sources and logs are retained. They are not valid identities.

Write `DG=Gv partial_v+Gt partial_t` and
`Kmat=div(G) I+Gamma`. The tested vector coefficients and fluxes are

\[
S=\alpha/G_v,\qquad T=(v\beta-D_GS-K_{\rm mat}S)/G_v,
\]
\[
J_a=0,\quad J_v=G_v(S\chi_v+T\chi),\quad
J_t=G_t(S\chi_v+T\chi).
\]

Their exact full residual is

\[
R_2-\operatorname{Div}_NJ
=\chi(-\beta-D_GT-K_{\rm mat}T).
\]

At the allowed point `(r,v,t,a)=(1,2,1,3)`, `A_r=-3`, `Delta=1036`,
`Gv=-108/7`, `Gt=24`, and Gamma is `[[-36,12/7],[0,-12]]`.
The full two-row residual is

\[
\left(-\frac{242298600715}{34686091188},
\frac{255188727685}{15416040528}\right)^T\ne0.
\]

An independently executed finite-jet implementation also rejects it at t=2.
Controls detect omitted moving-root derivatives, t differentiation,
t connection, and matrix transposition. A generic expression expansion timed
out at 60 seconds; no result is inferred from that interruption.

This current adds the divisor Gv. Removing chi-derivatives from its residual
is not a new exactness result: direct a integration by parts already gives
`Qa=-chi Mb e0/36` and survivor
`chi(partial_a Mb+Ma Mb)e0/36`. Ben'ediamond's earlier H/L reduction also
removes ramification poles. The triangular current is retained as a failed
construction, not promoted as a better pole reduction.

## 2. A complete exclusion of one universal mixed first-jet family

For the reused `R0=chi_vv e1/(36t²)`, consider

\[
J_a=0,\quad J_v=\frac{\chi_v e_1}{36t^2}
-\frac{\chi M_ae_0}{36t},\quad J_t=\chi K(a,v,t).
\]

For arbitrary rational two-vector K, the exact identity is

\[
\operatorname{Div}_NJ-R_0
=\chi\left((\partial_t+N_t)K-T_0\right),\qquad
T_0=\frac{(\partial_bM_a+M_bM_a)e_0}{36}.
\]

The already checked `M_b e1=M_a e0` cancels the chi_v coefficient; every
derivative and both rows remain. For R2 directly, subtract the reused Y:

```
Z_a=0
Z_v=chi_v e1/(36t²)-chi Ma e0/(36t)+kappa e0/(108at)
Z_t=chi K+gamma e1/(36t)
R2-Div(Z)=chi*(T0-(partial_t+Nt)K).
```

The new full-matrix rational equation for K is inconsistent. Generic residue
and infinity checks reduce every possible rational K to
`K=(P0,P1)/Delta_monic`, with degrees at most 15 and 13. At a finite
discriminant zero the residue eigenvalues are 0 and -1/3; the source has at
most a double pole, so K has at most a simple pole. Elsewhere no finite pole
is allowed. Under `diag(t^-3,t^-1)`, the connection is O(t^-2) and the target
O(t^-6), giving the degree bounds.

At `(a,v)=(3,2)`, the exact 52-by-30 coefficient system has rank 30 and
augmented rank 31. The separate checker reconstructed its coefficient
recurrence and an integer left-null witness. The generic system is regular
at this point and has a 30-square minor nonzero there. Cramer's rule forces
any hypothetical generic solution to be regular there, so the specialization
contradiction is legitimate. This excludes K in Q(a,v,t)^2 in this displayed
family, not arbitrary currents using the physical cover relation.

For the concrete K=0 current, `Div(J)-R0=(40/67081,-1945/2414916)` at the
same allowed physical point. This is a mixed v,t family; it is distinct from
the previous t-only R2 exclusion, which was reused and not rerun.

## 3. Direct physical Laurent family: exact finite exclusion

All six physical flux components were allowed to vary independently in

\[
\operatorname{span}_{\mathbf Q}\{r^m v^n t^k:
-10\le m\le2,\ 0\le n,k\le2\}.
\]

There are 702 coefficients. This is a constructive finite search on the
actual physical base; no beta, fixed-L, scalar trace, arbitrary-chi, or
one-row restriction is imposed. It allows only Laurent poles at r=0 in the
current and bounded polynomial v,t dependence. No completeness argument
extends these bounds to all mixed currents.

With deterministic seed 2026102415, the author assembled a 762-by-703
augmented sample matrix modulo 32003. The separate checker reconstructed
all entries through a restricted integer AST evaluator and exponent-lowered
derivatives, checked all 381 allowed points, and independently evaluated a
703-square minor:

\[
\det=13884\pmod{32003}\ne0.
\]

The first 703 rows in their original order have this same determinant.
Consequently the rational augmented matrix has rank at least 703, whereas
there are only 702 coefficient columns. The declared family is inconsistent
over Q (and after constant-field extension). This reasoning does not reduce
unknown rational solution denominators modulo p. Mutations detect an omitted
A_v chain term, missing 1/12, reversed source sign, and a wrong Laurent derivative.

The [standalone plain-text verifier](../results/skew-mixed-construction-20261024/reproduce_laurent.py)
reconstructs the minor from the pinned connection alone. It does not require
any old ZIP, saved matrix, or unavailable prior receipt.

## Evidence, limits and next dependency

The [run card](../results/skew-mixed-construction-20261024/PLAN.md),
[reproduction commands](../results/skew-mixed-construction-20261024/RUN.md),
[alternate handoff](../results/skew-mixed-construction-20261024/alternate/HANDOFF.txt),
and [independent checker review](../results/skew-mixed-construction-20261024/checker/REVIEW.md)
separate author executions, independent AI executions, read-only argument
review, reused prior evidence, and user-relayed external results. Failed
sign gates, a Python implementation failure, and two 60-second expanded
calculations remain saved. Interrupted calculations are not results.

![Both compact rows remain at an allowed physical point](../results/skew-mixed-construction-20261024/figure-02/result/full-residuals.png)

The [figure generator](../results/skew-mixed-construction-20261024/render.py)
reads the exact saved residuals; input/output hashes accompany the figure.
It illustrates nonzero point witnesses and does not replace either rational
family exclusion. The SVG and inspected PNG are supplied for coordinator integration.

Mathematical work stopped at 15:32:59 UTC (11:32:59 EDT), before the authorized
16:00 UTC deadline. No remote CI or Lean execution occurred. No old receipt
was rewritten, and no old archive is included in this new packet.

The coordinator relayed a fixed-L exclusion and a generic discriminant-image
compatibility result. Those are external handoffs here, not our executed
checks. Local residue compatibility is consistent with a global rational
obstruction and does not construct a primitive. The old t-only R2 exclusion
was not replayed.

The remaining requirement is still an actual mixed current cancelling the
full source outside the two excluded families. A next test must explicitly
change the a/v flux constraints or use the physical cover relation with
coefficients outside the declared Laurent box or another justified pole
support; merely rerunning the t-only completion or rewriting chi*C is
insufficient. No general rational nonexistence, source exactness, fibre-exact
lift, cohomology/GM identification, global clearing, certificate, or solve is
claimed. Scalar trace zero remains separate from the full two-row source.

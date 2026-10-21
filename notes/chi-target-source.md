# The chi-curve idea tested against the actual skew source

21 October 2026. **Successful source binding; failed generic fiber-only
integration.** The lesson from the [chi-curve pilot](chi-curve-bridge.md) is
to transport the differential and its weight, not only an equation. Here
that test reaches the protected source of `one-reflection-skew`.

[![The source operator, two exact matrix samples, and the failed constant primitive](../visualizations/chi-target-source.png)](../visualizations/chi-target-source.svg)

The target gives a genus-four cyclic curve rather than the chi model's
genus-one curve. We have not constructed a correspondence from the chi
elliptic curve to the sextic. The concrete connection is the same sequence:
use a square coordinate, retain the source/Jacobian, then test the weighted
primitive equation. This note does not rule out an ambient Hodge certificate.

## Protected input and prior work

Upstream pin:
[`a6b4cc49452abe31ead0be71d04e8146639896d9`](https://github.com/hodge-computer/sextics/tree/a6b4cc49452abe31ead0be71d04e8146639896d9).
Notebook base: `e5067915e93b968e0e55133d41379fe2dd438cec`.
The pinned catalogue says **open / unproved**, with no certificate available.
The exact variable order is X0, X1, X2, Y0, Y1, Y2; q = 1 and A = X0^3 Y0^3.
Writing F0 for the sum of the six sixth powers, the fixed sextic is

$$
F=F_0+X_0^3X_1Y_0Y_1+X_1^3X_2Y_0Y_1
+\frac17X_0X_1Y_0Y_1(Y_0^2-Y_1^2).
$$

The checker reads F, A and q directly from the saved protected
[`instance.rec`](../results/chi-target-source/inputs/data/one-reflection-skew/instance.rec)
using a restricted arithmetic parser, and compares every coefficient with
the separately structured record. Variable order comes from provenance.
[Input hashes and exact Git blobs](../results/chi-target-source/inputs.json)
also pin the instructions, formal contract, motivation and catalogue.

The physical quotient and source below are prior work of `fqlx` in
[comment 19080252](https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19080252),
already examined in our [earlier audit](one-reflection-skew-mathematical-audit.md).
They are not claimed as discoveries of this pilot. The full discussion
snapshot at 19:43:23 UTC and a bounded search returning no matching open PR
are retained in [context.json](../results/chi-target-source/context.json).
The text search alone does not prove no differently titled proposal exists.
The companion packet, large exports, trace construction and completed
Prompt 3 checks were not replayed here.

## Carry the actual source through the square coordinate

On Y0 = 1 put

$$
(X_0,X_1,X_2,Y_1,Y_2)=(x,rx,wx,t,z),\qquad U=x^2,
\qquad \nu=dr\wedge dw\wedge dt.
$$

The protected polynomial becomes G = z^6 + P(U), with

$$
P=aU^3+bU^2+cU+d,\qquad
(a,b,c,d)=\left(1+r^6+w^6,\ rt(1+r^2w),\ \frac{rt(1-t^2)}7,\ 1+t^6\right).
$$

These coefficients are reconstructed from F, retaining the skew term.
The projective volume on this chart has a minus sign; the coordinate
Jacobian is x^2 and A becomes x^3. Hence

$$
\psi=\frac{A\Omega}{F^2}
=-\frac{U^2}{2G^2}\,dU\wedge\nu\wedge dz.
$$

The factor 1/2 comes from dU = 2x dx. It is not a normalized trace. Both
A and the volume change sign under simultaneous negation of the three X
coordinates, so their product descends. With alpha = dU wedge nu, set

$$
\beta=\frac{U^2}{12z^5G}\alpha,\qquad
\psi=d\beta+\frac{5U^2}{12z^6G}\alpha\wedge dz.
$$

For the convention Res((dG/G) wedge theta) = theta this gives

$$
\theta=\omega\wedge\nu,\qquad
\boxed{\omega=\frac{5U^2}{72z^{11}}\,dU},\qquad z^6=-P(U).
$$

The positive sign uses this order of forms; putting nu before omega reverses
it. All displayed coefficient identities are checked exactly. The charts
use x and z nonzero; conclusions are rational identities, not assertions
that these coordinates never vanish on the variety.

Work relatively over K = Q(r,w,t), or C(r,w,t), so base parameters are
constant under d_rel. On a != 0 and disc(P) != 0, the smooth projective
curve has genus four: the degree-six map to the U-line contributes 15 at
the three simple finite roots and 3 at infinity. Thus 2g-2 = -12+18 = 6.
This is an algebraic argument about the smooth completion, not a mesh test.

## Exact criterion for direct integration along the fiber

On this smooth cubic open, omega has a rational relative primitive if and
only if **b = c = 0**. In that case

$$
\boxed{W=\frac{1}{36a z^5}},\qquad d_{\rm rel}W=\omega.
$$

This criterion is proved, rather than extrapolated from bounded matrix ranks:

1. Over the algebraic closure of the coefficient field, a simple root of P
   makes z^6+P Eisenstein at that root. The function field therefore has basis
   1,z,...,z^5 over K(U). Since dz/z = P' dU/(6P), relative differentiation
   preserves each basis component. The source is 5U^2 z dU/(72P^2), in the
   z component. Any rational primitive would give one in that component,
   expressible as B(U)/z^5 with B in K(U). No ordinary trace or untracked
   root-of-unity average is used.
2. Direct differentiation gives

   $$
   d_{\rm rel}(B/z^5)=\frac{5P'B-6PB'}{6z^{11}}\,dU,
   \qquad 5P'B-6PB'=\frac5{12}U^2.
   $$

   Away from roots of P, a finite pole of B produces an unmatched derivative
   pole. At a simple root, a pole of order k >= 1 gives a nonzero leading
   coefficient proportional to (6k+5)P'. Thus B has no finite poles and is
   polynomial. This includes possible moving poles; they were not silently
   excluded by the initial trial.
3. If B has degree n, the left side has leading coefficient a(15-6n) times
   that of B. It never vanishes for integer n. The quadratic right side
   forces n=0; B=0 is also impossible. Comparing coefficients then gives
   B=1/(36a), b=c=0. Substitution proves sufficiency.

The generic physical coefficients do not satisfy b=c=0. Their exact locus
is rt=0, or (t^2=1 and r^2 w=-1), intersected with the smooth cubic open.
Thus increasing the degree of B or allowing rational poles cannot rescue
this **relative** integration route at the generic physical point.

## Two source-bound samples and failed attempts

| Parameters (r,w,t) | Reconstructed P | Discriminant | Outcome |
| --- | --- | --- | --- |
| (1,1,2) | 3U^3 + 4U^2 - 6U/7 + 65 | -361978181/343 | No rational relative primitive. |
| (0,1,2) | 2U^3 + 65 | -456300 | W = 1/(72z^5) works along this fiber. |

The special fiber is a positive control, not generic endpoint coverage or a
solve. With B=1/(36a), the generic cleared residual is
5bU/(18a)+5c/(36a), or 10U/27-5/126 at the first sample.

Independent exact matrices for polynomial B of degrees at most 0,2,4,8
have ranks 1,3,5,9. At the first sample the augmented ranks are 2,4,6,10;
at the control they equal the original ranks. The receipt supplies rational
left duals with lambda^T M=0 and lambda^T rhs=1 for each failed sample
search, and exact coefficient vectors for each successful control.
The figure shows degree four and the cleared residual. Colors are signed
logarithms for display; ranks come from rational arithmetic.

A scratch derivation initially put a plus sign before 5P'B in the alternative
equation 6PB' - 5P'B = -5U^2/12, leading to a negative proposed constant.
Independent review corrected this **before** the first implemented replay.
That draft mistake is not evidence against the source or a published result.
The final suite deliberately reverses the primitive sign, omits the
connection term, and drops the skew coefficient; all three are rejected.

## What remains open

The chi pilot had a Gaussian factor and the operator B' - phi' B. Here the
algebraic factor z^(-5) instead gives B' - 5P'B/(6P). Carrying that weight
exposes a concrete obstruction to the naive primitive. It does not identify
the chi curve with this curve or transfer a Gaussian integration result.

Relative nonexactness does **not** imply absolute nonexactness. For example,
even though dU/U has no rational primitive in U,

$$
\frac{dU}{U}\wedge dr\wedge dw\wedge dt
=d\left(-r\frac{dU}{U}\wedge dw\wedge dt\right).
$$

The full target can use base-parameter derivatives and their connection
terms. The existing twisted-companion equation explicitly retains them;
this experiment does not restrict its unknowns, settle it, or invalidate
other constructions. No numerator/denominator degree bound for the full
protected certificate follows. No Lean proof, primitive for the full target,
or accepted solve is produced.

The smallest useful next check is a **specific proposed primitive including
base components**, evaluated against the full source with its connection
terms retained. Merely enlarging the fiber-only B ansatz would repeat a
route the elementary argument has already ruled out. This bounded pass
stops at source binding, the criterion, two samples and error controls.

## Reproduction and evidence

```sh
python scripts/validate_chi_target_source.py
```

The suite requires SymPy (recorded version 1.14.0); its figure uses NumPy
and Matplotlib. Python 3.11.9, CPU exact arithmetic. **58 requirements passed**,
including source binding, differential identities, rational ranks and duals.
Three additional mutated runs exit 1 at the required messages under Python
-O; checks use explicit exceptions. The final suite took **10.562 seconds**,
with 0.313 seconds in the positive algebra calculation. Bounds: 120 seconds
per checker, 60 seconds for plotting, 300 seconds for the suite. No timeout.
No numerical roots, modular lifting, GPU computation, or full historical
packet/Lean replay was needed. The first implementation run also passed;
its separate receipt is retained, not added to the check count.

[Checker](../scripts/check_chi_target_source.py) ·
[Exact results and duals](../results/chi-target-source/replay.json) ·
[Commands, bounds and failures](../results/chi-target-source/validation.json) ·
[Read-only review scope](../results/chi-target-source/review.json).

Credit: Benjamin E. Diamond and the upstream contributors for the protected
problem and certificate framework; `fqlx` for the physical quotient, source
reduction and companion formulation. The GOE motivation comes from Ravi
Bajaj's correction work and its sources. This elementary relative criterion
and computational illustration were prepared for rbajaj5 with OpenAI Codex
and two read-only reviewers; no novelty claim is made. Previous audit counts
and browser-reported checks remain separate. This is a Hodge Lab research
batch; no upstream contribution is published or counted in this pass.

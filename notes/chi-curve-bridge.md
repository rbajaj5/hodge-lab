# From the chi density to a curve: what survives transport?

21 October 2026. A bounded pilot prompted by Ravi Bajaj's suggestion to use
the algebraic geometry of the corrected GOE factor in the Hodge searches.
There is a genuine genus-one curve here. Its presence alone does not identify
a nonzero Hodge class: the particular differential and its weight matter.

[![The real curve, its rational primitive, and the exponential weight](../visualizations/chi-curve-bridge.png)](../visualizations/chi-curve-bridge.svg)

The picture shows the real affine slice and the positive probability arc;
it is not a picture of the whole complex curve or a Hodge certificate.

## Inputs and scope

The model and corrected density are transcribed from
[GOE CORRECTION.md at e864d2c](https://github.com/rbajaj5/goe-determinant-factor-density/blob/e864d2c164a6ded910b8ecf764905193102c2a83/CORRECTION.md).
The exact source bytes, Git blob and SHA-256 are retained in
[inputs.json](../results/chi-curve-bridge/inputs.json).
Notebook base: `ae043a1b037cc8b0393460f0b58fc5dedd4c35cb`.
Observed upstream head: `b2ee2acb5409e37b6fad800b256fb8f2fee163bf`.
Hash validation binds the copied text; it is not an automatic proof that
every sentence of the source note has been reconstructed.

Let independent variables have distributions X ~ chi_1 and Y ~ chi_(2m), with
integer m >= 1, and put R_m = (X^4 + 2 X^2 Y^2)^(1/4). This pilot starts from
that factor law; it does not rederive the complete GOE determinant factorization.
Its corrected density is

$$
f_{R_m}(t)=\frac{2^{2-m}t^3}{\Gamma(m)\sqrt{2\pi}}
\int_0^t g_t(s)^{2m-2}s^{-2}e^{-(s^2+g_t(s)^2)/2}\,ds,
\qquad g_t(s)^2=\frac{t^4/s^2-s^2}{2}.
$$

The probability integral uses t > 0 and the positive square root. The
algebraic identities are over Q(t), with t nonzero, on the stated open charts.

## A genuine curve, not just a new name

The fixed-value equation is s^4 + 2 s^2 y^2 = t^4. On s != 0 use

$$
u=s/t,\qquad v=2sy/t^2,\qquad s=tu,\qquad y=tv/(2u).
$$

It becomes E: v^2 = 2(1-u^4). The degree-two map to the u-line has four
simple branch points over the algebraic closure and is unramified at
infinity. Riemann-Hurwitz gives genus one for the smooth projective
completion. The rational point (1,0) supplies an origin if an elliptic-curve
structure is desired. The original projective plane quartic is singular at
[s:y:z] = [0:1:0]; the smooth completion, not that singular plane model,
is what has genus one.

The parameter t scales out. Thus this family is isotrivial after the displayed
change of coordinates, and m changes the probability weight rather than the
curve or its genus. No varying-moduli or phase-transition claim follows.

## Transport the measure as well as the equation

Retaining ds = t du gives

$$
f_{R_m}(t)=\frac{2^{4-3m}t^{2m}}{\Gamma(m)\sqrt{2\pi}}
\int_0^1 v^{2m-2}u^{-2m}e^{-\phi_t(u)}\,du,
\qquad \phi_t(u)=\frac{t^2}{4}(u^2+u^{-2}).
$$

Here v is positive on 0 < u < 1. The inverse Jacobian used in the original
density is dy/dt = t^3/(s^2 y). The checker derives it from the implicit
equation and verifies the prefactors, exponent and ds factor.

For integer m >= 1 the unweighted algebraic differential is

$$
\eta_m=v^{2m-2}u^{-2m}\,du
=2^{m-1}(1-u^4)^{m-1}u^{-2m}\,du=dB_m,
$$

$$
B_m=2^{m-1}\sum_{k=0}^{m-1}(-1)^k\binom{m-1}{k}
\frac{u^{4k-2m+1}}{4k-2m+1}.
$$

This is a general proof by binomial expansion and differentiation: each
denominator 4k-2m+1 is odd and hence nonzero. For example, eta_1 = du/u^2
and B_1 = -1/u. The form is rationally exact on the appropriate open curve;
it does not supply a nonzero ordinary algebraic de Rham class merely because
we wrote it on a genus-one curve. Computational examples m = 1,...,8
supplement this proof, rather than establish the universal quantifier.

The weighted form is different. In particular,

$$
d(e^{-\phi_t}B_m)=e^{-\phi_t}(B'_m-\phi'_t B_m)\,du.
$$

The additional term is nonzero for each tested m. This rejects the naive
candidate e^(-phi_t) B_m as a primitive of the weighted density. It does
**not** prove nonexistence of all weighted primitives or nonelementarity.
The exponential weight requires its own differential equation; it is not an
ordinary algebraic differential on a compact elliptic curve.

Two quotients must also be distinguished. The involution v -> -v gives
the u-line, and eta_m already pulls back from that line. The different
involution (u,v) -> (-u,v) gives the conic v^2 = 2(1-z^2), z = u^2.
The form eta_m is anti-invariant under the latter involution, including
the sign of du. Squaring both original variables gives a rational equation
U^2 + 2UV = t^4; forgetting the covering data or the differential can hide
exactly the information under investigation.

## What to try in a Hodge target

The constructive proposal is to find a map or correspondence to a simpler
curve and transport the **specified source class** through it. A candidate
needs an explicit binding to the protected F, A and q, the correct signed
Jacobian and trace, matching cohomological degree and any Tate twist,
the coefficient field and nonzero chart assumptions,
and a proof that the resulting differential has the required primitive or
support. Moving maps also require their first-variation corrections.

Our [physical transport audit](physical-source-transport-audit.md) and
[covariant-jet replay](covariant-jet-audit.md) already illustrate that
strategy in an accepted construction, with their separate limits. They
remain complete and were not rerun for this pilot. The present chi curve
provides a small example in which the form can be tracked completely; no
map from a protected sextic to this curve has been constructed. There is no
new family exclusion, supporting cycle, primitive for a Hodge target, or
Hodge-conjecture theorem here. The classical conjecture concerns rational
Hodge classes and algebraic cycles, not the mere existence of an algebraic
description of a probability model ([Clay statement](https://www.claymath.org/millennium/hodge-conjecture/)).

## Executed checks, limits and reproduction

The [checker](../scripts/check_chi_curve_bridge.py) passes **46 requirements**:
38 exact equalities and eight nonzero residual controls. This includes the
curve chart, inverse, branch squarefreeness, singular plane point, measure
prefactors, and eight rational primitives. Two additional command-line
mutations fail with the intended message: reversed primitive sign and
omitted ds factor. Explicit exceptions keep these checks active under
Python -O. A read-only reviewer independently derived the formulas and
inspected the checker and receipt; that review was not a separate execution
of the same suite. [Review scope](../results/chi-curve-bridge/review.json).

Python 3.11.9 and SymPy 1.14.0; CPU exact arithmetic. Every executed process
had a 60-second timeout; none timed out. The main calculation took 0.296
seconds, or 2.422 seconds including process startup. The two mutation
processes took 2.203 and 2.265 seconds. No numerical density integration,
Lean/kernel build, Hodge-target search, or previous audit replay was executed.
The successful transport and the failed naive weighted primitive are both
retained, without treating the latter as a nonexistence proof.

From the repository root (SymPy required; Matplotlib and NumPy for the figure):

```sh
python scripts/check_chi_curve_bridge.py
python -O scripts/check_chi_curve_bridge.py --perturb primitive-sign
python -O scripts/check_chi_curve_bridge.py --perturb omit-ds
python scripts/visualize_chi_curve_bridge.py
```

The two perturbation commands are expected to exit 1 with their specific
failure messages. The positive command regenerates the replay receipt.
[Exact receipt](../results/chi-curve-bridge/replay.json) and
[executed commands and bounds](../results/chi-curve-bridge/validation.json)
retain the actual outputs and script/input hashes. The figure's real arc is
sampled for display; its samples are not the exact proof.

Attribution: the corrected GOE factor and its sources are in Ravi Bajaj's
pinned correction repository, including the Bornemann-Lacroix determinant
work. The elementary curve and differential calculations here were prepared
for rbajaj5 with OpenAI Codex and a separate read-only reviewer. This is an
expository reconstruction, with no novelty claim. Compare the distinction
between a curve and its integrand in [DLMF 19.2](https://dlmf.nist.gov/19.2).
Published only in Hodge Lab; no upstream discussion contribution is counted.

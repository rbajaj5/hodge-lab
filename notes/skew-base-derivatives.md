# Base-parameter derivatives in the skew source equation

21 October 2026. **No target primitive found in four specified bounded
spaces.** This extends checkpoint 117's fiber-only test to a rational
three-form with all four components, including derivatives in the three
base parameters. Exact rational duals exclude numerator total degree at
most four for each fixed denominator `1`, `r`, `t`, and `a=1+r^6+w^6`.
These are bounded negative results, not a nonexistence result for the target.

[![Actual four-component operator and its exact dual](../visualizations/skew-base-derivatives.png)](../visualizations/skew-base-derivatives.svg)

The figure shows nonzero coefficients of the actual degree-four matrix for
`D=a`, with all four components distinguished. Three horizontal lines locate
the coefficient functionals used by one exact certificate. Matrix patterns
are not evidence of a geometric phase transition, a full resolution, or a solve.

## Inputs and reused work

Protected target: **one-reflection-skew**, open at upstream
[`a6b4cc49452abe31ead0be71d04e8146639896d9`](https://github.com/hodge-computer/sextics/tree/a6b4cc49452abe31ead0be71d04e8146639896d9).
Notebook base: `eb36f9a199dc9e8d7b206f4fedcebbd8f13a3751`.
[Pins and hashes](../results/skew-base-derivatives/inputs.json) record the
current heads and the unchanged ten upstream blobs from checkpoint 117.
This pass reuses the completed source-to-residue derivation and its chart
hypotheses; it does not rerun the prior 58-check suite or previous audits.

Variable order is `(X0,X1,X2,Y0,Y1,Y2)`, `q=1`, and `A=X0^3 Y0^3`.
The protected sextic is the sum of the six sixth powers plus

$$
X_0^3X_1Y_0Y_1+X_1^3X_2Y_0Y_1
+\frac17X_0X_1Y_0Y_1(Y_0^2-Y_1^2).
$$

On `Y0=1`, substitute `(X0,X1,X2,Y1,Y2)=(x,rx,wx,t,z)` and `U=x^2`.
The search parses `instance.rec` afresh; its separate verifier reconstructs
the polynomial from the structured terms of `record.json`. These give

$$
G=z^6+P,\quad P=aU^3+bU^2+cU+d,
\quad (a,b,c,d)=\left(1+r^6+w^6,rt(1+r^2w),\frac{rt(1-t^2)}7,1+t^6\right).
$$

With $\alpha=dU\wedge dr\wedge dw\wedge dt$, the reused residue source is

$$
\theta=\frac{5U^2}{72z^{11}}\alpha.
$$

The source normalization and orientation are documented in
[checkpoint 117's note](chi-target-source.md). The physical quotient and
residue reduction are prior work of `fqlx` in
[comment 19080252](https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19080252).
They are not discoveries of this experiment. This pass does not construct
a correspondence from the GOE chi curve to the sextic.

## The full differential, including the base

Use rational functions in `U,r,w,t` over characteristic-zero constants,
initially $\mathbb Q$. Put $V=(B,C_r,C_w,C_t)$ and

$$
\Gamma=z^{-5}\iota_V\alpha,
$$

where the contraction has signs

$$
\iota_V\alpha=B\,dr\wedge dw\wedge dt
-C_r\,dU\wedge dw\wedge dt
+C_w\,dU\wedge dr\wedge dt
-C_t\,dU\wedge dr\wedge dw.
$$

From $z^6=-P$, each coordinate derivative has
$\partial_jz=-P_j/(6z^5)$. Therefore

$$
d\Gamma=\frac{5\nabla P\cdot V-6P\operatorname{div}V}{6z^{11}}\alpha,
\qquad
5\nabla P\cdot V-6P\operatorname{div}V=\frac5{12}U^2. \tag{1}
$$

All four derivatives occur in (1). In particular, the three base functions
are not treated as constants when differentiating. On the generic cyclic
cover, the source has character one under `z -> zeta*z`, `zeta^6=1`.
Projecting a rational primitive to this character commutes with exterior
derivative. Its coefficient functions are `z^(-5)` times rational functions
of `U,r,w,t`, so an unrestricted rational vector field in (1) describes that
character sector. **Our bounded searches do not range over all such fields.**

For the actual tests, choose one common denominator $D$ and write $V=N/D$.
Clearing $D^2$ yields

$$
5D\nabla P\cdot N
-6P\left(D\operatorname{div}N-N\cdot\nabla D\right)
=\frac5{12}U^2D^2. \tag{2}
$$

The $N\cdot\nabla D$ term is retained. This is an identity on the nonempty
open chart `zD != 0`; multiplying by $D^2$ is reversible in the function
field. No specialization of `r,w,t` is made. With `P7=7P`, the matrix is
formed from $12[5D\nabla P7\cdot N-6P7(D\operatorname{div}N-N\cdot\nabla D)]$;
it is exactly **84 times** the left side of (2). Its right-hand side is
`35 U^2 D^2`. This integer scaling does not change the source normalization.

## Exhausted finite spaces and exact certificates

For each `D` in `{1,r,t,a}`, each of the four components of `N` contains
**every monomial in U,r,w,t of total degree at most n**, with independent
constant coefficients, for `n=0,2,4`. There are `4 binomial(n+4,4)` columns:
4, 60 and 280. No component, mixed monomial, or base direction is removed by
a symmetry or gauge reduction. These are four denominator choices with
nested bounds, not twelve independent new families. They are not bounds
on the homogeneous denominator degree in the original certificate problem.

At degree four:

| Fixed D | Coefficient rows | Columns | Nonzero entries | Exact dual terms | Outcome |
| --- | ---: | ---: | ---: | ---: | --- |
| 1 | 705 | 280 | 1,925 | 5 | Excluded in this space |
| r | 841 | 280 | 1,985 | 9 | Excluded in this space |
| t | 841 | 280 | 1,985 | 8 | Excluded in this space |
| a | 2,068 | 280 | 5,495 | 3 | Excluded in this space |

For every tested space the search supplies a rational coefficient functional
$\lambda$ with $\lambda^TM=0$ and $\lambda^T(35U^2D^2)=1$.
For `D=a`, degree at most four, one particularly small certificate is

$$
\lambda=\frac35[rt^3]+\frac1{35}[U^2w^{12}]
-\frac1{35}[U^2w^{12}t^2],
$$

where brackets extract a polynomial coefficient. The verifier checks this
against all 280 columns, not a selected subsystem. The analogous data for
all twelve bounded tests are saved in `search-*-degree*.json` under
[the results directory](../results/skew-base-derivatives).

A read-only reviewer also derived this particular certificate directly.
Let $n_0=[1]N_U$ and $n_2=[t^2]N_U$. Degree and monomial support give
the following three coefficients of the scaled left side:

$$
[rt^3]=60(n_2-n_0),\qquad
[U^2w^{12}]=1260n_0,\qquad
[U^2w^{12}t^2]=1260n_2.
$$

All base-component contributions to these three coefficients vanish within
the degree-four bound. The right side has coefficients `(0,35,0)`, forcing
simultaneously $n_2=n_0$, $n_0=1/36$, and $n_2=0$. This is the displayed
dual's contradiction written as three scalar equations. It is a manual
coefficient derivation, not an additional computer replay or check count.

These rational identities also exclude solutions with complex constant
coefficients, by extension of scalars. No inference from numerical rank or
modular arithmetic is involved. Elimination stops at an exact contradiction;
the saved number of pivots is **not claimed to be the full matrix rank**.

## Positive controls and deliberate errors

To ensure the new code genuinely uses the base derivatives, use the
manufactured family $P=U^3+U+r$ and $V_r=U^2/12$, all other components zero.
Then $\operatorname{div}V=0$ and $P_r=1$, so (1) holds. Permuting the base
coordinate exercises each of `r,w,t`. This family has nonzero linear term
in its fiber polynomial, yet has an absolute primitive using the base.
It illustrates why the previous fiber-only obstruction cannot settle the
absolute problem. It is **not** a solution or specialization of the protected
target's full derivative system.

A second control uses $H=U^3+U+1$, $P=r^2H$ and
$V_r=5U^2/(192rH)$. The two terms on the left of (1) contribute
`50U^2/192` and `30U^2/192`, respectively, and sum to `5U^2/12`.
Ignoring the derivative of its denominator leaves residual `-5U^2/32`.

Three deliberately invalid executions exit 1 with the required diagnostics:
omit base components; omit denominator differentiation; remove a nonzero
dual term. They run under `python -O`, and the requirements use explicit
exceptions rather than assertions. All are detected.

## Relation to previous companion calculations

`fqlx`'s twisted-companion packet already studies base derivatives. Section 7
of `rank2/rank2_primitive_notes.md` reports six rank-two coefficient functions,
polynomial through degree six or of the form `H/a` through degree six:
504 columns, augmented modular rank 505 in both cases. Our
[earlier audit](one-reflection-skew-mathematical-audit.md) pins that archive
at SHA-256 `3901f358ec9f1f46b6f4900cba80aa82160dd50d28e86e766aae826e39a960be`.
Those bounded searches were **not rerun here**. The present four-component
equation is unreduced; its degree-four spaces are not identified with the
rank-two degree-six spaces without a checked Hermite-reduction conversion.
No claim of disjoint coverage, larger coverage, or first use of base
derivatives is made. The useful addition here is a direct source equation
and small exact dual certificates with independently reconstructed columns.

## Reproduce and interpret

```sh
python scripts/search_skew_base_derivatives.py --denominator 1
python scripts/search_skew_base_derivatives.py --denominator r
python scripts/search_skew_base_derivatives.py --denominator t
python scripts/search_skew_base_derivatives.py --denominator a
python -O scripts/check_skew_base_derivatives.py
python scripts/validate_skew_base_derivatives.py
```

Python 3.11.9, SymPy 1.14.0 and python-flint 0.9.0; Matplotlib renders the
figure. The search uses sparse exact rational elimination. The independent
verifier uses `Poly` multiplication/differentiation and a separate monomial
enumerator, importing neither the search matrix nor its elimination. It
reconstructs the protected polynomial from `record.json`, while the search
uses `instance.rec`.

**1,376 full columns and 1,533 required checks pass** across the twelve
nested systems; these are not added to any previous audit count. The
positive verifier took 0.990 seconds internally / 2.847 seconds as a process.
The four search processes each took about one second. Their internally
rounded small timings can be zero because of clock resolution; the external
wall times are preserved. Search bounds were 90 seconds internally and
120 seconds per process; the verifier had 120 seconds; mutation/plot
validation had a 300-second total budget and a 60-second plot limit.
No computation timed out.

One plot rendering attempt failed because Matplotlib required braces in
`frac{3}{5}`. Its complete failure receipt is retained; only the corrected
plot was rerun. The saved validation includes the successful mutation checks,
failed plot and successful repair, totaling 10.492 seconds. The search and
positive verification were preserved, not repeated. This rendering failure
is not a mathematical result.

[Independent verification](../results/skew-base-derivatives/verification.json) ·
[Commands and retained failures](../results/skew-base-derivatives/validation.json) ·
[First independent execution](../results/skew-base-derivatives/first-independent-run.json) ·
[Read-only review scope](../results/skew-base-derivatives/review.json).

**Remaining limits.** Other fixed denominators (including discriminant or
moving-fiber factors), higher powers, higher numerator degrees and general
rational functions remain untested. Constants are extended from $\mathbb Q$
to $\mathbb C$, not to arbitrary base-dependent coefficients without changing
the ansatz. No rational primitive, ambient `HasCertificate` result, new
homogeneous degree bound, Lean/kernel proof, trace or global clearing is
constructed. No large historical packet, accepted transport or covariant-jet
audit was replayed. This bounded pass is complete and stops here.

Credit Benjamin E. Diamond and contributors for the protected framework,
`fqlx` for the quotient/residue and companion formulation, and Ravi Bajaj's
chi-curve experiment for the motivation. Prepared for rbajaj5 with OpenAI
Codex and independent read-only review; no novelty claim. Published to Hodge
Lab only in this pass. Contribution tally remains 28 discussion contributions,
one closed maintenance PR and zero accepted authored solves.

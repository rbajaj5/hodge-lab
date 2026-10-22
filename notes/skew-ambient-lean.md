# One-reflection-skew: constructing the ambient derivation

21 October 2026 EDT / 22 October UTC. **The coordinate derivation assumed
by checkpoint 126 now exists as an explicit Lean definition on the ambient
rational-function field.** Its coordinate values, nonzero denominators and
instantiation of the previous coefficient reduction are proved. This does
not construct a derivation on the sextic hypersurface or a rational primitive.

![Construction, exact coordinate values and domain boundary](../visualizations/skew-ambient.png)

## Inputs and reuse

Notebook parent [`71a44f0`](https://github.com/rbajaj5/hodge-lab/commit/71a44f03e38234f4f2ce82b6d4a956c9e3a2bbc0).
The protected target remains pinned to upstream
[`d5e9ef2`](https://github.com/hodge-computer/sextics/tree/d5e9ef223a2cd210517f35c071e9a5108a15e025).
[Input hashes and conventions](../formal/results/skew-ambient/inputs.json)
reuse the completed source binding: rational coefficients, q=1, physical
variable order `(X0,X1,X2,Y0,Y1,Y2)`, and chart order `(U,r,w,t,z)`.
No new upstream acceptance or discussion audit was performed in this batch.

The [substitution](skew-chart-lean.md), [volume](skew-volume-lean.md) and
[residue coefficient](skew-residue-lean.md) proofs and their saved passing
receipt are hash-checked and reused. Their counts are not added to the
new verification counts. In particular, the chart polynomial is still

\[
G=z^6+(1+r^6+w^6)U^3+rt(1+r^2w)U^2+
\frac{rt(1-t^2)}7U+1+t^6.
\]

## Construction rather than an assumed derivative

[AmbientDerivation.lean](../formal/HodgeLab/OneReflectionSkew/AmbientDerivation.lean)
sets `P = MvPolynomial (Fin 5) ℚ` and `K = FractionRing P`. The five
coordinates are images of polynomial variables under the injective
algebra map `ι : P → K`; no relation G=0 is imposed.

Starting from the actual `MvPolynomial.pderiv 4`, compose with `ι` to
obtain a derivation P → K. Mathlib's formally étale localization theorem
provides the isomorphism

\[
K\otimes_P\Omega_{P/\mathbb Q}\simeq\Omega_{K/\mathbb Q}.
\]

The universal map for the polynomial derivation, base change, this
isomorphism and the universal Kähler derivation define `ambientD`.
Lean then proves `D(ι p)=ι(∂z p)`. Thus DU=Dr=Dw=Dt=0 and Dz=1 are
consequences of the construction, not new hypotheses. The module also
checks the quotient rule and `z² D(z⁻¹)=−1`.

The generic quotient-rule identity is valid even with zero denominator
under Lean's total division convention. Its interpretation as an ordinary
fraction requires a nonzero denominator. The concrete pole reduction
proves the needed conditions: z≠0 by fraction-field injectivity, then
DG=6z⁵≠0, hence G≠0 because D(0)=0. The exact `G_eq_algebraMap`
theorem binds G to the previously checked five-variable chart polynomial,
including its rational coefficient 1/7.

Instantiating the earlier theorem gives, in this explicit ambient field,

\[
-\frac{U^2}{2G^2}
=D\left(\frac{U^2}{12z^5G}\right)
+\frac{6z^5}{G}\frac{5U^2}{72z^{11}}.
\]

No unspecified coordinate derivation remains in that theorem. Conversely,
`no_unchanged_derivation_on_divisor` proves that DU=Dr=Dw=Dt=0, Dz=1,
G=0 and z≠0 are incompatible over a characteristic-zero field. This is
the expected behavior of a normal derivative, not an obstruction to a
rational primitive or to tangential derivations.

## Executed verification and failures

[The reproducible checker](../formal/check_skew_ambient.py) passed with
Python optimization enabled, so required checks do not depend on Python
assertions. [The receipt](../formal/results/skew-ambient/validation.json)
records **12 theorem axiom audits, one new-module kernel replay, seven
positive controls and three rejected false statements**, in **40.047
seconds**. Bounds: 120 seconds per verification process, 600 seconds total;
no timeout. Lean 4.31.0, Python 3.11.9, mathlib
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`.

The negative controls change a base derivative to 1, reverse Dz, or
reverse the reciprocal derivative sign. Each reaches exactly one closed
false goal. The controls are not independent algebraic reconstructions.
The new module's axiom reports contain only standard kernel assumptions;
the default kernel replay reuses imported proofs, including Mathlib's
localization theorem. It is not a fresh replay of all dependencies.

[Development evidence](../formal/results/skew-ambient/development/README.md)
preserves missing-cache, cache-path, field-instance, coefficient-rewrite
and reciprocal-simplification failures. One preliminary verifier run
stopped at that reciprocal elaboration error. The final run passed after
the rewrite. These failures are implementation outcomes, not mathematical
counterexamples or exclusions. A separate read-only agent reviewed the
construction, final verifier and error-control logs without rerunning them.

```sh
# From formal/, with the pinned dependencies installed:
python3 -O check_skew_ambient.py
# From the repository root, with Matplotlib:
python3 scripts/visualize_skew_ambient.py
```

The [diagram generator](../scripts/visualize_skew_ambient.py) requires a
passing receipt and checks source hashes. It displays proved coordinate
values and the dependency chain; it is not a geometric embedding or proof
of a primitive. CI includes the new checker; no future CI result is claimed.

## What remains separate

This closes the ambient-derivation existence dependency for
**Frac(ℚ[U,r,w,t,z])**, with independent coordinates. It does not construct
the lift through the physical square cover U=x², an exterior-derivative or
residue operator, global descent, finite trace, denominator clearing, a
rational primitive or `HasCertificate`. The next interface obligation is
connecting the scalar coefficient identity to actual differential forms
and residue transport. There is no larger denominator exclusion or new
accepted solve.

Credit: Benjamin E. Diamond and contributors for the protected target and
framework; fqlx for the quotient/source reduction; Mathlib contributors,
including Andrew Yang's localization/Kähler differential development, for
the extension theorem used here. No mathematical novelty claim is made.
This batch is published in Hodge Lab only. The Posts index stays at 29
verified discussion contributions; this notebook batch creates no post.

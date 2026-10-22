# One-reflection-skew: from the coefficient identity to actual forms

21 October 2026 EDT / 22 October UTC. **The local reduction now holds
in the exterior algebra of actual Kähler differentials over the explicit
ambient rational-function field.** The ordered volume form is proved
nonzero. This closes the scalar-to-exterior-product step; it does not
construct a general exterior derivative, residue map or rational primitive.

![Actual differentials, orientation, nonzero volume and reduction](../visualizations/skew-forms.png)

## Inputs and reused work

Notebook parent [`2db781f`](https://github.com/rbajaj5/hodge-lab/commit/2db781f19ddc5577db01a3bc178c6c6594e58756).
The protected target remains pinned to upstream
[`d5e9ef2`](https://github.com/hodge-computer/sextics/tree/d5e9ef223a2cd210517f35c071e9a5108a15e025).
[Input hashes and conventions](../formal/results/skew-forms/inputs.json)
retain q=1, rational coefficients, physical variable order
`(X0,X1,X2,Y0,Y1,Y2)` and chart order `(U,r,w,t,z)`.

The completed [substitution](skew-chart-lean.md),
[coordinate-volume](skew-volume-lean.md), [residue coefficient](skew-residue-lean.md)
and [ambient derivation](skew-ambient-lean.md) proofs are reused. The checker
verifies their source hashes and the prior receipt; it does not count these
as new mathematical replays or fetch a new target revision. The polynomial is

\[
G=z^6+(1+r^6+w^6)U^3+rt(1+r^2w)U^2+
\frac{rt(1-t^2)}7U+1+t^6.
\]

## Actual forms and orientation

[DifferentialForms.lean](../formal/HodgeLab/OneReflectionSkew/DifferentialForms.lean)
uses the existing field K=Frac(ℚ[U,r,w,t,z]), with independent coordinates.
It sets Ω=Ω(K/ℚ), E=ExteriorAlgebra(K,Ω), and sends the universal
Kähler differential of f into E to define `oneForm f`. Multiplication in
E is the exterior product. In particular, these are not freely introduced
symbols with an assumed derivative rule.

Fix

\[
\alpha=dU\wedge dr\wedge dw\wedge dt,\qquad
\mathrm{vol}=\alpha\wedge dz.
\]

Lean proves that wedging any of dU, dr, dw, dt on the left of α gives zero.
It derives dz∧α=vol by four antisymmetric swaps, hence the **positive**
normal-first sign. No matrix orientation is silently substituted here.

The two maps f↦df∧α and f↦D(f)vol are ℚ-derivations K→E, where D is
the already constructed normal derivative. They agree on the five
polynomial generators. Polynomial derivation extensionality and then
the quotient rule for arbitrary fractions prove

\[
df\wedge\alpha=D(f)\,\mathrm{vol}\qquad(f\in K).
\]

This is `differential_wedge`. Its proof works in the entire ambient
rational-function field, without adding a relation G=0.

For nonvacuity, base-change the polynomial Kähler basis to K, and use
Mathlib's formally étale localization isomorphism to obtain the basis
(dU,dr,dw,dt,dz) of Ω. Its determinant alternating form extends to a
linear functional λ on E via `ExteriorAlgebra.liftAlternating`, with
zero components in other degrees. Lean proves λ(vol)=1, hence vol≠0.
Thus the orientation and coefficient tests have a nonzero volume against
which to be checked.

## The coefficient reduction now lives in the exterior algebra

The reused coefficient identity and DG=6z⁵ imply the following theorem
`actual_form_reduction` in E:

\[
-\frac{U^2}{2G^2}\,\mathrm{vol}
=d\!\left(\frac{U^2}{12z^5G}\right)\wedge\alpha
+\frac{5U^2}{72z^{11}}\,\frac{dG}{G}\wedge\alpha.
\]

The logarithmic normal form is explicitly G⁻¹dG. Both G and z are
nonzero in K, as proved in the reused ambient module. Geometrically the
formulas are rational on a common open chart; they are not defined at
every point, and this ambient equality cannot simply be evaluated at G=0.

The name `betaDifferential` denotes exactly d(f)∧α, where
f=U²/(12z⁵G). This is the standard differential expression for the
specific decomposable four-form fα, since α is a wedge of coordinate
differentials. **The module does not construct a general map d on E,
prove that such a map is well-defined on every presentation, or provide
a de Rham complex.** The theorem is stated directly in terms of actual
Kähler one-forms and their exterior products, avoiding that extra claim.

## Executed checks and bounded failures

The [checker](../formal/check_skew_forms.py), run with Python optimization
enabled, passed **13 theorem axiom audits, one new-module kernel replay,
five positive controls and three deliberately false statements rejected**
in **60.828 seconds**. [Source-bound receipt](../formal/results/skew-forms/validation.json).
Bounds were 120 seconds per process and 600 seconds total; no timeout.
Lean 4.31.0, Python 3.11.9, mathlib
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`.

The positive controls check λ(vol)=1, vol≠0, λ(dz∧α)=1,
λ(dU∧α)=0 and z²λ(d(z⁻¹)∧α)=−1. Three negative controls reverse
the orientation answer, replace the repeated-wedge zero with one, or
reverse the reciprocal sign. Each fails at exactly one closed False
goal, not an import or elaboration error. These are proof controls,
not independent mathematical reconstructions.

The axiom reports use only propext, Classical.choice and Quot.sound.
The default kernel replay checks the new module and trusts its imports;
it is not a new replay of Mathlib or all earlier notebook proofs.
[Development snapshots and failures](../formal/results/skew-forms/development/README.md)
retain the scalar-tower, missing-cache, noncommutative-algebra and basis
simplification errors. They are implementation failures, not failed
mathematical candidates. A separate read-only agent reviewed the
construction, final checker and error logs without rerunning them.

```sh
# From formal/, with pinned dependencies installed:
python3 -O check_skew_forms.py
# From the repository root, with Matplotlib:
python3 scripts/visualize_skew_forms.py
```

The [diagram generator](../scripts/visualize_skew_forms.py) checks the
receipt and proof-source hashes. It shows the proved orientation,
nonzero functional and form identity; it is a proof dependency diagram,
not a geometric picture of the hypersurface. The rendered PNG was inspected.
CI is wired to the new checker; no future CI outcome is asserted.

## Remaining obligations and attribution

The immediate remaining transport interface is a compatible pullback on
actual differential forms for the physical square cover U=x², followed
by the relevant residue construction. This batch does not supply that
pullback, a general exterior derivative/residue map, global descent,
finite trace, denominator clearing, a hypersurface rational primitive
or `HasCertificate`. It does not extend the bounded exclusion family,
compare the 45 higher-U columns with 504 columns, or solve the target.

Credit Benjamin E. Diamond and contributors for the protected target and
framework; fqlx for the quotient/source reduction; Mathlib contributors,
including Andrew Yang for Kähler localization, for the algebraic APIs.
The formalization combines their results and the previous notebook proofs;
no mathematical novelty claim is made.

Hodge Lab publication only. The Posts list remains at **29** discussion
contributions, including the two recent posts and the edit within the
last one. No upstream post, reply, edit or PR was made in this batch.

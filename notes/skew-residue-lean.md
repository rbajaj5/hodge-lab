# One-reflection-skew: local residue coefficient in Lean

21 October 2026 EDT / 22 October UTC. **The local coefficient +5/72 is now
checked in Lean**, including its sign and the normal-chart assumptions.
The ambient derivative theorem assumes an explicitly specified coordinate
derivation; this pass does not construct that derivation in the target's
function field or instantiate a general residue operator.

![Actual coefficient reduction and separate ambient and divisor charts](../visualizations/skew-residue.png)

## Pinned inputs and reused work

Notebook parent [`4c010b2`](https://github.com/rbajaj5/hodge-lab/commit/4c010b26ee5386f73deee8c9d526f7322420338b);
fresh upstream [`d5e9ef2`](https://github.com/hodge-computer/sextics/tree/d5e9ef223a2cd210517f35c071e9a5108a15e025).
The protected record, REC equation and provenance were freshly read with
45-second request limits. [Input pins and hashes](../formal/results/skew-residue/inputs.json)
agree with the completed proofs: order `(X0,X1,X2,Y0,Y1,Y2)`, rational
coefficients, q=1 and A=X0³Y0³. This is not a new status or acceptance audit.

The [protected substitution](skew-chart-lean.md) and
[ordered coordinate volume](skew-volume-lean.md) are reused. In the chart
Y0=1, φ=(x,rx,wx,1,t,z), U=x², they bind F to

\[
G=z^6+P(U),\quad
P=(1+r^6+w^6)U^3+rt(1+r^2w)U^2+\frac{rt(1-t^2)}7U+1+t^6.
\]

With α=dU∧dr∧dw∧dt, the preceding ordered coefficient is
ψ=−U² α∧dz/(2G²). Its factor 1/2 is from the square-coordinate Jacobian,
not a trace. Existing proofs, input bytes and the prior passing volume
receipt are hash-checked before and after the new verifier; they are not
credited as new kernel replays.

## The actual normal derivative and alternating sign

[NormalChart.lean](../formal/HodgeLab/OneReflectionSkew/NormalChart.lean)
defines the full five-variable polynomial, including its base-parameter
dependence. Lean proves that it evaluates to the existing `chartDenominator`,
that its actual `MvPolynomial.pderiv 4` is 6z⁵, and that the Jacobian of
`(U,r,w,t,G)` has determinant 6z⁵. In characteristic zero this determinant
is nonzero exactly when z≠0.

For **any** covector v=(vU,vr,vw,vt,vz), Lean also proves

\[
\det[v,e_U,e_r,e_w,e_t]=v_z.
\]

This is the ordered alternating-coefficient model of v∧α. The four base
components cancel because their differentials repeat; they need not be
zero. Since α has degree four, dz∧α=+α∧dz. Applying the identity to the
actual gradient gives dG∧α=6z⁵ α∧dz in this coefficient model.

The independent arithmetic check demonstrates the distinction concretely:
at `(U,r,w,t,z)=(1,1,0,0,1)`, the r-partial of the correction coefficient
below is **−1/32**, while its dr∧α contribution is zero. No full base
derivative is silently frozen.

## Quotient differentiation and the factor 5/72

Set f=U²/(12z⁵G) and β=fα. In
[ResidueNormalization.lean](../formal/HodgeLab/OneReflectionSkew/ResidueNormalization.lean),
the derivative calculation is over a characteristic-zero field K with a
rational-algebra structure and **an explicit D : Derivation ℚ K K** such
that DU=Dr=Dw=Dt=0 and Dz=1. These are the values of a normal coordinate
partial, not an assertion that the full differential has no base components.

Using the actual cubic and mathlib's product/power/quotient rules, Lean derives

\[
DG=6z^5,\qquad D(12z^5G)=60z^4G+72z^{10},
\]
\[
Df=-\frac{U^2}{2G^2}-\frac{5U^2}{12z^6G}.
\]

For z≠0 and G≠0, the alternating-coefficient interpretation therefore gives

\[
\psi=d\beta+\frac{5U^2}{12z^6G}\alpha\wedge dz.
\]

The 5 arises from differentiating z⁻⁵; omitting that term changes the
identity. Define the normalized simple-pole coefficient by dividing its
numerator by the **actual evaluated normal partial**:

\[
h=\frac{5U^2/(12z^6)}{G_z}.
\]

The theorem `normalizedPoleCoefficient_eq` proves, using only z≠0,

\[
\boxed{h=\frac{5U^2}{72z^{11}}}.
\]

The separate `simple_pole_factorization` proves the remaining ambient
coefficient is `(G_z/G)h`. Together with the alternating identity, it is
the local factorization `(dG/G)∧(hα)`. Thus under the convention
**Res((dG/G)∧θ)=θ**, the local residue coefficient on the divisor is +hα.
The scalar factor 72 is 12×6; the sign is positive in the stated order.

## The two domains must remain separate

| Step | Conditions actually used |
| --- | --- |
| Actual normal polynomial, partial and determinant | Polynomial identities; nonzero-normal equivalence uses characteristic zero |
| Ambient quotient differentiation and pole reduction | Coordinate derivation as above, z≠0 and G≠0 |
| Simple-pole ambient factorization | z≠0 and G≠0; no derivation hypothesis |
| Normalized coefficient formula | Only z≠0; neither a derivation nor G≠0 is assumed |
| Restricting the final coefficient to the divisor | G=0 and z≠0; it is the coefficient formula that is restricted |

**The ambient derivation cannot be restricted with DU=Dr=Dw=Dt=0,Dz=1
to G=0:** it would send the zero relation to 6z⁵≠0. The proof keeps this
ambient operation separate from the final divisor coefficient. The new
unit does not require x≠0, a≠0 or a discriminant condition. The earlier
inverse square-coordinate step retains its own x≠0 requirement.

The checked divisor control `(U,r,w,t,z)=(-1,1,0,0,1)` has G=0,
G_z=6 and h=5/72. No claim that these five rational coordinates lift to
a rational physical x is needed; the test concerns the U-chart coefficient.

## Executed verification and failed attempts

The [final receipt](../formal/results/skew-residue/validation.json) records
**19 theorem axiom audits, two new-module kernel replays, eight true
control statements compiled together, and five rejected false statements**.
Allowed reported axioms are only `propext`, `Classical.choice`, `Quot.sound`.
Earlier proofs and mathlib are trusted imports, not freshly replayed.

The [independent exact reconstruction](../formal/results/skew-residue/independent.json)
reads the protected polynomial terms, transports them through U=x², and
computes all five G and f partials by sparse rational arithmetic. It checks
the normal determinant, arbitrary-covector cancellation, the complete
pole-reduction and simple-pole factorization, and the divisor specialization.
At `(1,0,0,0,1)`, G=3 and the coefficients satisfy
`−1/18 = −7/36 + 5/36`; h=5/72. These are exact identities and fractions,
not numerical rank estimates. This external computation is distinct from
Lean's conditional derivation theorems.

Lean controls reject a reversed wedge sign, reversed residue sign, missing
normal factor six, omitted z⁻⁵ derivative, and a nonzero-normal claim at
z=0. Each true evaluation is compiled before the false statements. A
negative run must contain exactly one false-proposition diagnostic and no
unrelated error. Explicit requirement failures remain active under `-O`.

Final verification took **36.593 seconds**, bounded by 120 seconds per
process and 600 seconds overall, with no timeout. Lean 4.31.0, mathlib
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`, Python 3.11.9.
[Development snapshots](../formal/results/skew-residue/development/README.md)
preserve algebra-instance, simplification and syntax failures; they are
implementation attempts, not mathematical exclusions. CI is wired to run
the new checker; this note reports local execution, not a future CI outcome.

```sh
# From formal/, with the pinned dependencies installed:
python3 -O check_skew_residue.py
# From the repository root, with Matplotlib:
python3 scripts/visualize_skew_residue.py
```

The [visualization generator](../scripts/visualize_skew_residue.py) reads
the exact receipt, checks source hashes and displays the rational control
identity and the two chart domains. Its rendered PNG was inspected.

## Remaining proof obligations and attribution

This formalizes the **local normal-coefficient calculation under stated
hypotheses**, not a general residue theorem. Constructing the coordinate
derivation in the appropriate ambient function field, connecting this
determinant model to an exterior-derivative/residue API and proving the
global cohomological transport remain separate obligations. No trace,
denominator clearing, rational primitive, `HasCertificate`, extra
denominator coverage, 45-versus-504 comparison or accepted solve follows.
The smallest next formal connection is the ambient derivation construction;
it must precede any claim that all its coordinate hypotheses are instantiated.

Credit remains with Benjamin E. Diamond and upstream contributors for the
protected target/framework, and fqlx for the quotient/source reduction and
companion formulation. The earlier [source note](chi-target-source.md)
already derives this coefficient; the present work formalizes its local
algebra, with no novelty claim. Read-only review checked signs, base
cancellation and the ambient/divisor distinction. Hodge Lab only; no
upstream post or edit. Tally unchanged: **29 discussion contributions,
one closed maintenance PR, zero accepted authored solves**.

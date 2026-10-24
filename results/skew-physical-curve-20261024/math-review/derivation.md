# Read-only mathematical and API review

24 October 2026, America/New_York. Executor: Pro curve_math_review AI.
This is a separate AI review, not human review. No Lean process, symbolic
mathematics checker or historical checker is executed by this reviewer.
The root agent is the sole Lean writer.

## Selected construction

Let B0 = Q[U,r,w,t], realized as `MvPolynomial (Fin 4) Q`, and let B be its
fraction field. Let L be `AlgebraicClosure B`. The chain B0 -> B -> L is
injective: the first map is the fraction-ring embedding and the second is
an injective unital field homomorphism. Consequently the four displayed
base coordinates remain algebraically independent over Q. This is the
critical noncollapse condition. The map from the five-variable chart
polynomial ring into L will intentionally not be injective.

Define the cubic using the existing literal `ChartSubstitution.cubic`.
The algebraically closed root theorem supplies z with
z^6 = -cubic(U,r,w,t). This is an actual field realization of the curve
equation, not an assumption that a suitable field exists. The cubic is
nonzero: its polynomial in B0 evaluates to 1 at U=r=w=t=0, so injectivity
carries its nonzero value into B and L. The equation then gives z != 0.
Likewise each base variable is nonzero by injectivity of its polynomial
image, in particular r and U.

Within the same L one may choose x with x^2=U. Then x != 0, and the prior
protected substitution theorem proves F(x,rx,wx,1,t,z)=0. The protected A
pulls back to x^3. This realizes the square coordinate used in the earlier
normalization without replacing U by an unrelated parameter or silently
collapsing the independent base.

L is an algebraically closed extension of the independent base field. It
is not asserted to be the whole hypersurface function field, nor is the
curve polynomial asserted irreducible. A smaller generated root field
could be extracted later, but no such minimality is needed for the selected
realization. The general result may retain f_r and physical Delta nonzero
as explicit chart hypotheses; their generic nonvanishing is not supplied
by the root-existence argument alone.

## Allowed specialization and forbidden ambient-field map

Let P = Q[U,r,w,t,z], the existing `AmbientDerivation.P`. Polynomial
evaluation P ->_Q L at the five coordinates kills the literal chart
polynomial G. Such a homomorphism is valid; its kernel contains G.

There cannot be a compatible unital homomorphism from the entire old
`AmbientDerivation.K = FractionRing P` to L. The old `G_ne_zero` theorem
makes G invertible in that field, whereas the curve specialization would
send it to zero. A unital field homomorphism is injective, or equivalently
would send G*G^-1=1 to 0=1. This is a domain restriction, not a theorem
about absence of primitives. The existing normal derivation also cannot
descend unchanged: it differentiates G to 6*z^5, which is nonzero on the
chosen z != 0 chart.

The common regular domain S=P[z^-1] is sufficient for the normalized
coefficient. Its inverted element maps to a unit in both old ambient K and
curve L. Thus S maps to both fields while the entire ambient K does not
map to L. A common element is

    (5/72) * U^2 * (z^-1)^11 in S.

Its images are the old `DifferentialForms.residueScalar` and the new
5*U^2/(72*z^11). This route does not try to specialize beta or logarithmic
expressions that invert G. It also does not construct a residue map.

## Universal Kähler and exterior maps

For either target H and the chosen Q-algebra homomorphism f:S->_Q H,
retain the existing Q-algebra on H and obtain its S-algebra from f.
`IsScalarTower.of_algHom f` supplies compatibility of Q->S->H.
Then `KaehlerDifferential.map Q Q S H` is the universal S-linear map
Omega(S/Q) -> Omega(H/Q), and `KaehlerDifferential.map_D` sends d(s)
to d(f(s)). In particular the images of dU,dr,dw,dt,dz are the actual
target Kähler differentials of the realized coordinates.

Compose this map with the degree-one inclusion of
`ExteriorAlgebra H (KaehlerDifferential Q H)`, restricting its scalar
linearity to S. Every resulting degree-one element squares to zero by
`ExteriorAlgebra.ι_sq_zero`, so `ExteriorAlgebra.lift S` produces an actual
exterior-algebra homomorphism. It maps the fourfold product dU*dr*dw*dt to
the target four-form and transports the common normalized coefficient
multiplicatively. The curve relation gives d(G)=0 in Omega(L/Q), including
the induced dependence of dz; it does not preserve the old normal
coordinate derivation.

## Pinned API declarations inspected

Mathlib commit: fabf563a7c95a166b8d7b6efca11c8b4dc9d911f.

- `Mathlib.FieldTheory.IsAlgClosed.AlgebraicClosure` defines the canonical
  `AlgebraicClosure B`, and supplies compatible scalar-tower, Field,
  IsAlgClosed and CharZero instances.
- `IsAlgClosed.exists_pow_nat_eq` produces the sixth and square roots
  directly, avoiding a separate polynomial-degree proof.
- `MvPolynomial.algebraicIndependent_X` and
  `AlgHom.algebraicIndependent_iff` can express the base independence.
- `IsLocalization.liftAlgHom` constructs S->_Q H from the polynomial
  evaluation and unit images of powers of z.
- `Localization.awayLift` is the ring-hom variant.
- `IsLocalization.Away.lift_eq` computes the lift on polynomial images.
- `IsLocalization.Away.mul_invSelf` computes the localized inverse.
- `IsScalarTower.of_algHom` avoids installing an incompatible Q-algebra.
- `KaehlerDifferential.map`, `map_D` and `ExteriorAlgebra.lift` implement
  the universal form maps, rather than stipulating the requested images.

These are API/source observations, not successful compiler executions.
The writer's eventual source and focused receipts must determine what
actually compiles and which of the described links are delivered.

## Source review of the implemented common-domain maps

The current implementation defines one `regularSource` in the actual
exterior algebra over S, then supplies separate `ambientExterior` and
`curveExterior` maps obtained by the universal exterior lift. This is the
right comparison: the two images share an allowed source, without an
ambient-field specialization. `regularCoefficient_curve` targets the
existing normalized coefficient, and `regularCoefficient_ambient` targets
the existing ambient `residueScalar`. The relevant four-form products are
mapped explicitly and both actual target Kähler structures are used.

The public Kähler map is the Q-linear restriction of the universal S-linear
map with target S-action through the selected algebra homomorphism. The
exterior map is returned as a ring homomorphism, with its coefficient action
proved separately; its implementation still comes from the universal
S-algebra map. Neither weakened presentation loses the required coordinate
or coefficient compatibility.

A real implementation obstruction in saved attempt-02 was the old ambient
field's two propositionally equal but not definitionally equal Q-algebras:
`DivisionRing.toRatAlgebra` versus `OreLocalization.instAlgebra`. The old
`DifferentialForms.E` captures the latter. Pinned source inspection supports
matching it explicitly for Ambient-specific declarations by

    OreLocalization.instAlgebra
      (R := P) (S := nonZeroDivisors P) (R₀ := Q).

The generic map must use the supplied target Q-algebra rather than replace
it. `Rat.algebra_rat_subsingleton` also gives propositional equality of the
structures, but explicit instance matching avoids transporting Kähler
modules across that equality. This is an elaboration issue, not a new
mathematical hypothesis or an invalid field-specialization workaround.

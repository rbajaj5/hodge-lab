# Physical chart to trace tower: read-only mathematical/API review

Reviewer: AI worker `/root/curve_math_review`; writer/integrator: `/root`.
Notebook parent: `2bbbaa312642822c28483ba85cbbccf0af97d6dc`.
Upstream pin: `e96be434bd55d6013d7a5854732cb317ca0e43e7`.
Review is source inspection and mathematical reasoning, not Lean execution or an independent human review.

## Initial API lead: basis exchange (not the final implementation)

Reuse the exact actual curve `Curve = AlgebraicClosure (FractionRing (MvPolynomial (Fin 4) Q))` from the preceding unit. Its coordinates U,r,w,t are independent; its chosen z and x satisfy the literal physical curve and square-cover equations. No old proof is rerun by this reviewer.

First promote U,r,w,t to a transcendence basis of Curve. The polynomial variables form a transcendence basis of the polynomial ring. A fraction field is algebraic over its underlying domain (every fraction satisfies a linear polynomial); Curve is algebraic over that fraction field. Therefore two applications of `IsTranscendenceBasis.algebraMap_comp` preserve the basis.

Replace w with v = 1/r + r*w. The nonzero polynomial r^2*Y - (r*v-1) over Q[U,r,t,v] vanishes at w. Its leading coefficient is r^2, which is nonzero in the actual curve field. This relation does not require r inverse to belong to the coefficient subalgebra. The transcendence-basis exchange theorem then gives U,r,v,t as a basis.

Replace r with a = (1+r^6+w^6)/r^3. The already proved exact chart relation says that r is a root of the literal monic polynomial f(Y)=Y^18+Y^12+(vY-1)^6-aY^15 over Q[U,a,v,t]. The exchange theorem gives U,a,v,t as a basis. Restricting gives algebraic independence of a,v,t. This is a proof of generic chart dominance with U retained; it uses neither a random specialization nor an unproved Jacobian criterion.

The intended exchange API is `IsTranscendenceBasis.of_isAlgebraic_adjoin_image_compl`. Finite indexing can use the tuple U,r,w,t,v, exchanging excluded index4 for index2, followed by U,r,v,t,a, exchanging excluded index4 for index1. `finSuccAboveEquiv` identifies each excluded-coordinate subtype with Fin4. These are implementation leads, not reviewer-executed Lean proofs.

## Actual selected implementation: algebraicity and transcendence degree

The sole Lean writer found a shorter implementation of the same algebraic argument. Define ChartField as Q(U,a,v,t) inside the existing Curve. The exact monic physical f makes r algebraic over ChartField; w=(v*r-1)/r^2 is then algebraic there. U and t belong to ChartField. The original transcendence basis U,r,w,t therefore makes Curve algebraic over ChartField, and the field-adjoin/algebra-adjoin transfer converts this to algebraicity over Q[U,a,v,t]. Since Curve has transcendence degree at least4 from the existing independent original coordinates, its four displayed transformed generators must form a transcendence basis. This uses `Algebra.IsAlgebraic.isTranscendenceBasis_of_le_trdeg_of_finite`. Thus the writer does not need explicit basis-exchange indexing.

The generic tower's triple (a,v,t) is independent by applying `AlgebraicIndependent.sumElim_comp` twice to the already proved successive generic transcendence facts and reindexing. Its generated intermediate field is all of BaseField: the helper `ratfunc_image_mem` applies `IntermediateField.adjoin_le_subfield` to a subfield preimage and `RatFunc.adjoin_X`, then is used successively through the three RatFunc layers.

Consequently the generic and physical triples each give an `aevalEquivField` from the same three-variable fraction field. The generic generated field is exactly the existing BaseField. Composing its inverse with the physical fraction-field evaluation produces an actual baseToCurve homomorphism sending a,v,t to the literal chart coordinates. This avoids any unproved successive denominator condition and does not replace the existing generic base.

The source-level argument is mathematically sound; compilation remains the sole writer's responsibility. Pinned APIs reveal competing definitional Q-algebra choices in RatFunc/fraction-field/subfield structures. The review advised composing underlying ring equivalences/homomorphisms and upgrading once using rational-map uniqueness, with `AlgEquiv.ofRingEquiv`, `RingHom.toRatAlgHom`, and `RingHom.map_rat_algebraMap`. The raw rational scalar tower is provided by `IsScalarTower.rat` in `Mathlib.Algebra.Module.Rat`. These are structure-compatibility repairs, not new mathematical hypotheses.

## Field embedding

The generic tower is exactly Q(v)(t)(a), represented by RatFunc(RatFunc(RatFunc Q)). Its injection into Curve must send the three generic generators to the actual vChart(r,w), t, aChart(r,w) and respect all scalar maps. Successive rational-function lifts require transcendence over each already embedded coefficient field, not merely separate transcendence over Q.

Relevant APIs are `RatFunc.algEquivOfTranscendental`, `RatFunc.liftRingHom`/`liftAlgHom`, and `IsFractionRing.liftAlgHom`. The scoped `IntermediateField.algebraAdjoinAdjoin` instances identify the generated field as the fraction field of the generated subalgebra. `IsFractionRing.isAlgebraic_iff` transfers transcendence from the polynomial adjoin to that field. An arbitrary total `RatFunc.eval` is not automatically a homomorphism: denominator nonvanishing must be proved by transcendence.

Once a homomorphism from the generic base field exists, its injectivity follows from the field structure. This does not imply injectivity of E=AdjoinRoot(f) into Curve; f is not assumed irreducible.

## Physical root and optional full splitting comparison

After installing the compatible K-algebra on Curve, explicit polynomial-map equality must identify the mapped generic f with physicalPolynomial(aChart(r,w),vChart(r,w)). The existing chart root theorem gives f(r)=0, hence an actual K-algebra map E -> Curve taking theta to r.

An arbitrary splitting-field embedding into Curve can be constructed with `Polynomial.SplittingField.lift` and `IsAlgClosed.splits`. It does not pick a predetermined sheet index. However, `Polynomial.Splits.image_rootSet` proves that the images of all generic roots exhaust the roots in Curve. Thus there exists a unique index j among Fin18 with splitToCurve(roots j)=r. `AdjoinRoot.algHom_ext` identifies the physical evaluation with splitToCurve composed with sigma_j, since the two maps agree on theta and base scalars. No irreducibility or Galois-transitivity argument is needed.

The physical derivative image must be the literal fR(r,w), proved by derivative/map compatibility, and the existing quotient inverse must map to its reciprocal. The exact physical scalar is sourceScalar's image r^11/(12*fR(r,w)), not the unnormalized weight and not either compact connection row on its own.

## Trace and source boundaries

Trace belongs to the finite free rank18 algebra E/K. It may be transported along K->Curve and equals the sum of all eighteen embedded evaluations. It is not the trace of the one physical root evaluation, not the field trace Curve/K, and has no splitting-field-degree multiplier. E need not be a field. The actual rank-two physical four-form still includes both compact connection rows and the explicit correction term from PhysicalSourceNormalization.

The earlier standard normal-last versus packet/fibre-first sign convention remains unchanged. A scalar trace-zero statement by itself is not a cohomology-source trace-zero theorem. No new residue map, cohomology quotient, primitive, global clearing, certificate or solve follows from this bridge.

## Reviewer execution labels

Executed here: bounded local reads/searches and file/hash recording only. Lean processes:0. Symbolic mathematical checks:0. Old focused checkers:0. Remote CI:0. Commits/pushes/publication:0. The parent writer is responsible for compilation, new kernel replay and controls. A later source-bound review will distinguish proved declarations from these proposed API routes.

# Source and specialization review gates

24 October 2026, America/New_York. Read-only source review by the separate
`curve_evidence_review` AI agent. No Lean, symbolic mathematics, old focused
checker, remote CI or publication was executed by this reviewer.

## Preserved source

The exact notebook parent is e2182223a0395cfb758a2ee09e304eb940b7a67a.
Its ledger has 430,885 bytes and SHA256
f4e1e853360368889cd83be8536d4f0c509a73464d391311c91639c326abbc66.
AGENTS.md and the protected target fields match the prior published source
pins in this checkout; a fresh upstream read is separately recorded by the
integration writer. The protected fields are q=1, A=X0^3Y0^3 and the literal
F in the saved instance.rec. Metadata differences must not replace old hashes.

## Necessary map boundary

The old `AmbientDerivation.P` is Q[U,r,w,t,z], represented by
`MvPolynomial (Fin 5) Q`; its `K` is the full fraction field. The existing
`G_eq_algebraMap` binds the ambient G to `chartPolynomial`, and `G_ne_zero`
proves that G is nonzero in the ambient field. A unital homomorphism from
that field into a nontrivial curve field is injective. Consequently there
is no such field homomorphism that sends G to zero.

Specialization must start with the polynomial ring, or a localization for
which every inverted denominator is proved to survive the specialization.
In particular, G^-1 and the ambient logarithmic-normal expression cannot
be transported through a specialization that imposes G=0. The normal
coordinate derivation also cannot descend unchanged: the existing
`no_unchanged_derivation_on_divisor` is the explicit obstruction.

The normalized coefficient 5U^2/(72z^11) has only a z-dependent denominator
in characteristic zero. This permits a narrower regular domain when z is
proved nonzero. A valid source comparison should exhibit the domain and
both its ambient and curve maps, or explicitly state the narrower polynomial
form comparison it actually constructs. It must not silently introduce a
map from every ambient rational function.

## Generic realization and coordinate independence

A root extension of Frac(Q[U,r,w,t]) for Z^6+cubic(U,r,w,t) is a legitimate
nonvacuous generic curve realization if the base-field map is constructed
and injective. It is not automatically the function field of the entire
irreducible hypersurface. The construction must not assume irreducibility,
replace independent parameters by constants, or claim algebraic independence
without the appropriate injectivity/independence statement.

The existing protected substitution uses U=x^2 and evaluates the sextic at
(x,rx,wx,1,t,z). A construction with independent U,r,w,t is the cubic square-cover
chart. A direct protected-sextic realization additionally needs an actual x
with x^2=U and nonzero x for the ratio chart, or must leave that square-cover
pullback as an explicit boundary. This is separate from the curve equation
in U and z.

## Kähler and exterior comparison

The universal differential maps must use compatible Q-algebra and scalar
structures. They should display the images of dU,dr,dw,dt,dz, preserve the
actual ordered product used by the previous source-normalization theorem,
and derive the curve differential relation from a constructed algebra map.
The same check applies when forming an exterior map after scalar extension.
An expression merely named a pullback is insufficient unless its algebra
or module map has been constructed and its coordinate actions are proved.

The curve realization can discharge r and z nonvanishing by proved facts.
The nonzero f_r and physically substituted Delta conditions remain explicit
unless proved. Generic degree-18 cover separability is not a proof of the
cubic Delta condition. The source theorem must be instantiated with the
actual constructed coordinates and actual curve relation; the desired
cohomology/source equality must not be introduced as an assumption.

## Scope and evidence

The packet's fibre-first versus normal-last convention, the three-swap minus
sign, both compact rows in slot11, and its reported rank34 rational-base
system remain the prior result's scope. No new rank17/CM normalization or
1/864 factor is introduced. A valid map/theorem does not provide a residue
map, de Rham complex, cohomology basis, primitive, global clearing,
certificate or solve.

The final receipt review will distinguish current executions from reused
historical receipts and inspected sources. It will inspect all new declared
axioms, the new-module-only replay, source/input hashes, intended-failure
logs and fresh receipt paths. Reviewer inspection is not independent human
review or a separately executed Lean proof.

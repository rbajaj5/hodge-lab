# Scalar-extension trace bridge: mathematical/API derivation

23 October 2026, America/New_York. Prepared by the Pro AI mathematical/API
reviewer. This is a mathematical derivation and source inspection, not an
independent Lean run or human review. Exact inspected source hashes are in
`api-source-inspection.json`.

## Objects and maps

Use the already constructed field K = Q(v)(t)(a), literal monic polynomial
f = X^18 + X^12 + (vX-1)^6 - aX^15, and its full splitting field L. The previous
module supplies 18 distinct roots rho_j in L, degree 18, separability and the
polynomial equality map(f) = coverPolynomial 1 rho. Those are reused results.
Let E = AdjoinRoot f, theta = AdjoinRoot.root f, and T = L tensor_K E with the
L-algebra structure on the left tensor factor. No field structure on E and
no irreducibility assumption are needed.

For each j, f(rho_j) = 0 makes evaluation descend to a K-algebra map
sigma_j : E -> L. This map sends theta to rho_j and c in K to baseToSplit(c).
The maps sigma_j are not claimed injective: E need not be a domain. Their
product sigma : E -> L^18 extends by the tensor universal property to an
L-algebra map beta : T -> L^18. On pure tensors,

    beta(l tensor e)(j) = l * sigma_j(e).

Consequently beta(1 tensor theta) = rho and beta(l tensor 1) is the constant
vector l. The implementation uses `Algebra.TensorProduct.lift` with the L-scalar
map and all evaluations. Its pure-tensor law reduces definitionally to the
displayed coordinate formula, with the standard left L-algebra structure.

## Why beta is an actual isomorphism

The quotient E has its 18-element power basis because f is nonzero of degree
18 (monicity also suffices). `Algebra.TensorProduct.basis L b` gives the
L-basis of T indexed by that same finite set; its i-th vector is 1 tensor b_i.
Thus dim_L T = 18, with finite/free instances supplied by these bases.

Given y in L^18, let p_y be the degree-at-most-17 Lagrange interpolation
polynomial with p_y(rho_j) = y_j. Evaluate p_y at 1 tensor theta in T. Applying
beta commutes with this L-polynomial evaluation, yielding y. Hence beta is
surjective. Equal finite dimensions imply injectivity, and
`AlgEquiv.ofBijective` gives the L-algebra isomorphism. This argument uses all
18 roots and does not replace the full splitting field by a single-root field.

Compose beta with the inverse of the previous
`SplitTraceQuotient.evaluationEquiv 1 ... rho ...` to obtain the isomorphism
T -> CoverAlgebra 1 rho. Its generator image is the quotient root, since both
are sent to rho by the existing evaluation isomorphism. Scalars remain the
canonical scalars. The equality map(f) = coverPolynomial 1 rho connects this
cover quotient to the literal mapped polynomial without changing any source
normalization or historical pin.

## Trace identity, arbitrary elements

For e in E, multiplication by 1 tensor e on T is the base change of
multiplication by e on E. This is precisely `Algebra.baseChange_lmul`.
`LinearMap.trace_baseChange` applies because E is finite free over K. Taking
traces gives

    baseToSplit(trace_K,E(e)) = trace_L,T(1 tensor e).

An algebra isomorphism conjugates multiplication maps, so for arbitrary z in T,

    trace_L,T(z) = trace_L,L^18(beta(z)) = sum_j beta(z)(j).

The first equality follows from `Algebra.trace_eq_of_algEquiv` (or the existing
short conjugation proof); the second is the already proved split-algebra trace
formula. Combining these identities, for arbitrary e in E,

    baseToSplit(trace_K,E(e)) = sum_j sigma_j(e).

No field trace from L to K is involved, and there is no [L:K] multiplier.
For l in L one further has trace_L,T(l tensor e) =
l * baseToSplit(trace_K,E(e)). In particular trace_K,E(1) = 18 and
trace_L,T(2 tensor 1) = 36. These are useful controls against normalized trace
and a missing tensor scalar factor.

## Element transport completed within the same unit

Separability gives Bezout coprimality of f and f'. Mapping that relation by
AdjoinRoot.mk f makes f vanish, so delta = f'(theta) is a unit in E.
The source APIs are `IsCoprime.map`, `AdjoinRoot.mk_self` and
`isCoprime_zero_left`. The implementation chooses an inverse eta from
`isUnit_iff_exists_inv`, without postulating a field E. Then sigma_j(eta) is
1 / map(f)'(rho_j), proved by mapping delta * eta = 1 and using the previously
proved derivative nonvanishing. Thus theta^i * eta maps to the known
derivative-weighted vector. Trace base change, old slot values, and injectivity
of baseToSplit imply trace 1 for i = 17 and trace 0 for i = 11. The actual module also proves this trace formula
uniformly for all i in Fin 18. The writer compiled these statements in
attempt05, whose exact source snapshot and receipt were inspected by this
reviewer. See `mathematical-review.json` for the hash-bound review. This
reviewer did not execute Lean; the focused checker and kernel replay remain
separate writer executions.

## Boundaries

Every split vector has a preimage in T, but an arbitrary split vector need not
be the image of an element of E. The argument does not furnish arbitrary
Galois descent, a rational primitive, physical differential-source normalization,
global clearing, HasCertificate or a target solve. It preserves all previous
chart and generic-characteristic-zero assumptions and does not turn generic
separability into a universal specialization claim.

# Curvature-mediated response duality

The common object is the holdout's eight-coefficient family, restricted to the same seeded real plane used by the flow experiment. Let `Psi(theta)` contain its eight monomials and write `H(theta,a)=a·Psi(theta)`. The baseline `a=(1,...,1)` is the actual sextic. Changing `a` probes sensitivity; it does not change the target submitted to any certificate checker.

Because all monomials have even total degree, antipodal directions agree. We therefore use `X=RP^1`, with angle modulo pi and a fixed uniform reference measure. On the ordinary circle a maximum would have an equal antipodal partner. The numerical scan on the projective circle finds two simple stationary points, one a maximum. This scan is not an interval proof that all roots were found.

## Envelope response

More generally take a smooth affine family `H(x,a)=h(x)+a·Psi(x)` and a smoothly varying nondegenerate interior maximum `c(a)`. At this critical point define

```text
K = -H_xx > 0,       L = H_xa,       D(a) = H(c(a),a).
```

Differentiating `H_x(c(a),a)=0` gives `K Dc=L`. Differentiating the envelope derivative `D_a D=Psi(c(a))` then gives, in affine coefficient coordinates,

```text
Q = Hess_a D = L^vee K^-1 L = (Dc)^vee K (Dc).
```

Thus coefficient directions generate forces, inverse curvature turns them into motion, and pulling back gives the anisotropic response form. Its kernel is precisely `ker L`, and its positive definite part lives on `A/ker L`. The induced map to `im L` is an isometry for the inverse-curvature pairing. Kernel directions can still change the envelope linearly.

The equivalent variational identity is

```text
(1/2) Q(u,u) = sup_z { <Lu,z> - (1/2) K(z,z) }.
```

This is quadratic convex conjugacy and a Schur complement, standard constructions described in [Boyd–Vandenberghe](https://web.stanford.edu/~boyd/cvxbook/). In one spatial dimension `Q=Psi'(c)Psi'(c)^T/kappa`. For `Psi=sigma*phi` with constant sigma, this includes the factor `sigma^2`; it disappears only when `sigma^2=1`.

## A finite Hodge complex

Choose inner products and use the corresponding Riesz identifications. Put `W=K^-1/2 L`. The two-term complex `A --W--> V` has

```text
Delta_0 = W* W = Q,       Delta_1 = W W*,
Dirac = [[0,W*],[W,0]],   Dirac^2 = diag(Delta_0,Delta_1).
```

Orthogonal decompositions give `A=ker W + im W*` and `V=ker W* + im W`. Harmonic spaces represent `H^0=ker W` and `H^1=coker W`. Positive spectra on the two sides agree, by the singular-value correspondence. This is an instance of the Hilbert-complex framework of [Arnold–Falk–Winther](https://sites.math.rutgers.edu/~falk/papers/bulletin-orig.pdf).

For this chosen plane probe, the eight-dimensional coefficient space couples to one spatial tangent direction. The computed zero-temperature complex has dimensions `dim H^0=7`, `dim H^1=0`. These are the cohomology dimensions of the constructed response complex, not Betti numbers of the sextic hypersurface.

## Thermal extension

For a fixed measure and finite partition function, define `F_T=T log integral exp(H/T)`. Differentiation under the integral gives

```text
Q_T = Hess_a F_T = Cov(Psi)/T = R_T* R_T,
R_T u = <u,Psi-E Psi>/sqrt(T).
```

On a compact domain with a unique global nondegenerate maximum and smooth dependence on parameters, Laplace localization gives `Q_T -> L^vee K^-1 L`. If maxima tie, become degenerate, or lie at a boundary, this conclusion needs to be reconsidered. In a noncompact setting, appropriate integrability and tail control are additional requirements.

The experiment forms the covariance on the GPU and checks its Gram factorization, paired positive eigenmodes, grid refinement, and finite-difference derivatives of the reoptimized maximum. The sampled centered feature curve has rank six although the zero-temperature tangent response has rank one. At `T=0.00002`, the relative Frobenius discrepancy from the predicted limit is about `0.000697`, or `0.070%`.

The signed observable `A/F^(q+1)` is also tracked on this unit-plane probe, retaining the target's `q` and `A` as diagnostics. This real scalar observable is not identified with a complex cohomology class.

```sh
python experiments/response_hodge.py       # GPU covariance calculation
python experiments/response_hodge.py --cpu
```

See the [figure](../results/response-hodge/response-hodge.png), [report](../results/response-hodge/report.json), and [implementation](../experiments/response_hodge.py).

## Spatial weighted Hodge theory

With Gibbs density `p proportional to exp(H/T)` relative to Riemannian volume, the weighted de Rham complex has exterior derivative `d`, weighted adjoint `d_T*`, and Laplacian `d d_T* + d_T* d`. Conjugating by multiplication with `sqrt(p)` sends the derivative to

```text
d_tilde = d - dH wedge /(2T),       d_tilde^2=0.
```

This is the [Witten deformation](https://www.ias.edu/sites/default/files/sns/files/supersymmetry-and-morse-theory-1982.pdf) with potential `-H` and the stated parameter convention. If the reference measure is instead `rho_0 dvol`, conjugation includes the extra term `-(1/2)d log(rho_0) wedge`. Operator domains and boundary conditions remain part of the definition. Our projective-circle probe has no boundary.

The finite covariance complex and the full weighted de Rham complex are different operators. A bridge to algebraic-geometric Hodge theory would further require an identified geometric cohomology object with its Hodge decomposition or filtration and any claimed rational structure or polarization; see [Milne, section 2](https://jmilne.org/math/xnotes/svi2004.pdf). The present factorization supplies concrete response operators, without supplying those additional identifications.

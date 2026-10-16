# Anisotropic interpretations of a sextic puzzle

The holdout fixes six variables, a sextic `F`, pole order `q=1`, and numerator `A=X0^3 Y0^3`. The mixed terms of `F` distinguish coordinate directions:

```text
F = X0^6 + X1^6 + X2^6 + Y0^6 + Y1^6 + Y2^6
    + X0^3 X1 Y0 Y1 + X1^3 X2 Y1 Y2.
```

This suggests three interpretations, with different mathematical content.

## 1. A planar surface energy extracted from F — implemented

Choose a seeded orthonormal real 6-by-2 matrix `U` and evaluate

```text
f(theta) = F(U (cos(theta), sin(theta))).
```

Because `F` is homogeneous of even degree, this is a pi-periodic trigonometric polynomial of degree at most six. Remove its mean and normalize the remaining angular signal to get `g`. Define

```text
S = sum_k |(1-k^2) g_hat(k)|,
epsilon = 0.35/S,
phi(theta) = 1 + epsilon g(theta).
```

The Fourier triangle inequality gives `phi + phi'' >= 0.65` at every angle in exact arithmetic. The even angular symmetry and positive stiffness produce a smooth, strictly convex centrally symmetric Wulff shape and an elliptic anisotropy. The implementation uses floating-point Fourier coefficients and checks the resulting discretization; it is not an interval-certified construction. The constant-signal case would require the isotropic choice `phi=1`; the selected plane has nonzero signal.

We deliberately construct this norm rather than assuming that `F^(1/6)` is convex. A homogeneous polynomial by itself need not define a norm. The map depends on the plane and normalization and is not a canonical invariant of the complex hypersurface.

For a smooth convex curve, let `h(theta,t)` be its support function. Its radius of curvature is `rho=h+h''`. With Euclidean mobility, the planar area-preserving anisotropic curvature equation becomes

```text
h_t = -(phi+phi'')/(h+h'') + lambda(t),
lambda(t) = integral(phi+phi'') dtheta / integral(h+h'') dtheta.
```

The equilibrium support functions are scaled copies of `phi`, plus translation modes. The code uses periodic central differences and explicit Euler steps, followed by rescaling to restore discrete area. That numerical projection is an additional discretization step. Both the uncorrected per-step area error and corrected drift are reported, alongside perimeter, convexity, and grid refinement.

The experiment runs eight curves at 64 and 128 angles. It compares a short GPU trajectory with an independent NumPy implementation. See [the saved report](../results/anisotropic-flow/report.json) and [code](../experiments/anisotropic_flow.py).

[Kim and Kwon](https://arxiv.org/abs/2405.08296v1) study area-preserving anisotropic flat flow and its convergence to unions of equal-area Wulff shapes in the plane. Our convex smooth-flow discretization is inspired by that setting. It does not implement their general minimizing-movement construction or test topology changes. Their planar convergence result does not by itself apply to a high-genus surface or a complex sextic fourfold.

## 2. Anisotropic discrete Hodge theory — a further experiment

Give each oriented mesh edge a positive conductance, collected in a diagonal matrix `W`. If `B` maps vertex functions to edge differences, the scalar energy is

```text
E(f) = (Bf)^T W (Bf),       L = B^T W B.
```

After removing the constant mode on a connected graph, `L` defines a Gaussian field covariance through its inverse. Direction-dependent conductances change the field covariance and the metric used for Hodge projection. For a fixed finite cell complex with positive inner products, harmonic representative spaces still have dimensions equal to the corresponding Betti numbers. The representatives change; topology need not change.

This is a natural bridge to Gaussian fields and the operator/determinant viewpoint in [Dubédat's work on dimers and Cauchy–Riemann operators](https://arxiv.org/abs/1110.2808). It is a proposed extension here, not an implementation of his dimer model. The existing cube benchmark currently uses equal edge conductances and a positive mass.

## 3. Directional heuristics for exact certificate search — open

The two coupling monomials may suggest coordinate blocks, sparsity patterns, or denominator candidates. Such a heuristic can prioritize a search, but every candidate must be checked against the original `(F,q,A)` in the original variables. No equivalence has been established between curvature-flow convergence and existence of the challenge's algebraic certificate.

The concrete exact work is in [the degree-six model](../algebra/README.md): once a denominator is fixed, every permitted numerator correction is included in a rational linear system. That is where a promising geometric pattern would have to become a verifiable algebraic statement.

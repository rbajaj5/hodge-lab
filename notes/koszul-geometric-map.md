# A geometric view of the actual Koszul correction map

The [interactive view](../visualizations/koszul-geometry-standalone.html)
maps a circle of correction coefficients to a response ellipse, while an
exact left syzygy places the target outside the entire projected image.
Download the HTML and open it in a browser; GitHub's file viewer shows its
source. Probe the circle, rotate the equation space, and choose **Fit target
in plane** to see the two displayed response coordinates match while the
syzygy gap remains.

![Three syzygy-preserving views of the actual correction map](../results/koszul-geometry/operator-geometry.png)

This uses three already rejected rational denominators from the
[parameter optimization experiment](koszul-parameter-optimization.md).
We select the first optimized finalist in packet order with each of one,
two, and three nonzero characters: families **1, 2, and 4**. These are fixed
points within families, not new family exclusions. The full failed search
history and all 32 rational rejections remain in that packet.

## Which geometry is displayed?

For fixed `D` and its checked first-equation lift `N0`, the actual induced map is

$$
R_D:z\longmapsto B_D\!\left(\sum_jz_jK_j\right)\bmod F,
\qquad B_D(N)=D\operatorname{div}N-N(D).
$$

The **840** corrections `K_j` are the degree-three monomial multiples of the
gradient Koszul generators `F_j e_i - F_i e_j`. Thus the displayed map is the
composition of the Koszul differential with `B_D`, reduction, and coefficient
extraction. It is not the bare Koszul differential. Write its coefficient
matrix as `M`, the uncorrected term as `b`, and the desired target as `t=-b`.
The exact packet supplies a functional `lambda` satisfying

$$
\lambda M=0,\qquad \lambda b=1.
$$

For every correction, therefore, `-lambda(Mz)=0`, while `-lambda(t)=1`.
This remains true for arbitrary complex correction coefficients. It is the
exact reason the target cannot be reached; the picture displays a real slice.

We choose two orthonormal numerical response observables `U` in the image
of `M`. The first follows `M M^T t`; the second is the matrix column with
largest squared length after removing its first component (ties within
relative `1e-12` go to the first column in the fixed ordering). This is a
specified projection, not a computation of the full map's rank or its two
largest singular directions. Set `S=UM` and diagonalize its two-by-two Gram
matrix:

$$
H=SS^T=V\operatorname{diag}(\sigma_1^2,\sigma_2^2)V^T,
\qquad Q=S^TV\operatorname{diag}(\sigma_1^{-1},\sigma_2^{-1}).
$$

The two columns of `Q` are orthonormal correction directions and
`V^T U M Q = diag(sigma_1,sigma_2)`. The displayed input disk is
`z=R0 Q a`, with `||a||<=1`. Its image in the horizontal observables is an
ellipse. More strongly, the entire 840-dimensional ball `||z||<=R0` projects
onto this same ellipse: components orthogonal to the two columns of `Q` lie
in `ker S`. They need not lie in `ker M`.

Both singular values of **this two-row projection** are positive in the
three examples. The image of the unrestricted full map under these two
observables and the syzygy coordinate is consequently the whole plane at
height zero. The drawn ellipse is a bounded part of that plane, not the
whole correction image.

The source radius is `R0=1.25 ||diag(1/sigma) V^T U t||`. The minimum-norm
correction matching the two horizontal observables therefore lies at radius
`0.8` in the normalized input disk. The fit button finds that projected fit;
it does not solve the full physical least-squares problem. Other undisplayed
equation coordinates can still disagree.

Horizontal coordinates are divided by `R0 sigma_1`, equally in both
directions. The vertical coordinate is `-lambda(v)`, normalized by the
archived exact witness. Thus **gap 1 is a functional value**, not a Euclidean
distance or a comparable error magnitude between denominators. Ellipse
ratios are approximately `0.090`, `0.419`, and `0.986`. The choice of
observables affects these ratios. No general relationship between character
count and conditioning is inferred from these three examples.

Animated transitions interpolate the drawing between selected examples;
they are not additional denominators or an algebraic deformation family.

## The Dubedat intuition, made concrete

Dubedat's [*Dimers and analytic torsion I*](https://arxiv.org/abs/1110.2808v2)
studies families of discrete and continuous Cauchy--Riemann operators,
their determinants, and inverse kernels in the analysis of dimer fields.
Here that motivates examining a linear operator through its image,
response Gram matrix, inverse response, and directions it cannot change.
No identification of our coefficient matrix with his Cauchy--Riemann or
dimer operator is established.

There is a precise finite-dimensional Gaussian analogy. If one *chooses*
independent standard Gaussian correction coefficients `z`, then `Sz` has
covariance `H`. Its covariance ellipses are the same response geometry;
`H^{-1}` measures the minimum squared source norm needed to produce a
horizontal response. Before display rescaling, the image disk has area
`pi R0^2 sqrt(det H)`. None of these operations generates a component with
nonzero syzygy height. This visualization draws the operator directly; it
does not sample a Gaussian free field or add a genus parameter.

The almost round ellipse in family 4 is particularly instructive: good
conditioning of the displayed response does not imply target membership in
the full image. This is a concrete limitation of determinant/Gram intuition
as a solution test. It sharpens a way to inspect our failed attempts, rather
than supplying another solve.

## Checks, source, and reproduction

The builder reads the protected target from `sources/sextics/data/holdout`
at the existing submodule pin. It reconstructs all three first-equation
lifts and all **2,520 correction columns** over `Fraction`, checks the exact
dual pairings, then reconstructs those same columns using the separate
polynomial API and opposite reduction order. The latter shares the stored
E1 basis; this is not independent human review. Orthonormality and the
displayed numerical map are checked to tolerance `1e-10`; the recorded
maximum map discrepancy is below `2.12e-16`.

The browser check covers 126 combinations of family, camera, fit mode,
and width at 736, 360, and 320 pixels. It verifies the displayed map,
fit, obstruction invariant, controls, state restoration, and absence of
detected text collisions or horizontal overflow. Initial label-spacing
failures were corrected before this version was published.

```sh
python experiments/build_koszul_geometry.py --check
python experiments/plot_koszul_geometry.py --check
# Regenerate data, editable fragment, and the static figure:
python experiments/build_koszul_geometry.py
python experiments/plot_koszul_geometry.py
# Optional browser QA after installing Playwright and its Chromium browser:
node experiments/check_koszul_geometry.cjs
```

After a fragment edit, refresh the standalone export with Codex's bundled
visualization renderer before checking it. The check confirms that the
export contains the current fragment. Set `HODGE_BROWSER_CHANNEL=msedge`
to run browser QA with an installed Edge instead of bundled Chromium.

[Display data](../results/koszul-geometry/geometry.json),
[exact/numerical validation](../results/koszul-geometry/validation.json),
[browser validation](../results/koszul-geometry/browser-validation.json), and
[static-figure hashes](../results/koszul-geometry/figure-validation.json)
are retained. The calculations use CPU arithmetic; the display needs no GPU.

Credit belongs to the sextics authors' certificate framework, fqlx's
E1/Koszul and symmetry work, the earlier Hodge Lab computations and exact
witnesses, and Dubedat for the motivating operator viewpoint. This
visualization and explanation were developed with OpenAI Codex assistance
for `rbajaj5`. No new upstream post, full-family exclusion, or accepted
certificate is claimed.

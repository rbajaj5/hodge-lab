# Varying the denominator: rank changes and persistent obstructions

The full Koszul-induced correction map changes rank in this experiment. At
81 rational points in one two-parameter slice its exact rank is 720, 713, or
690. Nevertheless, a common exact left syzygy rejects **every denominator in
that entire slice**, over the complex numbers. This is a restricted consequence
of an already archived necessary condition, not an exclusion of family 4.

A separate search in the full remaining spans of families 1, 4, and 149 keeps
all three characters present. Its six rounded finalists also fail exact checks.
No holdout certificate, Lean proof, or new upstream post results from this batch.

[Interactive denominator sweep](../visualizations/koszul-map-sweep-standalone.html)
— download and open the HTML in a browser; GitHub displays its source.

![Exact rank changes and the persistent target obstruction](../results/koszul-map-sweep/rank-sweep.png)

## The actual map being varied

Keep the upstream target at commit
`b8c4edeb80a82395ec07164caf445cfa43bbbd56`, with `q=1`,
`A=X0^3 Y0^3`, and the exact sextic in
[`instance.rec`](../sources/sextics/data/holdout/instance.rec).
The degree-seven E1 basis supplies pairs `(D_i,N_i)` with `N_i(F)=A D_i`.
Indices below are zero-based raw basis indices, as in the preceding packets.
Set

\[
D(s,t)=D_{42}+sD_{272}+tD_{294},\qquad
N_0(s,t)=N_{42}+sN_{272}+tN_{294}.
\]

These three basis directions have distinct characters, so this normalized
denominator is never zero modulo `F`. It is a small affine slice of family 4,
not its whole surviving 16-dimensional linear span. Fixing the coefficient of
`D_42` to one does not cover directions with that coefficient zero.

For every one of the 840 cubic Koszul fields
`K=m(F_j e_i-F_i e_j)`, form

\[
B_D(N)=D\operatorname{div}N-N(D),\quad
M(s,t)_{\cdot k}=B_{D(s,t)}(K_k)\bmod F,\quad
b(s,t)=B_{D(s,t)}(N_0(s,t))\bmod F.
\]

Thus `M=M0+s M1+t M2` is affine and `b` is quadratic. The numerator condition
is `M z=-b`, allowing a nonzero quotient by `F`; no strict-zero-quotient
restriction is introduced. All 840 correction columns are included. The
matrix has 4,922 coefficient rows in the common union of supports used here.

The sliders evaluate these operators, with fixed coordinates and scales within
each view. They do not interpolate unrelated SVD frames from separate examples.
The 180 ms visual transition evaluates the same polynomial formulas between
the selected rational grid points; the full-rank readout belongs to the selected
endpoint. The exact grid is `s,t in {-2,-3/2,-1,-1/2,0,1/2,1,3/2,2}`.

## What changes rank

| Sampled locus | Points | Full rank over Q | Kernel dimension |
| --- | ---: | ---: | ---: |
| `s != 0` | 72 | 720 | 120 |
| `s = 0, t != 0` | 8 | 713 | 127 |
| `(s,t) = (0,0)` | 1 | 690 | 150 |

These are full rational elimination results, cross-checked by a separate
finite-field elimination modulo 1,000,003. A modular rank by itself would only
give a lower bound over Q; we do not use it alone. These checks also establish
the same ranks over C at the rational samples. **The table does not claim a
complete rank stratification at every unsampled real or complex parameter.**

The spectral view tracks the *720th largest* singular value, divided by the
largest. It is set to exact zero when the independently determined rank is
below 720. This avoids the misleading upward jump obtained by plotting the
smallest *nonzero* singular value after the kernel grows. Nonzero values are
numerical Gram eigenvalues; lines between sampled values are only interpolation.
We also retain a full least-squares residual at each grid point, normalized by
the fourth power of the remainder-coefficient norm of `D`. This score uses a
fixed coefficient metric, not a metric optimized to shrink the error.

These are finite algebraic rank changes. There is no increasing-size ensemble,
free-energy limit, or finite-size scaling test here, so they do not establish
a statistical phase transition.

## Why the projected picture can mislead

The default view reads two actual remainder coefficients, with exponent tuples

```
(5,1,0,5,3,0), (5,5,1,0,0,3)
```

in variable order `X0,X1,X2,Y0,Y1,Y2`. The first row is supported only by the
`D_272` contribution and the second only by `D_294`. Exact row products give

\[
S(s,t)S(s,t)^T
=\begin{pmatrix}2308s^2&0\\0&(2308/9)t^2\end{pmatrix}.
\]

Both projected target coordinates are identically zero. A fixed source ball
therefore projects to an ellipse with displayed semiaxes `|s|` and `|t|/3`.
Its projected rank is 2 when both parameters are nonzero, 1 when exactly one
is zero, and 0 at the origin. At `(1,0)` it collapses to a line even though
the **full** rank remains 720. At `(0,1)` it is also a line, but the full rank
is 713. This is why the picture and exact full rank are shown together.

The alternate view uses two orthonormal response observables selected once
from the full map at `(1,1)`: one Gram response to the target and a transverse
column direction. They remain fixed throughout the sweep. The source radius
is fixed in all 840 coordinates; each view has its own fixed horizontal
normalization. Neither view is a spatial surface or a picture of the full image.

## The obstruction does not disappear

Necessity 24 (zero-based) of family 4's final archived reduction stage restricts
to a nonzero constant on this plane. After normalization its physical dual
`lambda`, stored in
[`validation.json`](../results/koszul-map-sweep/validation.json), satisfies

\[
\lambda M_0=\lambda M_1=\lambda M_2=0,\qquad
\lambda b(s,t)=1.
\]

All 2,520 column pairings and all six quadratic target coefficients are checked
exactly. Therefore `M(s,t)z+b(s,t)=0` is impossible for every complex `s,t,z`
in this slice. The vertical coordinate in the image is `-lambda(v)`: all
corrections have height zero and the desired target `-b` has height one. It
is a functional value with a separately chosen display scale, not Euclidean
distance from the full image. The grid's lower ranks do not defeat this witness.

This restriction was selected for a readable parameter experiment after pilot
checks found ranks 690, 622, 694, 552, and 609 at several pure basis directions,
and 707 or 720 at two trial combinations. Those pilot observations motivated
the slice; this is not a random or representative survey of denominator space.
The final script reconstructs and checks the chosen slice without relying on
the pilot's modular observations.

## A continued search away from character boundaries

The [preceding optimization](koszul-parameter-optimization.md) often converged
toward previously excluded one- or two-character sectors. Here SLSQP searches
the full remaining spans of families **1, 4, and 149**, chosen to include a prior
boundary winner, the visualized family, and another remaining coordinate triple.
This is a deliberately small follow-up, not a new systematic sweep of all triples.

Two seeded starts per family balance the three character energies initially.
The chart fixes its first scaled coefficient to one, bounds the others by
`[-4,4]`, and constrains each character to at least 10% of the denominator's
squared remainder-coefficient norm. Same-character Gram cross terms are
retained. This is an extra *search constraint*, not a condition in the problem.
The full 840-column least-squares correction and the preceding unweighted
objective are retained. Each run allows 80 iterations, 120 evaluations, and
120 seconds; seed is `202610170201 + family`.

| Family | Start | Evaluations | Initial score | Best feasible score | Exact result |
| --- | ---: | ---: | ---: | ---: | --- |
| 1 | 0 | 83 | 0.116966 | 0.0217503 | Rejected |
| 1 | 1 | 81 | 0.347794 | 0.0302585 | Rejected |
| 4 | 0 | 82 | 0.176999 | 0.0245339 | Rejected |
| 4 | 1 | 84 | 0.255292 | 0.0180578 | Rejected |
| 149 | 0 | 82 | 0.139886 | 0.0145694 | Rejected |
| 149 | 1 | 81 | 0.233423 | 0.0186748 | Rejected |

All six runs reached the iteration limit; none established a local or global
optimum. The 493 evaluations include infeasible intermediate SLSQP proposals;
finalists are selected only from feasible, valid fits. All six distinct rational
finalists retain three characters, with minimum exact shares between 0.10000009
and 0.10023638 after rounding the scaled coefficients to rationals with
denominators at most 1,024, then undoing the basis-height scaling. Exact
duals reject them even with every correction allowed. Each rejection is also
reconstructed with a separate polynomial API and opposite remainder reduction
order, checking another 5,040 column pairings.

Scores improved relative to each run's own balanced starting point. There is
**no equal-budget random comparator in this follow-up**, and its constrained
scores should not be presented as beating the earlier unconstrained search.
The constraint prevented character loss but the optimization again pushed
several character shares close to the imposed lower bound. This is useful
diagnostic evidence, not evidence of a solution.

All evaluations, stop messages, exact shares, rounded coordinates, and rejected
certificates remain in
[`results/koszul-interior-search/`](../results/koszul-interior-search).
The preliminary run stopped on JSON serialization of a NumPy boolean; the flag
was converted explicitly and the same seeded batch was rerun. Before archiving
the sweep, its score normalization was corrected to reduce both factors in the
denominator Gram matrix modulo `F`; the rank and obstruction calculations were
unaffected. These implementation corrections are separate from the six failed
mathematical candidates.

## Dubedat intuition, checks, and next questions

The motivation comes from Dubedat's use of parameterized operators,
determinants, and inverse kernels in
[*Dimers and analytic torsion I*](https://arxiv.org/abs/1110.2808v2).
For a standard Gaussian correction vector `z`, `S z` has covariance `S S^T`.
A vanishing covariance eigenvalue is a lost response direction; an inverse
Gram energy becomes singular there. This linear-algebra viewpoint is useful
here. No identification with a dimer model, GFF flow line, high-genus surface,
or imaginary geometry theorem has been proved. In particular this experiment
does not import genus-dependent phase-transition claims.

The exact setup builds on the repository authors' certificate framework,
Griffiths's residue theory and the bridge attributed upstream to Benjamin E.
Diamond; the E1/Koszul and character work includes fqlx's prior results and our
previous checked packets. Eisenbud's syzygy viewpoint motivates retaining the
left relations while changing the map. The constant slice obstruction is a
restriction of our archived triple-family calculation, not a newly discovered
full-family theorem. This batch was developed with OpenAI Codex assistance;
two polynomial implementations and a modular elimination cross-check were run.
No fresh independent human or agent review is claimed.

Reproduce from the repository root:

```sh
python experiments/sweep_koszul_map.py --check
python -S experiments/search_koszul_interior.py --check
python experiments/plot_koszul_sweep.py --check
# Optional new search and figure regeneration:
python experiments/search_koszul_interior.py
python experiments/plot_koszul_sweep.py
# Optional presentation QA, with Playwright installed:
node experiments/check_koszul_sweep.cjs
```

The sweep checker recomputes all rational ranks, modular ranks, physical
columns, quadratic terms, spectra, residuals, and frame data. Check modes do
not overwrite reports. The browser checks cover 72 combinations at content
widths 736, 360, and 320 pixels, both projections and charts, slider/cell input,
tooltips, and saved-state restoration. Static figure hashes bind the image
to the sweep data. Computation here used CPU exact arithmetic and sparse
linear algebra; no GPU acceleration is claimed for this batch.

Useful next steps are to solve the common necessary quadratics before doing
another continuous fit, or to compute symbolic rank bounds on a slice not
already rejected by one constant witness. Widening a picture alone cannot
remove this obstruction. The broader selected families, other character
supports, higher denominator degrees, and the unrestricted holdout problem
remain outside this slice result.

Upstream was checked again during this batch: `main` is still the pinned commit,
`data/holdout/` has no accepted proof, and there were no open PRs. Upstream files
are unchanged. No discussion comment was posted; the ledger tally remains six.

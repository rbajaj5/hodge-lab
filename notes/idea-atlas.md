# An atlas of the ideas behind Hodge Lab

This notebook began with a question about Hodge theory and a wish to see
geometry on a GPU. It developed into a sequence of concrete algebraic
experiments. The route matters: fields suggested operators, operators
suggested candidate rankings, and failed candidates led to exact maps,
syzygies, and polynomial identities.

This is an independent companion notebook to the problems at
[hodge.computer](https://hodge.computer/), with no affiliation to Hodge Labs.
Its purpose is to make our mathematical motivations and experimental record
inspectable. Correctness depends on the stated checks, and acceptance
belongs to the upstream project.

![The idea atlas](../results/idea-atlas/idea-atlas.png)

Purple means an organizing perspective, gold a tested model or heuristic,
and teal an exact result with a specified scope. Dotted connections mean
that one question motivated another. They do not identify different
mathematical objects or prove an implication between the named theories.
The parameter grid is the actual 75-direction quadratic-polar exclusion
history, split into nine earlier vanishings, 56 new power identities, and
ten directions covered by an inherited subfamily proof.

## Fields, handles, and imaginary geometry

**Question:** what do harmonic directions and random fields look like when
a surface has many handles, and how does directional stiffness change them?

The [genus-48 model](high-genus-flow.md) has 7,200 vertices and 96 independent
real harmonic directions. CUDA-sampled Gaussian fields rotate a harmonic
reference field; a paired experiment varies conductance and stiffness. Its
phase response shows a broad crossover. The finite Gaussian covariance
depends analytically on these positive parameters, so a sharp-looking
picture would not establish a thermodynamic phase transition.

The [imaginary-geometry gallery](imaginary-geometry-gallery.md) studies a
different, periodic model: flow textures from a smoothed Gaussian field at
several angles and anisotropies. Sellke's exposition and the Miller–Sheffield
theory motivate the pictures. Dubédat motivates looking at fields and
families of operators together. We do not claim the smooth numerical curves
are continuum SLE flow lines or that either surface is the algebraic target.

**Next useful question:** choose a precise limiting ensemble or a statistic
that can be compared with a theorem before spending more computation on a
claimed phase transition. Chatterjee's concentration perspective remains a
motivation here; no superconcentration theorem was established or applied
to this finite experiment.

## Dubédat, determinants, and candidate design

**Question:** can a determinant with cycle structure generate useful
denominators and a compatible numerator automatically?

The [six-cycle experiment](dubedat-cycles.md) adapts the determinant idea to
the fixed holdout polynomial. Two perfect matchings give a degree-seven
denominator, and its cofactor construction satisfies the first certificate
equation. All 45 distinct tested directions fail the second equation under
the complete permitted correction space; rational dual functionals prove
each rejection. Reciprocal edge reweighting leaves the candidate unchanged,
which identifies a redundant parameter rather than a new search direction.

This is a deliberately chosen algebraic adaptation of ideas from Dubédat's
work. We did not construct the discrete Cauchy–Riemann operators, torsion,
or continuum limits required to invoke his theorems as certificate results.

## Anisotropic Gram matrices

**Question:** can inexpensive geometric measurements help rank polynomial
candidates before an exact test?

In [five sparse candidate pools](denominator-ranking.md), geometric Gram
ranking improved the chosen numerical residual by about 32% relative to a
random-selection expectation. Uniform weighting performed essentially as
well as anisotropic weighting. All 254 distinct finalists were rejected
exactly. A subsequent frontier audit showed that the entire tested degree
had already been excluded upstream; the note preserves this timing mistake.

The useful result is a measured heuristic and its limits. It is not a higher
solve rate. A new test should use an unresolved search space and retain the
uniform control and exact verification.

## Braids, random matrices, and moving roots

**Question:** can tracking roots or eigenspaces through parameter loops
reveal singular behavior that a single matrix snapshot misses?

The [saved Ginibre experiment](../results/source-bridges/report.json) traces
a smooth random-matrix loop. Its discriminant winding is numerically -11
at five sampling resolutions; [the strands](../results/source-bridges/ginibre-braid.png)
make the motion visible. Winding alone does not identify a full braid, and
sampling is not an interval-certified noncollision proof.

A separate [exact cyclic-Fano calculation](cyclic-fano-unfolding.md) finds
a local evaluation map with ramification index three. Circling its branch
value cycles three sheets. This is an actual connection to moving roots on
the fixed target, but we have not transported it into a useful monodromy
action on the certificate correction space. Nor is it identified with the
sextic's separate order-three deck symmetry.

## Yang, types, and Koszul homology

**Question:** which relations are already explained by the equations, and
which graded pieces can force a denominator coefficient to vanish?

The [Yang rationale](why-yang.md) separates Koszul H1, which detects relations
modulo preceding boundaries, from H0, which detects a remaining quotient.
Checked examples have equal H1 dimensions and different H0 dimensions.
Homology-based ranking did not beat its small control groups. We have not
identified the variety, sheaf, and hypotheses needed to apply Yang's
equivariant-sheaf theorems directly to these parameter systems.

The [typed rewrite experiment](typed-rewrite-search.md) uses actual degree
and character gradings, motivated separately by Vishnikin and Okhotin.
Typed caching was slower than the existing method in the frozen comparison.
It did not supply the exclusions. Reordering the actual operator explains
visible blocks, but a new arrangement of pixels is not a new equation.

## Eisenbud, rebuilding, and exact algebra

**Question:** can polynomial multiples of necessary equations force powers
of parameters to vanish, and does rebuilding after those vanishings help?

This has produced concrete progress. On cyclic Fano, the
[full 75-parameter quadratic-direction family](cyclic-fano-remaining66-multipliers.md)
is excluded by exact polynomial identities, physical rebuilding, and a
previous subfamily proof. The last continuation supplies 56 new cube or
fourth-power identities. Separate rational implementations replay the
argument; CUDA evaluations provide a supplementary finite-field check.

The algebraic habit is to keep the full correction space, export witnesses,
and distinguish restricting old equations from rebuilding the physical
map. The computation does not construct a minimal free resolution, prove
the Hodge conjecture, or solve the instance. The
[cubic-direction continuation](cyclic-fano-cubic-polars.md) has 175
coefficients and a larger correction space. Five separate one-component
families and 16 fixed candidates are excluded; arbitrary mixtures remain open.

## Bourbaki, Dolgachev, and Shafarevich

**Question:** can spectral decomposition, curve geometry, and polars suggest
better global support equations?

The [spectral calculation](cyclic-fano-spectrum.md) resolves a normalized
evaluation fiber of length 120 into 117 simple points and one triple point.
Failed squarefree characteristic-polynomial attempts led to the nilpotent
block that explains the multiplicity. [Curve deformation](cyclic-fano-curve.md),
[branch jets](cyclic-fano-higher-unfolding.md), [polars](cyclic-fano-polar-family.md),
and [blowup charts](cyclic-fano-blowup-audit.md) make the geometric route
explicit. They have generated exact tests and useful obstructions, but a
global support divisor with the required certificate remains unconstructed.

## Questions still on the shelf

The conversation also proposed free probability, noncommutative geometry,
vertex algebras, p-adic Hodge theory, Beilinson–Bernstein localization,
KZ/KPZ connections, quantum optics, and Vapnik complexity. These are recorded
as interests, not established methods used in our certificate proofs.

A useful bridge needs a specified object on each side, a map or theorem
with checked hypotheses, and an observable that changes the search. Working
modulo a prime is not by itself p-adic Hodge theory. A genus expansion is
not automatically a strong-coupling calculation. An evocative matrix pattern
does not establish a vertex-algebra structure. The
[T100 record](t100-rebuilt-exclusion.md) preserves earlier unsupported bridges
alongside the exact result that was ultimately obtained.

## What the failures taught us

| Observation | Consequence for the next experiment |
| --- | --- |
| Uniform and anisotropic Gram ranking perform similarly. | Keep the simpler uniform baseline. |
| Reciprocal dimer-edge weights leave the denominator unchanged. | Search distinct polynomial directions, not redundant edge labels. |
| Equal H1 can accompany different H0. | Test the actual graded image before treating homology size as a ranking score. |
| Typed caching adds overhead. | Keep the ordinary exact implementation as the control. |
| A favorable slice can hide a pole. | Test the rational field and the ambient equations, not just the slice. |
| Rebuilding adds constraints after proved vanishings. | Recompute the physical map instead of only deleting old columns. |
| A degree changes the correction space. | Derive completeness again before reusing an old obstruction. |

The linked notes credit the original mathematical sources and upstream
contributions. [LEDGER.md](../LEDGER.md) records publication separately from
research, and [the evidence standards](research-milestones.md) explain what
each type of check establishes.

## Reproduce the atlas

```sh
python experiments/plot_idea_atlas.py
```

The [renderer](../experiments/plot_idea_atlas.py) checks its recorded source
bindings and saves [plot data](../results/idea-atlas/plot-data.json),
[PNG](../results/idea-atlas/idea-atlas.png), and
[SVG](../results/idea-atlas/idea-atlas.svg). This is a navigation diagram
built from existing results, not an additional mathematical proof.

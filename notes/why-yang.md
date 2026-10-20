# Why Yang is useful to this search

**The concrete reason is to distinguish relations among equations from
equations that actually constrain a candidate.** David H. Yang's
[*S_n-equivariant sheaves and Koszul cohomology* (2014)](https://link.springer.com/article/10.1186/s40687-014-0010-9)
describes Koszul cohomology through complexes and gives a geometric
interpretation using equivariant sheaves. This makes it useful background
for organizing our syzygy calculations by kernels, images, and symmetry,
rather than treating a visually complicated matrix or a large kernel as
evidence of progress.

## A checked example that changes the search criterion

For our selected necessary equations P=(P_1,...,P_r) in a rational
polynomial ring S, we compute the classical Koszul complex

\[
K_2(P;S)\xrightarrow{d_2}K_1(P;S)\xrightarrow{d_1}S,
\qquad d_1(C)=\sum_j C_jP_j.
\]

Its two relevant quotients answer different questions:

- `H1 = ker(d1)/im(d2)` measures relations after removing the automatic
  Koszul boundaries. A cycle is a relation among the existing equations;
  it is not itself an additional equation on a denominator.
- `H0 = S/(P)` measures what the equations' polynomial multiples fail to
  span. If its degree-d part is zero, every degree-d monomial, including
  every coordinate power, lies in the necessary ideal.

The [already checked added-character experiment](added-character-homology.md#what-h1-misses-and-h0-detects)
gives a concrete distinction:

| Selected family | Degree-four H1 dimension | Degree-four H0 dimension |
| --- | ---: | ---: |
| A19 | 3 | 11 |
| A30 | 3 | 0 |
| A61 | 0 | 0 |

A19 and A30 have equal H1, but different images. A61 has no degree-four
H1 and nevertheless supplies all quartic coordinate powers. Thus ranking
only by H1 can miss the property needed for this exclusion search. The
experiment's high-H1 and low-H1 groups both closed 4/4; it did not establish
a ranking advantage.

![Actual added-character maps and their H0 comparison](../results/added-character-homology/added-character-koszul-map.png)

Our practical response is to inspect the graded image and test explicit
identities `a_i^d = sum_j C_j P_j`. Such an identity forces `a_i=0` over
the complex numbers. Individual coordinate powers can suffice even when
H0 is nonzero, so a full image is a useful sufficient condition, not a
required one. Every identity still has to be linked to the fixed holdout
equations; these necessary ideals need not describe every valid numerator.

## What is, and is not, being used

The kernel/image distinction is classical Koszul algebra, not a new result
of Yang's paper. Yang supplies a relevant geometric perspective and a
reason to study the whole complex, including symmetry. Our actual
calculations above use classical Koszul homology and Eisenbud's graded
syzygy framework. They are not an implementation of Yang's equivariant
sheaf construction.

To apply Yang's geometric theorems directly, we would first need to identify
the appropriate smooth projective variety, line bundles and sheaf, and
verify the required hypotheses. We have not done that. Our coefficient
degree is not automatically his positivity parameter, and our diagonal
character grading is not his symmetric-group action. GPUs cannot supply
these missing mathematical identifications; the current exact calculations
run on CPUs.

This is a concrete, limited reason to read and borrow perspective from
Yang: it helped frame a testable distinction, and the recorded experiment
shows why that distinction matters. It does not establish that Yang's
theorem solves holdout or that the homology heuristic improves search.

## Evidence and credit

The numerical dimensions and failed ranking comparison were already
published in [holdout discussion contribution 15](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18999334).
The [immutable experiment](https://github.com/rbajaj5/hodge-lab/blob/718cf9a2e721b58782748ac90414dd7707f2a061/notes/added-character-homology.md)
contains the exact checks, figure data, search bounds, prior work, and
limitations. This note explains that evidence; it adds no new exclusion.

Prepared with OpenAI Codex assistance for rbajaj5. Credit Yang for his
geometric interpretation, Eisenbud for the syzygy viewpoint, and the
Sextics authors, Benjamin E. Diamond's attributed bridge, Griffiths,
fqlx, and preceding contributors for the certificate framework and
physical reductions used in the experiment. Holdout remains unsolved.

## Update (19 October 2026): Visual Categorification & Chain Maps on `one-reflection-skew`

We extended the Yang/Eisenbud Koszul homology diagnostic and implemented
explicit functorial chain maps on `one-reflection-skew` ([Discussion #127](https://github.com/hodge-computer/sextics/discussions/127)):
- **Graded Koszul homology ($H_0, H_1, H_2$) across the 5-ideal hierarchy:** [`notes/one-reflection-skew-koszul-homology.md`](one-reflection-skew-koszul-homology.md) · [`one-reflection-skew-koszul-homology.png`](../results/one-reflection-skew-koszul/one-reflection-skew-koszul-homology.png)
- **Spivak operadic wiring & exterior-power chain maps $\Lambda^k(T)$, Yang $\mathbb{Z}_2^{\text{Kramers}}$ channels, and Buehler 2-head bilinear attention $\mathcal{B} = \mathcal{A}_{\text{div}} + \mathcal{A}_{\text{Lie}}$:** [`notes/categorified-koszul-network.md`](categorified-koszul-network.md) · [`categorified-koszul-network.png`](../results/categorified-koszul-network/categorified-koszul-network.png)
- **Mumford (*Indra's Pearls* & *Pattern Theory*), Dyatlov (Fractal Uncertainty Principle & Pollicott–Ruelle resonances), and Minsky (curve-complex subsurface hierarchy):** [`notes/dyatlov-mumford-minsky-chaos-ag.md`](dyatlov-mumford-minsky-chaos-ag.md) · [`dyatlov-mumford-minsky-chaos-ag.png`](../results/dyatlov-mumford-minsky/dyatlov-mumford-minsky-chaos-ag.png)

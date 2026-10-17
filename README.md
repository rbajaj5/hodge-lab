# Hodge Lab

**From random surfaces and flowing fields to exact polynomial identities.**

An independent mathematical notebook by [rbajaj5](https://github.com/rbajaj5),
exploring problems from [hodge.computer](https://hodge.computer/). Geometric
intuition suggests a candidate; computation tests it; exact algebra decides
whether the proposed identity holds. This repository keeps the pictures,
source code, checks, and failed approaches together.

This is an independent learning and research notebook. It is not affiliated
with Hodge Labs, hodge.computer, or the maintainers of
`hodge-computer/sextics`; similar naming was unintentional.

This is the **meta-repository for our work in [hodge-computer/sextics](https://github.com/hodge-computer/sextics)**: it records the motivation for our approaches, supporting experiments, and the purpose and outcome of each public contribution. The [contribution ledger](LEDGER.md) links to the actual upstream posts and submissions.

**Current status: no new accepted Hodge solve.** The repository contains actual GPU runs, exact rejection certificates, independent checks, and the approaches that failed. Code and notes were developed with AI assistance; the recorded checks describe what was executed.

**Publication:** new experiments appear here first. Upstream discussion
updates are reserved for infrequent, substantial batches; the
[ledger](LEDGER.md) distinguishes notebook work from actual contributions.

**How we judge progress:** a useful exclusion, a simpler baseline that performs equally well, and a corrected claim all count as results. Numerical ranking, exact certificates, and external review are separate milestones. [Evidence standards and next experiments](notes/research-milestones.md).

## GPU spotlight: a rank gap becomes a proof

**175 correction columns. 25 exact relations. Rank at most 150.**
The RTX 5070 Ti Laptop GPU finds rank **151** when the target column is
added for each of 16 tested cubic-direction denominators. An exact upper
bound makes that gap decisive: the target cannot lie in the correction image.

Each correction column is an allowed change to the numerator. The added
column is the error the candidate must cancel. If it increases the rank,
no combination of allowed corrections can reach it. The reusable exact
bound lets small finite-field witnesses certify that failure in characteristic zero.

[![The actual GPU rank calculation, the exact 175-to-150 correction shortcut, CPU checks, and the sixteen fixed-denominator exclusion certificates](results/cyclic-fano-cubic-polars-figures/cyclic-fano-cubic-gpu-shortcut.png)](notes/cyclic-fano-cubic-polars.md)

| What ran | Recorded result |
| --- | --- |
| **CUDA integer elimination**, modulo 65,521, on the complete coefficient matrices | All 16 candidates: correction rank **150**, augmented rank **151**. |
| **GPU controls** with a target constructed inside each correction image | All 16 controls: **150 / 150**. Three small rank controls also pass. |
| **Independent NumPy elimination** on all 32 candidate/control matrices | Every rank agrees with CUDA. |
| **Exact CPU algebra** | 25 universal column relations prove rank ≤150 over the rationals; 16 nonzero 151×151 minors prove augmented rank ≥151. This certifies the fixed exclusions over the complex numbers. |

**Measured elimination time:** CUDA **0.192 s**; NumPy **14.175 s**.
Matrix construction took **16.894 s** separately. These are timings for this
batch and these implementations; CUDA compilation, upload and minor
extraction are outside the elimination timing. The GPU run uses all 175
columns. The algebraic shortcut makes the modular rank result a proof;
it is not a measured column-compression speedup.

The GPU performed the arithmetic screen. CPU code reconstructed the
polynomials and checked the exact proof. AI assisted experiment design,
code, mathematical reasoning and documentation. **Five cases are controls;
eleven are fixed mixed candidates. The full 175-parameter family remains open.**

[Run the CUDA code](experiments/gpu_cyclic_fano_cubic_screen.py)
· [Inspect the device, directions, timings and minors](results/cyclic-fano-cubic-gpu/report.json)
· [Replay the independent CPU certificate](experiments/check_cyclic_fano_cubic_polars.py)
· [Read the derivation and limits](notes/cyclic-fano-cubic-polars.md).

## Lean proof map

[![A source-linked proof map: external dimension bounds feed a Lean proof that an augmented rank gap rules out span membership, with the 150/151 specialization and no-correction corollary](results/lean-rank-gap/lean-rank-gap.png)](formal/README.md)

The first Lean project formalizes the **generic rank-gap argument**. Its
proof map follows the actual code: assuming the target is in the correction
span makes the augmented span equal to it, contradicting the two dimension
bounds. Three theorem statements cover the general argument, the 150/151
specialization, and the absence of a correction solution.

**Checked locally:** all three theorems compile in Lean 4.31.0, pass the
axiom audit, and replay with the standalone kernel checker. The figure
binds those records to the exact source files.

The concrete matrices, 25 column relations, and sixteen minor calculations
are checked by the Python programs above; their rank bounds are explicit
hypotheses in Lean. They have not yet been formalized there.
[Lean source](formal/HodgeLab/RankGap.lean)
· [Build, axiom audit, and visual walkthrough](formal/README.md).

## A map of the ideas

[![Seven research routes: high-genus fields, Dubédat-inspired determinants, Gram ranking, braids, typed relations, Koszul equations and classical geometry; each linked to its tested outcome and limits](results/idea-atlas/idea-atlas.png)](notes/idea-atlas.md)

The connections are research motivations, not claimed theorem implications.
[Open the idea atlas](notes/idea-atlas.md) for the question behind each route,
what was actually computed, and what would make the next experiment useful.

| See the geometry | Inspect the algebra |
| --- | --- |
| [![A computed Gaussian field and flow on a surface with 48 handles](results/high-genus-flow/genus48-K-0.2.png)](notes/high-genus-flow.md) | [![The actual Koszul operator drawn as correction directions and an obstruction](results/koszul-geometry/operator-geometry.png)](notes/koszul-geometric-map.md) |
| **48 handles, 96 harmonic directions.** A finite Gaussian model shows a smooth coherence crossover. [Fields, topology and phase-response measurements](notes/high-genus-flow.md). | **What can a correction change?** A geometric picture of the actual linear map helps separate its image from an obstruction. [Construction and limits](notes/koszul-geometric-map.md). |
| [![Flow textures for three angles of the same smoothed Gaussian field](results/imaginary-geometry/angle-triptych.png)](notes/imaginary-geometry-gallery.md) | [![Numerical eigenvalue strands in a smooth random-matrix loop](results/source-bridges/ginibre-braid.png)](notes/idea-atlas.md#braids-random-matrices-and-moving-roots) |
| **Imaginary-geometry intuition.** CUDA-generated field textures make angle and anisotropy visible. These are regularized finite models. | **Braids and moving roots.** Follow the winding of random-matrix eigenvalues, then compare it with the exact local three-sheet geometry on cyclic Fano. |

Choose a route: [visual intuition](notes/idea-atlas.md#fields-handles-and-imaginary-geometry)
· [candidate design](notes/dubedat-cycles.md)
· [exact syzygy calculations](notes/cyclic-fano-remaining66-multipliers.md)
· [negative results worth keeping](notes/idea-atlas.md#what-the-failures-taught-us).

## Visual notebook: cyclic Fano

Click a figure to open its equations, reproducible code, checks, and limits.
These pictures show actual calculations and failed candidates; the instance
still has no certificate from this notebook.

**Latest calculation — cubic directions, degree eight.** Five separate
35-parameter families are excluded: allow any homogeneous cubic in one
vector component, with the other four components zero. In each family,
exact cubes give `35 → 10`, then squares in the reduced equations finish
the exclusion. The initial square searches failed. These are five
conditional family exclusions. The full mixed 175-parameter family remains open.

[![Five separate cubic-direction families reduce from 35 parameters to 10 and then zero, with the full mixed family still open](results/cyclic-fano-cubic-polars-figures/cyclic-fano-cubic-polars.png)](notes/cyclic-fano-cubic-polars.md)

The GPU also screens 16 fixed candidates. Exact relations bound the
correction rank by 150, and explicit nonzero augmented minors give rank
151. Independent CPU reconstruction turns these particular rank failures
into exact exclusions, including eleven mixed candidates and five controls.
[Actual maps, correction-space growth, and the rank checks](results/cyclic-fano-cubic-polars-figures/cyclic-fano-cubic-polars-maps.png).

**Previous complete family — all 75 quadratic-direction parameters excluded.**
Larger polynomial multipliers and repeated rebuilding reduce the previous
66-parameter remainder through `65 → 60 → 53 → 45 → 37 → 21 → 10`.
The final ten directions lie in the already excluded coordinate-divisible
subfamily; its exact proof closes the chain. All numerator corrections remain
allowed. This is a complete exclusion of this degree-seven polar family,
not a solution of the instance or an exclusion of arbitrary degree-seven
denominators. Unsuccessful searches and timeouts remain in the packet.

[![Exact polynomial identities and rebuilding close the 66-parameter remainder of the full quadratic-direction polar family](results/cyclic-fano-remaining66-multipliers-figures/cyclic-fano-remaining66-multipliers.png)](notes/cyclic-fano-remaining66-multipliers.md)

[Inspect the equivalent bases, larger multiplier maps, and rebuilding gains](results/cyclic-fano-remaining66-multipliers-figures/cyclic-fano-remaining66-multipliers-maps.png).

**Previous checkpoint — nine necessary vanishings in the full 75-parameter family.**
All five components of the direction field may now be arbitrary homogeneous
quadratics. Eight exact cube identities force eight coefficients to zero;
rebuilding supplies five extra independent quadratic constraints and a ninth
cube identity. The 66-parameter remainder was unresolved at this checkpoint;
the continuation above closes it. The earlier sparse cubic searches and
small quartic search found no additional powers in their tested spaces.

[![The full quadratic-direction parameter grid, its nine exact vanishings, and the unresolved 66-parameter remainder](results/cyclic-fano-full-quadratic-multipliers-figures/cyclic-fano-full-quadratic-multipliers.png)](notes/cyclic-fano-full-quadratic-multipliers.md)

[Inspect the full-family coefficient blocks and bounded searches](results/cyclic-fano-full-quadratic-multipliers-figures/cyclic-fano-full-quadratic-multipliers-maps.png).

**Previous complete subfamily — polynomial multipliers close a 25-parameter gap.**
For the degree-seven family with `v_i = x_i (M x)_i`, cubic identities force
20 matrix entries to vanish. Rebuilding the complete correction equations
then forces the five remaining entries to vanish. This excludes the entire
stated family over the complex numbers. The continuation above uses this
result to finish the unrestricted 75-parameter quadratic-direction family.

[![Cubic multiplier identities reduce the coordinate-divisible direction matrix from 25 entries to its Y0 column, then to zero after rebuilding](results/cyclic-fano-divisible-multipliers-figures/cyclic-fano-divisible-multipliers.png)](notes/cyclic-fano-divisible-multipliers.md)

[Inspect the necessary equations and multiplier maps](results/cyclic-fano-divisible-multipliers-figures/cyclic-fano-divisible-multipliers-maps.png).

| Follow the algebraic reductions | Compare earlier calculations |
| --- | --- |
| [![The preceding quadratic-polar checkpoint: five separate component families excluded](results/cyclic-fano-quadratic-polars-figures/cyclic-fano-quadratic-polars.png)](notes/cyclic-fano-quadratic-polars.md) | [![The degree-six linear-polar map and its exact reduction from 25 parameters to zero](results/cyclic-fano-linear-polars-figures/cyclic-fano-linear-polars.png)](notes/cyclic-fano-linear-polars.md) |
| **Earlier quadratic screen.** Five separate component families were excluded. The 25-parameter gap marked open in this historical figure is closed above. [Coefficient maps](results/cyclic-fano-quadratic-polars-figures/cyclic-fano-quadratic-polars-maps.png). | **Linear directions, degree six.** Square and cubic identities exclude every nonzero `v = M x`. [Coefficient maps](results/cyclic-fano-linear-polars-figures/cyclic-fano-linear-polars-maps.png). |
| [![The 26 tested products grouped by formal factor labels, with direct exclusions distinguished from the support-theorem deduction for S squared](results/cyclic-fano-support-audit-figures/cyclic-fano-support-audit.png)](notes/cyclic-fano-support-audit.md) | [![The denominator curve before and after blowing up a transverse plane](results/cyclic-fano-blowup-audit-figures/cyclic-fano-blowup-audit.png)](notes/cyclic-fano-blowup-audit.md) |
| **Support versus multiplicity.** The `q=1` theorem closes the `S²` timeout from the checked `S` obstruction. The failed run remains recorded. | **Blowup charts.** A pole order of five separates into one exceptional factor and four orders of contact. The pole persists. |
| [![Exact deformation matrix of a complex rational curve on the weighted cyclic quotient](results/cyclic-fano-curve-figures/cyclic-fano-map.png)](notes/cyclic-fano-curve.md) | [![Higher local branch jets, two contacting branches, and nine rejected denominator guesses](results/cyclic-fano-higher-unfolding-figures/cyclic-fano-higher-unfolding.png)](notes/cyclic-fano-higher-unfolding.md) |
| **A curve we can deform.** An exact rank-six matrix supplies a free rational curve on the quotient. A global support equation is still missing. | **Local branches to global guesses.** Higher jets suggest nine candidates; complete exact tests reject all nine. The displayed curves are leading-term approximations. |

**Why read Yang?** The checked examples distinguish relations among equations
from the graded images that force denominator coefficients to vanish.
Equal Koszul H1 dimensions can accompany very different H0 dimensions;
our homology ranking did not outperform its controls.
[Concrete mathematical rationale, figure, evidence, and limits](notes/why-yang.md).

**Current direction: Diamond's ten newly added targets only.** On
`cyclic-triple-fano`, an explicit free rational curve and a checked
three-parameter incidence family give dominant marked evaluation on the
weighted quotient. Its deformation map has an exact positive Gram matrix;
Bourbaki's spectral projectors give a checked right inverse. The support
divisor and certificate remain unconstructed.
[Curve, spectral visualizations, checks, and limits](notes/cyclic-fano-curve.md).

The continuation reduces one complete normalized evaluation fiber to three
equations of degrees four, five, and six. An exact Macaulay minor proves
fiber length 120 with multiplicities. Both curve charts have unit evaluation
minors, and one omitted section maps into `X1=0`.
[Fiber proof, boundary visualization, and limits](notes/cyclic-fano-continuation.md).

The spectral follow-up resolves that fiber's multiplicities: **117 simple
points and one triple point over the complex numbers**. Exact multiplication
operators, a trace-pairing minor, and a local cubic calculation prove the
count. All seven squarefree-characteristic-polynomial attempts failed;
the resulting nilpotent block supplied the useful clue.
[Spectral proof, two visualizations, and failed attempts](notes/cyclic-fano-spectrum.md).

Moving the evaluation point along an actual curve on the same target
smooths the triple point into three nearby sheets. The exact local map has
ramification index three. All four target tangent directions together still
fail the first-order versality test; no generic cusp or global branch equation
is claimed. [Local geometry, monodromy visualization, and failed directions](notes/cyclic-fano-unfolding.md).

The final supplied Bourbaki character projectors reduce a degree-three
fixed-denominator numerator search from 756 to 150 coefficients. Exact
Piola transfer preserves the physical equations. Three denominators suggested
by the branch and boundary geometry all fail, each with a short rational
obstruction. [Character maps, proof, and failed guesses](notes/cyclic-fano-transfer.md).

Higher-order unfolding reveals two local critical-value branches with
contact order three in the `Y0` direction. The `X0` direction remains zero
at the tested centered orders. The more specific geometry generates nine
denominator guesses and repairs; **all nine fail exact tests**, including
the full Koszul correction and quotient spaces for the repaired candidates.
[Local geometry and visualization](notes/cyclic-fano-higher-unfolding.md),
[candidate tests, exact obstructions, and failures](notes/cyclic-fano-guided-denominators.md).

The powers-and-products continuation directly excludes **25 of 26 specified
denominators**, with degrees ranging from two to twelve. The degree-twelve
square `S^2` timed out after a 120-second search. A later
[support audit](notes/cyclic-fano-support-audit.md) closes it using the exact
`S` obstruction and the repository's prescribed-support theorem at `q=1`.
All 26 are now covered with that theorem; the timeout remains recorded.
Higher powers of each excluded support are also ruled out. A complete
reflection reduction makes the larger tests smaller; the pure Jacobian
powers `J^3` and `J^4` share the same 630-column system. These are selected
products, not every denominator through degree twelve.
[Proof reduction, coverage visualization, exact failures, and timeout](notes/cyclic-fano-branch-products.md).

Dolgachev's first-polars construction gives a separate degree-five family
with an explicit solution of the first equation. Seven fixed directions
all fail the complete second equation, each with a one-coefficient exact
obstruction. This original pilot tested seven directions.
[Geometric derivation, actual Koszul-map visualization, and checked pilot](notes/cyclic-fano-branch-polars.md).

The [full constant-direction polar-family calculation](notes/cyclic-fano-polar-family.md)
extends that pilot to **every nonzero complex constant direction**. Five
exact coefficient equations force all five direction parameters to vanish;
the complete correction and quotient spaces cannot change those equations
after reflection averaging. This excludes this degree-five family, not
arbitrary degree-five denominators or products of polars.

The [degree-six continuation](notes/cyclic-fano-linear-polars.md) lets the
direction vary linearly as `v = M x`. Twenty exact square identities and
five cubic identities exclude every nonzero matrix `M`, with all permitted
corrections retained. This excludes that 25-parameter family; other
degree-six denominators remain open.

The [quadratic-direction continuation](notes/cyclic-fano-quadratic-polars.md)
raises the denominator degree to seven and retains 55 correction types,
including five mixed types that first appear at this degree. Complete
one-component families `v = f(x) partial_i`, with arbitrary homogeneous
quadratic `f`, are excluded by two rounds of exact square identities.
This permits extra support from `f`; it goes beyond taking powers of the
old fixed polar. The 75-parameter family of general sums was unresolved at
this checkpoint and is excluded in the latest continuation above.

The [polynomial-multiplier follow-up](notes/cyclic-fano-divisible-multipliers.md)
closes the previously unresolved 25-parameter subfamily `v_i = x_i (M x)_i`.
Eliminating corrections gives 155 exact necessary quadrics. Linear
multipliers force cubes of 20 entries outside the `Y0` column. Rebuilding
with the five remaining entries yields 12 necessary quadrics whose linear
multiples force the last five cubes. Both unsuccessful square tests remain
recorded; a degree-four search was unnecessary. This is a complete exclusion
of that subfamily, with all numerator corrections allowed. The instance
remains unsolved by this notebook.

The [full-family continuation](notes/cyclic-fano-full-quadratic-multipliers.md)
allows all 75 coefficients simultaneously. It proves nine necessary
coefficient vanishings using two rounds of cubic identities, retaining all
55 correction types. The first rebuild gains five independent quadrics;
the second gains none. The remaining 66 parameters were unresolved. Four
large modular block searches hit explicit work limits, and a restricted
quartic search found no additional coordinate powers. These limits remain
recorded alongside the rational proofs.

The [larger-multiplier continuation](notes/cyclic-fano-remaining66-multipliers.md)
now closes those 66 parameters. Exact changes of equation basis expose
useful sparse subsystems; cubic and quartic identities force further zeros.
Six physical rebuilds add respectively `1, 11, 7, 13, 26, 20` independent
necessary quadrics beyond simply restricting the preceding equations.
The final ten directions embed in the previously excluded 25-parameter
subfamily. Both rational checkers replay the chain and the closure. A
separate CUDA finite-field screen checks the factored identities and rejects
deliberately altered coefficients; it supplements the exact proofs.

A Shafarevich-inspired [restriction audit](notes/cyclic-fano-slice-audit.md)
shows why a successful-looking curve slice can mislead: one polar's residual
and denominator both vanish on the slice, while a numerator component stays
nonzero. The rational field has a pole; this is no new certificate.

The follow-up [blowup-chart audit](notes/cyclic-fano-blowup-audit.md)
separates exceptional-divisor multiplicity from special approach directions.
The scalar coefficient still has a simple pole along the exceptional divisor;
the previously observed order-five pole is one plus four orders of contact
with the strict transform. The figure shows this local geometry, not a
resolved candidate or a new certificate.

A preceding bounded pilot examined `quadric-contact-broken`, another newly
added target. A natural quartic denominator passes the first equation but fails
the complete normalized correction test: one coefficient annihilates all
36 correction/quotient columns and detects a nonzero residual.
[Fixed-denominator obstruction, map visualization, and limits](notes/quadric-contact-pilot.md).
This earlier pilot is included in the notebook batch; no new upstream
discussion comment is implied.

![Exact deformation map for the new cyclic Fano target](results/cyclic-fano-curve-figures/cyclic-fano-map.png)

**Preceding checkpoint:** work on `cycle-three` and `mixed-biweight`, with
different fixed hypersurface equations from holdout. Exact calculations now
exclude every denominator of **degree zero through six for both targets**.
All coefficients and numerator corrections are included; nonzero quotients
are allowed. The mixed continuation includes all three extra E1 directions,
reduces the full family to two complex candidates, and rejects both with a
three-term coefficient functional. Denominator degree seven and higher
remain open; neither instance is solved.
[Mixed argument, packets, figures, and failures](notes/mixed-degree6-extra.md),
[cyclic degree-six obstruction](notes/fresh-instance-degree6.md),
[preceding degree-five bounds](notes/fresh-instance-baselines.md).
Further holdout discussion posts remain paused.

![Three coefficients exclude the two remaining mixed-biweight candidates](results/mixed-degree6-extra-figures/mixed-extra-field.png)

**Holdout checkpoint: degree seven.** Our exact **{chi_X0, chi_Y0}** exclusion, our earlier **{chi_Y0, chi_X1}** result, and fqlx's reproduced **{chi_X1, chi_Y1}** proof complete **9,453 of 9,453 two-character families** in the preceding scan. Denominators with three or more characters and higher degrees remain open. [Combined coverage, attribution, and checks](notes/x0-y0-exclusion.md).

**Latest holdout result:** the rebuilt T100 multiplier search forces all five
Y1 coefficients to vanish and makes both added-character charts contradictory.
The separately replayed anchor dependency then closes the family. This
completes **132 of 132** fresh X0/Y1 triples and brings the selected union to
**812 triples**. Exact ranks agree modulo three primes, but all proof witnesses
are rational; this is finite-field screening, not p-adic Hodge theory. The five
failed rebuilt charts and unsupported BB/KZ/KPZ and VC-complexity suggestions
remain visible. [Proof, visualization, checks, and limits](notes/t100-rebuilt-exclusion.md).

![T100 rebuilt multiplier exclusion](results/typed-rewrite-families/t100-rebuilt-multipliers/t100-rebuilt.png)

**Preceding exact result:** 131 of 132 fresh X0/Y1 three-character families
were excluded, bringing the selected union to 811 triples at that checkpoint.
T100 remained open after a separate exact reduction from thirteen to twelve
directions. A frozen typed-cache comparison was slower than the existing
method; target-character projection nevertheless gave smaller exact power
queries. [Results, figures, and limits](notes/typed-rewrite-search.md).

![Exact type decomposition of the coefficient operator](results/typed-rewrite-families/typed-operator.png)

**Preceding exact result:** an exact search guided by the added character's
Koszul homology and a separate multiplier continuation exclude all
**132 fresh X0/X1 extensions**, bringing the selected union to **680 triples**.
The earlier 131/132 checkpoint and A100's failed charts are preserved.
High-score and low-score groups both close 4/4. The figures
separate empty blocks from computed zero homology and compare H1 with H0,
which directly detects full graded images. Both physical reconstructions
pass; failed charts and the reproduced full-pair dependency are retained.
[Results, visualizations, and limits](notes/added-character-homology.md).

![Added-character Koszul maps and the H0 comparison](results/added-character-homology/added-character-koszul-map.png)

**Preceding exact result:** 132 additional complete three-character families
around `Y0/Y1` are excluded, bringing the selected union to **548 triples**.
Koszul homology guided a prospective comparison, but high- and low-score
groups both closed 4/4; no ranking advantage was established. All seven
later continuations closed too. Both physical polynomial implementations
pass. The record keeps the unsuccessful charts, an explicit pair-dependency
correction, actual Koszul-map figures, and the rebuild history.
[Proofs, homology experiment, visualizations, and failed attempts](notes/homology-guided-triples.md).

![Homology-guided search and its control](results/homology-guided-triples/homology-guided-triples.png)

**Preceding exact result:** another 132 complete three-character families around
`Y0/X1` are excluded, bringing our selected union to **416 triples**.
Small-block reductions close 123; shared equations and rebuilding close
eight more. The last family needs 39 additional cubic consequences,
quartic power identities, and a further rebuild. Both physical polynomial
implementations pass the exact chain. This completes all 136 third-character
extensions of Y0/X1; holdout remains unsolved.
[Proof, visual record, and unsuccessful attempts](notes/y0x1-extensions.md).

![Y0/X1 extension exclusions and rebuilding](results/y0x1-extensions/y0x1-extensions.png)

**What do the curved matrix bands mean?** Compare old X1/Y1 cases 19, 49,
and 100 in [original, factor-adapted, and reordered bases](notes/graded-map-patterns.md),
with alternative sign palettes and relative coefficient strength. Exact
ranks survive; apparent curves depend on ordering. The record includes the
rejected first factorization for case 100 and its checked correction.

**From the matrix to a complex:** the [Koszul homology companion](notes/categorical-syzygies.md)
separates relations from boundaries in degrees two through six. At degree
four, B19 has six relations, three Koszul boundaries, and three remaining
homology classes. Thirty exact complexes pass checks in both bases. This
also clarifies the distinct roles of Yang, Eisenbud-Erman, and Riehl; it
does not assert a geometric cohomology identification or a new exclusion.

**Preceding exact result:** 132 further three-character families around the
`X1/Y1` pair are excluded, bringing our selected union to **284 triples**.
Necessary block reductions close 123; full shared-numerator charts and
rebuilding finish the remaining nine. Both physical polynomial
implementations replay the proofs, including the explicitly reproduced
fqlx pair-30 dependency. This completes all 136 third-character extensions
of X1/Y1, with four already covered previously. Other triples among the
428,536 possible supports, larger supports, and higher degrees remain open.
[Proofs, graded-map visualization, and failed searches](notes/x1y1-extensions.md).

![New triple exclusions and the nine rebuilt families](results/x1y1-extensions/x1y1-extensions.png)

The [preceding polynomial-multiplier result](notes/family151-multipliers.md)
closed family 151, completing the original 152 selected triples. Its full
Linux workflow subsequently passed all eight jobs.

The [preceding shared-numerator batch](notes/remaining-triples-shared.md)
closed family 17 and supplied the linear constraint used to rebuild 151,
giving 151/152 at that checkpoint.

The [eleven-family quartic batch](notes/eleven-quartic.md) closed families
1, 2, 4, 5, 7, 9, 15, 39, and 150, giving 150/152 at that checkpoint.

The [preceding degree-four batch](notes/eisenbud-quartic-strand.md) closed
families 6, 8, 10, 149, and 152, giving 141/152 at that checkpoint.

**Earlier parameter optimization:** two L-BFGS-B starts in each of the 16
then-remaining selected triple spans beat an equal-evaluation uniform-random comparator on
the numerical score (median reduction 91.9%). All 32 rounded finalists fail
exact checks; ten optimized winners round into previously excluded one- or
two-character sectors. [Search history, visualization, checks, and limits](notes/koszul-parameter-optimization.md).

**Explore those searches:** the [interactive trajectory view](visualizations/koszul-search-standalone.html)
links the residual history to the denominator's three character shares. Select
a family and move through its recorded evaluations to see boundary drift.
Download the HTML and open it in a browser; GitHub's file viewer shows source.
This presents the existing experiment, with all failed finalists retained.

**Original systematic three-character batch:** of all 136 extensions of the `X0/Y0` pair by a third character, **132 complete families were excluded and four remained unresolved at that checkpoint**. Including all coordinate-character triples gave 152 tested families and 20 unresolved. Exact duals and shared-numerator chart proofs are replayed by two polynomial constructions. [Coverage, failed charts, and reproducible proofs](notes/three-character-families.md).

**First polynomial-syzygy follow-up:** one of those four residual families was
excluded, giving **133/136 fixed-pair extensions excluded** (133/152 in the
combined selection). Affine polynomial multipliers preserve shared numerator
coefficients and yield new denominator constraints. Three cubic identities
then close family 87; two charts of family 115 gain constraints but remain
open. [Short proof, literature motivation, and failed attempts](notes/polynomial-syzygies.md).

**Rebuilt-syzygy continuation:** family 115 is now excluded as well, giving
**134/136 fixed-pair extensions excluded** (134/152 in the combined selection).
Rebuilding after the verified zeros and searching through total degree five
closes one chart; its forced zero closes the other. The two larger families
remained unresolved at that checkpoint, with checked conditional progress and ten timed-out
searches retained. [Proof, visualization, and failed attempts](notes/syzygy-rebuild.md).

**Earlier Koszul continuation:** families 16 and 137 are now excluded, completing
**136/136 fixed-pair extensions** (136/152 in the original combined selection).
Two-row square identities force global linear vanishings; rebuilding the
Koszul correction equations then closes all ten third-component charts.
Sixteen other selected triples remained open at that checkpoint. [Exact proof, dependencies,
and retained failed searches](notes/koszul-rank-continuation.md).

**Eisenbud follow-up:** degree-three maps of the necessary ideals force
eleven family-specific coordinate zeros in five of those sixteen triples.
All sixteen remained unresolved at that checkpoint. The [calculation and cancellation explorer](notes/eisenbud-linear-strand.md)
show the actual polynomial identities, 1,149 checked relation vectors, and
where the bounded search fails. Every substantive research batch now includes
a reproducible internal visualization and a ledger entry.

![Linear syzygies, forced zeros, and unsuccessful families](results/eisenbud-linear-strand/linear-strand.png)

**See the correction map:** [three views of post six](notes/koszul-map-visualizations.md)
show its actual polynomial support, the syzygies cancelling corrections, and
the chart dependencies. The two-row example explains how a weighted numerical
score can improve while the exact obstruction stays nonzero.

**A geometric operator view:** [move a circle through the Koszul correction
map](notes/koszul-geometric-map.md). Three actual denominators give response
ellipses, while their exact syzygies keep the target off the image plane.
The interactive version links correction coefficients to their image and
lets you fit the projected target, rotate the view, and compare the examples.

**Now vary the denominator:** an [interactive two-parameter sweep](notes/koszul-denominator-sweep.md)
shows exact full-map ranks of 720, 713, and 690 at 81 rational samples. One
projection also collapses where the full rank stays unchanged. A common exact
syzygy rejects the entire restricted slice. Six additional searches constrained
to retain three characters produce six new exact rejections; all reach their
iteration limit. These finite rank changes do not establish a statistical
phase transition or solve holdout.

![Denominator parameters, exact ranks, and the persistent obstruction](results/koszul-map-sweep/rank-sweep.png)

![Response ellipses and their exact target obstructions](results/koszul-geometry/operator-geometry.png)

![Koszul correction-map support and cancelling syzygies](results/degree7-rank-strata/koszul-map-support.png)

![How syzygies close family 115](results/degree7-syzygy-rebuild/syzygy-proof-map.png)

![Coverage of all X0/Y0 three-character extensions](results/degree7-triples/character-atlas.png)

**Dubedat-inspired construction:** a weighted six-cycle matrix generates degree-seven determinants and exact first-equation lifts. All **45** tested directions fail the full second equation, including 30 with seven or eight characters. [Construction and exact witnesses](notes/dubedat-cycles.md).

**Imaginary geometry gallery:** the same GPU-generated Gaussian input under different flow angles and directional conductances. These are regularized illustrations. [Equations, images, and checks](notes/imaginary-geometry-gallery.md).

**Hodge projection search:** 600 new three-character degree-seven candidates outside the Jacobian ideal; all 34 shortlisted/control directions fail exact checks with the full 840-dimensional correction space. [The coefficient heat flow and its obstruction](notes/hodge-projected-search.md).

**48-handle continuation:** paired GPU fields, rotated harmonic directions, and a measured phase-coherence crossover. No phase transition found in this finite Gaussian model; the crossover scale depends on smoothing. [Images, equations, and failed long-flow approximation](notes/high-genus-flow.md).

![One genus-48 field at three stiffnesses](results/high-genus-flow/stiffness-triptych.png)

![One field, three directions](results/imaginary-geometry/angle-triptych.png)

**Attribution update:** fqlx had already published the 138 single-character exclusions before our preceding commit. Our separately implemented calculation checks that result; it is not a first report of the bound. [Single-character calculation and chronology](notes/degree-seven.md).

![Exact degree-seven symmetry-family exclusions](results/degree7-characters/character-map.png)

**Earlier ranking benchmark:** five pools of 768 degree-six candidates gave about a 32% lower normalized E2 residual for Gram-ranked shortlists than random selection. Anisotropic and uniform weighting were essentially tied; all 254 distinct shortlisted directions failed exact checks. The upstream degree-six exclusion had not yet been incorporated into that experiment. [Method and corrected frontier context](notes/denominator-ranking.md).

![Denominator Gram ranking compared with exact algebra](results/denominator-gram/denominator-ranking.png)

![Paired Hodge response operators](results/response-hodge/response-hodge.png)

The unifying construction is [curvature-mediated response duality](notes/response-duality.md): coefficient changes produce spatial forces, inverse curvature turns them into displacement, and the pulled-back form is `Q=L* K^-1 L`. Its factorization defines a two-term Hodge complex. The holdout's eight coefficients give a concrete numerical example; its thermal Gram approaches the predicted rank-one limit to about 0.070% in the recorded low-temperature run.

![An anisotropic flow derived from the holdout sextic](results/anisotropic-flow/anisotropic-flow.png)

The flow experiment uses the holdout polynomial's directional variation to construct an elliptic surface energy, then evolves eight planar curves toward area-matched Wulff shapes. This is a chosen interpretation of the polynomial inspired by [Kim–Kwon, arXiv:2405.08296](https://arxiv.org/abs/2405.08296v1). [Construction, equations, and scope](notes/anisotropy.md).

## What is here

| Experiment | Recorded result | Evidence |
|---|---|---|
| Standard parameter optimization | 16 bounded triple spans; 2,078 evaluations per strategy; 32 exact rejections, no new family exclusion | [Methods, comparison, and failures](notes/koszul-parameter-optimization.md) |
| Koszul-map visual companion | 173 displayed cancellation identities replayed; exact two-row obstruction and weighting diagnostic | [Three figures, interpretation, and checks](notes/koszul-map-visualizations.md) |
| Koszul continuation after local rank identities | Families 16 and 137 excluded; 136/136 fixed-pair extensions covered; 16 other selected triples still open | [Exact chart covers and failed searches](notes/koszul-rank-continuation.md) |
| Rebuilt polynomial syzygies | Family 115 excluded; 134/136 fixed-pair extensions covered; two remain unresolved | [Exact proof, dependencies, and visualization](notes/syzygy-rebuild.md) |
| Polynomial syzygies of the shared correction map | One further complete family excluded; 133/136 X0/Y0 extensions now excluded; two next-family charts still unresolved | [Exact identities, literature, and failures](notes/polynomial-syzygies.md) |
| Original systematic three-character batch | 152 complete families tested; 132 excluded at that checkpoint; all 136 X0/Y0 extensions included | [Exact duals, shared charts, and coverage map](notes/three-character-families.md) |
| Hodge correction projection | 600 three-character directions screened; 34 fixed directions exactly rejected | [Heat flow and complete correction map](notes/hodge-projected-search.md) |
| Genus-48 Gaussian phase response | Three paired weightings, 256 samples each; broad analytic crossover and strong smoothing dependence | [High-genus gallery and limits](notes/high-genus-flow.md) |
| Imaginary geometry gallery | CUDA GFF transforms and flow textures; paired angle and directional-weight comparisons | [Gallery and model](notes/imaginary-geometry-gallery.md) |
| Dimer-inspired cycle determinants | 45 distinct directions pass E1; all fail E2 with all 840 corrections allowed | [Determinants, twists, and redundant edge weights](notes/dubedat-cycles.md) |
| Degree-seven {chi_X0, chi_Y0} family | Excluded by 25 exact chart identities; combined work covers all 9,453 two-character families | [Family-13 continuation and family-30 replay](notes/x0-y0-exclusion.md) |
| Degree-seven {chi_Y0, chi_X1} family | Excluded by an exact square of a linear form, chart contradictions, and the single-character theorem | [Two-character continuation](notes/degree-seven-pair.md) |
| Degree-seven character families | All 138 single-character families excluded with 289 exact chart certificates; mixed characters remain open | [Degree-seven frontier](notes/degree-seven.md) |
| Upstream degree-six exclusion | fqlx's full bound reproduced, including opposite-pivot verification | [Attributed replay](results/upstream-degree6/replay.json) |
| Denominator Gram rankings | 3,840 candidate draws; lower E2 residual than random, no anisotropy advantage; 254 distinct exact rejections | [Ranking experiment](notes/denominator-ranking.md) |
| Coefficient response and Hodge complex | Envelope derivatives, Gram factorization, paired modes, and thermal localization checked | [Response report](results/response-hodge/report.json) |
| Competing Gram models | Six Gaussian comparisons using a product-TV proxy and independent likelihood sampling | [Interpretation and results](notes/gram-discrimination.md) |
| Actual holdout, degree-six denominators | 120 fixed denominator directions tested with all 315 numerator corrections | [Exact search and dual certificates](algebra/README.md) |
| Accepted-witness transfer | 36 controls pass; all 582 transfers fail, including common scalar repairs | [CPU-replayable packet](results/leaderboard-experiments/report.json) |
| Holdout period coefficients | Seven failures of the naive cubic divisibility benchmark among the tested cases with primes at least five | [Exact arithmetic](results/period-congruence/report.json) |
| HodgeRank vs Kemeny | 216 of 2,600 three-ballot profiles have strict Hodge scores but a suboptimal induced ranking | [Source bridge report](results/source-bridges/report.json) |
| Cube Gaussian field | 2,048 samples on 1,024 vertices checked against the exact Walsh spectrum | [Source bridge report](results/source-bridges/report.json) |
| Ginibre loop | Discriminant winding −11, stable through five sampling resolutions | [Source bridge report](results/source-bridges/report.json) |
| Fractional fields and triangulations | Three independently checked four-colorings of triangulated spheres | [Saved fields and meshes](results/source-bridges/fractional-field-meshes.npz) |

The anisotropic flow uses the actual `F` but does not encode the target `q,A`. Pictures, numerical convergence, and a rejected family of candidates do not establish an algebraic certificate.

## Reproduce

Python 3.11 and Git are required. Clone the pinned source repositories:

```sh
git clone --recurse-submodules https://github.com/rbajaj5/hodge-lab.git
cd hodge-lab
python -m venv .venv
# Activate the environment using your shell's usual command.
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python experiments/check_transfer_packet.py
python algebra/degree6_verify_all_coefficients.py
python algebra/fixed_denominator_search.py --check
python experiments/denominator_gram_search.py --check
python algebra/degree7_e1.py --check
python algebra/degree7_verify_polynomials.py
python algebra/degree7_character_search.py --check
python algebra/degree7_y0_x1.py --check
python -S algebra/degree7_x0_y0.py --check
python -S experiments/dubedat_cycle_search.py --check
python -S experiments/hodge_projected_search.py --check
python -S experiments/check_hodge_projected_search.py
python experiments/check_high_genus_flow.py
python -S algebra/degree7_triples.py --check
python -S algebra/check_degree7_triples.py
python -S algebra/degree7_triple_shared.py --check
python -S algebra/degree7_triple_shared.py --check --independent
python -S algebra/degree7_rank_strata.py --check-all
python -S algebra/degree7_rank_strata.py --check-all --independent
python -S algebra/degree7_koszul_continuation.py
python -S algebra/degree7_koszul_continuation.py --independent
python experiments/plot_koszul_continuation.py --check
python -S experiments/optimize_koszul_parameters.py --check
python experiments/optimize_koszul_parameters.py --check --independent --numerics
python experiments/plot_parameter_optimization.py --check
```

These checks run on a CPU. They use exact rational arithmetic for algebraic certificates; floating-point tolerances are confined to numerical experiments. Do not run verification scripts with Python's `-O` option.

Source-text hashes normalize CRLF line endings to LF so that Windows and Unix clones verify the same inputs. The compressed algebra tensor and E1 basis use their stored bytes without normalization.

To regenerate experiments and figures:

```sh
python experiments/period_congruence_probe.py
python algebra/fixed_denominator_search.py
python experiments/plot_source_bridges.py
python experiments/anisotropic_flow.py --cpu
python experiments/response_hodge.py --cpu
python experiments/gram_discrimination.py --cpu
python experiments/denominator_gram_search.py --cpu
python -S experiments/dubedat_cycle_search.py --workers 3
python experiments/plot_dubedat_cycles.py
python experiments/hodge_projected_search.py
python experiments/plot_hodge_search.py
python experiments/plot_koszul_continuation.py
```

For an NVIDIA GPU with a compatible CUDA 12 environment:

```sh
python -m pip install -r requirements-cuda.txt
python experiments/source_bridge_lab.py
python experiments/anisotropic_flow.py
python experiments/response_hodge.py
python experiments/gram_discrimination.py
python experiments/denominator_gram_search.py
python experiments/gpu_identity_screen.py
python experiments/imaginary_geometry_gallery.py
python experiments/high_genus_flow.py
python experiments/render_high_genus_flow.py
```

The recorded GPU was an RTX 5070 Ti Laptop GPU, using CuPy 13.6.0. Gaussian noise is seeded on the CPU; GPU/CPU responsibilities are recorded in each report. `HODGE_CUDA_DEPS` can point to an existing isolated dependency directory; it is optional. Regeneration overwrites the corresponding result files; review the diff before committing a new run. Floating-point output may vary slightly by platform.

`python experiments/leaderboard_experiments.py` additionally requires GitHub CLI access and network access. It checks the live upstream commit against the pinned checkout and intentionally stops if they differ. The saved CPU replay needs neither a GPU nor network access.

## Gallery

![Ginibre eigenvalue strands](results/source-bridges/ginibre-braid.png)

![Fractional Gaussian fields and checked colorings](results/source-bridges/fractional-fields-and-colors.png)

![Exact period coefficient divisibility](results/source-bridges/period-divisibility.png)

## The leaderboard

The snapshot of 16 October 2026 contains 61 entries: 42 solved and 19 open, with 42 credited to `benediamond`. These are historical counts, not a live dashboard. The upstream [contribution contract](https://github.com/hodge-computer/sextics/blob/b8c4edeb80a82395ec07164caf445cfa43bbbd56/CONTRIBUTING.md) requires an accepted proof for the fixed target. A public experiment or picture does not earn a solve point.

See [source attribution](SOURCES.md), [research notes](RESEARCH_LOG.md), and the [degree-six holdout model](algebra/README.md). Source submodules retain their own authorship and licensing. This repository does not post or submit anything to the challenge automatically.

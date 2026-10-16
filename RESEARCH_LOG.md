# Research log — 16 October 2026

The purpose is to make small computational connections and test them against explicit targets. Results below include failed approaches.

The [research milestones](notes/research-milestones.md) separate candidate ranking, exact exclusions, implementation checks, and external review. They give failed approaches and corrected claims an explicit role in deciding what to try next.

## One residual two-character family closed

Reading the full discussion, including replies, revealed fqlx's 21:00:49 UTC degree-seven update. It already contained the 138 single-character exclusions and went further: 9,450 of 9,453 two-character families were excluded, with three remaining. Our preceding single-character commit is therefore a separate check of an already reported result, not the first report. The pinned upstream package was reproduced, including all pair and subgroup checks; a Windows log-encoding failure in the final tangent phase was resolved by rerunning that phase in UTF-8 mode.

Our [continuation](notes/degree-seven-pair.md) closes the `{chi_Y0,chi_X1}` family. Starting with its full 14-coordinate denominator space and 60 shared numerator corrections, a six-term coefficient identity forces the square of a linear form to vanish. Subsequent exact chart contradictions eliminate the entire `chi_Y0` component, reducing to the already excluded `chi_X1` family. The checker reconstructs all 945 physical columns with a second polynomial API, checks 18,253 coefficients and 196 proof inferences, and rejects an altered witness. Two two-character families, more general mixtures, and higher degrees remain open. No Lean `HasCertificate` proof has been obtained.

## Frontier correction and degree-seven exclusions

At approximately 20:47 UTC, a refreshed read of Discussion 44 revealed fqlx's 19:58 UTC update excluding every denominator of degree at most six. That update had not been incorporated into the earlier Gram-ranking run. We reproduced the pinned source package and its opposite-pivot audit, verifying all 26 source hashes. The degree-six bound is fqlx's result.

The [degree-seven calculation](notes/degree-seven.md) independently reproduces the complete 295-dimensional E1 denominator space, its six `F S1` gauge directions, and the 840-dimensional numerator kernel. The retained 289-dimensional denominator space splits into 138 diagonal-character families. Full E2 with the complete character-projected numerator space excludes 262 charts by affine/square-zero consequences and the remaining 27 by explicit cubic ideal identities. Every one of the 138 families is therefore excluded. This does not exclude mixed-character denominators at degree seven.

A second polynomial implementation rebuilt all 2,294 E2 columns and 25,201 coefficients, checked all 295 E1 lifts, and verified 1,770 degree-seven gauge identities. Independent proof replay checks 460 inferences and rejects altered witnesses. All exact calculations use rational arithmetic; no Lean existence theorem or solved holdout is claimed.

## Denominator Gram ranking

The [denominator ranking experiment](notes/denominator-ranking.md) constructs Grams on the actual 108-coordinate denominator basis, using 24 random plane restrictions of the fixed holdout. Five independent candidate pools contain 3,840 draws with two or four nonzero coordinates. Each geometric selector freezes 16 picks before the complete E2 least-squares evaluation.

Mean residuals were 0.31257 (anisotropic), 0.31222 (uniform), and 0.45896 (random expectation from repeated balanced shortlists). Both Grams improve this normalized coefficient residual by about 32%; the extra anisotropic weighting provides no aggregate gain. The relative residual after corrections is about 0.93 for both anisotropic and random picks, so the gain mainly reflects smaller initial obstructions. An algebra reference that sees all E2 fits achieves 0.23946. All 254 distinct shortlisted directions fail exact rational dual checks, including the best numerical candidate, which has a three-coefficient obstruction. No solution is claimed.

The primary result was followed by four fresh candidate seeds with no changes to the ranking rule or geometric matrices. All results, seeds, matrices, candidates, and exact witnesses are public. CPU checks independently compare numerical contraction with exact coefficients and sparse fitting with dense factorization, then replay the certificates with corruption controls.

## Exact holdout work

The degree-six E1 parameterization reproduces prior results by fqlx, with source attribution in `algebra/README.md`. The full E2 coefficient tensor is independently reconstructed. The fixed-denominator search allows every degree-six numerator correction and exports exact rational dual certificates for unsuccessful choices. It does not search all denominator combinations or all degrees.

The GPU transfer screen reuses 36 accepted rational witnesses on 582 eligible open targets with matching pole order. All controls pass. Every direct transfer fails, and every common scalar repair of `N,Q` fails. A separate CPU evaluator replays the two-point rejection certificates and verifies 182 input hashes; an intentionally changed certificate is rejected. No new witness was found.

## Arithmetic suggested by the supercongruence repository

For `M=X0 X1 X2 Y0 Y1 Y2`, write `C(m)=CT(F/M)^(6m)`. An explicit multinomial formula is checked by independent repeated polynomial multiplication, including terms in which the couplings contribute.

The 24 exact adjacent-scale comparisons include seven failures of a naive `p^(3r)` divisibility benchmark for primes at least five. In particular `v_7(C(49)-C(7))=4`, below six, with residue 7203 modulo `7^6`. This disproves that naive extension, not a theorem asserted by the source repository. These coefficients describe a torus period expansion of the pencil `M-tF=0` near `t=0`. The holdout `F=0` is at `t=infinity`; endpoint continuation and a certificate for `A` were not computed.

## HodgeRank and finite combinatorics

All 2,600 multisets of three rankings of four labeled candidates were checked. Exact integer identities verify the gradient/cyclic decomposition. In 216 cases the Hodge scores are all distinct but their sorted order is not Kemeny optimal. Example: ballots `ABCD, ABCD, BCDA` give Hodge order `BACD` with cost four and Kemeny order `ABCD` with cost three. This uses HodgeRank, following [Jiang–Lim–Yao–Ye](https://arxiv.org/abs/0811.1067), rather than the algebraic Hodge conjecture.

## Random geometry

The Boolean-cube field has precision eigenvalues `2|S|+0.5`, using the unnormalized graph Laplacian and counting measure. Its Walsh transform is checked against a CPU implementation and exact spectral identities. This normalization differs from the normalized refresh operator in the hypercube notes.

The matrix loop has Ginibre marginals at each time and a smooth periodic dependence on time. It is not Brownian motion or an Ornstein–Uhlenbeck process. Sampling refinements from 1,024 through 16,384 steps give the same discriminant winding −11 and endpoint permutation. The final sampled gap/step diagnostic passes; early resolutions do not. No interval-certified noncollision statement or complete braid classification follows. BetGuard conditioning detects a negative control with zero residual and badly conditioned eigenvectors.

The source braid fixture `sigma1^2 sigma2^2` versus `sigma2^2 sigma1^2` has the same pairwise windings and different Burau matrices. This existing fixture illustrates information lost by abelianization. It is credited as reuse, not a discovery.

Three cutoff fractional fields use a shared Gaussian noise sample. Unlike the original sampler, we omit per-sample variance normalization to retain a Gaussian law. Curvature signs choose grid diagonals; the source coloring routine produces verified proper colorings. Capping the boundary creates a sphere: surface `b1=0`, although its graph has cycle rank 575. Graph cycles are not surface harmonic one-forms. These are finite models, not a simulation of continuum SLE or a proof in imaginary geometry. [Miller–Sheffield](https://arxiv.org/abs/1201.1496) provides the precise continuum setting.

## Anisotropic flow

The user-suggested [Kim–Kwon paper](https://arxiv.org/abs/2405.08296v1) motivates the implemented convex curve-flow experiment. A seeded plane restriction of the actual holdout sextic supplies its angular energy. Area, convexity, perimeter, refinement, and CPU/GPU agreement are measured. The [anisotropy note](notes/anisotropy.md) distinguishes this implemented probe from proposed weighted Hodge/GFF experiments and from the exact algebraic certificate target.

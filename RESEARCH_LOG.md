# Research log — 16 October 2026

The purpose is to make small computational connections and test them against explicit targets. Results below include failed approaches.

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

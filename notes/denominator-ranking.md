# Can geometric Gram matrices rank denominator candidates?

**Frontier update:** a later review of [fqlx's upstream update](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18982028) established that all degree-six denominators were already excluded by an exact argument. We reproduced that bound. This experiment remains a numerical benchmark on an excluded degree; the active work has moved to [degree seven](degree-seven.md). The upstream update was posted before this experiment ran but had not been incorporated into it.

**They improve the chosen numerical residual in this experiment. The anisotropic weighting adds no clear benefit over uniform weighting, and no exact solution was found.** Five pools of 768 rational candidates gave a mean shortlisted E2 residual of **0.31257** for the anisotropic Gram and **0.31222** for the uniform Gram, against a random-selection expectation of **0.45896**. That is about a **32% reduction** for either geometric ranking. All **254 distinct shortlisted directions** were rejected by exact rational certificates.

![Denominator rankings and exact checks](../results/denominator-gram/denominator-ranking.png)

## From eight sextic coefficients to 108 denominator coordinates

The earlier [response Gram](response-duality.md) acts on changes to the eight coefficients of `F`. It cannot directly rank the 108 denominator coordinates in the [degree-six E1 parameterization](../algebra/README.md). We instead use the actual denominator polynomials as features.

Let `D_i` be the 108 retained basis polynomials. Remove each polynomial's coefficient-orthogonal projection onto `F`, obtaining `Dbar_i`. This chooses a representative of the established `D -> D+cF` gauge. On each of 24 seeded random projective circles, evaluate these features at 128 angles. Set

```text
H(theta) = F(U(cos(theta), sin(theta))),
T = 0.2 * (max H - min H),
p(theta) proportional to exp(H(theta)/T),
G = average_over_planes Cov_p(Dbar_i, Dbar_j) / T.
```

For each plane, `T` is held fixed when interpreting this covariance as the Hessian of the temperature-scaled log partition function `T log Z` for perturbations `F + sum_i u_i Dbar_i`. The temperature choice is a declared heuristic. The uniform control replaces `p` by uniform angular weights, keeping the same planes, features, and temperatures. A second set of 24 planes diagnoses geometric ranking stability; it does not tune the ranking.

For `D = sum_i a_i D_i`, the score is

```text
score(D) = a^T G a / ||sum_i a_i Dbar_i||_coeff^2.
```

Lower scores prefer denominators whose values vary less under these probes, at fixed polynomial size. This is a hypothesis about useful candidates, not a necessary condition for a certificate. No Gram inverse or spectral cutoff is needed.

## Pools and the independent algebraic metric

Each pool contains 384 candidates with two nonzero basis coordinates and 384 with four. Integer weights from `{-3,-2,-1,1,2,3}` are divided by the exact L1 coefficient height of their basis polynomial, then projectively normalized. This accounts for the different scales of the stored basis columns. The sampler uses an 88-coordinate slice, omitting the 20 indices listed in the report, informed by previous individual-square reductions. This experiment does not require a completeness claim for that slice: every exact candidate check uses the full 108-coordinate tensor and all 315 numerator corrections.

Each method selects eight candidates from each support-size stratum. The anisotropic, uniform, and seeded random selections are frozen before computing any E2 residual. Evaluation uses

```text
R(a) = min_z ||b(a) + M(a) z||_2,
        with ||sum_i a_i Dbar_i||_coeff = 1.
```

Here `b+Mz` is the complete normalized E2 remainder modulo `F`, in its fixed monomial basis. All 315 corrections are allowed. This is a coordinate-dependent numerical surrogate, not distance to the algebraic solution set. Normalization prevents shrinking the denominator to zero. An **algebra reference** selects the smallest residuals after inspecting every fit; it has more information than the geometric selectors.

The primary seed is `202610170108`. After observing its result, four further pools were run with seeds `202610170208` through `202610170211`. Their Gram matrices, temperature, candidate recipe, and selection rule were unchanged. All replications are reported; this was not a preregistered significance test.

| Pool | Anisotropic | Uniform | One random shortlist | Algebra reference |
|---|---:|---:|---:|---:|
| Primary | 0.306679 | 0.314940 | 0.499314 | 0.228953 |
| Fresh 1 | 0.314803 | 0.307841 | 0.387586 | 0.238618 |
| Fresh 2 | 0.307591 | 0.310835 | 0.380245 | 0.242092 |
| Fresh 3 | 0.300337 | 0.300590 | 0.416662 | 0.242819 |
| Fresh 4 | 0.333437 | 0.326874 | 0.499552 | 0.244826 |
| Mean | **0.312569** | **0.312216** | **0.436672** | **0.239462** |

The separate random expectation, **0.458961**, averages 2,000 balanced random shortlists within each pool. The plot's bands show the central 90% of those shortlist means, not confidence intervals for a population of algebraic problems.

The relative residual `||b+Mz|| / ||b||` is about **0.930** for anisotropic picks, **0.926** for uniform picks, and **0.932** for random picks. Most improvement in the unit-denominator residual therefore comes from selecting a smaller initial obstruction, rather than a markedly better fraction canceled by corrections. The extra anisotropic weighting was about 0.1% worse than uniform on the aggregate metric. This supports the geometric ranking heuristic in these sparse pools, not an anisotropy advantage or a higher exact success rate.

## Exact rejection of the best numerical candidate

The lowest residual among all draws was about **0.190345**, for candidate 272 in seed `202610170209`:

```text
D = D_28 + (7/6) D_62
  = (1/6) X0^4 X1 Y1 + X0 Y0^5
    + (7/3) X0^3 X2 Y0^2 + (7/6) X1 X2 Y0^3 Y1.
```

Write `[m]P` for the coefficient of monomial `m` in the canonical remainder of `P` modulo `F`. The exact checker found

```text
L(P) = -[X0^5 X1^6 Y0]P
       + 3 [X0^5 X1^3 X2 Y0 Y1 Y2]P
       - 12 [X0^5 X1^2 Y0^3 Y1^2]P.
```

For this fixed `D` and its stored E1 lift, **`L(b)=1` and `L(M_k)=0` for every one of the 315 correction columns**. Consequently `L(b+Mz)=1` for every complex `z`: this candidate cannot satisfy E2. The report contains witnesses for all 254 distinct shortlisted directions (255 check records because one direction recurs across pools). Every functional also supplies a positive residual lower bound by Cauchy–Schwarz; its floating evaluation is recorded separately from the exact identity.

## Reproduction and checks

```sh
python experiments/denominator_gram_search.py --check
python -m unittest discover -s tests -v
# Regenerate using the GPU, or add --cpu:
python experiments/denominator_gram_search.py
```

The recorded RTX 5070 Ti Laptop GPU run used the GPU for covariance and quadratic-score reductions. Polynomial feature evaluation, sparse least squares, and rational certificates ran on the CPU. Computation through certificate generation took about 70 seconds; plotting and independent replay followed. First-plane CPU/GPU covariance discrepancy was about `2.2e-16`. The largest normalized normal-equation residual in the fits was about `2.9e-11`.

Tests compare covariance with scalar weighted variance, floating contraction with exact rational specialization, sparse least squares with an independent dense rank-revealing factorization, and saved Gram scores with direct contractions. CPU replay checks hashes, seeded pools, selections, all exact witnesses, and deliberately corrupted witnesses. Existing independent reconstruction still validates the entire E2 tensor.

The [report](../results/denominator-gram/report.json) contains every draw and score. [Saved matrices](../results/denominator-gram/grams.npz) contain both Grams, their fresh-plane counterparts, and the denominator coefficient map. [The experiment](../experiments/denominator_gram_search.py) generates the data and figure. Upstream E1 attribution remains in the [algebra notes](../algebra/README.md).

For subsequent searches in an unresolved degree, a denominator Gram can provide an inexpensive ordering heuristic while retaining algebraic checks. Uniform weighting is the simpler default supported by this comparison. This finite experiment did not itself exclude all degree-six denominators; the separately attributed upstream argument now does. The current search concerns degree seven and above.

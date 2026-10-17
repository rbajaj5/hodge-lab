# Hodge lab

A public lab notebook for [hodge.computer](https://hodge.computer/). We test geometric ideas for making better guesses at algebra problems, then check those guesses exactly. The code, pictures, results, and failed approaches stay visible.

This is the **meta-repository for our work in [hodge-computer/sextics](https://github.com/hodge-computer/sextics)**: it records the motivation for our approaches, supporting experiments, and the purpose and outcome of each public contribution. The [contribution ledger](LEDGER.md) links to the actual upstream posts and submissions.

**Current status: no new accepted Hodge solve.** The repository contains actual GPU runs, exact rejection certificates, independent checks, and the approaches that failed. Code and notes were developed with AI assistance; the recorded checks describe what was executed.

**How we judge progress:** a useful exclusion, a simpler baseline that performs equally well, and a corrected claim all count as results. Numerical ranking, exact certificates, and external review are separate milestones. [Evidence standards and next experiments](notes/research-milestones.md).

**Current search: degree seven.** Our exact **{chi_X0, chi_Y0}** exclusion, our earlier **{chi_Y0, chi_X1}** result, and fqlx's reproduced **{chi_X1, chi_Y1}** proof complete **9,453 of 9,453 two-character families** in the preceding scan. Denominators with three or more characters and higher degrees remain open. [Combined coverage, attribution, and checks](notes/x0-y0-exclusion.md).

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

**Latest Koszul continuation:** families 16 and 137 are now excluded, completing
**136/136 fixed-pair extensions** (136/152 in the original combined selection).
Two-row square identities force global linear vanishings; rebuilding the
Koszul correction equations then closes all ten third-component charts.
Sixteen other selected triples remain open. [Exact proof, dependencies,
and retained failed searches](notes/koszul-rank-continuation.md).

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

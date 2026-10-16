# Hodge lab

A public computational notebook for exploring [hodge.computer](https://hodge.computer/), exact polynomial certificates, and random geometry. It connects earlier experiments in rankings, braids, Gaussian fields, and arithmetic through small reproducible calculations.

**Current status: no new accepted Hodge solve.** The repository contains actual GPU runs, exact rejection certificates, independent checks, and the approaches that failed. Code and notes were developed with AI assistance; the recorded checks describe what was executed.

![Paired Hodge response operators](results/response-hodge/response-hodge.png)

The unifying construction is [curvature-mediated response duality](notes/response-duality.md): coefficient changes produce spatial forces, inverse curvature turns them into displacement, and the pulled-back form is `Q=L* K^-1 L`. Its factorization defines a two-term Hodge complex. The holdout's eight coefficients give a concrete numerical example; its thermal Gram approaches the predicted rank-one limit to about 0.070% in the recorded low-temperature run.

![An anisotropic flow derived from the holdout sextic](results/anisotropic-flow/anisotropic-flow.png)

The newest experiment uses the holdout polynomial's directional variation to construct an elliptic surface energy, then evolves eight planar curves toward area-matched Wulff shapes. This is a chosen interpretation of the polynomial inspired by [Kim–Kwon, arXiv:2405.08296](https://arxiv.org/abs/2405.08296v1). [Construction, equations, and scope](notes/anisotropy.md).

## What is here

| Experiment | Recorded result | Evidence |
|---|---|---|
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
```

For an NVIDIA GPU with a compatible CUDA 12 environment:

```sh
python -m pip install -r requirements-cuda.txt
python experiments/source_bridge_lab.py
python experiments/anisotropic_flow.py
python experiments/response_hodge.py
python experiments/gram_discrimination.py
python experiments/gpu_identity_screen.py
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

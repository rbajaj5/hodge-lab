# Hodge Lab

**Exact computation, geometric experiments, and a public research ledger.**

An independent research notebook by [Ravi Bajaj](https://github.com/rbajaj5), exploring the fixed polynomial-certificate problems in [hodge-computer/sextics](https://github.com/hodge-computer/sextics). It brings together candidate constructions, exact exclusions, visual explanations, formal checks, and the record of what each experiment established.

[Research ledger](LEDGER.md) · [Current feedback audit](notes/one-reflection-skew-feedback-audit.md) · [Visual idea atlas](notes/idea-atlas.md) · [Lean proofs](formal/README.md) · [Sources](SOURCES.md)

## Current frontier

**Snapshot: 21 October 2026.** The upstream catalogue at [`be8ec039`](https://github.com/hodge-computer/sextics/blob/be8ec0395eccbb0cc8b0a293e638396a3e486822/data/index.json) contains **78 targets: 64 solved and 14 open**.

| Target | Upstream status | Notebook entry point |
| --- | --- | --- |
| `one-reflection-skew` | **Open.** The feedback describes bounded obstructions and a remaining rational-primitive problem. | [Feedback, attribution, and verification limits](notes/one-reflection-skew-feedback-audit.md) · [Degree-seven calculations](notes/one-reflection-skew-degree7.md) |
| `cycle-three` | **Accepted existence proof**, credited to `hodgepodgeconjecture` in [PR165](https://github.com/hodge-computer/sextics/pull/165). | [Earlier bounded exclusions](notes/fresh-instance-degree6.md) · [Acceptance audit](LEDGER.md) |
| `mixed-biweight` | **Accepted existence proof**, credited to `fqlx` in [PR170](https://github.com/hodge-computer/sextics/pull/170), merged and published on 21 October. | [Bounded denominator calculation](notes/mixed-degree6-extra.md) |
| `cycle-q2` | **Open.** This is a separate higher-pole target; the accepted `cycle-three` proof does not settle it. | [Upstream problem and remaining obstruction](https://github.com/hodge-computer/sextics/blob/be8ec0395eccbb0cc8b0a293e638396a3e486822/data/cycle-q2/why.md) |

The two accepted existence proofs above do not provide an expanded polynomial witness or a numerical denominator-degree bound. Their acceptance is compatible with earlier bounded exclusions. [Mixed-biweight acceptance receipt](https://github.com/hodge-computer/sextics/blob/be8ec0395eccbb0cc8b0a293e638396a3e486822/data/mixed-biweight/acceptance.json).

Research notes retain the status at the time they were written. This dated table and the ledger record later developments.

## What the computations ask

For fixed polynomial data, seek a rational vector field satisfying the prescribed certificate identity. Clearing denominators produces exact polynomial conditions. A useful outcome can be a certificate, a proof that a specified family cannot work, or a failed experiment with enough evidence to guide the next search.

The [algebra notebook](algebra/README.md) develops the normalized `q=1` equations, complete correction spaces, and exact rejection witnesses. Each calculation specifies its target revision, denominator family, allowed corrections, and verification boundary.

## Selected results

### From a GPU screen to exact exclusions

[![GPU rank calculation and the exact correction-space bound for sixteen fixed cubic-direction candidates](results/cyclic-fano-cubic-polars-figures/cyclic-fano-cubic-gpu-shortcut.png)](notes/cyclic-fano-cubic-polars.md)

For sixteen fixed cubic-direction candidates, **25 exact relations bound the correction rank by 150**, while nonzero augmented minors establish rank at least **151** after adding the target. The recorded CUDA screen and independent CPU reconstruction agree.

These results exclude the sixteen fixed candidates. The full mixed 175-parameter denominator family remains open in this calculation.

[Derivation and scope](notes/cyclic-fano-cubic-polars.md) · [Recorded GPU run](results/cyclic-fano-cubic-gpu/report.json) · [Independent exact checker](experiments/check_cyclic_fano_cubic_polars.py)

### A polynomial obstruction checked in Lean

For the fixed **Case05** candidate, Lean constructs the polynomial operators and verifies the coefficients giving a two-row contradiction over every characteristic-zero field. This formalizes an existing exclusion.

Identification with the original geometric problem and completeness of the normalized correction space remain outside those Lean theorems.

[Proof and boundary](notes/cyclic-fano-polynomial-bridge.md) · [Lean source](formal/HodgeLab/CyclicFano/Case05PolynomialField.lean) · [Archived CI receipt](formal/results/polynomial-bridge-ci/39089131101/metadata.json)

### See the actual correction map

[![Correction directions and target obstructions for three fixed denominators](results/koszul-geometry/operator-geometry.png)](notes/koszul-geometric-map.md)

The diagrams show what the allowed numerator corrections can change, and why a target can retain an obstruction even as a numerical fit improves.

[Operator geometry](notes/koszul-geometric-map.md) · [Denominator sweep](notes/koszul-denominator-sweep.md) · [Visual idea atlas](notes/idea-atlas.md)

The atlas also connects the experiments with Gaussian fields, flows, random matrices, and geometric constructions. Each route links its motivation to the computations and limits recorded in the corresponding note.

## Explore the repository

| Directory or document | What to find |
| --- | --- |
| [`LEDGER.md`](LEDGER.md) | Dated research checkpoints, upstream contributions, corrections, and attribution |
| [`notes/`](notes/) | Derivations, visual explanations, experimental choices, and failed approaches |
| [`experiments/`](experiments/) | Search programs, independent checkers, and figure generators |
| [`results/`](results/) | Saved inputs, outputs, exact certificates, figures, and verification receipts |
| [`algebra/`](algebra/README.md) | Polynomial certificate models and exact linear-algebra machinery |
| [`formal/`](formal/README.md) | Lean statements, proof sources, build instructions, and audit boundaries |
| [`SOURCES.md`](SOURCES.md) | Source attribution and the origins of the methods and data |

## Reproduce an exact check

With Git and Python 3.11 or later:

```sh
git clone --recurse-submodules https://github.com/rbajaj5/hodge-lab.git
cd hodge-lab
python -S experiments/check_cyclic_fano_cubic_polars.py
```

This checker uses standard-library exact arithmetic and needs no GPU. Read the [reproduction notes](notes/cyclic-fano-cubic-polars.md#bounds-failures-and-reproduction) for the complete scope and recorded controls.

Plotting and numerical experiments use [`requirements.txt`](requirements.txt); CUDA experiments have separate [dependencies](requirements-cuda.txt). Lean setup and replay commands are in [`formal/README.md`](formal/README.md). Do not run verification scripts with Python's `-O` option. Regeneration commands may overwrite saved outputs; the individual notes identify them.

## Evidence, credit, and publication

The ledger distinguishes numerical observations, exact identities, bounded exclusions, formal proofs, and accepted upstream submissions. Author-reported findings and locally reproduced checks are recorded separately. AI assistance is part of the workflow; each audit states what was actually executed.

The recorded upstream contribution tally is **27 discussion contributions, one closed maintenance PR, and zero accepted authored solves by rbajaj5**. Acknowledgment of a research direction does not transfer solve authorship.

Every upstream post, reply, or substantive edit requires a ledger audit before publication, followed by the actual outcome and permanent link. Routine technical updates stay in this notebook. Discussion 127 is included in the intended monitoring scope; that policy does not itself change an external scheduled monitor.

[Research standards](notes/research-milestones.md) · [Repository workflow](AGENTS.md) · [Earlier front-page snapshot](https://github.com/rbajaj5/hodge-lab/blob/b3e213e27e6fb153d99d7118fc8a35cb059e9c7a/README.md)

---

Hodge Lab is an independent learning and research notebook. It is not affiliated with Hodge Labs, hodge.computer, or the maintainers of `hodge-computer/sextics`.

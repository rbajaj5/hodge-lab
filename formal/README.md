# Lean proofs for the rank shortcut and concrete obstructions

## One-reflection-skew polynomial obstruction

The [coordinate-volume module](HodgeLab/OneReflectionSkew/CoordinateVolume.lean)
now derives the actual polynomial Jacobians and ordered Euler-volume sign.
The [density module](HodgeLab/OneReflectionSkew/VolumeDensity.lean) proves
the coefficient −U²/(2G²), with G≠0 on the ambient complement and x≠0
for inverse-Jacobian recovery. Run `python3 -O check_skew_volume.py`:
16 theorem audits, two new-module kernel replays and four false-statement
controls. [Scope and diagram](../notes/skew-volume-lean.md) ·
[Receipt](results/skew-volume/validation.json).
This is an ordered determinant coefficient model; residue reduction and
general differential-form transport remain separate.

The [protected chart substitution](HodgeLab/OneReflectionSkew/ChartSubstitution.lean)
now proves `F(x,rx,wx,1,t,z)=z^6+P(x^2)` and `A=x^3`, binding P to the
actual existing `p7` (with its factor seven) and its leading coefficient
to the existing `a`. Eight theorem audits and a new-module kernel replay
are checked by `python3 -O check_skew_chart.py`.
[Exact scope and reproducible diagram](../notes/skew-chart-lean.md) ·
[Receipt](results/skew-chart/validation.json).
This closes the polynomial step. The later volume/Jacobian coefficient proof
is linked above; residue normalization and the rational primitive remain
separate formal obligations.

The [degree-bound extension](HodgeLab/OneReflectionSkew/DegreeFour.lean) now proves
the same exclusion for arbitrary numerator polynomials of total degree at most
four, with the unused fifth coordinate explicitly absent. The separate
[protected-target comparison](HodgeLab/OneReflectionSkew/CoordinateComparison.lean)
checks why the accepted mixed-polar coordinate formula cannot transfer unchanged.
Run `python3 -O check_skew_extension.py` for the two new-module kernel replays,
23 theorem audits and three rejected false statements.
[Scope, visualization and remaining transport dependency](../notes/skew-lean-extension.md)
· [New receipt](results/skew-extension/validation.json).

The [new module](HodgeLab/OneReflectionSkew/ThreeCoefficient.lean) constructs
the degree-four chart operator, checks its 840 selected column coefficients
and three source coefficients, and proves the encoded polynomial equation
has no solution over any characteristic-zero field. It reuses the sparse
polynomial and row-certificate libraries below. It does not formalize the
geometric source transport or compare the 45 higher-U images with fqlx's space.

Run `python3 -O check_skew.py` with the pinned dependencies installed.
[Scope and diagram](../notes/skew-lean.md) · [Executed local receipt](results/skew-lean/validation.json).

## Earlier cyclic-Fano stages

The notebook has three stages of formalization. The original rank-gap theorem
accepts dimension bounds as hypotheses. The new concrete project encodes
integer coefficient rows for all sixteen fixed cubic-direction candidates
and checks a separating row functional for each one. Its final theorems
have **no rank-bound hypotheses**: they rule out solutions to the literal
encoded equations over every characteristic-zero field. The latest stage
constructs the polynomial operators for Case05 and proves that their
selected coefficients give the existing matrix.

[Concrete experiment and limits](../notes/cyclic-fano-concrete-lean.md)
· [Concrete proof visualization](../results/cyclic-fano-lean-figures/concrete-lean.png)
· [Case 05 source](HodgeLab/CyclicFano/Case05.lean)
· [Reusable row-certificate lemmas](HodgeLab/RowCertificate.lean).

For Case05, the polynomial-to-matrix step is now formalized in Lean. For the
other fifteen cases, it remains an independent Python check. Identification
with the original geometric problem and completeness of the correction
space remain outside the Lean theorems. No `HodgeComputer.HasCertificate`
is established.
They also do not compute the exact ranks 150 and 151: an exact row
obstruction is enough to prove the required inconsistency.

## Case05 polynomial-to-matrix bridge

[`SparsePolynomial.lean`](HodgeLab/SparsePolynomial.lean) proves that finite
list operations for scaling, multiplication, differentiation and coefficient
extraction agree with mathlib's `MvPolynomial` operations. The
[`Case05Polynomial` module](HodgeLab/CyclicFano/Case05Polynomial.lean) constructs
the fixed denominator and 175 correction polynomials from the displayed
`Q`, `H` and density. Lean computes the 352 selected coefficients using
kernel reduction and derives the original matrix equation.

[`Case05PolynomialField`](HodgeLab/CyclicFano/Case05PolynomialField.lean)
maps rational coefficients into any characteristic-zero field and proves
the corresponding polynomial equation has no solution. This strengthens
the formal verification of an existing fixed exclusion; it is not a new
denominator search or a proof of correction-space completeness.

[Full derivation and reproduction](../notes/cyclic-fano-polynomial-bridge.md)
· [New proof diagram](../results/cyclic-fano-polynomial-bridge-figures/polynomial-bridge.png)
· [Independent reconstruction](../results/cyclic-fano-polynomial-bridge/independent-validation.json)
· [Bounded development attempts](results/polynomial-bridge-development/README.md).

Run `python3 -S check_polynomial_bridge.py --fetch-cache` here for the
separate five-module audit. The previous sixteen-case sources and their
receipts remain unchanged.

**Fresh CI: PASS.** All five modules compiled and replayed, all 30 listed
declaration reports used only the allowed standard axioms, and both altered
inputs were rejected. Separate kernel-checked proofs establish that the
altered coefficient equations are false. The archive binds the exact
tested sources and all 26 command logs.
[Receipt and metadata](results/polynomial-bridge-ci/39089131101/metadata.json)
· [CI run](https://github.com/rbajaj5/hodge-lab/actions/runs/39089131101).

## Concrete integer row certificates

For each case, `matrix`, `target`, and `dual` are transparent integer
definitions. Unlisted entries are zero. All 175 correction columns remain
in the encoded matrix; the selected row counts range from 2 to 39.

- `annihilates` splits the 175 finite column cases and checks each
  cancellation using kernel `decide`.
- `separates` checks the nonzero target pairing using kernel `decide`.
- `no_solution` applies the generic integer-certificate lemma over an
  arbitrary characteristic-zero field, including the complex numbers.

For case 05, the two rows have their only nonzero entries in column 119:
`1` and `-756`. Their target entries are `0` and `-5`. The row functional
`(756, 1)` cancels the correction column but gives `-5` on the target.
Every other column has zero pairing as well. This is a concrete two-row
contradiction, rather than an assumed rank inequality.

The portable audit driver builds all seventeen modules, audits fifty
declarations, and runs standalone kernel replay. It also requires two
deliberately corrupted concrete certificates to fail compilation. It
uses no new proof axioms or unchecked native decision procedure. The
[local compilation and axiom receipt](results/concrete-compilation-validation.json),
[separate native replay receipt](results/concrete-direct-replay-validation.json),
[export manifest](results/concrete-export.json), and
[development record](results/concrete-development.json) retain the source
bindings, checks, and failed build/replay attempts.

Repeated local WSL interruptions required a separate Windows replay route.
`ReplayConcrete.lean` calls the installed official
`replayFromImports` routine from `LeanChecker` sequentially for the seventeen
explicit modules. It avoids the command-line checker's full-cache scan
and parallel task dispatch. It retains the standard trusted-import
semantics; it is not a fresh replay of mathlib or a different kernel
implementation. The native receipt records the actual completed modules
and must be read separately from the compilation receipt. Its result
does not claim execution of the portable driver's two mutation controls.

**Complete Linux audit: PASS.** The fresh
[CI run](https://github.com/rbajaj5/hodge-lab/actions/runs/39082400121)
compiled and replayed all seventeen modules, checked all fifty expected
declaration reports, and rejected both deliberately corrupted Case05
certificates. The
[archived receipt](results/concrete-ci/39082400121/concrete-coefficient-validation.json)
and [run metadata with all command-log hashes](results/concrete-ci/39082400121/metadata.json)
bind the exact tested sources and inputs. A separate audit compared those
bindings with commit `7fe139a` and checked all 38 command logs. The recorded
build and replay artifact hashes match pairwise; compiled binaries are not
included in this archive. The seventeen kernel replays took 135.321 seconds
in that run, excluding compilation and other checks.

**Earlier local status:** all seventeen modules compiled and all fifty
axiom audits passed. The additional aggregate native replay is
**INCOMPLETE** after its 420-second bound. The two Lean mutation controls
were not executed locally; the later Linux run above completed them.

## Earlier generic rank-gap bridge

This notebook now has a small Lean project. It formalizes the **generic logical
step** used by the [cubic-polar rank certificates](../notes/cyclic-fano-cubic-polars.md):
if the correction span has dimension at most `n` and adjoining the target gives
dimension at least `n + 1`, the target cannot belong to that correction span.
The particular `150 / 151` bounds are a specialization.

In this earlier rank-gap module, the actual polynomial matrices, the 25 correction relations, the sixteen
modular minors, and the transfer of a nonzero modular minor to characteristic
zero are checked by the Python experiment, **not by the rank-gap module**. The
dimension inequalities remain explicit hypotheses of the Lean theorem. No
`HodgeComputer.HasCertificate` statement, instance solution, or upstream
acceptance is established here.

## What the proof does

```mermaid
flowchart TD
    A["External exact computation:<br/>correction dimension at most n"]
    B["External exact computation:<br/>augmented dimension at least n + 1"]
    A --> C["Lean theorem hypotheses"]
    B --> C
    C --> D["Assume target belongs to correction span"]
    D --> E["span_insert_eq_span:<br/>adjoining target leaves the span equal"]
    E --> F["The two dimensions are equal"]
    F --> G["n + 1 is at most n: contradiction"]
    G --> H["Target is outside correction span"]
    classDef external fill:#fff1cf,stroke:#9a6a00,color:#202020;
    classDef checked fill:#d7eee7,stroke:#26755b,color:#202020;
    class A,B external;
    class C,D,E,F,G,H checked;
```

The yellow nodes identify the current boundary of formalization. The green
nodes describe the actual implication proved in
[`HodgeLab/RankGap.lean`](HodgeLab/RankGap.lean):

- `HodgeLab.not_mem_of_finrank_gap` proves the general implication.
- `HodgeLab.not_mem_of_finrank_150_151` instantiates the experimental bounds.
- `HodgeLab.no_correction_solution_of_finrank_gap` rules out equality with any
  proposed candidate known to lie in the correction span.

The proof does not require independence of the correction generators. It also
does not require a separate finite-dimensional ambient-space assumption: under
the contradiction hypothesis the two spans are literally equal, hence their
`finrank` values are equal. The experiment itself concerns finite matrices.

## Pinned environment and reproduction

This standalone notebook project pins Lean **4.31.0** and mathlib commit
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`. It uses the already available local
cache. The upstream challenge pins Lean 4.33.0 and a different mathlib commit.
The two proposed maintenance modules now also pass the isolated upstream
compatibility audit described below. This does not migrate or validate all
sixteen notebook cases under that newer toolchain.

With Elan installed, run from `formal/`:

```sh
lake exe cache get
python3 check.py
python3 check_concrete.py
```

The original audit driver runs `lake build`, prints the axioms for its three declarations,
and replays `HodgeLab.RankGap` with the standalone `leanchecker`. It rejects
unfinished-proof tokens in this project's Lean files and allows only `propext`,
`Classical.choice`, and `Quot.sound` in the reported theorem dependencies.
Each command has a 300-second bound. The source-bound result is saved in
[`results/rank-gap-validation.json`](results/rank-gap-validation.json), with
the actual compiler, build, axiom, and kernel logs beside it.

**Local status: PASS.** All three theorems compiled, their printed dependencies
contain only the three allowed axioms, and standalone kernel replay exited
successfully. The receipt records the exact sources and environment. This does
not by itself report a remote CI result.

The local cache link inside `.lake/` is ignored; it is not a portable dependency.
The committed Lake manifest pins the dependencies needed by a fresh checkout.
CI repeats both builds and audits without CUDA. Local compilation, a concrete
coefficient obstruction, and an accepted instance solution are distinct.

The separate [compatibility runner](compatibility/upstream433/check.py)
uses an isolated copy of upstream's final Lean 4.33.0 toolchain, exact
mathlib manifest, and the two files proposed in PR #121. It checks
the source bindings, actual dependency revisions, five declaration
reports, two module replays, and two deliberately altered certificates.
It checks those two proposed modules, not a build of the whole upstream
repository. Run it from a fresh checkout with:

```sh
python3 formal/compatibility/upstream433/check.py --fetch-cache
```

The separate `Upstream Lean 4.33 compatibility` workflow runs this same
command. Its result must be read separately from the notebook's Lean
4.31.0 audit and from any protected upstream acceptance decision.

**Upstream-toolchain compatibility: PASS.**
[Run 39084143971](https://github.com/rbajaj5/hodge-lab/actions/runs/39084143971)
completed on final Lean 4.33.0 with all nine pinned dependencies. Both
exact proposed modules compiled and replayed, all five axiom reports
passed, and both altered certificates were rejected. The downloaded
[receipt](results/upstream433-ci/39084143971/validation.json) and
[all 18 command logs](results/upstream433-ci/39084143971/metadata.json)
were independently checked against PR head `84b1c158` and the tested
notebook commit. PR #121 was subsequently closed unmerged on 18 October 2026; this is
our compatibility CI, not protected upstream acceptance. On 17 October
at 21:52 EDT, upstream's check stopped at missing owner authorization
and skipped Lean. [Observed run and diagnostic](../results/cyclic-fano-lean/upstream-maintenance/owner-gate-39087992575/observation.json).

The Lean workflow uploads its actual receipts and command logs as
`concrete-lean-verification`, including diagnostic logs on failure.
The ordinary `check_concrete.py` invocation does not reuse committed
checkpoints; `--resume` is an explicit local recovery option.

This proof uses mathlib's span and dimension API, especially
`Submodule.span_insert_eq_span`. Codex assisted its construction and a separate
statement/scope review. The exact numerical experiments and their independent
replays remain linked from the mathematical notebook.

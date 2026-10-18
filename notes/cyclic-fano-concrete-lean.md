# From a GPU rank gap to a concrete Lean obstruction

**Continuation:** the [Case05 polynomial bridge](cyclic-fano-polynomial-bridge.md)
now formalizes the polynomial-to-matrix step for this one fixed candidate.
This note retains the original sixteen-case literal-matrix audit and its
limits; the new work does not change those sources or add a new exclusion.

The [cubic-direction experiment](cyclic-fano-cubic-polars.md) tested sixteen
fixed denominators for `cyclic-triple-fano`. Its rational correction matrix
has 175 columns. The GPU found a rank gap modulo 65,521, and the separate
Python checker combined exact column relations with nonzero modular minors
to certify the fixed exclusions in characteristic zero.

The [first Lean project](../formal/HodgeLab/RankGap.lean) proved only the
generic implication from two dimension bounds. The next step is to put
actual matrix coefficients inside Lean, replacing those rank-bound
hypotheses with a checked finite certificate.

## A smaller certificate to check

Write the necessary coefficient equations as `M x = b`. Select a finite
set of their rows, clear rational denominators, and divide out any common
integer factor. Each row is therefore multiplied by a nonzero rational
number. Call the resulting integer matrix `B` and target
vector `t`. An integer row vector `w` is an obstruction when

$$
w^{\mathsf T}B=0,\qquad w^{\mathsf T}t=c\ne0.
$$

Any solution would give `0 = c` after taking that weighted sum of its
equations. The contradiction works over every field of characteristic
zero, including the rationals and complex numbers. A small subset of
rows suffices, provided it includes every one of the 175 correction
columns. The selected rows need not describe the entire coefficient
system: inconsistency of a subsystem already excludes a solution of the
full system.

This route avoids computing a 151-by-151 determinant in the Lean kernel.
It checks a concrete obstruction directly. It does not, by itself,
formalize the numerical assertions that the two ranks are exactly 150
and 151, nor does it produce an existence certificate for the instance.

## The first mixed example

For fixed case 05 the denominator direction is raw parameter `0 + 69`.
The selected coefficient monomials, in the order
`X0, X1, Z, Y0, Y1, Y2`, are `(0,1,0,7,1,5)` and `(1,0,0,5,2,6)`.
Multiplying their physical coefficient rows by `49/2400` and `147/40`
respectively gives

$$
x_{119}=0,\qquad -756x_{119}=-5.
$$

All other 174 correction columns are zero in these two rows. The integer
functional `w = (756, 1)` gives `0 = -5`. Both equations and all 175
columns are literal data in
[`Case05.lean`](../formal/HodgeLab/CyclicFano/Case05.lean).
[`case-05.json`](../results/cyclic-fano-lean/case-05.json) retains the
row scaling, denominator, direction, monomials, and search record.

The [concrete proof map](../results/cyclic-fano-lean-figures/concrete-lean.png)
shows the actual selected rows, their only active correction column, and
the integer functional. Its renderer checks the source bindings and
reconstructs both displayed physical rows before drawing them.

## Coverage and reproduction

All sixteen frozen candidates admit these certificates, with **100 selected
rows and 611 nonzero matrix entries** in total. The exporter searches exact
rational row combinations, preferring rows with nonzero correction entries
so that the result exhibits cancellation. Each candidate completed its
first search; no row search timed out or required the zero-row fallback.
The outer process bound was 120 seconds per candidate, with a 90-second
elimination bound inside each search.

| Saved candidates | Count | Selected rows per candidate |
| --- | ---: | --- |
| Monomial controls, cases 00–04 | 5 | 2–3 |
| Two-component directions, cases 05–09 | 5 | 2 |
| Seeded eight-term directions, cases 10–12 | 3 | 2–3 |
| Seeded dense directions, cases 13–15 | 3 | 16, 39, 16 |

[Search packet](../results/cyclic-fano-lean/packet.json)
· [Primary replay](../results/cyclic-fano-lean/validation.json)
· [Independent reconstruction](../results/cyclic-fano-lean/independent-validation.json)
· [Lean export manifest](../formal/results/concrete-export.json)
· [Lean compilation and axiom receipt](../formal/results/concrete-compilation-validation.json)
· [Separate kernel replay receipt](../formal/results/concrete-direct-replay-validation.json).

The primary replay checks all sixteen witnesses and rejects 48 deliberately
altered inputs. The independent implementation reconstructs 17,600 physical
coefficients, checks every column cancellation, compares every Lean matrix,
target, and dual literal with the certificate data, and rejects 112 altered
inputs. The checks include absent entries, whose coefficients must be zero.
It does not import the primary polynomial producer or the certificate
exporter.

From the repository root:

```sh
python3 -S experiments/export_cyclic_fano_lean.py verify
python3 -S experiments/check_cyclic_fano_lean.py
cd formal
lake exe cache get
python3 check_concrete.py
cd ..
python3 experiments/plot_cyclic_fano_lean.py
```

The export generator is `formal/generate_concrete.py`. The proof splits
the 175 finite column cases and uses kernel `decide` for each integer
equality, followed by a finite-sum lemma and an injective integer cast
into any characteristic-zero field.
No unchecked native decision procedure or additional axiom is used.

## Failed attempts and resource limits

The first generic proof build missed two narrow imports: the finite-sum
interchange lemma and the field definitions. Adding the imports repaired
compilation without changing the theorem statement.

All sixteen concrete modules compiled and passed the fifty-declaration
axiom audit. The first standalone replay passed seventeen module names
to `leanchecker` together. The installed checker launches a task for each
module; the concurrent replay exhausted WSL memory and was killed at
roughly 14 GB resident memory. A separate two-module upstream-port replay
was also interrupted when that WSL session ended. This failed run did not
produce a passing kernel receipt.

Two sequential retries then stopped at case 04. The WSL-hosted Python
driver ended without a traceback; a Windows-hosted retry isolated the
failure to that single module, again with empty checker output. No
additional out-of-memory event was observed for those retries, so their
exact termination cause is unconfirmed. Splitting the closed universal
arithmetic proof into 175 column cases repaired the isolated replay.
The literal matrices, row weights, targets, and theorem statements did
not change. The replacement audit uses that smaller proof structure
and runs one module per checker process with explicit time bounds and
per-command checkpoints.

A later batch rebuild was interrupted again, eventually reporting
`Wsl/Service/E_UNEXPECTED`. Sequential compilation advanced through
case 11 before another empty exit; case 12 subsequently compiled when
retried in a short phase. The checker therefore supports opt-in
resumption against the exact source fingerprint. Ordinary invocation,
including CI, runs the checks afresh. Interruptions and successful
retries are recorded separately; a partial run cannot write a final
passing receipt.

All sixteen refactored modules subsequently compiled and passed the
fifty-declaration axiom audit. Further WSL replay interruptions moved
to previously successful cases. The Windows command-line checker then
spent its bounded attempt traversing the dependency cache over UNC.
A small audit runner instead calls the installed official
`replayFromImports` from `LeanChecker` for each explicit module. The first
concrete native replay succeeded. This uses the same target-declaration
checking routine and standard trusted imports as the command-line tool;
it does not recheck all of mathlib or use an independent kernel.
The compilation and replay receipts remain separate so success in one
cannot stand in for success in the other.

The final bounded native seventeen-module replay timed out after 420
seconds. Its captured output contained no completed-module markers, so
the saved aggregate receipt is **INCOMPLETE**. All seventeen module
compilations and fifty axiom audits are recorded separately as **PASS**.
The two deliberate Lean mutation controls have not run locally; the
portable CI driver requires them along with a fresh full replay.

The later [fresh Linux CI run](https://github.com/rbajaj5/hodge-lab/actions/runs/39082400121)
completed that full audit successfully: seventeen builds, seventeen
standalone module replays, fifty expected axiom reports, and two rejected
corrupted certificates. Its
[actual receipt](../formal/results/concrete-ci/39082400121/concrete-coefficient-validation.json)
and [archived logs and metadata](../formal/results/concrete-ci/39082400121/metadata.json)
were downloaded and checked against the tested commit. The seventeen
replays took 135.321 seconds. The two negative controls fail because
`decide` establishes that their altered propositions are false, rather
than because of a missing import. The original local timeout is preserved
as a separate historical outcome. The successful CI establishes the
encoded matrix obstruction; it does not move the polynomial identification
inside Lean or prove a `HasCertificate` statement.

The smaller two-file upstream maintenance proposal was checked separately:
both exact proposed modules compiled, all five axiom reports passed, and
the official replay routine completed for both modules under Lean 4.31.0.
Its [receipt and command logs](../results/cyclic-fano-lean/upstream-maintenance/receipt.json)
bind the actual proposed source files. A later isolated
[Linux run](https://github.com/rbajaj5/hodge-lab/actions/runs/39084143971)
also checks those exact two files against upstream's final Lean 4.33.0
and all nine pinned dependencies. Both modules compile and replay, all
five declaration reports pass, and both altered-certificate controls are
rejected. The [source-bound receipt and logs](../formal/results/upstream433-ci/39084143971/metadata.json)
were downloaded and independently audited. This establishes compatibility
of those two maintenance modules. The PR is now ready for review; upstream's
17 October, 21:52 EDT run stopped at missing owner authorization and skipped
Lean. [Observed diagnostic](../results/cyclic-fano-lean/upstream-maintenance/owner-gate-39087992575/observation.json).
No protected upstream acceptance or `HasCertificate` proof is claimed.

The [development record](../formal/results/concrete-development.json)
retains the failure and subsequent outcome. The comparison with the older
GPU rank method is about proof size and verification scope; no benchmark
of two fully formalized rank algorithms is claimed.

## Where the formal argument starts

Working in Lean can feel like whack-a-mole: repair a missing import,
and the next obstacle is a finite-sum rewrite; align the sums, and an
integer cast needs its own justification; get the proof to compile,
and replay can become the expensive part. Here the mathematical
contradiction was simply `0 = -5`, while expressing and checking every
step took considerably more work. Some obstacles belonged to the
formalization, some to our code, and some to Windows/WSL. Each successful
repair makes another dependency explicit. That is useful progress,
even when it adds no new mathematical exclusion.

The numerical search and rational certificate construction may suggest
the row weights. Lean must check their actual cancellations and the
nonzero target pairing; an imported claim of success is insufficient.

The separate Python reconstruction checks that the exported integer
coefficients really are scaled rows of the polynomial correction system,
with the target, denominator direction, row monomials, and all correction
columns fixed. For the other fifteen cases, that reconstruction is still
outside Lean, and their theorems concern the literal exported matrices.
The new Case05 continuation formally connects its displayed polynomial
operators to the matrix; the geometric completeness boundary remains.
The original figure records the earlier literal-matrix stage.

The sixteen directions are a finite sample already excluded by the
preceding exact calculation. Formalizing their certificates strengthens
the verification of those results; it does not add sixteen new
exclusions or settle the full 175-parameter denominator family.

## Attribution

This continues the upstream certificate framework and the notebook's
source-based Koszul calculation. Finite-dimensional separation by a left
null vector is standard linear algebra; no new separation theorem is
claimed. Mathlib supplies the algebra and finite-sum API. Codex assists
certificate construction, formalization, independent reconstruction,
documentation, and visualization. The GPU supplies the preceding rank
screen, rather than the Lean proof.

# 132 further three-character exclusions around X1/Y1

**Exact result:** 132 new complete degree-seven three-character families are
excluded. Together with the preceding 152, our selected union now contains
**284 excluded triples**. The new batch completes all 136 third-character
extensions of `X1/Y1`; four were already in the preceding selection.
This is a small specified subset of the 428,536 unordered triples among
the 138 retained character sectors. Holdout remains unsolved. There is no
Lean `HasCertificate` proof, solve PR, or improved unconditional degree bound.

The fixed target remains `q = 1`, `A = X0^3 Y0^3`, and the exact `F` in
`sources/sextics/data/holdout/instance.rec` at upstream
`b8c4edeb80a82395ec07164caf445cfa43bbbd56`. All existing upstream files are
unchanged. A nonzero quotient modulo `F` is allowed throughout.

## Selection and motivation

The preceding family-151 calculation suggested a practical sequence: use
small graded multiplication maps, retain partial normalized-chart results,
then reconstruct the physical equations after every proved vanishing.
We apply that sequence to another fixed pair, rather than treating a failed
degree-four search as a reason to abandon the entire family.

The pair is `X1/Y1`, with characters `(0,1,0)` and `(5,3,0)`. Add each of
the other 136 retained characters, using its **complete E1 eigenspace**.
Exclude from the new batch the four triples already proved as old families
7, 17, 150, and 151: their additional characters are respectively `(0,0,0)`,
`(0,0,1)`, `(1,0,0)`, and `(1,2,3)`.

The [manifest](../results/x1y1-extensions/plan.json) records all 132 triples,
their full basis lists, a new local batch number, and a one-based global
lexicographic index among all 428,536 triples. **B19 below means batch 19
here, not family 19 in the preceding 152-family packet.** Initial denominator
coordinate counts range from 15 to 20. No family-151-specific linear
constraint is transferred to these new families.

## First pass: necessary ideals and small graded maps

For active denominator coefficients `a`, exact physical left annihilators
of the independently enlarged Koszul correction columns give homogeneous
quadratic necessities `P(a) = 0`. Enlarging that correction space weakens
the test: its obstructions remain valid, while its surviving systems need
not correspond to certificates.

We first check coordinate squares in the rational span of these necessities.
When no square is found, retain every necessary polynomial supported in one
character's coordinates and form its degree-three and degree-four maps:

\[
\bigoplus_j S_{d-2}\longrightarrow S_d,
\qquad (u_j)_j\longmapsto\sum_j u_jP_j,\qquad d=3,4.
\]

These pure-block equations are consequences of the full equations; they
are not obtained by setting the other character components to zero.
An explicit identity `a_i^d = sum u_j P_j` forces `a_i = 0` over the complex
numbers. Rebuild after each nonempty group of forced zeros. Each successful
step strictly decreases the active coordinate list.

This pass reduces **123 families** to the already proved X1/Y1 pair.
Its checker replays 5,911 physical duals, 660,743 correction pairings,
160,903 quadratic pairings, 739 square identities, nine higher-power
identities, and 69 graded maps. One deliberately altered power witness in
each of the 132 family packets is rejected. These are verification-operation
counts; they are not counts of independent discoveries.

Nine families remain unresolved by this bounded procedure. Their unsuccessful
degree-three/four block searches are retained without reclassifying them as
successful just because a later method finishes the families.

## Shared numerators and rebuilding close the nine survivors

For each survivor, construct the full physical system

\[
E(a,z)=b(a)+M(a)z=0
\]

using the entire numerator-character coset allowed by the denominator's
stabilizer. The permitted Koszul correction counts range from 68 to 256;
the same `z` variables occur in every row. Normalize each remaining
third-character coefficient to one in turn, and replay affine consequences
and square-zero inferences. The system is homogeneous in `(a,z)`, so a
contradiction on `a_i=1` forces `a_i=0` globally. No matrix minor is divided
out and no generic-rank assumption is used.

Of **22 charts**, **20 contradict** immediately under this propagation.
Two remain unresolved: B19 at `a119=1`, and B100 at `a6=1`. Nevertheless,
other chart exclusions in those families already force global zeros.
Rebuilding after those zeros exposes new square identities and closes both.

| New batch | Global triple index | Added character | Initial → after blocks → after shared charts → residual | New zeros after rebuilding |
| --- | ---: | --- | --- | --- |
| B19 | 55710 | (0,4,3) | 19 → 15 → 12 → 10 | 119, then 139 |
| B49 | 58894 | (2,0,3) | 19 → 14 → 11 → 10 | 170 |
| B61 | 59824 | (2,3,0) | 19 → 16 → 12 → 10 | 170, 198 |
| B72 | 60550 | (3,0,1) | 16 → 14 → 12 → 10 | 139, 170 |
| B75 | 60727 | (3,1,0) | 18 → 11 → 10 → 10 | none needed |
| B84 | 61204 | (3,4,3) | 18 → 13 → 10 → 10 | none needed |
| B100 | 61852 | (4,2,3) | 17 → 12 → 11 → 10 | 6 |
| B113 | 62190 | (5,0,3) | 18 → 12 → 11 → 10 | 170 |
| B132 | 62336 | (5,5,4) | 16 → 13 → 11 → 10 | 170 |

For example, the B19 charts force `a7=a159=a216=0`. The first rebuilt
necessary system contains `a119^2 = 3 P6`; after removing 119, the next
system contains `a139^2 = -36 P5`. In B100 the chart `a211=1` contradicts;
after `a211=0`, rebuilding gives `a6^2 = -12 P8`. The `P` labels here are
**zero-based rows in the corresponding rebuilt packet**, not universal
equations or indices in the original shared system. Each identity is stored
with its physical dual and checked coefficient by coefficient.

The shared continuation replays 22 chart traces and 745 exact inferences,
rejects nine deliberately altered chart identities, and adds ten square
identities after rebuilding. Its receipt also includes replays of the
inherited reductions for these nine families; those overlapping counts
should not be added to the first-pass totals as new results.

Every family finally has support contained in the ten raw basis directions

```
123, 135, 180, 210, 229, 232, 235, 272, 289, 293.
```

The exclusion of this remaining pair is **fqlx's prior result**, not a new
discovery here. We rerun both checkers from the pinned
[pair-30 proof packet](https://gist.github.com/fqlx/58c0183e1fdbfc5d42a78d005e1d9bab/d69313fe578843f8341e6ed557c425bc7755c1d7),
check all 20 source hashes, and explicitly match the exact `F`, `A`, and all
ten denominator/numerator-lift pairs to our physical construction. The
[replay receipt](../results/x1y1-extensions/pair30/replay.json) and logs are
included. Extra anchor coordinates such as 139, 170, and 198 are removed by
our new identities before invoking that ten-coordinate dependency.

## Visual record

![Coverage and rebuilding of the nine survivors](../results/x1y1-extensions/x1y1-extensions.png)

The left panel shows all 132 new batch IDs and which route was needed. The
right panel counts retained denominator coefficients at successive proof
stages. These counts are not dimensions of the certificate solution variety.

The [interactive graded-map view](../visualizations/x1y1-extensions-standalone.html)
shows the **18 actual failed pure-third-character maps** at degrees three
and four for the nine survivors. Select a character and degree, then inspect
an entry for its equation product, output monomial, and exact rational
coefficient. Color gives the coefficient sign, not its magnitude. Missing
columns mean that no pure-block generator was available, not that the full
physical system has no constraints. No coordinate power belongs to any of
these 18 displayed images; that claim is checked separately from the ranks.
The full computation, rather than the picture alone, establishes the result.

All 294 nonzero displayed entries and exact map ranks are reconstructed.
All 54 browser layouts pass at widths 736, 360, and 320, including native
controls, exact-entry inspection, empty maps, and restored state. Static,
desktop, and mobile images were inspected. Download the standalone HTML to
use it; GitHub's file viewer displays source.

These are finite graded maps of necessary ideals. We do not compute a full
free resolution, establish a statistical phase transition, or apply an
imaginary-geometry theorem.

## Bounds, unsuccessful searches, and corrections

- The initial 132-family pass uses two chunks with **300 seconds per chunk**,
  two workers, and maximum block degree four. Both chunks finish; no timeout
  occurs. The [plan](../results/x1y1-extensions/plan.json),
  [attempts](../results/x1y1-extensions/attempts.json), complete family
  packets, and logs retain all nine first-pass failures.
- The shared-equation pass uses **60 seconds per family**, two workers, and
  affine/square propagation only. All nine jobs finish. It does not silently
  extend a stalled chart into a larger polynomial-multiplier search.
  Both unresolved charts retain their original traces, with respectively
  132 and 104 retained chart variables. Their later closures use globally
  forced zeros from other charts, not a claim that the original searches
  succeeded. [Plan](../results/x1y1-extensions/shared-plan.json) and
  [attempts](../results/x1y1-extensions/shared-attempts.json).
- The deterministic continuation rebuilds necessities after those verified
  zeros and stops when each residual support matches the proved pair. Every
  successful iteration removes at least one coordinate; all nine complete
  in the recorded run. [Continuation outcomes](../results/x1y1-extensions/continuation-attempts.json).
- A checker syntax typo (`==not` instead of `==(not ...)`) was fixed before
  the first successful verification; no generated identity was changed.
  The older shared constructor now accepts an optional anchor pair, while
  preserving its X0/Y0 default. Its existing 24-family replay passes.
- No numerical residual, real-positivity test, or GPU approximation is used
  as a proof premise. These exact sparse systems were checked on the CPU.

## Reproduce

With the pinned upstream submodule initialized, run:

```sh
python -S experiments/reproduce_pair30.py --fetch --output-directory results/x1y1-extensions/pair30
python -S experiments/check_x1y1_extensions.py
python -S experiments/check_x1y1_extensions.py --independent
python -S experiments/check_x1y1_shared.py
python -S experiments/check_x1y1_shared.py --independent
python -S experiments/plot_x1y1_extensions.py --check
```

All pass locally. The proof replays require only Python's standard library;
`--fetch` needs network access to the pinned dependency. The two physical
polynomial implementations use different polynomial APIs and opposite monic
division but share identity-replay code. This is not independent human
review or a claim of a fresh independent agent audit. Local checks and
remote CI results are recorded separately.

To regenerate the search and static figure:

```sh
python -S experiments/x1y1_extensions.py --limit 300
python -S experiments/x1y1_shared.py --limit 60
python -S experiments/x1y1_continue.py
# Rerun the four proof checks above before building the visual data.
python experiments/plot_x1y1_extensions.py
```

Matplotlib is needed for static figure generation only. Regenerating gzip
files can change their metadata and hashes; regenerate dependent packets
and figures together. Check-only commands preserve proof payloads.

## Attribution and limits

Credit the Sextics authors' certificate framework, the geometric bridge
attributed there to Benjamin E. Diamond, Griffiths's residue theory, fqlx's
E1/character calculations and pair-30 obstruction, and the preceding Hodge
Lab reductions. Eisenbud's graded-module and syzygy viewpoint motivates the
multiplication-map tests. Earlier Dubedat-inspired operator visualizations
informed the research direction, but no theorem of Dubedat is used here.
Prepared with OpenAI Codex assistance on behalf of `rbajaj5`.

The completed selected union comprises both sets of 136 extensions of the
X0/Y0 and X1/Y1 pairs, plus the 20 coordinate-character triples, with eight
overlaps removed: 284 in total. Other three-character supports, larger
supports, and higher degrees are outside this result. The unconditional
lower bound remains degree at least seven.

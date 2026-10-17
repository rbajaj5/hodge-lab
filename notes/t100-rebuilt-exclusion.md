# T100: rebuilt multipliers close the last fresh X0/Y1 triple

This is an independent, AI-assisted computational notebook result for the
fixed `holdout` instance. It is not affiliated with Hodge Labs or the
hodge.computer maintainers. The protected `(F,q,A)` is unchanged at upstream
revision `b8c4edeb80a82395ec07164caf445cfa43bbbd56`, with `q=1`.

## Result

The remaining fresh family T100, global three-character family 17957, has
characters

```text
(0,0,1), (4,2,3), (5,3,0).
```

It is excluded by exact rational identities. This changes the frozen fresh
X0/Y1 batch from 131/132 to **132/132** and the selected union tracked in this
notebook from 811 to **812 three-character families**. It does not solve the
holdout instance: other degree-seven supports, larger character supports,
higher degrees, and the Lean `HasCertificate` goal remain outside this result.

![Exact graded ranks and the T100 closure](../results/typed-rewrite-families/t100-rebuilt-multipliers/t100-rebuilt.png)

## Exact chain

The preceding T100 attempt retained thirteen denominator directions and
proved `a56=0`, but its multiplier search timed out after thirteen of fourteen
blocks and both added-character charts failed. Those files remain unchanged.

This continuation rebuilds the physical shared-numerator equations after that
proved vanishing. The new system has 706 equations, 12 denominator directions,
and 128 stabilizer-compatible Koszul correction directions. Constants and all
12 linear denominator multipliers complete in 73.2 seconds on this host. They
produce 156 independent denominator relations; 39 are new modulo the finite
span of the nine constant-multiplier baseline relations and their affine
multiples. Both physical polynomial constructions replay the relations,
checking 22,037 source products and rejecting an altered witness.

The selected pure-character relations give twelve exact graded maps in degrees
three through six. In the Y1 block on raw coordinates
`135,235,272,289,293`, the degree-four map has rank 61 of 70 and already forces
`a135=a272=a289=0`. The degree-five map has full rank 126 of 126 and supplies
exact fifth-power identities for all five coordinates. Thus every Y1
coefficient vanishes. The saved packet contains 13 power witnesses with 1,725
products; both physical reconstructions replay them over the rationals and
reject each deliberately altered witness.

Rebuilding on the seven remaining X0-plus-added directions makes the charts
for raw coordinates 6 and 211 contradictory. The other five chart attempts,
for `42,88,102,111,114`, fail under this propagation and are retained. After
removing 6 and 211, the remaining denominator lies in the X0 anchor sector,
which is excluded by the separately replayed full X0/Y1 dependency. The two
physical replays agree on the complete closure, including 121 chart
inferences, 18 replayed charts across the closure and dependency, four
excluded charts, and the earlier dependency's failed charts.

These equations are necessary conditions for a certificate, so contradiction
excludes the family. The converse is not used. No claim is made that the
finite constant/linear multiplier span is the full elimination ideal.

## What the prime calculation does

Each of the twelve graded maps was also reduced modulo 1009, 1013, and 1019.
All 36 modular ranks equal the exact rational rank. This is a useful screen for
rank anomalies and implementation errors, but the exclusion does not rely on
it: every vanishing and chart contradiction has an explicit witness over
`Fraction` and is replayed against the physical equations.

Calling this “p-adic Hodge theory” would overstate the connection. We did not
construct a p-adic Galois representation, a comparison isomorphism, a filtered
module, or a Hodge–Tate decomposition. The implemented method is finite-field
linear algebra followed by exact rational certification.

## Ideas considered but not used

- Yang's viewpoint remains useful for distinguishing Koszul relations from
  the graded images that force coordinate powers. The implemented proof uses
  classical finite Koszul/Macaulay maps; it does not establish the geometric
  hypotheses of Yang's results.
- Beilinson–Bernstein localization would require a specified Lie algebra,
  flag variety, and module/localization correspondence for this certificate
  system. None was constructed.
- KZ or KPZ equations would require a conformal-block, stochastic-growth, or
  related analytic structure tied to these polynomial equations. No such
  bridge was found. They supplied no constraint in this proof.
- Vapnik/VC complexity could regularize a heuristic family of numerical rank
  predictors. It cannot replace an exact identity, and no learning-theoretic
  model was needed after the rational witnesses were found.
- The character grading visually resembles charge sectors in a vertex
  algebra: multiplication shifts sectors and the Koszul maps respect the
  grading. We have not constructed fields and modes, a state–field
  correspondence, locality, or the Borcherds/Jacobi identity, so no vertex
  algebra acts on the T100 equations in this experiment.

These are retained as failed or unsupported approaches rather than attached
to the proof after the fact.

## Reproduce

From this checkout with the pinned `sources/sextics` submodule:

```sh
python -S experiments/t100_rebuilt_multipliers.py --check
python -S experiments/t100_rebuilt_multipliers.py --check --independent
python -S experiments/t100_rebuilt_blocks.py --check
python -S experiments/t100_rebuilt_blocks.py --check --independent
python -S experiments/t100_rebuilt_closure.py --check
python -S experiments/t100_rebuilt_closure.py --check --independent
python experiments/plot_t100_rebuilt.py --check
```

All seven commands pass locally. The primary and independent reports agree
after removing timing and implementation labels. The calculation uses Python
3.11 standard-library rational arithmetic; Matplotlib is needed only to render
the PNG/SVG figure. The proof packets, plans, bounded-attempt logs, validation
reports, figure data, and five unsuccessful rebuilt charts are all retained in
[`results/typed-rewrite-families/t100-rebuilt-multipliers`](../results/typed-rewrite-families/t100-rebuilt-multipliers/).

The checked result was subsequently shared as one reply to the existing T100
thread: [discussion comment 19001784](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-19001784).
It is a mathematical-progress comment, not a pull request, Lean proof,
accepted solve, or leaderboard claim.

Prepared with OpenAI Codex assistance for rbajaj5. Credit the hodge.computer
authors' certificate and geometric-support framework, the bridge attributed
there to Benjamin E. Diamond, Griffiths's residue theory, fqlx's E1/Koszul and
symmetry calculations, the previously checked anchor-family exclusions, and
Eisenbud's graded-module viewpoint.

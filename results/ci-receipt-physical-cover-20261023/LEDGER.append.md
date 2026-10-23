

## Checkpoint 137 — 23 October 2026: CI receipt repair and one conditional physical-cover binding (local handoff)

This is a reviewed local handoff against notebook parent
d29cd55b7c7e738ae84bec7da50c8c843877506d, with upstream freshly pinned at
554757eca1aebecdd1d21f3452d3c71ffa601b19. The human assigned final Git
publication and ledger integration to the original Goal-enabled coordinator.
This chat made no commit, push or upstream publication. Reconcile concurrent
remote ledger additions before publishing; do not replace historical bytes.

First, the documented forms-to-trace receipt conflict was repaired. Both
checkers keep immutable input/history paths and allocate fresh execution
outputs; original context pins remain unchanged. Collisions, historical
paths, descendants and symlink aliases reject without overwriting a saved
PASS. CI collects fresh receipts separately. Earlier workflow checkers'
output locations were not migrated by this bounded repair.

Root executed the affected sequence on Lean 4.31.0 / Mathlib
fabf563a7c95a166b8d7b6efca11c8b4dc9d911f. Forms passed 13 theorem audits,
one module replay, five positive and three negative controls in 119.117 s.
Trace passed 56 declaration audits, three module replays, seven positive
and three negative controls in 22.223 s. All 2,862 tracked result files were
byte-identical afterward. These are CI repair rechecks, not new mathematical
results. The original remote run 39832127430 remains a recorded failure;
no fresh remote CI outcome is claimed before coordinator publication.

Then one selected conditional source-binding lemma was completed. For any
field K and a,v in K, the literal polynomial
f=X^18+X^12+(vX-1)^6-aX^15 equals coverPolynomial 1 roots when all eighteen
listed roots are roots of f and are pairwise distinct. Helpers prove monicity,
degree 18 and leading coefficient 1; the base parameter a is not a18. Two
short corollaries reuse the completed split-basis proof for last trace 1 and
slot-eleven trace 0. The proof used only the first declared approach: degree
bounds, coprime root factors and equality of monic equal-degree polynomials.
The interpolation fallback was unused.

The Lean implementation agent executed the new checker: eight declaration
audits, one new-module kernel replay, nine positive controls and four
expected false-goal rejections, all PASS in 20.775 s. Root executed the
literal-source gate, comparing the pinned comment equation and Lean
definition, current versus historical F/A/q, and five source mutation
controls. A separate derivation agent ran exact integer polynomial controls
in 0.0017 s under a 30-second bound. A read-only adversarial agent checked
the source, assumptions and saved execution hashes; this is AI review, not
independent human review. Mathlib and prior imported proofs were not newly
kernel-replayed as part of the new lemma.

At a=2,v=1, f=r^12(r^3-1)^2+(r-1)^6 has f(1)=f'(1)=0 and f''(1)=18 over Q.
The constant tuple roots_j=1 satisfies root membership, but f(2)=200705
while its eighteen-factor product at 2 is 1. Distinctness cannot be dropped.
This control does not settle generic separability. For the intended base
k=Q(a,v,t), roots must be supplied in a specified splitting extension L/k;
this pass does not establish those hypotheses or descend the trace formula.
The ratio-chart interpretation requires Y0=1, X0!=0 and r!=0; chart transport
and physical differential-source normalization were not repeated.

- [Statement, CI repair, execution attribution and limits](notes/skew-physical-cover-binding.md).
- [Actual affected sequence and history preservation](results/ci-receipt-physical-cover-20261023/sequence-executed/sequence.json).
- [New Lean checker receipt](results/ci-receipt-physical-cover-20261023/lean-development/checker-01/validation.json).
- [Literal-source and mutation receipt](results/ci-receipt-physical-cover-20261023/physical-source/validation.json).
- [Independent derivation and exact controls](results/ci-receipt-physical-cover-20261023/math-review/derivation-review.json).
- [AI source review](results/ci-receipt-physical-cover-20261023/source-review/review.json).
- [Reproducible visualization](visualizations/skew-physical-cover-binding.png),
  [generator](scripts/visualize_skew_physical_cover.py) and
  [input/output hashes](results/ci-receipt-physical-cover-20261023/visualization.json).

Retained failures include the original CI job log, the first local Lake
installation-detection failure before compilation, the first Lean API/coercion
errors with exact source snapshots, and the derivation agent's missing-SymPy
import before its successful standard-library exact check. No interrupted
calculation or import failure is counted as a result. Bounds were declared
before computation: 90 minutes for the pass, one new lemma, at most two
approaches, 120 seconds per Lean command and 600 seconds per checker.
No successful checker timed out. The figure encodes actual receipts,
coefficients, conditional dependencies and trace values; it cannot establish
the missing physical hypotheses.

Credit benediamond / Benjamin Diamond for the newer physical cover, fqlx /
Ben Burns for the compact architecture and Mathlib contributors for the APIs.
Existing degree-seven credit is retained without recounting. The smallest
remaining dependency is distinct-root data for this literal polynomial over
a specified splitting extension of Q(a,v,t). No rational primitive, global
clearing, HasCertificate or target solve is claimed.

No upstream post, reply, edit or PR. Posts remain entries 1–29. Tally unchanged:
**29 discussion contributions, one closed maintenance PR, zero accepted
authored solves**. The entire earlier ledger is preserved byte-for-byte; this
local append is supplied for the coordinator's integration and publication.

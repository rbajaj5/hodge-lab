# CI receipt repair and one conditional physical-cover binding

> Coordinator integration, 23 October 2026: the Pro handoff below is preserved
> as the record of its work. In its tables, **Root means the Pro chat root**.
> The coordinator independently passed delivery/source/log audits, the literal
> source gate and the non-Lean receipt-lifecycle regression; it reused the
> reported Lean runs. See [integration evidence](../results/ci-receipt-physical-cover-20261023/integration/integration.json).
> Published in [5d21669](https://github.com/rbajaj5/hodge-lab/commit/5d216691981cdb248073209bdc80df86021412d4).
> The complete [Lean CI run 40026828482](https://github.com/rbajaj5/hodge-lab/actions/runs/40026828482)
> passed, including the repaired sequence and new lemma. Downloaded receipts
> were checked against 43 published source files and 28 logs; see the separate
> [remote verification](../results/ci-receipt-physical-cover-20261023/integration/remote-ci/verification.json).
> Historical handoff statements below refer to the earlier local-only stage.

23 October 2026. **Reviewed local handoff; no commit, push, new remote CI run,
or upstream publication by this chat.** The human assigned final Git
publication and ledger integration to the original coordinator. The patch
base is `d29cd55b7c7e738ae84bec7da50c8c843877506d` (checkpoint 136); the live
upstream checkout was pinned at `554757eca1aebecdd1d21f3452d3c71ffa601b19`.
These heads were fetched rather than assumed from the prompt.

The affected forms-to-trace sequence now passes locally without changing
historical result files. One new conditional Lean lemma identifies the literal
physical polynomial with the split polynomial used by the completed basis
proof, **given all eighteen distinct roots**. Separability and descent remain
outside this pass.

![Receipt lifecycle and conditional cover binding](../visualizations/skew-physical-cover-binding.png)

## The selected statement

For any field K, arbitrary a,v in K, and

\[
f(X)=X^{18}+X^{12}+(vX-1)^6-aX^{15},
\]

suppose a tuple rho: Fin 18 -> K is injective and f(rho_j)=0 for every j.
The new theorem proves

\[
f(X)=\prod_{j=0}^{17}(X-\rho_j)
     =\operatorname{coverPolynomial}(1,\rho).
\]

The [Lean module](../formal/HodgeLab/OneReflectionSkew/PhysicalCoverBinding.lean)
is explicit about these hypotheses. Supporting helpers prove that the lower
terms have degree at most 15 and that f has degree 18 and leading coefficient
1. The coordinate a is not the leading coefficient a18. No assumption a!=0
or characteristic zero is required for the conditional theorem.

Only the first declared mathematical approach was used. Each distinct linear
root factor divides f; pairwise coprimality makes their product divide f.
Both polynomials are monic of degree 18, so they agree. The interpolation
fallback was not needed. Helpers and two short trace corollaries support this
one source-binding unit; no second physical-cover problem was undertaken.

The completed [split quotient and trace-free basis proof](skew-trace-basis-lean.md)
is reused. After the literal equality, the derivative-weighted split vectors
have last trace 1 and slot-eleven trace 0. All eighteen components remain
present. The existing quotient theorem supplies the full basis and its
17-dimensional trace kernel under the same root data; this pass does not
repeat that construction or descend it to an unsplit field. Trace zero does
not identify the vector with the physical differential source, make it zero,
or establish exactness.

## Field, chart and physical-source boundary

The intended physical base is k=Q(a,v,t), with independent parameters. To use
the new theorem physically, take a specified splitting extension L/k, map a
and v into L, and establish the required distinct-root tuple there. The theorem
does not assert that the roots lie in k or construct that tuple. Generic
separability, trace-compatible base change and descent have not been proved.

The pinned [Benjamin Diamond / benediamond source comment](https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19129985)
uses the canonical Y0=1 chart. Recovering r=X1/X0 and w=X2/X0 also requires
X0!=0, and v=r^(-1)+r*w requires r!=0. These are the ratio-chart assumptions;
the formal polynomial identity itself has no inverse or chart hypothesis.
The previously checked chart and nine rational identities are historical
context, not new calculations in this pass.

The [source gate](../scripts/check_skew_physical_source.py) compares the literal
Lean definition with the displayed equation in the pinned comment, checks
raw file and comment-body hashes, and compares current versus historical
protected F, A and q. Those three target fields agree exactly. The current
record's rendering metadata is not part of that mathematical comparison.
This establishes source correspondence and unchanged target data; it is not
a new derivation of the cover or the physical differential-source normalization
from the protected sextic.

The source comment body SHA256 remains
`bbebae10b90520c5c3d4c6bd0a4f090c26a13bb5ae2feab45562a6589997b521`.
See the [new immutable manifest](../formal/results/skew-physical-cover/inputs.json),
[source receipt](../results/ci-receipt-physical-cover-20261023/physical-source/validation.json)
and [upstream source pins](../results/ci-receipt-physical-cover-20261023/source-pins.json).

## The CI lifecycle repair

The live [original CI run 39832127430](https://github.com/rbajaj5/hodge-lab/actions/runs/39832127430)
at `0200f4c07e76af3cdd29f45e9078c245c222b28c` failed before trace-basis Lean
compilation. The forms checker passed and rewrote its runtime receipt; the
next checker correctly rejected the changed historical context hash.
The [decoded original job log](../results/ci-receipt-physical-cover-20261023/original-ci-job.log)
and run/job metadata are retained. A source-integrity failure is not a theorem
refutation.

The repair separates immutable HISTORY/inputs from fresh OUT directories in
both affected checkers. The forms receipt still has its original pinned hash:

`29cc594f52a403ca17a46958497aea73fbc099f042ec4d9be962e0ae1b1a1c4c`.

The historical trace receipt also remains byte-identical. No historical
receipt, old input manifest or old proof module was rewritten. The shared
[allocator](../formal/fresh_receipts.py) creates a unique output by default and
refuses existing directories, protected historical paths, descendants and
symlink aliases. All new PASS/FAIL receipts, logs and control snapshots go
to fresh locations. The failure handler cannot overwrite an existing PASS
when allocation is rejected. Original context integrity checks remain;
the trace input manifest is additionally checked before and after execution.

The [lifecycle regression](../formal/test_receipt_lifecycle.py) runs under
Python -O, stops its preflight fixtures explicitly before Lean, and checks
historical corruption, repeated fresh outputs, collisions and aliases.
It is not presented as a simulated proof replay. The actual
[forms-to-trace driver](../scripts/check_skew_ci_sequence.py) subsequently
ran both real checkers and verified **2,862 tracked result files unchanged**.

The workflow now uploads fresh forms/trace/physical outputs under
formal/results/runs, without mixing in the saved forms/trace PASS artifacts.
Earlier workflow checkers still use their pre-existing output locations;
this bounded repair does not claim a migration of every checker. The full
remote workflow has not been rerun by this chat. The coordinator must record
the post-publication run separately.

## Executed checks and attribution

All Lean checks used Lean 4.31.0, commit
`68218e876d2a38b1985b8590fff244a83c321783`, and pinned Mathlib
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`. Python was 3.12.14.
Each checker retained a 120-second process bound and 600-second total budget.

| Check | Executed by | Outcome |
| --- | --- | --- |
| Lifecycle regression | Root, plus implementation agent's earlier focused runs | PASS under -O; corruption rejected before Lean and saved PASS files preserved |
| Actual forms checker | Root | PASS: 13 theorem audits, 1 module replay, 5 positive and 3 expected negative controls; 119.117 s |
| Actual trace-basis checker | Root | PASS: 56 declaration audits, 3 module replays, 7 positive and 3 expected negative controls; 22.223 s |
| New physical-cover checker | Lean implementation agent | PASS: 8 declaration audits, 1 new-module replay, 9 positive and 4 expected false-goal controls; 20.775 s |
| Literal-source gate | Root | PASS: exact source/pin correspondence, F/A/q comparison, 4 rejected definition mutations and 1 checksum-byte control |
| Independent exact polynomial controls | Separate mathematical-derivation agent | PASS using standard-library integer sparse arithmetic, 0.0017 s under 30 s bound |
| Adversarial review | Separate source-review agent | No blocking source defect found; checked saved source/log hashes and exits, without rerunning Lean |

The [affected-sequence receipt](../results/ci-receipt-physical-cover-20261023/sequence-executed/sequence.json)
and [new Lean receipt](../results/ci-receipt-physical-cover-20261023/lean-development/checker-01/validation.json)
contain exact commands, outputs, source hashes and timings. Audited axiom
dependencies are confined to propext, Classical.choice and Quot.sound.
Only the named modules were kernel-replayed; Mathlib and other prior imported
proofs were not newly kernel-replayed. Counts for the old sequence are rechecks
needed for CI repair, not new mathematical results.

The [independent derivation](../results/ci-receipt-physical-cover-20261023/math-review/derivation-review.json)
includes its exact executable Python and coefficient table. The
[source review](../results/ci-receipt-physical-cover-20261023/source-review/review.json),
[checker review](../results/ci-receipt-physical-cover-20261023/source-review/checker-review.json)
and [source-gate review](../results/ci-receipt-physical-cover-20261023/source-review/source-gate-review.json)
distinguish reviewer observations from actual executions. These are separate
AI derivation/review roles, not independent human review.

## Mutation controls and retained failures

The source gate rejects changes to the lower-term sign, exponent, parameter
slot and leading coefficient. This is necessary because changing -aX^15 to
+aX^15 preserves degree and monicity and would not invalidate the generic
root-factorization argument for the incorrectly transcribed polynomial.

At a=2,v=1, exact controls give

\[
f(r)=r^{12}(r^3-1)^2+(r-1)^6,\qquad
f(1)=f'(1)=0,\quad f''(1)=18\quad\text{over Q}.
\]

Thus this specialization has a double root. Taking every rho_j=1 satisfies
all listed root equations but is not injective: f(2)=200705 while
(2-1)^18=1. Conversely, the injective tuple 0,...,17 does not satisfy the root
equations because f(0)=1. These controls justify retaining both hypotheses;
they do not resolve the generic separability question.

Retained unsuccessful attempts are:

- The original remote CI integrity failure, with its full decoded job log.
- The [first local sequence attempt](../results/ci-receipt-physical-cover-20261023/sequence/sequence.json),
  which failed at Lake installation detection before compilation in the
  syscall-restricted environment. The permitted execution route then passed.
- The [first Lean development compilation](../results/ci-receipt-physical-cover-20261023/lean-development/approach1-01.log),
  which had a WithBot degree-coercion issue and a nonexistent API lemma name.
  Exact source snapshots and corrected attempts are retained. This did not
  require a second mathematical approach.
- The derivation agent's [missing-SymPy import](../results/ci-receipt-physical-cover-20261023/math-review/dependency-failure.json),
  which occurred before calculation. Its successful exact check used only
  the Python standard library.

No interrupted calculation or import failure is counted as a mathematical
result. There were no timed-out mathematical runs in the successful checks.
The predeclared pass limit was 90 minutes, one new lemma and at most two
approaches; one approach was used.

## Visualization and reproduction

The [figure generator](../scripts/visualize_skew_physical_cover.py) reads actual
PASS receipts and the exact coefficient table. It displays the historical/fresh
receipt separation, polynomial support, assumed root data, proved binding,
split traces and repeated-root control. The rendered PNG was visually inspected;
the same generator supplies the matching SVG. The
[generation receipt](../results/ci-receipt-physical-cover-20261023/visualization.json)
records input, script and output hashes. The figure is not independent proof
evidence and does not sample physical roots or establish missing hypotheses.

From a patched checkout, with the pinned Lean toolchain and Mathlib cache:

```sh
cd formal
lake exe cache get
cd ..
python3 scripts/check_skew_ci_sequence.py /tmp/hodge-fresh-ci-sequence
python3 -O scripts/check_skew_physical_source.py --output-dir /tmp/hodge-fresh-source
cd formal
python3 -O check_skew_physical_cover.py --output-dir /tmp/hodge-fresh-physical
cd ..
python3 -B scripts/visualize_skew_physical_cover.py
```

All three output directories must be new. These are reproduction commands,
not an instruction to repeat the already accepted local sequence during the
handoff. The source and proof checkers fail closed under -O.

Credit Benjamin Diamond / benediamond for the newer literal physical cover,
fqlx / Ben Burns for the compact connection/source architecture, and Mathlib
contributors for the polynomial, trace and basis APIs. Existing credited
degree-seven contributions remain historical and are not counted again.

**Smallest remaining dependency:** establish the required distinct-root data
for this literal polynomial over a specified splitting extension of Q(a,v,t).
Trace-compatible descent and physical differential-source normalization remain
separate later obligations. No rational primitive, global clearing,
HasCertificate or target solve is claimed. No upstream post, reply, edit or
PR occurred. Posts stay 1–29; tally unchanged: 29 discussion contributions,
one closed maintenance PR, zero accepted authored solves.

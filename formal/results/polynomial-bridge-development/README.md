# Polynomial bridge development record

These are local compilation attempts, not the final independent replay receipt.
The [index](index.json) binds every command record, log, and retained source
snapshot. All attempts have an explicit 60-, 120-, or 180-second inner bound.
Wall-clock timings include process startup; the two timeout exits are 124.

| Attempt | Outcome | What it established or changed |
| --- | --- | --- |
| `sparse-01` | Failed | Native compiler could not find a cached mathlib module. |
| `sparse-02` | Failed | Two induction proofs needed their hypotheses unfolded. |
| `sparse-03` | Passed | Initial sparse-list operations interpreted as `MvPolynomial`. |
| `case05-01` | Failed | Ordinary `decide` stopped at opaque rational arithmetic. |
| `coefficient-probe-01` | Failed | A single coefficient exceeded the default recursion limit. |
| `coefficient-probe-02` | Passed | Kernel reduction checked one coefficient with an explicit recursion bound. |
| `case05-02` | Timed out | Full coefficient check, before sparse evaluator optimizations. |
| `sparse-04` | Passed | Skipping rational zero additions preserved coefficient semantics. |
| `case05-03` | Timed out | Zero-addition optimization alone did not finish within 180 seconds. |
| `sparse-05` | Passed | Dropping zero derivative terms preserved derivative semantics. |
| `case05-04` | Passed, 79.76 s | All 352 coefficient checks, polynomial formulas, matrix implication, and rational no-solution theorem compiled. |
| `field-01` | Failed | Scalar extension needed the explicit coefficient-map rewrite. |
| `field-02` | Passed, 3.76 s | The mapped-polynomial obstruction compiled over every characteristic-zero field. |
| `negative-coefficient-01` | Rejected | Altered scale `49/2401` failed its claimed coefficient equality. |
| `negative-coefficient-negation` | Passed | The kernel proved the exact negation of that altered equality. |

The last two entries deliberately distinguish rejection from proof of falsity:
the rejected goal's diagnostic reports unsuccessful decidable reduction, while
the separate negation compiles successfully. Both source snapshots are retained.

Each record contains its actual command. On the pinned Linux project, a source
can be checked with `lake env lean -o <output.olean> <module.lean>` and the listed
timeout. Historical snapshots must be restored together with the indicated
`SparsePolynomial` dependency in an isolated copy; do not overwrite the current
proved sources. Three early diagnostic records lack their original source bytes
and are explicitly marked as such in the index. Matching later snapshots were
attached only after their hashes were checked against the original records.

No source simplification changed the mathematical operator. The proved sparse
semantics connect multiplication and differentiation to `MvPolynomial`; the
final coefficient checks use kernel reduction. Source identification and the
listed raw correction columns are independently audited in Python; covering
every normalized certificate numerator remains a separate mathematical obligation.
The fresh build, declaration-dependency audit, standalone replay, and full
mutated-module controls are recorded by `formal/check_polynomial_bridge.py`.

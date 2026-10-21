# Substantive repository audit — 21 October 2026

This pass found a wrong ideal identification and several claims exceeding their
recorded checks. It corrected Hodge Lab only. No upstream comment, reply, edit,
issue, PR, or verification workflow was submitted.

## Pinned scope and live evidence

- Hodge Lab starting head: [`09539bb5151f918f73ec9fd4b9faba781959c436`](https://github.com/rbajaj5/hodge-lab/tree/09539bb5151f918f73ec9fd4b9faba781959c436), freshly fetched from `origin/main`.
- Upstream observed head: [`dda4c5e72eeea8cfd52dd6e731e90031884f32fc`](https://github.com/hodge-computer/sextics/tree/dda4c5e72eeea8cfd52dd6e731e90031884f32fc). GitHub API observations were made through 15:43 UTC. Two Git fetches, including a depth-one attempt, failed with connection-reset / early-EOF errors; the pinned API files were obtained successfully and checked against their Git blob hashes. This is a documented retrieval limit, not an assertion that the old local upstream checkout was current.
- The complete 14-discussion snapshot at 15:08 UTC covered #44, #55, #56, #111–120 and #127, including all reply pages. All 47 records were unchanged from the 13:50 snapshot. The current [post 25](https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19049585) already uses the correct Hessian scale, calls the exchange an involution, and limits the coefficient-vanishing interpretation. The notebook had not propagated those corrections.
- Three independent read-only review assignments covered repository integrity, formal verification scope, and skew-instance mathematics. One writer made the changes in an isolated worktree. The earlier unfinished rank-proof work and user changes in other checkouts were preserved.

Evidence: [upstream records and requests](../results/repository-audit-20261021/upstream-review.json),
[formal review](../results/repository-audit-20261021/formal-review.json),
[pre-correction mathematical counterchecks](../results/repository-audit-20261021/audit_skew_checks.json),
[commands and final validation](../results/repository-audit-20261021/validation.json).

## Findings and corrections

### A1. `P_Hess` was a different ideal — incorrect identification

**Claim and source.** At the starting head,
[`canonical_quadrics`, line 97](https://github.com/rbajaj5/hodge-lab/blob/09539bb5151f918f73ec9fd4b9faba781959c436/experiments/one_reflection_skew_koszul_homology.py#L97)
called `(Q_node/9,Q_Kramers,Q_bridge,Q3)` the four pure-Hessian modes. The corresponding note, table and picture interpreted its homology as that of the physical Hessian rowspace.

**Evidence.** The saved degree-six residual packet has 49 relevant physical rows,
of rank four. The claimed four generators also have rank four, but their joint
span has rank five. At `(a0,a1,a2,a3,a4)=(1,1,1,1,1)`, every physical row vanishes
while `Q3=5/4`. Thus this is an actual mismatch of zero loci, not merely an
unproved change of basis. Identical sampled Hilbert functions concealed it.

**Correction.** Replace `Q3` by `Q_anchor`. The new independent standard-library
[checker](../experiments/check_one_reflection_skew_hessian.py) reconstructs the 49
rows from the saved packet and verifies explicit linear combinations in both
directions. It also rejects the old `Q3` identification. The corrected finite
complexes still give `H0=(11,15,16,16,16)` and zero positive homology in degrees
2–6. The producer now runs this source-space guard before its calculation.

**Consequence and boundary.** The physical interpretation is repaired. This
audit did not reconstruct the 49 rows from the original sextic; it checked their
saved packet and its hash. This error does not by itself refute the separate
full-E2 degree-six exclusion, which uses nine quadrics and its own witnesses.

### A2. Finite strands were used as an all-degree proof — missing proof obligation

**Claim and source.** The
[`P_Hess` regularity paragraph, line 41](https://github.com/rbajaj5/hodge-lab/blob/09539bb5151f918f73ec9fd4b9faba781959c436/notes/one-reflection-skew-koszul-homology.md#L41)
invoked the regular-sequence criterion from vanishing in degrees 2–6. The
twisted-Euler section similarly promoted three computed degrees to regularity.

**Evidence and correction.** Finite samples alone do not supply the all-degree
criterion. For corrected `P_Hess`, we supplied a separate height certificate:
after setting `a4=0`, a degree-five 56×80 Macaulay matrix has rational rank 56,
and a selected minor is 6 modulo 101. All denominator reductions are legal.
Consequently the four quadrics together with `a4` form a homogeneous system of
parameters. Cohen–Macaulayness of the polynomial ring gives a regular sequence;
the resulting Hilbert series is `(1+t)^4/(1-t)`. See the
[exact certificate and argument](../results/repository-audit-20261021/corrected-hessian-validation.json)
and [Stacks, Cohen–Macaulay rings](https://stacks.math.columbia.edu/tag/00N7).

The five twisted-Euler ideals are now described only by their computed
degree 2–4 profiles. Their analogous all-degree proof remains unexecuted here.
A missing proof obligation is not a counterexample to regularity.

The degree-seven note also needed a parameter-space qualification: its rank 44
calculation spans quadratic coefficient columns, not arbitrary values of the
nonlinear parameter map. The first equation splits across characters; the
quadratic second equation can couple them. The note now explicitly limits the
exclusions to pure-character sectors, matching the current
[upstream post 27](https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19052407).
Its historical figure is retained with an adjacent qualification; no full
degree-seven elimination was rerun.

### A3. Figure values and verification counts exceeded the output — incorrect display

**Claim and source.** The old
[figure table](https://github.com/rbajaj5/hodge-lab/blob/09539bb5151f918f73ec9fd4b9faba781959c436/experiments/one_reflection_skew_koszul_homology.py#L398)
displayed zero added-block `H1` through degree 5 even though its summary only
reported degree 2. It also extended the twisted-Euler profile to degree 5.
The footer and note said 26 complexes / 709 composition columns; the committed
summary actually recorded 39 / 664.

**Correction and consequence.** Uncomputed entries are dashes, and inherited
added-block data are labeled as such. The counts are generated from the actual
run. As a concrete diagnostic, the ideal generated by all 28 quadrics in seven
variables has `H1` dimension 112 in degree 3, not zero: `196-84=112`, since
`K2,3=0`. This abstract full-quadratic model was checked independently; it is
not a fresh reconstruction of the physical added block. The corrected figure
no longer asserts its uncomputed higher-degree homology.

### A4. Pilot normalization, symmetry order and degeneration — incorrect claims

**Claims and source.** The
[pilot note](https://github.com/rbajaj5/hodge-lab/blob/09539bb5151f918f73ec9fd4b9faba781959c436/notes/one-reflection-skew-pilot.md#L44)
printed `h=det(Hess(f))/36`, called `(Y0,Y1) ↦ (iY1,-iY0)` order four, and inferred
flow degeneration along `X1Y1=0` from a vanishing Cramer coefficient/resultant.

**Evidence.** Direct symbolic expansion gives `det(Hess(f))=4h`. The exchange
squares to the identity and is not a symmetry of the full sextic. Both `c1,c2`
have a factor `beta`, so their resultant is identically zero for all `r,w`.
At the valid chart point `r=w=beta=0`, `h=9uv`, `disc(h)=81`, and
`H=9u∂u−9v∂v`, although `L_h=0`. This is a counterexample to the claimed
degeneracy of that locus.

**Correction.** Fix the factor to 1/4, describe the interaction involution
correctly, and retain only the established coefficient-vanishing observation.
New assertions test these facts and the existing universal Cramer/Cayley
identities. The pilot figure and symbolic receipt were refreshed. Its expensive
low-degree elimination and smoothness portions were inherited unchanged and
are explicitly marked as not replayed. No global transport obstruction follows.

### A5. The line checker did not enforce its result — verification defect

**Claim and source.** Checkpoint 103 links the
[line checker](https://github.com/rbajaj5/hodge-lab/blob/09539bb5151f918f73ec9fd4b9faba781959c436/experiments/check_one_reflection_skew_line.py#L59).
Changing `X2=6s+2t` to `5s+2t` made it print nonzero incidence coefficients and
`All zero? False`, yet exit successfully.

**Correction.** Required incidence and fixed source-restriction failures now
raise `ValueError`. The valid input passes, and separate line/source mutations
fail with nonzero exit codes even under Python `-O`. This is an enforcement
defect; the valid line's earlier substitution result was not false. No matrix
rank or characteristic-zero conclusion is added by this fix.

### A6. Lean coverage was conflated — incorrect summary, not a false theorem

**Claim and source.** The
[ledger dashboard, line 16](https://github.com/rbajaj5/hodge-lab/blob/09539bb5151f918f73ec9fd4b9faba781959c436/LEDGER.md#L16)
said “16-module polynomial-to-matrix Lean 4 bridge.”

**Evidence and correction.** Sixteen fixed candidates have literal-matrix
certificates in 17 modules. Only Case05 has the five-module polynomial-to-matrix
bridge. The separate Lean 4.33 compatibility run covered two proposed
maintenance modules, not the entire Lean 4.31 notebook. The dashboard now says
this explicitly. Detailed README/formal documentation was already appropriately
scoped. The polynomial normalization and correction-space completeness remain
outside those Lean theorems.

The independently replayed Case05 arithmetic checked 352 coefficients,
525 raw Koszul and 636 quotient columns, pairing −5, and nine arithmetic mutations.
Source-scope checks and all reviewed source/log bindings passed. There was no
fresh Lean compilation or kernel replay in this audit. A fresh sixteen-minor
reconstruction exceeded its 60-second bound and produced no result; it is not
counted as a pass or a refutation. [Detailed commands and hashes](../results/repository-audit-20261021/formal-review.json).

### A7. Publication descriptions needed dating — superseded statuses

Current pinned upstream records give **82 targets, 65 solved, 17 open**. PR #178
added four open targets relative to `f247a366`. The older README 78/64/14 and
feedback-note 78/63/15 counts were correct at their cited commits. The README
now uses the live snapshot; the historical feedback note has a later-status
notice. Mixed-biweight is accepted/published, credited to `fqlx`; cycle-three
is credited to `hodgepodgeconjecture`; holdout-moving-branch to `benediamond`.
One-reflection-skew and cycle-q2 remain open. PR #121 is closed and unmerged,
so its “ready for review” wording was updated.

We inspected acceptance/publication records, verified fetched blob hashes, and
compared recorded attribution. We did not independently replay upstream Lean
proofs or audit their mathematical completeness. Successful protected checking,
accepted publication, and our own replay are separate evidence levels. This pass
adds no upstream contribution and no accepted authored solve.

### A8. Ledger encoding repair already held — no new corruption found

The 205 repaired lines exactly recover the earlier UTF-8 text. The repair receipt
hashes match, checkpoint 103 was preserved, and older truncations were repaired
before this audit. All 1,180 tracked text files decoded as UTF-8; all tracked JSON
parsed. Checkpoints 1–105 occurred exactly once. Scanning 799 local Markdown
targets found no confirmed missing notebook file; one link requires the declared
submodule. An archived website-route fragment was not treated as a broken anchor.

We moved checkpoint 103 before 104 without altering either entry's text or
renumbering anything, and appended 106. The current dashboard was corrected;
numbered historical statements remain historical and are superseded explicitly
by this note. No old ledger snapshot replaced the current ledger. See
[integrity scan](../results/repository-audit-20261021/tracked-text-integrity-scan.json)
and [history comparison](../results/repository-audit-20261021/ledger-history-audit.json).

## Reproduce the corrections and pictures

```sh
python -S experiments/check_one_reflection_skew_hessian.py
python experiments/check_repository_audit_20261021.py
python -S results/repository-audit-20261021/check_integrity.py
```

The first command uses only the standard library. The second needs the existing
plotting dependencies and refreshes the focused outputs. It does not access
GitHub or rerun Lean/full eliminations. Versions, command bounds, outputs and
hashes are in [validation.json](../results/repository-audit-20261021/validation.json).
The third command checks saved source/output/log bindings, UTF-8 and JSON,
local links in changed Markdown, preservation of all 105 historical checkpoints,
and rejection of optimized Python execution by the two new assertion-based
checkers. It also checks that the inherited pilot elimination and smoothness
sections are unchanged. [Final integrity receipt](../results/repository-audit-20261021/final-integrity.json).
The initial audit harness matched both a comment and the source assignment in
its source-mutation test; that harness failure is preserved under
`results/repository-audit-20261021/failures/first-run/` and was repaired by using
an exact line-boundary match. It was not a mathematical failure.
The first integrity-helper run also confused the separately numbered Posts and
Research sections. Its [failure record](../results/repository-audit-20261021/failures/integrity-first-run.json)
is preserved; the corrected check isolates the research checkpoints and separately
compares the entire historical Posts/Pull requests block.

![Corrected finite-strand comparison and reported-vs-computed boundaries](../results/one-reflection-skew-koszul/one-reflection-skew-koszul-homology.png)

![Corrected binary-cubic boundary interpretation](../results/one-reflection-skew-pilot/one-reflection-skew-audit.png)

This is one focused pass, not a repository-wide mathematical certification.
The formal bridge's stated completeness gap, uncomputed twisted-Euler degrees,
physical added-block reconstruction, expensive elimination replays, and upstream
proof replay remain outside it. Future upstream publication still requires its
own prior Hodge Lab ledger audit.

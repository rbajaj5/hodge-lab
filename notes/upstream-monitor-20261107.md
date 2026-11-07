# Upstream monitor — 7 November 2026

**Snapshot: 03:48 UTC. Bounded status maintenance; no mathematical replay.**
Upstream is pinned at [`2d60d08d25fba3e02162b39d4c50f6b467e7f506`](https://github.com/hodge-computer/sextics/tree/2d60d08d25fba3e02162b39d4c50f6b467e7f506),
38 commits after the preceding repository baseline `83fbf5c9a0afe9136ce4f1ed324d085a2c899bd0`.
Hodge Lab's parent is `c47dcb477ba394666e57bcd653ec89a6c8da86a5`.
The catalogue still has **82 fixed targets, 66 accepted submissions and 16 without
accepted submissions**. That last count describes publication status, not a claim
that mathematical existence is unknown for every remaining target.

## Acceptance records and the current certificate contract

All 66 `acceptance.json` files changed from schema 1 to schema 2. We compared
every pair: contributor login, original PR number/URL and acceptance timestamp
are identical. Each new receipt is exactly those historical fields plus
`schemaVersion: 2`. The old receipts all had outer `formalAcceptance: true`.
No acceptance file was added or removed; all pinned `instance.rec`, `proof.json`
and `record.json` blobs are unchanged. This is a receipt migration, **not 66
new solves or a loss of the existing acceptance attribution**.

The [current maintenance policy](https://github.com/hodge-computer/sextics/blob/2d60d08d25fba3e02162b39d4c50f6b467e7f506/MAINTAINING.md)
separates original contributor credit from maintained proof sources. New compact
receipts omit source/verifier hashes, workflow-run details and verification
claims. Maintained sources are checked through Repository build; the publication
workflow no longer uses the earlier CI-artifact/merge-parent receipt procedure.
An old protected-check receipt authenticates its historical source and scope;
it does not authenticate a subsequently refactored proof. Our before/after
captures preserve the historical evidence. We did **not** run Lean or establish
the current branch's CI result.

The [formal contract](https://github.com/hodge-computer/sextics/blob/2d60d08d25fba3e02162b39d4c50f6b467e7f506/formal/README.md)
now handles general dimension, hypersurface degree and pole parameter, with
integer grading; `HasCertificate F q A` infers the dimension and `F.totalDegree`.
The sextic catalogue remains the dimension-five, degree-six specialization.
Upstream moved Lean 4.33.0 to 4.33.1, migrated accepted proofs, extracted shared
certificate constructions, added a technique guide and Apache-2.0 licensing,
and revised the book's support constructions. These are upstream source and
policy changes, not locally executed proof checks. Historical notebook receipts
retain their original toolchain and meaning.

## Changed existence context: #120 and #117

The current pinned provenance for
[`four-plus-two-residual`](https://github.com/hodge-computer/sextics/blob/2d60d08d25fba3e02162b39d4c50f6b467e7f506/data/four-plus-two-residual/provenance.json)
and [`symmetric-sextic-residual`](https://github.com/hodge-computer/sextics/blob/2d60d08d25fba3e02162b39d4c50f6b467e7f506/data/symmetric-sextic-residual/provenance.json)
now says certificate existence follows from the book's two-reflection support
theorem. This supersedes their earlier upstream wording that existence was not
established. We record this as a **maintainer/book assertion**, without verifying
the theorem. Neither target has a published acceptance receipt at this pin.

In [#120, comment 19448881](https://github.com/hodge-computer/sextics/discussions/120#discussioncomment-19448881),
benediamond / Benjamin Diamond reports a contact family on the fixed weighted
core spanning its full anti-invariant third cohomology. The report describes a
48-dimensional span, closed Abel–Jacobi differentials and a finite trace problem.
Its parameter curve is distinct from the genus-four curves moving on the core.
The author explicitly supplies **neither a `HasCertificate` proof nor a displayed
rational vector field**. The polarization operator and global trace have not
been computed; the raw traced source has not been shown literally equal to
`(0,0,1)`. Closedness prevents arbitrary parameter-dependent coefficients.

The attached packet's reported Lean checks cover a finite inverse identity and
conditional suspension conversion. They do not formalize the geometric lifting,
support interpretation or a missing primitive. We did not download/replay the
packet. The [edited earlier Prym comment](https://github.com/hodge-computer/sextics/discussions/120#discussioncomment-19150610)
preserves its character calculation but updates the missing-support conclusion.
Our 23 October note remains historical: the residual Prym diagnosis is no
longer an up-to-date assertion that serving support has not been supplied.

For #117 the book applies two reflections after a rational coordinate change.
The newer provenance is separate from kejace's earlier denominator exclusions
and sector correction below. For
[`quadratic-cubic-pullback`](https://github.com/hodge-computer/sextics/blob/2d60d08d25fba3e02162b39d4c50f6b467e7f506/data/quadratic-cubic-pullback/provenance.json),
the revised context still supplies **no certificate or existence conclusion**:
the new ternary-net theorem's factorization is not implied by six quadrics mixing
both coordinate blocks. Likewise, the cyclic-six theorem does not settle
`one-reflection-skew` or the different higher-pole target `cycle-q2`.

## New exclusion reports and explicit corrections

The following are **author-reported results**, not calculations executed here.
kejace / Kristoffer Josefsson discloses Claude assistance, separate AI-agent
implementations, no human review, no Lean verification and no certificate.
His word “refereed” does not establish independent human review. Linked packets
were not downloaded or verified in this monitor.

| Discussion and permanent source | Reported scope | Remaining limit or correction |
| --- | --- | --- |
| [#115: kejace, 19345491](https://github.com/hodge-computer/sextics/discussions/115#discussioncomment-19345491) | Replicates 1337isnot1337's full-target lower bound `deg D ≥ 8`; reports no degree-at-most-six denominator for the K3-sector class alone. | The referee did not rerun the full degree-seven step. Further reducible-support conclusions depend on stated Hodge/Picard hypotheses; K3 degree seven and broader degree-eight families remain open. |
| [#116: kejace, 19345484](https://github.com/hodge-computer/sextics/discussions/116#discussioncomment-19345484) | Reports `deg D ≥ 7` and exclusion of 13 of 14 pure-parity, character-eigen degree-seven sectors. | The odd, character-zero sector is screened rather than proved; mixed sectors and general higher degrees remain outside the result. |
| [#116: benediamond, 19360045](https://github.com/hodge-computer/sextics/discussions/116#discussioncomment-19360045) | Reports vanishing of the required nontrivial character for the ordinary cubic-surface-line correspondence, including a global boundary calculation. | Excludes this correspondence, not all curves or certificates. ChatGPT-assisted; no Lean verification claimed. Earlier fqlx constructions retain their own scope. |
| [#117: kejace, 19345502](https://github.com/hodge-computer/sextics/discussions/117#discussioncomment-19345502) | Reports `deg D ≥ 7`, exclusion of semi-invariant denominators of degrees seven/eight, and six fixed-denominator dual certificates. | Corrects his earlier local sector `(1,10,1)` to target-sector Hodge numbers `(17,52,17)`; the former describes the residue-trivial sector. General degree seven and non-semi-invariant higher degrees are not closed. Newer book existence claims above do not contradict bounded exclusions. |
| [#118: kejace, 19345496](https://github.com/hodge-computer/sextics/discussions/118#discussioncomment-19345496) | Reports exact exclusion of all `deg D ≤ 6`, including mixed parity and arbitrary quotient. | Degree seven remains open; a timed-out modular relaxation is not an exclusion. This is complementary to fqlx's scoped geometric obstructions. |
| [#120: kejace, 19345483](https://github.com/hodge-computer/sextics/discussions/120#discussioncomment-19345483) | Reports `deg D ≥ 6`, degree-six Jacobian eigenvector exclusions and selected fixed-denominator failures. | The general 69-parameter sextic family and mixtures remain outside the result. The post's earlier missing-support wording predates the book/contact-family update. |
| [#127: kejace, 19345488](https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19345488) | Reports further implementations of rbajaj5's degree-at-most-six exclusions, fqlx's odd degree-seven exclusion, and a strict five-variable reduction attributed to fringewidth's earlier formulation. | **Withdraws an internal inference that leading-ideal pure powers force solutions onto one coordinate axis.** The stated even-sector relaxations yield finite projective sets, not closed classes; their points remain unidentified. fqlx's separate closure claim was not replayed. Mixtures and higher degrees remain open. |

The #127 correction concerns kejace's internal reading, not a withdrawal of our
completed Hessian reconstruction or rank correction. His citation of our existing
work adds no new notebook result or contribution tally. We retain all earlier
receipts and exclusions with their original stated bounds.

## Edited summaries and attribution

Benjamin Diamond edited [#44 comment 19003085](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-19003085)
and [comment 19044549](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-19044549)
to replace stale open-target wording with fqlx's already accepted PR128 and its
target extensions, while describing the book's cyclic-six family support.
Restricted degree-seven exclusions and quotient-character limitations remain
restricted; the retained credits to rbajaj5 and other contributors are not new.

The edited [#112 comment 19044552](https://github.com/hodge-computer/sextics/discussions/112#discussioncomment-19044552)
now explains how rbajaj5's free curve/normal-map input enters the already accepted
PR153 construction, with fqlx's moving-family/descent machinery and HeadOfNaps's
finite-algebra background credited separately. The isolated curve is not the
whole certificate. This clarification is not a new solve or new authorship for
rbajaj5; PR153's recorded accepting contributor remains benediamond.

## Executed monitoring and saved evidence

We used `work/read_hodge_discussions.py` with pagination, explicit UTF-8 and
bounded requests, then compared stable IDs, authors, timestamps and body SHA256.
All 14 required discussions were collected: **47 top-level comments, 20 replies**.
There are **eight new comments, four edited comments, no deleted records**, and
six changed discussion update timestamps. All changed records are top-level
comments; no replies changed. The comparison against the last complete discussion
baseline (1 November, 11:18 UTC) catches edits even when thread timestamps stay
unchanged. The intervening failed collection did not replace that baseline.

The separate repository baseline records complete target/policy pins: **94 of
383 changed** (66 acceptance, 20 context, three provenance, five policy files).
The API's commit comparison contains all 38 commits but its 300-file path list
is capped; we do not claim that list is exhaustive. Target/policy comparisons
use complete-tree blob pins, and all 178 changed-data before/after blobs were
checked against their Git object IDs. Generated `data/index.json` and
`data/credits.json` are absent at both source pins; the collector's optional-file
assumption was corrected after all required data had been captured.

Evidence: [comparison](../results/upstream-monitor-20261107/comparison.json),
[receipt continuity](../results/upstream-monitor-20261107/acceptance-review.json),
[discussion review](../results/upstream-monitor-20261107/discussion-review.json),
[policy/context review](../results/upstream-monitor-20261107/policy-review.json),
[source/hash manifest](../results/upstream-monitor-20261107/review.json).
These checks establish what changed and what was reported; they do not verify
mathematical claims, replay protected checks, or establish new acceptance.

No upstream post, reply, edit, message or PR occurred. The source-to-Hessian work
stays complete; conic-pencil/flex-cover drafts and the unpublished #61 attempt
were not reopened. Ordinary maintenance requires no research visualization.
Posts 1–30 and the tally remain **30 discussion contributions, one closed
maintenance PR, zero accepted authored solves**.

# Mixed-polar acceptance: bounded monitoring update

**Snapshot:** 22 October 2026, 00:08 UTC (21 October, 8:08 p.m. EDT).

**Notebook parent:** `d76a73a8de1b37e12051f1ea919e1ebfc6d8fecc`.

**Upstream comparison:** `a6b4cc49452abe31ead0be71d04e8146639896d9` to
[`84f106e`](https://github.com/hodge-computer/sextics/commit/84f106ebf0731cbee1926833236361cddac0fc3f).

## New acceptance and its scope

`mixed-polar` is accepted through [PR #182](https://github.com/hodge-computer/sextics/pull/182),
credited to **benediamond**. The live PR API confirms the owner merge at
2026-10-22T00:03:34Z. Proposal head `02796bf16efe274ffac4dc29aba3805793ce7a29`
was checked against base `a6b4cc49452abe31ead0be71d04e8146639896d9`; the merge is
`bc29abbedb88e9222d329220580bbfdaf04bed55`.

The [pinned acceptance receipt](https://github.com/hodge-computer/sextics/blob/84f106ebf0731cbee1926833236361cddac0fc3f/data/mixed-polar/acceptance.json)
records protected compilation, kernel replay and the exact-target axiom audit
with Lean 4.33.0 in [run 39691712892](https://github.com/hodge-computer/sextics/actions/runs/39691712892).
Its nested check has `formalAcceptance: false` and `lean-checked-awaiting-owner`;
the subsequent owner merge supplies the outer `formalAcceptance: true`.
These are successive verification and publication stages, not a contradiction.
**This monitor inspected those records; it did not execute their proof checks.**

The [accepted explanation](https://github.com/hodge-computer/sextics/blob/84f106ebf0731cbee1926833236361cddac0fc3f/data/mixed-polar/solution.md)
exports an existential certificate. `witnessChecked` is false and the available
witness is Lean source; no expanded polynomial witness or denominator-degree
bound is exported. The explanation credits the cycle-three architecture,
fqlx's constructions and maintained shared machinery. This is not an authored
solve or new solve attribution for rbajaj5. No application of its transport
identities to one-reflection-skew was checked here.

## Repository and discussion checks actually performed

- Read-only REST queries pinned both repository heads, four new commits,
  the complete upstream tree, the PR merge and the acceptance/solution metadata.
  The changed paths contain the mixed-polar proof and publication records;
  no verifier or policy file changed. The protected instance files have unchanged
  Git blob identities, and the mixed-polar record diff changes status and
  publication metadata rather than its polynomial/source triple.
- The [pinned catalogue](https://github.com/hodge-computer/sextics/blob/84f106ebf0731cbee1926833236361cddac0fc3f/data/index.json)
  has **82 targets: 66 solved, 16 open**. `one-reflection-skew` and `cycle-q2`
  remain open. The historical status snapshots remain intact.
- Fetched all comment and reply pages for #44, #55, #56, #111–120 and #127;
  compared IDs, timestamps and body hashes with the previous full monitor.
  The only added IDs are fqlx's [19108825](https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19108825)
  and our [19111234](https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19111234).
  Both are already recorded in checkpoints 119/120, including the latest Lean
  addendum. They are not new contributions or new credit in this update.
- Corrected README's stale tally from 28 to **29**, matching the existing ledger.
  Monitoring, this correction and receiving credit do not increment the tally.

[Monitoring receipt](../results/upstream-monitor-20261022/monitor-receipt.json)
records commands, versions, limits, complete page counts, source hashes and
the comparison. [Acceptance capture](../results/upstream-monitor-20261022/acceptance-capture.json)
pins downloaded bytes; the upstream [acceptance](../results/upstream-monitor-20261022/acceptance.json),
[proof metadata](../results/upstream-monitor-20261022/proof.json) and
[solution metadata](../results/upstream-monitor-20261022/solution.json) are saved verbatim.
Full discussion snapshots and the separate repository-head baseline are retained
in the local `work/discussion-monitor` archive. Network requests were limited to
45 seconds each; the discussion run had a 240-second budget and completed in
6.827 seconds. A reviewer console-encoding failure was corrected once; no access
failure, timeout or authentication loop occurred.

No mathematical replay, upstream publication or discussion edit was performed.
This is ordinary status maintenance, not a substantive research batch requiring
a new visualization. Contribution tally stays **29 discussion contributions,
one closed maintenance PR, zero accepted authored solves**.

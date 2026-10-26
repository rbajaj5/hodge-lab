# Split ternaries: historical discussion clarified after acceptance

Snapshot: **26 October 2026, 15:27 UTC / 11:27 EDT**. Bounded status
maintenance; no mathematical or Lean replay. Hodge Lab parent:
`8a43e161eff1b24dbf1c62ff16967a90d42b3158`; upstream:
`27f4bb9ad8757e5841f884d9d30124a3c97a847d`.

Kristoffer Josefsson (`kejace`) edited [comment 19029838 in #113](https://github.com/hodge-computer/sextics/discussions/113#discussioncomment-19029838)
at **14:40:14 UTC on 26 October**, adding a dated status paragraph. It
credits **fqlx / Ben Burns** for the accepted `split-ternary-q2` existence
proof in [PR #159](https://github.com/hodge-computer/sextics/pull/159), using
companion curves and higher residues. The entire earlier body is preserved
unchanged after the new paragraph.

The clarification separates kejace's earlier small-denominator calculations,
prepared with Codex assistance, from fqlx's accepted existence proof. The
earlier finite-field observations and their limits remain historical claims;
we did not replay them. The old statements about no Lean proof being claimed
or available refer to that earlier work, not the current accepted status.
The accepted existence result does not supply an expanded witness or a
numerical degree bound here; the earlier calculations are not its proof.

## Published acceptance, already recorded

The [revision-pinned acceptance receipt](https://github.com/hodge-computer/sextics/blob/27f4bb9ad8757e5841f884d9d30124a3c97a847d/data/split-ternary-q2/acceptance.json)
has outer `formalAcceptance=true`, credited to fqlx, with acceptance on
**20 October at 20:26:11 UTC** and publication at **20:26:37 UTC**.
The embedded protected-verification receipt records `kernelReplay=true` and
`witnessChecked=false`. Its earlier `formalAcceptance=false` and
`lean-checked-awaiting-owner` describe the pre-merge check; the outer receipt
records subsequent owner merge and published acceptance. We read this receipt
and matched its Git blob hash, but did not execute that verifier or Lean.

[Ledger entry 97](../LEDGER.md) already recorded this acceptance on 20 October.
This edit is a historical-status clarification, not a new solve, new
acceptance, or new credit for Hodge Lab. Previous shared-construction credits
remain as recorded there.

## Monitoring evidence and limits

All pages of #44, #55, #56, #111–120 and #127 were compared by record ID,
timestamps, author and UTF-8 body hash: 14 threads, 39 comments, 20 replies.
Exactly one comment body and its update timestamp changed; no comment/reply
was added or removed. The discussion-level update timestamp did not change,
so the comment-level comparison detected this edit. All other records,
both repository heads, and all 383 target/policy pins are unchanged.

[Before/after comparison](../results/split-ternary-monitor-20261026/comparison.json),
[current thread](../results/split-ternary-monitor-20261026/discussion-113.md),
[captured acceptance receipt](../results/split-ternary-monitor-20261026/acceptance.json)
and [review receipt](../results/split-ternary-monitor-20261026/review.json)
preserve the sources. A separate read-only agent confirmed the exact old-body
suffix and attribution limits. Each request was bounded to 45 seconds and
discussion collection to 240 seconds; no access failure or timeout occurred.

No mathematics, proof packet, Lean/kernel or certificate replay was run.
This maintenance adds no research visualization. No upstream post, reply,
edit or PR occurred. Posts 1–30 and the tally remain **30 discussion
contributions, one closed maintenance PR, zero accepted authored solves**.
README's accepted/open snapshot is unchanged because acceptance did not change.

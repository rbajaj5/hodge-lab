# Catalogue migration and four-plus-two character report

Snapshot: **23 October 2026, 21:44 UTC / 17:44 EDT**. Notebook parent
`69616138811d9f951d586049bd7f6407bea2c4f5`; upstream advanced from
`554757eca1aebecdd1d21f3452d3c71ffa601b19` to
[`4a8e09b`](https://github.com/hodge-computer/sextics/commit/4a8e09b6002d250094cb1c1152a6026c55030ead).
This is bounded monitoring and status maintenance, with no research replay.

## New report in discussion 120

Benjamin Diamond (`benediamond`) posted
[comment 19150610](https://github.com/hodge-computer/sextics/discussions/120#discussioncomment-19150610)
at 17:11:49 UTC. We read the complete thread and saved the
[full context](../results/catalogue-monitor-20261023/discussion-120.md),
including its original source pins. The author reports that the binary
triple cover for `four-plus-two-residual` has genus four, with a
three-dimensional anti-invariant Prym of order-three signature (2,1),
up to embedding order. Its visible elliptic quotient lies in the invariant
sector, whereas the specified residue uses the anti-invariant sector.
Thus that projection is reported to miss the required binary source.

The post identifies the binary holomorphic character line as `dt/w`,
and a remaining Prym/K3 correspondence obligation. It explicitly does not
establish an exceptional splitting, simplicity of this individual Prym,
a rational primitive, certificate nonexistence, a Lean proof or acceptance.
The signature alone does not identify a product of CM elliptic curves.
These are **author-reported calculations and limits**, including the
post's separate AI-agent checks; we have not independently replayed them.
Credit for this report is benediamond's, with the upstream split/K3 framework
and ChatGPT assistance acknowledged in the post. There is no new specific
rbajaj5 attribution to count.

All comment and reply pages in **#44, #55, #56, #111–120 and #127** were
fetched. The ID/timestamp/body-hash comparison finds exactly this one new
comment and its thread timestamp change: no edited or removed old record,
new reply, or answer change. The other thirteen threads are unchanged;
earlier credit is not summarized again.

## Acceptance metadata moved; target equations and receipts did not change

The 21 upstream commits include atlas navigation/view work and the
[PR 201](https://github.com/hodge-computer/sextics/pull/201) /
[PR 202](https://github.com/hodge-computer/sextics/pull/202) separation of
mathematical source from generated website data. Current `instance.rec`
files retain the exact mathematical fields. Presentation is kept separately;
browser records are built under `assets/atlas/` and are not committed copies.
The old `data/index.json`, `data/<id>/record.json`, `solution.rec/json`,
generated chapters and separate solve-credit file were removed as duplicates.

The pinned [builder](https://github.com/hodge-computer/sextics/blob/4a8e09b6002d250094cb1c1152a6026c55030ead/scripts/build-content.py)
starts from `formalStatus: unproved`, then validates `acceptance.json`
before setting `formalStatus: proved` and deriving solver credit from it.
The [acceptance reader](https://github.com/hodge-computer/sextics/blob/4a8e09b6002d250094cb1c1152a6026c55030ead/scripts/proposals/acceptance.py)
retains its validation implementation. The publisher drops the redundant
`solution.rec` write and continues to validate the receipt and build content.
No new authorization policy change was found beyond checkpoint 136.
**Removed generated records are not evidence of revoked acceptance.**

Our executed source comparison establishes:

- All **82** target IDs and literal `F`, `q`, `A` scalar values match between
  the pinned revisions, including continuation lines. This is text equality
  of protected fields, not a new polynomial or proof calculation.
- All **66 acceptance**, **66 proof**, **82 provenance**, and **82 why** files
  retain their Git blob identities. All 66 outer receipt publication flags
  remain `formalAcceptance: true`. The remaining **16 targets** have no
  acceptance receipt; `one-reflection-skew` and `four-plus-two-residual`
  remain open. No accepted solve or solver attribution changed.
- `read_acceptance` has an identical Python AST and no `formal/` source
  path changed. We inspected this implementation; we did not execute the
  acceptance validator, protected verifier or Lean kernel.
- The API comparison returned its capped 300 files. Complete local Git
  trees and a no-rename diff cover **593 changed paths** (578 diff entries
  with rename detection), avoiding that coverage limitation.
- Of the old **532 monitored pins**, 233 changed: two policy documents,
  82 instance files, removal of 82 browser records, 66 solution JSON files
  and the index. The current tracked set has **383 pins**. This pin-count
  reduction is explained by the generated-data migration.

Current consumers should use exact `data/<id>/instance.rec`, proof sources
and `acceptance.json` for evidence, and the deployed generated
`assets/atlas/index.json` / `assets/atlas/<id>/record.json` for presentation.
The builder's solve field is `formalStatus`; old duplicate status fields
are retired. Historical notebook source pins and receipts remain unchanged.

## Evidence and limits

[Review and hashes](../results/catalogue-monitor-20261023/review.json),
[complete source comparison](../results/catalogue-monitor-20261023/source-comparison.json),
[discussion comparison](../results/catalogue-monitor-20261023/monitor-comparison.json),
and [current repository pins](../results/catalogue-monitor-20261023/repository-after.json)
retain the observations. The separate read-only reviewer inspected policy
and generator changes; it performed no builds or proof replays.

Reproduce the source comparison with a clone containing both pinned commits:

```text
python -X utf8 results/catalogue-monitor-20261023/verify_snapshot.py PATH_TO_SEXTICS OUTPUT_JSON
```

It completed in **0.297 seconds**, with a 20-second per-process and
60-second total bound. The complete discussion run completed in **7.280
seconds**, under a 45-second request / 240-second total bound. Network
operations succeeded without authentication retries or timeouts. An initial
PyYAML availability probe failed; the saved checker instead uses the
standard library for explicit literal-field extraction and checks field
uniqueness. No interrupted calculation is counted as evidence.

We did not replay the new Prym mathematics, build the website, test its live
deployment, rerun completed research or publish upstream. Ordinary status
maintenance does not require a new research visualization. The Posts list
remains 1–29; the tally is **29 discussion contributions, one closed
maintenance PR, zero accepted authored solves**.

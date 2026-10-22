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


## Later monitor — 22 October 2026, 01:09 UTC

The upstream head remains `84f106ebf0731cbee1926833236361cddac0fc3f`; catalogue,
target/acceptance records and policy pins are unchanged. Hodge Lab now includes
the completed checkpoint-122 Lean batch at `c4fc59eb3c2f4ea2c3382a3cb9a1e7d77e4f3740`.
The previous status and verification summaries above remain historical records.

There is one new substantive discussion update: fqlx's
[rank-one-biquartic report, comment 19111720](https://github.com/hodge-computer/sextics/discussions/118#discussioncomment-19111720),
posted 22 October at 00:19:35 UTC (21 October, 8:19:35 p.m. EDT).
The author reports geometric generic Picard rank one for the weighted X-pencil,
scoped exclusions of compact-Y base currents, and an elliptic partial current
that still leaves a nonzero **17-dimensional residue sector**. Generic Picard
rank is not a statement about every special fiber, and these current exclusions
do not cover a support correlating the individual X and Y curve coordinates.

The linked [portable packet](https://gist.github.com/fqlx/93cce6ff81f26815d56d1c2865a0b9a9)
and its **15 focused replays** are author-reported evidence here. This monitor
read the complete discussion; it did not download or replay that packet or
verify the geometric arguments. The post explicitly claims no unrestricted
certificate, Lean proof or acceptance receipt. Its newer mixed-support,
conductor and residue proposals are described as not independently replayed by
the author, so this note does not promote them to checked conclusions.

`rank-one-biquartic` remains **open** in the pinned catalogue. The post supplies
no new rbajaj5 attribution, and receiving or recording it is not a contribution.
All pages in the 14 monitored discussions were fetched; no other comment,
reply, body-hash or answer change was found.
[Snapshot, coverage, pins, commands and scope](../results/upstream-monitor-20261022/010928/monitor-receipt.json)
and [complete thread snapshot](../results/upstream-monitor-20261022/010928/discussion-118.json).
No access failure or timeout occurred. No research replay or upstream action
was performed. The tally remains **29 discussion contributions, one closed
maintenance PR, zero accepted authored solves**.


## Later monitor — 22 October 2026, 11:58 UTC

Upstream remains at `d5e9ef223a2cd210517f35c071e9a5108a15e025`; all
532 saved target/policy blob pins are unchanged from the previous monitor.
Hodge Lab is at `824a5ba427eed35cd2c6ab4504612390533f2f2c`, including
the completed ambient-form proof. No new acceptance is recorded.

One new reply in [#127, fqlx comment 19113830](https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19113830)
reports a rational physical correction with a nonzero remainder and a
rank-17 reformulation of the compact source problem. The primitive,
homogeneous certificate and protected theorem remain missing. The claimed
22 exact current checks, 16 audit checks and two-point matrix tests are
author-reported; we did not replay them. The compact equivalence must not
be widened to all certificates with extra fibre supports or general Q.

All comment/reply pages in the 14 monitored discussions were compared by
IDs, timestamps and body hashes. No other comment, reply or answer change
was found. This is not new specific credit to rbajaj5; earlier parent-comment
credit remains historical. [Pins, complete changed-thread snapshot and scope](../results/skew-compact-architecture/monitor-receipt.json).

At the user's request, we also inspected and mapped the packet's architecture.
The archive and all 40 member hashes pass, and its protected target matches
our pin. This establishes byte provenance, not the reported mathematics.
[Architecture, proposed Lean interface and limits](skew-compact-architecture.md).
No packet math replay, upstream post, reply, edit or PR was performed.
Posts and contribution tally remain 29; historical entries are preserved.


## 22 October 2026, 15:58 UTC: atlas refresh changes file pins, not the two checked targets

Upstream advanced from `d5e9ef223a2cd210517f35c071e9a5108a15e025`
to [21fccb6b4f1d4070ddaa30195a78f268247569e6](https://github.com/hodge-computer/sextics/commit/21fccb6b4f1d4070ddaa30195a78f268247569e6),
merging [PR #187](https://github.com/hodge-computer/sextics/pull/187).
Benjamin E. Diamond's three commits update atlas slices/cameras, publish adaptive
meshes and adjust renderer startup. Hodge Lab's observed head was
`903fdfe27f05318446d9b6686c673385a8e9f84d`.

All 532 monitored paths remain present. Exactly 165 blob pins changed:
82 `instance.rec`, 82 `record.json`, and `MAINTAINING.md`. All 66 acceptance,
66 proof and 66 solution JSON pins are unchanged, as are provenance, why notes,
index, README and contribution-policy files. The maintainer documentation adds
mesh simplification/refinement commands and explicitly warns that a local
simplification tolerance is not a global error bound.

We fetched old/new `instance.rec` and `record.json` for **one-reflection-skew
and cyclic-triple-fano**, verified eight Git blob/SHA256 hashes, and checked
that only `render` changes. Every other JSON field, including F, A, q and
status, is identical. The rec files also match outside their render blocks.
This is an executed data comparison, not a mathematical or rendering replay.
The old one-reflection-skew record SHA256 remains
`fc7e070e4f459a521e3515c3b0d7e85fe4a557e345839f9cdb324491c289063f`;
the new full file is
`7c724757bc4e1147b57a96e4ce1344938a82d4825ab444b9027f00621859fa85`.
Historical audits retain their original inputs and receipts. A historical
byte-equality claim must not be silently restated against the new full file.

[Inputs, pins and executed validation](../results/atlas-monitor-20261022/validation.json)
and [offline checker](../scripts/check_atlas_target_metadata.py):
`python -X utf8 -O scripts/check_atlas_target_metadata.py` (15-second bound).
The [fetch receipt](../results/atlas-monitor-20261022/fetch-receipt.json) pins
all eight files; [repository comparison](../results/atlas-monitor-20261022/repository-comparison.json)
and [full tracked blob pins](../results/atlas-monitor-20261022/monitor-pins.json)
record the broader scope. The GitHub comparison's 300-file listing is capped:
we have **not** independently compared mathematical fields for all 82 targets.
No Lean build, certificate validation, mesh execution or new proof is claimed.

All pages of the 14 monitored discussions were fetched, including replies,
and [compared](../results/atlas-monitor-20261022/discussion-comparison.json):
zero additions, edits, removals or metadata changes. No new acceptance or
attribution was found. All network requests had a 45-second bound; the main
collector had a 240-second total budget and the eight-file follow-up a
120-second budget. No timeout or access failure occurred. This is ordinary
status/pin maintenance; no new research visualization or README change is
warranted. No upstream publication. Posts and tally remain 29.

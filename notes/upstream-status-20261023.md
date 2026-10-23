# Upstream status — 23 October 2026, 00:25 UTC

One new [Discussion #127 post by Josh Diamond / DiamondJM](https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19134103)
reports limited negative results for one-reflection-skew. It claims no
certificate, Lean proof or solve PR. The target remains open. This entry
records the report and its limits; we did not replay its mathematics.

The author reports symmetry restrictions and a proof sketch excluding a
cubic-surface construction with one active X coordinate, passive X ratios,
and specified transported-density hypotheses. Two active X coordinates and
passive ratios mixing X and Y remain outside that sketch. Supporting Singular
tests use modulus 32003 at Y0=2, Y1=3. These special-point tests are not our
verification of the general proof sketch.

The post also reports tests of 55 degree-six supports modulo 268435399 and
a modular replay of fqlx's existing half-certificate. It explicitly cautions
that low-degree failures are weak evidence, including on solved one-reflection.
An estimated large first-order deformation was not attempted. Its fibration
analysis concerns a particular presentation; it is not a blanket refutation
of the other compact/companion constructions in this thread.

The [observed reproduction branch head](https://github.com/DiamondJM/hodgeHoldout/commit/fc57193621c91939f5d3ea1c5329c04feddd216f)
is `fc57193621c91939f5d3ea1c5329c04feddd216f`, retrieved at 00:26 UTC.
Its commit time, 22:55:33 UTC on 22 October, follows the post's 22:47:39 UTC
creation/update time. This pins the observed branch, not necessarily the
exact revision used for the posted calculations. We fetched commit metadata
only, without reading or executing the linked scripts. The post credits fqlx,
fringewidth, the framework authors and Griffiths, and discloses Claude Code
assistance. It claims no independent human review. No new rbajaj5-specific
credit was observed.

## Observation and verification scope

- Hodge Lab parent: `08d405d21632f78887dd0f78c28f248f9c17fb6b`.
- Upstream: [59d570e2823d7c605decc3055dae392ec5b8d5f2](https://github.com/hodge-computer/sextics/commit/59d570e2823d7c605decc3055dae392ec5b8d5f2).
- All 532 monitored target/policy blob pins match the previous local baseline.
- All comment and reply pages were fetched for #44, #55, #56, #111–120
  and #127. IDs, timestamps and body hashes were compared, including edits.
  Only the new post and #127's update timestamp changed; the other 13 threads
  and all previously recorded comments/replies were unchanged.
- Requests had 45-second bounds; discussion collection had a 240-second
  total bound. The run recorded no access failure or timeout. A separate
  read-only agent reviewed the new post's scope.
- No mathematical, modular, Singular, Lean/kernel, primitive, or certificate
  verification was executed. No prior replay or attribution was counted again.

The [monitor receipt](../results/skew-monitor-20261023/review.json) links the
saved evidence through hashes. The [complete #127 context](../results/skew-monitor-20261023/discussion-127.json),
[comparison](../results/skew-monitor-20261023/comparison.json),
[repository pins](../results/skew-monitor-20261023/repository-heads.json), and
[linked branch receipt](../results/skew-monitor-20261023/linked-source-pin.json)
preserve the observed source state. The full local monitor snapshots remain
under `work/discussion-monitor`; the repository stores #127 and the all-thread
manifest rather than duplicating all unchanged discussion bodies.

This is status maintenance, with no new research visualization. No upstream
post, reply, edit or PR was made. The Posts list remains entries 1–29; the tally
remains **29 discussion contributions, one closed maintenance PR, zero
accepted authored solves**. README mathematical claims and historical receipts
remain unchanged. The new report does not close the primitive/certificate gap
or any outstanding physical-instantiation/descent obligations of our Lean work.

## 23 October 2026, 02:24 UTC: comment rankings move to a live service

Upstream [faa9df2ec6406e4eacc135f677cf3711315d0e41](https://github.com/hodge-computer/sextics/commit/faa9df2ec6406e4eacc135f677cf3711315d0e41)
includes PRs [193](https://github.com/hodge-computer/sextics/pull/193) and
[194](https://github.com/hodge-computer/sextics/pull/194). The source now obtains
comment rankings and contributor profiles through its backend, replacing the
committed comment/account snapshots and refresh workflow. The separate spacing
change affects the loading message.

The [maintenance documentation](https://github.com/hodge-computer/sextics/blob/faa9df2ec6406e4eacc135f677cf3711315d0e41/MAINTAINING.md)
and [backend implementation](https://github.com/hodge-computer/sextics/blob/faa9df2ec6406e4eacc135f677cf3711315d0e41/server/comment-leaderboard.mjs)
describe counts of comments/replies in mapped atlas threads, omitting minimized
posts and deleted-account authors. The visible board is designed to refresh
without a repository commit. Accepted-solve scoring remains acceptance-backed.
These are implementation observations, not verification of the deployed site.

**Checkpoint 133's count of 12 rbajaj5 entries remains a historical snapshot.**
We did not measure a new live count. The curated Posts list and tally of 29
contributions retain their separate scope. No new mathematical attribution
or acceptance follows from this implementation change.

The new instruction against committing discussion snapshots is explicitly
scoped to the upstream leaderboard feature. Hodge Lab's separate pinned
research-evidence archive and historical receipts are preserved.

[Receipt and limits](../results/live-comment-monitor-20261023/review.json)
record the 20-file/four-commit comparison and source pins. Among 532 monitored
target/policy pins only README.md and MAINTAINING.md changed; the other 530
are identical, including all monitored target/acceptance/proof/solution files.
All 14 monitored discussions are unchanged, with complete comments/replies
and edited-body comparison. Requests were bounded at 45 seconds and discussion
collection at 240 seconds; no failure occurred. A separate read-only agent
reviewed the scope. No backend tests, live endpoint check, mathematical replay
or Lean build was performed. This is ordinary status maintenance, with no
new research visualization, upstream publication or contribution-tally change.
Credit Benjamin E. Diamond and the upstream contributors for the interface work.

## 23 October 2026, 16:46 UTC: publication policy and local CI follow-up

Upstream moved from `faa9df2ec6406e4eacc135f677cf3711315d0e41` to
[`554757eca1aebecdd1d21f3452d3c71ffa601b19`](https://github.com/hodge-computer/sextics/commit/554757eca1aebecdd1d21f3452d3c71ffa601b19)
through PRs #195–197. The complete local Git comparison has 742 files;
GitHub's compare response listed only its first 300. We used the full Git
diff for the structural checks below rather than treating that API list as complete.

The [current contribution rules](https://github.com/hodge-computer/sextics/blob/554757eca1aebecdd1d21f3452d3c71ffa601b19/CONTRIBUTING.md)
remove CI-specific approving-review and workflow-signoff requirements.
Maintenance PRs use Repository build. The publisher no longer tests the
merging account against a configured owner; GitHub repository permissions
control merging. Historical authorization fields remain in existing receipts.
The [publisher](https://github.com/hodge-computer/sextics/blob/554757eca1aebecdd1d21f3452d3c71ffa601b19/scripts/proposals/publish.py)
still requires protected verification, matching source/target/verifier hashes,
kernel-replay evidence, contributor identity and exact merge parents. A green
proof check and accepted publication remain separate. Documentation identifies
benediamond as the sole human writer; we did not inspect the actual access settings.

The verifier regression workflow and its `test_check.py` / `test_lean.py`
scripts were removed. The replacement Repository build validates release
content and conditionally checks changed shared Lean modules and affected
accepted applications. These are source observations; we did not run the
builds, inspect deployment behavior or audit the revised verifier end to end.
Hodge Lab's own ledger-before-upstream-publication requirement is unchanged.

The 167 changed monitored blob hashes comprise three documentation files,
82 `instance.rec` files and 82 generated `record.json` files. Exact text
comparison finds only camera-key edits in every `instance.rec`. JSON
comparison finds the corresponding camera edits and one removal of
`render.divisorProgram` from quadric-contact-broken's generated record. That
removed field describes approximate slice-presentation data. All other JSON
content is identical. Forty-one `solution.md` files change only their two
witness/proof link targets to document-relative paths. No Lean source,
formal-library file, witness, acceptance receipt, proof manifest, provenance
or motivation file changed. Camera-rotation equivalence was not tested.

All 14 monitored threads have complete comment/reply pagination and unchanged
IDs, timestamps and body hashes (56 records). There is no new discussion
result, credit or acceptance. The review of the chat now titled **Correct Grok
Assessment** confirms that the original holdout's accepted PR #128 and its
explicit rbajaj5 attribution are existing facts; checkpoint 91 already records
the acceptance and preceding-work credit. The accepted explanation does not
give a minimal denominator degree. Our bounded degree-seven exclusions are
not a universal degree-eight bound, and the accepted holdout result is not a
solve of one-reflection-skew. No new contribution is counted for this read-back.

### A verified notebook CI failure, separate from the upstream cleanup

The live [Notebook Lean proofs run](https://github.com/rbajaj5/hodge-lab/actions/runs/39832127430)
at checkpoint 132 (`0200f4c07e76af3cdd29f45e9078c245c222b28c`) passed the
differential-form step, then stopped in the trace-basis check with:

```text
RuntimeError: Historical context receipt changed: formal/results/skew-forms/validation.json
```

The current workflow runs `check_skew_forms.py` before
`check_skew_trace_basis.py`. The former rewrites its validation receipt,
including run-dependent timestamps and timings. The latter compares that
working file with a pinned historical hash before calling Lean. The logs and
current source therefore identify a receipt-lifecycle conflict. This failure
does not refute the theorem, and it does not establish a successful CI replay
of the new trace-basis modules. The saved local checkpoint-132 checks retain
their original scope. No repair or Lean replay was performed in this review.
The smallest next maintenance step is to separate immutable historical
context receipts from fresh run outputs, retain the hash check on the former,
and rerun the affected CI sequence.

[Evidence, reproducible structural checker and limits](../results/upstream-policy-monitor-20261023/review.json)
include a complete changed-file list, policy diff and the exact CI error
excerpt. The structural check ran under Python 3.11.9 with required checks
active under `-O`; Git was 2.55.0.windows.5. Each Git subprocess was bounded
at 30 seconds, fetches at 90, network reads at 45, and discussion collection
at 240. The initial checker assumptions and their corrections are retained:
some cameras already had orientation data, one generated renderer field was
removed, and explanation links also changed. A separate read-only AI agent
reviewed the policy source; no independent human or mathematical review is claimed.

This is status/provenance maintenance, not a research batch; no new figure is
needed. No upstream post, reply, edit or PR was made. Posts remain 1–29 and
the tally remains **29 discussion contributions, one closed maintenance PR,
zero accepted authored solves**. Existing ledger text and proof receipts are preserved.

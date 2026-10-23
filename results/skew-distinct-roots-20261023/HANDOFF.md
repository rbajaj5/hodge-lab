# Hodge Lab handoff: generic distinct roots

## Outcome and publication ownership

The chosen generic distinct-root dependency is closed locally in Lean.
For the literal polynomial `X^18+X^12+(vX-1)^6-aX^15`, the new module proves
separability over the explicit iterated field `Q(v)(t)(a)`, constructs the
full splitting field, and supplies an injective `Fin18` tuple of all roots.
It instantiates the existing physical binding and two split-L trace
corollaries. The `a=2,v=1` nonseparable specialization remains formalized.

This package is for the original Goal-enabled coordinator to apply, review
and publish. No commit, push or upstream write was made by this Pro chat.
Goal activation is human-reported in coordinator chat
`01a145f0-1bc3-7321-8c36-83a883bf061f`; no Goal-control or cross-chat messaging
capability is exposed to this mathematics worker.

## Pins and archive structure

- Parent: `bf0c69287865ba00d3e651cdbc4d0f881deba4db`.
- Upstream source: `b790130d43b49ec0ddc6865d0bdc949eeeee2319`.
- Lean: 4.31.0, commit `68218e876d2a38b1985b8590fff244a83c321783`.
- Mathlib: `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`.
- Python used: 3.12.14; Matplotlib: 3.10.8.

`payload/` contains only the changed and added files against the pinned
parent. The coordinator already has that exact checkout and the historical
raw hashes. Unchanged parent files, submodule contents, Git object databases
and build caches are intentionally omitted under the final five-minute
handoff bound. The patch preserves every unchanged parent entry, including
the ten existing submodule Git-link pins.

`hodge-distinct-roots-bf0c692.patch` is a binary-safe Git patch.
`MANIFEST.sha256` covers every regular-file ZIP member other than itself.
The external `SHA256SUMS` additionally covers the ZIP, patch, manifest,
guide, figure and package report. `handoff.json` records the final staged
Git tree and the archive's precise scope.

The proposal changes only three pre-existing files: README, an append to
LEDGER, and a single new focused CI step. All other paths are new files.
All 3,086 historical tracked result files and the original 393,826-byte
ledger prefix are byte-identical. The prefix SHA256 is
`645c410bb39705ad63f849caa7c7948e978808b9eb6ce18d6df35117eb48820f`.
Posts 1–29 and the tally 29 discussions / 1 closed maintenance PR / 0
accepted authored solves remain unchanged.

## Apply and reconcile

Use an isolated checkout and fetch current Hodge Lab main before applying.
If main is still the pinned parent, the following patch checks should pass:

```sh
git apply --check --index /absolute/path/hodge-distinct-roots-bf0c692.patch
git apply --index /absolute/path/hodge-distinct-roots-bf0c692.patch
git write-tree
```

The resulting tree must match `handoff.json`. The initial patch passed
this procedure in a separate local verification worktree, before subsequent
packaging-only additions. Under the final handoff bound, the final patch
is not reapplied here; the coordinator will perform that final check. If remote main advanced,
reconcile the intervening changes in the coordinator's isolated checkout;
preserve the existing ledger prefix and integrate the proposed checkpoint
append, renumbering only if a concurrent checkpoint already occupies 139.
Review the final staged diff before a normal commit and push. Never force
push. A publication access error should be recorded once with the retained
patch and pins, without authentication retry loops.

The human explicitly restricts publication to `rbajaj5/hodge-lab`.
Do not post, reply, edit discussions or submit a PR in `hodge-computer`.

## What actually ran

The sole Lean writer executed seven development commands: five ordinary
normalization/API/coercion failures, a separability-core PASS and a complete-
module PASS. Exact snapshots, stdout, stderr, exits and timings are retained.
The first focused checker passed in 22.576 seconds. Root integration then
corrected its hardcoded executor label and scratch-name collision risk;
the final checker passed in 16.801 seconds with the proof module unchanged.

The final check audited **48 public declarations**, kernel-replayed **one
new module**, checked **nine grouped positive interfaces**, and rejected
**three intended false claims**. Its axiom union is exactly `propext`,
`Classical.choice`, `Quot.sound`. The false claims are universal separability
of rational specializations, the eliminant constant +15, and a collision
of constructed roots 0 and 1. No unrelated elaboration failure was accepted.

A separate mathematical AI specialist executed exact sparse integer
arithmetic and three multiplier/exponent/sign mutations in 0.039754 seconds.
A separate adversarial AI reviewer audited 95 saved artifacts and the
source/assumption boundaries in 0.047446 seconds, without rerunning Lean.
Its first receipt-schema audit error and corrected successful audit are
both preserved. These AI roles are not independent human review.

Root executed the current source comparison, a 192-file staged delivery
audit, the 3,086-file historical-byte checks, link/UTF-8 checks, visualization
and patch application. The first figure render's text overlap and its
generator are preserved; the corrected final render was visually inspected.
The package manifest covers files generated after the staged delivery audit.

The first packaging check stopped when its regular-file count also included
ten existing Git-link entries. Its source, Git command logs, exact missing
paths and already-successful patch verification are preserved under
`integration/package-attempt-01`. The full-parent archive route was stopped on the user’s instruction.
The final changed-file package needs no expanded submodules. The failed
full-archive script and exact failure records remain available; the corrected
full-archive draft was not executed. This was a packaging issue; no new
mathematical execution was involved.

The coordinator's SymPy review was human-relayed support, distinct from
these actual executions. No prior CI repair, source-to-Hessian, transport,
covariant-jet or split-basis checker was rerun. The prior full Lean CI
run 40026828482 is confirmed successful at published commit
`5d216691981cdb248073209bdc80df86021412d4`. There is **no new remote CI result**
for this unit until coordinator publication. Record that result separately.

## Focused reproduction

With the pinned Lean toolchain and Mathlib cache available, run from the
patched repository. Every output directory below must be fresh.

```sh
python3 -O results/skew-distinct-roots-20261023/verify_source_snapshot.py \
  --output-dir /tmp/hodge-distinct-source-reproduction
python3 results/skew-distinct-roots-20261023/math-review/run_exact_review.py \
  --output-dir /tmp/hodge-distinct-exact-reproduction
cd formal
HODGE_CHECK_EXECUTOR="coordinator reproduction" \
python3 -O check_skew_distinct_roots.py \
  --output-dir /tmp/hodge-distinct-lean-reproduction
cd ..
python3 -B scripts/visualize_skew_distinct_roots.py \
  --output-dir /tmp/hodge-distinct-figure-reproduction
```

`lake exe cache get` in `formal/` is the repository's normal cache setup
when needed. The checker limits each child command to 120 seconds and the
focused run to 600 seconds. The mathematical pass used only the eliminant
approach and completed within 13 minutes 44 seconds of its declared start,
well within the 60-minute, two-approach bound. No timeout or interrupted
calculation is counted as a result.

The reproduction commands above repeat only the new unit. Do not rerun
unrelated work to increase check counts. The added workflow step writes
fresh outputs to `formal/results/runs/ci-skew-distinct-roots`, already
covered by the workflow's artifact upload.

## Review entry points and exact limits

Within `payload/`, start with (other referenced files are in the pinned parent):

- `notes/skew-generic-distinct-roots.md` — statement, proof, fields, chart assumptions and scope.
- `formal/HodgeLab/OneReflectionSkew/GenericDistinctRoots.lean` — exact formal source.
- `results/skew-distinct-roots-20261023/lean-development/checker-02/validation.json` — final writer execution.
- `results/skew-distinct-roots-20261023/source-review/final-review.json` — read-only AI review.
- `results/skew-distinct-roots-20261023/integration/delivery-01/validation.json` — root's staged preservation/UTF-8/link audit.
- `results/skew-distinct-roots-20261023/checkpoint139-append.md` — proposed ledger text, also appended in the patch.
- `results/skew-distinct-roots-20261023/visualization-02/` — accepted PNG/SVG, input/output hashes and visual review.

The proof source SHA256 is
`7edbe6bde88a36cc68e33cb270cc8a349449ab45e4699df91d806be94138f08b`.
The final focused receipt SHA256 is
`8042bce23d5f79de6f3265da9b43ba0dcae9f42654d8a8b60a076dfb105d1835`.

The field is the explicit iterated rational-function presentation; no
separate equivalence to another multivariate implementation is claimed.
The tuple is noncomputable. Generic distinctness does not hold at every
specialization. Traces remain over the split L-algebra.

The smallest future formal bridge toward an unsplit statement is the
scalar-extension comparison of K[X]/(f) with the existing split L quotient,
including trace compatibility. That work was not started. Physical
differential-source normalization remains another obligation. No primitive,
global clearing, HasCertificate or target solve is claimed.

# Upstream monitor — 11 November 2026

**Observed at 18:18 UTC; bounded monitoring, Hodge Lab only.** Upstream is
[`03cc4fc`](https://github.com/hodge-computer/sextics/tree/03cc4fc1bad78d33c2a40bbfa545dea3ac9aa29f),
28 commits after `e3936ff366ae2302f21fb9e5730bbbd284c81d69`.
Notebook parent: `27d5498288c7257436fa04f0cdaea18aea58c83d`.
The trigger predates collection; these are observations made on 11 November.

The catalogue still contains **82 targets, 66 accepted submissions and 16
without accepted submissions**. Every fixed instance, acceptance and proof
blob in the monitored inventory is unchanged. Six of 383 target/policy pins
changed: four policy/readme files and the two `cycle-q2` context files.
Current source pins, historical verification receipts and published acceptance
remain separate evidence.

## Cycle-q2: new upstream existence statement, no accepted submission

Benjamin Diamond's maintained
[target context](https://github.com/hodge-computer/sextics/blob/03cc4fc1bad78d33c2a40bbfa545dea3ac9aa29f/data/cycle-q2/why.md)
and [provenance](https://github.com/hodge-computer/sextics/blob/03cc4fc1bad78d33c2a40bbfa545dea3ac9aa29f/data/cycle-q2/provenance.json)
now assert rational certificate existence for the exact q=2 target through
the new [Chapter 3D](https://github.com/hodge-computer/sextics/blob/03cc4fc1bad78d33c2a40bbfa545dea3ac9aa29f/docs/03d-hodge-loci.md)
paired-sign/order-three support theorem. This updates the earlier unresolved
existence wording. It does not record a new accepted submission, an extracted
rational primitive or our verification of the argument.

The stated symmetries are the paired sign on `(X2,Y2)` and
`gamma = diag(omega^2,omega^2,1,omega,1,1)`. The source and projective-volume
characters combine to give an invariant residue for this action. The older
sixth-root quotient still erases the target's nontrivial character; that
limitation was retained, not disproved. The accepted `cycle-three` proof and
the separate all-target cyclic-six family are also distinct arguments.

The final chapter uses moving divisor classes on surface sections, their
Hodge loci and Abel–Jacobi variation, followed by supported-projector
specialization. The Fano-fourfold route from an intermediate revision is now
a remark. The finite computations and smoothness argument are upstream
supporting claims. We read their scope; we did not run the new verifier or
audit the proof.

## Residue and prescribed-support proof maintenance

[Chapter 1](https://github.com/hodge-computer/sextics/blob/03cc4fc1bad78d33c2a40bbfa545dea3ac9aa29f/docs/01-certificates.md)
reworks higher-pole residues and the proof from divisor support to a
certificate, distinguishing the affine pole-reduction step from the bounded
pole argument using resolution, logarithmic degeneration and currents.
The prescribed-support statement retains the smooth-hypersurface hypothesis
and the range `1 <= q <= n-1` (q=1 through 4 for a sextic fourfold).
For a supplied support it asserts a denominator `D_red^q`; it imposes no
smoothness or normal-crossing condition on the support. This does **not**
bound the degree of a support that has yet to be found, or replace that power
by the original denominator. We record the revised exposition and proof
claim, not a new local proof or formal replay.

## Four new discussion reports

All four are partial construction reports, with checks attributed to their
authors. Attachments and external proof services were not independently
replayed or validated here.

- **kmehltretter82, #117:** [canonical source coefficients](https://github.com/hodge-computer/sextics/discussions/117#discussioncomment-19483304)
  supplies explicit coefficients and reports Lean/function-field identities.
  It credits fqlx's chart and benediamond's transport. The reported Prove2Me
  acceptance concerns a standalone scalar result, not this Sextics target.
  No current or primitive is supplied.
- **fqlx, #117:** [current/trace reduction](https://github.com/hodge-computer/sextics/discussions/117#discussioncomment-19484532)
  reports checked helper declarations and their original replay scope.
  The final draft still admits `Submission.relative_primitive_exists` and
  depends on `sorryAx`. An actual extension, compatible derivations, current
  and complete normalized source identities remain necessary. The attachment
  migration claims no fresh Lean run.
- **benediamond, #117:** [construction synthesis](https://github.com/hodge-computer/sextics/discussions/117#discussioncomment-19494559)
  reports six source conditions after a rational correction, a smaller
  incidence presentation and an unrestricted square-coordinate equation.
  It credits fqlx and kmehltretter82 for their specified components. The
  admissible weight or rational solution is missing; the smaller model still
  needs its selected-component comparison. The Hermite current has a nonzero
  remainder. Rank-48 cohomological spanning does not supply the literal trace
  equations. Reported SymPy checks and reference Lean snapshots do not close
  the primitive admission or constitute a fresh kernel replay.
- **DiamondJM, #120:** [core bridge and numerical model](https://github.com/hodge-computer/sextics/discussions/120#discussioncomment-19504157)
  rewrites the book's suspension construction conditional on a rational core
  field that has not been found. Selected-support searches are not a complete
  degree exclusion. The 44-equation numerical contact model still requires
  exact certification and smoothness. The historical 3,065-run report is
  explicitly insufficient for a million-sheet bound or swept-surface degree;
  no elimination-impossibility conclusion is retained. No primitive or Lean
  proof is supplied. Claude Code assistance and later ChatGPT curation/checks
  are disclosed separately.

The symmetric and four-plus-two book existence assertions were already
recorded on 7 November. These posts do not create another acceptance or new
credit to rbajaj5.

## Edited evidence, missing reply and preserved corrections

The complete 14-thread collection contains **51 comments and 19 replies**.
Compared with 8 November, four records are new, 66 existing records changed
and one earlier reply is absent. Three discussion-level timestamps changed;
individual IDs, timestamps and body hashes were compared for every record.

Many edits replace repository/PR/gist links with discussion attachments or
remove links, hashes, replay instructions and qualifications. The six kejace
reports retain their complete low-degree bounds but narrow the current
attachment scope: higher-degree/individual-sector experiments are often
summarized without their original per-case certificates. That is a change
in available evidence and stated replay scope, not proof that every omitted
calculation was false. The before/after bodies and exact differences remain
in the [discussion review](../results/upstream-monitor-20261111/discussion-review.json).

kejace's [coupled-Klein edit](https://github.com/hodge-computer/sextics/discussions/116#discussioncomment-19345484)
also reports a new bounded rational reconstruction of the existing
eight-dimensional second-stage quadric span. It expressly claims no new
Singular run. We did not execute this reconstruction; the reported complete
degree-six exclusion is unchanged, and the target still has no accepted
submission.

In rbajaj5's [#127 comment 19049585](https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19049585),
the live quadratic rank remains **15**, but the dated rank-16-to-15 correction
paragraph and notebook audit links were removed. Our
[completed correction](one-reflection-skew-mathematical-audit.md) and
[source-to-Hessian reconstruction](one-reflection-skew-hessian-source.md)
remain unchanged; neither was rerun or republished.

fqlx's previously captured [T100 reproduction reply](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-19003434)
is absent from this complete snapshot. Its earlier body, source pins,
verification limits and attribution are preserved in the review. Absence
does not refute the result or erase earlier recorded credit. The API
identifies original authors, not the editor or reason for each change;
this monitor made no upstream edits.

## Policy and verification boundary

Upstream [AGENTS.md](https://github.com/hodge-computer/sextics/blob/03cc4fc1bad78d33c2a40bbfa545dea3ac9aa29f/AGENTS.md)
now delegates to [CONTRIBUTING.md](https://github.com/hodge-computer/sextics/blob/03cc4fc1bad78d33c2a40bbfa545dea3ac9aa29f/CONTRIBUTING.md).
Discussion comments must state their result and limits themselves; curated
ZIP evidence is strongly encouraged. Their permitted links are book items,
instance pages, discussions/attachments and external research papers.
Repository, fork, repository-file, gist and PR links (including `#123`
shorthand) are prohibited in discussion comments. These rules are distinct
from solution and maintenance PR workflows. The historical notebook keeps
its source pins and evidence links. Any separately authorized future upstream
action still requires the prior Hodge Lab ledger audit; none occurred here.

Our executed checks cover collection completeness, repository/blob identity,
source hashes, textual differences, attribution and publication integrity.
They do not include mathematical, Lean, attachment, numerical or CI replay.
See the [evidence manifest](../results/upstream-monitor-20261111/review.json),
[repository status comparison](../results/upstream-monitor-20261111/status-review.json)
and [policy/source review](../results/upstream-monitor-20261111/policy-review.json).
Earlier ledger text and receipts remain history. Ordinary maintenance needs
no research visualization. Contribution tally remains **30 discussion
contributions, one closed maintenance PR, zero accepted authored solves**.

# Holdout discussion checkpoint — 17 October 2026

Checked the current inventory of
[discussion 44](https://github.com/hodge-computer/sextics/discussions/44) and
read the six newer top-level updates following `fringewidth`'s structural post.
There are 15 top-level posts and five replies: six posts by `rbajaj5`, thirteen
posts/replies by `fqlx`, and one by `fringewidth`. This note records other
contributors' reported results and their implications; **we have not replayed
the newly linked proof packets or independently verified their geometric claims**.

The latest upstream commit is `adf3f2212cdd6f23433cc698f477aade81f097c6`.
The changes since our pinned snapshot concern presentation and participation
documentation. `data/holdout/` still has no solution files. Our pinned source
and protected target remain unchanged.

## What changes the research picture

* **A further degree-seven character family is reported excluded:**
  `{(0,1,0),(2,3,0),(4,5,0)}`. The author supplies square/cube ideal identities
  in 17 denominator parameters, with the shared numerator and quotient retained.
  We checked that the character generators match ours and that this triple is
  **outside our original 152-family selection**. It therefore does not reduce
  our list of sixteen remaining selected families. This is a comparison of
  coverage, not a replay of the exclusion proof.
  [Exclusion and closing update](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18989248).

* **A particular degree-30 support is reported excluded**, throughout the six-
  dimensional target-character sector and, using the prescribed-support theorem,
  including arbitrary multiplicities. This is a support-specific exclusion,
  not a prohibition on all degree-30 denominators. It warns against trying to
  repair an excluded support simply by raising its multiplicity.
  [Support obstruction](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18986834).

* **Several geometric construction routes have stronger limitations.** The
  automorphism analysis reportedly extends beyond monomial automorphisms to
  the full group. Higgs/variation calculations restrict persistent product
  sources. The newest such argument concerns elliptic-times-curve
  correspondences spread properly and flatly over both coupling parameters;
  it does not exclude every source on the single fixed fourfold. A stated
  product-of-curves requirement is `g h >= 12` under those family hypotheses.
  These genus constraints belong to the algebraic source problem and are not
  deductions about our synthetic genus-48 graph/GFF experiments.
  [Automorphisms and earlier Higgs analysis](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18988138),
  [simplicity and stronger source requirements](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18988590).

* **The constructive work moves toward nonelliptic sources:** a reciprocal
  genus-four curve with a genus-two quotient, an original-character connection,
  and a resolved-surface calculation. The missing step remains a global form
  with the required descent and boundary behavior whose Gysin image actually
  hits the target. Local differentials and numerical representatives alone do
  not supply that step. The closing edit explicitly withdraws an earlier
  auxiliary claim about a smooth square-six divisor on a minimal K3 and
  replaces it with a resolved-surface argument; do not reuse the withdrawn
  claim. The author says their research run has now stopped at their request.
  [Reciprocal construction](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18988590),
  [corrected closing checkpoint](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18989248).

None of these posts claims a legal holdout certificate, accepted Lean proof,
or solve PR. They credit the preceding work by `rbajaj5`, `fringewidth`, the
repository authors, and other named mathematical sources. Their computational
and geometric assertions require their own checks; being posted or credited
does not constitute independent verification.

## Implications for Hodge Lab

The immediate algebraic priority should be to reproduce and index the new
exclusion packet before broadening our search, then constrain searches by
known necessary equations rather than merely lowering residuals. Our recent
rank sweep is a useful explanatory example, but its entire plane is already
rejected by a common inherited syzygy. Another fit in that same plane cannot
solve holdout. The new reciprocal connection could inform future operator
visualizations; a graph-GFF analogy alone would not validate its geometry.

Upstream has also added a
[participation policy](https://github.com/hodge-computer/sextics/blob/adf3f2212cdd6f23433cc698f477aade81f097c6/AGENTS.md#return-results-to-the-project)
asking contributors to return useful outcomes to the shared project no later
than announcing or publishing them elsewhere. This is relevant to how we use
Hodge Lab as a supporting notebook. It is not a reason to mirror every lab
entry as a separate comment. A concise, substantive, reproducible update is
the appropriate unit of discussion. This reading checkpoint itself makes no
new upstream post, and our tally remains six.

## Correction to the preceding CI status

The last turn accurately reported local checks passing and CI still running.
That [CI run subsequently failed](https://github.com/rbajaj5/hodge-lab/actions/runs/38994316222)
after all 81 rank calculations and the numeric data comparison, when comparing
the source manifest. Its Windows-generated JSON keys used backslashes while
Linux generated forward slashes. The fix serializes repository-relative paths
with `as_posix()` and updates only those three manifest keys. Source hashes,
exact equations, rank results, numeric tolerances, and failed search data are
unchanged. The full sweep check is rerun, and Linux CI will replay it as well.

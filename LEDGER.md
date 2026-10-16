# Contribution and research ledger

Contributions by **rbajaj5** to [hodge-computer/sextics](https://github.com/hodge-computer/sextics), alongside the motivation and experiments recorded in Hodge Lab.

Our intent is to understand the fixed problems, share reproducible results and unsuccessful approaches, credit prior mathematical work, and pursue solution credit through the project's verification process. This statement is recorded on **16 October 2026**; the entry below summarizes an earlier public post.

**Tally, checked against GitHub on 16 October 2026:** 2 discussion comments; 0 authored issues; 0 pull requests; 0 reviews or review comments; 0 authored upstream commits; 0 accepted solves. Commits to Hodge Lab and unpublished experiments are separate from this upstream tally.

## Posts

1. **16 October 2026, 17:20 EDT / 21:20 UTC — [Holdout discussion #44: exact partial result](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18983276).** Shared an exact exclusion of the degree-seven `{chi_Y0, chi_X1}` denominator family, with reproducible code and certificate checks. The purpose was to contribute a checkable partial result and narrow the remaining search. The post credits fqlx's preceding calculations and the project's mathematical framework, and discloses Codex assistance. It reports 9,451 of 9,453 two-character families excluded **at the time of posting**, while explicitly leaving the full holdout unresolved. No Lean `HasCertificate` proof or solve submission was claimed. Evidence: [pinned explanation and code links](https://github.com/rbajaj5/hodge-lab/blob/dc2756300cbfa7a54d4735c60b852cd38ca8725e/notes/degree-seven-pair.md) and [passing CI](https://github.com/rbajaj5/hodge-lab/actions/runs/38968484482).

2. **16 October 2026, 18:52 EDT / 22:52 UTC — [Holdout discussion #44: family-13 exclusion](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18984345).** Shared the exact `{chi_X0, chi_Y0}` degree-seven exclusion and our reproduction of fqlx's distinct family-30 proof. The purpose was to fill the last two-character proof gap with a portable check, while crediting the complementary upstream work. The post records the 25 rational chart identities, independent coefficient reconstruction, corruption check, and [passing CI](https://github.com/rbajaj5/hodge-lab/actions/runs/38978064849). It links [immutable source and explanation](https://github.com/rbajaj5/hodge-lab/blob/5a1683fb82217aa49450614dc78d3b3e18b768c1/notes/x0-y0-exclusion.md), discloses Codex assistance, and explicitly leaves three-or-more-character denominators and higher degrees open. The combined count is 9,453/9,453 two-character families; no existence certificate, Lean proof, or accepted solve is claimed. The published body, author, and permanent URL were read back and verified.

## Research intuition and experiments

These entries record our reasoning even when it has not been posted upstream.
They do not add to the public contribution tally above. They were recorded on
16 October 2026; where they summarize earlier experiments, that is stated
explicitly. They are a public research record, not a transcript of private
conversations or evidence of an accepted solve.

1. **16 October 2026 — Why Dubedat.** The user's intended direction is to use
   free fields, geometric response, and visualization to develop ideas for the
   fixed algebra problem. Dubedat's dimer work suggests determinant partition
   functions, inverse operators, cycle twists, and deformation identities.
   Our working hypothesis is that structured operators may provide better
   denominator constructions than arbitrary coefficient guesses. No theorem
   connecting these constructions to the holdout has been established.
   [Sources and concrete adaptation](notes/dubedat-cycles.md).

2. **16 October 2026 — Earlier Gram-ranking results, recorded retrospectively.**
   Geometric/anisotropic Gram matrices were meant to improve candidate ranking.
   The recorded experiment reduced a numerical residual by about 32% against
   random selection, but extra anisotropic weighting did not clearly improve
   on uniform weighting and all 254 distinct shortlisted candidates failed
   exact checks. This motivated treating numerical ranking and algebraic
   validity as separate questions. [Experiment](notes/denominator-ranking.md).

3. **16 October 2026 — Six-cycle determinant experiment.** A small bipartite
   graph matrix supplies a degree-seven determinant and cofactor numerator
   lift satisfying E1 automatically. We tested all 15 gradient pairs with
   monomial edges and with mixed linear edges at twists +1 and -1. All 45
   directions were rejected with exact dual witnesses, allowing all 840
   numerator corrections. Thirty have seven or eight characters, beyond the
   two-character family theorem. Reciprocal edge reweighting left the
   denominator unchanged: a useful warning against counting redundant
   parameters as new geometric freedom. This finite failure does not reject
   Dubedat's ideas or all graph-matrix constructions. [Code, reasoning, and
   checks](notes/dubedat-cycles.md). No upstream post for this experiment.

4. **16 October 2026 — Imaginary geometry pictures.** The user's request is to
   make the geometric intuition visible. The new CUDA gallery holds Gaussian
   input fixed while varying the angle of a smoothed field's flow or the
   directional conductances of its Laplacian. Colors and textures are display
   choices; these finite periodic models do not establish an SLE coupling or
   an algebraic certificate. They help us inspect what a weighting change
   actually does before interpreting a numerical matrix score.
   [Gallery, equations, and validation](notes/imaginary-geometry-gallery.md).
   No upstream post for these pictures.

5. **16 October 2026 — Complementary exact algebra.** fqlx published and
   credited our family-22 continuation while supplying a portable proof for
   family 30. We reproduced that proof and its separate audit. Our checked
   family-13 exclusion fills the remaining two-character gap. This supports
   collaboration through attributed, reproducible partial results; it does
   not validate the separate geometric heuristics or solve holdout.
   [Combined argument and provenance](notes/x0-y0-exclusion.md).

6. **16 October 2026 — Proposed next tests, not executed here.** Use E1
   denominator/lift pairs outside the Jacobian ideal as graph-matrix entries;
   test multiple independent cycles after removing rescaling redundancy; and
   investigate whether inverse-operator/deformation identities impose useful
   relations on the full certificate equations. Each proposal still needs
   exact checks and a stated comparison baseline.

7. **16 October 2026 — Failed family-30 proof exports.** Before fqlx's portable
   proof, our rational Singular `slimgb` calculations returned the unit ideal
   on five full-system charts. Exporting a transformation matrix on the first
   chart exceeded 50 seconds and returned no polynomial multipliers. A bounded
   48-test subset search reduced 223 equations to 63 while retaining a CAS
   unit-ideal result; exporting that subsystem's multipliers also timed out
   after 50 seconds. Minimality was not proved. We did not count either export
   attempt as a portable proof. The subsequent proof is attributed to fqlx.
   [Saved inputs and stopping conditions](results/degree7-x1-y1-provisional/report.json).

8. **16 October 2026 — Unsuccessful routes before the family-13 proof.**
   Individual coordinate cubes/fourth powers produced no new vanishings in
   the tested row spaces. Squares of the 25 mixed products had no witnesses
   in the tested degree-four space. A larger tracked degree-six calculation
   was stopped when the 25-chart route succeeded. These are bounded search
   outcomes, not claims that no such polynomial consequences exist at higher
   degree. [Discovery history and the successful replacement](notes/x0-y0-exclusion.md).

9. **16 October 2026 — Hodge projection applied to the actual holdout equations.**
   The torus decomposition suggested separating each residual into a removable
   numerator-correction part and a cokernel obstruction. We screened 600
   degree-seven directions in six seeded three-character spans, chosen from
   E1 directions outside the Jacobian ideal. All 840 numerator corrections
   and the unrestricted quotient were retained. The 34 distinct directions
   selected by two numerical metrics and random controls all failed exact
   rational checks. A separate polynomial implementation verified 28,560
   correction-column annihilations. For the best coefficient-norm candidate,
   heat flow stalls at 57.24% of the initial squared residual; sparse and
   dense calculations agree. The numerical improvement from selecting the
   smallest measured residual is not a predictive-performance claim. These
   are fixed-direction exclusions, not exclusions of six continuous families.
   [Method, code, packet, and limits](notes/hodge-projected-search.md).
   No upstream post, solve submission, or leaderboard point from this run.

10. **16 October 2026 — High-genus pictures and a failed transition lead.**
    Reused the original connected genus-48 surface and ran 256 independent
    Gaussian samples under each of three paired directional weightings.
    Rotating a checked harmonic reference gives a visible connection between
    Hodge decomposition and regularized phase directions. The scalar phase
    response agrees with the finite-Gaussian covariance formula and has a
    broad crossover near stiffness 0.20, not a phase transition. Changing
    smoothing shifts that scale substantially. This finite positive Gaussian
    model is analytic; no volume/genus/refinement limit was studied. CPU
    reconstruction checks all three GPU covariance matrices to relative error
    below 8e-13. [Images, definitions, response curves, and checks](notes/high-genus-flow.md).
    This surface is a synthetic intuition model, not the algebraic holdout.
    No upstream post for these pictures.

11. **16 October 2026 — Failed long-flow approximation and implementation repair.**
    Most traced paths on the piecewise-constant triangle field terminate at
    an immediate edge reversal (1,352–1,527 of 1,600 seeds across the three
    images). We retained short streamlets but rejected path trapping and
    length as physical observables. The covariance-based phase test does not
    use these paths. An initial CUDA matrix contraction also failed because
    cuBLAS was absent; CUDA reductions replaced it and independent CPU
    reconstruction checked the result. Neither failure was omitted or
    interpreted as a mathematical obstruction. [Recorded limits](notes/high-genus-flow.md#phase-response-and-what-failed).

12. **16 October 2026 — What counts as work.** The user's stated aim is to
    continue experiments, exact checks, and useful Lean formalization when
    appropriate, while keeping the motivation and outcomes honest. A public
    discussion contribution, a computational obstruction, a formalized partial
    lemma, and an accepted solution are separate outcomes. No new Lean theorem
    was attempted in entries 9–11. The upstream contribution tally remains two
    comments and zero accepted solves; there is no pending solve point from
    these experiments.

## Keeping this current

Append each new upstream post or submission with its actual date, permanent link, purpose, result, attribution, and limits; update the tally after verifying publication. Record corrections and acceptance decisions as dated updates. Preserve what earlier posts claimed at the time. A discussion post, passing local checks, and an accepted solve are distinct outcomes.

Also append substantive changes in research intuition, experiments, failed
approaches, and proposed tests, with dates and links. Distinguish a motivation
from an implemented experiment and a checked result. Keep the upstream tally
restricted to actual upstream activity.

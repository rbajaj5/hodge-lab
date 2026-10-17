# Contribution and research ledger

Contributions by **rbajaj5** to [hodge-computer/sextics](https://github.com/hodge-computer/sextics), alongside the motivation and experiments recorded in Hodge Lab.

Our intent is to understand the fixed problems, share reproducible results and unsuccessful approaches, credit prior mathematical work, and pursue solution credit through the project's verification process. This statement is recorded on **16 October 2026**; the entry below summarizes an earlier public post.

**Tally, checked against GitHub on 17 October 2026 (EDT):** 8 discussion contributions (six top-level comments and two replies); 0 authored issues; 0 pull requests; 0 reviews or review comments; 0 authored upstream commits; 0 accepted solves. Commits to Hodge Lab and unpublished experiments are separate from this upstream tally.

## Posts

1. **16 October 2026, 17:20 EDT / 21:20 UTC — [Holdout discussion #44: exact partial result](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18983276).** Shared an exact exclusion of the degree-seven `{chi_Y0, chi_X1}` denominator family, with reproducible code and certificate checks. The purpose was to contribute a checkable partial result and narrow the remaining search. The post credits fqlx's preceding calculations and the project's mathematical framework, and discloses Codex assistance. It reports 9,451 of 9,453 two-character families excluded **at the time of posting**, while explicitly leaving the full holdout unresolved. No Lean `HasCertificate` proof or solve submission was claimed. Evidence: [pinned explanation and code links](https://github.com/rbajaj5/hodge-lab/blob/dc2756300cbfa7a54d4735c60b852cd38ca8725e/notes/degree-seven-pair.md) and [passing CI](https://github.com/rbajaj5/hodge-lab/actions/runs/38968484482).

2. **16 October 2026, 18:52 EDT / 22:52 UTC — [Holdout discussion #44: family-13 exclusion](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18984345).** Shared the exact `{chi_X0, chi_Y0}` degree-seven exclusion and our reproduction of fqlx's distinct family-30 proof. The purpose was to fill the last two-character proof gap with a portable check, while crediting the complementary upstream work. The post records the 25 rational chart identities, independent coefficient reconstruction, corruption check, and [passing CI](https://github.com/rbajaj5/hodge-lab/actions/runs/38978064849). It links [immutable source and explanation](https://github.com/rbajaj5/hodge-lab/blob/5a1683fb82217aa49450614dc78d3b3e18b768c1/notes/x0-y0-exclusion.md), discloses Codex assistance, and explicitly leaves three-or-more-character denominators and higher degrees open. The combined count is 9,453/9,453 two-character families; no existence certificate, Lean proof, or accepted solve is claimed. The published body, author, and permanent URL were read back and verified.

3. **16 October 2026, 19:33 EDT / 23:33 UTC — [Holdout discussion #44: 132 three-character family exclusions](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18984710).** Shared the systematic test of all 136 third-character extensions of the `X0/Y0` pair: 112 exclusions via exact necessary-condition duals and 20 through shared-numerator chart covers. The post explicitly retains four unresolved extensions and the 16 additional coordinate triples that survived the relaxed pass. It links [immutable proofs, failed attempts, and explanation](https://github.com/rbajaj5/hodge-lab/blob/841cd0623c64d917a31ddf8433ddfbcc10c1260a/notes/three-character-families.md) and [passing CI](https://github.com/rbajaj5/hodge-lab/actions/runs/38981740498), credits fqlx and the prior mathematical framework, and discloses Codex assistance and the shared identity replayer. The purpose is to narrow a reproducible search region and make the four residual extensions available to collaborators. No Lean theorem, solution, improved unconditional degree bound, or leaderboard point is claimed. The body was previewed using GitHub's Markdown renderer; the published author and full body were independently read back and matched to the prepared text. [Publication receipt](results/degree7-triples/upstream-post.json).

4. **16 October 2026, 20:00 EDT / 17 October 2026, 00:00 UTC — [Holdout discussion #44: polynomial-syzygy exclusion of triple family 87](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18985544).** Shared one new complete exclusion, increasing the fixed-`X0/Y0` extension coverage to 133/136. Polynomial relations eliminate the shared numerator corrections; three cubic identities and a three-row physical identity finish the contradiction. The post includes the bounded method, the two unresolved family-115 charts, failed module searches and multiplier exports, and the limits of the literature connection. It links the [immutable proof and explanation](https://github.com/rbajaj5/hodge-lab/blob/cf75f3b67385c78769325db138104435ffa04b35/notes/polynomial-syzygies.md) and [passing full CI](https://github.com/rbajaj5/hodge-lab/actions/runs/38983831725), credits prior work, and discloses Codex assistance and shared verification code. No Lean theorem, general three-character exclusion, solve submission, or leaderboard point is claimed. The draft was previewed through GitHub Markdown; the published author, URL, and full body were read back and matched exactly. [Publication receipt](results/degree7-syzygies/upstream-post.json).

5. **16 October 2026, 20:24 EDT / 17 October 2026, 00:24 UTC — [Holdout discussion #44: rebuilt-syzygy exclusion of triple family 115](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18985755).** Shared the new complete exclusion, increasing fixed-`X0/Y0` extension coverage to 134/136. Rebuilding after the verified zeros and searching through degree five closes chart 10; its forced zero then closes chart 0. The post links [immutable proofs, visualization, and failed attempts](https://github.com/rbajaj5/hodge-lab/blob/b366f33c5a9421532d452ec4d15588c5f9998b7f/notes/syzygy-rebuild.md) and [passing full CI](https://github.com/rbajaj5/hodge-lab/actions/runs/38985896164). It records the ten larger-chart timeouts and two conditional chart improvements, credits prior work, and discloses Codex assistance and the shared identity replayer. The purpose is to supply another portable exclusion and reusable reductions while keeping the unresolved scope explicit. No Lean proof, solve submission, or leaderboard point is claimed. GitHub rendered the draft's four math blocks; the published author, URL, and full body were independently read back and matched exactly. [Publication receipt](results/degree7-syzygy-rebuild/upstream-post.json).

6. **16 October 2026, 21:08 EDT / 17 October 2026, 01:08 UTC — [Holdout discussion #44: the last two fixed-pair triple extensions](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18986224).** Shared the exact exclusions of families 16 and 137, completing 136/136 third-character extensions of the fixed `X0/Y0` pair and 136/152 selected triples. Two-row global identities and rebuilt Koszul syzygies close all ten charts. The post links [immutable proofs, dependencies, and failed searches](https://github.com/rbajaj5/hodge-lab/blob/17799c6c210373d4e7d2e9dcab837097161f8bfc/notes/koszul-rank-continuation.md) and [passing full CI](https://github.com/rbajaj5/hodge-lab/actions/runs/38988964935). It records exceptional-rank handling, bounded timeouts, two polynomial reconstructions, and the shared identity replayer; it credits prior work and discloses Codex assistance. Sixteen other selected triples and the full holdout remain unresolved. No Lean theorem, general degree-seven exclusion, solve submission, or leaderboard point is claimed. GitHub rendered the three math blocks and chart table before publication; the published author, URL, and full body were read back and matched exactly. [Publication receipt](results/degree7-rank-strata/upstream-post.json).

7. **17 October 2026, 07:10 EDT / 11:10 UTC — [Reply to post six: degree-three necessary ideals](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18997300).** Shared eleven family-coordinate vanishings across families 6, 8, 10, 149, and 152, with a pinned exact packet and cancellation visualizations. Six cubic identities and five rebuilt square identities reduce parameter spaces; no additional family is excluded and all sixteen remain open. The reply links [immutable code, explanation, visualizations, and failed attempts](https://github.com/rbajaj5/hodge-lab/blob/6d478ea5b8896935ebabf1ffd323afc66c26cd0e/notes/eisenbud-linear-strand.md), states the bounded degree-three search and the relaxed correction-space assumption, credits prior work, and discloses Codex assistance and shared verification code. It reports both local exact replays passing without claiming full CI, independent human review, a full resolution, a Lean proof, or solve credit. The existing thread was reread; GitHub's Markdown preview was inspected before posting. The published author, permanent URL, and complete body were independently read back and matched. [Publication receipt](results/eisenbud-linear-strand/upstream-post.json).

8. **17 October 2026, 07:32 EDT / 11:32 UTC — [Reply to post six: degree-four blocks close five triples](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18997670).** Shared exact exclusions of families 6, 8, 10, 149, and 152, increasing selected coverage to 141/152. Six blocks of six quadratics in five variables have a full quartic image; thirty fourth-power identities and replayed residual-sector proofs close the five triples. The reply links [immutable proof packets, explanation, visualizations, and failed attempts](https://github.com/rbajaj5/hodge-lab/blob/f131c2f9649fe5eb08f1a36caff7cc87162f5ad9/notes/eisenbud-quartic-strand.md), credits fqlx's pre-existing Y0/Y1 pair exclusion and the prior framework, and discloses Codex assistance and shared verification code. Both local physical reconstructions pass. It retains the timeout, slower alternative basis, and failed relaxed pair search, while leaving eleven selected triples and holdout open. No Lean proof, full resolution, improved unconditional degree bound, or solve credit is claimed. The full thread was reread and GitHub's mathematical Markdown preview inspected. Publication preceded the linked Hodge Lab push; the author, URL, and complete body were independently read back and matched. [Publication receipt](results/eisenbud-quartic-strand/upstream-post.json).

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

13. **16 October 2026 — From sampled directions to complete three-character families.**
    The user's request was to make the holdout search systematic. We tested
    all 136 third-character extensions of the previously difficult `X0/Y0`
    pair, plus all 20 coordinate-character triples, giving 152 distinct
    families after four overlaps. All coefficients in each retained E1
    character space vary over the complex numbers. Exact obstruction
    functionals replace the earlier numerical projection: 112 families
    reduce to the already excluded pair. This extends fqlx's enlarged-
    correction pair strategy; it is not a new theorem from imaginary geometry.
    [Selection, equations, attribution, and coverage map](notes/three-character-families.md).

14. **16 October 2026 — Successful shared-numerator continuation and retained failures.**
    The relaxed test left 40 families unresolved. For the 24 remaining
    `X0/Y0` extensions we restored the actual shared numerator coefficients,
    retaining the full correction space allowed by exact stabilizer projection.
    Seventeen complete chart covers succeeded. Three more succeeded after
    removing coefficients already proved zero and repeating the remaining
    charts. Their original failed charts remain in the packet. The result is
    **132 excluded and four unresolved X0/Y0 extensions**, or 132 excluded
    and 20 unresolved families in the combined selection. All 24 initial
    shared-family runs completed inside their 60-second limits. No numerical
    failure, timeout, or unresolved chart is treated as a nonexistence proof.
    The four residual third characters are `(0,1,0)`, `(3,0,1)`, `(4,2,3)`,
    and `(5,3,0)`; their 13 terminal charts need stronger methods. The other
    16 coordinate triples received only the relaxed pass. [Proof packets,
    stopping rules, and failed attempts](notes/three-character-families.md#what-remains-and-what-failed).

15. **16 October 2026 — Evidence and scope of this batch.** Exact replay checks
    6,219 physical duals, 265 square identities, and 70 chart attempts with
    1,739 inferences. A separate polynomial construction uses the pinned target
    and opposite division order; it shares the identity replayer and is not
    independent human review. Damaged identities are rejected, and all 28
    unit tests pass. No Lean theorem was attempted: the useful output here is
    the portable rational obstruction and explicit remaining families. This
    covers 152 of 428,536 possible triples; the unconditional degree bound
    remains seven and holdout remains unsolved. The checkpoint-read race in an
    early pilot was an implementation failure, repaired with atomic writes,
    not a mathematical result. This batch was initially recorded only in
    Hodge Lab. After the proof commit passed CI, it was shared as post 3 above;
    no solve submission is counted.

16. **16 October 2026 — Keep the simpler baseline competitive.** The comparison
    with sequence-model research suggests evaluating an ambitious mechanism
    against improvements to an established method. The analogy has limits:
    [Mamba](https://arxiv.org/abs/2312.00752) changes sequence processing and its
    computational scaling, whereas [RoPE](https://arxiv.org/abs/2104.09864),
    [ALiBi](https://arxiv.org/abs/2108.12409), and
    [YaRN](https://arxiv.org/abs/2309.00071) concern positional representation
    or context extension; their original papers predate Mamba. This is not a
    claim that one settles the other's research questions. In Hodge Lab, the
    practical lesson is to compare geometric proposals with exact symmetry
    and algebraic baselines, and attribute success to the method that actually
    supplied the verified obstruction. The 132-family result does not establish
    an advantage for anisotropy, GPUs, or imaginary geometry.

17. **16 October 2026 — Algebra as composition: Marco Kuhlmann's dependency structures.**
    The user supplied [Kuhlmann's 2007 dissertation](https://www.ps.uni-saarland.de/Publications/documents/kuhlmann2007dependency.pdf).
    Its dependency algebras connect rules for composing structures with
    grammatical expressivity and parsing complexity; sections 3.2, 4.2, and
    8.3 are relevant. This is a more precise methodological connection than
    treating every matrix problem as the same algebraic problem. A proposed,
    **unexecuted** follow-up is to examine variable/constraint incidence and
    separator sizes in the four residual holdout systems, then test whether
    elimination can be organized into smaller pieces while preserving shared
    variables and compatibility conditions. The current relaxed-to-shared
    comparison already demonstrates why losing those conditions matters.
    No reduction from polynomial certificate search to Kuhlmann's grammar
    algorithms, complexity bound, or new holdout theorem has been established
    from this analogy.

18. **16 October 2026 — Polynomial syzygies turn the literature lead into a new exclusion.**
    The user supplied David Yang's paper on equivariant sheaves and Koszul
    cohomology and asked us to pursue that direction. We tested affine
    polynomial multipliers of the actual shared correction equations,
    producing denominator-only identities while retaining all numerator
    compatibility. Across three charts, 94 directions extend the bounded
    constant-multiplier baseline. Three cubic power identities and a final
    three-row physical identity exclude the complete triple with third
    character `(3,0,1)` (our family 87). Cumulative coverage is 133/136 fixed-
    pair extensions, with three still open; holdout remains unsolved. The
    computation is ordinary exact polynomial elimination. No application of
    Yang's line-bundle cohomology theorem has been proved.
    [Proof, comparison, checks, and scope](notes/polynomial-syzygies.md).
    After the proof commit passed full CI, this was published as post 4 above.

19. **16 October 2026 — Unsuccessful searches and the choice to seek powers.**
    Full Singular module-syzygy searches timed out at 45 seconds on all three
    charts. A Gröbner calculation on family 87 suggested a stronger component
    vanishing, but multiplier exports timed out at 60 and 90 seconds.
    A direct bounded search for linear memberships was also insufficient.
    Seeking coordinate powers instead supplied the three useful cubes, each
    with an exact rational identity. Two charts of family 115 gain cubic
    vanishings but still survive the configured degree-four continuation.
    All failed bounds and CAS-only observations are separated from the
    portable proof. The next proposed step is to rebuild its syzygy system
    after those vanishings; this remains unexecuted in this batch.
    [Attempts and reproducible inputs](results/degree7-syzygies/experiments.json).

20. **16 October 2026 — Etingof and Kelly: useful hypotheses, no automatic transfer.**
    The later PDFs are Etingof's paper on Koszul duality and PBW in symmetric
    tensor categories, and Jack Kelly's thesis on exact categories and derived
    analytic algebra. We examined the introductions and relevant deformation
    and duality statements. Etingof's low-degree flatness criterion requires
    a Koszul special fiber; Kelly's equivalences require the relevant
    homotopical/operadic constructions. Neither setup has been established
    for holdout. These sources guide questions about higher relations and
    compatibility, but do not certify our calculation or justify a universal
    degree-three stopping rule. The source PDFs and private conversations
    are not republished here. [Sources and interpretation](notes/polynomial-syzygies.md#how-the-papers-guided-the-experiment).

21. **16 October 2026 — Rebuild after the proven zeros.** The proposed
    family-115 rebuild was executed. Affine syzygies alone and power searches
    through degree four still failed. A degree-five search on chart `a10=1`
    supplied two square identities; a subsequent fourth-power identity and
    physical contradiction closed that chart. Setting its coefficient to
    zero then closed chart `a0=1`. Family 115 is excluded, raising coverage
    to 134/136 fixed-pair extensions. Both polynomial constructions replay
    the dependencies and reject corrupted or unjustified proof steps.
    [Proof and exact packets](notes/syzygy-rebuild.md).
    After the proof commit passed full CI, this was published as post 5 above.

22. **16 October 2026 — Larger families and unsuccessful computations.** All
    ten remaining third-component charts of families 16 and 137 were attempted
    with full shared numerator corrections and affine polynomial multipliers.
    Every full search reached its 120-second limit. Six later runs retained
    partial checkpoints after checkpoint export was added; the earlier four
    exported none. Two checkpoints give new cubic vanishings on their
    respective charts, but neither closes through the tested degree-four
    continuation. They are not global family vanishings. Larger CAS exports
    timed out, and two quadratic syzygy searches were cancelled after a more
    economical lead emerged. An unused 39 MB CAS unit export was superseded
    by the smaller checked proof. [Bounds, logs, and retained failures](results/degree7-syzygy-rebuild/experiments.json).

23. **16 October 2026 — Visualizing the algebra rather than substituting a picture for it.**
    The new figure shows the actual cancellation-support matrix and the
    dependency chain from syzygies to powers, chart exclusion, and refinement.
    Its colors count multiplier monomials; they do not represent conditioning
    or a physical field. The Hodge intuition is the annihilator of the
    correction map. No phase transition or new geometric theorem is inferred
    from this figure. [Reproducible visualization](results/degree7-syzygy-rebuild/syzygy-proof-map.png).

24. **16 October 2026 — Braids and arithmetic: possible next tools.** The user
    asked whether the braid and supercongruence projects could help. A kernel
    bundle around rank-drop loci could motivate a monodromy experiment, but
    no braid action or compatible transport on this certificate system has
    been constructed. Ordinary Hermitian Gram spectra do not automatically
    produce Ginibre eigenvalue braids. Modular pilot elimination followed by
    rational reconstruction and exact replay is a more immediate proposed
    computational improvement. Neither proposal was used in the family-115
    proof; no supercongruence theorem is transferred. The syzygy approach
    already produced another complete restricted-family result.
    [Sources and explicit limits](notes/syzygy-rebuild.md#braids-hodge-projection-and-arithmetic-as-research-tools).

25. **16 October 2026 — A further family-16 lead after the fifth proof packet.**
    Composing the two conditional chart identities back to physical equations
    leaves only linear multipliers. Homogenizing these multipliers gives two
    identities against the unnormalized family: `a1^3=a9^3=0`, with ten and
    eight physical products. Both polynomial constructions replay them and
    reject a corrupted coefficient. Thus these two zeros hold throughout
    family 16 after its original first-pass reduction. The family remains
    unresolved; rebuilding its five charts is the next unexecuted step.
    This strengthening is recorded after the immutable fifth-post packet and
    is not a sixth public post. [Small checker](algebra/check_family16_global_cubes.py).

26. **16 October 2026 — Three syzygy sources and a precise next question.**
    Read the relevant definitions and theorem statements in the user's
    Eisenbud, Ein--Lazarsfeld--Yang, and Caucci--Lahoz links. The polynomial
    matrix viewpoint fits our existing equations directly; the geometric
    vanishing and bundle-stability theorems require identifications and
    hypotheses we have not established. The proposed next experiment is to
    compare bounded syzygies with exact elimination on rank strata, retaining
    every exceptional branch. This assessment reuses the previously recorded
    specialization counterexample; it is not a new obstruction, an executed
    rank-stratification experiment, or a sixth upstream post.
    [Sources, assumptions, and proposed calculation](notes/syzygy-literature-map.md).

27. **16 October 2026 — A local rank obstruction becomes a two-row identity.**
    Ten bounded rank-block searches all remained unresolved after discovering
    one new linear relation per family. Each relation has a simpler global
    proof: two unnormalized physical rows give `L^2=(9/2)Ej-27Ek`. Hence `L=0`
    even on exceptional rank loci. No nonconstant pivot is silently inverted.
    The search was local to small blocks, not a complete stratification of
    the full correction matrix. [Identities, bounds, and reasoning](notes/koszul-rank-continuation.md).

28. **16 October 2026 — Rebuilding Koszul syzygies closes families 16 and 137.**
    The family-16 global cubes and new linear identity close chart 11; its
    forced zero makes the other four charts tractable. For family 137,
    composing and homogenizing conditional relations supplies two global
    cubes after its linear vanishing. Chart 13 then closes, and its zero
    closes the remaining four charts. Both polynomial constructions replay
    the complete dependency chain. Combined coverage is now 136/136 fixed-
    `X0/Y0` extensions and 136/152 selected triples; holdout remains unsolved.
    This is computation in the gradient Koszul complex and its correction
    map, not an application of a geometric Koszul-cohomology vanishing
    theorem. [Complete proof and checks](notes/koszul-rank-continuation.md).
    After the proof commit passed full CI, this was published as post 6 above.

29. **16 October 2026 — Failed bounds and the successful change of order.**
    Three of four initial syzygy follow-ups timed out at 120 seconds; an
    unrefined family-137 chart timed out again at 150 seconds. Their retained
    checkpoints led to useful reductions but are not themselves exclusions.
    All eight final rebuilds completed within their stated limits. A
    generic-pivot pilot with unhandled exceptional guards was discarded as
    a proof route. The successful intervention was to substitute verified
    vanishings before rebuilding shared correction syzygies, then export
    exact powers or unit identities. CPU exact arithmetic supplied the
    proofs; no GPU, braid, optical, or imaginary-geometry advantage is
    asserted. [Logs and retained discovery inputs](results/degree7-rank-strata/).

30. **16 October 2026 — Visualizing the actual Koszul correction map.**
    Added three companions to post six: polynomial support of the correction
    map and its selected left syzygies, the exact two-row image/cokernel
    obstruction, and the dependencies closing all ten charts. The displayed
    173 identities replay 29,031 physical products against stored equations.
    Twenty rational checks verify a local weighted-projection formula,
    including its zero-rank branch. In this block, changing equation weights
    can reduce the residual fraction from 97.3% to 0.36% without removing
    the exact obstruction. This clarifies a limitation of our Gram-ranking
    intuition; it is not a new search benchmark. Dubedat motivates the
    operator viewpoint, while genus and Chatterjee's stochastic frameworks
    would require further constructions. No such identification is claimed.
    The ten unresolved initial rank searches and four later timeouts remain
    visible in the proof history. No new family exclusion or upstream post;
    the contribution tally remains six. [Figures, sources, and reproducible
    checks](notes/koszul-map-visualizations.md).

31. **16 October 2026 — Standard parameter optimization with exact follow-up.**
    Optimized the surviving coefficients in each of the 16 other selected
    holdout triple families. Two L-BFGS-B starts per bounded real chart use
    the full 840-column correction map and fixed equation weights. The
    optimizer and uniform-random comparator each use 2,078 objective
    evaluations; their starting distributions differ as recorded. The median
    best-score reduction is 91.9%, but all 32 distinct rationalized finalists
    fail exact checks. Ten of the 16 optimized winners round into one- or
    two-character sectors already excluded; seven float winners touch the
    parameter box boundary. Nineteen starts hit iteration/evaluation limits.
    Both polynomial assemblies verify all 26,880 correction pairings, and
    separately assembled numerical scores agree to relative error below
    1.29e-15. No new family exclusion, solution, or upstream post follows.
    [Complete history, figure, checks, and proposed next tests](notes/koszul-parameter-optimization.md).
    The contribution policy welcomes reproducible partial results and failed
    searches but asks for substantive updates instead of a running transcript.
    This batch stays in Hodge Lab; the upstream tally remains six, reconfirmed
    against discussion #44.

32. **16 October 2026 — Visual focus: where the parameter search moves.**
    Added an interactive view of the existing 16-family optimization batch.
    The triangle shows squared coefficient-norm shares of the denominator's
    three characters; its paths are linked to the best residual seen at each
    evaluation. All 4,156 recorded evaluations remain available. Same-character
    Gram cross terms are retained, with 64 direct polynomial checks. Small
    floating-point shares and exact character loss after rounding are labeled
    separately. All 32 failed rational finalists remain in the source packet.
    Browser checks cover desktop/mobile layouts, controls, tooltips, and state
    restoration. This is an interpretation of an existing search, not a new
    exclusion, phase transition, or imaginary-geometry identification. The
    user's current priority is visual understanding; no new upstream post
    was made and the tally remains six.
    Publication checks exposed an earlier reporting bug: numeric verification
    overwrote archived values before the figure checked their hashes. Check
    mode now preserves those reports; replacing them requires an explicit
    flag. The score tolerance and exact certificate checks are unchanged.
    [Explorer, interpretation, and checks](notes/koszul-parameter-optimization.md#interactive-view-of-character-concentration).

33. **16 October 2026 — Geometry of the Koszul-induced operator.**
    Built a circle-to-ellipse view of three previously rejected rational
    denominators: the first optimized endpoints with one, two, and three
    characters, from families 1, 2, and 4. Two response observables and an
    exact left syzygy make a three-dimensional coefficient-space picture.
    All 2,520 columns are reconstructed and checked with two polynomial
    APIs. The fit button matches the two displayed response coordinates;
    the syzygy height remains nonzero for every correction. A nearly round
    response ellipse therefore still fails to certify a solution.
    Dubedat motivates the operator, inverse-Gram, and Gaussian-covariance
    viewpoint; no dimer/GFF or genus identification is asserted. The failed
    finalists remain in their original packet. Browser label-spacing failures
    were repaired; 126 layout/state combinations pass. Added an interactive
    explorer and static PNG/SVG companion, with source and checks. No new
    search or upstream post; the contribution tally remains six.
    [Derivation, limits, and visualizations](notes/koszul-geometric-map.md).

34. **16 October 2026 — Denominator sweep and an interior-character search.**
    Varied `D_42 + s D_272 + t D_294` in a fixed pair of viewing frames. All
    81 sampled rational full-map ranks are checked by rational elimination
    and separate modular elimination: 72 have rank 720, eight rank 713, and
    the origin rank 690. The two-row projection can also collapse while the
    full rank remains 720. Restricting an archived family-4 necessity yields
    a common exact dual that rejects the entire complex parameter plane;
    this does not exclude family 4. A separate bounded SLSQP follow-up uses
    two balanced starts in each of families 1, 4, and 149, retaining at least
    10% character energy during feasible evaluations. All six runs reach
    their iteration limit; all six distinct rounded, three-character
    finalists are rejected exactly. The 493 evaluations, rejected candidates,
    stop reasons, and implementation corrections remain recorded. Two
    polynomial assemblies check the physical equations; no fresh independent
    agent or human review is claimed. Added a live denominator explorer,
    static PNG/SVG, exact replay, and 72 desktop/mobile presentation checks.
    Dubedat supplies an operator/covariance motivation; no imaginary-geometry
    identification, statistical phase transition, Lean proof, or holdout
    solve is claimed. Upstream files remain unchanged and no upstream comment
    was posted; the public contribution tally remains six.
    [Derivation, visualizations, failed attempts, and reproduction](notes/koszul-denominator-sweep.md).

35. **17 October 2026 — Read the expanded discussion; repair CI portability.**
    Checked the thread inventory (15 top-level posts and five replies) and
    read the six newer updates, including the corrected closing edit.
    Recorded the reported new character
    exclusion, support obstruction, conditional geometric limitations, and
    still-missing target image. The new character triple is outside our
    152-family selection, so our sixteen remaining selected families are
    unchanged. This coverage comparison is checked; the newly linked proof
    packets have not been independently replayed here. Also recorded the new
    upstream participation policy. Our preceding CI run failed on Windows
    versus Linux path separators in a source-manifest key after completing
    the arithmetic checks. Standardized those keys without changing source
    hashes, mathematical data, or tolerances, and reran the sweep check.
    No upstream message or solve submission; our contribution tally remains six.
    [Discussion sources, implications, and CI correction](notes/discussion-checkpoint-2026-10-17.md).

36. **17 October 2026 — Eisenbud linear strands, with inspectable cancellation.**
    Extended the necessary-ideal power search from degree two to degree three
    in all sixteen remaining selected triples. Six cubic identities force
    zeros in families 6, 8, 10, 149, and 152; rebuilding yields five more
    square-zero coordinates. These are eleven family-coordinate vanishings
    using three raw indices, not eleven distinct raw indices. All sixteen
    families remain unresolved and the selected-family exclusion count stays
    136/152. Retained all 26 stages, 1,149 syzygy vectors, sixteen power
    identities (five are redundant cubes), and every bounded failure.
    Exact replay and a separate physical polynomial reconstruction pass;
    52 rational and modular ranks agree. The interactive explorer exposes
    each identity's monomial cancellation, including empty relation spaces;
    the static figure includes all families. All 111 browser layout/state
    checks pass. Recorded the standing visualization requirement in AGENTS.md.
    Corrected a preliminary chat miscount of seven initial vanishings to six.
    The first Linux CI job stopped on a CRLF/LF target-file fingerprint;
    normalized text hashing and replayed both checks without changing any
    mathematical payload. The failed run remains linked in the note.
    No full resolution, phase transition, new family exclusion, or solve is
    claimed. [Result, visualizations, rationale, failures, and checks](notes/eisenbud-linear-strand.md).
    Shared one consolidated reply in the existing holdout thread, recorded as
    upstream contribution 7 above; the earlier numerical and visual notebooks
    were not posted as additional discussion messages.
    The corrected Linux `eisenbud-strand` job subsequently passed both exact
    replays and the visualization-data check at the linked publication commit.

37. **17 October 2026 — Degree-four blocks close five selected triples.**
    Tested families 6, 8, 10, 149, and 152 after the preceding reductions.
    Full degree-four maps found thirty family-coordinate fourth-power
    identities; inspection reduced their proof to six blocks of six
    quadratics in five variables. Each block has ranks 6, 30, and 70 in
    degrees two, three, and four, with a full quartic image. Replayed the
    original physical necessities, inherited zeros, and all residual pair
    and single-character proofs using two polynomial constructions. All
    five complete triples are excluded, increasing selected coverage to
    141/152. Eleven selected triples and holdout remain unresolved.
    Retained the 300-second family-8 timeout, its completed 600-second-bound
    sparse-order retry, an invertible equation-basis experiment that did not
    improve the observed runtime, and the failed necessary-ideal search
    through degree four on Y0/Y1. Its shared-numerator closure reproduces
    fqlx's earlier pair result and is credited as a dependency.
    Added a scientific figure and an interactive view of forty exact
    identities; all 120 browser layouts pass. A presentation-test assumption
    about monomial ordering was corrected and is recorded. The small-block
    proof emerged after the larger calculations; no universal block theorem
    or phase transition is claimed. No Lean proof or accepted solve.
    [Proof, rationale, visualizations, checks, and unsuccessful attempts](notes/eisenbud-quartic-strand.md).
    Shared one consolidated upstream reply, recorded as contribution 8 above.
    The Linux `eisenbud-quartic` job passed every new arithmetic and figure-data
    check at the pinned publication commit; its receipt is retained in the note.

## Keeping this current

Append each new upstream post or submission with its actual date, permanent link, purpose, result, attribution, and limits; update the tally after verifying publication. Record corrections and acceptance decisions as dated updates. Preserve what earlier posts claimed at the time. A discussion post, passing local checks, and an accepted solve are distinct outcomes.

Also append substantive changes in research intuition, experiments, failed
approaches, and proposed tests, with dates and links. Distinguish a motivation
from an implemented experiment and a checked result. Keep the upstream tally
restricted to actual upstream activity.

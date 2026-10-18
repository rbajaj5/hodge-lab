# Contribution and research ledger

Contributions by **rbajaj5** to [hodge-computer/sextics](https://github.com/hodge-computer/sextics), alongside the motivation and experiments recorded in Hodge Lab.

Our intent is to understand the fixed problems, share reproducible results and unsuccessful approaches, credit prior mathematical work, and pursue solution credit through the project's verification process. This statement is recorded on **16 October 2026**; the entry below summarizes an earlier public post.

**Historical publication tally, through 17 October 2026 (EDT):** 24 discussion contributions (originally seventeen top-level comments and seven replies); 0 authored issues; 1 draft maintenance pull request; 0 reviews or review comments; 0 merged authored upstream commits; 0 accepted solves. Commits to Hodge Lab and unpublished experiments are separate from this upstream tally. The maintainer consolidated several holdout updates on 17 October; this records publication history, not the current number of visible comments. See [the maintainer summary](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-19003085) and checkpoint 70 below. Receiving credit does not increase this tally.

## Posts

1. **16 October 2026, 17:20 EDT / 21:20 UTC — [Holdout discussion #44: exact partial result](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18983276).** Shared an exact exclusion of the degree-seven `{chi_Y0, chi_X1}` denominator family, with reproducible code and certificate checks. The purpose was to contribute a checkable partial result and narrow the remaining search. The post credits fqlx's preceding calculations and the project's mathematical framework, and discloses Codex assistance. It reports 9,451 of 9,453 two-character families excluded **at the time of posting**, while explicitly leaving the full holdout unresolved. No Lean `HasCertificate` proof or solve submission was claimed. Evidence: [pinned explanation and code links](https://github.com/rbajaj5/hodge-lab/blob/dc2756300cbfa7a54d4735c60b852cd38ca8725e/notes/degree-seven-pair.md) and [passing CI](https://github.com/rbajaj5/hodge-lab/actions/runs/38968484482).

2. **16 October 2026, 18:52 EDT / 22:52 UTC — [Holdout discussion #44: family-13 exclusion](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18984345).** Shared the exact `{chi_X0, chi_Y0}` degree-seven exclusion and our reproduction of fqlx's distinct family-30 proof. The purpose was to fill the last two-character proof gap with a portable check, while crediting the complementary upstream work. The post records the 25 rational chart identities, independent coefficient reconstruction, corruption check, and [passing CI](https://github.com/rbajaj5/hodge-lab/actions/runs/38978064849). It links [immutable source and explanation](https://github.com/rbajaj5/hodge-lab/blob/5a1683fb82217aa49450614dc78d3b3e18b768c1/notes/x0-y0-exclusion.md), discloses Codex assistance, and explicitly leaves three-or-more-character denominators and higher degrees open. The combined count is 9,453/9,453 two-character families; no existence certificate, Lean proof, or accepted solve is claimed. The published body, author, and permanent URL were read back and verified.

3. **16 October 2026, 19:33 EDT / 23:33 UTC — [Holdout discussion #44: 132 three-character family exclusions](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18984710).** Shared the systematic test of all 136 third-character extensions of the `X0/Y0` pair: 112 exclusions via exact necessary-condition duals and 20 through shared-numerator chart covers. The post explicitly retains four unresolved extensions and the 16 additional coordinate triples that survived the relaxed pass. It links [immutable proofs, failed attempts, and explanation](https://github.com/rbajaj5/hodge-lab/blob/841cd0623c64d917a31ddf8433ddfbcc10c1260a/notes/three-character-families.md) and [passing CI](https://github.com/rbajaj5/hodge-lab/actions/runs/38981740498), credits fqlx and the prior mathematical framework, and discloses Codex assistance and the shared identity replayer. The purpose is to narrow a reproducible search region and make the four residual extensions available to collaborators. No Lean theorem, solution, improved unconditional degree bound, or leaderboard point is claimed. The body was previewed using GitHub's Markdown renderer; the published author and full body were independently read back and matched to the prepared text. [Publication receipt](results/degree7-triples/upstream-post.json).

4. **16 October 2026, 20:00 EDT / 17 October 2026, 00:00 UTC — [Holdout discussion #44: polynomial-syzygy exclusion of triple family 87](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18985544).** Shared one new complete exclusion, increasing the fixed-`X0/Y0` extension coverage to 133/136. Polynomial relations eliminate the shared numerator corrections; three cubic identities and a three-row physical identity finish the contradiction. The post includes the bounded method, the two unresolved family-115 charts, failed module searches and multiplier exports, and the limits of the literature connection. It links the [immutable proof and explanation](https://github.com/rbajaj5/hodge-lab/blob/cf75f3b67385c78769325db138104435ffa04b35/notes/polynomial-syzygies.md) and [passing full CI](https://github.com/rbajaj5/hodge-lab/actions/runs/38983831725), credits prior work, and discloses Codex assistance and shared verification code. No Lean theorem, general three-character exclusion, solve submission, or leaderboard point is claimed. The draft was previewed through GitHub Markdown; the published author, URL, and full body were read back and matched exactly. [Publication receipt](results/degree7-syzygies/upstream-post.json).

5. **16 October 2026, 20:24 EDT / 17 October 2026, 00:24 UTC — [Holdout discussion #44: rebuilt-syzygy exclusion of triple family 115](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18985755).** Shared the new complete exclusion, increasing fixed-`X0/Y0` extension coverage to 134/136. Rebuilding after the verified zeros and searching through degree five closes chart 10; its forced zero then closes chart 0. The post links [immutable proofs, visualization, and failed attempts](https://github.com/rbajaj5/hodge-lab/blob/b366f33c5a9421532d452ec4d15588c5f9998b7f/notes/syzygy-rebuild.md) and [passing full CI](https://github.com/rbajaj5/hodge-lab/actions/runs/38985896164). It records the ten larger-chart timeouts and two conditional chart improvements, credits prior work, and discloses Codex assistance and the shared identity replayer. The purpose is to supply another portable exclusion and reusable reductions while keeping the unresolved scope explicit. No Lean proof, solve submission, or leaderboard point is claimed. GitHub rendered the draft's four math blocks; the published author, URL, and full body were independently read back and matched exactly. [Publication receipt](results/degree7-syzygy-rebuild/upstream-post.json).

6. **16 October 2026, 21:08 EDT / 17 October 2026, 01:08 UTC — [Holdout discussion #44: the last two fixed-pair triple extensions](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18986224).** Shared the exact exclusions of families 16 and 137, completing 136/136 third-character extensions of the fixed `X0/Y0` pair and 136/152 selected triples. Two-row global identities and rebuilt Koszul syzygies close all ten charts. The post links [immutable proofs, dependencies, and failed searches](https://github.com/rbajaj5/hodge-lab/blob/17799c6c210373d4e7d2e9dcab837097161f8bfc/notes/koszul-rank-continuation.md) and [passing full CI](https://github.com/rbajaj5/hodge-lab/actions/runs/38988964935). It records exceptional-rank handling, bounded timeouts, two polynomial reconstructions, and the shared identity replayer; it credits prior work and discloses Codex assistance. Sixteen other selected triples and the full holdout remain unresolved. No Lean theorem, general degree-seven exclusion, solve submission, or leaderboard point is claimed. GitHub rendered the three math blocks and chart table before publication; the published author, URL, and full body were read back and matched exactly. [Publication receipt](results/degree7-rank-strata/upstream-post.json).

7. **17 October 2026, 07:10 EDT / 11:10 UTC — [Reply to post six: degree-three necessary ideals](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18997300).** Shared eleven family-coordinate vanishings across families 6, 8, 10, 149, and 152, with a pinned exact packet and cancellation visualizations. Six cubic identities and five rebuilt square identities reduce parameter spaces; no additional family is excluded and all sixteen remain open. The reply links [immutable code, explanation, visualizations, and failed attempts](https://github.com/rbajaj5/hodge-lab/blob/6d478ea5b8896935ebabf1ffd323afc66c26cd0e/notes/eisenbud-linear-strand.md), states the bounded degree-three search and the relaxed correction-space assumption, credits prior work, and discloses Codex assistance and shared verification code. It reports both local exact replays passing without claiming full CI, independent human review, a full resolution, a Lean proof, or solve credit. The existing thread was reread; GitHub's Markdown preview was inspected before posting. The published author, permanent URL, and complete body were independently read back and matched. [Publication receipt](results/eisenbud-linear-strand/upstream-post.json).

8. **17 October 2026, 07:32 EDT / 11:32 UTC — [Reply to post six: degree-four blocks close five triples](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18997670).** Shared exact exclusions of families 6, 8, 10, 149, and 152, increasing selected coverage to 141/152. Six blocks of six quadratics in five variables have a full quartic image; thirty fourth-power identities and replayed residual-sector proofs close the five triples. The reply links [immutable proof packets, explanation, visualizations, and failed attempts](https://github.com/rbajaj5/hodge-lab/blob/f131c2f9649fe5eb08f1a36caff7cc87162f5ad9/notes/eisenbud-quartic-strand.md), credits fqlx's pre-existing Y0/Y1 pair exclusion and the prior framework, and discloses Codex assistance and shared verification code. Both local physical reconstructions pass. It retains the timeout, slower alternative basis, and failed relaxed pair search, while leaving eleven selected triples and holdout open. No Lean proof, full resolution, improved unconditional degree bound, or solve credit is claimed. The full thread was reread and GitHub's mathematical Markdown preview inspected. Publication preceded the linked Hodge Lab push; the author, URL, and complete body were independently read back and matched. [Publication receipt](results/eisenbud-quartic-strand/upstream-post.json).

9. **17 October 2026, 07:45 EDT / 11:45 UTC — [Holdout discussion #44: nine more quartic triple exclusions](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18997810).** Shared exact exclusions of families 1, 2, 4, 5, 7, 9, 15, 39, and 150, increasing selected coverage to 150/152. All 33 small blocks were tested; 62 fourth-power identities and explicit residual-sector replays close the nine triples. The full quartic maps for 17 and 151 fail to force coordinate fourth powers, and those families remain open. The post links [immutable proofs, visualizations, and failures](https://github.com/rbajaj5/hodge-lab/blob/d44f72a44a36d7f58b623b8c905bd2f0f8e6c8a0/notes/eleven-quartic.md), credits fqlx's existing family-30 proof as a reproduced dependency, and discloses Codex assistance and shared verification code. Both local physical reconstructions and 330 presentation checks pass. The existing discussion was reread; GitHub's mathematical Markdown preview was inspected. Posted as a self-contained top-level result, followed immediately by the linked repository push. The author, body, URL, and absence of a reply parent were read back and matched. No remote CI result was claimed before it ran, and no Lean proof, improved degree bound, solve submission, or leaderboard point is claimed. [Publication receipt](results/eleven-quartic/upstream-post.json).

10. **17 October 2026, 08:16 EDT / 12:16 UTC — [Holdout discussion #44: shared numerators close family 17](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18998140).** Shared one new complete selected-family exclusion and one exact linear reduction in the remaining family 151. The shared-numerator chart forces a56=0 in family 17; rebuilding yields a full degree-six image and five sixth-power identities, followed by the explicitly reproduced fqlx X1/Y1 proof. Selected coverage is 151/152. The post links [immutable proofs, before/after visualizations, and failed attempts](https://github.com/rbajaj5/hodge-lab/blob/5e768a2c1261f12fe124bcf9d62ee768fdd482b6/notes/remaining-triples-shared.md), credits dependencies and the mathematical framework, and discloses Codex assistance and shared verification code. Both local physical reconstructions pass, with 17 chart traces, 167 exact inferences, seven corruption checks, and 21 presentation checks. The complete discussion was reread and GitHub's mathematical preview inspected. Posted as one self-contained top-level result before the linked Hodge Lab push; author, complete body, permanent URL, and absence of a reply parent were read back and matched. Remote CI was not claimed before running. No Lean proof, solve PR, improved unconditional degree bound, or leaderboard credit is claimed. [Publication receipt](results/remaining-triples-shared/upstream-post.json).

11. **17 October 2026, 08:34 EDT / 12:34 UTC — [Holdout discussion #44: polynomial multipliers close family 151](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18998404).** Shared the exact exclusion of X1/Y0/Y1, completing 152/152 selected triples while leaving other triple supports, larger supports, higher degrees, and holdout open. Polynomial multipliers of the rebuilt shared-numerator equations produce 96 additional cubic relations; three correctly graded small blocks force thirteen fourth powers, and two direct residual charts contradict. The post links [immutable proof packets, visualizations, and failures](https://github.com/rbajaj5/hodge-lab/blob/a825be71140bb5c70327c2229c208df7d959e164/notes/family151-multipliers.md), credits the preceding framework and calculations, and discloses Codex assistance and shared verification code. Both physical reconstructions pass. Failed degree-three searches, three bounded timeouts, and a discarded mixed-degree pilot remain documented. The entire existing thread was reread, GitHub's mathematical preview inspected, and the result posted before the linked repository push. The complete published body, author, permanent URL, and lack of a reply parent were independently read back and matched. No Lean proof, solve PR, unconditional degree-bound improvement, or leaderboard point is claimed. Remote CI was still running at publication. [Publication receipt](results/family151-multipliers/upstream-post.json).

12. **17 October 2026, 09:08 EDT / 13:08 UTC — [Holdout discussion #44: 132 further X1/Y1 triple exclusions](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18998764).** Shared 132 new complete three-character exclusions, completing all 136 extensions of X1/Y1 and increasing our selected union to 284 triples. Necessary blocks close 123; shared-numerator charts and reconstruction finish nine. The post links [immutable proofs, exact graded-map visualizations, and failed searches](https://github.com/rbajaj5/hodge-lab/blob/c126e8bbc6ccc3f4c37a14d6be20809bdbccef25/notes/x1y1-extensions.md), explicitly credits fqlx's reproduced pair-30 dependency, and discloses Codex assistance and shared verification code. Both physical constructions pass. Nine unsuccessful first-pass systems and two initially unresolved charts remain recorded, alongside their later closures. The thread and current participation policy were reread, and GitHub's mathematical preview was inspected. Posted before the linked Hodge Lab push; the complete body, author, permanent URL, and absence of a reply parent were read back and matched. The current thread confirms ten top-level contributions and two replies. Other triple supports, larger supports, higher degrees, and holdout remain open; no Lean proof, solve PR, degree-bound improvement, or leaderboard credit is claimed. Remote CI was not claimed at publication. [Publication receipt](results/x1y1-extensions/upstream-post.json).

13. **17 October 2026, 09:28 EDT / 13:28 UTC — [Holdout discussion #44: 132 Y0/X1 extensions](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18998994).** Shared one consolidated result completing another 132 full three-character families, bringing our selected union to 416. The final family required 39 new cubic consequences, three quartic power identities, two rebuilt cubic power identities, and two chart contradictions before applying the prior pair-22 exclusion. The post links [immutable proof packets, figures, and failed searches](https://github.com/rbajaj5/hodge-lab/blob/840b88c22386687c745cf944c5c2a41c6b854d39/notes/y0x1-extensions.md), credits preceding work and Eisenbud's viewpoint, discloses Codex assistance, and gives the exact checks and resource bounds. The current discussion and contribution policy were reread. The mathematical Markdown preview was inspected. Posted before the supporting Hodge Lab push; the full body, rbajaj5 author, permanent URL, and absent reply parent were read back and matched. No Lean proof, solve PR, improved degree bound, or leaderboard credit is claimed. Remote CI was not claimed at publication. [Publication receipt](results/y0x1-extensions/upstream-post.json).

14. **17 October 2026, 09:43 EDT / 13:43 UTC — [Holdout discussion #44: 132 Y0/Y1 extensions and a homology-ranking comparison](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18999145).** Shared one consolidated result completing 132 new full three-character families, giving 548 selected exclusions. A prospective comparison closes four high-homology and four low-homology cases alike; no ranking advantage is established. The post links [immutable proofs, figures, plans, failures, and corrections](https://github.com/rbajaj5/hodge-lab/blob/876a0cc913a059dd384f77451a9a59b1999d66df/notes/homology-guided-triples.md), retains the two initially failed charts, and explains the explicit fourteen-to-eleven-direction binding to the prior Y0/Y1 proof. Both physical polynomial implementations and figure-data checks pass. The post credits prior work and Yang/Eisenbud-Erman as motivation, without claiming their categorical or geometric theorems were applied. The current discussion and participation policy were reread; GitHub's mathematical Markdown preview was inspected. Published before the supporting Hodge Lab push. The complete body, author, permanent URL, and absence of a reply parent were read back and matched. No Lean proof, solve PR, improved unconditional degree bound, or leaderboard credit is claimed. Remote CI was not claimed at publication. [Publication receipt](results/homology-guided-triples/upstream-post.json).

15. **17 October 2026, 09:57 EDT / 13:57 UTC — [Holdout discussion #44: added-character homology and 132 X0/X1 extensions](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18999334).** Shared one consolidated exact partial result: 132 fresh full three-character families are excluded, bringing the selected union to **680**. The added-only homology ranking shows no advantage: both prospective groups close 4/4, with unmatched block sizes and empty controls explicitly disclosed. The post preserves the 131/132 checkpoint and explains A100's separate multiplier/power/rebuilding closure, including failed charts. It links [immutable proof, figures, credits, limits, and unsuccessful attempts](https://github.com/rbajaj5/hodge-lab/blob/718cf9a2e721b58782748ac90414dd7707f2a061/notes/added-character-homology.md), credits the prior mathematical work and Codex-assisted implementation, and distinguishes both physical replays from human review. The full body, author, URL, and absence of a reply parent were read back and verified; the proof commit was pushed immediately after posting. No Lean proof, solve PR, improved unconditional degree bound, or leaderboard credit is claimed. Remote CI was not claimed at publication. [Publication receipt](results/added-character-homology/upstream-post.json).

16. **17 October 2026, 10:43 EDT / 14:43 UTC — [Holdout discussion #44: concrete reason for reading Yang](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18999956).** Replied to contribution 15 with the distinction between Koszul H1 relations and H0/image information relevant to coordinate-power exclusions. The checked A19/A30/A61 examples show why equal H1 need not give equal constraint strength. The reply retains the negative ranking result, credits classical Koszul algebra separately from Yang's geometric interpretation, and explicitly says Yang's geometric hypotheses have not been established here. It links the public rationale and existing visualization; no new exclusion, solve, or GPU requirement is claimed. The complete existing thread was reread, Markdown preview inspected, and published body, author, URL, and reply parent read back and matched. [Publication receipt](results/yang-rationale/upstream-post.json).

17. **17 October 2026, 10:45 EDT / 14:45 UTC — [Holdout discussion #44: 131 fresh X0/Y1 triple exclusions and typed-search comparison](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18999988).** Shared the checked 131/132 batch, bringing selected coverage to 811 triples. T100's additional nineteen necessary relations and raw56 vanishing are explicitly partial; both rebuilt charts remain unsuccessful. The post reports the negative frozen cache experiment and the separate exact target-character projection, preserving timeouts and distinguishing their evidence. It links the immutable proof commit, five actual-operator/history figures, credits, bounds, and fifteen passing local checks. The current thread was reread and Markdown preview inspected; the complete published body, author, URL, and absence of a reply parent were read back and matched. The proof commit was pushed immediately after posting. Remote CI is pending, not claimed successful. No Lean proof, solve PR, improved degree bound, or leaderboard point is claimed. [Publication receipt](results/typed-rewrite-families/upstream-post.json).

18. **17 October 2026, 10:58 EDT / 14:58 UTC — [Holdout discussion #44: explicit T100 cubic identity and residual system](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-19000117).** Replied to contribution 17 with the displayed fifteen-product physical-equation identity for raw coefficient 56 cubed, exact equation/generator indices, and the twelve-direction residual support. Both physical reconstructions re-expanded the displayed identity exactly (1,075 coefficient products each). The reply specifies the missing multiplier block, all 128 remaining compatible corrections, and the two still-unresolved charts. It unpacks an existing checked reduction, adding no new family exclusion. The complete current thread and unchanged contribution policy were read; mathematical Markdown was previewed. Published author, complete body, permanent URL, and reply parent were read back and matched. [Receipt](results/typed-rewrite-families/followups/t100-detail.json).

19. **17 October 2026, 10:58 EDT / 14:58 UTC — [Holdout discussion #44: exact character-projection argument](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-19000118).** Replied to contribution 17 with the direct-sum argument preserving finite coordinate-power membership when off-character rows are omitted. The reply links the checker, gives exact T3/T16 row counts, and distinguishes projected-only computations from completed full elimination. It clarifies stale review metadata: T3's full quartic attempt timed out, whereas T16's completed. The remote job had passed the family/T100 checks and primary comparison checker; remaining steps were running or pending. No full CI success, new family exclusion, speedup, or solve is claimed. The complete body, author, URL, and reply parent were independently read back and matched after a small math-formatting edit. [Receipt](results/typed-rewrite-families/followups/typed-projection.json), [CI snapshot](results/typed-rewrite-families/followups/ci-snapshot.json).

20. **17 October 2026, 13:22 EDT / 17:22 UTC — [Reply to contribution 17: exact T100 exclusion](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-19001784).** Shared the rebuilt T100 result after checking that the thread was unlocked and contained no newer T100 solution. Starting from the previously published `a56=0`, the complete twelve-direction constant/linear multiplier pass yields 39 additional necessary relations. Exact degree-five identities force all five Y1 coefficients to vanish; rebuilt charts for raw 6 and 211 contradict, while five X0 chart failures remain recorded. The reproduced anchor dependency closes the residual sector, completing 132/132 in this fresh batch and raising the selected union to 812 triples. The reply links immutable commit `c50638e`, gives seven reproduction commands, reports two physical replays, and labels 36 three-prime rank comparisons as diagnostic rather than p-adic Hodge theory. It credits prior work and discloses Codex assistance. Holdout remains unsolved; no Lean proof, solve PR, improved unconditional degree bound, accepted solve, or leaderboard point is claimed. GitHub's Markdown renderer was inspected before publication. The published author, permanent URL, complete 4,159-character body, and reply parent were read back and matched exactly. [Publication receipt](results/typed-rewrite-families/t100-rebuilt-multipliers/upstream-post.json).

21. **17 October 2026, 13:48 EDT / 17:48 UTC — [Cyclic instance discussion #55: degree-five bounds for two fresh targets](https://github.com/hodge-computer/sextics/discussions/55#discussioncomment-19002099).** Shared one consolidated exact result for `cycle-three` and the companion `mixed-biweight` calculation: every denominator of degree at most five is excluded for each fixed target. The complete E1 kernels vanish through degree four; the degree-five gradient spans fail the necessary Hessian quotient test after all 90 Koszul numerator syzygies are accounted for. The post links the immutable explanation at `02026b3`, exact packets, both actual-map figures, bounded-attempt logs, and reproduction commands. It reports rational replays, a separate coefficient/rank implementation, and explicit limits; it credits the repository framework and discloses Codex assistance. The current threads were reread and were empty of research comments. GitHub's Markdown preview covered three display equations and a table; a typography correction and source-link update were made within the same comment. The final body, author, URL, thread, and absence of a reply parent were read back and matched. The supporting Hodge Lab result was pushed after the shared discussion record was created. No new holdout comment, existence proof, Lean theorem, solve PR, accepted solve, or leaderboard point is counted. [Publication receipt](results/fresh-instance-e1/upstream-post.json). Remote CI was still running when recorded.

22. **17 October 2026, 13:59 EDT / 17:59 UTC — [Reply in cyclic instance discussion #55: degree-six exclusion](https://github.com/hodge-computer/sextics/discussions/55#discussioncomment-19002223).** Shared the complete degree-six exclusion for `cycle-three`, raising its denominator lower bound to seven. Thirty rational square functionals remove the off-diagonal parameters; seven consequences of the full second equation and five quartic identities close the diagonal sector. All 315 Koszul corrections and an unrestricted quotient are included before the stated independent-product relaxation. The companion `mixed-biweight` kernel has three extra directions and remains open in degree six. The reply links immutable proof commit `55083fa`, two actual-map visualizations, exact and separate reconstruction checks, and the unsuccessful weaker tests. Both current threads were reread; Diamond's latest upstream push was still unchanged. GitHub's mathematical preview was inspected before publication, including a bracket-formatting correction. The full published body, author, URL, discussion, and reply parent were independently read back and matched. The linked Hodge Lab commit was pushed immediately after posting. This is the only upstream contribution in this batch; no holdout post, Lean theorem, solve PR, accepted solve, or leaderboard point is counted. [Publication receipt](results/fresh-instance-degree6/upstream-post.json). Remote CI was running when recorded.

23. **17 October 2026, 14:10 EDT / 18:10 UTC — [Mixed-biweight discussion #56: complete degree-six exclusion](https://github.com/hodge-computer/sextics/discussions/56#discussioncomment-19002359).** Shared the exact degree-six obstruction including all three extra E1 directions, raising this fixed target's denominator lower bound to seven. The post explains why correction elimination modulo the Jacobian ideal applies outside the Jacobian denominator subspace, the two rounds of square identities, the failed lower multiplier degrees, and the two remaining complex points. It displays the three-term coefficient functional that rejects both points while retaining all 315 shared Koszul corrections and an unrestricted quotient. The post links immutable proof commit `b5d294e`, four actual-map/support/root visualizations, rational checks, the separate reconstruction, and retained exploratory probes. The separate checker rejects 50 altered witnesses. The current discussion was reread and empty; upstream main was unchanged and no open PR existed. GitHub's mathematical preview was inspected. The full 4,059-character body, author, permanent URL, discussion, and absence of a reply parent were independently read back and matched. The linked repository push succeeded after one transient SSH connection failure. This is the only upstream post in the batch; no holdout post, existence certificate, Lean theorem, solve PR, accepted solve, or leaderboard point is counted. [Publication receipt](results/mixed-degree6-extra/upstream-post.json). Remote CI was not claimed in the post.

24. **17 October 2026, 14:31 EDT / 18:31 UTC — [Cyclic-triple-fano discussion #112: explicit free curve and local covering family](https://github.com/hodge-computer/sextics/discussions/112#discussioncomment-19002605).** Shared one checked geometric partial result for this new target only. The quotient curve's twisted deformation map has rank six; seven incidence equations give a smooth three-parameter component, and marked evaluation has a four-by-four minor equal to one. The post links [immutable code, exact checks, three figures, and limits](https://github.com/rbajaj5/hodge-lab/blob/d846f781066534411c8ed7398430b2ff68f810e6/notes/cyclic-fano-curve.md), credits the upstream framework and classical methods, and discloses Codex assistance. The two implementations reject ten and six altered witnesses. No supporting divisor, certificate, Lean proof, solution PR, or accepted solve is claimed. The thread was read and empty before posting. The author, complete 5,002-character body, URL, discussion, and absence of a reply parent were read back and matched. The supporting Hodge Lab commit was pushed immediately afterward. Local previews rendered all math, but live GitHub inspection found that the Gram display rejected `\operatorname`; the internal note uses `\mathrm{diag}`. **The post preceded the user's stand-down instruction. Further upstream posts and edits are now paused, so that live-comment formatting issue remains uncorrected upstream.** [Publication receipt and rendering limitation](results/cyclic-fano-curve/upstream-post.json).

## Pull requests

1. **17 October 2026, 20:20 EDT / 18 October, 00:20 UTC — [Draft maintenance PR #121: finite-row obstruction lemmas](https://github.com/hodge-computer/sextics/pull/121).**
   Submitted the reusable row-functional lemma and a literal two-row,
   175-column worked example, following the user's request to contribute
   reusable Lean work. Only two new files under `formal/lean/HodgeTestbed/`
   are proposed; no existing upstream file changed. Author `rbajaj5`,
   draft status, base `main`, and head
   `84b1c1584b7615ec7189e896df2734a0833e84e1` were read back and verified.
   Both files compiled, all five axiom reports passed, and the official
   replay routine completed under Lean 4.31.0. Upstream's pinned 4.33.0
   environment remains untested. The polynomial-to-matrix correspondence
   remains checked separately in Python. The proposal credits the project
   authors, standard finite-sum algebra and mathlib, and discloses Codex
   assistance. It is not a `HasCertificate` proof, an accepted solution,
   or a claim to solve points. No discussion comment was added.
   [Publication receipt](results/cyclic-fano-lean/upstream-maintenance/publication.json)
   · [immutable notebook](https://github.com/rbajaj5/hodge-lab/blob/7fe139a725339afd1a45caf801dbee27f7d97417/notes/cyclic-fano-concrete-lean.md).

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

38. **17 October 2026 — Degree four on the eleven remaining triples.**
    Tested all 33 pure-character blocks and the two surviving full maps.
    Twelve blocks fill their quartic target and force sixty family-coordinate
    zeros; a rank-65/70 block in family 2 forces two more. After replaying
    all residual sectors, families 1, 2, 4, 5, 7, 9, 15, 39, and 150 are
    excluded, increasing selected coverage to 150/152. Families 17 and 151
    remain unresolved: their completed 300-second-bound full-map searches
    find no coordinate fourth powers. Both physical polynomial constructions
    pass; all 62 altered-identity checks reject the corruption.
    Families 7 and 150 depend on fqlx's existing family-30 proof, reproduced
    from its hash-pinned packet and bound to our target and basis. This is
    credited reproduction, not a new pair result. Added a static figure and
    110 exact cancellation examples across 35 block/full-map views; all 330
    browser layouts pass. Retained failed searches and corrected presentation
    size/redraw issues. No full resolution, phase transition, Lean proof,
    or holdout solution is claimed.
    [Proof, visualizations, checks, and failed attempts](notes/eleven-quartic.md).
    Read Bright's argument about the mixed effects of credit incentives and
    updated the [publication rationale and current milestones](notes/research-milestones.md).
    Post counts record activity, not scientific quality.
    Shared one consolidated top-level result, recorded as upstream
    contribution 9 above; the ledger distinguishes the eight earlier posts
    and replies from this new publication.
    The Linux `eleven-quartic` job subsequently passed all new arithmetic,
    pinned-dependency fetch, and visualization-data checks at the linked
    proof commit. Its receipt is retained; the other workflow jobs were
    still running at that checkpoint.

39. **17 October 2026 — Shared numerators close family 17; reduce family 151.**
    Followed the failed quartic searches with bounded shared-numerator chart
    tests and pure-block powers through degree six. The original blocks
    force no coordinate powers. The full family-17 system excludes the
    a56=1 chart; after that global zero, rebuilding gives five quadratics in
    five variables with full degree-six image. Five explicit sixth-power
    identities remove X0, and the reproduced fqlx X1/Y1 proof finishes the
    family. Selected coverage increases to 151/152. In family 151, a checked
    three-row identity forces a linear combination to vanish; an explicit
    denominator/lift basis change removes a133. All five rebuilt charts and
    the reduced block's powers through degree six remain unresolved.
    Retained initial failed charts, unsuccessful higher-degree packets,
    declared bounds, exploratory factorization/Groebner motivation, and the
    successful reconstruction. Both polynomial implementations replay the
    proof; seven corrupted identities are rejected. Added a before/after
    figure and seven exact cancellation examples, with 21 browser layouts
    passing. No Lean proof, accepted solve, full resolution, or unrestricted
    degree-seven exclusion. [Proof, intuition, visualizations, and failures](notes/remaining-triples-shared.md).
    Shared one consolidated top-level upstream result, recorded as contribution
    10 above. The unsuccessful searches remain part of the same research packet.
    The Linux `remaining-triples` job subsequently passed the fresh dependency
    fetch, both exact replays, and figure-data validation at the publication
    commit. Its receipt is retained; other workflow jobs were still running
    when that receipt was recorded.

40. **17 October 2026 — Polynomial multipliers close family 151.**
    Rebuilt the shared equations after the checked linear constraint and
    searched global and normalized-chart multipliers of degree at most one.
    The global calculation supplies 96 cubic relations independent of linear
    multiples of the twelve old quadratics. Inspection revealed small pure
    character blocks. Their quartic maps force thirteen coordinate powers;
    two direct residual charts complete the exclusion. All 152 selected
    triples are now excluded, without a holdout solution or unrestricted
    three-character theorem. Both physical polynomial implementations pass
    the exclusion replay, and thirteen altered power witnesses are rejected.
    Retained unsuccessful degree-three searches, bounded chart timeouts,
    and an invalid mixed-degree pilot that was stopped and replaced with
    correctly graded maps. The visualization exposes actual numerator
    cancellation and the small-block proof; no phase transition or full
    resolution is claimed. [Proof, visual record, checks, and failures](notes/family151-multipliers.md).
    All six multiplier packets and the auxiliary chart results pass both
    replays. The seven illustrative identities expose 1,792 checked monomial
    sums; all 42 desktop/mobile layouts pass. Shared one consolidated
    top-level result, recorded as upstream contribution 11 above.

    The complete Linux workflow subsequently passed all eight jobs; the
    [receipt](results/family151-multipliers/ci-family151.json) records that
    later success separately from the publication-time status.

41. **17 October 2026 — Complete the X1/Y1 extension batch.**
    Chose all 132 extensions not already in the preceding 152-family
    selection, with complete character eigenspaces and no transferred
    family-specific constraint. Necessary block equations and powers through
    degree four reduce 123 to the previously proved pair. Nine first-pass
    failures require full shared-numerator charts: 20 of 22 contradict.
    Retaining those partial zeros and rebuilding finishes the two stalled
    charts and removes extra anchor directions. All 132 new families reduce
    to the explicitly matched, reproduced fqlx pair-30 proof, giving 284
    selected triple exclusions. Both physical polynomial implementations
    pass; changed witnesses are rejected. Holdout is still unsolved.
    Kept all failed degree-three/four searches, both originally unresolved
    charts, explicit resource bounds, logs, and the checker syntax correction.
    The new static figure shows all 132 outcomes and the nine reductions;
    the interactive view exposes 18 actual failed graded maps, with 294
    exact nonzero entries and all 54 desktop/mobile layouts checked.
    [Proof, motivation, visualizations, and unsuccessful attempts](notes/x1y1-extensions.md).
    This is finite graded algebra, not a full resolution or phase transition.
    Shared one consolidated top-level result, recorded as contribution 12 above.
    The dedicated Linux job subsequently passed the pinned dependency fetch,
    both first-pass and both shared-system replays, and figure-data validation
    at the published proof commit. The [CI receipt](results/x1y1-extensions/ci-x1y1.json)
    preserves that success while other workflow jobs were still running.

    A later check confirms the complete preceding workflow passed all nine
    jobs at that proof commit. The [full-workflow receipt](results/x1y1-extensions/ci-complete-workflow.json)
    records the update without a separate upstream status comment.

42. **17 October 2026 — Curved bands and a corrected factorization.**
    The user noticed parabola-like bands in old X1/Y1 case B19 at degree
    four, compared B49 and B100, and asked for different colors. Added
    original, adapted, and reordered matrix views with two sign palettes
    and optional relative strength. Exact invertible basis changes give
    B19 generators `v^2, uv, w^2-4vw`, B49 `u^2`, and B100 `u^2+v^2`.
    The first proposed B100 factorization was rejected by the exact check
    before figure generation and corrected in the conversation; the rejected
    identity is retained. The matrices' apparent curves are ordering
    dependent, while ranks and kernel dimensions agree in both bases.
    No new exclusion, full resolution, or phase transition follows from
    these pictures. Twelve maps, six ordering controls, the source physical
    necessities, and 162 browser layouts pass checks.
    [Equations, visual comparison, and correction](notes/graded-map-patterns.md).

43. **17 October 2026 — Complete the new Y0/X1 extension batch.**
    Extended the same rebuild strategy to 132 families disjoint from the
    previous 284. First-pass blocks close 123, shared equations and rebuilding
    close eight, and Y100 needs a global polynomial-multiplier continuation.
    It supplies 39 new cubic consequences; a small mixed-degree quartic map
    forces three X1 coordinates to vanish. Rebuilding forces the remaining
    two X1 coordinates, and two shared-system charts remove the third
    character. The prior Y0/X1 exclusion closes the residual support.
    Both physical implementations pass the chain, giving **416 selected
    triple exclusions**. Kept the 131/132 checkpoint, failed strands and
    charts, all bounds, logs, and explicit witness dependencies. A new
    coverage/rebuilding figure is checked against the packets. These Y IDs
    denote different families from the old B IDs in entry 42. Holdout remains
    unsolved; no Lean or leaderboard claim.
    [Proof, credit, visualizations, and failed attempts](notes/y0x1-extensions.md).
    Shared one consolidated top-level result, recorded as contribution 13
    above; the linked proof commit was then pushed to Hodge Lab.
    The dedicated Linux job subsequently passed both physical replays,
    both multiplier checks, the mixed-degree powers, both closure replays,
    and the coverage and basis-comparison data checks at the proof commit.
    The [CI receipt](results/y0x1-extensions/ci-y0x1.json) records that job's
    success while other workflow jobs were still running.

44. **17 October 2026 — Distinguish relations from Koszul homology.**
    The user redirected the proposed grammar-inspired experiment toward
    categorifications of syzygies, recalling David H. Yang and Emily Riehl.
    Checked the primary references: Yang's equivariant-sheaf interpretation,
    Eisenbud-Erman's categorical pairing, and Riehl's broader foundations.
    The grammar-filter experiment was deferred without being run. As a
    concrete first step, built the Koszul complexes of the three already
    checked necessary-block ideals, at degrees two through six, in both
    original and adapted bases. All thirty complexes pass exact checks,
    including 92 zero-composition columns and basis-invariant homology.
    At degree four B19 has six cycles but three boundaries, so H1 has
    dimension three; B49 and B100 have zero H1 in this range. Added a
    reproducible figure, quotient representatives, and the nonboundary
    degree-three cycle `(-u,v,0)`. This is classical Koszul homology, not
    yet an implementation of either categorical theorem, a full resolution,
    or a new holdout exclusion. No extra upstream post was made for this
    internal comparison. [References, exact data, and figure](notes/categorical-syzygies.md).
    The [later full Linux receipt](results/necessary-koszul-complex/ci-complete-workflow.json)
    confirms all eleven workflow jobs passed at the published commit.

45. **17 October 2026 — Use finite Koszul homology to choose continuations.**
    Selected 132 previously uncovered full Y0/Y1 extensions. Square identities
    close 117. Computed 70 finite complexes for the fifteen survivors, then
    froze a ranking before testing four high-score families and four low-score
    controls with the same bounded method. Both groups close 4/4, so the
    ranking has no demonstrated advantage. Preserved that 125/132 checkpoint;
    all seven later continuations also close, giving **548 selected triples**.
    High scores largely come from Y0 anchor blocks. Retained two initially
    unsuccessful charts and their later rebuilding closures. An audit caught
    the full pair's fourteen directions versus the archived proof's eleven;
    an explicit reduction now binds them. Corrected a checker that mutated
    equations during rank computation, without changing witness packets.
    Both physical reconstructions pass. Added score-composition, actual
    Koszul-differential, and H100 rebuilding figures with exact data checks.
    This implements classical finite Koszul homology, not Yang's geometric
    theorem or the Eisenbud-Erman categorical pairing. No solve or improved
    unconditional degree bound is claimed.
    [Method, references, checks, figures, corrections, and failures](notes/homology-guided-triples.md).
    Shared one consolidated top-level result, recorded as contribution 14
    above, and pushed the linked proof commit to Hodge Lab.
    The [dedicated Linux job receipt](results/homology-guided-triples/ci-homology.json)
    subsequently confirmed both physical replays and the figure-data check
    passed at the proof commit; other workflow jobs were still running.

46. **17 October 2026 — Rank only the added-character homology.**
    Chose 132 fresh X0/X1 extensions, disjoint from the preceding 548.
    Square identities close 117. Computed the added-character block alone
    for fifteen survivors and froze high-score and low-score groups before
    continuation. Both groups close 4/4; preserved the 125/132 checkpoint.
    Six of seven later continuations close, leaving A100 unresolved and
    giving **679 selected exclusions** at the primary checkpoint. Three
    low controls have empty blocks, and variable/generator counts differ;
    no efficacy advantage is established. The score is for a selected
    necessary subideal, not an intrinsic invariant of the full family.
    New figures compare the ranking, actual Koszul maps, H0 versus H1,
    and successful/failed chart histories. A19's failed chart is resolved
    by rebuilding; A100's two failed charts remain. Reconstructed the full
    thirteen-direction X0/X1 pair dependency, preserving nine failed pair
    charts. Both physical implementations pass, along with altered-witness
    rejection and a separate AI source review of chart-prefix handling.
    A separate bounded follow-up then supplies 52 additional necessary
    relations, cubic/quartic powers removing four coordinates, two more
    powers after rebuilding, and contradictions in A100's two formerly
    failed charts. All 132 new families now close, giving **680 selected
    exclusions**. Both physical reconstructions replay the full chain.
    Five unsuccessful charts in the rebuilt system are retained too.
    This is not human review, Lean acceptance, or a solve.
    [Evidence, motivation, figures, and failed attempts](notes/added-character-homology.md).
    Shared the consolidated result as contribution 15 above and pushed
    the pinned proof commit to Hodge Lab.
    The [dedicated Linux CI job](results/added-character-homology/ci-added-character.json)
    subsequently passed both primary physical replays, all six A100
    verification variants, and both visualization checks at that commit.
    Other workflow jobs were still running at receipt time.

47. **17 October 2026 — Revisit unique-category grammars.**
    Read the supplied Vishnikin–Okhotin paper while continuing the
    added-character experiment. Its encoding theorem and preservation of
    primitive-category counts suggest an analogy with typed composition
    and degree/character filters. Unique lexical typing does not remove
    parse ambiguity. Recorded a possible future cache of typed identity
    compositions, with a matched-budget comparison still required. No
    grammar solver or speedup was implemented, and no current exclusion
    is attributed to this paper. Kept the earlier deferral in the record.
    [Precise scope and connection to the existing map figures](notes/categorical-syzygies.md#revisiting-the-grammar-suggestion-17-october-2026).
    This reading adds no upstream contribution to the tally.

48. **17 October 2026 — Implement typed rewrites and goal projection.**
    Following the user's request, implemented an experiment motivated by
    Vishnikin–Okhotin's conserved category counts. Derived auxiliary
    degree/character types from the actual fixed physical polynomials.
    Selected 132 fresh X0/Y1 extensions outside the preceding 680-family
    union; the square pass excludes 119 with both physical replays passing.
    Reconstructed the full thirteen-direction anchor dependency, retaining
    its nine unsuccessful charts. Froze the first two survivors, T3/T16,
    for sequential alternating typed-cache and existing-elimination runs
    with equal row budgets and process limits. The cache reuses only exact
    residual identities; matching types alone is not a proof. The prototype
    also changes allocation and proof-bookkeeping costs, so this is not a
    typing-only performance ablation. The cache is slower on T3 and times
    out twice on T16; both physical replays pass the retained rowspaces.
    Ordinary continuations close twelve more families, giving 131/132 and
    811 selected triples. T100's separate bounded continuation supplies
    nineteen necessary relations and raw56=0, but both rebuilt charts still
    fail; no T100 exclusion is claimed. A separate goal projection gives
    exact cubic and quartic coordinate powers in smaller character blocks.
    T3's full quartic comparison times out; T16's completes. Both separate
    projected-only quartic jobs complete, but add no new vanishings beyond
    the cubes. These adaptive follow-ups are not a matched timing benchmark.
    Five figures show the actual operator, cache outcome, query filtering,
    and successful/failed family history. The grammar encoding theorem is
    not being applied to the Hodge problem.
    [Method, references, limits, and experimental record](notes/typed-rewrite-search.md).
    Published the consolidated result as contribution 17 and pushed the
    proof, figures, failures, and checks. Remote CI was pending at handoff.

49. **17 October 2026 — Publish the concrete reason for reading Yang.**
    Added a [public rationale with an existing checked visualization](notes/why-yang.md)
    and linked it from the README at commit `5f267e4`. A19 and A30 both
    have degree-four H1 dimension three but H0 dimensions eleven and zero;
    A61 has H1=0 and H0=0. This distinguishes relations among equations
    from the graded images needed for coordinate-power certificates.
    The note retains the failed homology-ranking comparison and explicitly
    identifies the implemented calculations as classical Koszul homology,
    not an application of Yang's geometric theorem. It uses evidence already
    returned in contribution 15. The requested rationale was then posted as
    contribution 16; it adds no new mathematical exclusion.

50. **17 October 2026 — Make two existing results easier to inspect.**
    Expanded the exact T100 cubic identity into physical equations and
    explained the target-character projection lemma in contributions 18–19.
    The [T100 continuation figure](results/typed-rewrite-families/typed100-continuation.png)
    and [projection figure](results/typed-rewrite-families/typed-goal-powers.png)
    remain the corresponding visualizations. Corrected two stale scope
    sentences in the quartic review metadata: only the original T3 full
    comparison timed out; the separate projected-only packets do not claim
    full ranks, while the original T16 comparison computed its full rank.
    The prior wording is retained in the dated correction record. Proof
    packets, code, actual result note, and figures are unchanged. Recorded
    a separate T100 source-review receipt and a pending remote-CI snapshot.
    No new search, mathematical exclusion, or accepted solution is counted.

51. **17 October 2026 — Close T100 locally with rebuilt multipliers.**
    Preserved the earlier thirteen-direction timeout, the exact `a56=0`
    reduction, and its two failed rebuilt charts. Rebuilt the physical system
    on twelve directions and completed all constant/linear multiplier blocks
    in 73.2 seconds, obtaining 39 additional necessary relations beyond the
    finite baseline span. Exact degree-five identities then force all five Y1
    coordinates to vanish. Rebuilding on seven directions makes the two
    added-character charts, raw 6 and 211, contradictory; five X0 chart
    attempts remain unsuccessful and are retained. The separately replayed
    anchor dependency excludes the remaining X0 sector. Both physical
    polynomial constructions pass the complete rational chain. Twelve exact
    graded ranks also agree modulo 1009, 1013, and 1019, for 36 diagnostic
    comparisons; those screens are not p-adic Hodge-theory proofs. This closes
    T100, completes 132/132 in the fresh X0/Y1 batch, and raises the selected
    union to **812**. Recorded unsupported Yang-geometric, Beilinson–Bernstein,
    KZ/KPZ, and VC-complexity bridges as ideas not used by the proof. Added a
    data-bound visualization, complete bounded-attempt logs, and exact
    checkers. [Proof, figure, failures, and reproduction](notes/t100-rebuilt-exclusion.md).
    Shared the consolidated exact result as contribution 20 above. No pull
    request, Lean proof, accepted solve, or leaderboard point is counted.

52. **17 October 2026 — Pause holdout posts and prepare to change instances.**
    Retain the T100 checkpoint and stop adding holdout discussion posts while
    waiting for the announced new instances. At 17:37 UTC, upstream main was
    `0768616c9b70b318011b7c421abdd640322ccbfc`; its
    [catalogue](https://github.com/hodge-computer/sextics/blob/0768616c9b70b318011b7c421abdd640322ccbfc/data/catalogue.json)
    contained the same 61 instance IDs as our pinned checkout, with no added
    or removed IDs. The open-PR query returned no entries. A later instance
    choice must recheck its current acceptance status, discussion, fixed
    target, and contribution requirements. This check is not ongoing
    monitoring. The existing [T100 CI run](https://github.com/rbajaj5/hodge-lab/actions/runs/39053416474)
    was still in progress, so no full remote-CI success is claimed here.
    Preliminary reading of Yi Sun's *Quantum intertwiners and integrable
    systems* (MIT thesis, 2016) remains exploratory: no theorem from it has
    been applied to holdout, the proposed symmetry review did not finish,
    and no new experiment or mathematical result is counted. This is a
    workflow checkpoint; the existing T100 visualization and proof packet
    remain unchanged. No upstream comment was made, and the public tally
    remains 20 contributions, with no solve submission or accepted solve.

53. **17 October 2026 — Begin two different fixed targets.**
    Selected `cycle-three` and `mixed-biweight` after checking their exact
    targets, context, provenance, current proof/acceptance files, open PRs,
    and complete discussion threads. Both threads had no research comments.
    The complete rational E1 denominator kernels vanish in degrees zero
    through four. At degree five, each kernel is exactly the six-dimensional
    gradient span. All 90 linear Koszul numerator syzygies are retained;
    the necessary Hessian map has rank 21 and rational duals force all six
    coefficient squares to vanish. Thus both fixed targets exclude every
    denominator of degree at most five, including complex coefficients and
    nonzero quotients. Degree six is unattempted. Preserved all bounded
    failed searches, exported identities, exact checks, two coefficient-map
    visualizations, and a separate implementation's rank and rational-dual
    checks. Fixed a Windows line-ending portability issue before publication
    and replayed both checkers on LF copies. No existence proof, Lean proof,
    accepted solution, or leaderboard point follows.
    [Result, figures, limits, credits, and reproduction](notes/fresh-instance-baselines.md).
    Shared as the single consolidated contribution 21 above and pushed the
    supporting notebook. The pause on additional holdout posts remains in effect.
    Subsequent [Linux CI](https://github.com/rbajaj5/hodge-lab/actions/runs/39055352335)
    passed the `fresh-instance-baselines` job at commit `02026b3`, including
    both verifiers and the plot generator. Other jobs in the full workflow
    were still running; no full-workflow success is claimed.

54. **17 October 2026 — Full second equation closes cyclic degree six.**
    Upstream main remained `0768616c9b70b318011b7c421abdd640322ccbfc`;
    the announced additional instances had not appeared. Continued
    `cycle-three` and `mixed-biweight`, with fixed targets and all existing
    upstream files intact. The complete degree-six kernels have dimensions
    36 and 39, respectively. For the cyclic target the kernel equals $J_6$.
    Euler gauge leaves 35 parameters, and 30 rational square functionals
    remove every off-diagonal matrix entry. The weaker Jacobian-quotient
    test stalls on five diagonal parameters. Eliminating the full relaxed
    numerator-correction space instead gives seven necessary quadratics;
    their quartic multiplier map has rank 70/70 and supplies five exact
    fourth-power identities. Hence cyclic denominators of degree six are
    excluded over the complex numbers, raising its lower bound to seven.
    Mixed degree six remains open, including three directions outside $J_6$.
    Kept the unsuccessful weaker tests, bounded-attempt logs, rational
    witnesses, separate equation reconstruction, and two actual-map figures.
    [Argument, visualizations, failures, and reproduction](notes/fresh-instance-degree6.md).
    No existence proof, Lean proof, accepted solve, or leaderboard point
    follows. Shared as the single contribution 22 above, with verified
    readback, then pushed the supporting proof packet. The pause on further
    holdout posts remains in effect.
    The subsequent [Linux CI run](https://github.com/rbajaj5/hodge-lab/actions/runs/39056144747)
    passed the `fresh-instance-degree6` job, including both implementations
    and figure generation. This records that targeted job, not a claim
    about every unrelated job in the workflow.

55. **17 October 2026 — Include all three mixed extra directions and close degree six.**
    Rebuilt the actual mixed-biweight $B_D(N_0)$ map on all 38 parameters
    after Euler gauge. Two rounds of rational square identities eliminate
    the three extra E1 directions and all 30 off-diagonal matrix entries.
    Five full-E2 consequences then reduce the diagonal family: failed
    degree-two and degree-three searches are retained; the degree-four
    image has rank 65/70 and gives three fourth-power identities for linear
    differences. The reduced family has two complex points, explaining why
    the preceding individual-coordinate-power search failed. Keeping one
    shared set of 315 numerator corrections rejects both points: an exact
    three-term coefficient functional annihilates all 777 correction and
    quotient columns but evaluates to one on the target. Complete primary
    and separate rational reconstructions pass. This excludes all degree-six
    denominators and raises mixed-biweight's lower bound to seven; it does
    not establish existence. Kept exact proof packets, bounded runs, failed
    multiplier degrees, and the modular exploration as diagnostic evidence.
    [Argument, actual-map visualizations, checks, failures, and reproduction](notes/mixed-degree6-extra.md).
    Shared as the single verified contribution 23 above and pushed the
    supporting proof packet. Four figures retain the support, quotient,
    failed-search, and final three-coefficient views.
    The subsequent [Linux CI run](https://github.com/rbajaj5/hodge-lab/actions/runs/39057001593)
    passed the `mixed-degree6-extra` job. This records that targeted job,
    not a result for every unrelated workflow job.

56. **17 October 2026 — Switch to Diamond's ten new targets; explicit cyclic Fano curve.**
    Following the user's direction to work only on the newly added targets,
    inspected commit `d96911d725077e66a8f10848908be01a643b1714`, all ten new
    discussions, current guides, and open PRs. All ten discussions were
    initially empty and the open-PR list was empty. Selected
    `cyclic-triple-fano`, whose geometric existence was already known by
    the cited upstream weighted-Fano theorem. Constructed the explicit
    quotient curve `[0:s:0:is:t:it]` and verified its full twisted
    deformation map has rank six. Its coefficient Gram spectrum is
    `72` twice and `25/49` four times. The supplied Bourbaki excerpts have
    a concrete role: exact spectral projectors, positivity, an exact
    right inverse, and a coefficient-norm stability bound.
    Seven polynomial incidence equations define a smooth three-dimensional
    component through the curve; the marked evaluation has an exact
    nonzero four-by-four minor. The initial density-zero curve and its
    nonzero density deformation are both recorded. The auxiliary zero
    coupling gives a failed freeness test for this particular curve on a
    different sextic, not a failure of the protected target. Boundary and
    branch elimination, support extraction, and numerator construction
    remain unattempted. No witness, Lean proof, solve PR, or point is claimed.
    [Argument, actual-map visualizations, bounds, checks, and limits](notes/cyclic-fano-curve.md).
    The unfinished mixed-biweight degree-seven batch is retained locally
    and is outside this publication. Shared as contribution 24 before the
    user's stand-down instruction; the posted body was read back and the
    supporting notebook was pushed. See the contribution entry for the
    subsequent live-rendering limitation.

57. **17 October 2026 — Pause all upstream publication; continue only in Hodge Lab.**
    The user directed that further work be applied only to this notebook.
    Recorded that boundary in README.md and AGENTS.md. No additional upstream
    post, reply, PR, or formatting edit was made after the instruction.
    Retained the already-published contribution 24 in the tally, together
    with its exact receipt and the unresolved live-comment rendering issue.
    Corrected the equivalent diagonal-matrix notation in the internal note;
    all mathematical packets, check results, and figures remain unchanged.
    The latest Fourier and invariant-subspace excerpts remain background
    reading; no application to another new target is asserted. Resuming
    upstream activity requires a new explicit direction from the user.
    The [targeted Linux CI job](https://github.com/rbajaj5/hodge-lab/actions/runs/39058500295/job/117471299490)
    passed for proof commit `d846f78`; this is not a full-workflow claim.
    Further notebook-only typography fixes preserve the multiplication sign
    and double-bar norm notation through GitHub Markdown.

58. **17 October 2026 — Resume new-target contributions in consolidated batches.**
    The user explicitly reopened useful contributions and requested fewer
    comments. Updated the repository instructions accordingly. Continued only
    `cyclic-triple-fano`: exact Taylor elimination reduces the full normalized
    fiber through `[0:1:0:i:1:i]` to three equations of degrees four, five, and
    six. A 105-by-105 minor of the degree-13 Macaulay map is 47 modulo 101,
    proving a nonzero characteristic-zero minor and no points at infinity.
    Complete-intersection degree gives total fiber length 120, counting
    multiplicities. The seed is reduced; distinctness of all points and
    the seed component's covering degree are not established. A separate
    recurrence reconstruction from the protected F verifies the equations
    and every Macaulay column. The bounded modular Groebner attempt completed
    and is retained as corroboration, not the characteristic-zero proof.
    Two exact unit minors show evaluation is unramified along the whole seed;
    the apparent zero of the single r^5 minor was a misleading diagnostic.
    The omitted s=0 section maps locally to a divisor inside X1=0. This is
    only one boundary image; no support equation or certificate is claimed.
    [Proof, exact-data visualization, attempts, and limits](notes/cyclic-fano-continuation.md).
    The publication plan is to consolidate the existing #112 contribution,
    with no additional comment or increment to the upstream tally.

59. **17 October 2026 — Use the supplied spectral theory to resolve the fiber's multiplicities.**
    Continued only `cyclic-triple-fano` after the user supplied Bourbaki's
    spectral multiplicity, trace, normal-operator and polar-decomposition
    passages. Built the actual 120-dimensional quotient multiplication maps
    modulo 101. All seven squarefree-characteristic-polynomial tests failed;
    the retained length-three nilpotent block suggested the exact swapped
    curve `[0:s:0:it:t:is]`. A separate rational cubic-jet calculation proves
    its local length is three over Q(i). A size-118 trace minor is 89 modulo
    101; the finite-free model lifts its nonvanishing to characteristic zero.
    Together with total length 120, this proves 118 geometric points over C:
    the triple point and 117 simple points. It does not identify the degree
    of the seed component or construct a support or certificate. Kept all
    seven failed tests and the initial type-coercion implementation error.
    [Proof, actual-operator visualizations, reproduction, and limits](notes/cyclic-fano-spectrum.md).
    The user then requested still more infrequent comments. The prepared
    consolidation of contribution 24 is held locally; no upstream edit,
    new comment, or supporting public push has been made for entries 58–59.
    The upstream tally remains 24. Current upstream main `4e920b8` changes
    website/navigation files; the protected target and relevant contribution
    rules are unchanged from the pinned source. Discussion 112 still contains
    only our original comment, with no replies or open solution PRs observed.

60. **17 October 2026 — Choose a tractable pilot on the new quadric-contact target.**
    Following the user's invitation to select an easier new instance,
    compared the new targets and chose `quadric-contact-broken` for a small
    exact test, without claiming it is the easiest target to solve. Its
    discussion 119 was empty and unlocked, with no answer or open solution
    PR observed. A natural quartic denominator repairs the first equation
    of the old contact field. The full second-equation test has 15 constant
    Koszul corrections and 21 quadratic quotient coefficients. Its actual
    487-by-36 matrix has rank 36 and augmented rank 37. One coefficient
    already gives an exact rational obstruction, excluding this denominator
    even with unrestricted corrections and a nonzero quotient. Higher powers
    and other denominators remain open. Retained the bounded failed attempt,
    protected source snapshot, exact witness, and operator visualization.
    Primary and separate standard-library reconstructions pass, including
    five mutation controls in the independent checker. The visualization
    reconstructs the physical map and binds the final validation receipt.
    [Pilot, explanation, source binding, and reproduction](notes/quadric-contact-pilot.md).
    Work remains local alongside entries 58–59; no post, discussion edit,
    public push, solve PR, or accepted solution is claimed.

61. **17 October 2026 — Resume notebook pushes while holding upstream comments.**
    The user explicitly asked to continue cyclic Fano, push results,
    visualizations and failures here, and save upstream comments for a
    substantial batch. This supersedes the local-only staging of entries
    58–60. The notebook publication includes their previously local commit
    `9cf26be` and the continuation below. Read discussion 112 again: only
    the original contribution was present, with no replies, accepted answer,
    or open solution PR observed. Upstream main `adfb848` differs from the
    pinned `d96911d` only in website/server files and revision metadata;
    the target and contribution rules are unchanged. No upstream comment,
    edit, or PR accompanies this notebook batch. The tally remains 24.

62. **17 October 2026 — Unfold the cyclic Fano triple point on the fixed target.**
    Moved the evaluation point along the actual quotient curve
    `[0:1:0:i:1+h:i(1+h)]`. Exact order-four implicit jets give
    `h=(5/6+8i/35)b^3+O(b^4)`, proving a smooth local source curve,
    ramification index three, and a three-cycle on nearby local sheets.
    Three bounded second-direction attempts collectively test all four
    target tangent directions; their first-order deformation image has
    rank one, so the hoped-for miniversal two-parameter description fails.
    Kept this limitation and the initial serialization error alongside
    the successful cubic calculation. The visualization distinguishes
    actual jets from analytic normal-form coordinates, and the local
    evaluation monodromy from the original cyclic deck symmetry.
    All three primary checks and a separate standard-library reconstruction
    pass, including the fourth-order branch jet and fifteen mutation controls.
    [Argument, exact checks, branch picture, and failed directions](notes/cyclic-fano-unfolding.md).
    No quantitative convergence radius, full branch equation, supporting
    divisor, certificate, or solve follows.

63. **17 October 2026 — Apply the final Bourbaki character projector concretely.**
    The supplied corpus ends with compact-group character averaging;
    Chapter V, section 4, pages 465–466 supplies the finite-group projector
    used here. On the fixed cyclic target, invariant degree-three
    denominators admit a complete numerator reduction from 756 to 150
    coefficients. Polynomial Piola identities transfer both physical
    equations exactly to the weighted quotient. Tested three geometric
    guesses: the cyclic branch `Z`, quadratic branch `2Z+Q`, and omitted
    section power `X1^3`. All fail: each coefficient matrix has rank 150
    and augmented rank 151, with a one- or two-term rational dual witness.
    Primary and separate standard-library reconstructions verify all 450
    basis transfers, all columns and dual pairings; the independent checker
    rejects six mutations. The bounded search completed under one second.
    [Actual-map visualization, exact reduction, failures, and reproduction](notes/cyclic-fano-transfer.md).
    This excludes the displayed denominators, not their arbitrary powers,
    products, all supports on these zero sets, or unrestricted certificates.
    No new upstream post or accepted solve is counted.

64. **17 October 2026 — Use higher unfolding terms to make and test denominator guesses.**
    Continued only `cyclic-triple-fano`. Solved all seven physical incidence
    coefficients for the actual local evaluation map through degree twelve
    in the X0 direction and degree eight in Y0. X0 gives no centered height
    through order twelve or centered linear term through eleven; these are
    finite-order negative results. Y0 has a nonzero quadratic centered-linear
    coefficient. The exact leading cubic proves two local critical-value
    branches with contact order three. It does not supply a global branch
    equation or a supporting divisor. The local geometry generates three
    explicit homogeneous guesses of degrees one, three and six.
    [Derivation, branch visualization, precision limits, and failed direction](notes/cyclic-fano-higher-unfolding.md).
    Tested these three, three rational tangent-norm powers, and three
    Jacobian-multiplied repairs. All nine fixed denominators are excluded:
    six fail E1; three satisfy E1 by construction but fail E2 with the full
    weighted Koszul correction and quotient spaces. Eight obstructions
    use one coefficient; the repaired cubic uses eleven. No full matrix
    ranks are claimed from the early-stopping discovery algorithm.
    [Complete tests, exact witnesses, bounded attempts, and limits](notes/cyclic-fano-guided-denominators.md).
    All workers completed within their 120-second bounds. Retained the
    initial symbolic-comparison implementation failure and the unsuccessful
    geometric choices. The primary and independent jet checks pass,
    including nine independent mutation controls. Candidate replay passes
    all nine obstructions; the independent implementation checks 3,129
    physical columns, Piola and Euler identities, and eighteen mutations.
    The visualization separates leading local branch jets from the global
    candidate failures and binds the exact packets and validation receipts.
    This batch is for Hodge Lab; no upstream comment, comment edit, or PR
    accompanies it. The contribution tally remains 24. Discussion 112
    still had only our original contribution when read before this batch.
    Upstream main `83e952f` changed website/server files, metadata, and
    one-reflection explanatory files; the cyclic target and relevant
    contribution rules remain unchanged from pinned source `d96911d`.
    Previous push `efb819b` passed its cyclic unfolding/transfer and cyclic
    continuation CI jobs. Its quadric pilot passed both exact checkers but
    failed plotting because SymPy was not installed in that job. This batch
    adds the missing dependency and a dedicated higher-unfolding CI job;
    the prior plotting failure is not recorded as a mathematical failure.
    Published the full batch as notebook commit
    [`3504189`](https://github.com/rbajaj5/hodge-lab/commit/35041890bcb93753dd9402d5eea29c87b4ad66d0).
    Its [higher-unfolding replay and visualization job](https://github.com/rbajaj5/hodge-lab/actions/runs/39063156844/job/117485140998)
    and [repaired quadric plotting job](https://github.com/rbajaj5/hodge-lab/actions/runs/39063156844/job/117485141302)
    both passed on Linux. This records the two targeted jobs, not a completed
    full-workflow result; the broader workflow was still running when checked.

65. **17 October 2026 — Test higher powers and products on cyclic Fano.**
    Continued the same fixed `(F,q,A)` with 26 explicitly listed products of
    the tangent, centered cubic, leading branch sextic, rational tangent
    norm, and Jacobian factor. Degrees range from two to twelve. Exactly
    25 selected denominators are excluded: eleven fail the complete E1
    equation and fourteen fail the complete E2 correction problem. The
    degree-twelve square `S^2` hit its 120-second worker limit and remains
    unresolved; no E1 success or obstruction was established for that run.
    This is a finite product list, not an exclusion of all denominators or
    all products through degree twelve.
    The new reduction uses `t=2Z+Q`, `Delta=Q^2-4H`, reflection averaging,
    complete Koszul corrections, and exact reduction modulo `t^2-Delta`.
    Cancelling a common nonzero polynomial produces a five-variable system
    while retaining the full allowed quotient freedom. For pure powers,
    `J^(2m-1)` and `J^(2m)` share the same complete system. In this batch
    `J^3` and `J^4` share one 630-column problem and a five-term obstruction;
    the latter reuses and rechecks the former's witness, rather than counting
    the two calculations as independent evidence.
    Three additional raw six-variable controls agree with the compressed
    tests. They cover 340 original Koszul directions and 336 quotient
    coefficients and are not additional denominator candidates. Separate
    verification passes all 33,695 physical columns across the completed
    tests and controls, 560 first-order operator coefficient identities,
    and 56 deliberately changed inputs. The source-bound timeout stays in
    the final validation receipts and the coverage visualization.
    [Exact reduction, product table, visualization, reproduction, and failed attempt](notes/cyclic-fano-branch-products.md).
    Published this batch and the polar pilot below as notebook commit
    [`b424552`](https://github.com/rbajaj5/hodge-lab/commit/b4245527b033c099524cc784c810aa563fc6078a).
    Its [dedicated Linux CI job](https://github.com/rbajaj5/hodge-lab/actions/runs/39064680185/job/117489722552)
    passed the compact identities, both primary replays, both independent
    checkers, and both visualization generators. This reports that targeted
    job, not the completion state of every job in the larger workflow.
    No upstream comment, edit, PR, Lean proof, accepted solve, or leaderboard
    point accompanies it. The upstream contribution tally remains 24.

66. **17 October 2026 — Apply Dolgachev's first polars to the branch sextic.**
    The supplied classical-geometry excerpts suggest an explicit new family,
    `E_v = partial_v Delta`, where `Delta = Q^2 - 4H` is the actual branch
    sextic. Direct differentiation gives a polynomial first-equation lift
    for every constant base direction. Tested the five coordinate directions
    and two specified sums, with separate 60-second bounds. All seven
    completed in under 0.5 seconds each including startup and are excluded
    by one-coefficient exact obstructions to the second equation.
    No conclusion about arbitrary linear combinations follows from this
    finite pilot. The field, target identities, complete sparse correction
    maps, attempts, and witnesses are retained with source hashes.
    Primary replay passes all seven. Independent reconstruction passes all
    175 Koszul columns, 105 quotient columns, original-coordinate identities,
    and 21 deliberately altered inputs. It also constructs independent
    reflection-even coefficient obstructions. At this degree the relevant
    reflection sector has no correction freedom; a nonzero even residual
    therefore cannot be repaired. The figure shows an actual correction map
    and the coefficient row responsible for one of these failures.
    [Dolgachev connection, map visualization, exact tests, and limits](notes/cyclic-fano-branch-polars.md).
    The plane-cubic and determinantal material is treated as further reading,
    not as a theorem automatically applicable to this weighted cover.
    The subsequent hyperelliptic excerpt suggests a concrete future setting:
    the line `(X0,X1,Y0,Y1,Y2)=(s,u,s,0,0)` yields a genus-two double
    cover and a genus-ten cyclic triple cover above it, with nonzero
    restricted density. Two source substitutions and the smoothness/genus
    arguments agree. The note gives the equations and explicitly leaves
    extension of divisors to fourfold support unproved; this is a slicing
    observation, not another denominator experiment or solve.
    This is notebook research; no upstream comment, edit, or PR accompanies
    it. The contribution tally remains 24, with no certificate or solve claimed.

67. **17 October 2026 — Audit curve restrictions using Shafarevich.**
    Applied the supplied introductory chapters on coordinate rings, rational
    functions, dominant rational maps, and tangent spaces to the same seven
    already excluded cyclic-Fano polars. This is an exact restriction audit,
    not a new denominator search. On the closed base line
    `(X0,X1,Y0,Y1,Y2)=(s,u,s,0,0)`, the `Y2` polar has both denominator
    and particular E2 residual zero. Its field numerator component is
    `-4*s^4/3`, so the rational component does not acquire a regular
    restriction. The apparent zero residual is not a success. The other six
    denominators and particular residuals remain nonzero on the slice.
    The explicit control `Y1` is nonzero modulo the full target and zero on
    the slice, illustrating that restriction to a closed curve loses
    information. No universal pullback of ambient rational functions to
    the slice follows from the function-field theorem for dominant maps.
    The audit also tests the linear slice equations and the target equation
    separately; none of these particular fields descends to a curve
    derivation. Derivatives are taken before restriction.
    The subsequent blowup excerpt motivates two transverse arcs. Exact
    substitution gives denominator orders one and five, with the same
    nonzero numerator, hence pole orders one and five. These are local
    directional data, not a phase transition or a performed blowup. Formal
    lifts to the target require a chosen point away from the branch locus.
    Primary replay and independent reconstruction pass all seven cases,
    both arcs, and the tangency and noncancellation controls. The independent
    checker rejects nine mutated inputs. The visualization binds these
    receipts and shows the exact polynomial restrictions.
    [Exact restricted polynomials, visualization, checks, and interpretation](notes/cyclic-fano-slice-audit.md).
    Published as notebook commit
    [`dc6ff3f`](https://github.com/rbajaj5/hodge-lab/commit/dc6ff3ffb4678952801e847a5b4c99865e5b2ac1).
    Its [dedicated Linux CI job](https://github.com/rbajaj5/hodge-lab/actions/runs/39066408172/job/117494904808)
    passed the primary replay, independent checker, and visualization
    generator. This records that targeted job, not every workflow job.
    All previous exclusions, target files, and prior packets are preserved.
    No upstream comment or PR accompanies this notebook audit. The
    contribution tally remains 24; no new solve or Lean proof is claimed.

68. **17 October 2026 — Separate pole orders with exact blowup charts.**
    Continued the Shafarevich reading with the two charts of a chosen
    transverse plane, setting `X0=Y0=1` and retaining `X1=u` as a parameter.
    The same failed `Y2` polar defines a smooth plane curve at the origin.
    Each chart's total denominator has one exceptional factor; its strict
    transform meets the exceptional curve transversely. The scalar numerator
    remains `-4/3`, so the pole persists. Along the special axis, four orders
    of contact with the strict transform add to the one exceptional factor,
    explaining the previously observed pole order five. This is not
    exceptional multiplicity five or a phase transition.
    The subsequent intersection-theory excerpt identifies exact local
    quotient-ring lengths 1, 4, and 5 for these three intersections.
    The next excerpt's surface-blowup formulas explain the same drop from
    five to four and the exceptional multiplicity one; no fourfold
    intersection number is inferred.
    Primary replay checks both charts and overlap identities and rejects six
    altered packets; independent reconstruction rejects eight altered inputs.
    The figure uses exact equations with a labeled numerical real-curve
    display. The calculation pulls back a scalar coefficient in its original
    frame; it does not transform the full vector field or construct a
    fourfold blowup. This is a geometric explanation of an existing failed
    candidate, with no additional denominator exclusion or certificate.
    [Equations, geometric visualization, local lengths, and reproduction](notes/cyclic-fano-blowup-audit.md).
    No upstream comment or PR accompanies this notebook batch. The upstream
    contribution tally remains 24.

69. **17 October 2026 — Exclude the complete constant first-polar family.**
    Extended the preceding seven-direction pilot to every nonzero complex
    constant vector `v` in the five base directions, with denominator
    `E_v = partial_v Delta` of degree five. All directions satisfy the first
    equation by the same explicit polynomial lift. Five pure-monomial
    coefficients give an invertible minor, so nonzero `v` cannot give a zero
    denominator. Reflection averaging in `t=2Z+Q` annihilates the complete
    degree-five correction space while preserving the particular residual.
    Five coefficient equations force all direction parameters to vanish;
    explicit ideal identities give four parameter squares and the remaining
    parameter's fourth power. Thus no nonzero member of this family works,
    including exceptional parameter choices. The mixed term in the `X0`
    equation is retained until the `Y1` and `Y2` vanishings have been proved.
    The source-based primary replay checks all 15 quadratic parameter terms,
    125 basis/Koszul projection identities, 15 quotient directions, the
    five coefficient rows and five coordinate-power identities. It rejects
    seven altered packets. Shafarevich's supplied finite-group averaging
    discussion gives a direct interpretation of the projection; the
    exclusion comes from the checked equations, not the analogy.
    Independent reconstruction passes the same full coefficient and
    correction checks, five original-coordinate Piola lifts, 180 Euler
    normalization identities, and eight altered-input rejection controls.
    [Complete proof, coefficient-map visualization, exact packet, and limits](notes/cyclic-fano-polar-family.md).
    Published this proof and the blowup audit above in notebook commit
    [`97f0318`](https://github.com/rbajaj5/hodge-lab/commit/97f03189c2d22a698bde953e18410dcb71a5c374).
    Its [dedicated Linux CI job](https://github.com/rbajaj5/hodge-lab/actions/runs/39066917738/job/117496404893)
    passed the primary and independent checkers and visualization generators
    for the slice audit, blowup audit, and full polar-family proof. This
    records that completed job, not every job in the larger workflow.
    This rules out this constant first-polar family only. Polynomial
    directions, products, powers, and other degree-five denominators are
    outside the result. No successful certificate, Lean proof, accepted solve
    or upstream post is claimed. The contribution tally remains 24.

70. **17 October 2026, 16:32 EDT / 20:32 UTC — Read the complete discussion and record new T100 credit.**
    Fetched every current comment and reply page for holdout #44,
    cycle-three #55, mixed-biweight #56, and all ten new-target threads
    #111–120. The holdout snapshot contains 13 top-level comments and six
    replies following the maintainer's consolidation; the historical
    publication entries above remain intact.

    [Ben Burns's T100 reproduction audit](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-19003434),
    posted at 15:41 EDT, explicitly credits `rbajaj5`'s result. GitHub's
    public author metadata identifies `fqlx` as Ben Burns. He reports
    replaying the full five-stage chain at notebook commit `c50638e`,
    including the initial 16-to-13 reductions, the `a56=0` reduction,
    all 156 necessary relations, 13 power identities, and the terminal
    charts and pair dependency. He reports that all stages pass and
    altered witnesses are rejected. His audit uses our supplied checkers;
    it does not claim a separately authored implementation or independent
    human review. We verified the live attribution and read its scope in
    this checkpoint; we did not execute his new reproduction packet.

    [Benjamin Diamond's maintainer summary](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-19003085)
    also credits the linked pair results and our **812 selected triples**.
    Burns separately checked the support counting and the distinctness of
    his additional triple, reporting **813** supports in that combined
    union. This is reported coverage of selected supports, not an accepted
    solve, an independently replayed audit of every family, or an improved
    unconditional degree bound. The holdout remains open. The summary
    recommends substantial continuations as replies to existing results,
    with detailed logs retained in linked research notes.

    Cyclic-triple-fano #112 currently has our one top-level contribution
    and no replies. No answer is marked in any monitored thread. An hourly
    read-only watch now checks new comments, replies, and edits against a
    local timestamped snapshot, reporting meaningful changes rather than
    repeating unchanged material. No upstream comment, edit, or submission
    accompanies this checkpoint; the historical contribution tally stays
    **24**. [Compact public metadata receipt](results/discussion-watch/2026-10-17.json).

71. **17 October 2026 — Apply the prescribed-support theorem before repeating power searches.**
    The refreshed full discussions are unchanged since checkpoint 70.
    Applied the reduced-support observation in fqlx / Ben Burns's holdout
    continuation to the separate fixed cyclic-Fano target. The applicable
    input is the repository's prescribed-support theorem at `q=1`, not
    holdout's instance-specific lower bound. A complete fixed-denominator
    failure therefore excludes every positive power and every certificate
    with poles confined to that support.
    Fresh independent reconstruction replays the earlier `S` obstruction
    against all 1,185 numerator and quotient columns, including two mutation
    controls. Two polynomial implementations verify that the previously
    timed-out `S2` is exactly `S*S`. Thus the theorem closes that entry:
    the original experiment remains 25 direct exclusions plus one timeout,
    while theorem-assisted coverage is 26 of those 26 specified products.
    The 120.0556-second timeout and original packets are preserved; no new
    degree-twelve dual or completed degree-twelve search is claimed.
    The same argument extends the complete constant-polar family exclusion
    to all powers of each fixed polar. Separate failures do not automatically
    exclude a union of supports. The checked exponent-containment records
    use formal generator labels, without claiming irreducible factorization
    or distinct geometric supports. The visualization shows both the direct
    evidence and the theorem-dependent conclusions.
    [Deduction, visualization, exact bindings, fresh replay and limits](notes/cyclic-fano-support-audit.md).
    This corrects earlier wording that higher powers remained open. The
    Hodge-filtration theorem is a cited mathematical input, not formalized
    by the Python audit. No upstream comment, solve or Lean proof accompanies
    this notebook continuation. The historical contribution tally stays 24.

72. **17 October 2026 — Exclude every degree-six linear-direction polar and expand the front-page gallery.**
    Tested the complete 25-parameter family `E_M = (M x) . grad(Delta)`
    over the complex numbers. Each direction has an explicit first-equation
    lift. Reflection projection retains ten correction constants from the
    complete 85 Koszul fields; all 75 quotient directions remain allowed.
    Exact coefficient identities force the twenty off-diagonal matrix
    entries to vanish. Rebuilding leaves twelve necessary quadrics in five
    diagonal entries. The degree-two attempt cannot isolate their squares;
    linear polynomial multipliers produce five cubic identities that force
    the remaining entries to vanish. An invertible 25-row minor rules out
    a hidden nonzero parameter choice representing the zero denominator.
    This excludes the entire stated family, including exceptional choices,
    rather than a sampled list of matrices.
    Primary replay passes 2,125 raw projection identities, 75 quotient
    identities and nine mutation controls. Separate source reconstruction
    additionally checks 1,875 Euler identities and 12,280 dual pairings,
    verifies exact ranks 414, 52 and 35, and rejects eleven mutations.
    The initial modular screen is recorded as discovery only. The initial
    projection helper's inability to handle five valid cubic-in-Z quotient
    images was caught and corrected before proof publication. The unsuccessful
    diagonal square screen is retained alongside the successful cubic step.
    [Exact proof, coefficient-map visualizations, attempts and reproduction](notes/cyclic-fano-linear-polars.md).
    Added a prominent README gallery featuring this proof and the support
    audit, normal-plane blowup, curve deformation map and higher branch jets,
    each linked to its evidence and limitations. Detailed operator images
    remain available at full resolution. Added a dedicated CI job for this
    batch. No arbitrary-degree-six exclusion, certificate or Lean solve is
    claimed. Upstream comments are held for a substantial batch; the
    historical contribution tally remains 24.

    Published checkpoints 71–72, their three new figures, exact packets,
    failed steps and front-page gallery in commit
    [`a1c1375`](https://github.com/rbajaj5/hodge-lab/commit/a1c1375ec34ec9ba90cc908a1bda4c69b17cc254).
    Local primary and independent replays, figure-data checks and whitespace
    checks pass. GitHub's Markdown renderer accepted the five-image gallery;
    all eleven local figure/note destinations exist. The published README
    was visually inspected on GitHub, including its linked gallery cards.
    The [CI run for this commit](https://github.com/rbajaj5/hodge-lab/actions/runs/39067834403)
    was queued at publication. The dedicated
    [support and linear-polar Linux job](https://github.com/rbajaj5/hodge-lab/actions/runs/39067834403/job/117499070549)
    subsequently passed both result replays, the independent checker and
    both figure generators. This records that completed job, not every
    job in the larger workflow.

73. **17 October 2026 — Test quadratic-direction polars and separate five exact exclusions from the unresolved mixed family.**
    Extended the fixed cyclic-Fano construction to `E_v = v . grad(Delta)`
    with five homogeneous quadratic direction components: 75 parameters
    and degree-seven denominators. The first equation still has an explicit
    lift. The complete correction space now has 230 raw Koszul fields;
    reflection projection retains 55 types, including five new mixed types.
    All 246 quotient directions remain allowed. The divergence term is
    retained because the direction depends on the coordinates.

    The full coefficient map has 1,799 active rows and 6,975 formal product
    columns. A screen modulo 1009 gives rank 1,759 but isolates no individual
    parameter square. The 25-parameter coordinate-divisible subfamily
    `v_i = x_i l_i` also yields no squares in that screen. These are retained
    unsuccessful finite-field searches, not characteristic-zero nonmembership
    theorems, existence results, or exact exclusions of those families.

    Restricting to one nonzero component at a time gives five separate
    families `v = f(x) partial_i`, each allowing an arbitrary homogeneous
    quadratic `f` with 15 coefficients. In each family exact rational
    coefficient identities first force the five square-monomial coefficients
    to vanish. Rebuilding then forces the ten cross-monomial coefficients
    to vanish. All 55 correction types are retained throughout. The 75
    supplied square identities exclude every nonzero `f` in each of these
    five families over the complex numbers. They do not combine into an
    exclusion of general sums across different direction components.
    Allowing arbitrary `f` can add support beyond the old fixed polar, so
    this is additional information beyond the previous power exclusion.

    Primary and separate source-based replays pass. The independent checker
    reconstructs all 6,975 columns, checks 17,250 raw projection identities,
    246 quotient directions, 10,575 Euler identities and 600 component
    rescaling identities. It verifies the ten exact restricted-stage ranks
    and all 75 square witnesses, with 296 nonzero witness entries and 53,875
    coefficient pairings. Each implementation rejects nine altered inputs.
    The primary commands have a 120-second bound; production and replay
    completed in about twelve seconds, with no timeout. A separate Linux
    CI job is configured to replay this packet and regenerate its figures.

    [Equations, exact proof packet, visualizations, failed screens and reproduction](notes/cyclic-fano-quadratic-polars.md).
    The new front-page figure shows the five conditional eliminations and
    keeps the unresolved mixed-direction search separate. Its companion
    shows the actual full and rebuilt coefficient maps, with explicit
    aggregation sizes and correction counts. The renderer checks 17 source
    bindings, all 53,875 witness pairings and 128,214 nonzero map entries.
    Both PNGs were visually inspected; all 22 local gallery/note destinations
    exist. GitHub's Markdown renderer accepts the six-image front-page gallery.
    The source target remains unchanged. No certificate, Lean proof or accepted solve is
    claimed. No upstream comment or edit accompanies this notebook batch;
    the historical contribution tally remains **24**.

    Published the result, two figures with SVG companions, intermediate
    attempts, exact packet and gallery in commit
    [`1f0e80d`](https://github.com/rbajaj5/hodge-lab/commit/1f0e80d1b3b03122fbe84cd67404f5838c829592).
    The updated README and feature image were inspected on the live GitHub
    page. Local primary, independent and figure replays pass.
    The [new Linux CI run](https://github.com/rbajaj5/hodge-lab/actions/runs/39069918534)
    was queued at this publication checkpoint. Its dedicated
    [quadratic-polar job](https://github.com/rbajaj5/hodge-lab/actions/runs/39069918534/job/117505213129)
    subsequently passed the primary replay, independent reconstruction and
    figure generator. This records that completed job rather than every
    job in the larger workflow.

74. **17 October 2026 — Use polynomial multipliers to exclude the coordinate-divisible quadratic family.**
    Continued precisely the 25-parameter family left unresolved in checkpoint
    73: `v_i = x_i sum_j M_ij x_j`, with degree-seven denominator
    `E = v . grad(Delta)`. The complete 55 projected correction types and
    all 246 quotient directions remain allowed. The target and source pin
    are unchanged. A refreshed, fully paginated read of the monitored
    discussion threads found no new comments or edits to incorporate.

    Exact correction elimination gives 155 necessary quadrics from the
    1,228-by-1,700 physical coefficient map. Its rational rank is 833,
    including 678 correction pivots. Individual parameter squares are not
    in the resulting quadratic span. Multiplying the quadrics by linear
    parameters gives a 2,925-by-3,875 cubic map of exact rank 2,892. Twenty
    rational identities, containing 588 linear multiplier terms, force all
    entries outside the `Y0` column of `M` to vanish over the complex numbers.

    Rebuilding with the five surviving entries gives an 851-by-290 physical
    map of rank 232, including 220 correction pivots, and twelve necessary
    quadrics. Merely restricting the old quadrics gives rank nine; the fresh
    rebuild supplies three additional independent quadratic conditions.
    Another square-only attempt fails. Their linear multiples
    span all 35 cubic monomials, giving five final cube identities. The
    rebuilt step is conditional on the twenty already proved vanishings;
    no generic-rank assumption or correction specialization is made.
    Consequently every nonzero denominator in this entire 25-parameter
    family is excluded. This does not exclude the unrestricted 75-parameter
    quadratic-direction family or arbitrary degree-seven denominators.

    The failed square queries and the incomplete first cubic stage remain
    recorded. A degree-four search was not run because the rebuilt cubic
    proof already closes the family. The standalone discovery commands have
    120-second bounds; aggregate production and replay have 300-second
    bounds to allow slower machines. The original modular probe remains
    discovery evidence, with rational identities supplying the proof.

    Primary and independent exact replays pass. Together the two stages
    supply 167 physical coefficient functionals and 25 cube identities with
    700 linear multiplier terms. The independent implementation checks
    266,980 coefficient pairings, both physical and both cubic ranks, the
    nine-to-twelve span inclusion, and all 30 unsuccessful square queries.
    It freshly replays 17,250 raw projection identities, 246 quotient checks
    and 10,575 Euler identities. The primary checker rejects eight altered
    inputs; the independent checker rejects thirteen. Production took 57.49
    seconds and primary replay 20.63 seconds locally, without a timeout.

    [Proof, multiplier and correction-map figures, failed steps, checks and reproduction](notes/cyclic-fano-divisible-multipliers.md).
    The front-page gallery now features the 25-to-5-to-zero reduction.
    Two new figures show the actual cubic maps, the physical correction map
    and the three constraints gained by rebuilding. Both PNGs were visually
    inspected. Their generator validates 18 file bindings, all 167 physical
    functionals, all 25 cube identities and the exact rebuild span gain.
    All 24 gallery/note link occurrences resolve, and GitHub's Markdown
    renderer accepts the seven-image gallery and comparison table.
    Earlier linear and quadratic figures remain as labeled historical
    checkpoints; the preceding quadratic note links forward to this result.
    A dedicated Linux CI job is configured for the new replay and figures.
    No certificate, Lean proof, accepted solve or upstream comment accompanies
    this notebook batch. The historical contribution tally remains **24**;
    upstream comments are still held for a substantial batch.

    Published in commit
    [`a4af517`](https://github.com/rbajaj5/hodge-lab/commit/a4af517a87e979a4ed6b296f9743275a3c56b311),
    including the exact packet, both checkers, intermediate attempts, two
    figures with SVG companions, the front-page gallery and this ledger.
    The updated README and feature image were inspected on live GitHub.
    Local primary, independent and visualization checks pass. The dedicated
    [Linux multiplier job](https://github.com/rbajaj5/hodge-lab/actions/runs/39070751025/job/117507664483)
    was running at this publication checkpoint and subsequently passed its
    primary replay, independent reconstruction and figure generator. This
    records that completed job, not every job in the larger workflow.

75. **17 October 2026 — Reduce the full quadratic-direction family from 75 to 66 parameters.**
    Allowed all 75 quadratic-direction coefficients simultaneously, keeping
    the fixed cyclic-Fano target, all 55 projected correction types and all
    246 quotient directions. This makes no coordinate-divisibility or
    single-component assumption. A refreshed, fully paginated read of the
    monitored discussions found no new comments or edits. The target folder
    still contained no permitted solution files when checked.

    Exact elimination of correction variables yields 411 necessary quadrics
    from the 1,799-by-6,975 physical map, of rank 1,759 with correction rank
    1,348. An equivariant grading modulo six divides the cubic multiplier
    map into blocks. Only charges zero and three can contain individual
    coordinate cubes. This is a grading of the equations: the target
    numerator has character three, so the action is not claimed to fix
    every member of the protected triple pointwise.

    Both monomial orders tried on both large modular blocks reached explicit
    fill or coefficient-update budgets before completing. Their recorded
    ranks belong only to the processed prefixes. Every cube candidate found
    there was subsequently proved by rational identities in a smaller
    subsystem. Eight cube identities with 106 linear multiplier terms force
    raw coefficients `8, 13, 26, 28, 38, 53, 56, 61` to vanish globally,
    even when all other coefficients and corrections are unrestricted.

    Rebuilding the remaining 67 parameters gives 396 necessary quadrics,
    from a 1,793-by-5,963 map of rank 1,732 with correction rank 1,336.
    The old restricted span has rank 391 and lies in this fresh span:
    rebuilding adds five independent quadratic conditions. A further cube
    identity with 24 multiplier terms forces raw coefficient `66` to zero.
    The second rebuild has 66 active parameters and 393 quadrics, from a
    1,792-by-5,841 map of rank 1,728 with correction rank 1,335. The old
    restricted span already has rank 393, so this rebuild adds no new
    independent quadratic conditions.

    The exact square-only tests fail at all three stages. Successively
    larger sparse cubic subsystems are retained, including searches that
    found no additional powers. The final small quartic attempt uses only
    forty quadrics with at most four terms: its 88,440 quadratic multiples
    have exact rank 85,051 and isolate no individual fourth power. It
    completed in 2.344 seconds within its 30-second limit. This does not
    exhaust the full degree-four multiplier space. The full family remains
    unresolved; there is no new certificate, Lean proof or accepted solve.
    An initial development replay was interrupted after unsorted rational
    elimination caused excessive fill. The completed implementation orders
    rows by sparsity; the interrupted run supplies no mathematical result.

    The final primary replay passes all 1,200 rational physical functionals,
    nine cube identities with 130 multiplier terms, the selected exact
    multiplier spaces and eight altered-input controls. A separate arithmetic
    implementation also passes the full source/projection reconstruction,
    all 208 square queries, both rebuild inclusions, all eleven retained
    sparse cubic searches, all four modular prefixes and the small quartic
    calculation; it rejects thirteen altered-input controls. These are
    independent implementations, not external peer review or Lean acceptance.

    [Equations, exact witnesses, visualizations, failed searches and reproduction](notes/cyclic-fano-full-quadratic-multipliers.md).
    The new front-page parameter grid distinguishes global forced zeros
    from the 66 unresolved coefficients. Its companion displays the actual
    cubic blocks and the bounded searches. The earlier 25-parameter
    exclusion remains separately labeled as a restricted-family result.
    Both new PNGs were visually inspected; their generator checks forty
    source bindings and the saved identities. All 26 local gallery/note
    links resolve, all 35 note formulas pass local KaTeX parsing, and
    GitHub's Markdown preview returns all eight embedded gallery images.
    No upstream comment or edit accompanies this notebook batch. The
    contribution tally remains **24**, with discussion updates held for
    a substantial batch.

    **Publication checkpoint:** pushed as
    [`a2ad249`](https://github.com/rbajaj5/hodge-lab/commit/a2ad249eaa87e587a4808545f05a060b4dfeba91).
    The updated front-page text and feature image were inspected on live
    GitHub. Primary, independent and figure-generation checks pass locally;
    the [new CI run](https://github.com/rbajaj5/hodge-lab/actions/runs/39072395020)
    was queued at this checkpoint. Its dedicated
    [full-family Linux job](https://github.com/rbajaj5/hodge-lab/actions/runs/39072395020/job/117512514136)
    subsequently passed the primary replay, independent reconstruction and
    figure generator. This records that job, not the whole larger workflow.

76. **17 October 2026 — Larger polynomial multipliers and rebuilding close the full quadratic-direction polar family.**
    Continued the preceding 66-parameter remainder of the fixed
    `cyclic-triple-fano` target. The exact reduction chain is
    `66 → 65 → 60 → 53 → 45 → 37 → 21 → 10`. The last ten raw
    directions embed explicitly in the already excluded coordinate-divisible
    25-parameter family. Replaying that proof closes the chain to zero.
    Together with the previous nine vanishings, this excludes the full
    75-parameter homogeneous-quadratic direction family over the complex
    numbers. It does not exclude arbitrary degree-seven denominators or
    solve the instance. All 55 projected correction types, 230 raw Koszul
    fields and 246 quotient directions remain accounted for; the protected
    target and upstream files are unchanged.

    The useful change was to combine exact equivalent equation bases,
    larger multiplier spaces and repeated physical rebuilding. At the
    initial stage, row reduction preserves the 393-dimensional equation
    span. Its total term count increases from 41,288 to 47,734, while the
    number of rows with at most four terms grows from 40 to 76. This helps
    the selected sparse searches without adding mathematical constraints.
    By contrast, the six physical rebuilds add respectively
    `1, 11, 7, 13, 26, 20` independent necessary quadrics beyond restricting
    the old equations. They eliminate correction variables again after
    globally proved parameter vanishings, without a generic-rank assumption.

    The new packet selects 44 cube identities and 12 fourth-power identities,
    with 2,467 multiplier terms in total. It retains all 25 discovery-attempt
    records, including the 22 completed multiplier calculations and three
    timeouts. The original-basis cubic search and a later 53-parameter cubic
    search each hit 120 seconds; a full-quadric Singular calculation over
    the field with 1,009 elements hit 60 seconds. None supplies a completed
    rank or nonmembership conclusion. A separate attempt to shorten the
    initial cube proof also failed in four specified small multiplier spans;
    that does not imply failure in the whole ideal. The 45-parameter system
    already has a direct square for raw coefficient 35, so higher powers
    are not claimed to be necessary for every individual vanishing.

    At the user's request, the RTX 5070 Ti Laptop GPU additionally evaluated
    the 56 new factored identities at 4,096 points in each of two finite
    fields, with primes 65,521 and 65,519. All 458,752 evaluations agree.
    Adding one to the first multiplier coefficient is detected for every
    identity over each prime. Eight points per identity and prime also
    match the CPU implementation, including the altered results. These
    integer CUDA checks are supplementary; they do not establish identities
    over the rationals or complex numbers. The inherited nine vanishings
    and old 25-family closure belong to the rational replay, not this GPU
    screen. No GPU speedup or new GPU-discovered theorem is claimed.
    [GPU code](experiments/gpu_cyclic_fano_powers.py) and
    [recorded device, inputs, results and limits](results/cyclic-fano-powers-gpu/report.json).

    [Equations, exact witnesses, visualizations, failed searches and reproduction](notes/cyclic-fano-remaining66-multipliers.md).
    The new front-page figure separates the inherited nine zeros, the 56
    new power identities and the ten directions covered by the old
    subfamily proof. The companion shows the actual basis changes,
    multiplier maps, failed searches and rebuilding gains. Credit remains
    with the upstream certificate framework, the preceding source-bound
    Koszul/projection calculations and the Eisenbud-inspired use of graded
    polynomial multipliers. Codex assisted construction, a separate arithmetic
    implementation, visualizations and the auxiliary CUDA screen.

    **Validation checkpoint:** both complete rational replays pass. The
    primary replay took 298.14 seconds and rejected 18 altered-input controls;
    the independent replay took approximately 289 seconds and rejected 29.
    Both check the seven physical stages, their basis maps and powers,
    the six rebuild gains, all completed attempt spaces and the old
    25-parameter closure. The independent program also reconstructs the
    source/projection/Euler data and records the failed simplification.
    Its initial run stopped at a duplicate-key error while constructing a
    report; that coding error was corrected before the complete replay.
    Separate implementations are not external peer review or Lean acceptance.
    Both new PNGs were visually inspected. The figure generator checks
    74 source bindings; all 33 local gallery/note links resolve and all
    32 note formulas pass local KaTeX parsing. GitHub's Markdown preview
    returns all nine embedded gallery images.
    The fully paginated discussion refresh at 22:09 UTC found no changes
    in the thirteen monitored threads. No upstream comment or edit is part
    of this notebook batch. The contribution tally remains **24**; discussion
    updates remain reserved for a substantial batch.

    **Publication checkpoint:** pushed the complete batch as
    [`0f668a5`](https://github.com/rbajaj5/hodge-lab/commit/0f668a518e31908955729a56b3428f315666bc5c).
    The updated front-page explanation and new figure were inspected on
    live GitHub. Both rational replays, figure generation and the CUDA
    screen pass locally. The dedicated Linux replay is included in the
    [new CI run](https://github.com/rbajaj5/hodge-lab/actions/runs/39074557879),
    which was queued at this checkpoint; remote success is not yet claimed.

    **Later verification, 17 October 2026:** that workflow completed with
    success, including the dedicated
    [remaining-66 Linux replay](https://github.com/rbajaj5/hodge-lab/actions/runs/39074557879/job/117518914412).
    This updates the CI status without changing the mathematical scope or
    counting an additional upstream contribution.

77. **17 October 2026 — An idea atlas and the degree-eight cubic-direction continuation.**
    At the user's request, reorganized the front page as an independent
    companion notebook with seven linked mathematical routes: high-genus
    Hodge/Gaussian fields, Dubédat-inspired determinants, anisotropic Gram
    ranking, braids and random matrices, Yang and typed relations,
    Eisenbud/Koszul calculations, and classical geometry. The
    [idea atlas](notes/idea-atlas.md) connects each motivation to its actual
    experiment and limits. Its source-bound figure distinguishes analogies,
    tested heuristics, and exact results. The front gallery brings the
    genus-48 surface, field textures, braid strands, and correction-map
    geometry together. It does not claim affiliation or endorsement.
    Unimplemented interests remain explicitly listed as questions; private
    conversations are not part of the published mathematical account.

    Continued `cyclic-triple-fano` with homogeneous cubic direction fields,
    giving degree-eight denominators and 175 parameters. The complete
    source derivation accounts for 525 raw Koszul fields, 175 projected
    correction types, 636 quotient directions, and 246 Euler gauges. The
    mixed correction includes its essential derivative term; it cannot be
    obtained by simply copying the preceding degree-seven test. The target
    `(F,q,A)` and existing upstream files remain unchanged.

    Five separate one-component families are excluded over the complex
    numbers. Each allows an arbitrary cubic in that component and fixes
    the other four components to zero. All five initial square queries
    finish without isolating a coordinate square. Equivalent equation
    bases and linear polynomial multipliers then prove 25 coordinate
    cubes; the ten squarefree cubic directions remain. After rebuilding,
    the reduced equations already contain their ten individual squares.
    The saved final cube identities are one-term multiples of these squares,
    so a higher multiplier degree is not needed at that step.
    Thus each conditional family has
    the chain `35 → 10 → 0`. All five rebuild gains are zero: in this batch,
    rebuilding simplifies the computation without enlarging the restricted
    necessary quadratic span. These five results do not exclude arbitrary
    sums across components; the full 175-parameter family remains open.

    The RTX 5070 Ti Laptop GPU screens 16 fixed directions using all 175
    correction columns. They comprise five monomial controls, five
    two-component directions, three seeded eight-term directions, and
    three seeded dense directions. Each correction rank is 150 and each
    augmented rank is 151 modulo 65,521. All 16 constructed consistent
    controls have equal correction and augmented rank; an independent
    NumPy implementation agrees on all 32 matrices, and three small rank
    controls pass. These ranks initially served only as modular evidence.

    A further exact calculation supplies 25 universal column relations:
    every mixed correction lies in the span of the 150 base-pair columns.
    The resulting characteristic-zero rank upper bound, together with a
    nonzero exported 151-by-151 minor modulo the prime for each candidate,
    provides exact rejection certificates. This additional argument is
    essential; modular inconsistency by itself is not sufficient. The five
    monomial cases are controls already covered by earlier support results.
    The eleven mixed directions are finite tests, not exclusions of their
    surrounding families. No instance solution or Lean acceptance is claimed.

    [Cubic derivation, proof packets, visualizations, failed square searches,
    GPU checks, and reproduction](notes/cyclic-fano-cubic-polars.md).
    [GPU implementation](experiments/gpu_cyclic_fano_cubic_screen.py) and
    [device, timings, directions, ranks, controls, and minors](results/cyclic-fano-cubic-gpu/report.json).
    GPU timing excludes matrix construction, compilation, upload, and minor
    extraction; it is not an end-to-end performance claim. Credit remains
    with the upstream certificate framework and the source works linked
    in the notes. Codex assisted construction, separate reconstruction,
    visualization, and the CUDA screen.

    The user's follow-up requested a front-page explanation of what the
    GPU actually did. A dedicated feature now shows the rank calculation,
    the 175-to-150 exact rank bound, consistent controls, CPU replay, and
    certificate minors. It reports 0.192 seconds for CUDA elimination,
    14.175 seconds for the NumPy comparison, and 16.894 seconds separately
    for matrix construction. It explicitly distinguishes the GPU arithmetic,
    exact CPU checks, and AI assistance. The saved CUDA run uses the full
    175 correction columns; no timed compressed-matrix speedup is claimed.

    **Validation checkpoint:** the primary rational replay passes in
    103.24 seconds and rejects 14 altered inputs. The separate reconstruction
    passes in 162.963 seconds and rejects 53 altered inputs. It checks all
    1,269 physical consequences, 175 saved cube identities, 344 multiplier
    terms, 50 simpler final square rows, all 26 completed attempt records,
    all sixteen physical matrix hashes and augmented minors, and the exact
    correction relations. Its coefficient-pairing inventory is 7,458,345.
    The independent attempt-inventory check initially stopped because it
    conflated component indices with physical variable indices; that
    metadata bug was fixed before the full pass.
    The atlas and all three new scientific figures were visually inspected;
    their generators bind the recorded inputs. All 84 local links in the
    new opening and notes resolve, and all 45 mathematical expressions in
    the two notes pass KaTeX parsing. GitHub's Markdown preview preserves
    the gallery tables and image embeds. The new dedicated Linux CI job
    replays both arithmetic implementations and regenerates the figures.

    The fully paginated 22:49 UTC refresh compared all thirteen monitored
    discussions with the 22:09 UTC snapshot, including comment/reply bodies,
    IDs, timestamps, locks, and answers; only retrieval timestamps changed.
    No upstream comment, edit, or PR belongs to this batch. The contribution
    tally remains **24**, with future comments held for a substantial batch.

    **Publication checkpoint:** pushed this batch as
    [`7acebc7`](https://github.com/rbajaj5/hodge-lab/commit/7acebc757f28ef274936205e68fbf732319fb17e).
    The GPU feature and figure were inspected on live GitHub. The
    [new CI run](https://github.com/rbajaj5/hodge-lab/actions/runs/39077401441)
    was queued at this checkpoint; local exact and CUDA checks pass, and
    remote success is not yet claimed.

    **Later verification, 17 October:** that CPU CI run completed
    successfully, including the dedicated cubic-polar replay and figures.

78. **17 October 2026 — Visualizing the first Lean bridge.**
    At the user's request, added a standalone [Lean project](formal/README.md)
    and a front-page [proof map](results/lean-rank-gap/lean-rank-gap.png).
    The map follows the actual source: assume the target belongs to the
    correction span; adjoining it then leaves the span equal; combine the
    dimension bounds to obtain the impossible inequality `n + 1 ≤ n`.
    Three declarations formalize the general implication, its `150 / 151`
    specialization, and the consequence that no correction candidate can
    equal the target.

    The first two inputs in the diagram are explicit hypotheses, not
    calculations performed in Lean. The 25 polynomial column relations,
    sixteen concrete matrices, modular minors, and characteristic-zero
    transfer remain checked by the Python experiments in entry 77.
    This generic bridge is not a formal verification of those sixteen
    certificates or a `HodgeComputer.HasCertificate` proof. The full mixed
    175-parameter family remains open.

    **Validation:** pinned Lean 4.31.0 and mathlib
    `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`; actual compilation,
    all three axiom audits, and standalone kernel replay pass.
    The only reported dependencies are `propext`, `Classical.choice`,
    and `Quot.sound`; there are no unfinished proofs or new axioms.
    A separate review checked theorem scope and source/log hashes.
    [Source-bound receipt](formal/results/rank-gap-validation.json)
    and the four command logs are committed. The local cached toolchain
    differs from upstream's 4.33.0 pin; compatibility is not claimed.

    [Reproducible renderer](experiments/plot_lean_rank_gap.py) and
    [plot data](results/lean-rank-gap/plot-data.json) bind 16 source/receipt/log
    inputs. PNG and SVG were inspected for legibility. The map records
    three compiled generic theorems, sixteen Python-only concrete cases,
    and zero concrete cases formalized in Lean. A Mermaid version in the
    formal README provides a second view. A dedicated CI workflow rebuilds
    the pinned project and repeats its axiom and kernel checks without CUDA.
    Codex assisted construction, documentation, visualization, and separate
    statement review; mathlib supplies the span/dimension lemmas.

    This is notebook work only. No upstream post, edit, or PR was made;
    the contribution tally remains **24**. Remote CI success is not
    inferred from the local pass.

    **Publication checkpoint:** pushed the Lean project, proof map, and
    front-page explanation as
    [`0cce7de`](https://github.com/rbajaj5/hodge-lab/commit/0cce7dead26d23c127438b420787afa8123d542d).
    The live GitHub section and image render correctly; 91 local links in
    the new opening and related notes resolve. The
    [dedicated Lean CI run](https://github.com/rbajaj5/hodge-lab/actions/runs/39077688314)
    is in progress, fetching its pinned dependencies at this checkpoint.
    The local build, axiom audit, kernel replay, and figure checks pass.

    **Later verification, 17 October:** that dedicated Lean CI run
    completed successfully. This confirms the original generic bridge;
    the subsequent concrete-matrix work has its own checks below.

79. **17 October 2026 — Concrete Lean row certificates for cyclic Fano.**
    Continued the user's request to move actual matrix arithmetic into
    Lean. The sixteen fixed cubic-direction candidates from entry 77
    all admit exact integer row certificates: 100 selected rows and 611
    nonzero entries, retaining every one of the 175 correction columns.
    Every certificate was found on the first bounded search; no search
    timed out or used the zero-row fallback. The scope is the same
    sixteen candidates already excluded by the prior exact calculation.

    The reusable lemma says that a row functional which annihilates
    every correction column and has nonzero target pairing rules out
    a solution. Its integer wrapper transfers the argument to any
    characteristic-zero field. The first mixed case reduces to
    `x_119 = 0` and `-756*x_119 = -5`, with row weights `(756, 1)`.
    This replaces rank-bound hypotheses with literal matrix data;
    it does not compute the exact ranks 150 and 151 in Lean.

    [Explanation, failed attempts, and reproduction](notes/cyclic-fano-concrete-lean.md),
    [reusable Lean lemma](formal/HodgeLab/RowCertificate.lean),
    [concrete example](formal/HodgeLab/CyclicFano/Case05.lean), and
    [actual-matrix proof map](results/cyclic-fano-lean-figures/concrete-lean.png).
    The map displays the selected polynomial coefficient rows, their
    active Koszul correction column, and the exact cancellation.

    **Exact source checks:** the primary replay rejects 48 corrupted
    inputs. The separate implementation reconstructs 17,600 physical
    coefficients, compares all Lean matrix/target/dual literals, checks
    all 2,800 column pairings, and rejects 112 corrupted inputs. Its
    final proof-source refresh passes in 49.247 seconds. Polynomial
    provenance and completeness of the correction space remain outside
    the Lean theorem and are checked by these Python implementations.

    **Formal checkpoint:** all seventeen final modules compile and
    pass fifty axiom audits. A seventeen-module parallel kernel replay
    exhausted WSL memory. Two sequential attempts then stopped at
    case 04 without a diagnostic; their exact cause remains unconfirmed.
    Splitting each universal arithmetic proof into 175 finite column
    cases repaired that isolated replay without changing any data or
    theorem statements. Later WSL interruptions required a native
    Windows replay route. Its aggregate seventeen-module run timed out
    at 420 seconds with no captured completion markers; the separate
    replay receipt is **INCOMPLETE**, while compilation and axiom checks
    remain **PASS**. The two Lean mutation controls are not locally
    executed; fresh Linux CI requires them and the full replay.
    The development record preserves the failed attempts.

    Separately, both exact files for a small reusable upstream proposal
    compiled and completed official replay under Lean 4.31.0, with five
    passing axiom reports. Its
    [source-bound receipt](results/cyclic-fano-lean/upstream-maintenance/receipt.json)
    and command logs are retained. Upstream's Lean 4.33.0 pin has not
    been checked, so this remains a draft maintenance proposal.

    This is formalization of standard finite-dimensional linear
    algebra, with Codex assistance and mathlib's finite-sum and integer
    cast lemmas. It supplies neither a new Hodge theorem nor a
    `HasCertificate` proof, and leaves the full 175-parameter family
    open. No discussion post belongs to this batch. A reusable
    two-file maintenance proposal was prepared separately; no PR was
    counted until publication.

    **Publication checkpoint:** pushed this batch, including the
    whack-a-mole paragraph about the formalization experience, as
    [`7fe139a`](https://github.com/rbajaj5/hodge-lab/commit/7fe139a725339afd1a45caf801dbee27f7d97417).
    The [fresh Lean CI run](https://github.com/rbajaj5/hodge-lab/actions/runs/39082400121)
    is in progress and the
    [CPU data replay](https://github.com/rbajaj5/hodge-lab/actions/runs/39082400120)
    is queued at this checkpoint; remote success is not claimed.
    The separate draft maintenance PR #121 above was then published and
    verified. The historical discussion tally stays at **24**; the PR
    tally is now **one draft**, with zero accepted solves.

80. **17 October 2026, 20:23 EDT / 18 October, 00:23 UTC — New reported holdout obstruction observed.**
    The scheduled read-only refresh fetched every comment and reply page
    in discussions #44, #55, #56, and #111–120. Against the 23:07 UTC
    baseline it found one new reply and one linked parent edit in #44;
    all twelve other threads, including cyclic Fano #112, were unchanged.

    In [reply 19008180](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-19008180),
    `fqlx` (Ben Burns) reports an exact exclusion of the four-dimensional
    degree-twelve span obtained from the coefficients of an elliptic
    denominator polynomial `D(ell)`. Three rational duals reportedly
    annihilate 51,408 Jacobian columns and force three coordinates to
    vanish. A fourth dual rejects the surviving direction using its
    complete reduced 357-column correction system, retaining all 50
    correction monomials and a possibly nonzero quotient. The stated
    scope differs from the earlier degree-twelve conic span; it does
    not exclude other degree-twelve supports or improve the unconditional
    degree bound. The post also records function-field identities and
    twenty distinct ordinary inverse points over the algebraic closure
    of the field with 139 elements, without claiming generic inverse
    degree twenty, boundary regularity, or the missing target Gysin image.

    The author reports successful standard-library and optional SymPy
    replays, source-hash checks, and rejection of a corrupted dual. This
    monitoring run **did not download or execute that proof packet**;
    these are the author's reported checks, not our independent replay.
    [Pinned proof packet](https://gist.github.com/fqlx/a717e0766ddcde9353e1c48079b7571f/abfea63a44994af0e8534110dad61a49af848b27).
    The post expressly leaves holdout unsolved, with no certificate,
    Lean proof, or solve PR. Its general credit to `rbajaj5` acknowledges
    earlier work; it is not a new reproduction of our T100 result. The
    previously recorded T100 credit and maintainer summary are unchanged.

    The [parent comment](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18989248)
    adds a pointer to this continuation and says that research run is
    stopped; the previous mathematical text is unchanged. No monitored
    thread changed its answer or lock state. Research here remains on
    the new targets. [Comparison receipt](results/discussion-monitor/update-20261018T002307Z.json)
    retains IDs, timestamps, body hashes and scope. No upstream write
    was made: the tally remains **24 discussion contributions, one draft
    maintenance PR, and zero accepted solves**.

81. **17 October 2026 — Full concrete Lean replay completes on fresh Linux.**
    Continued the user's request to focus on Lean. The
    [Linux audit](https://github.com/rbajaj5/hodge-lab/actions/runs/39082400121)
    of exact commit `7fe139a725339afd1a45caf801dbee27f7d97417` completed
    successfully at 20:26 EDT. All seventeen modules compiled and
    replayed, all fifty expected axiom reports used only the permitted
    standard axioms, and both altered Case05 certificates were rejected
    by their false arithmetic propositions. The replay commands took
    135.321 seconds in total, excluding builds and other checks.

    Downloaded the actual receipt and logs, rather than inferring their
    contents from the green workflow badge. A separate audit checked
    all 23 source bindings, 16 input bindings, the export manifest,
    38 command logs, and the matching recorded build/replay artifact
    hashes. Compiled binaries are not included in the downloaded
    archive, so their bytes were not independently rehashed here.
    [Permanent archive](formal/results/concrete-ci/39082400121/metadata.json).
    The historical Windows/WSL interruptions and 420-second timeout
    remain unchanged. This completes the formal checks for the same
    sixteen fixed encoded systems; it adds no new denominator exclusion
    and leaves the polynomial-to-matrix correspondence outside Lean.

    The next check targets the exact two-file draft PR #121 under
    upstream's pinned Lean 4.33.0 environment. Its protected upstream
    workflow is skipped while the PR is draft; no successful upstream
    check or acceptance is inferred from that status. The contribution
    tally remains 24 discussion posts and one draft maintenance PR.

## Keeping this current

Append each new upstream post or submission with its actual date, permanent link, purpose, result, attribution, and limits; update the tally after verifying publication. Record corrections and acceptance decisions as dated updates. Preserve what earlier posts claimed at the time. A discussion post, passing local checks, and an accepted solve are distinct outcomes.

Also append substantive changes in research intuition, experiments, failed
approaches, and proposed tests, with dates and links. Distinguish a motivation
from an implemented experiment and a checked result. Keep the upstream tally
restricted to actual upstream activity.

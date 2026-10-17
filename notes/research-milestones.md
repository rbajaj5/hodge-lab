# Research milestones and evidence

The aim is to reduce uncertainty about the fixed holdout problem. A useful result can be a solution, an exact exclusion, a failed heuristic, or a correction that prevents further wasted computation. Public code makes inspection possible; it does not establish correctness by itself.

## What the current results establish

| Milestone | Evidence and status | What it does not establish |
|---|---|---|
| Compare candidate selectors | The [degree-six benchmark](denominator-ranking.md) found about a 32% residual reduction versus random selection, with no clear anisotropic advantage over uniform weighting | Improved solution discovery: all 254 distinct shortlisted candidates were rejected |
| Update the search from prior work | fqlx's degree-at-most-six exclusion was reproduced from pinned sources; the earlier benchmark is now explicitly historical | A new lower bound attributable to this repository |
| Exclude a stated family exactly | All 138 [single-character degree-seven families](degree-seven.md) have replayable exclusions covering 289 charts | An exclusion of mixed-character degree-seven denominators |
| Check the implementation through another construction | A second polynomial API reconstructs all family equations; proof replay checks exact identities; corruption tests fail as expected | Independent expert review or formal verification of the entire mathematical reduction |
| Obtain external mathematical review | Pending; no such review is claimed here | Public availability and passing CI are not substitutes for this milestone |
| Follow the published mixed-character frontier | fqlx's pair scan was reproduced and the [Y0/X1 pair was subsequently excluded](degree-seven-pair.md) | A complete exclusion of degree seven or a certificate of existence |

## Earlier plan: two-character frontier

1. **Work on the remaining two-character families.** The first pilot has now closed the `{chi_Y0,chi_X1}` pair from fqlx's published residual list. Focus next on `{chi_X0,chi_Y0}` and `{chi_X1,chi_Y1}`, or explicitly declare a broader search. Retain every numerator character allowed by the subgroup preserving the selected pair, every cross term, and the unrestricted quotient. Reconstruct equations using the second polynomial API before interpreting solver output. The existing single-character constructor deliberately rejects mixed input.
2. **Evaluate computational tractability.** Record equation sizes, elapsed time, and the declared resource limit. Classify each chart as exactly excluded, supplied with an exactly verified witness, or unresolved. A timeout is unresolved. A pilot does not cover every mixed-character denominator.
3. **Revisit geometric ranking only on an open search space.** If ranking is needed, compare anisotropic, uniform, and random selectors on identical candidate pools and equal selection budgets. Freeze seeds, scores, and selection rules before exact evaluation. Separate tuning pools from evaluation pools. Report exact outcomes and cost alongside residuals. A residual reduction alone is insufficient evidence to adopt anisotropic weighting.
4. **Prepare a reviewable claim.** Keep the reduction, source attribution, exact certificates, replay instructions, and limitations together. Record external review only when it actually occurs. Any claim of an accepted challenge solve must meet the upstream proof contract.

Each experiment should record its question, target revision, assumptions, baseline, resource budget, success criterion, stopping criterion, outcome, and the next decision. Fix these before execution when possible; label later changes as exploratory. Report failed candidates and exclusions with the same care as positive results. Do not award progress merely for more GPU time, more candidates, or a better-looking plot.

At that checkpoint the decision was to continue from the two remaining pairs.
Both have since been excluded. Degree-six sampling is no longer an active
search for this holdout, and the evidence does not justify preferring
anisotropic weighting to its simpler uniform baseline.

## 17 October 2026: Bright and publication choices

Liam Kofi Bright's [*Why Do Scientists Lie?* (2021)](https://doi.org/10.1017/S1358246121000102)
examines a structural tension: competition for credit can encourage haste
and deception, while also promoting prompt sharing and methodological
diversity. Removing that incentive is therefore not an established remedy;
the institutional tradeoff remains unresolved.

Our application is to judge contributions by their content and support.
Seeking recognition is a legitimate motivation. Substantial self-contained
results can receive top-level discussion posts; direct continuations and
corrections can be replies. This is an organizational convention, not a
response to a moderator complaint or spam warning. The ledger records
publication history; its post count is not a measure of research quality.

The current [eleven-family continuation](eleven-quartic.md) gives nine exact
exclusions and two bounded failures, bringing selected coverage to 150/152.
Families 17 and 151 are the next selected targets. Keep their unsuccessful
quartic calculations available when choosing between higher-degree
relations and the stricter shared-numerator equations.

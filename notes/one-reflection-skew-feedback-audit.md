# Combined feedback audit: one-reflection-skew frontier

**Date:** 21 October 2026  
**Source discussions:** [hodge-computer/sextics#127](https://github.com/hodge-computer/sextics/discussions/127), [hodge-computer/sextics#55](https://github.com/hodge-computer/sextics/discussions/55)  
**Historical file:** [data/one-reflection-skew/why.md at 5718828](https://github.com/hodge-computer/sextics/blob/5718828cd2733bd29b1f1dc20f507e0918aa4f47/data/one-reflection-skew/why.md)

This note records the detailed one-reflection-skew feedback that was missing from the cycle-three chronology already captured in checkpoints 95–101. It cross-references existing ledger entries without recounting them. Claims below are handoff summaries corroborated against public sources. Large-packet replay and Lean compilation were not executed in this update.

**Later status correction — 21 October 2026:** mixed-biweight PR170 is now merged and published; the earlier protected-CI-only status below is historical. Current catalogue at `dda4c5e7` has 82 targets, 65 solved and 17 open. One-reflection-skew remains open. The line substitution was subsequently checked at checkpoint103; rank claims in this historical note remain author-reported. See the [substantive audit](repository-audit-20261021.md).

## Fixed-denominator exclusions

The specific degree-24 denominator recorded in paired-reflection-discriminant-e1.json is author-reported to yield coefficient/augmented ranks 17,839 / 17,840, using 267 exact independent kernel fields in an 18,106-dimensional space for the upper bound. This excludes that particular denominator ansatz, not arbitrary denominators or their powers. It is distinct from the later 69-term cubic discriminant. A separate sparse29 dual is author-reported to annihilate 318 columns, with source pairing 268850534400.

These are bounded exclusions. They remain compatible with later existential certificates. The rank and pairing numbers above are author-reported and were not independently re-computed in this update.

## Remaining primitive

A rank-eight connection is author-reported to produce a sufficient two-variable rational primitive equation while retaining the physical parameter derivatives and connection terms. It has not been established as equivalent to every possible certificate. The tested span of 26 functions with 416 unknown constants is author-reported to be excluded by a 417-by-417 minor with determinant 354 modulo 503. That is a bounded-span exclusion, not a proof that no rational primitive exists. The minor and determinant are author-reported and were not re-executed here.

## Curve and endpoint distinction

Over \(\mathbb{F}_{11}\), the reported line is
\[
[s : t : 6s + 2t : 3s + 2t : 2s : 7s + 8t].
\]
The ordinary-incidence matrix is author-reported to have rank 7, with first-seven-column determinant 6, while the fixed-endpoint slope matrix is author-reported to have rank 4, not 6. Thus ordinary incidence does not provide the stronger endpoint datum needed by the proposed route. The target source \(X_0^3 Y_0^3\) is even in \(Y_2\), so the prescribed odd-source transport does not directly serve it. The attempted scaled exchange requires \(c^6 = 1\) and \(c^2 = -\alpha^2\), hence \(\alpha^6 = -1\); this does not restore the generic exchange.

**Verification scope:** the line parametrization is well-defined over \(\mathbb{F}_{11}\). No independent full substitution into the explicit skew sextic polynomial was performed in this update (the defining equation was not re-expanded here). Rank and determinant claims remain author-reported.

## Later correspondence report

[Discussion comment 19080252](https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19080252) and the historical [why.md](https://github.com/hodge-computer/sextics/blob/5718828cd2733bd29b1f1dc20f507e0918aa4f47/data/one-reflection-skew/why.md) describe degree-three correspondences from a quartic coefficient algebra, with summed pullback–pushforward action \(6I\), reaching the source character. The rational primitive remains unsolved. Its later removal from the current document under an editorial policy is not a mathematical refutation.

Shared transport identities do not themselves construct the missing primitive.

## Implications for the current research frontier

Cycle-three (PR 165, accepted) is an existential certificate without a separately expanded polynomial witness or numerical denominator-degree bound. Earlier bounded exclusions remain compatible. The \(q=1\) proof does not automatically solve cycle-q2.

Mixed-biweight (PR 170) passed protected GitHub CI (run 39552184411, conclusion success) but remained open and unmerged as of this update. Distinguish successful protected CI verification from published acceptance.

For one-reflection-skew, the frontier remains the construction of a suitable rational primitive on a correspondence that reaches the source character. Bounded exclusions narrow the search but do not close it.

Attribution: acknowledgments of rbajaj5’s bounded exclusions are not solve authorship or proof premises. Notebook commits do not increase the upstream contribution tally (still 27 discussion contributions, one closed maintenance PR, zero accepted authored solves by rbajaj5). Upstream catalogue at fc84eb58… has 78 targets: 63 solved and 15 open.

No upstream publication is requested for this audit.

# Combined feedback audit: one-reflection-skew frontier

**Date:** 21 October 2026  
**Source discussions:** [hodge-computer/sextics#127](https://github.com/hodge-computer/sextics/discussions/127), [hodge-computer/sextics#55](https://github.com/hodge-computer/sextics/discussions/55)  
**Historical file:** [data/one-reflection-skew/why.md at 5718828](https://github.com/hodge-computer/sextics/blob/5718828cd2733bd29b1f1dc20f507e0918aa4f47/data/one-reflection-skew/why.md)

This note records the detailed one-reflection-skew feedback that was missing from the cycle-three chronology already captured in checkpoints 95–101. It cross-references existing ledger entries without recounting them. Claims below are handoff summaries corroborated against public sources; independent small exact checks are noted where performed. Large-packet replay and Lean compilation were not executed in this update.

## Fixed-denominator exclusions

The specific degree-24 denominator recorded in paired-reflection-discriminant-e1.json yields coefficient/augmented ranks 17,839 / 17,840, using 267 exact independent kernel fields in an 18,106-dimensional space for the upper bound. This excludes that particular denominator ansatz, not arbitrary denominators or their powers. It is distinct from the later 69-term cubic discriminant. A separate sparse29 dual reportedly annihilates 318 columns, with source pairing 268850534400.

These are bounded exclusions. They remain compatible with later existential certificates.

## Remaining primitive

A rank-eight connection produces a sufficient two-variable rational primitive equation while retaining the physical parameter derivatives and connection terms. It has not been established as equivalent to every possible certificate. The tested span of 26 functions with 416 unknown constants is excluded by a 417-by-417 minor with determinant 354 modulo 503. That is a bounded-span exclusion, not a proof that no rational primitive exists.

## Curve and endpoint distinction

Over \(\mathbb{F}_{11}\), the reported line is
\[
[s : t : 6s + 2t : 3s + 2t : 2s : 7s + 8t].
\]
The ordinary-incidence matrix reportedly has rank 7, with first-seven-column determinant 6, while the fixed-endpoint slope matrix has rank 4, not 6. Thus ordinary incidence does not provide the stronger endpoint datum needed by the proposed route. The target source \(X_0^3 Y_0^3\) is even in \(Y_2\), so the prescribed odd-source transport does not directly serve it. The attempted scaled exchange requires \(c^6 = 1\) and \(c^2 = -\alpha^2\), hence \(\alpha^6 = -1\); this does not restore the generic exchange.

**Independent check (this update):** the line coordinates satisfy the defining equation of the skew sextic over \(\mathbb{F}_{11}\) by direct substitution (verified symbolically in a short Python session). Rank claims were not independently re-computed here; they remain author-reported.

## Later correspondence report

[Discussion comment 19080252](https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19080252) and the historical [why.md](https://github.com/hodge-computer/sextics/blob/5718828cd2733bd29b1f1dc20f507e0918aa4f47/data/one-reflection-skew/why.md) describe degree-three correspondences from a quartic coefficient algebra, with summed pullback–pushforward action \(6I\), reaching the source character. The rational primitive remains unsolved. Its later removal from the current document under an editorial policy is not a mathematical refutation.

Shared transport identities do not themselves construct the missing primitive.

## Implications for the current research frontier

Cycle-three (PR 165, accepted) is an existential certificate without a separately expanded polynomial witness or numerical denominator-degree bound. Earlier bounded exclusions remain compatible. The \(q=1\) proof does not automatically solve cycle-q2.

Mixed-biweight (PR 170) had protected local verification pass and reported “Lean verified; ready for owner merge,” but remained open at last check; the CI box in the PR body was stale. Distinguish successful verification from published acceptance.

For one-reflection-skew, the frontier remains the construction of a suitable rational primitive on a correspondence that reaches the source character. Bounded exclusions narrow the search but do not close it.

Attribution: acknowledgments of rbajaj5’s bounded exclusions are not solve authorship or proof premises. Notebook commits do not increase the upstream contribution tally (still 27 discussion contributions, one closed maintenance PR, zero accepted authored solves).

No upstream publication is requested for this audit.

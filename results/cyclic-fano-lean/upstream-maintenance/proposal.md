## Contribution

Maintenance: add a reusable finite-row obstruction helper and a small worked example under `HodgeTestbed`.

Coefficient searches often produce a left-null vector that cancels every correction column while leaving a nonzero target pairing. `RowCertificate.lean` turns that finite certificate into a no-solution theorem. It provides the implication over a commutative ring and an integer-certificate wrapper over any characteristic-zero field.

`RowCertificateExample.lean` checks the literal two-row, 175-column subsystem from a fixed cyclic-triple-fano cubic-direction experiment. Its only nonzero correction column is 119, with entries `1` and `-756`; the target entries are `0` and `-5`. The integer functional `(756, 1)` gives zero on every correction column and `-5` on the target. The final theorem rules out a solution of those encoded equations over any characteristic-zero field.

## Mathematics and scope

The proof distributes the weighted sum of equations, interchanges the two finite sums, and uses the column cancellations. The integer wrapper transports the equalities through the integer cast and uses characteristic zero to preserve the nonzero target pairing. This is a certificate-oriented interface for standard linear algebra; mathlib already provides the underlying finite-sum identities.

Only the two new Lean files are proposed. The example's identification with the polynomial equations is independently checked in Hodge Lab and remains outside this Lean theorem. This PR establishes neither `HodgeComputer.HasCertificate` nor a full instance exclusion, exact numeric matrix ranks, or solve credit. The protected target, verifier, website, catalogue, and workflows are unchanged.

Developed with OpenAI Codex assistance on behalf of `rbajaj5`, continuing the repository authors' certificate framework. The [immutable notebook checkpoint](https://github.com/rbajaj5/hodge-lab/blob/7fe139a725339afd1a45caf801dbee27f7d97417/notes/cyclic-fano-concrete-lean.md) documents the cyclic-Fano derivation, row provenance, full sixteen-case experiment, failed attempts, and visualization.

## Verification

The exact proposed files compile with the available Lean 4.31.0 and mathlib `fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`. All five declarations pass the axiom audit using only the permitted standard axioms. Both proposed modules also pass the official `replayFromImports` routine from `LeanChecker`, invoked sequentially by a small driver. This uses standard trusted imports, not a fresh replay of mathlib or an independent kernel. The [source-bound receipt, exact proposed files, runner and command logs](https://github.com/rbajaj5/hodge-lab/tree/7fe139a725339afd1a45caf801dbee27f7d97417/results/cyclic-fano-lean/upstream-maintenance) retain the actual checks. The separate full sixteen-case notebook replay timed out; no passing full-family replay is claimed.

Upstream pins Lean 4.33.0 and mathlib `db584cd6d46c92f209a44c0f1c829460d327499d`. That environment has not been run locally. This is a draft maintenance proposal for API review and target-toolchain validation; it does not claim upstream compatibility or acceptance. Maintenance authorization of the exact head remains with the repository owner under `CONTRIBUTING.md` and `MAINTAINING.md`.

To check with the upstream pinned environment:

```sh
cd formal/lean
lake exe cache get
lake build HodgeTestbed.RowCertificate HodgeTestbed.RowCertificateExample
lake env leanchecker HodgeTestbed.RowCertificate
lake env leanchecker HodgeTestbed.RowCertificateExample
```

Use separate checker invocations: the available Lean checker starts parallel tasks when given multiple module names. Hodge Lab's large initial batch exhausted memory that way; its revised replay checks one module per process.

## Contribution

Coefficient searches produce left-null vectors that cancel every correction column while leaving a nonzero target pairing. This maintenance PR adds a finite-row obstruction lemma that turns such a certificate into a no-solution theorem, together with a small checked example.

- `RowCertificate.lean` proves the implication over a commutative ring and supplies an integer-certificate wrapper over any characteristic-zero field.
- `RowCertificateExample.lean` encodes a two-row, 175-column subsystem from a fixed cyclic-triple-fano experiment. Its only nonzero column is 119, with entries `1` and `-756`; the target entries are `0` and `-5`. The functional `(756, 1)` annihilates every column and evaluates to `-5` on the target.

The proof distributes a weighted sum of equations and interchanges two finite sums. The wrapper transports integer equalities through the cast and uses characteristic zero to preserve the nonzero target pairing. This is a reusable interface for standard linear algebra, using mathlib's finite-sum identities.

## Verification

The exact proposed files at head `84b1c1584b7615ec7189e896df2734a0833e84e1` pass a fresh Linux check with upstream's pinned **Lean 4.33.0** and mathlib `db584cd6d46c92f209a44c0f1c829460d327499d`. The isolated project copies upstream's toolchain, Lake configuration and dependency manifest; all nine dependency commits match their pins.

- Both modules compile and pass separate official `leanchecker` invocations.
- All five expected theorem axiom reports use only the permitted standard axioms.
- Both deliberately altered certificates are rejected because their arithmetic propositions are false.
- Source bindings and all eighteen command logs were checked against the downloaded receipt and the proposed commit.

[Successful compatibility run](https://github.com/rbajaj5/hodge-lab/actions/runs/39084143971) · [immutable receipt, metadata and logs](https://github.com/rbajaj5/hodge-lab/tree/197dafba1322efbf50621dfa2358a55cb14552d1/formal/results/upstream433-ci/39084143971) · [isolated checker and reproduction instructions](https://github.com/rbajaj5/hodge-lab/tree/197dafba1322efbf50621dfa2358a55cb14552d1/formal/compatibility/upstream433).

The separate sixteen-case notebook project also completed its Lean 4.31.0 audit: seventeen module replays, fifty axiom reports, and two rejected altered certificates. [Successful run](https://github.com/rbajaj5/hodge-lab/actions/runs/39082400121) · [immutable archive](https://github.com/rbajaj5/hodge-lab/tree/197dafba1322efbf50621dfa2358a55cb14552d1/formal/results/concrete-ci/39082400121). That verifies the same sixteen fixed encoded systems already checked in exact arithmetic; it is not a proof about an unrestricted parameter family. Earlier interrupted attempts remain in the notebook history.

These checker runs trust the standard imported environment; they do not replay all of mathlib from scratch or use an independent kernel. Recorded build/replay artifact hashes agree, but compiled binaries were not uploaded for an independent byte audit. The compatibility check covers these two proposed modules, not a build of the entire upstream repository or its protected acceptance workflow.

To reproduce the module checks in the upstream pinned environment:

```sh
cd formal/lean
lake exe cache get
lake build HodgeTestbed.RowCertificate HodgeTestbed.RowCertificateExample
lake env leanchecker HodgeTestbed.RowCertificate
lake env leanchecker HodgeTestbed.RowCertificateExample
```

## Scope and attribution

Only two new files under `formal/lean/HodgeTestbed/` are proposed; existing files are unchanged. The example's polynomial-to-matrix correspondence and correction-space completeness remain separately checked in Python, outside the Lean theorem. This establishes neither `HodgeComputer.HasCertificate`, a full instance exclusion, exact numeric matrix ranks, nor solve credit. This remains a draft maintenance proposal for maintainer review; owner authorization and protected acceptance have not been obtained.

Developed with OpenAI Codex assistance on behalf of `rbajaj5`, building on the repository authors' certificate framework and standard finite-sum algebra in mathlib. The [immutable notebook](https://github.com/rbajaj5/hodge-lab/blob/197dafba1322efbf50621dfa2358a55cb14552d1/notes/cyclic-fano-concrete-lean.md) records the derivation, provenance, failed attempts, checks and visualization.

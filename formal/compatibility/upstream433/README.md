# Exact upstream compatibility check

This isolated project tests the two files proposed in
[sextics PR 121](https://github.com/hodge-computer/sextics/pull/121), at head
`84b1c1584b7615ec7189e896df2734a0833e84e1`. The two Lean sources, `lakefile.toml`,
`lake-manifest.json`, and `lean-toolchain` are exact LF-normalized copies from
that proposal. [bindings.json](bindings.json) records their hashes and upstream
URLs. The source copies also match the earlier notebook proposal archive.

The required toolchain is final **Lean 4.33.0**, with mathlib commit
`db584cd6d46c92f209a44c0f1c829460d327499d`. Lean 4.31 results and 4.33 release
candidates do not satisfy this check. No 4.33 success is asserted until the
new workflow produces a `PASS` receipt.

From a fresh checkout with Elan available:

```sh
cd formal/compatibility/upstream433
python3 -S check.py --check-inputs-only
python3 -S check.py --fetch-cache
```

The runner checks all nine dependency commits and requires fresh builds of
`HodgeTestbed.RowCertificate` and `HodgeTestbed.RowCertificateExample`. It audits
five declarations, accepts only the standard `propext`, `Classical.choice`,
and `Quot.sound` dependencies, and sequentially replays both modules using the
official `leanchecker`. Default replay trusts imported dependencies; this is
not a recursive `--fresh` replay of mathlib. Built module bytes are hashed and
must remain identical through replay. Each of two altered certificates must
fail specifically because `decide` establishes that its proposition is false.

The [own-repository workflow](../../../.github/workflows/lean-upstream.yml)
uses a fresh Ubuntu runner and uploads `results/validation.json` and command
logs as `upstream-lean433-compatibility`, including failure records. Individual
commands have explicit bounds; the whole CI job has a 20-minute limit.
Target builds are never reused, and the existing Lean 4.31 project and receipts
are not changed. To repeat a full run, use another fresh checkout.

This validates only these two maintenance modules. The generic row-functional
lemma and concrete two-row inconsistency apply over characteristic-zero
fields. Identifying the encoded rows with polynomial coefficients remains an
external exact Python check. Neither the rest of upstream nor a
`HodgeComputer.HasCertificate` statement is validated here.

Prepared with OpenAI Codex assistance. The proposed theorem sources retain
their original attribution and scope comments.

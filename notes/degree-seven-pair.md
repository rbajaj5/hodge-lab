# Closing the {chi_Y0, chi_X1} degree-seven family

For the fixed `holdout`, the complete degree-seven denominator family with characters **chi_Y0 and chi_X1**, modulo `F S_1`, is excluded. This closes family **22** in [fqlx's published list of 35 mixed residuals](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18982957). That update excluded 32 of the 35 and left families 13, 22, and 30 unresolved.

At the time this result was posted, combining it with the reproduced upstream calculation gave **9,451 excluded pairs out of 9,453**. The two remaining pairs have since been excluded by our `{chi_X0, chi_Y0}` proof and fqlx's `{chi_X1, chi_Y1}` proof; see the [subsequent update and attribution](x0-y0-exclusion.md). Denominators involving three or more full-group characters, and higher degrees, are not excluded. No certificate of existence or Lean `HasCertificate` theorem has been found.

## Exact system and completeness

The target is unchanged: `q=1`, `A=X0^3 Y0^3`, and the eight-term `F` pinned at upstream `b8c4edeb80a82395ec07164caf445cfa43bbbd56`. The normalized equations are

```text
N(F) = A D,
D div(N) - N(D) = F C.
```

Here `deg D=7`, `deg N_i=8`, and `C` is an unrestricted degree-eight polynomial. The same Euler normalization and `F S_1` gauge argument as in the [single-character calculation](degree-seven.md) apply.

Use the order-216 diagonal group and coordinate weights recorded there. The two characters are `chi_X1=(0,1,0)` and `chi_Y0=(1,2,3)`. Their difference has order six. Its kernel `H` has order 36; both denominator characters restrict to the same character on `H`.

With `D` fixed in this family, project only the numerator to the required `H` character. All full-group Koszul characters in that coset are retained. The resulting system has **14 denominator coordinates, 60 shared Koszul correction coordinates, and 344 physical coefficient equations** after exact division by `F`. This is the full E2 system for this denominator family, including equations that contain only numerator-correction terms. There is no separate correction coefficient for each product, and no zero-quotient restriction.

The 14 denominator basis indices in this repository's pinned E1 file are

```text
123,139,180,210,229,232,262,115,133,168,234,271,285,288.
```

Call their coefficients `a0,...,a13`. The first seven have character `chi_X1`; the last seven have character `chi_Y0`. These are local indices, not fqlx's raw parameter labels. The E1 basis hash is included in the certificate packet.

## The additional relation

Complete affine chart checks first force `a1=a6=a9=0`. On this space define

```text
L = 3 a7 - 6 a8 + a10 + a12 + a13.
```

Let `E_r` denote the coefficient equation at zero-based row `r` in the packet's ordered physical monomial list, after these three substitutions. Direct exact summation gives

```text
L^2 = -18 E_88 - 18 E_89 - 18 E_106 + 9 E_163 + 108 E_173 - 54 E_209.
```

Thus `L=0` over the complex numbers. This uses the field implication `L^2=0 => L=0`; it makes no positivity or real-coefficient assumption. The discovery step factored necessary quadrics to suggest `L`. The saved identity against the actual shared-coefficient equations is the verification.

Solve this linear relation for `a7`. A complete affine chart check with `a11=1` is inconsistent, forcing `a11=0`. Four further checks, individually normalizing `a8`, `a10`, `a12`, or `a13` to one, force all four to vanish. Hence `a7=0` as well: the entire `chi_Y0` component is zero.

The five remaining free denominator coordinates are `a0,a2,a3,a4,a5`, all in the `chi_X1` family. The separately verified single-character theorem excludes every nonzero denominator in that family. The zero class modulo `F S_1` is inadmissible. This covers the complete two-character family, not only finitely many chosen denominators.

## Checks, artifacts, and limits

The checker rebuilds the full system and verifies **196 exact inferences**, including the six-term square identity. A second polynomial implementation reconstructs **945 columns and 18,253 nonzero coefficients**, uses the opposite physical-monomial division order, and selects the numerator fields through a direct subgroup test. Changing a coefficient in the square witness causes verification to fail. The single-character certificate packet is also replayed as an explicit dependency.

```sh
python algebra/degree7_e1.py --check
python algebra/degree7_y0_x1.py --check
```

To regenerate the new packet from the stored, separately reconstructible E1 basis:

```sh
python algebra/degree7_y0_x1.py
```

All these exact calculations use Python's standard library. See the [source](../algebra/degree7_y0_x1.py), [proof packet](../results/degree7-y0-x1/certificate.json.gz), [result](../results/degree7-y0-x1/report.json), and [validation log](../results/degree7-y0-x1/validation.txt).

The upstream degree-seven package was fetched at revision `ffff4273a7a04905bb7de50382d731b91e08b328`, with 26 source hashes checked. Its single-character, global, pair, actual-pair, subgroup, and tangent-factor checks were run. The last phase initially encountered a Windows log-encoding error; rerunning it with `PYTHONUTF8=1` passed. See the [pinned manifest](../references/fqlx-degree7.json) and [replay record](../results/upstream-degree7/replay.json).

The saved replay record audits the outputs of those completed runs. A fresh execution of the entire upstream package is available with `python experiments/reproduce_degree7_progress.py --fetch`; this wrapper enables UTF-8 for its subprocesses. Its `--audit-existing` option checks existing records only and is not a substitute for executing the mathematics.

Credit: fqlx supplied the prior exclusions, complete E1 dimensions, symmetry strategy, and identification of the three residual pairs. The repository authors' Euler normalization and full Koszul correction formulation supply the framework; their exposition credits Benjamin E. Diamond's certificate bridge. This continuation and its code were developed with OpenAI Codex assistance for `rbajaj5`. Separate code paths and CI are computational checks, not external mathematical review or a Lean existence proof.

# One-reflection-skew: protected polynomial to chart in Lean

21 October 2026. This bounded unit closes the polynomial-substitution step
left by checkpoint 122. It binds the protected sextic and scalar source to
the actual `p7` and `a` definitions used by the existing Lean obstruction.
The differential transport remains a separate proof obligation.

![Protected monomial substitution and formal proof boundary](../visualizations/skew-chart.png)

The table is generated from the pinned protected terms. Colors group the
powers of U; the dashed arrows mark the still-unformalized differential
transport, not established implications. [Generator](../scripts/visualize_skew_chart.py)
and [machine-readable figure data](../formal/results/skew-chart/visualization-data.json).

## Pins and the exact map

Notebook parent: `c0b4347ad4d2dbad112813e57b9e7554dc0cad9b`.
Current upstream head at retrieval:
[`84f106ebf0731cbee1926833236361cddac0fc3f`](https://github.com/hodge-computer/sextics/tree/84f106ebf0731cbee1926833236361cddac0fc3f).
The [protected record](https://github.com/hodge-computer/sextics/blob/84f106ebf0731cbee1926833236361cddac0fc3f/data/one-reflection-skew/record.json)
and [REC equation](https://github.com/hodge-computer/sextics/blob/84f106ebf0731cbee1926833236361cddac0fc3f/data/one-reflection-skew/instance.rec)
were fetched again and are byte-identical to the saved inputs.
[Input hashes and fetch commands](../formal/results/skew-chart/inputs.json).
The target is still marked open in this pinned record.

Coefficients are rational, the protected order is `(X0,X1,X2,Y0,Y1,Y2)`,
and the pole parameter is `q=1`. On the Y0=1 substitution set

\[
 (X_0,X_1,X_2,Y_0,Y_1,Y_2)=(x,rx,wx,1,t,z),\qquad U=x^2.
\]

With

\[
 a=1+r^6+w^6,\quad b=rt(1+r^2w),\quad
 c=\frac{rt(1-t^2)}7,\quad d=1+t^6,\qquad
 P(U)=aU^3+bU^2+cU+d,
\]

the new Lean module proves

\[
 F(x,rx,wx,1,t,z)=z^6+P(x^2),\qquad
 A(x,rx,wx,1,t,z)=x^3.
\]

It also proves the binding to the **existing**, unchanged sparse polynomial:

\[
 \operatorname{eval}(p7)(U,r,w,t,0)=7P(U),\qquad
 7F(x,rx,wx,1,t,z)=7z^6+\operatorname{eval}(p7)(x^2,r,w,t,0).
\]

The fifth polynomial coordinate is the unused coordinate of the earlier
operator, set to zero here. `p7Over` and `aOver` are the earlier coefficient
extensions to a field K; the corresponding evaluation identities are proved
as well. The factor seven is retained explicitly.

The sextic/p7 statements use `[Field K] [CharZero K]`. The scalar-source
identity needs only `[Field K]`. None needs a nonzero value of x, z, a or P.
These are forward polynomial identities. To recover r=X1/X0 and w=X2/X0
on Y0=1 requires X0 nonzero; no inverse-chart theorem is included. Passing
from x to U=x² is not asserted to be a rational isomorphism or to cover every
K-point. No global chart coverage or nonvanishing theorem is inferred.

## What was actually checked

The [new Lean source](../formal/HodgeLab/OneReflectionSkew/ChartSubstitution.lean)
has eight audited theorems: `eval_a`, `eval_aOver`, `eval_p7`,
`protected_substitution`, `protected_source_substitution`,
`protected_substitution_p7`, `eval_p7Over`, and `protected_substitution_p7Over`.
The [receipt](../formal/results/skew-chart/validation.json) records compilation,
the exact allowed-axiom reports and default kernel replay of this new module.
Its imported modules, earlier coefficient proof and mathlib are reused,
not freshly kernel-replayed. Source and artifact hashes are recorded.

The [external source-binding check](../formal/results/skew-chart/source-binding.json)
independently parses the REC expressions with exact rational arithmetic,
compares both JSON representations and the literal existing Lean definitions,
and substitutes all ten sextic terms and the source term. Removing z⁶ and
replacing even powers x² with U reproduces **all nine actual p7 terms**.
This binds repository files to the formal definitions; Lean itself does not
parse Git, JSON or REC. The code rejects duplicate terms, unparsed syntax
and a changed pin. Inputs and inherited proof hashes are checked both before
and after execution to detect concurrent changes.

Three meaningful error controls are rejected by Lean after proving the true
point evaluation:

| Deliberate error | Point `(x,r,w,t,z)` | Correct value | Wrong value |
| --- | --- | --- | --- |
| Substitute U=x in place of U=x² | `(2,0,0,0,0)` | F=65 | 9 |
| Reverse the sign of the linear-in-U coefficient c | `(1,1,0,2,0)` | F=477/7 | 489/7 |
| Replace source x³ by x² | `(2,0,0,0,0)` | A=8 | 4 |

An error exit, timeout or elaboration failure alone does not pass a control:
the verifier requires exactly one explicit false-proposition diagnostic and
rejects unrelated errors. Two control implementations failed to reduce the
point evaluation; the complete verifier returned FAIL both times. The second
attempt exposed that a later false-equality message could coexist with an
earlier failed proof. The final harness separately compiles all three true
evaluations successfully, then uses `decide +kernel` on each false equality.
The sign control is multiplied by seven, comparing 477 with 489. Five bounded
Lean development attempts and both verifier failures are preserved in the
[development archive](../formal/results/skew-chart/development/README.md).
They are implementation issues, not mathematical nonexistence results.

From `formal`, with pinned dependencies already installed:

```sh
python3 -O check_skew_chart.py
```

From the repository root:

```sh
python3 scripts/visualize_skew_chart.py
```

Toolchain: Lean 4.31.0; mathlib
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`. The runner needs only Python's
standard library; the visualization uses Matplotlib. Each verification process
is capped at 120 seconds, the run at 600 seconds. Development compiles were
capped at 90 seconds. No resource-limit failure is credited as a result.
The receipt records actual commands, versions, elapsed times and outputs.
CI is wired to run this check; this note reports executed local checks,
not an unobserved future CI outcome.

## What this does not close

The protected **scalar source** is x³ here. It does not turn into the U²
source of the reduced differential merely by renaming variables. The volume
Jacobian, dU=2x dx, residue reduction, normalizations and the permitted
derivative/correction space still need their formal transport proof. The
[earlier exact derivation](chi-target-source.md) is separate evidence, not a
Lean theorem created by this batch.

The [existing arbitrary degree-four obstruction](skew-lean-extension.md)
remains the same bounded statement for D=a. No new denominator/degree family,
45-versus-504 image comparison, rational primitive, `HasCertificate`, trace,
denominator clearing or accepted solve is established. The smallest next
formal unit is the affine coordinate-volume/Jacobian identity, with its
orientation and open-chart assumptions stated before any residue formula.
This batch stops before that unit.

Credit: Benjamin E. Diamond and the upstream contributors for the protected
target and framework; fqlx for the physical quotient/source-reduction and
companion formulation cited by the earlier notebook. This adds formal
verification of the notebook substitution, with no novelty or solve claim.
An independent read-only reviewer checked the statements and verifier and
recommended the final concurrent-input hash checks. Hodge Lab only; no
upstream post or edit. Tally unchanged: **29 discussion contributions, one
closed maintenance PR, zero accepted authored solves**.


## Follow-up — checkpoint 125

The subsequent [coordinate-volume proof](skew-volume-lean.md) closes the
ordered Jacobian and ambient source-coefficient step: x², 2x, −x² and
−U²/(2G²), with chart assumptions explicit. The earlier description above
is retained as the boundary of checkpoint 124. Residue reduction, trace,
global descent and the rational primitive remain outside the new proof.

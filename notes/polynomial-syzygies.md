# Polynomial syzygies of the shared correction map

**Later continuation:** rebuilding family 115 closes that family and raises
coverage to 134/136. This note preserves the earlier checkpoint;
see [the new proof, visualization, and failures](syzygy-rebuild.md).

Published in [holdout Discussion 44](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18985544),
with [full CI passing on the immutable proof commit](https://github.com/rbajaj5/hodge-lab/actions/runs/38983831725).

**One further complete degree-seven family is excluded:**
`{(0,0,1), (1,2,3), (3,0,1)}`, family **87** in our preceding triple packet.
The fixed-pair coverage is now **133 of 136** `X0/Y0` extensions. Three remain:
third characters `(0,1,0)`, `(4,2,3)`, and `(5,3,0)`.
In the preceding 152-family selection, the count becomes **133 excluded and
19 unresolved**. This does not exclude all 428,536 triples or arbitrary
degree-seven denominators. The unconditional degree bound remains at least
seven. There is no existence certificate, Lean proof, solve PR, or leaderboard
point from this calculation.

The two smaller residual families were selected before running this search:
87 and 115 each retain 58 correction directions, compared with 256 for the
other two. We tested the one remaining third-component chart of 87 and both
of 115. [Machine-readable report](../results/degree7-syzygies/report.json).

## The new step

Keep the protected holdout `(F,q,A)` fixed at upstream
`b8c4edeb80a82395ec07164caf445cfa43bbbd56`, with `q=1` and `A=X0^3 Y0^3`.
Use the complete E1 space and the same stabilizer projection as the
[preceding packet](three-character-families.md). The quotient by `F` remains
unrestricted. Write the physical coefficient equations as

```text
E(a,z) = R(a) z + b(a) = 0.
```

Here `a` consists of denominator coordinates and `z` of the shared numerator
corrections. The entries of `R` are linear in `a`; `b` is quadratic. On a
chart normalizing one denominator coordinate to one these degrees are bounds.
Search for polynomial row vectors `u(a)` with

```text
u(a)^T R(a) = 0,
P(a) = u(a)^T b(a) = sum_j u_j(a) E_j(a,z).
```

Then `P(a)=0` is necessary. The search permits affine-linear `u_j`, by taking
all original rows and their products with each remaining denominator coordinate,
then eliminating monomials containing any numerator coordinate. Coefficients
of `z` stay shared throughout; the products `a_i z_k` are not made independent.
Every retained relation carries explicit rational multipliers of the physical
equations, checked by direct polynomial multiplication.

For comparison, first permit only constant multipliers. Multiply those output
relations by all affine-linear denominator monomials. The new output contains
the following additional independent directions modulo that vector space:

| Family / chart pivot | Physical equations | Constant-multiplier relations | Rank of their affine multiples | Rank after polynomial cancellation | Additional directions |
|---|---:|---:|---:|---:|---:|
| 87 / 2 | 244 | 17 | 213 | 245 | 32 |
| 115 / 0 | 255 | 17 | 233 | 264 | 31 |
| 115 / 10 | 255 | 17 | 233 | 264 | 31 |

The 94 additional directions are a **bounded vector-space comparison**.
They are not claimed independent modulo the entire old polynomial ideal or
its radical. The checker establishes each identity and the displayed relation
ranks; it does not prove that the packet generates the full syzygy module.

Necessary relations can miss exceptional rank-drop loci. For example,
`xz+1=yz+1=0` implies `x-y=0`, but `x=y=0` satisfies that consequence while
admitting no `z`. A unit test records this limit. Surviving the syzygy test is
never treated as an existence certificate.

## A short obstruction for family 87

This family originally has 15 denominator directions. The preceding exact
first pass removes raw basis index 46. Its remaining 14 directions, in order,
are

```text
[42,56,75,88,102,111,114,115,133,168,234,271,285,288].
```

These are Hodge Lab zero-based basis indices, not fqlx's raw indexing. Write
their coefficients as `a0,...,a13`. Only `a2` belongs to the third character
`(3,0,1)` after the earlier reduction. If it is zero, the already checked
`X0/Y0` pair exclusion applies. Otherwise simultaneously scale `D,N` to set
`a2=1`. Its order-36 stabilizer retains all 58 allowed Koszul corrections.

Among the 17 baseline and 32 selected new necessary relations, exact affine
and square identities imply

```text
a0 = -6 a1 + a3/6 - a4/2 - a5/3 + a6/6,
a7 = -a11-a12,
a8 = a10/6-a11/2-a12/3+a13/6,
a9 = 0.
```

After these substitutions, three supplied identities give

```text
a1^3 = 0,   a11^3 = 0,   a12^3 = 0.
```

There are only **19 polynomial-multiplier terms** in these three identities
against the selected necessary equations. Thus `a1=a11=a12=0` over C.
After these substitutions the original physical rows, numbered from zero,
satisfy the exact identity

```text
3 (E134 + E135 + E164) = 1.
```

This contradicts the full E2 system. Both the syzygy-to-physical maps and the
power identities are checked, as is the final three-row identity. No assumption
of real coefficients, positivity, zero quotient, a linear denominator factor,
or a relation between the three character components is used.

Although the complete search output is retained, this proof uses only eight
of the selected necessary relations: five baseline relations (indices
`1,9,12,15,16`) and three polynomial-syzygy relations (`31,44,48`), numbered
in the concatenated baseline-plus-selected list. The short proof is therefore
much smaller than the full exploratory packet.

## What did not close

Family 115 has third character `(4,2,3)`. The two charts prove additional
cubic vanishings of local coordinates `a9` and `a2`, but neither chart closes.
After the bounded necessary-condition continuation, neither full physical test
produces a contradiction. Exhausting the chosen degree-three and degree-four
coordinate-power tests supplies no higher-degree nonexistence claim.
The two 256-correction families were not continued in this batch.

Discovery failures are retained in
[the experiment log](../results/degree7-syzygies/experiments.json) and
[Singular inputs and outputs](../results/degree7-syzygies/singular-exploration.zip):

- Unrestricted polynomial-module `syz` on all three charts exceeded 45 seconds
  per call and exported no identities.
- On family 87 the selected necessary ideal has a CAS Gröbner basis containing
  all seven `Y0` coordinates. Direct multiplier exports exceeded 60 seconds
  before affine reduction and 90 seconds after it. These failed exports are
  not used as proof. The successful argument above needs only three cubes and
  the original physical equations; it does not require proving all seven
  coordinates vanish.
- Searching directly for the seven linear coordinate memberships through
  total degree five found only two at that bound, one already known zero.
  Asking for powers instead found the useful three cubes immediately. This
  distinguishes a failed proof-search choice from a false mathematical claim.
- The family-115 Gröbner calculations exceeded their 30-second limits. Their
  exported polynomial syzygies and cubic identities, rather than the timed-out
  calculations, are the checked partial results.

## How the papers guided the experiment

The user supplied David Yang's
[*S_n-Equivariant Sheaves and Koszul Cohomology*](https://arxiv.org/pdf/1407.4183v1).
It motivated looking for relations among relations while preserving symmetry.
Yang's line-bundle Koszul cohomology is not identified here with the holdout's
Jacobian/Koszul correction module. Its asymptotic theorem is not invoked.
The implemented method is ordinary polynomial syzygy elimination, discovered
and checked by finite exact linear algebra.

The two later supplied PDFs were identified and their introductions and relevant
statements examined:

- Pavel Etingof, [*Koszul duality and the PBW theorem in symmetric tensor
  categories in positive characteristic*](https://doi.org/10.1016/j.aim.2017.06.014),
  especially Theorem 3.4. Its deformation principle controls flatness from low
  degrees **under a Koszul special-fiber hypothesis**. We have not established
  such a deformation or Koszul algebra for holdout. Having quadratic equations
  does not license stopping all checks at degree three. The positive-characteristic
  tensor-category phenomena are also distinct from our rational identities.
- Jack Kelly, [*Exact Categories, Koszul Duality, and Derived Analytic Algebra*](https://ora.ox.ac.uk/objects/uuid%3A27064241-0ad3-49c3-9d7d-870d51fe110b),
  Oxford DPhil thesis (2018), especially the introduction and sections 4.2–4.3.
  Its homotopical and operadic framework suggests organizing relations and their
  higher compatibilities. No controlling Lie algebra, bar-cobar equivalence,
  or analytic deformation model for this certificate search has been constructed.

These are research motivations, not transferred theorems. No supplied PDF or
private conversation has been copied into this public repository. A possible
next experiment is to recompute polynomial syzygies after the new family-115
vanishings, rather than only multiplying the old relations. That has not yet
been executed in this batch.

## Reproduce and audit

In a recursive checkout:

```sh
python -S algebra/degree7_e1.py --check
python -S algebra/degree7_x0_y0.py --check
python -S algebra/degree7_syzygies.py --check
python -S algebra/degree7_syzygies.py --check --independent
python -m unittest discover -s tests -v
```

The two new replays check 824 cancellation identities (including the 51 baseline
identities), 75,312 equation-multiplier terms, seven power identities with 42
terms, and 21 chart inferences. Both damaged syzygies and damaged power
identities are rejected. All 31 unit tests pass. The independent mode uses the
second polynomial API, the actual `instance.rec`, and opposite monic-division
ordering. It shares the small identity replayer, so this is not fully independent
verification, independent human review, or Lean acceptance.

The earlier first-pass reductions for families 87 and 115 are replayed by the
new checks. The `X0/Y0` pair theorem needed when the third component vanishes
remains an explicit prior dependency checked by the command above and CI.

Discovery can be regenerated, overwriting the corresponding packet:

```sh
python -S algebra/degree7_syzygies.py --family 87 --pivot 2
python -S algebra/degree7_syzygies.py --family 115 --pivot 0
python -S algebra/degree7_syzygies.py --family 115 --pivot 10
```

Each searches affine multiplier degree at most one and power consequences
through total degree four. Add `--continue` to reuse archived cancellation
identities and rerun only the power/physical continuation. The full module
searches in the failure archive are exploratory and unnecessary for replay.

Credit belongs to the repository authors for the certificate and normalization
framework; to the bridge attributed there to Benjamin E. Diamond and Griffiths's
residue theory; to fqlx for prior E1/Koszul, symmetry, and pair calculations;
and to our preceding pair and triple packets for their explicit reductions.
Yang, Etingof, and Kelly supplied the literature motivation described above.
Prepared with OpenAI Codex assistance on behalf of `rbajaj5`. No separate
review agent was available in this batch; the second implementation is a
computational check, not an additional human or agent endorsement.

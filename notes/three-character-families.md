# A systematic three-character slice of holdout

Published as a [partial result in holdout Discussion 44](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18984710), with [passing CI for the immutable proof commit](https://github.com/rbajaj5/hodge-lab/actions/runs/38981740498).

**132 complete degree-seven three-character families are excluded.** We tested
all 136 extensions of the pair `chi_X0=(0,0,1), chi_Y0=(1,2,3)` by one other
nonempty E1 character. Four extensions remain unresolved. We also tested all
20 triples drawn from the six coordinate characters. Four overlap the first
set, so the combined selection has **152 distinct families: 132 excluded and
20 unresolved**. These are families with arbitrary complex coefficients,
not a finite list of sampled denominators.

This is a bounded part of the **428,536** unordered triples among the 138
retained characters. It does not settle arbitrary three-character denominators,
general degree-seven denominators, higher degrees, or holdout. The unconditional
degree bound stays at least seven. No Lean `HasCertificate` proof, solve PR,
or leaderboard point is claimed.

![Exact coverage of all X0/Y0 extensions](../results/degree7-triples/character-atlas.png)

## Target, basis, and selection

The protected target is unchanged at upstream
`b8c4edeb80a82395ec07164caf445cfa43bbbd56`:

```text
F = X0^6 + X1^6 + X2^6 + Y0^6 + Y1^6 + Y2^6
    + X0^3 X1 Y0 Y1 + X1^3 X2 Y1 Y2,
A = X0^3 Y0^3, q = 1.
```

The complete E1 calculation supplies 295 denominator/lift pairs and the full
840-dimensional numerator kernel. Removing the six `F*S_1` gauge directions
leaves 289 denominator coordinates in 138 character spaces. The degree-seven
basis and gauge identities are reconstructed by the existing checks; this is
prior work, not a new dimension calculation. See [the basis and character
convention](degree-seven.md).

For each selected triple we use **every retained basis vector** in its three
character spaces. Initial family dimensions range from 14 to 21. Family numbers
in this packet are one-based positions in the lexicographically sorted list of
152 triples; they are **not** the earlier pair-family numbers. The indices of
denominator basis vectors are the zero-based Hodge Lab indices, not fqlx's raw
basis labels. [Machine-readable coverage](../results/degree7-triples/coverage.json)
lists the characters and status of each family.

Every exclusion in this batch ends by reducing to the complete `X0/Y0` pair.
The [previous exact pair exclusion](x0-y0-exclusion.md), including its
single-character closure, is therefore an explicit dependency. We do not
infer a three-character exclusion merely from its pairwise subfamilies being
excluded.

## First pass: exact obstruction functionals

Write the normalized equations as

```text
N(F) = A D,
B(D,N) = D div(N) - N(D) = F C.
```

For the complete family, let `D=sum_i a_i D_i`,
`N=sum_i a_i N_i + sum_k z_k K_k`. The 840 `K_k` span all E1 corrections.
Monic division by `F` eliminates the unrestricted degree-eight quotient `C`.
The remaining equation has the form

```text
sum_{i<=j} a_i a_j Q_ij + sum_{i,k} a_i z_k R_ik = 0,
Q_ii = B(D_i,N_i) mod F,
Q_ij = (B(D_i,N_j)+B(D_j,N_i)) mod F   (i<j),
R_ik = B(D_i,K_k) mod F.
```

We first enlarge the correction space by allowing each product `a_i z_k` to
vary independently. A rational linear functional `ell` annihilating every
`R_ik` gives a necessary equation

```text
P_ell(a) = sum_{i<=j} ell(Q_ij) a_i a_j = 0.
```

Characters split this computation into small blocks without losing any
correction. All 840 fields are considered; fields in other characters pair
to zero automatically. The packet stores the physical coefficient functional
`ell`, not just a numerical rank or a statement that elimination succeeded.
The checker verifies its annihilation of the correction columns and reconstructs
every coefficient of `P_ell`.

Rational combinations of these necessary equations give `a_i^2=0`; hence
`a_i=0` over the complex numbers. We remove such coordinates and repeat. The
generic search also permits cubic powers when at most 12 coordinates remain,
and fourth powers when at most eight remain. **All 265 vanishing identities
actually used in this run are squares.** There is no real-positivity argument.

This pass reduces **112 of the 152 families** to the previously excluded
`X0/Y0` pair. Forty families retain three characters. Survival is inconclusive:
the relaxed correction coefficients need not factor as the actual shared
products `a_i z_k`.

## Second pass: restore the shared numerator

For each of the **24 surviving X0/Y0 extensions**, we reconstruct the full
shared-coefficient equations. If the characters are `w,z,t`, set

```text
H = ker(z-w) intersect ker(t-w) inside (Z/6)^3.
```

The denominator is an eigenvector for `H`. With this denominator fixed, project
only the numerator to character `chi_A+w` on `H`. This preserves both normalized
equations and retains every possible solution. The checker enumerates `H`,
computes its annihilator, verifies that it is generated by `z-w` and `t-w`,
and includes **all** Koszul fields in the required coset. Coefficients of each
included field are shared across every equation. The quotient remains
unrestricted.

If the third character component is nonzero, at least one of its coefficients
is nonzero. Simultaneously scaling `D` and `N` normalizes that coefficient to
one. Exact affine row consequences and square-zero consequences are applied
on each chart. Every substitution and contradiction is supplied as a rational
combination of the reconstructed physical equations. No independent scaling
of the three character components is assumed.

The initial pass closes **17** extensions. Three other families have some
excluded charts but an incomplete cover. Removing the coefficients already
proved zero and repeating the remaining charts closes all three. This leaves
**20** full shared-system closures, added to the 112 first-pass reductions.
The original unsuccessful charts are retained alongside the successful
refinements in families 3, 38, and 145.

The packet contains **70 chart attempts and 1,739 verified inferences**.
Forty-eight chart attempts end in contradiction; 22 historical attempts do
not. Nine of those unsuccessful attempts belong to families subsequently
closed by refinement. The four still unresolved extensions have 13 terminal
unresolved charts. No cubic ideal certificate was needed in this packet.

## What remains, and what failed

The four unresolved third characters are:

| Third character | Packet family | Original denominator dimension | Unresolved terminal charts |
|---|---:|---:|---:|
| `(0,1,0)` = `chi_X1` | 16 | 20 | 5 |
| `(3,0,1)` | 87 | 15 | 1 |
| `(4,2,3)` | 115 | 16 | 2 |
| `(5,3,0)` = `chi_Y1` | 137 | 20 | 5 |

The other **16 coordinate-character triples**, outside the fixed-pair selection,
survive the first necessary-condition pass and were not given the shared-chart
continuation in this batch. Together these make the 20 unresolved families in
the combined selection. The other 428,384 triples were not tested here.

Each initial shared-family run had a 60-second process limit; all 24 completed
without a timeout. The three refinement runs also completed. The chart routine
stops when its exact affine/square propagation finds no further consequence.
It is configured to try degree-three ideal combinations only when at most 16
variables remain. The final unresolved charts have 64–273 variables, so this
larger nonlinear search was not attempted for them. Failure of these bounded
tests is neither a solution nor a proof that an exact contradiction cannot be
found by another method.

An initial pilot also tried to read a checkpoint during its rewrite and failed
with an incomplete JSON/gzip read. It produced no mathematical result. Completed
packets were then used, and generation now writes to a temporary file and
replaces the checkpoint atomically.

The next useful algebraic targets are the four listed extensions, especially
the two smaller ones. Full denominator-coordinate chart covers, linear-form
square relations, or polynomial ideal certificates may improve on the current
third-component chart test. These are proposals, not completed results.

## Intuition, attribution, and verification

The preceding Hodge-projection experiment split a fixed denominator's residual
into a removable correction component and a surviving obstruction. Here we
replace numerical projection with **exact dual functionals**, and let all
denominator coefficients in each selected family vary. The shared-chart pass
then recovers constraints lost in the first relaxation. This is a concrete
continuation of the operator intuition; it is not a theorem derived from
Dubedat's imaginary geometry, an SLE construction, or GPU evidence.

The enlarged-correction strategy directly extends **fqlx's two-character scan**
in [the preceding degree-seven packet](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18982957).
Credit also belongs to the repository authors' Euler normalization and complete
Koszul framework, the prior E1/gauge and symmetry calculations, and the
certificate bridge and residue theory attributed in the exposition to Benjamin
E. Diamond and Griffiths. Our archived `X0/Y0` exclusion supplies the final
closure. The separately posted
[degree-12 conic-span obstruction](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18984539)
was read as context; it is not used or reproduced in this calculation.

Prepared with OpenAI Codex assistance on behalf of `rbajaj5`. A second polynomial
implementation reads the exact protected `instance.rec`, constructs derivatives
and Koszul fields separately, and divides by `F` in the opposite monomial order.
It reconstructs the same necessities and shared systems. **It shares the small
identity replayer with the producer**; this is a separate construction check,
not independent human review or a Lean formalization.

The first-pass replay checks **6,219 physical duals, 530,307 correction pairings,
166,729 quadratic pairings, and 265 square identities**. The independent version
constructs 20,426 distinct correction columns and 4,470 quadratic columns. Both
shared-system reconstructions replay all 70 charts and 1,739 inferences. Damaged
identities are rejected. Controls include a complex conic with genuine nonzero
solutions and a cubic consequence that does not appear as a quadratic square.

From a recursive Hodge Lab checkout:

```sh
python -S algebra/degree7_e1.py --check
python -S algebra/degree7_x0_y0.py --check
python -S algebra/degree7_triples.py --check
python -S algebra/check_degree7_triples.py
python -S algebra/degree7_triple_shared.py --check
python -S algebra/degree7_triple_shared.py --check --independent
python -m unittest discover -s tests -v
```

All new mathematical checks use Python's standard library and exact `Fraction`
arithmetic. Do not use `python -O`. No Lean theorem was attempted in this batch:
the delivered proof objects are the explicit rational identities and chart
maps. A later formalization would need to check both those identities and their
connection to the protected certificate statement.

Regenerate the discovery and figure with:

```sh
python -S algebra/degree7_triples.py
python -S algebra/degree7_triple_shared.py --timeout 60 --workers 2
python -S algebra/degree7_triple_shared.py --refine-family 3
python -S algebra/degree7_triple_shared.py --refine-family 38
python -S algebra/degree7_triple_shared.py --refine-family 145
python -S algebra/degree7_triple_shared.py --check > results/degree7-triples/shared-validation.json
python -S algebra/degree7_triple_shared.py --check --independent > results/degree7-triples/shared-independent-validation.json
python experiments/plot_triple_families.py
```

Artifacts: [coverage](../results/degree7-triples/coverage.json),
[first-pass proof packet](../results/degree7-triples/certificates.json.gz),
[shared chart packets and attempt logs](../results/degree7-triples/shared),
[first-pass validation](../results/degree7-triples/validation.json),
[independent first-pass validation](../results/degree7-triples/independent-validation.json),
[shared validation](../results/degree7-triples/shared-validation.json), and
[independent shared validation](../results/degree7-triples/shared-independent-validation.json).

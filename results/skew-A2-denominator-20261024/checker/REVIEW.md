# Separate AI checker: A squared denominator sum

24 October 2026 EDT. Executed 16:37:54–16:38:11 UTC by
`a2_denominator_checker`, a separate AI worker, not a human reviewer.

## Result

PASS for the declared necessary 1698-parameter family. I reconstructed all
2,986,842 entries of the author's 1758 × 1699 augmented matrix from the
literal, hash-pinned connection JSON. All 879 domain records agree.
Modular Bareiss elimination, distinct from the author's Gaussian rank
search, gives determinant **14098 modulo 32003** for the selected 1699-square
augmented minor. Its selected rows are the first 1699 rows as a set, with
four inversions, so the first 1699 rows in their original order give the
same determinant.

The coefficient matrix has 1698 columns; the nonzero augmented minor proves
coefficient rank 1698 and augmented rank 1699 over Q. This is a determinant
certificate, not an inference from a rank-defective modular system. No
assumption that hypothetical rational solution coefficients reduce modulo
32003 is needed: the nonzero modular determinant certifies a nonzero
rational determinant of the evaluated system.

## Independent implementation and controls

The author evaluates parsed rational polynomials and uses direct quotient
derivatives. This checker evaluates the exact JSON expression syntax using a
restricted integer AST and uses the independently supplied reduced top
operator

    T·∂ + (4 r^7 + 9 r) I + ell A M_a + t T_v M_b,
    ell = 3 r (r^6 - 1).

The remaining sectors are all 702 coefficients of P1 and all 702 coefficients
of P0. Their columns are respectively A(D_i − A_i/A) and A² D_i after the
full equation is multiplied by A². The top t-flux has D_t, because A_t = 0.
Monomial derivatives are implemented by lowering exponents. The source is
A² r^-4 M_b e0 / 12 with both compact rows and the positive packet sign.

Ten nonzero exact modular mutation witnesses detect: replacing the top
quotient factor 2 by 1; omitting either top r or v quotient term; reversing
the top quotient sign; omitting either P1 quotient derivative; dropping the
A_v M_a chain term; dropping source factor 1/12; reversing source sign; and
omitting a top t-flux derivative. They are witnesses at the saved ordinary
modular point [12817, 4220, 29800], not evidence for a positive rational
identity. The full negative certificate is the augmented minor.

The script checks the source SHA256, prime, declared basis, all sampled
denominator loci, all entries, minor row uniqueness, nonzero pivots, and
the int64 bound 2(p−1)^3 < 2^63. Gates use explicit exceptions and remain
active under Python -O. The fresh run completed with exit 0, empty stderr,
16.178 seconds mathematical time and 16.519 seconds total wall time, under
the 60-second subprocess bound. Python 3.12.14; NumPy 2.5.4. There were no
failed mathematical attempts or timeouts by this checker.

## Imported dependency and exact scope

I did **not** rerun the coordinator's structural algebra. The imported
highest-pole theorem says every solution in the original 2106-parameter
family (B + B/A + B/A²)^6 must have

    P2 = (T_r h2, T_v h2, k2),
    T_r = r²(r^6 + 1),
    T_v = r(2r^6 + 1)v − (3r^6 + 2),

with h2 supported in r = −10..−6, v = 0..1, t = 0..2, and k2 in B.
The pole coefficient is (R_a − 2I)(A_r P2_r + A_v P2_v), with
det(R_a − 2I) = 14/3. This yields 60 + 234 top-sector coefficients.
P1 is **not** constrained separately to be tangent: its double pole can
couple to the remaining top-sector pole. All 702 P1 parameters were retained.
The later proposed 1683-parameter refinement is unused.

The same necessary highest-pole theorem applies to homogeneous currents.
Consequently any kernel current in the original family belongs to the
tested 1698-parameter subfamily. Full coefficient rank then rules out an
unaccounted kernel there. This is the required kernel accounting for the
original-family exclusion; it does not follow merely from input-family
direct-sum independence.

The certificate therefore excludes the entire declared sum, conditional on
the imported structural theorem, including the requested B/A² subfamily.
It does not exclude arbitrary rational currents, other supports, higher
powers or other divisors. No primitive, exactness theorem, certificate, or
target solve is claimed. Old mathematical batches were not rerun.

## Reproduction

From the repository root, using a **new** checker run directory:

```sh
python3 results/skew-A2-denominator-20261024/checker/run_bounded.py \
  results/skew-A2-denominator-20261024/checker/check_A2_sum.py \
  new-check \
  results/skew-A2-denominator-20261024/lead/sum-01/result
```

The wrapper runs the checker with -O, enforces 60 seconds, snapshots the
source and wrapper, and saves stdout, stderr, exit, timing, versions and
hashes in a fresh directory. `sum-01` is immutable historical output.

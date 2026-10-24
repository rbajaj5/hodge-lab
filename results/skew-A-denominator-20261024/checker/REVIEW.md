# Separate AI checker: new A-denominator SUM family

Parent `aa5a30dff2fd70994c48c484845981c141e77ef9`.
Connection SHA256 `a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d`.
This worker did not write or run Lean, use network tools, alter old results,
commit, push, publish, or edit shared README/LEDGER/team-board files.

## Exactly what was executed

One fresh `python3 -O` child process, with an external 60-second bound,
reconstructed the new 1056-by-997 augmented matrix. It completed with exit0
in 3.777 seconds wall time. The script uses a restricted integer AST evaluator
for the pinned literal connection, exponent-lowered monomial derivatives, and
modular Bareiss for the minor. The author's code uses a SymPy polynomial
evaluator, direct quotient differentiation, and Gaussian elimination instead.
These are separate AI computations, not independent human review.

The matrix represents the necessary reduced family

```
F_r = L_r + T_r h/A
F_v = L_v + T_v h/A
F_t = L_t + P_t/A

T_r=r²(r⁶+1), T_v=r(2r⁶+1)v-(3r⁶+2)
h_j in span{r^m v^n t^k: m=-10..-6, n=0..1, k=0..2}
(P_t)_j and (L_i)_j in B=span{r^m v^n t^k: m=-10..2,n,k=0..2}.
```

There are 60 h parameters, 234 P_t parameters and 702 L parameters. The
equation is multiplied by the nonzero rational function A. The independent
operator used for h is

```
T_r partial_r + T_v partial_v + (7r^7+6r) I
    + 3r(r^6-1) A M_a + t T_v M_b.
```

The P_t block uses `partial_t+N_t`; the Laurent block uses
`A*(partial_i+Nphysical_i)`. The right side is `A*r^-4*M_b*e0/12`.
All six original flux components remain represented with the necessary
tangency relation. Both compact rows and all derivative directions are kept.
The code compares the reduced h operator to direct quotient-rule expressions
at every sample, including both `-A_r/A²` and `-A_v/A²`; A_t=0.

All 1,052,832 entries agree. All 528 point-domain bindings agree. Samples
avoid r=0,A=0,Delta=0; their v,t coordinates are also nonzero for evaluation
convenience. No claim of validity at excluded divisors is made. A_r is not
inverted by this physical-coordinate calculation.

The independently checked 997-square augmented minor has

```
det = 26947 modulo 32003.
```

The saved selected rows are exactly the first997 rows, reordered by an even
permutation (four inversions), so the first997 rows in their original order
have the same determinant. `minor-row-order.json` records this simplification.
The int64 intermediate bound is `2*(32003-1)^3 < 2^63`.

Seven nonzero controls detect omitted r-quotient derivative, omitted v-quotient
derivative, reversed quotient sign, omitted A_v connection chain, missing
source factor1/12, reversed source sign and omitted P_t derivative.

## What follows from this computation

The rational augmented sample matrix has rank at least997, since its minor
is nonzero modulo a prime at which every sampled coefficient denominator is
invertible. There are only996 coefficient columns. Therefore the reduced
family has no solution over Q, or after extension of the constant field.
This does not reduce unknown solution denominators modulo32003.

The nonzero full augmented minor also implies independence of all996
coefficient columns. Hence there is no operator kernel in the reduced family;
no rank-deficient modular-gap inference is being used.

## Imported structural evidence, not rerun by this checker

The coordinator supplied the necessary-condition theorem that every solution
in the original full 1404-parameter space `(B+B/A)^6` has exactly the reduced
form above. Its ingredients are the a=0 residue, invertibility of R_a-I,
the irreducible A-divisor and the narrow-v tangency/support argument. The
coordinator also supplied `B intersect B/A = 0` by v-degree. Those source-bound
structural checks are external handoffs here, not this worker's executions.

Combining that necessary theorem with the new reduced-family certificate
excludes the original `(B+B/A)^6` family. The same leading-pole necessary
condition applies to homogeneous currents, so reduced full column rank also
rules out operator kernels in the original family, conditional on that imported
necessity argument. This is the explicit kernel/rank gate for the broader claim.

There is no claim against arbitrary rational current supports or degrees,
and no primitive, source exactness, global clearing, certificate or solve.
All completed old Laurent, first-jet, Q/R2, beta, source/curve/trace and t-only
checks were reused as context only and were not rerun.

## Reproduction

From the repository root with NumPy installed and a fresh run name:

```sh
python3 -O results/skew-A-denominator-20261024/checker/run_bounded.py \
  results/skew-A-denominator-20261024/checker/check_A_sum.py REPLAY-NEW \
  results/skew-A-denominator-20261024/lead/sum-01/result
```

The runner records its source snapshot, command, versions, stdout/stderr,
exit, timing, input/output hashes and the 60-second timeout. No failed or
timed-out mathematical process occurred in this checker assignment.

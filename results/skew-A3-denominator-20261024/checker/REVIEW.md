# Independent A-cubed matrix and minor check

24 October 2026 EDT. Executor: `a3_denominator_checker`, a separate AI
worker, not an independent human reviewer. Mathematical work completed at
17:03:42 UTC / 13:03:42 EDT. No further mathematics was run after the pass.

## Result

PASS: independently reconstructed all **5,906,460** entries of the
**2460 × 2401** augmented matrix and all **1230** sample-domain records.
The new 2401-square augmented minor has determinant

\[
13752\pmod{32003}\ne0.
\]

The author-selected rows are exactly the first2401 rows as a set; their
order has four inversions. Thus the first2401 rows in original order also
have determinant13752. Both the row list and permutation count are retained.
The coefficient rank is2400, augmented rank2401. No deficient-rank gap is
promoted to a characteristic-zero exclusion.

## Independent mathematics versus file binding

Two processes were planned before execution so that neither approaches the
60-second limit by combining matrix reconstruction and elimination.

1. `reconstruct_A3.py` independently parses the pinned literal JSON using a
   restricted integer-AST evaluator. It computes the chart, all three
   physical connection matrices, the scaled source, the reduced top
   operator and exponent-lowered monomial derivatives. It reconstructs
   every matrix entry, then compares the resulting array to the author's
   CSV. This is mathematical reconstruction, not just hash checking.
2. `determinant_A3.py` verifies that the CSV, input record and author receipt
   are exactly those bound by phase1, then computes a modular Bareiss
   determinant. Those hash checks bind the phases; they are not counted as
   another reconstruction. Bareiss differs from the author's normalized
   Gaussian rank search. The integer bound 2(p-1)^3 < 2^63 is enforced.

No duplicate full matrix is saved by the checker: phase1 establishes that
the delivered author CSV equals the independently reconstructed matrix.
Its SHA256 is
`81a5ac8ee1b82bf1e5149e06fe0389c67c6371a058b70f59a84dbfbe256de17b`.

## Scope and kernel gate

The declared basis order is h3(60), k3(234), P2(702), P1(702), P0(702).
Directions r,v,t and input compact rows0,1 are retained separately. h3 has
r=-10..-6, v=0..1, t=0..2. Every lower numerator and k3 uses the original
r=-10..2, v,t=0..2 box. Prime32003 and seed2026102458 are checked.

Only P3 is tangent. The independently used top operator has zeroth scalar
tau3=r^7+12r and connection ell*A*M_a+t*T_v*M_b, with
ell=3r(r^6-1). Its direct quotient zero-order value div(T)-3T(A)/A is also
checked at every sample. P2, P1 and P0 remain completely unrestricted;
neither lower tangency nor the earlier A-squared projection is imposed.
Both compact output rows, all physical derivatives, source orientation and
the 1/12 factor remain present.

A nonzero modular determinant at points where all denominators are units
gives a nonzero determinant of the fixed rational evaluation matrix. There
are only2400 coefficient columns, so its equation is inconsistent over Q.
This does not assume that hypothetical rational solution coefficients have
good reduction at32003.

Exclusion of the original2808-parameter B+B/A+B/A²+B/A³ family additionally
uses the **imported** highest-pole/support theorem. At A=0,
det(R_a-3I)=10 forces only P3=(T_r h3,T_v h3,k3). This theorem applies to
homogeneous currents as well as candidate solutions. Hence every original
kernel current lies in the tested2400-parameter family; full coefficient
rank makes its reduced coefficients zero. Injectivity of the tangent map
and directness of the sectors then give the zero original current.

The old divisor, tangency and support checks, A/A² determinants, Q/R2, beta,
source/trace and Lean results were not rerun. This checker makes no general
rational-current exclusion, source-exactness, primitive or solve claim.

## Source binding and executions

The literal connection SHA256 is
`a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d`.
Public integration parent is `2dff6afddab993a216ba3f262197ae69aeb9143a`.
The local cached checkout is `fc4f38a338b47addf62d1bf699783302285378fe`;
this review does not claim a fresh checkout of the newer parent. Root's
live-source binding is distinct from these mathematical executions.

| Process | Mathematical seconds | Wall seconds | Exit | Timeout |
| --- | ---: | ---: | ---: | --- |
| Independent reconstruction | 7.202408 | 7.590859 | 0 | No |
| Bound-matrix Bareiss determinant | 38.733696 | 38.934952 | 0 | No |

Both ran under `-O`, with explicit exception gates and fresh output
directories, Python3.12.14 and NumPy2.5.4. Both had empty stderr. Each
wrapper imposed60 seconds. No failed calculation, timeout or repair occurred.
The source snapshots, commands, versions, stdout/stderr, exits and times
are retained in their individual execution receipts.

Twelve mutation differences were nonzero at (r,v,t)=(9563,25785,6750)
modulo32003:

| Mutation | Nonzero difference |
| --- | ---: |
| Replace top quotient factor3 by2 | 17960 |
| Omit top r quotient term | 15442 |
| Omit top v quotient term | 6435 |
| Reverse top quotient sign | 11751 |
| Omit P2 r quotient term | 24066 |
| Omit P2 v quotient term | 6340 |
| Omit P1 r quotient term | 1147 |
| Omit P1 v quotient term | 491 |
| Omit A_v connection chain | 28220 |
| Omit source1/12 | 26457 |
| Reverse source sign | 1901 |
| Omit k3 t derivative | 661 |

These controls discriminate specified implementation mistakes; the new
nonzero minor supplies the finite-family exclusion.

## Reproduction

From the repository root, choose fresh run names or absolute output paths:

```sh
python3 -O results/skew-A3-denominator-20261024/checker/run_bounded.py \
  results/skew-A3-denominator-20261024/checker/reconstruct_A3.py \
  reconstruction-NEW results/skew-A3-denominator-20261024/lead/sum-01/result
python3 -O results/skew-A3-denominator-20261024/checker/run_bounded.py \
  results/skew-A3-denominator-20261024/checker/determinant_A3.py \
  determinant-NEW results/skew-A3-denominator-20261024/lead/sum-01/result \
  results/skew-A3-denominator-20261024/checker/reconstruction-NEW/result
```

The checker owned only this new directory. No commit, push, upstream action,
shared README/ledger/team-board edit or Lean process was performed.

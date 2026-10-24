# Separate A-sixth matrix reconstruction

24 October 2026, 13:56 EDT. This AI worker independently reconstructed the
new matrix from the literal connection. It computed no determinant, replayed
no earlier mathematics, and made no Lean or shared-file changes.

## Executed result

- **PASS:** all **20,551,920 entries** in the **4,560 by 4,507** matrix.
- All **2,280 sample/domain records**, the rejection sequence and the full
  basis order were regenerated independently from `random.Random(2026102486)`
  modulo prime 65521. This seed produced no rejected points.
- Every one of the **4,212 lower-sector parameters** remains free. Only the
  top P6 sector uses the imported tangent parametrization, giving 4,506
  coefficient directions in total.
- **21 mutation controls** detected: top order 6→5, missing top r/v quotient
  corrections, reversed quotient sign, every P5/P4/P3/P2/P1 r/v quotient
  omission, missing A_v chain, each of the three N_t terms, the source sign
  and 1/12 normalization, and the k6 t derivative. The receipt saves the
  actual expected/mutated entries and nonzero differences.
- One new process, under `-O` and a 60-second watchdog: **18.318808 seconds
  wall**, 18.104680 seconds internally, exit **0**. No failure, timeout or
  repair occurred.
- Mathematics stopped at **2026-10-24 17:56:56 UTC / 13:56:56 EDT**.
  Later README and manifest writes are packaging only.

## Implementation and source binding

The checker uses a restricted integer-AST evaluator for the literal JSON,
the reduced W6 operator with tau6=-8*r^7+21*r, and exponent-lowered monomial
derivatives. It does not import the author's direct-quotient implementation.
Values remain Python integers until stored as uint16; c' is reduced modulo
the prime before connection arithmetic. Both output rows and the complete
physical N_t remain. No separate lower tangency or previous family exclusion
is imposed on the changed residual.

Literal connection SHA256:
`a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d`.

The independently reconstructed bytes and author matrix are exactly equal:

`a9dc98a238c3fabc1d19f7fded3ea59c69f836e8c20c9824dafeab3597f45838`.

The format is row-major little-endian unsigned 16-bit integers, no header,
shape (4560,4507), **41,103,840 bytes**. No duplicate matrix is saved by this
checker. This is mathematical reconstruction plus byte comparison, not just
hash checking. Inputs.json SHA256 is
`9bf8f320d34d485987866280c3f7925e0d4d1502e48462f2642a96ecf977d627`.

The generic divisor, bounded tangent/support theorem and order-six
highest-pole reduction are imported evidence. The coordinator separately
reports 7 exact structural checks and 3 controls in 7.250 seconds, including
det(Ra-6I)=38, tau6=-8*r^7+21*r and the 4914-to-4506 injection with all lower
coefficients free. Its reported algebra script SHA256 is
`642e1ff19774630891bb9e18d51d10f11d7aacc25b30651e3a6839cb88b62d2b`.
This worker checks use of the resulting operator at all new samples; it
does not reprove those generic structural statements.

## Determinant and delivery evidence are separate

The coordinator reports a separately reconstructed first 4507-row minor:
20,313,049 entries at 2254 points, determinant **60070 modulo 65521**, one
12.438-second FLINT 0.9.0 process and three controls. This determinant was
**not executed by this checker**. Reported coordinator hashes are:

- Script: `c6e087f7e7f4de30ac85a56d957fb6b6289bf0b0991f85f7c0b5991192752984`.
- Report: `e76ec5b025e4b60e1cff69539b3cc9030f366ebf32e58d7ca55d2764f9bf0d5a`.
- Frozen NPY: `c12a14314359c8ba92f967238cf55e4d88e89b01b160e0af8be8039e8bea9817`.

Those coordinator-owned files are not included as this worker's executions.
The later direct matching of delivered entries/domain/basis records to the
coordinator's frozen data is IO binding, separately from its mathematical
reconstruction and determinant. That receiver comparison is pending at this
worker's freeze.

A nonzero rational augmented minor, combined with the imported necessary
top-pole restriction, excludes the stated finite constant-Q coefficient
family. Reconstruction alone is not the determinant proof. No deficient
modular rank gap, hidden-kernel assumption, general rational-current
exclusion, primitive, source exactness, certificate or solve is claimed.
Separate AI implementations are not independent human reviews.

## Fresh reproduction

From the repository root, with NumPy available, choose an unused run name:

```sh
python3 results/skew-A6-denominator-20261024/checker/run_bounded.py \
  results/skew-A6-denominator-20261024/checker/reconstruct_A6.py \
  reconstruction-fresh \
  results/skew-A6-denominator-20261024/lead/matrix-01/result
```

The wrapper puts the named run under checker/, rejects an existing output
directory, launches the checker with `-O`, and preserves source/runner
snapshots, command, versions, stdout/stderr, timing, exit and hashes. Gates
use explicit exceptions rather than removable assertions. The actual run
is `reconstruction-01/`; no additional replay was run for packaging.

Credit fqlx for the connection, benediamond for the physical cover and earlier
reductions, and the hodge.computer contributors for the fixed framework.
This is scoped AI-assisted work for Ravi Bajaj.

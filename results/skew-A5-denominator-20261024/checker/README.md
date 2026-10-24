# Separate A-fifth matrix reconstruction

24 October 2026, 13:42 EDT. **PASS: all 14,687,300 entries of the
3,860 by 3,805 augmented matrix independently reconstructed.** No determinant
was calculated by this worker. Mathematics stopped at 17:42:22 UTC /
13:42:22 EDT. The remaining writes are packaging only.

## New execution and exact scope

The single process ran under `-O` with a 60-second watchdog, exit 0,
13.006718 seconds wall (12.803464 seconds internally).
There was no mathematical failure, timeout or repair. It checked all 1,930
sample/domain records, the complete independently regenerated rejection
sequence, every basis label and all matrix bytes. There were
0 rejected draws in the saved sequence.

The fixed specification is prime 65519, Python `random.Random` seed
2026102475, successive nonzero r,v,t draws, and compact output row0 then
row1. Columns are h5 (60), k5 (234), P4,P3,P2,P1,P0 (702 each), then the
positive A^5*r^-4*M_b*e0/12 source. Direction, input row and m,n,k ordering
matches the published specification. Only the top P5 sector is parametrized
by the imported tangent module; **all 3,510 lower parameters remain free**.
No old lower-sector exclusion or separate tangency is imposed.

The checker uses the literal connection through a restricted integer-AST
evaluator, the reduced W5 with tau5=-5*r^7+18*r and exponent-lowered
monomial derivatives. It does not import the lead's direct-quotient code.
All physical r,v,t chain terms and both compact rows remain. Values are
Python integers before the uint16 output assignment; the c' coefficient is
reduced modulo the prime before connection arithmetic.

Nineteen single-entry controls detected top order5→4, missing top r/v
quotient corrections, reversed quotient sign, each P4/P3/P2/P1 r/v quotient
omission, the A_v connection chain, each N_t coefficient term, source sign
and 1/12 normalization, and the k5 t derivative. The receipt preserves each
expected value, altered value and nonzero difference. These diagnose
implementation errors; they do not replace a determinant certificate.

## Source, file and evidence binding

Literal packet SHA256:
`a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d`.

Author binary and independently reconstructed raw bytes both have SHA256:
`63a48714c2f7a7ce3a20829540a8573607b5ced164b2203922604e60d9fa342e`.

The matrix is row-major little-endian unsigned 16-bit integers, no header,
shape 3860 by 3805. No duplicate matrix is saved in this checker directory.
All entries were mathematically reconstructed before the byte comparison;
this execution is more than a file-hash check.

The top-pole determinant det(Ra-5I)=80/3, the generic divisor/tangent/support
arguments, and the coordinator's minimal symbolic checks are imported
structural evidence, not rerun by this checker. The coordinator reported
7 new identities and 3 controls in 2.250 seconds, script SHA256
`bad3f26c1f1f07c944024b6acdfa91f0c4953951a3c8f434ebd66b24850e8d8c`.
This reconstruction checks their use in the saved numerical operator, not
those generic proofs anew.

The coordinator separately reports an exact first-3805-row determinant
31971 modulo 65519 from python-flint0.9.0, reconstructing 14,478,025 entries
at 1,903 points in 11.656 seconds with three controls. Its reported report
SHA256 is
`3ead7fda7eb606548b1b12604324a781ab452fb38395f13e112cfe631c36437f`.
That determinant is **not this worker's execution**. The later comparison
against the delivered frozen minor is a separate IO-only binding step.
No backend installation or determinant attempt was made here.

The nonzero rational augmented minor, together with the imported necessary
restriction, excludes the stated finite constant-Q coefficient family.
Reconstruction alone is not that determinant proof. No general rational
current exclusion, source exactness, primitive, certificate or solve is
claimed. Separate AI implementations are not independent human review.

## Reproduction in a fresh directory

From the repository root with NumPy available:

```sh
python3 results/skew-A5-denominator-20261024/checker/run_bounded.py \
  results/skew-A5-denominator-20261024/checker/reconstruct_A5.py \
  reconstruction-fresh \
  results/skew-A5-denominator-20261024/lead/matrix-01/result
```

The wrapper places the run beneath checker/, rejects an existing run
location, invokes Python with `-O`, and saves source/runner snapshots,
stdout/stderr, commands, versions, timing and exit status. Validation uses
explicit exceptions rather than removable assertions. The executed command
is in `reconstruction-01/execution.json`. No replay is needed for integration.

Integration parent: ce22ec3a0636e9c2dbe7e90e1a36ae63f5f4b44a.
Actual cached execution checkout: fc4f38a338b47addf62d1bf699783302285378fe.
Only this new checker directory was written. No old mathematics, Lean,
shared-file edit, commit, push or upstream action was performed.

Credit fqlx for the connection, benediamond for the physical cover and earlier
reductions, and the hodge.computer framework. This is scoped AI-assisted
research for Ravi Bajaj.

# Separate A-seventh matrix reconstruction

24 October 2026, 2:12 p.m. EDT. This AI worker independently reconstructed
the new matrix from the literal connection, using the reduced W7 operator.
It executed no determinant, earlier mathematical batch, Lean command,
installation, Git mutation or shared-file change.

## Executed result

- **PASS:** all **27,503,520 entries** of the **5,280 by 5,209** full matrix.
- All **2,640 sample/domain records**, the rejection sequence and the full
  basis order were independently regenerated from `random.Random(2026102497)`
  modulo **65519**. This seed produced no rejected points.
- **All 4,914 lower-sector coefficients remain free**. Only P7 uses the
  imported tangent parametrization. There are 5,208 coefficient directions.
- **23 mutation controls detected:** top order 7→6; missing top r/v quotient
  terms; reversed top quotient sign; each P6/P5/P4/P3/P2/P1 r/v quotient
  omission; missing A_v chain; each of the three N_t terms; source sign and
  1/12 normalization; and the k7 t derivative. The receipt saves concrete
  expected/mutated entries and nonzero differences.
- One new `-O` process with a 60-second watchdog, **26.800365 seconds wall**,
  26.504078 seconds internally, exit **0**, no timeout, failure or repair.
- This worker's mathematics ended at **2026-10-24 18:12:49.311741 UTC**
  (**2:12:49 p.m. EDT**). Subsequent README/manifest work is packaging only.

## Independent implementation and binding

The checker uses a restricted integer-AST evaluator for the literal JSON,
the reduced W7 operator with tau7=-11*r^7+24*r, and exponent-lowered monomial
derivatives. It does not import the lead's direct-quotient implementation.
Values remain Python integers until stored as uint16. Both output rows,
positive source orientation and all three terms in N_t are retained. No
independent lower tangency or prior finite-family exclusion is imposed on
this changed residual.

Literal connection SHA256:
`a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d`.

Independently reconstructed matrix bytes exactly equal the author's bytes:
`7ab80831f8757663bc208ecb4a391509ab18080b0a6f776d0a4b57695c9e2230`.
Format: row-major little-endian uint16, no header, shape (5280,5209),
**55,007,040 bytes**. No duplicate matrix is saved by this checker.
This is mathematical reconstruction followed by byte comparison, not only
a comparison of supplied hashes. Inputs.json SHA256:
`4d67271f1607894a72afab28a39d3ee0e2e1752da414f3e85b6b32f418ee4ded`.

The generic divisor, bounded tangent/support theorem and order-seven
highest-pole restriction are imported. The coordinator reports 7 exact
structural checks and 3 controls in 2.297 seconds, including det(Ra-7I)=154/3,
tau7=-11*r^7+24*r and the 5616-to-5208 sparse injection. Its algebra script
SHA256 is `aca70673f8a5273e56bbe4f60066102678c3a7157199c8fde29415455c7a1cab`.
This worker checks the reduced operator's use at every new sample; it does
not reprove those generic structural statements.

## Determinant and delivered-file binding are separate

The coordinator separately reports its first 5209-row minor: **27,133,681
entries** at **2605 points**, exact determinant **56940 modulo 65519**, one
18.563-second FLINT 0.9.0 process and three controls. This determinant was
**not executed by this checker**. Reported coordinator hashes are:

- Script: `07ddcf92422a9147799d31bfc623f54c81f9df498f2421f0953eb9b2c09725e0`.
- Report: `9ab4f9b0617984a5780e5e042f5b660bd86c4dfb0395df24e4a5a411dc655526`.
- Frozen uint16 array: `8f4a48490018861c4599e08ae1e6da0e279b874c260e96d6350af74110f81b28`.

Those coordinator-owned files are not represented as this worker's
executions. Coordinator matching of delivered decisive entries and
domain/basis records to its frozen data is a later IO-only binding step,
distinct from either mathematical reconstruction. That receiver comparison
is pending at this worker's freeze.

A nonzero rational augmented minor, with the imported necessary top-pole
restriction, excludes the stated finite constant-Q coefficient family.
Reconstruction alone is not a determinant proof. The nonzero full-size
augmented minor also establishes full coefficient-column rank, so no
deficient modular rank gap or unaccounted kernel is used. No general
rational-current exclusion, primitive, full-source exactness, certificate
or solve is claimed. Separate AI implementations are not independent
human reviews.

## Fresh reproduction

From the repository root, with NumPy available, use an unused run name:

```sh
python3 results/skew-A7-denominator-20261024/checker/run_bounded.py \
  results/skew-A7-denominator-20261024/checker/reconstruct_A7.py \
  reconstruction-fresh \
  results/skew-A7-denominator-20261024/lead/matrix-01/result
```

The wrapper places the run under checker/, refuses an existing directory,
launches `-O`, and preserves source/runner snapshots, exact command,
versions, stdout/stderr, timing, exit and hashes. Gates use explicit
exceptions rather than removable assertions. The executed run is
`reconstruction-01/`; there was no packaging replay.

Credit fqlx for the connection, benediamond for the physical cover and
earlier reductions, and hodge.computer contributors for the framework.
This is scoped AI-assisted work for Ravi Bajaj.

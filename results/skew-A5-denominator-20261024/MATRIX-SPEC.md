# Fixed A-fifth matrix specification

This specification was exposed in chat before the new mathematical execution,
24 October 2026 EDT. It is not selected after observing a determinant.

- Prime: **65519**. Python `random.Random` seed: **2026102475**.
- Draw successive `[rng.randrange(1, prime) for _ in range(3)]` in r,v,t order.
  Accept the first **1930** triples where A, Delta and every literal connection
  denominator are nonzero. Save every rejection in inputs.json.
- Rows: compact output row0 followed by row1 at each accepted point.
- Multiply the entire full-current equation, including its positive source,
  by A^5. The augmented matrix is **3860 by 3805**.
- The **first 3805 rows** form the proposed decisive square. They use 1903
  admissible points, with only row0 from the last point.

Columns in fixed order:

1. h5: input row j=0,1, then m=-10,...,-6, n=0,1, k=0,1,2 (60).
2. k5: input row j=0,1, then m=-10,...,2, n,k=0,1,2 (234).
3. P4, P3, P2, P1, P0 in that order: direction r,v,t, then input row j=0,1,
   then m=-10,...,2, n,k=0,1,2 (702 each).
4. Positive source A^5*r^-4*M_b*e0/12.

Each inner index increases before returning to the preceding outer loop.
h5 has direction label -1; k5 has direction label 2. All 3510 lower-sector
parameters remain free. No separate lower tangency or old family exclusion
is imposed on a changed residual.

The author constructs direct quotient derivatives. Its top scalar term is
div(T)-5*(T_r*A_r+T_v*A_v)/A. Its Pj column has -j*A_i/A before multiplying
by A^(5-j). A_t=0, but the full N_t remains. The separate checker uses the
literal JSON connection through an integer AST and reduced W5 with
tau5=-5*r^7+18*r, independently regenerating sample/domain and basis records.

The full matrix is saved without a redundant CSV or NPY: row-major,
little-endian unsigned 16-bit values, no header, **29,374,600 bytes**.
Load with `numpy.fromfile(path, dtype='<u2').reshape(3860, 3805)`.
All entries are canonical residues from0 through65518.

The coordinator's separate checker computes the exact modular determinant.
Pro performs no backend installation or determinant run. Later comparison
against the coordinator's frozen decisive minor is IO binding, separately
from its mathematical reconstruction and determinant computation.

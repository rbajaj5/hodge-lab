# Fixed A-fourth matrix specification

Declared in chat before the new matrix execution, 24 October 2026 EDT.
Prime **65521**; Python `random.Random` seed **2026102469**. Draw successive
`[rng.randrange(1, prime) for _ in range(3)]` in r,v,t order. Accept the first
**1580** triples where A, Delta and every literal connection denominator are
nonzero. The saved sequence contains no rejected triples. Rows are compact
output row0 then row1 at each accepted point.

The full physical equation is multiplied by A^4, including the positive
source A^4*r^-4*M_b*e0/12. The matrix has **3160 rows and 3103 columns**.
The first **3103 rows** form the declared decisive square; they use 1552
points, with only output row0 from the last point.

Columns, in order:

1. h4: input row j=0,1; m=-10,...,-6; n=0,1; k=0,1,2 (60).
2. k4: input row j=0,1; m=-10,...,2; n,k=0,1,2 (234).
3. P3, P2, P1, P0, in that order: direction r,v,t; input row j=0,1;
   m=-10,...,2; n,k=0,1,2 (702 each).
4. Positive source column.

Each inner exponent increases before returning to the preceding outer loop.
Thus the ordering within a lower sector is direction,j,m,n,k. h4 has
direction label -1 and k4 label 2. All 2808 lower parameters remain free.
Only the imported highest-pole restriction is applied to P4.

The author constructs direct quotient derivatives: the top contribution
contains -4*(T_r*A_r+T_v*A_v)/A; a lower Pj contribution contains
-j*A_i/A before multiplication by A^(4-j). A_t=0 but N_t is retained.
The checker reconstructs W4 with tau4=-2*r^7+15*r, plus every lower sector,
using the literal source through integer AST evaluation.

`lead/matrix-01/result/inputs.json` records every basis label and point/domain
record. `augmented-matrix.u16.bin` stores the full matrix as row-major
little-endian unsigned 16-bit integers, with no header. Its exact length is
19,610,960 bytes. Load it with:

```python
M = numpy.fromfile(path, dtype='<u2').reshape(3160, 3103)
minor = M[:3103]
```

No CSV or redundant NPY is included. The coordinator has independently
computed determinant 28764 modulo 65521 for its frozen minor. The included
`bind_local_minor.py` performs only the subsequent entry-by-entry delivery
binding; it has not been run here because the coordinator's NPY is local
to its environment. No expected parent-plus-payload Git tree is claimed.

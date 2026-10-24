# Fixed A-sixth matrix specification

Exposed in chat before numeric results, 24 October 2026 EDT. No determinant
was used to select this specification.

- Prime **65521**, Python `random.Random` seed **2026102486**.
- Draw successive `[rng.randrange(1, prime) for _ in range(3)]` in r,v,t
  order. Retain the first **2280** triples where A, Delta and every literal
  connection denominator are nonzero. Save all rejections in inputs.json.
- Rows: compact output row0, then row1, at each accepted point.
- Scale the entire full-current equation, including its positive source,
  by A^6. Full augmented matrix: **4560 by 4507**.
- Proposed decisive minor: **first 4507 rows**, using 2254 admissible points,
  with only row0 from the last point.

Columns in fixed order:

1. h6: input row j=0,1; m=-10,...,-6; n=0,1; k=0,1,2 (60).
2. k6: input row j=0,1; m=-10,...,2; n,k=0,1,2 (234).
3. P5,P4,P3,P2,P1,P0: direction r,v,t; input row j=0,1; m=-10,...,2;
   n,k=0,1,2 (702 per sector).
4. Positive source A^6*r^-4*M_b*e0/12.

Each inner index increases before returning to the preceding outer loop.
h6 has direction label -1; k6 has direction label 2. **All 4212 lower
parameters remain free.** No previous exclusion, lower tangency or separate
secondary projection restricts the changed lower residual.

The author uses direct quotient derivatives, including the top term
-6*(T_r*A_r+T_v*A_v)/A and every lower -j*A_i/A correction before scaling
by A^(6-j). A_t=0, but the full N_t remains. The separate checker uses a
literal integer-AST connection evaluator and reduced W6 with tau6=-8*r^7+21*r.

The complete matrix is raw row-major little-endian uint16, no header,
**41,103,840 bytes**, with canonical entries from 0 through 65520.
Load with `numpy.fromfile(path,dtype='<u2').reshape(4560,4507)`.
There is no redundant CSV or NPY in this packet. Inputs.json records every
domain/sample, rejection and basis label. This seed yielded no rejections.

The coordinator independently computes the exact determinant. Pro performs
no determinant/backend setup. Later comparison with its frozen minor and
domain/basis records is IO binding, not another mathematical execution.

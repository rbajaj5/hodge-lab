# A8 specification declared before numerical results

24 October 2026, America/New_York. Goal and exact determinant are coordinator-owned.
Integration parent: `c6e2e54f957eeeaa97cabc7a26df6d81ffd759ee`.
Literal connection SHA256: `a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d`.

- Prime **65521**, Python `random.Random` seed **2026102508**.
- Generate successive triples with three `randrange(1,65521)` calls for r,v,t.
- Reject A=0, Delta=0, or any zero literal connection denominator.
- Keep the first **3000 admissible points**, saving all rejections too.
- Multiply the equation by A^8. Retain both rows and the positive source.
- Each point emits compact output row0, then row1.
- Columns: h8(60), k8(234), P7,P6,P5,P4,P3,P2,P1,P0(702 each), positive source.
- h8 loops input row j=0,1; m=-10..-6; n=0..1; k=0..2.
- k8 loops input row j=0,1; m=-10..2; n=0..2; k=0..2.
- Each lower sector loops direction r,v,t; input row j=0,1; m=-10..2; n=0..2; k=0..2.
- Every loop increases. Direction labels: h8=-1,k8=2,lower r/v/t=0/1/2.
- Full matrix **6000 x 5911**. Decisive square: **first5911 rows**, using
  **2956 admissible points** with only row0 of the last point.
- Storage: row-major little-endian uint16 (`<u2`), no header.

Original nine-sector family:6318 rational-constant parameters. Imported
top-only tangency restricts P8 to294 parameters; all5616 lower coefficients
remain free. Necessary family has5910 coefficient columns. No lower tangency
or previous exclusion is imposed on changed residuals. A nonzero augmented
square supplies the required full coefficient rank and exclusion; deficient
modular rank alone would not exclude the characteristic-zero family.

Author:direct quotient columns. Separate Pro worker:literal integer-AST
connection evaluation,reducedW8,exponent-lowered derivatives. Coordinator:
independent exact determinant, then IO-only delivered-entry/domain/basis binding.

Budget:math child<=60s,network<=45s,one justified repair of an unchanged
failed approach. No determinant/backend setup here. Research deadline
2026-10-24 19:09:57UTC (3:09:57p.m.EDT); stop earlier after decisive checks.

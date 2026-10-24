# A7 specification fixed before numerical results

24 October 2026, America/New_York. Goal and exact determinant are coordinator-owned.
Integration parent: `030d13b75270f6ad1a774e9c11321038fe6305e9`.
Literal connection SHA256: `a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d`.

- Prime: **65519**; Python `random.Random` seed: **2026102497**.
- Draw three successive `randrange(1, 65519)` values for `(r,v,t)`.
- Reject `A=0`, `Delta=0`, or any zero literal connection denominator.
- Use the first **2640 admissible points**, recording rejected points too.
- The equation is multiplied by `A**7`; retain both rows and positive source.
- At each point, output compact row 0, then compact row 1.
- Columns: `h7` (60), `k7` (234), `P6,P5,P4,P3,P2,P1,P0` (702 each), then positive source.
- `h7` loops input compact row `j=0,1`, `m=-10..-6`, `n=0..1`, `k=0..2`.
- `k7` loops input compact row `j=0,1`, `m=-10..2`, `n=0..2`, `k=0..2`.
- Each `Pj` loops direction `r,v,t`, input compact row `0,1`, `m=-10..2`, `n=0..2`, `k=0..2`.
- Every loop increases. Basis labels use direction `-1` for h7, `2` for k7, and `0,1,2` for lower r,v,t fluxes.
- **5280 x 5209** full augmented matrix. Proposed decisive square: first **5209 rows**; **2605 points**, with only row 0 of the final point.
- Binary: row-major little-endian uint16 (`<u2`), no header.

The original eight-sector family has 5616 scalar parameters. Imported top-only
tangency gives a necessary 5208-column family: h7=60, k7=234, and all 4914
lower coefficients free. No lower tangency or previous exclusion is imposed.
A full-rank augmented square excludes this rational-constant family; deficient
modular rank alone would not be a characteristic-zero exclusion.

Author uses direct quotient columns. Separate Pro worker uses literal integer
AST connection evaluation and reduced W7. Coordinator runs the exact determinant
independently and later performs IO-only delivered-entry/domain/basis binding.

Limits: math child <=60 seconds; network <=45 seconds; one justified repair of
an unchanged failure; no determinant/backend setup here. Research deadline
2026-10-24 18:53:45 UTC (2:53:45 p.m. EDT); stop earlier on decisive evidence.

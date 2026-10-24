# Independent A-sixth-power minor check

The fixed **4507-square** augmented minor has exact determinant **60070 modulo 65521**. It excludes the declared finite family of six physical flux entries

```
(B+B/A+B/A^2+B/A^3+B/A^4+B/A^5+B/A^6)^6,
B=span_Q{r^m v^n t^k:-10<=m<=2,0<=n,k<=2},
A=r^3+r^-3+(rv-1)^6/r^15.
```

These are three rank-two compact fluxes, not six homogeneous-certificate numerators. This coefficient `A(r,v)` differs from the protected homogeneous source. No general rational-current obstruction, target solution, homogeneous certificate, Lean proof or accepted solve is claimed.

## Operator and scope

The positive source remains `S=r^-4 M_b e0/12`. At `(a,b,c,d)=(A,tv,t(1-t^2)/7,1+t^6)`, the coefficient connection is

```
N=(A_r M_a, A_v M_a+t M_b,
   v M_b+(1-3t^2)M_c/7+6t^5 M_d).
```

Input basis vectors index columns, and the operator is `d+N`. Both compact rows and all physical derivatives are retained.

The completed source/divisor/tangent/support certificates are reused. The new highest residue satisfies `det(R_a-6I)=38`, restricting only `P6` to `(T_r h6,T_v h6,k6)`, where

```
T_r=r^2(r^6+1), T_v=r(2r^6+1)v-(3r^6+2),
q=T(A)/A=3r(r^6-1), tau6=div(T)-6q=-8r^7+21r.
```

Each `h6` entry has support `r=-10..-6,v=0..1,t=0..2`; each `k6` entry has full `B` support. This gives 294 top coefficients. **All 4212 lower coefficients in P5,P4,P3,P2,P1,P0 remain unrestricted.** The original 4914-generator family therefore reduces necessarily to 4506 coefficients. No lower tangency, secondary projection or cross-sector cancellation is discarded.

After multiplying the full equation by `A^6`, the top contribution is

```
W6=[T_r partial_r+T_v partial_v+tau6 I
     +q A M_a+t T_v M_b]h6+(partial_t+N_t)k6.
```

The lower `Pj` columns are `A^(6-j)(partial_i+N_i)u-j A^(5-j)A_i u` for `j=5,4,3,2,1,0`, with scalar corrections in the matching compact row and `A_t=0`. The source column is `A^6 S`.

## Independent fixed execution

The specification was supplied before the Pro numerical result: prime **65521**, `random.Random(2026102486)`, successive `randrange(1,p)` triples `(r,v,t)`, rejecting zero `A`, literal JSON `Delta` or a connection denominator. The full author specification has 2280 accepted points and 4560-by-4507 entries, output row 0 then row 1. This local check reconstructs only the **first 4507 rows** from **2254 points**, using row 0 alone at the final point. The remaining 53 rows and 26 sample records are outside this local reconstruction.

Columns are `h6` (60), `k6` (234), `P5,P4,P3,P2,P1,P0` (702 each), then the positive source. Ordering within each sector is direction where applicable, compact input row, then increasing `r,v,t` exponents.

All **20313049 entries** were independently rebuilt with the previously checked rational-polynomial evaluator, symbolic physical Jacobian, monomial derivatives and reduced tangent operator. No Pro code was replayed and no old matrix was rerun. No point was rejected; 1138270 rational evaluation denominators were checked. The prime and a conservative int64 overflow bound were checked; the saved matrix uses little-endian uint16.

The new residue determinant, `tau6` and abstract sixth reciprocal derivative checks passed. Three local mutations were detected:

| Mutation | Column | Correct | Mutant |
| --- | ---: | ---: | ---: |
| Use order-five tau | 0 | 9620 | 15456 |
| Use quotient factor 4 instead of 5 in P5 | 294 | 11452 | 40527 |
| Omit the P1 quotient derivative | 3102 | 24720 | 16166 |

These are operator-entry controls, not separate determinants of mutated matrices.

Exact determinant backend: `flint.nmod_mat.det`, python-flint **0.9.0**. This is not an independently authored elimination algorithm. Reconstruction including imports took **3.531 seconds**; FLINT construction/determinant took **8.625 seconds**. The subprocess took **12.438 seconds**, with completion observed by **17:55:42 UTC** on 24 October 2026. Neither the 58-second watchdog nor the 60-second outer limit fired. There was one successful mathematical run, no failure, no timeout, no random retry and no additional matrix search.

The algebra worker's announced A-sixth-power formula was relayed by the coordinator before this run and used to define the highest-only family. Its executed receipt arrived during the run and was read afterward; it is not represented as a pre-read dependency. The new symbolic constants were also checked in this independent execution. Old source, trace, divisor and support facts were not re-proved.

## Why this excludes the declared family

At integer lifts of the fixed sample coordinates, every entry denominator is a unit modulo 65521. The rational augmented determinant therefore reduces to 60070 and is nonzero. Its 4507 columns are independent, while there are only 4506 coefficient columns. No rational constant coefficient vector solves these necessary evaluations. This directly handles the kernel issue; it does not infer a characteristic-zero rank upper bound from deficient modular rank. Denominators of hypothetical unknown coefficients need not be prime to 65521, since the argument does not reduce an unknown solution.

Together with the highest-pole/support necessity, this excludes the original declared sum and its pure `B/A^6` subfamily. Larger supports, seventh or higher powers of `A`, other denominator divisors, arbitrary rational compact currents and fibre-dependent functions remain outside scope.

## Provenance and reproduction

Observed parent: `a5087f7601b0d5047c55add75b5c020251b8a09b`. Only this owned checker directory was written. A read-only parent-identification command was used; no Git write, commit, push or network operation was performed.

| Artifact | SHA-256 |
| --- | --- |
| Literal connection | `a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d` |
| Reused structural report | `7493c4076b993709f51b15e612b2b102855887aba76d7907563addabfabf7af7` |
| Reused A-fifth-power report | `3ead7fda7eb606548b1b12604324a781ab452fb38395f13e112cfe631c36437f` |
| Executed script | `c6e087f7e7f4de30ac85a56d957fb6b6289bf0b0991f85f7c0b5991192752984` |
| `A6-minor.json` | `e76ec5b025e4b60e1cff69539b3cc9030f366ebf32e58d7ca55d2764f9bf0d5a` |
| `regenerated-inputs.json` | `708c10f9fc6420e179b71372c964e5b48bb8a649a447b8a22723a10fe9af238e` |
| `regenerated-minor.npy` | `c12a14314359c8ba92f967238cf55e4d88e89b01b160e0af8be8039e8bea9817` |

`A6-minor-receipt.json` binds the command, outputs, runtime and raw UTF-8 streams. The independently generated binary matrix has **40626226 bytes**; there is no duplicate text CSV. If omitted from a public payload, disclose that omission; the script regenerates the exact bytes.

Reproduce in a copy with Python 3.11.9, SymPy 1.14.0, NumPy 2.4.6 and python-flint 0.9.0:

```powershell
python audit_A6_regenerated_minor.py --connection 'C:/path/to/source-rank2-connection.json' --prior-structure 'C:/path/to/structure-independent.json' --prior-A5-report 'C:/path/to/A5-minor.json' --prime 65521 --seed 2026102486 --author-points 2280
```

Delivered-matrix binding is **pending and not performed at this freeze**. The prepared, unexecuted binder supports CSV, gzip, NPY, NPZ, raw `.u16` and `.u16.bin`. It requires delivered hashes and explicit raw dimensions. Later binding will have a separate report and receipt and repeat no mathematics.

```powershell
python bind_delivered_packet.py --matrix 'C:/path/to/augmented-matrix.u16.bin' --inputs 'C:/path/to/inputs.json' --matrix-sha256 MATRIX_FILE_SHA256 --inputs-sha256 INPUTS_SHA256 --raw-rows 4560 --raw-columns 4507
```

The complete original local inventory is `freeze-manifest.json`.

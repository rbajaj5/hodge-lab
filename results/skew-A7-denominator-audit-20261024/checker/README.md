# Independent A-seventh-power minor check

The fixed **5209-square** augmented minor has exact determinant **56940 modulo 65519**. It excludes the declared finite family of six physical flux entries

```
(B+B/A+B/A^2+B/A^3+B/A^4+B/A^5+B/A^6+B/A^7)^6,
B=span_Q{r^m v^n t^k:-10<=m<=2,0<=n,k<=2},
A=r^3+r^-3+(rv-1)^6/r^15.
```

These are three rank-two compact fluxes, not six homogeneous-certificate numerators. This coefficient `A(r,v)` differs from the protected homogeneous source. The target remains unsolved. No general rational-current obstruction, homogeneous certificate, Lean proof or accepted solve is claimed.

## Full operator and retained freedom

The source remains positive `S=r^-4 M_b e0/12`, with input columns, ordered compact rows, and operator `d+N`. At `(a,b,c,d)=(A,tv,t(1-t^2)/7,1+t^6)`,

```
N=(A_r M_a, A_v M_a+t M_b,
   v M_b+(1-3t^2)M_c/7+6t^5 M_d).
```

Completed source/divisor/tangent/support evidence is reused. The new highest residue has `det(R_a-7I)=154/3`, restricting only `P7` to `(T_r h7,T_v h7,k7)`, where

```
T_r=r^2(r^6+1), T_v=r(2r^6+1)v-(3r^6+2),
q=T(A)/A=3r(r^6-1), tau7=div(T)-7q=-11r^7+24r.
```

Each `h7` entry has support `r=-10..-6,v=0..1,t=0..2`; each `k7` entry has full `B` support. The top sector has 294 coefficients. **All 4914 lower coefficients in P6,P5,P4,P3,P2,P1,P0 remain unrestricted.** The original family has 5616 generators; this safe necessary family has 5208 coefficients. No secondary projection, lower tangency condition or cross-sector cancellation is discarded.

The whole equation is multiplied by `A^7`. Its top contribution is

```
W7=[T_r partial_r+T_v partial_v+tau7 I
     +q A M_a+t T_v M_b]h7+(partial_t+N_t)k7.
```

Lower `Pj` columns are `A^(7-j)(partial_i+N_i)u-j A^(6-j)A_i u` for `j=6,...,0`. Scalar derivative corrections occur in the matching compact row; `A_t=0`. The source column is `A^7 S`. Both rows and all physical derivatives are retained.

## Fixed independent execution

The specification was supplied before the Pro numerical result: prime **65519**, `random.Random(2026102497)`, successive `randrange(1,p)` triples `(r,v,t)`, rejecting zero `A`, literal JSON `Delta` or any connection denominator. The author specifies 2640 accepted points and a 5280-by-5209 matrix, row 0 then row 1. This check independently reconstructs the **first 5209 rows** using **2605 points**, with only row 0 at the last point. The remaining 71 rows and 35 point records are outside this local reconstruction.

Columns are `h7` (60), `k7` (234), `P6,...,P0` (702 each), then the positive source. Within each sector: direction where applicable, compact input row, increasing `r,v,t` exponents.

All **27133681 entries** were independently rebuilt with the previously checked rational-polynomial evaluator, symbolic physical Jacobian, monomial derivatives and reduced tangent operator. No Pro code was replayed or old matrix rerun. No candidate point was rejected; 1315525 rational evaluation denominators were checked. The prime and conservative int64 overflow bound were checked, and the saved matrix uses little-endian uint16.

The new residue determinant, `tau7` and abstract seventh reciprocal derivative controls passed. Three local operator mutations were detected:

| Mutation | Column | Correct | Mutant |
| --- | ---: | ---: | ---: |
| Use order-six tau | 0 | 30914 | 7549 |
| Use quotient factor 5 instead of 6 in P6 | 294 | 7358 | 23086 |
| Omit the P1 quotient derivative | 3804 | 45530 | 38359 |

The frozen mutation text says "A^6-scaled P1 column." That phrase refers to the `A^6` factor on the ordinary `P1` operator, not the normalization of the entire equation. The precise interpretation is: **omit `-A^5 A_i u` from the P1 column of the equation multiplied by A^7**. The executed code uses `A^6(partial_i+N_i)u-A^5 A_i u` correctly. This is a wording clarification; no executed bytes or numerical outputs were changed. The controls check individual operator entries, not determinants of mutated matrices.

The exact backend is `flint.nmod_mat.det`, python-flint **0.9.0**, not an independently authored elimination algorithm. Reconstruction including imports took **4.454 seconds**; FLINT construction/determinant took **13.718 seconds**. The subprocess took **18.563 seconds**, with completion observed by **18:12:05 UTC** on 24 October 2026. Neither the 58-second watchdog nor 60-second outer limit fired. There was one mathematical run, no failure, no timeout, no random retry and no extra matrix search.

## Characteristic-zero implication and limits

At integer lifts of the sample points, every rational entry denominator is a unit modulo 65519. Thus the rational augmented determinant reduces to 56940 and is nonzero. Its 5209 columns are independent, while there are only 5208 coefficient columns, excluding a rational constant coefficient solution. The nonzero augmented minor directly handles the kernel issue; no characteristic-zero rank upper bound is inferred from modular rank deficiency. Denominators of hypothetical unknown coefficients need not be prime to 65519, since no hypothetical solution is reduced.

The highest-pole/support necessity then excludes the original declared sum and its pure `B/A^7` subfamily. Larger monomial supports, eighth or higher powers of `A`, other denominators, arbitrary rational compact currents and fibre-dependent functions remain outside scope.

## Provenance and reproduction

Coordinator-supplied clean parent: `030d13b75270f6ad1a774e9c11321038fe6305e9`. Only this owned checker directory was written. No Git command, network operation, commit or push was performed in this batch. Old source/divisor/support/trace results were reused, not re-proved.

| Artifact | SHA-256 |
| --- | --- |
| Literal connection | `a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d` |
| Reused structural report | `7493c4076b993709f51b15e612b2b102855887aba76d7907563addabfabf7af7` |
| Reused A-sixth-power report | `e76ec5b025e4b60e1cff69539b3cc9030f366ebf32e58d7ca55d2764f9bf0d5a` |
| Executed script | `07ddcf92422a9147799d31bfc623f54c81f9df498f2421f0953eb9b2c09725e0` |
| `A7-minor.json` | `9ab4f9b0617984a5780e5e042f5b660bd86c4dfb0395df24e4a5a411dc655526` |
| `regenerated-inputs.json` | `3bb3a83d7b80a36ffc3171bb904ea21a855ab7989ff7dc0439280a39f12c7078` |
| `regenerated-minor.npy` | `8f4a48490018861c4599e08ae1e6da0e279b874c260e96d6350af74110f81b28` |

`A7-minor-receipt.json` binds the command, outputs, runtime and raw UTF-8 streams. The independent binary matrix has **54267490 bytes**; no duplicate text CSV is stored here. Disclose any public omission of the array; the script regenerates its exact bytes.

Reproduce in a copy with Python 3.11.9, SymPy 1.14.0, NumPy 2.4.6 and python-flint 0.9.0:

```powershell
python audit_A7_regenerated_minor.py --connection 'C:/path/to/source-rank2-connection.json' --prior-structure 'C:/path/to/structure-independent.json' --prior-A6-report 'C:/path/to/A6-minor.json' --prime 65519 --seed 2026102497 --author-points 2640
```

Delivered-matrix binding is **pending and not performed at this freeze**. The prepared, unexecuted binder supports CSV, gzip, NPY, NPZ, raw `.u16` and `.u16.bin`, requires delivered file hashes and explicit raw dimensions, and performs no mathematical replay. A later binding receives a separate report and receipt.

```powershell
python bind_delivered_packet.py --matrix 'C:/path/to/augmented-matrix.u16.bin' --inputs 'C:/path/to/inputs.json' --matrix-sha256 MATRIX_FILE_SHA256 --inputs-sha256 INPUTS_SHA256 --raw-rows 5280 --raw-columns 5209
```

The complete original local inventory is `freeze-manifest.json`.

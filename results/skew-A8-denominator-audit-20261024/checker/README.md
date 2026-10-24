# Independent A-eighth-power minor check

The fixed **5911-square** augmented minor has exact determinant **30337 modulo 65521**. It excludes the declared finite family of six physical flux entries

```
(B+B/A+B/A^2+B/A^3+B/A^4+B/A^5+B/A^6+B/A^7+B/A^8)^6,
B=span_Q{r^m v^n t^k:-10<=m<=2,0<=n,k<=2},
A=r^3+r^-3+(rv-1)^6/r^15.
```

These are three rank-two compact fluxes, not six homogeneous-certificate numerators. The coefficient `A(r,v)` differs from the protected homogeneous source. The target remains unsolved; no general rational-current obstruction, homogeneous certificate, Lean proof or accepted solve is claimed.

## Operator and retained freedom

The unchanged positive source is `S=r^-4 M_b e0/12`, with ordered input columns and coefficient operator `d+N`. At `(a,b,c,d)=(A,tv,t(1-t^2)/7,1+t^6)`,

```
N=(A_r M_a, A_v M_a+t M_b,
   v M_b+(1-3t^2)M_c/7+6t^5 M_d).
```

Completed source/divisor/tangent/support evidence is reused. The new highest-pole rule has `det(R_a-8I)=200/3`, restricting only `P8` to `(T_r h8,T_v h8,k8)`, where

```
T_r=r^2(r^6+1), T_v=r(2r^6+1)v-(3r^6+2),
q=T(A)/A=3r(r^6-1), tau8=div(T)-8q=-14r^7+27r.
```

Each `h8` entry has support `r=-10..-6,v=0..1,t=0..2`; each `k8` entry has full `B` support. This gives 294 top coefficients. **All 5616 lower coefficients in P7,...,P0 remain unrestricted.** The original family has 6318 generators; the necessary family has 5910 coefficients. No lower tangency, secondary projection or cross-sector cancellation is removed.

The whole equation is multiplied by **A^8**. Its top contribution is

```
W8=[T_r partial_r+T_v partial_v+tau8 I
     +q A M_a+t T_v M_b]h8+(partial_t+N_t)k8.
```

Lower `Pj` columns are `A^(8-j)(partial_i+N_i)u-j A^(7-j)A_i u` for `j=7,...,0`. Scalar derivative corrections occur in the matching compact row, with `A_t=0`. In particular, the **P1 ordinary-operator factor is A^7 and its quotient correction is -A^6 A_i u**. The source column is `A^8 S`. Both compact rows and all physical derivatives are retained.

## Fixed independent execution

The fixed specification arrived before Pro's numerical result: prime **65521**, `random.Random(2026102508)`, successive `randrange(1,p)` triples `(r,v,t)`, rejecting zero `A`, literal JSON `Delta` or a connection denominator. The author specifies 3000 accepted points and a 6000-by-5911 matrix, row 0 then row 1. This local check independently reconstructs the **first 5911 rows** using **2956 points**, with row 0 alone at the last point. The remaining 89 rows and 44 point records are outside this local reconstruction.

Columns are `h8` (60), `k8` (234), `P7,...,P0` (702 each), then the positive source. Within sectors: direction where applicable, compact input row, increasing `r,v,t` exponents.

All **34939921 entries** were independently rebuilt with the existing rational-polynomial evaluator, symbolic physical Jacobian, monomial derivatives and reduced tangent operator. No Pro code was replayed or old matrix rerun. No point was rejected; 1492780 rational evaluation denominators were checked. The prime and conservative int64 overflow bound were checked. The saved array uses little-endian uint16.

The new residue determinant, `tau8` and abstract eighth reciprocal derivative controls passed. Three local operator mutations were detected:

| Mutation | Column | Correct | Mutant |
| --- | ---: | ---: | ---: |
| Use order-seven tau | 0 | 61811 | 5428 |
| Use quotient factor 6 instead of 7 in P7 | 294 | 996 | 14149 |
| Omit `-A^6 A_r u` in P1 | 4506 | 30069 | 44751 |

The frozen P1 annotation explicitly states the A^8 whole-equation normalization and A^7 ordinary-operator factor. These controls concern individual operator entries, not separate determinants of mutated matrices.

The exact determinant backend is `flint.nmod_mat.det`, python-flint **0.9.0**, not an independently authored elimination algorithm. Reconstruction including imports took **4.938 seconds**; FLINT construction/determinant took **21.437 seconds**. Total subprocess time was **26.781 seconds**, with completion observed by **18:27:34 UTC** on 24 October 2026. Neither the 58-second watchdog nor the 60-second outer limit fired. There was one successful mathematical run, no failure, no timeout, no repair, no random retry and no expanded search.

## Characteristic-zero implication and limits

At integer lifts of the fixed sample coordinates, every rational entry denominator is a unit modulo 65521. The rational augmented determinant therefore reduces to 30337 and is nonzero. Its 5911 columns are independent, while there are only 5910 coefficient columns, excluding a rational constant coefficient solution. The augmented minor directly handles possible kernels; no characteristic-zero rank upper bound is inferred from deficient modular rank. Denominators of hypothetical unknown coefficients need not be prime to 65521, since no hypothetical solution is reduced modulo the prime.

Together with highest-pole/support necessity, this excludes the original declared sum and its pure `B/A^8` subfamily. Larger monomial supports, ninth or higher powers of `A`, other denominators, arbitrary rational compact currents and fibre-dependent functions remain outside scope.

## Provenance and reproduction

Coordinator-supplied parent: `c6e2e54f957eeeaa97cabc7a26df6d81ffd759ee`; upstream pin `27f4bb9ad8757e5841f884d9d30124a3c97a847d`. Only this owned checker directory was written. No Git command, network operation, Lean run, shared-document edit, commit or push was performed. Prior source/divisor/module/support/trace results were reused rather than re-proved.

| Artifact | SHA-256 |
| --- | --- |
| Literal connection | `a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d` |
| Reused structural report | `7493c4076b993709f51b15e612b2b102855887aba76d7907563addabfabf7af7` |
| Reused A-seventh-power report | `9ab4f9b0617984a5780e5e042f5b660bd86c4dfb0395df24e4a5a411dc655526` |
| Executed script | `a3ddd2085a67c1081ff1c38807cee17e29c23698fdd7b1f49c00395572fbdaf1` |
| `A8-minor.json` | `a9cbcfece3df8b8cd9c1813d685dbb0ad193838292b4212029f6c9c149fb92ff` |
| `regenerated-inputs.json` | `bfde47073da9b8c079222adfad49a989c493f73ffc1d2f28d4eb85542dcaafd0` |
| `regenerated-minor.npy` | `1c41301ad2a113d530bbd3b13c4ee004ac22fb55219b8bab99ae9850d46ac9e6` |

`A8-minor-receipt.json` binds the command, outputs, runtime and raw UTF-8 streams. The independent binary array has **69879970 bytes**; no duplicate text CSV is stored here. Disclose any public omission of the array; the script regenerates its exact bytes.

Reproduce in a copy with Python 3.11.9, SymPy 1.14.0, NumPy 2.4.6 and python-flint 0.9.0:

```powershell
python audit_A8_regenerated_minor.py --connection 'C:/path/to/source-rank2-connection.json' --prior-structure 'C:/path/to/structure-independent.json' --prior-A7-report 'C:/path/to/A7-minor.json' --prime 65521 --seed 2026102508 --author-points 3000
```

Delivered-matrix binding is **pending and not performed at this freeze**. The prepared, unexecuted binder supports CSV, gzip, NPY, NPZ, raw `.u16` and `.u16.bin`, requires delivered hashes and explicit raw dimensions, and performs no mathematical replay. A later binding receives a separate report and receipt.

```powershell
python bind_delivered_packet.py --matrix 'C:/path/to/augmented-matrix.u16.bin' --inputs 'C:/path/to/inputs.json' --matrix-sha256 MATRIX_FILE_SHA256 --inputs-sha256 INPUTS_SHA256 --raw-rows 6000 --raw-columns 5911
```

The complete original local inventory is `freeze-manifest.json`.

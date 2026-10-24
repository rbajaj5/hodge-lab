# Independent A-fifth-power minor check

The fixed **3805-square** augmented minor has exact determinant **31971 modulo 65519**. It excludes the declared finite six-component family

```
(B+B/A+B/A^2+B/A^3+B/A^4+B/A^5)^6,
B=span_Q{r^m v^n t^k:-10<=m<=2,0<=n,k<=2},
A=r^3+r^-3+(rv-1)^6/r^15.
```

The six components are three rank-two physical fluxes. This coefficient `A(r,v)` is distinct from the protected homogeneous source `X0^3Y0^3`. The full target remains unsolved; no general rational-current obstruction, homogeneous certificate, Lean proof or accepted solution is claimed.

## Full operator and retained freedom

The positive source remains `S=r^-4 M_b e0/12`, with column inputs, ordered compact rows and coefficient derivative `d+N`. At `(a,b,c,d)=(A,tv,t(1-t^2)/7,1+t^6)`, the physical connection is

```
N_r=A_r M_a,
N_v=A_v M_a+t M_b,
N_t=v M_b+(1-3t^2)M_c/7+6t^5 M_d.
```

The completed source/divisor/tangent/support evidence is reused. The new highest-pole rule has `det(R_a-5I)=80/3`, so only `P5` is restricted to the previously established tangent form `(T_r h5,T_v h5,k5)`. Here

```
T_r=r^2(r^6+1), T_v=r(2r^6+1)v-(3r^6+2),
q=T(A)/A=3r(r^6-1), tau5=div(T)-5q=-5r^7+18r.
```

Each entry of `h5` has exponents `r=-10..-6,v=0..1,t=0..2`; each entry of `k5` has full `B` support. The top sector therefore has 294 coefficients. **Every one of the 3510 lower coefficients in P4,P3,P2,P1,P0 remains free.** No previous secondary projection or tangency condition is imposed on a lower sector. The original family has 4212 generators, and this safe necessary family has 3804 coefficients.

The whole equation is multiplied by `A^5`. Its top operator is

```
W5=[T_r partial_r+T_v partial_v+tau5 I
     +q A M_a+t T_v M_b]h5+(partial_t+N_t)k5.
```

For lower `Pj`, `j=4,3,2,1,0`, each column is

```
A^(5-j)(partial_i+N_i)u-j A^(4-j)A_i u,
```

with scalar derivatives in the matching compact row and `A_t=0`. The source column is `A^5 S`. Both compact rows, all physical derivatives and all cross-sector cancellations are retained.

## Fixed execution

The specification arrived before the Pro numerical result: prime **65519**, `random.Random(2026102475)`, successive `randrange(1,p)` triples `(r,v,t)`, rejecting zero `A`, literal JSON `Delta`, or any connection denominator. The author specifies 1930 accepted triples and a 3860-by-3805 matrix, with row 0 then row 1 at each point. This check reconstructs only the **first 3805 rows** at **1903 points**, using row 0 alone at the last point. The remaining 55 rows and 27 point records are outside this independent reconstruction.

Columns are `h5` (60), `k5` (234), `P4,P3,P2,P1,P0` (702 each), then the positive source; within sectors: direction where applicable, compact input row, increasing `r,v,t` exponents.

All **14478025 entries** were independently rebuilt using this checker's rational-polynomial evaluator, symbolic physical Jacobian, monomial derivatives and reduced tangent operator. The sound A-fourth-power machinery was reused; no completed matrix was rerun and no Pro code was replayed. No candidate point was rejected. There were 961015 successful rational-denominator evaluations, and the prime was verified. The script checks an explicit int64 overflow bound before matrix assembly and stores the matrix as little-endian uint16.

The new `det(R_a-5I)`, `tau5` and abstract fifth reciprocal derivative controls passed. Three deliberate local operator mutations were detected:

| Mutation | Column | Correct | Mutant |
| --- | ---: | ---: | ---: |
| Use order-four tau | 0 | 36189 | 58405 |
| Use quotient factor 3 instead of 4 in P4 | 294 | 33086 | 35871 |
| Omit the P1 quotient derivative | 2400 | 49825 | 49545 |

These are operator-entry controls, not determinant calculations on mutated matrices.

The exact determinant backend is `flint.nmod_mat.det` through **python-flint 0.9.0**, not an independently authored elimination algorithm. Reconstruction including imports took **3.704 seconds**; FLINT construction/determinant took **7.656 seconds**. Total subprocess time was **11.656 seconds**, with completion observed by **17:40:43 UTC** on 24 October 2026. The 58-second internal watchdog and 60-second outer limit did not fire. There was one mathematical run, no failure or timeout, no random retry and no additional search.

## Characteristic-zero implication

At integer lifts of the sample coordinates, every rational entry denominator is a unit modulo 65519. Thus the rational augmented determinant reduces to 31971 and is nonzero. Its 3805 columns are independent while there are only 3804 coefficient columns, excluding a rational constant coefficient solution. This directly closes the kernel issue; it does not infer a characteristic-zero rank upper bound from a modular rank drop. Denominators of hypothetical unknown coefficients need not be prime to 65519, because no hypothetical solution is reduced modulo the prime.

Combined with the highest-pole/support necessity, this excludes the original declared sum and its pure `B/A^5` subfamily. Larger supports, sixth or higher powers of `A`, other denominators, arbitrary rational compact currents and fibre-dependent functions remain outside the result.

## Provenance and reproduction

Observed parent: `ce22ec3a0636e9c2dbe7e90e1a36ae63f5f4b44a`. Only this owned checker directory was written; no commit or push was performed.

| Artifact | SHA-256 |
| --- | --- |
| Literal connection | `a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d` |
| Reused structural report | `7493c4076b993709f51b15e612b2b102855887aba76d7907563addabfabf7af7` |
| Reused A-fourth-power report | `c39d7b4ee6207b1ca65f0c545bfd7925d7fc847a1b9ea7cf987d008e9dadb36d` |
| Executed script | `83f4b0e432d20fc769100f57c13c5909db9327bbe3b799024537394f2bb49404` |
| `A5-minor.json` | `3ead7fda7eb606548b1b12604324a781ab452fb38395f13e112cfe631c36437f` |
| `regenerated-inputs.json` | `b5d539fe40c322b7a34d13a25d4c879e7800a2accd7f8fee9087b02af0db8533` |
| `regenerated-minor.npy` | `10dcc8f2d407fb8098eab61fa1f36eeed9ecfc495000f2eb79a99268f760c3b4` |

`A5-minor-receipt.json` binds the command, outputs, runtime and raw UTF-8 stdout/stderr bytes. The independent uint16 array is **28956178 bytes**; no duplicate text CSV is stored here. Any publication omission of this array must be disclosed; the script reproduces its bytes.

Reproduce in a copy using Python 3.11.9, SymPy 1.14.0, NumPy 2.4.6 and python-flint 0.9.0:

```powershell
python audit_A5_regenerated_minor.py --connection 'C:/path/to/source-rank2-connection.json' --prior-structure 'C:/path/to/structure-independent.json' --prior-A4-report 'C:/path/to/A4-minor.json' --prime 65519 --seed 2026102475 --author-points 1930
```

Delivered-matrix binding is **pending and not performed at this freeze**. The prepared, unexecuted `bind_delivered_packet.py` supports CSV, gzip, NPY, NPZ, raw `.u16` and `.u16.bin`, with required delivered file hashes and explicit raw shape. A later binding gets a separate report and receipt; it does no mathematical replay. Example once the raw file and its hashes are available:

```powershell
python bind_delivered_packet.py --matrix 'C:/path/to/augmented-matrix.u16.bin' --inputs 'C:/path/to/inputs.json' --matrix-sha256 MATRIX_FILE_SHA256 --inputs-sha256 INPUTS_SHA256 --raw-rows 3860 --raw-columns 3805
```

The complete original local inventory is `freeze-manifest.json`.

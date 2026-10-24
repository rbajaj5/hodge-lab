# Independent A-fourth-power minor check

The fixed **3103 by 3103** augmented minor has exact determinant **28764 modulo 65521**. This independently excludes the declared finite six-component family `(B+B/A+B/A^2+B/A^3+B/A^4)^6` over the rationals, where

```
B = span_Q{r^m v^n t^k : -10<=m<=2, 0<=n,k<=2},
A = r^3+r^-3+(rv-1)^6/r^15.
```

The six entries are three rank-two physical fluxes. This coefficient `A(r,v)` differs from the protected homogeneous source `X0^3Y0^3`. The target itself remains unsolved. This is not a general rational-current obstruction, homogeneous certificate, Lean proof, or accepted solution.

## Operator and necessary family

The unchanged positive source is `S=r^-4 M_b e0/12`, with ordered input columns and coefficient derivative `d+N`. The full physical connection is

```
(N_r,N_v,N_t)=(A_r M_a, A_v M_a+t M_b,
               v M_b+(1-3t^2)M_c/7+6t^5 M_d),
(a,b,c,d)=(A,tv,t(1-t^2)/7,1+t^6).
```

The prior prime/smooth divisor, source regularity, tangent-module and support results are reused. At the generic `A=0` boundary, `det(R_a-4I)=52/3`, so only the highest numerator `P4` must be tangent. With

```
T_r=r^2(r^6+1), T_v=r(2r^6+1)v-(3r^6+2),
q=T(A)/A=3r(r^6-1), tau4=div(T)-4q=-2r^7+15r,
```

write `P4=(T_r h4,T_v h4,k4)`. Each entry of `h4` has `r` exponents -10 through -6, `v` exponents 0 through 1, and `t` exponents 0 through 2. Each entry of `k4` has the full `B` support. Thus the necessary top sector has 294 coefficients. **All 2808 lower coefficients in P3, P2, P1, P0 remain unrestricted.** The next pole couples `P3` to the top operator; no earlier secondary tangency or divisibility condition is imposed.

The safe necessary family has 3102 coefficients, compared with 3510 original generators. Its complete equation is multiplied by `A^4`. The top contribution is

```
W4=[T_r partial_r+T_v partial_v+tau4 I
      +q A M_a+t T_v M_b]h4+(partial_t+N_t)k4.
```

For each lower `Pj`, `j=3,2,1,0`, the columns are

```
A^(4-j)(partial_i+N_i)u-j A^(3-j)A_i u,
```

with scalar derivative corrections in the matching compact row and `A_t=0`. The source column is `A^4 S`. Both rows, all physical derivatives, and all cross-sector cancellations are retained.

## Executed independent check

The fixed specification arrived before the Pro numerical result: prime 65521, Python `random.Random(2026102469)`, successive `randrange(1,p)` triples `(r,v,t)`, rejecting zero `A`, literal JSON `Delta`, or any connection denominator. The author specifies 1580 accepted triples and 3160 rows, row 0 then row 1. This checker reconstructed the first **3103** rows using **1552** points, with only row 0 of the final point. It does not reconstruct the remaining 57 rows or 28 sample records.

Column order is `h4` (60), `k4` (234), `P3`, `P2`, `P1`, `P0` (702 each), then the positive source. Within each sector: direction where applicable, compact input row, then increasing `r,v,t` exponents.

All **9628609** entries were independently rebuilt using this checker's rational-polynomial evaluator, symbolic physical Jacobian, monomial derivatives and reduced tangent operator, reusing the sound A-cubed implementation. No Pro script was replayed. No candidate point was rejected; 783760 rational evaluation denominators were checked. The new `det(R_a-4I)`, `tau4` and abstract fourth reciprocal derivative controls also passed.

Three deliberate operator mutations were detected at the first point:

| Mutation | Column | Correct | Mutant |
| --- | ---: | ---: | ---: |
| Use order-three tau | 0 | 32782 | 62509 |
| Use quotient factor 2 instead of 3 in P3 | 294 | 31853 | 45920 |
| Omit the P1 quotient derivative | 1698 | 65424 | 34023 |

These are local operator controls, not determinant checks of mutated matrices.

The determinant backend is exact `flint.nmod_mat.det`, through **python-flint 0.9.0**, not an independently authored elimination algorithm. Reconstruction including imports took 2.765 seconds; FLINT construction/determinant took 3.454 seconds. The subprocess took **6.438 seconds**. Its 58-second internal watchdog and 60-second outer bound did not fire. There was one mathematical run, no failed run, no timeout, no determinant rerun, and no exploratory search.

## Characteristic-zero implication and limits

Lift the fixed point coordinates to integers. All rational entry denominators are units modulo 65521, so the rational augmented determinant reduces to 28764 and is nonzero. Its 3103 columns are independent, while there are only 3102 coefficient columns. Consequently no constant rational coefficient vector solves these necessary evaluations. This closes the kernel issue directly; no inference from a deficient modular rank is used. Denominators of hypothetical unknown coefficients need not be units modulo 65521, because the proof uses a nonzero rational determinant rather than reducing an unknown solution.

Combining this with the highest-pole/support necessity excludes the original declared sum, and hence its pure `B/A^4` subfamily. Larger monomial supports, fifth or higher powers of `A`, other denominator divisors, arbitrary rational compact currents and fibre-dependent sextic functions remain outside this result.

## Provenance, files and reproduction

Repository parent read before execution: `a773c34804b3d0e1e6db2e1b6e31d89f3c3455cf`. Only this owned checker directory was written; no commit or push was made.

| Artifact | SHA-256 |
| --- | --- |
| Literal connection JSON | `a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d` |
| Reused structural report | `7493c4076b993709f51b15e612b2b102855887aba76d7907563addabfabf7af7` |
| Reused A-cubed mathematical report | `6c2ed5fc2d425e6c3121ffd481d21b742e335fad9c29754f7bb36f497fa57cfc` |
| Executed A-fourth-power script | `cefa9592c78c0ccb8b5c1d9ff5e6e6f8473410d43b19484e1fbf9ba013d17faa` |
| `A4-minor.json` | `c39d7b4ee6207b1ca65f0c545bfd7925d7fc847a1b9ea7cf987d008e9dadb36d` |
| `regenerated-inputs.json` | `4f74073f8b69930cb46ecf2a4f787d33876edca3c778dbdd7ed276d9b17da893` |
| `regenerated-minor.npy` | `8a79cf56d9f01acd1e09e14a8e6b0d7a40db6f945288fb04a0a89008be54efc3` |

`A4-minor-receipt.json` binds the exact command, raw UTF-8 stdout/stderr bytes, outputs and runtime. The saved matrix is little-endian uint16, **19257346 bytes**, independently generated rather than copied from Pro. No duplicate text CSV is stored here. If omitted from a publication, disclose the omission; the script regenerates its exact bytes.

Run in a copy to preserve the frozen evidence, using Python 3.11.9, SymPy 1.14.0, NumPy 2.4.6 and python-flint 0.9.0:

```powershell
python audit_A4_regenerated_minor.py --connection 'C:/path/to/source-rank2-connection.json' --prior-structure 'C:/path/to/structure-independent.json' --prior-A3-report 'C:/path/to/A3-minor.json' --prime 65521 --seed 2026102469 --author-points 1580
```

At this freeze, delivered-matrix comparison is **pending and not performed**. `bind_delivered_packet.py` is prepared but unexecuted. It accepts CSV, CSV.gz, NPY or NPZ and requires hashes of the delivered files before reading them. For multi-array NPZ files, specify `--matrix-key`. A later execution must have a separate binding report/receipt; it performs I/O comparison only and does not repeat mathematics.

```powershell
python bind_delivered_packet.py --matrix 'C:/path/to/augmented-matrix.npy' --inputs 'C:/path/to/inputs.json' --matrix-sha256 DELIVERED_FILE_SHA256 --inputs-sha256 INPUTS_SHA256
```

For CSV.gz, `--matrix-sha256` refers to the compressed file; optionally also pass `--uncompressed-csv-sha256`. The complete local freeze inventory is `freeze-manifest.json`.

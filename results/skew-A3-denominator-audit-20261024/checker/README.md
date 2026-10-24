# Independent A-cubed checker

The fixed **2401 by 2401** augmented minor was independently reconstructed and has exact determinant **13752 modulo 32003**. This excludes the declared finite six-component family `B+B/A+B/A^2+B/A^3` over the rationals. The mathematical child finished in **4.453 seconds**, with three quotient/order mutation controls detected. No primitive, homogeneous certificate, Lean proof, or full-target solution is claimed.

The minimum new order-three controls separately passed in **8.359 seconds**. Prior source/divisor/support evidence is reused. The matrix specification was supplied before the Pro result, and this checker performed no exploratory point or minor search. The independent mathematical report is frozen; delivered-CSV binding, when available, is recorded separately.

**Delivery status at this freeze:** the Pro CSV has not been received, so no delivered-matrix comparison has been performed. The prepared `bind_delivered_packet.py` is unexecuted. Pro's announced full-matrix hashes and rank report remain separate from this independently executed fixed-minor check. The absent CSV does not affect the independently reconstructed nonzero minor. A later successful I/O-only binding must have its own report and receipt.

The declared scalar space is

```
B = span_Q{r^m v^n t^k : -10<=m<=2, 0<=n,k<=2},
A = r^3+r^-3+(vr-1)^6/r^15.
```

The initial family has all six entries of three rank-two physical fluxes in `B/A^3`. The tested containing sum is `B+B/A+B/A^2+B/A^3`. This `A(r,v)` is the cubic coefficient and must not be confused with the protected homogeneous source `X0^3 Y0^3`.

The physical equation retains both fibre rows and all derivatives, with source `r^-4 M_b e0/12` in the pinned positive orientation and connection `(A_r M_a, A_v M_a+t M_b, N_t)`, where `N_t=v M_b+(1-3t^2)M_c/7+6t^5 M_d`.

## Only new order-three identities are checked

`check_order3_controls.py` verifies

```
partial_i(A^-3) = -3*A_i/A^4,   A_t=0,
det(R-3I)=10,
tau3=div(T)-3q=r^7+12r.
```

It differentiates `r^45/(r^18+r^12+(vr-1)^6)^3`. At `(r,v,t)=(1,2,1)`, the correct `r` and `v` derivatives are `1/9` and `-2/9`; incorrectly using coefficient 2 gives `2/27` and `-4/27`. Both mutations are detected.

The residue matrix, tangent vector, divisor, and exact support theorem are reused from the prior independently checked report:

```
R = [[0,-c/(6b)],[0,-1/3]],
T_r=r^2(r^6+1),
T_v=r(2r^6+1)v-(3r^6+2),
q=T(A)/A=3r(r^6-1).
```

No prior source/chart/trace/tangency/support calculation is rerun. The source JSON bytes and prior report hash are checked again for binding.

## Highest-pole necessity and lower mixed freedom

For the highest numerator `P3`, the `A^-4` coefficient is

```
(R-3I)(A_r P3_r+A_v P3_v).
```

Invertibility forces only `P3` tangent modulo `A`. The earlier complete support theorem gives

```
P3_r=T_r*h3, P3_v=T_v*h3, P3_t=k3,
```

where each entry of `h3` has `-10<=m<=-6`, `0<=n<=1`, `0<=k<=2`, and each entry of `k3` is in the full `B`. This gives 294 necessary parameters for the pure family. The full top-sector divergence is

```
A^-3 [T_r*h3_r+T_v*h3_v+(r^7+12r)*h3
       + q*A*M_a*h3+t*T_v*M_b*h3+(partial_t+N_t)k3].
```

For the containing sum, the next coefficient is `H3+(R-2I)W2=0` on `A=0`, where `W2` is the normal flux of the lower `P2` numerator. The script checks a formal coefficient example `H3=(2,0)`, `W2=(1,0)` satisfying this equation with `W2` nonzero. This is a demonstration of coupling, not a global bounded current.

Therefore lower `P2` must remain unrestricted unless a new coupled theorem proves otherwise. The earlier A-squared secondary projection or tangency conditions cannot simply be transferred to it. The safe joint necessary family has **2400** coefficients: top 294 plus three unrestricted lower sectors of 702 each. The original sum has 2808 generators. No injectivity of the differential operator is assumed.

The independent reconstruction multiplies the equation by `A^3` and uses

```
top tangent: the tau3 bracket above without A^-3,
P2 columns: A*(partial_i+N_i)u-2*A_i*u,
P1 columns: A^2*(partial_i+N_i)u-A*A_i*u,
P0 columns: A^3*(partial_i+N_i)u,
source: A^3*r^-4*M_b*e0/12.
```

Scalar derivative corrections occur in the matching fibre row. The nonzero 2401-square augmented minor closes the rank issue directly: its 2401 augmented columns are independent, and there are only 2400 coefficient columns. No assumption about an unknown operator kernel or inference from a deficient modular rank is used.

## Fixed reconstruction and exact determinant

`audit_A3_regenerated_minor.py` uses Python's `random.Random(2026102458)`. Coordinates are successive `randrange(1,32003)` triples `(r,v,t)`. Points with zero `A`, literal JSON `Delta`, or a connection denominator are discarded. None of the first 1201 candidate points needed rejection. All rational coefficient and evaluation denominators are units modulo 32003; 606505 rational evaluation denominators were checked.

The author specification collects 1230 accepted points, with output row 0 then row 1 at each point. This check reconstructs only the **first 2401 rows**, thus the first 1201 points with only row 0 used at the last point. It does not reconstruct the remaining 59 rows or remaining 29 point records. Column order is `h3` (60), `k3` (234), `P2` (702), `P1` (702), `P0` (702), then the positive source. Within a sector, direction where applicable comes first, then compact input row, then increasing `r,v,t` exponents.

All **5764801** entries were built using this checker's rational-polynomial evaluator, symbolic physical Jacobian, monomial derivatives, and reduced tangent operator. The independent source computation is recorded in `A3-minor.json`; the complete basis and accepted points are in `regenerated-inputs.json`; the matrix is `regenerated-minor.npy` as little-endian unsigned 16-bit entries.

The determinant uses exact `flint.nmod_mat.det` through **python-flint 0.9.0**. It is not described as an independently authored elimination algorithm. Reconstruction took 2.422 seconds including imports; constructing the FLINT matrix and computing its determinant took 1.797 seconds. The process receipt records 4.453 seconds total. No Pro script was replayed.

At the first point, the check detects three deliberate mutations: using the order-two `tau` changes the first column from 11784 to 29744; using coefficient 1 instead of 2 in the `P2` quotient derivative changes column 294 from 3873 to 15906; omitting the `P1` quotient derivative changes column 996 from 28692 to 29839. These are local operator controls, not claims that a mutated full determinant vanishes.

For the characteristic-zero implication, lift the fixed sample coordinates to integers. Every rational matrix entry is defined and has denominator prime to 32003. The corresponding rational augmented determinant reduces to 13752, so it is nonzero. Thus no constant rational coefficient vector solves the necessary evaluations. Denominators of hypothetical unknown coefficients need not be prime to 32003: the argument uses a nonzero rational determinant, not reduction of a hypothetical solution. Combined with the highest-pole/support necessity, this excludes the entire declared original 2808-generator sum.

This result does not exclude larger monomial supports, fourth or higher powers of `A` in denominators, other denominators, arbitrary rational compact currents, or arbitrary fibre-dependent functions in the sextic field. It is not a certificate of the protected target's unsolvability.

## Provenance and limits

Observed repository pin: `2dff6afddab993a216ba3f262197ae69aeb9143a`. No shared-repository edit or commit was made.

| Artifact | SHA-256 |
| --- | --- |
| Connection JSON | `a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d` |
| Prior structural report | `7493c4076b993709f51b15e612b2b102855887aba76d7907563addabfabf7af7` |
| Executed control script | `998e485e82495c4f780b755bad570743f179ef75ff67edff1bb49bf3c29c9204` |
| `order3-controls.json` | `c0162a85b164906f02f16ef9d8091f320757192337141eb073ea2d0c89d93ca6` |
| Executed reconstruction script | `6a67d1eb51588910446e00de480fc5e170d13b51aaa5f94316f1268113a6acbc` |
| `A3-minor.json` | `6c2ed5fc2d425e6c3121ffd481d21b742e335fad9c29754f7bb36f497fa57cfc` |
| `regenerated-inputs.json` | `5d895b4f58fd3293068e19b7b9a27a0411ea57d4d42d54d5e12c24e605a3f51a` |
| `regenerated-minor.npy` | `4ac42e04498fa932c89b32a8e8b9943ae792ce6582a43b39dc5853f604e40298` |

Receipts are `order3-controls-receipt.json` and `A3-minor-receipt.json`, each with raw UTF-8 stdout/stderr files. The 58-second internal watchdog and 60-second outer limit did not fire in either run. The executed mathematical files are frozen. There were two successful mathematical child runs, no failed or timed-out mathematical runs, and no matrix rerun.

Reproduce in a copy to preserve the frozen files:

```powershell
python check_order3_controls.py --connection 'C:/path/to/source-rank2-connection.json' --prior-structure 'C:/path/to/structure-independent.json'
python audit_A3_regenerated_minor.py --connection 'C:/path/to/source-rank2-connection.json' --prior-structure 'C:/path/to/structure-independent.json'
```

Recorded environment: Python 3.11.9, SymPy 1.14.0, NumPy 2.4.6, python-flint 0.9.0. Both commands have their own 60-second outer subprocess bound and preserve timeout streams as raw bytes. Run the control script first because the reconstruction pins its report.

## Local array and publication payload

The frozen local `regenerated-minor.npy` has **11529730 bytes** and SHA-256 `4ac42e04498fa932c89b32a8e8b9943ae792ce6582a43b39dc5853f604e40298`. It is the independently built 2401-square minor, not a copy of Pro's 2460-row CSV. Include it with the publication while Pro CSV delivery remains pending if a saved numerical matrix is wanted. If omitted from a publication to avoid duplicate matrix storage, the manifest must mark that omission explicitly: the saved script reproduces the array, and the mathematical report and receipt retain its exact hash.

`publication-manifest.json` distinguishes the checked files, this local array, and the prepared but unexecuted binding script. `freeze-manifest.json` inventories the complete local frozen directory. Neither manifest claims a Pro CSV readback.

If the Pro payload later arrives, in a copy containing the frozen array run:

```powershell
python bind_delivered_packet.py --result 'C:/path/to/lead/sum-01/result'
```

The binder accepts `augmented-matrix.csv` or `.csv.gz`, optionally an explicit `--matrix` path. It requires the announced uncompressed CSV SHA-256 `81a5ac8ee1b82bf1e5149e06fe0389c67c6371a058b70f59a84dbfbe256de17b` and inputs SHA-256 `ffbb8171c6480c39960a60bb63e9d974fa4924999e8e536635061f1a512cec8a`. These hashes are author-reported until the binder actually executes.

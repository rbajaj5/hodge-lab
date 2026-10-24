# Frozen independent A-squared finite-family exclusion

Independent regeneration of the fixed **1699 by 1699 augmented minor** passed in **16.344 seconds**, with determinant **14098 modulo 32003**. Combined with the checked highest-pole reduction, this proves characteristic-zero exclusion of the declared full six-component family `V+V/A+V/A^2`, hence its requested subfamily `V/A^2`.

After the archive arrived, a separate **I/O-only comparison** passed in **0.547 seconds**: every entry of the delivered first 1699 rows equals the frozen regenerated minor, and its basis and sample/domain records match. No determinant or other mathematics was rerun for that comparison.

The minimum new pole-order-two controls passed separately in **2.875 seconds**. A genuinely new mixed next-pole projection passed in **1.047 seconds**, but that stronger reduction is **unused** in the decisive matrix. The matrix preserves all 702 lower-pole numerator coefficients and uses the safe 1698-parameter necessary family.

This is a finite-family exclusion. It does not exclude larger supports, higher pole orders, other denominators, arbitrary rational compact currents, or fibre-dependent sextic functions. It does not solve the full one-reflection-skew target or construct a homogeneous certificate.

The requested family allows each of the six physical flux components independently in `V/A^2`, where

```
A = r^3+r^-3+(vr-1)^6/r^15,
V = span_Q{r^m v^n t^k : -10<=m<=2, 0<=n,k<=2}.
```

The source remains `r^-4 M_b e0/12` in the positive packet orientation, and the physical connection remains `(A_r M_a, A_v M_a+t M_b, v M_b+(1-3t^2)M_c/7+6t^5 M_d)`. Both fibre rows and all three directions are retained.

## New controls and reused evidence

`check_order2_controls.py` proves the three generic identities

```
partial_i(A^-2) = -2*A_i/A^3,   A_t=0,
```

by differentiating `r^30/(r^18+r^12+(rv-1)^6)^2`. At `(r,v,t)=(1,2,1)`, the `r` and `v` derivatives are respectively `2/9` and `-4/9`; using coefficient 1 instead of 2 gives incorrect values `1/9` and `-2/9`. Both controls are rejected.

It reuses, by hash, the earlier independently checked residue matrix

```
R = Res_(a=0) M_a = [[0,-c/(6b)],[0,-1/3]]
```

and tangent vector

```
T_r = r^2(r^6+1),
T_v = r(2r^6+1)v-(3r^6+2),
q = T(A)/A = 3r(r^6-1).
```

The new checks show `det(R-2I)=14/3` and `div(T)-2q=r(4r^6+9)`. They do not rerun the old residue derivation, source/chart/trace checks, tangent-module proof, or support proof.

For a numerator `P2` of a pole-order-two current, the `A^-3` coefficient is

```
(R-2I)(A_r P2_r+A_v P2_v).
```

Consequently the prior exact tangent/support theorem applies to `P2` alone: `P2_r=T_r h2`, `P2_v=T_v h2`, with each entry of `h2` supported on `-10<=m<=-6`, `0<=n<=1`, `0<=k<=2`, and `P2_t` arbitrary in `V`. This is a necessary 294-parameter family. Its full divergence is

```
A^-2 [T_r*partial_r h2 + T_v*partial_v h2
       + r(4r^6+9)*h2 + q*A*M_a*h2 + t*T_v*M_b*h2
       + (partial_t+N_t)P2_t].
```

The generic locus and divisibility arguments are those of the pinned prior proof: `r!=0`, and the generic point of the irreducible smooth `A=0` divisor with `Delta!=0`.

## Lower poles must remain coupled

If the author extends the family to `V+V/A+V/A^2`, the first necessary reduction leaves **1698** coefficients: regular `V` contributes 702, unrestricted `V/A` contributes 702, and the tangent `V/A^2` sector contributes 294. The original sum has 2106 independent generators. Its independence follows by comparing the disjoint leading `v`-degree ranges of `A^2 P0`, `A P1`, and `P2` after multiplying by `A^2`.

The next coefficient, at `A^-2`, has the form

```
H2+(R-I)W1=0 on A=0,
W1=(A_r P1_r+A_v P1_v)|_(A=0),
```

where `H2` is the displayed order-two reduced bracket restricted to the divisor, with `A M_a` replaced by `R`. This equation does not separately imply `W1=0`. The script checks the formal local example `H2=(1,0)`, `W1=(1,0)`, which satisfies the displayed equation with nonzero `W1`. This is only a demonstration of coefficient coupling, not a constructed global current in the bounded family.

Any stronger reduction must prove this mixed next-pole equation and preserve all allowable solutions. Any modular exclusion must also handle kernels correctly: a nonzero augmented minor one larger than the entire coefficient count suffices; a deficient modular coefficient rank by itself supplies no characteristic-zero rank upper bound.

## New checked consequence of the mixed equation

`check_order2_projection.py` independently checks the author's next-pole handoff directly against the source JSON. It evaluates only the new second-row coefficients; it reuses the old normal-map remainder by hash. The second-row bracket has the form

```
W2_1 = [T_r*partial_r + T_v*partial_v
         + 2r^7+19r/2+(3r^6+2)/(2v)] h2_1
        + (partial_t-1/(2t))P2_t,1.
```

The lower-left entries vanish exactly, so the first fibre component does not enter this row. Write `h2_1=H0(r,t)+v H1(r,t)`. All terms have polynomial `v`-degree at most 2 except `(3r^6+2)H0/(2v)`.

With `x=rv-1`, `C=r^18+r^12`, and `F=x^6+C`, the exact inverse is

```
1/v = -r*(x^5-x^4+x^3-x^2+x-1)/(C+1) modulo F.
```

Consequently the `x^3` and `x^4` coefficients of `W2_1` are respectively `-mu H0` and `+mu H0`, where `mu=r(3r^6+2)/(2(C+1))` is a nonzero rational function. The prior exact normal-map remainder has support only in `x^0,x^1,x^2,x^5`. It was computed for `F_r P1_r+F_v P1_v`; the `A` normal map differs modulo `F` by the unit `r^-15`, so the two omitted projections remain zero.

The actual mixed equation is `W2_1-(4/3)Q1_1=0`, where `Q1` is the normal flux of the lower-pole numerator. Its two missing projections therefore force **H0=0**, or **h2_1 divisible by v**. This conclusion does not force `P1` to be tangent. It holds as a generic rational identity; no specialization to a zero of `mu` or `C+1` is used.

The safe necessary counts become **279** for the pure `V/A^2` family and **1683** for `V+V/A+V/A^2`: row 0 of `h2` retains 30 terms, row 1 retains 15 terms with `v` exponent exactly 1, and the two components of `P2_t` retain 234 terms. All 702 regular and all 702 lower-pole coefficients remain in the joint family. Other next-pole equations may impose additional conditions; none is silently assumed.

The deliberate control reverses the inverse-of-`v` sign; the remainder of `v*mutant-1` is then `-2`, so the wrong inverse is detected. This projection run completed in 1.047 seconds without timeout or watchdog termination.

## Decisive audit and normalization

The fixed author specification uses the entire equation multiplied by `A^2`. The independent regeneration constructs its columns as follows:

```
regular numerator: A^2*(partial_i+N_i)u,
lower-pole numerator: A*(partial_i+N_i)u-A_i*u,
order2 tangent numerator: the reduced tau2 bracket without A^-2,
order2 t numerator: (partial_t+N_t)u,
source: A^2*r^-4*M_b*e0/12.
```

Scalar derivative corrections occur only in the matching fibre component. The reconstruction uses a separately authored rational-polynomial evaluator, symbolic Jacobians of the physical coefficient map, symbolic monomial derivatives, the reduced order-two tangent operator, and normalized-pivot Gaussian elimination. No Pro script is executed, and no new matrix search is performed.

The explicit specification supplied during an archive-transfer delay is:

```
prime = 32003
random generator = random.Random(2026102432)
each coordinate = rng.randrange(1,32003)
discard a point only if A==0 or the literal JSON Delta==0
take first850 accepted points and first1699 output rows
row order = sample0-row0, sample0-row1, sample1-row0, ...
last column = source
```

Column order is `h2`, then `k2`, then `P1`, then `P0`. The `h2` sector runs fibre row `0,1`, `m=-10..-6`, `n=0..1`, `k=0..2`; the `k2` sector runs direction 2, fibre row `0,1`, and the full original monomial box; each of `P1,P0` runs direction `0,1,2`, fibre row `0,1`, and the original box. Counts are respectively 60, 234, 702, 702. In particular, all 15 row-1, `v^0` terms excluded by the optional projection remain present.

All **2886601 entries** are independently regenerated at **850 good points**. Every evaluated denominator and primality are checked. Two matrix controls are rejected at the first point:

| Deliberate error | Correct entry | Mutated entry |
| --- | --- | --- |
| Use `div(T)-q` instead of `div(T)-2q` | 21985 | 23385 |
| Omit the `-A_r*u` correction from a lower-pole column | 27030 | 4939 |

The determinant is computed directly on the regenerated minor. Its nonzero value closes the kernel issue without assuming injectivity beforehand: a 1699-column augmented matrix is independent, while there are only 1698 coefficient columns. At the integer lifts of the finite-field points, every rational input denominator is prime to 32003. The rational determinant thus reduces to 14098 and is nonzero in characteristic zero. The argument does not reduce hypothetical unknown coefficients modulo the prime, so their denominators do not invalidate it. The same rank obstruction persists after extending the characteristic-zero constant field.

The prior tangent/support proof and the new invertibility of `R-2I` show that this necessary family contains every possible solution in the original 2106-generator sum. The original family is therefore excluded, not just an arbitrarily selected smaller family.

`regenerated-inputs.json` preserves the complete basis, accepted and rejected points, and domain values. `regenerated-minor.npy` preserves the entire independently generated minor using exact unsigned 16-bit values; all entries are below 32003. The Gaussian calculation itself uses signed 64-bit arithmetic with checked product bounds. The report records both the saved-file hash and the canonical signed-64-bit matrix-byte hash.

At the time of the determinant execution, the Pro CSV had not arrived. Its report therefore correctly records an independently regenerated certificate from the explicit fixed specification without a delivered-CSV comparison. That executed report remains unchanged. The later `bind_delivered_packet.py` compares the frozen artifacts with the delivered data and records its own `packet-binding.json` and receipt. All 2886601 minor entries, all 1698 basis labels, and the first 850 sample/domain records agree exactly. The **remaining 59 matrix rows and 29 sample/domain records are outside this local comparison**; Pro's separately reported check of all 1758 rows has distinct provenance.

The original immutable archive and manifest hashes supplied by the coordinator were respectively `1c254f651668fc2633d338f848f0de8d45162d0c3fd1b80dc48ccde1f16c7d8c` and `17b551e448e42c7725ff440363c51d8214641bb427963b3b1fef4b5545965d8b`; archive verification belongs to the coordinator's separate receipt. The local binding hashes the delivered CSV and metadata directly.

## Provenance and reproduction

The observed repository pin was `fc4f38a338b47addf62d1bf699783302285378fe`. No repository edit or commit was made.

| Input or artifact | SHA-256 |
| --- | --- |
| Connection JSON | `a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d` |
| Prior `structure-independent.json` | `7493c4076b993709f51b15e612b2b102855887aba76d7907563addabfabf7af7` |
| Executed `check_order2_controls.py` | `87e5949e65800d6bdf1e69afc232232a9da1e8fa2665ffc88b6844b8ca65b514` |
| `order2-controls.json` | `4b6906e9e5423c4907ab1dd46f5fd919ad2d946455d3e0b0eeea7db77509d41f` |
| Executed `check_order2_projection.py` | `8f3687bc7fcd97c921eac284b0a64dd223b54c313dec35f9fd483220be790ed7` |
| `order2-projection.json` | `6b817d846079bcc39c792cc1ecc28fc5edc5259f20918f7542324a4143103d82` |
| Executed `audit_A2_regenerated_minor.py` | `e66b601251126a41ded6228236e4106ff8f7376c34a4daad833adaffad6ddc90` |
| `A2-minor.json` | `8794831226bc8be8134c1cf1faa67d8a38b5cf976266700fe830bcb3c858e7a9` |
| `regenerated-inputs.json` | `4fab5fc1d5aa57f120d3a772da05423dc93c094deefaa89c22c90f48e51002af` |
| `regenerated-minor.npy` | `7df9059c44de2ba802470f7388bad9d873783df942e4eda1a6d3d47e2bda7038` |
| Executed `bind_delivered_packet.py` | `3b762d5c835ca0a20f4c07808b1d3c18559cc28bd1ef67c2cb1707cc8d34dc55` |
| `packet-binding.json` | `8d9009acddfd6c2b127642364ac24f4fbb3bd0b9804516ff2ba898a8ad34fc3c` |
| Delivered `augmented-matrix.csv` | `28ec91d22fb0008e1519f28864a0a50a706dbc74dbcd8411c9bc4dca6805a6e7` |
| Delivered `inputs.json` | `21d60f4a9cdd180722f6b1aca76b55b813407c195c9af1144049cfdc222280c5` |

The receipt is `order2-controls-receipt.json`; logs are `order2-controls.stdout.log` and `order2-controls.stderr.log`. The process has a 58-second internal watchdog and a 60-second outer timeout. Neither fired. UTF-8 stdout and stderr are preserved as raw bytes; hashes use saved files. No failed attempt occurred in this minimum-controls run.

The second run has corresponding files `order2-projection-receipt.json`, `order2-projection.stdout.log`, and `order2-projection.stderr.log`, with the same bounds and byte-preservation rules. Both executed control sets are frozen.

The determinant run has files `A2-minor-receipt.json`, `A2-minor.stdout.log`, and `A2-minor.stderr.log`, with the same bounds. No timeout or watchdog fired. All three mathematical runs passed; no failed mathematical attempt occurred in this owned A-squared directory. Executed scripts, reports, logs, and receipts are frozen; only subsequent artifact-binding documentation may be added.

The I/O-only run has files `packet-binding-receipt.json`, `packet-binding.stdout.log`, and `packet-binding.stderr.log`. It also passed without timeout. `freeze-manifest.json` binds the exact byte lengths and SHA-256 hashes of every other file in this directory, including this README. The manifest excludes itself to avoid self-reference. The whole directory is frozen after that manifest is written.

Copy the directory before replaying to preserve the executed artifacts:

```powershell
python check_order2_controls.py --connection 'C:/path/to/source-rank2-connection.json' --prior-structure 'C:/path/to/structure-independent.json'
python check_order2_projection.py --connection 'C:/path/to/source-rank2-connection.json' --prior-structure 'C:/path/to/structure-independent.json'
python audit_A2_regenerated_minor.py --connection 'C:/path/to/source-rank2-connection.json' --prior-structure 'C:/path/to/structure-independent.json'
python bind_delivered_packet.py --result 'C:/path/to/skew-A2-denominator-20261024/lead/sum-01/result'
```

The determinant script also requires the frozen `order2-controls.json` beside it and verifies its hash. Recorded environment: Python 3.11.9, SymPy 1.14.0, and NumPy 2.4.6.

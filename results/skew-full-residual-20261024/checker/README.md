# Independent checks of the new complementary-beta family

This directory belongs to the full-residual batch with notebook parent
`84f294e0235c3fd4b5d4849e565536172a74329c`. Lean is benched. No older Q or
beta-current test is replayed here.

The only external algebra input is the public connection JSON, SHA-256
`a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d`.
The basis columns and coefficient connection use the pinned `d+N` convention.
The target in these checks is the already-established centered remainder R2.

Run from this directory, using Python 3 and SymPy:

```text
python check_complementary_row0.py --run --connection /path/to/source-rank2-connection.json
python check_complementary_operator_residue.py --run --connection /path/to/source-rank2-connection.json
```

Both scripts use explicit UTF-8 IO, a 60-second parent timeout, and a
58-second symbolic watchdog. Each successful wrapper writes a JSON report,
stdout/stderr log, and receipt binding the script, report, and log hashes.
The original expansion-heavy scalar prototype reached the watchdog; its
script and receipt are preserved as `prototype_row0_expansion.py` and
`prototype-row0-expansion-receipt.json`. That attempt is not evidence.

## Proposed explicit h does not cancel row zero

For `beta0 wedge L=da wedge dt`, the fixed-L current `Z=h beta wedge L`
has first output row `-D_v h`. Write the target row as

```text
R2_0 = alpha chi_vv + beta (v chi_v-chi)
alpha = (N_t[0,1]+v/(3a))/(36t)
beta  = M_b[0,0]/(108a)
chi = r^-3-v^3/3
```

The proposed
`h=-alpha chi_v-(v beta-alpha_v)chi`
leaves exactly `(alpha_vv-2beta-v beta_v)chi` in row zero. The derivative
subscripts are at fixed a,t and include the physical cover motion in chi.

At the allowed point `(r,v,a,t)=(1,2,3,1)`, the coefficient is
`2080045/9851046093`, and the row-zero remainder is
`-10400225/29553138279`. This proves generic nonvanishing without expanding
the entire multivariate coefficient. A reversed-current-sign control fails.
The final scalar replay took 1.156 seconds.

## Full operator for the explicit fixed L

Put `D=1+t^6`, `P=t^8-3t^6-3t^2+1`,
`J=(4-5t^2)/4`, and `U=7t(17+2t^2+14t^4-5t^6)/4`.
The polynomial Bezout relation is `cU+PJ=1`, with `c=t(1-t^2)/7`.
For `L=-7DJ da-3aU dt`, the current has first-row fluxes `(0,-h,0)`
and second-row fluxes `h Wtilde`, where

```text
Wtilde_a = -3atU
Wtilde_v = -v[7J(D-tD'/3)+2tU]
Wtilde_t = 7tDJ
qtilde = t[-3U+(49/6)D'J+7DJ']
```

Direct use of all entries of the pinned rank-two connection verifies the
full operator

```text
Div_N(Z) = (-D_v h,
            Wtilde_a D_a h+Wtilde_v D_v h+Wtilde_t h_t+qtilde h).
```

Here `D_a,D_v` include the cover derivatives. This is a check of the full
two-row operator for arbitrary h, not merely an evaluation of its first row.

## Residue obstruction to the entire fixed-L family

At `a=4,t=1`, `Delta=8(v^3+216)`, whose root `v=-6` is simple with
`Delta_v=864`. The scalar coefficients of the target row have residues

```text
Res alpha dv = 1/756
Res beta dv  = -1/2592
```

Consequently the target residue is `gamma/756-kappa/2592`, where
`gamma=chi_vv` and `kappa=v chi_v-chi` at that divisor point. No singular
connection matrix value is substituted. Instead, residues of its rational
entries are computed before restriction to the divisor.

The checker computes r_v and r_vv implicitly from f before reduction. Its
exact quotient arithmetic modulo the good prime 32003 yields a nonzero
degree-17 residue. The report stores the full coefficient vector. It also
verifies `gcd(f,f_r)=1` and invertibility of r and the scalar denominators.
A flipped-kappa-sign control fails; deliberately freezing r changes the
residue.

This is an exact characteristic-zero nonvanishing certificate: zero in the
characteristic-zero localized residue algebra would have zero image under
every reduction where all inverted factors remain units. All such factors
are checked at this prime. The monic polynomial and good gcd also prove the
characteristic-zero cover is etale at this specialization.

The argument does not specialize a hypothetical h. On `f_r Delta_v != 0`,
the simple-pole residue of the known target is a rational function on the
relative discriminant divisor over Q(a,t). Its allowed nonzero evaluation
proves it is not identically zero on at least one component. On each etale
branch a rational derivative D_v h has zero residue in the local parameter
`v-v0`. Therefore **no rational compact coefficient h on the degree-18
physical cover can make this fixed-L current solve centered R2**.

Precisely, the coefficient field here is
`K=Q(a,v,t)[r]/(f)`, equivalently `Q(r,v,t)` with `a=A(r,v)`.
The executed report's phrase "h in the full physical field" refers to this
compact coefficient field. It does not include arbitrary functions of the
fibre variables V or nu in the entire sextic function field. This scope
clarification leaves the hash-bound script, report, log, and receipt unchanged.

The operator/residue replay passed 11 scoped checks and one sign control in
1.547 seconds. This excludes only the stated fixed-L family. It does not
exclude general mixed currents, different complementary forms, or the target
problem. It supplies no full primitive, homogeneous certificate, Lean result,
or trace-free assertion for an arbitrary root-dependent h.

## Two subsequent two-row current representatives

These are separate tests, not reruns of Q, the earlier beta current, or the
fixed-L residue obstruction. They use the same base-field vectors alpha and
beta, now retaining both fibre rows.

For a direction `calD=Gv partial_v+Gt partial_t`, put
`Gamma=Gv N_v+Gt N_t`, `Mcal=(partial_v Gv+partial_t Gt)I+Gamma`,
`S=alpha/Gv`, and `T=(v beta-calD S-Mcal S)/Gv`. The current
`J_v=Gv(S chi_v+T chi)`, `J_t=Gt(S chi_v+T chi)` then has exact survivor
`chi[-beta-calD T-Mcal T]`. The generic formal identity and the full ordinary
point divergence are independently checked.

The first triangular handoff had an incorrect contraction. Its failed
script, log, and receipt are preserved as `failed_triangular_draft.py`,
`failed-triangular-draft.log`, and `failed-triangular-draft-receipt.json`.
The failure occurred before a candidate residual was accepted. The original
`check_two_row_ibp.py` is also that failed draft, not a passing checker.

Exactly one explicit repair supplied by the constructive lead was tested:

```text
K0=C^2-3tvD, w=C C'-2tvD', q=3D C'-2C D'
Gv=-tvw+3aq+2vK0, Gt=-2tK0
Gamma=[[3tw/2,-tq],[0,tw/2]]
```

`check_triangular_repair.py --run --connection /path/to/connection.json`
passed 13 scoped checks and one rejected connection-sign control in
3.297 seconds. At `(r,v,a,t)=(1,2,3,1)`, `Gv=-108/7`, `Gt=24`, and
the full two-row survivor is

```text
(-242298600715/34686091188, 255188727685/15416040528).
```

The unaffected v-only comparator sets `Gv=1,Gt=0`, hence
`T0=v beta-partial_v alpha-N_v alpha`, `J_v=alpha chi_v+T0 chi`,
and survivor `chi[-beta-partial_v T0-N_v T0]`.
`check_v_only_comparator.py --run --connection /path/to/connection.json`
passed 8 scoped checks and one rejected connection-sign control in
1.531 seconds. Its full survivor at the same physical point is

```text
(70505/312731622, -637135/1250926488).
```

The files `triangular-repair.json/.log`, `v-only-comparator.json/.log`, and
their corresponding `-receipt.json` files bind these executions. Coefficient
derivatives were evaluated by exact second-order rational jets before point
evaluation. Direct symbolic alpha derivatives cross-check the jets, including
all vv, vt, and tt derivatives in the triangular check. The physical chi_v
and chi_vv were independently derived using the moving cover root.

Both currents fail full cancellation. The triangular route introduces the
new Gv divisor; the v-only comparator avoids that divisor. Their final
coefficients lie in the base field and their root dependence is only chi,
so centering does transfer to their currents and survivors. This property
does not apply to arbitrary root-dependent multiplying coefficients.

These are tested representatives, not novel coverage or a newly discharged
ramification bottleneck: earlier source integrations already produced
representatives without f_r denominators. Neither point test excludes a
general mixed-current family. No further repair of this triangular family
was attempted after its nonzero survivor was found.

## Local coupled v-only compatibility is positive

The fixed-L exclusion must not be extended to arbitrary two-row v-only
currents. A separate check of the full matrix/source residues at
`a=4,t=1,v=-6` gives

```text
R = Res N_v dv = -(1/6)[[1,1],[1,1]]
eigenvalues(R) = 0,-1/3
Res R2 dv = s(1,1),  s=gamma/756-kappa/2592
(1,-1) Res R2 dv = 0
Z0 = -3s(1,1),  R Z0 = Res R2 dv.
```

Thus coupling supplies a regular leading current that matches the source
pole at this point. The scalar fixed-L family could not use that connection
contribution in its first row. This is point-local compatibility only: it
does not construct a rational v-only primitive or prove a generic-divisor
identity.

`check_v_only_local_compatibility.py --run --connection /path/to/connection.json`
passed 8 point-local checks and one sign control in 1.109 seconds. Its JSON,
log, and receipt are `v-only-local-compatibility.json/.log/-receipt.json`.
The previously checked moving-root residue and etaleness are cited by report
hash rather than recalculated. No all-sheet gcd computation was repeated.

## Separate generic residue-image certificate

The subsequent `check_generic_v_residue.py` establishes the generic extension
by universal polynomial identities, not by promoting the preceding point
test. For `B=Delta M_b`, `Delta_b=partial_b Delta`, and `H=bd-c^2/12`, it
checks

```text
tr(B)=-Delta_b/3, det(B)=Delta H,
B^2+(Delta_b/3)B=-Delta H I.
```

For each of the four source columns `(Delta M_b)e0`, `(Delta M_b)e1`,
`(Delta M_c)e1`, and `(Delta M_d)e1`, both `adj(B)` times the column and
`(B+Delta_b I/3)` times the column have zero polynomial remainder modulo
Delta. Thus on `Delta=0`, `Delta_v=t Delta_b!=0`, the coupled residue matrix
`C=B/Delta_b` has rank one and acts by -1/3 on the full target residue rho.
The regular leading data `Z0=-3rho+u`, with `u` in the kernel, are compatible.

This requires `a!=0`, `r!=0`, `f_r!=0` in characteristic zero, so the scalar
source densities are regular along the discriminant divisor. It does not
cover tangencies or ramification intersections. The pole eigenvalues exclude
positive-order current poles there, and the subsequent local formal recursion
has invertible matrices `nI+C` for every positive integer n. These are local
formal compatibility statements; global rationality remains unresolved.

Run `python check_generic_v_residue.py --run --connection /path/to/connection.json`.
The execution passed 13 generic polynomial checks and one rejected sign
control in 1.235 seconds. `generic-v-residue.json/.log/-receipt.json` preserve
the quotient polynomials and source/script/report/log bindings. No earlier
point calculation, cover gcd, Q identity, or beta-current check was repeated.

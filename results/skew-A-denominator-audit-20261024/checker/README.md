# Frozen independent check of the A-denominator family

The independent structural audit and decisive matrix audit both passed. The former establishes an exact **necessary reduction from 702 parameters to 294** for the six-component family `V/A`, or from 1404 parameters to 996 for the containing sum `V+V/A`. The latter reconstructs every entry of a **997 by 997 augmented minor**, obtaining determinant **26947 modulo 32003**. Together they prove that the declared full six-component sum family `V+V/A` cannot solve the pinned equation in characteristic zero. In particular, the requested `V/A` family is excluded.

This is a bounded-family exclusion. It does not exclude larger supports, higher powers of `A` in denominators, other denominators, arbitrary rational compact currents, or fibre-dependent sextic functions. It is not a solution of the full one-reflection-skew target or a homogeneous certificate.

Here

```
A = r^3 + r^-3 + (r*v-1)^6/r^15,
V = span_Q{r^m v^n t^k : -10 <= m <= 2, 0 <= n,k <= 2}.
```

All six scalar flux components are allowed independently. The ordinary physical connection is

```
N_r = A_r M_a,
N_v = A_v M_a + t M_b,
N_t = v M_b + (1-3t^2) M_c/7 + 6t^5 M_d,
```

and the full source is `r^-4 M_b e0/12` in the packet's positive orientation. These source conventions are reused from finished packet evidence. This check does not repeat the old chart, trace, source-normalization, or Laurent-family checks.

## Source and execution provenance

Connection file: `source-rank2-connection.json` in the public `one-reflection-skew-followup` packet.

Source SHA-256:
`a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d`.

The repository HEAD was read and matched the requested pin
`aa5a30dff2fd70994c48c484845981c141e77ef9` before the check. No repository edit or commit was made.

`check_structure_independent.py` is independently authored. It directly reads the pinned connection entries, constructs the residue matrix, and obtains the tangency remainder from physical derivatives of `F=r^15 A`. Its successful child process took **1.391 seconds**, with a 60-second outer limit and a 58-second internal watchdog. UTF-8 stdout and stderr are saved as their original raw bytes. Receipt hashes are computed from the files actually written, avoiding newline conversion differences.

Executed script SHA-256:
`a06659066130cfd06f48f9b6ae2063eca2c6a8e58861c561fa27dd7759eeb85e`.

Report SHA-256:
`7493c4076b993709f51b15e612b2b102855887aba76d7907563addabfabf7af7`.

The result files are `structure-independent.json`, `structure-independent-receipt.json`, `structure-independent.stdout.log`, and `structure-independent.stderr.log`.

`audit_joint_minor.py` is a separately authored local reconstruction, reusing the polynomial evaluator design from this checker's earlier completed Laurent audit. It reads the new packet data but does not execute either Pro script. It checks all **994009 entries** of the decisive first 997 rows, using 499 of the packet's 528 points. The remaining 59 rows of the 1056-row source matrix are not reconstructed here. It then computes the determinant using normalized-pivot Gaussian elimination. This run completed in **4.485 seconds**, exit 0, with neither watchdog nor outer timeout triggered.

Executed matrix-audit script SHA-256:
`610c0ebecbcca001cacea08b4029edc37131e2bd0c595ba759cce6a70f637b7b`.

Matrix-audit report SHA-256:
`d0003bc597bfd460936717a98d708fbc658e3acf95aaba2df1a310bc23ba0d9a`.

Matrix input SHA-256:
`dfd559995c74bf09fab0b74345a65672d80e0e19538e0b5db6c6393e5016babc`.

Basis/sample metadata SHA-256:
`1ba4cb45c4bfe2b750ae15eebc23e5ea3c8beb9376638172164d845a9eeebcb2`.

The result files are `joint-minor.json`, `joint-minor-receipt.json`, `joint-minor.stdout.log`, and `joint-minor.stderr.log`. Pro's lead execution and its separate checker remain distinct provenance; their run counts are not counted as local independent executions.

An earlier attempt, `check_quotient_controls.py`, tried 351 separate symbolic simplifications. Its **internal 58-second watchdog terminated it with exit 124**; elapsed wall time was 58.797 seconds. The original receipt's `timeout:false` means only that the outer 60-second subprocess timeout did not expire. It does not mean the attempt completed or passed. The original script, receipt, and empty raw stdout/stderr files are preserved unchanged. No report was produced. The later audit proves the three reciprocal derivative identities once and uses Leibniz for all monomials, so no exhaustive repetition is needed.

## Quotient rule and controls

For any monomial `u` in `V`,

```
partial_i(u/A) = (partial_i u)/A - u*A_i/A^2,
A_t = 0.
```

The audit differentiates `r^15/F` and compares with `-A_i/A^2` in all three coordinates. For the constant monomial at `(r,v,t)=(1,2,1)`, the exact derivatives are `1/3` in `r` and `-2/3` in `v`. Omitting either denominator derivative would give zero and is detected. The `A_v M_a` term remains in the physical connection; quotient differentiation does not replace it.

## Why the A-pole forces a tangent numerator

Write `J_i=P_i/A` with each entry of `P_i` in `V`. At the generic point of `A=0` with `Delta != 0`, the source and `M_b,M_c,M_d` are regular in `a`, while

```
R = Res_(a=0) M_a = [[0, -c/(6b)], [0, -1/3]],
det(R-I) = 4/3.
```

The coefficient of `A^-2` in the full divergence is therefore

```
(R-I) (A_r P_r + A_v P_v).
```

Its vanishing is necessary, and invertibility of `R-I` forces `A_r P_r+A_v P_v` to vanish modulo `A`, separately in both fibre components. This argument is generic on the divisor; it does not evaluate a singular connection matrix at an ordinary numerical point.

For completeness, set `w=(rv-1)/r^2`. Then

```
A = r^-3 (w^6+r^6+1).
```

The polynomial in `w` is Eisenstein at the prime `r^2+1` in `Q[r]`, since that prime divides `r^6+1` exactly once. Thus the divisor is irreducible on `r != 0`. The Fermat gradient shows it is smooth. The substituted `Delta` at `a=0` is a nonzero polynomial of degree 3 in `v`; it cannot vanish identically on the irreducible degree-6 divisor. The generic `Delta != 0` locus used above is consequently nonempty.

Explicit sign correction to earlier external handoff prose: the pinned JSON gives `Delta|_(a=0)=b^2*(4*b*d-c^2)`, not its negative. The matrix audit confirms this exact formula directly from the JSON. The generic-divisor argument is unchanged. Earlier executed reports, receipts, and logs have not been edited.

## Complete low-degree tangency calculation

Put `x=rv-1`, `C=r^12(r^6+1)`, and `F=x^6+C`. Write one fibre component as

```
P_r = p0+p1*x+p2*x^2,
P_v = q0+q1*x+q2*x^2,
E_i = p_i+r^2*q_i,
B = 6*r^11*(2*r^6+1).
```

Direct division of `F_r P_r+F_v P_v` by `F` gives the remainder

```
(6/r)*E0*x^5 + B*p2*x^2
  + (B*p1-6*C*E2/r)*x + B*p0-6*C*E1/r.
```

Over `Q(r,t)`, its vanishing forces

```
p2=0,
q0=-p0/r^2,
q1=(lambda*p0-p1)/r^2,
q2=lambda*p1/r^2,
lambda=(2*r^6+1)/(r^6+1).
```

Equivalently,

```
(P_r,P_v) = (T_r,T_v)*h,
T_r = r^2*(r^6+1),
T_v = r*(2*r^6+1)*v-(3*r^6+2),
T(A) = 3*r*(r^6-1)*A.
```

The audit verifies the remainder, its solution, the exact tangent identity, and `gcd(T_r,T_v)=1`. Coprimality in the Laurent polynomial UFD implies that `h` is a Laurent polynomial when both products are. The top `r` exponent of `T_r` is 8, giving `max_r(h)<=-6`; the unique trailing `r` term of `T_v` is `-2`, giving `min_r(h)>=-10`. The `v`-degree of `T_v` is 1, so `deg_v(h)<=1`. Since `T_r` is independent of `t`, its product also preserves the required `t`-exponent range `0..2`.

Thus every possible solution in `V/A` must have

```
J_r = T_r*h/A,
J_v = T_v*h/A,
J_t = P_t/A,
```

where `h` is a two-component vector with scalar support `-10<=m<=-6`, `0<=n<=1`, `0<=k<=2`, and `P_t` is an unrestricted two-component vector in `V`. This gives `2*30+2*117=294` parameters. These supports also suffice to keep all numerator components within the original box. They cancel the double `A` pole; the remaining equation still requires a full residual check.

For an independent reconstruction of eventual matrix columns, put `q=3r(r^6-1)`. The tangent part can be evaluated without differentiating quotient columns directly:

```
Div_D(T_r*h/A,T_v*h/A,0)
 = A^-1 [T_r*partial_r h + T_v*partial_v h
          + r*(7r^6+6)*h + q*A*M_a*h + t*T_v*M_b*h].
```

This follows from `T(A)=qA` and `div(T)-q=r(7r^6+6)`. The separate `t` part is `A^-1(partial_t P_t+N_t P_t)`. These are the forms used in the independent reconstruction, whereas the Pro lead used direct quotient differentiation.

The supplied matrix represents the entire equation multiplied by `A`. Accordingly, the audit uses the displayed tangent bracket without its prefactor `A^-1`, ordinary `partial_t+N_t` columns for `P_t`, original Laurent columns multiplied by `A`, and source `A*r^-4 M_b e0/12`. Every sampled `A` is nonzero, and multiplication by `A` is an equivalence of rational-function identities.

Its negative control omits the tangent denominator correction `-q*h`, changing `div(T)-q` to `div(T)`. At the first sample `(19366,2493,2152)`, row 0, column 0 changes from 846 to 357 modulo 32003, a nonzero difference of 31514. This deliberately incorrect operator is detected.

## Optional sum and kernel-aware certificate conditions

`V` and `V/A` have zero intersection: if nonzero `P,Q` in `V` satisfied `P=Q/A`, then `Q=A P` would have `v`-degree at least 6 over `Q(r,t)`, contradicting its degree bound 2. The sum therefore has 1404 independent scalar generators across six components. The single families are not nested. In the optional sum, the regular `V` part contributes at most a simple `A` pole, so the same double-pole condition restricts the quotient part alone; its necessary reduced family has `702+294=996` generators.

Independence of generators does not imply injectivity of their differential images. A modular coefficient/augmented rank gap alone is insufficient if the coefficient rank could increase in characteristic zero. A nonzero augmented minor of order one larger than the entire coefficient count is sufficient. If an exact kernel is used to reduce that count, its dimension and resulting characteristic-zero rank upper bound must also be certified, together with the nonzero augmented minor. An exact rational inconsistency certificate is another valid route. Unknown denominators in hypothetical constant coefficients do not invalidate a characteristic-zero argument based on a nonzero rational minor with good reduction.

Here the full 997-column augmented minor is nonzero, while there are only 996 coefficient columns, so that gate is closed directly. All evaluated denominators and the prime are checked. Lift the finite-field sample points to ordinary integers: the rational determinant at those lifts reduces to 26947, hence is nonzero over `Q`. Thus the source column is outside the span of the coefficient columns over `Q` and after any characteristic-zero constant-field extension. The argument never reduces hypothetical unknown coefficients modulo the prime. Combined with the independently checked necessary reduction, this excludes the entire original 1404-generator sum, rather than just an arbitrarily chosen smaller ansatz.

## Reproduction

Copy the directory before replaying to preserve frozen executed files and receipts. With Python and SymPy installed:

```powershell
python check_structure_independent.py --connection 'C:/path/to/source-rank2-connection.json'
python audit_joint_minor.py --packet 'C:/path/to/skew-A-denominator-20261024' --connection 'C:/path/to/source-rank2-connection.json'
```

The packet argument is the directory containing `lead/sum-01/result` and `checker/reduced-sum-01/result`. The local structural report is retained beside the matrix script and bound by its hash. Recorded environment: Python 3.11.9, SymPy 1.14.0, and NumPy 2.4.6. The earlier exhaustive watchdog-terminated attempt need not be rerun.

All scripts, reports, receipts, and raw logs are frozen after this README update. No further mathematical calculation or search is part of this handoff.

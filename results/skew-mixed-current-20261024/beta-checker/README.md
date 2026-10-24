# Independent canonical beta-current audit

This audits only the new beta-current candidate, not the earlier regular Q
construction. The earlier checker directory was not modified.

Use Python 3 and SymPy:

```text
python check_beta_candidate.py --run --connection /path/to/source-rank2-connection.json
python check_beta_poles.py --run
```

The first script uses the public connection JSON pinned by SHA-256
`a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d`.
No proposer code is imported. Both wrappers use explicit UTF-8 IO, a
60-second child timeout, and a 58-second internal symbolic watchdog.

Final successful runs:

- `check_beta_candidate.py`: 7 new exact checks and one rejected sign control;
  1.359 seconds. Results in `beta-check.json`, stdout/stderr in `beta-check.log`.
- `check_beta_poles.py`: 14 exact identity/pole checks; 17.766 seconds. Results
  in `beta-poles.json`, stdout/stderr in `beta-poles.log`.

## Canonical current and operator

Put `D=1+t^6`, `P=t^8-3t^6-3t^2+1`, `Q=t^8-5t^6-5t^2+1`.
The current `h beta wedge beta_0` is entirely in fibre row e1, with flux

```text
W_a = t P/(7D)
W_v = t v Q/(21aD)
W_t = t^2(1-t^2)/(21a)
q   = t(1-3t^2+2t^6-4t^8)/(21aD)
```

The first connection row vanishes exactly. The second row is
`Lh = W_a h_a + W_v h_v + W_t h_t + q h`.
On the physical cover it is
`Lh = (W_a-A_v W_v)h_r/A_r + W_v h_v|r + W_t h_t + q h`.

Take `chi=r^-3-v^3/3`, with `chi_v` differentiated at fixed a. Put
`E=W_a-A_v W_v`, `H=3aP-vA_vQ`, so `E=tH/(21aD)`. The candidate is
`h*=-A_v chi_v/(36t^2 E)`. Its three fluxes are

```text
J_a = -a P A_v chi_v/(12t^2 H)
J_v = -v Q A_v chi_v/(36t^2 H)
J_t = -D(1-t^2) A_v chi_v/(36t H)
```

At `(r,v,a,t)=(1,2,3,1)`, `A_r=-3`, `A_v=6`, `Delta=1036`,
`E=10/21`, `h*=7/2`. The scalar operator gives `Lh*=1`, whereas the centered
source is `chi_vv/(36t^2)=19/18`. The survivor is therefore exactly `e1/18`.

## Exact survivor after ramification cancellation

Write `p=A_v`, `z=A_r`, `u=A_vv`, `j=A_rv` and take all A derivatives at
fixed r or v as indicated by the indices. Define

```text
H_v = 3pP - (p+v u)Q
H_t = 3a P' - v p Q'
K = [p(2-5t^6+7t^8)-v Q u]/H
    + p[v Q H_v + tD(1-t^2)H_t]/H^2
```

Then the exact scalar survivor is

```text
S = 1/(36t^2) * (
      [9aP u/(H r^4) - 3pK/r^4 - 3aP v^2 j/H]/z
      - 6aP v/H + v^2 K
    ).
```

This proves cancellation of the third- and second-order A_r poles. The
remaining A_r pole is real: at v=2,t=1, the degree-18 numerator of A_r is
coprime to both the numerator and denominator of its survivor residue.

The H poles are also real. At v=2,t=1, H has a squarefree degree-18 numerator,
coprime to A_r. An exact leading-coefficient gcd check proves double H poles
in the survivor. The factored survivor has no explicit denominators a,
1+t^6, or Delta; after substituting the rational function A, its possible
support is r, t, A_r, and H.

The trade also reintroduces t poles: J has generic orders (-2,-2,-1), and
the survivor has order -2. At r=1,v=2 the coefficient of t^-2 in the survivor
is -47/6. These conclusions must not be combined with the earlier Q current's
t-regularity as if both improvements were simultaneous.

## Scope and superseded attempts

These results check a rational current subtraction with a nonzero survivor.
They do not solve the full source or provide a homogeneous certificate.
All exact identities use the packet orientation and pinned d+M connection.

No trace-free claim is made for this beta current or its survivor. Although
chi is centered, h* multiplies chi_v by the root-dependent factor A_v/E.
Centering alone therefore does not establish trace zero for J or the beta
remainder. The earlier Q/R2 argument used coefficients in the base field and
does not transfer here. The full compact source identity is valid without
any trace projection.

Two expansion-heavy attempts were stopped by the 58-second watchdog. Their
source snapshots and partial output are preserved as `prototype_beta_poles.py`,
`prototype-beta-poles.log`, `prototype_h_pole_expansion.py`, and
`prototype-h-pole-expansion.log`. They contribute no final check counts.
The final script avoids broad expansions by using formal A derivatives and
exact univariate gcd witnesses.

Provenance: independent parallel Codex checker; only the pinned public fqlx
connection and the proposed canonical beta-current formulas were inputs.

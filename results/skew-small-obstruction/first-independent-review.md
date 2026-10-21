# Independent review of the three-coefficient obstruction

This review uses the operator and protected polynomial stated in Hodge Lab
checkpoint 118. It does not replay the source transport, quotient derivation,
covariant jets, or companion reductions. The polynomial is independently
entered in a standalone exact sparse dictionary implementation using Python's
standard-library `Fraction`; no prior matrix or elimination code is imported.

Write `P7=7P`, `a=1+r^6+w^6`. The integer operator on a numerator `N` is

`M(N)=60 a grad(P7).N -72 P7 a div(N)+72 P7 N.grad(a)`.

For a component `j`, this is `A_j N_j+B partial_j N_j`, where
`A_j=60 a partial_j(P7)+72 P7 partial_j(a)` and `B=-72 P7 a`.
For any selected output monomial, the coefficient transpose therefore has
finite exact support: an `A_j` monomial of exponent `k` reads the numerator
coefficient at `target-k`; a `B` monomial reads it at `target-k+e_j`, weighted
by that exponent's `j`th coordinate. This directly exposes every possible
contribution, including all three base components.

## Verified degree-four statement

Let `n0=[1]N_U` and `n2=[t^2]N_U`. At total numerator degree at most four:

| Output coefficient | Value |
| --- | --- |
| `[rt^3]` | `60(n2-n0)` |
| `[U^2 w^12]` | `1260 n0` |
| `[U^2 w^12 t^2]` | `1260 n2` |

The right-hand side `35 U^2 a^2` has respective coefficients `(0,35,0)`.
Thus these equations require `n2=n0`, `n0=1/36`, and `n2=0`, a contradiction.
Equivalently `(3/5)[rt^3]+(1/35)[U^2 w^12]-(1/35)[U^2 w^12 t^2]`
annihilates the entire degree-four matrix and pairs to one with the source.
The checker applies the forward operator separately to all 280 monomial
columns, supplementing its coefficient-transpose derivation.

## Exact scope frontier of this particular certificate

The first selected coefficient, for arbitrary polynomial numerators, is

`60(n2-n0) - 504([Urt^3]N_U +2[r^2 t^3]N_r +[rwt^3]N_w +4[rt^4]N_t)`.

All four added numerator coefficients have total degree five. The two other
selected coefficient formulas above remain unchanged through degree five.
Consequently, at degree five the displayed dual is already nonzero on four
columns. For example, `N_r=r^2 t^3` pairs to `-3024/5`.

The numerator `N=(1/36,-5 r^2 t^3/3024,0,0)` satisfies all three selected
equations exactly. It is **not a primitive**: the full residual has
`[rt]=5/3`. This example establishes failure of the three-row contradiction
at degree five, not consistency of the complete degree-five system. No
degree-five matrix elimination was performed.

The three-row certificate cannot by itself validate inclusion of the
denominator derivative: omitting `72 P7 N.grad(a)` still gives the same
selected degree-four outputs. This is a limitation of these selected rows,
not an error in checkpoint 118's operator; that checkpoint uses separate
positive controls for denominator differentiation. Removing the first dual
term is detected immediately on constant `N_U`, with pairing `36`.

## Executed checks and bounds

Commands were executed twice, the second time after adding the constructive
degree-five selected-row control:

```sh
timeout 60s env PYTHONIOENCODING=utf-8 python -u \
  /workspace/scratch/b5ce893745f7/skew118-review/math/check_three_coefficient.py
```

- First execution: exit 0, 297 explicit requirements, internal runtime
  0.013887197 seconds.
- Final execution: exit 0, 299 explicit requirements, internal runtime
  0.015059487 seconds; same 280 degree-four columns plus two new scope checks.
- No timeout or failed execution. The two nested executions are not counted
  as independent proof coverage. The final JSON replaces the developmental
  JSON; both execution timings and scopes are retained here.
- Only standard-library exact arithmetic. The JSON records Python version.
- No comparison of companion-space degree bounds is established by this
  computation. That requires a checked change of representatives and tracking
  denominators and parameter degrees.

Credit fqlx for the existing quotient, residue, and companion formulation;
checkpoint 118 for the three-term certificate; this is an independent replay
and a concrete scope check, not a claim of new target coverage.

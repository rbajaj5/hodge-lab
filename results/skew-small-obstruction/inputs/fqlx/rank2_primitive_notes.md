# Exact rank-two primitive problem for one-reflection-skew

This is a verified reduction and explicit auxiliary correspondence. **It is
not a certificate.** The remaining rational divergence system is displayed
below. Its solutions would give legal certificate data after pullback and
denominator clearing; the bounded screens performed so far did not find one.

**Preferred chart:** the final section switches to `Y0=1`, where the source
coefficient is constant. Both charts are verified by the script. The universal
rank-two connection and exact-correction formulas are the same.

## 1. The fixed sextic and full density

Work on `Y1=1`, and put

\[
X_0=x,\quad X_1=rx,\quad X_2=wx,\quad Y_0=\alpha,\quad
Y_2=v,\quad U=x^2.
\]

Set

\[
a=1+r^6+w^6,\quad b=\alpha(r+r^3w),\quad
c=\frac{r\alpha(\alpha^2-1)}7,\quad d=\alpha^6+1,
\qquad P=aU^3+bU^2+cU+d.
\]

Then the exact protected equation is `F=P+v^6`. In the coordinate order
`(U,r,w,alpha,v)`, its complete source density is

\[
\frac{A\Omega}{F^2}
=\frac{\alpha^3U^2}{2F^2}
  dU\wedge dr\wedge dw\wedge d\alpha\wedge dv.
\]

Indeed the Jacobian of `(x,rx,wx,alpha,v)` with respect to
`(x,r,w,alpha,v)` is `x^2`, and `x^5 dx=U^2 dU/2`. The degree-two
map `x -> U` quotients the serving simultaneous sign change of all three
X coordinates. No source factor has been dropped.

Over `K=C(r,w,alpha)`, the curve

\[
C:\quad v^6=-P(U)
\]

has genus four when `a Delta != 0`, with

\[
\Delta=27a^2d^2-18abcd+4ac^3+4b^3d-b^2c^2.
\]

There are three finite branch points with ramification six and three points
above infinity with ramification two. Riemann--Hurwitz gives
`2g-2=-12+3*5+3=6`. The holomorphic differential basis is

\[
dU/v^3,\quad dU/v^4,\quad dU/v^5,\quad U\,dU/v^5.
\]

The source belongs to the primitive character `v -> zeta_6 v` with
eigenvalue `zeta_6`. Its compact-fibre de Rham subsystem has the two-element
basis

\[
\omega=(\omega_0,\omega_1)=(dU/v^5,U\,dU/v^5).
\]

This uses the full Jacobian/source character, not only the target monomial.

## 2. A completely explicit finite elliptic correspondence

Adjoin a solution of

\[
m^2=b-3a\beta,\qquad 2mn=c-3a\beta^2,\qquad
n^2=d-a\beta^3.
\]

It satisfies

\[
P=a(U+\beta)^3+(mU+n)^2.
\]

The parameter `beta` satisfies the division quartic

\[
3a^2\beta^4-4ab\beta^3+6ac\beta^2-12ad\beta+4bd-c^2=0.
\]

The incidence Jacobian in `(beta,m,n)` has determinant
`12a(n-beta*m)^2`, and

\[
\Delta=a(n-\beta m)^3\bigl(27a(n-\beta m)-4m^3\bigr).
\]

Thus this is a generically finite separable coefficient extension on the
stated dense open. After adjoining `a^(1/3)`, there is an exact map to the
fixed elliptic curve `E: X^3+Y^2=-1`:

\[
X=\frac{a^{1/3}(U+\beta)}{v^2},\qquad
Y=\frac{mU+n}{v^3}.
\]

Its action on the differential, including the sign from `v^6=-P`, is

\[
\frac{dX}{Y}
=-a^{1/3}\left(\frac m3U+n-\frac{2m\beta}{3}\right)
 \frac{dU}{v^5}.
\]

Two choices of `(beta,m,n)` give generically independent columns. For
example, at `P=U^3+1`, one choice is `(0,0,1)`, and a second has
`beta^3=4`, `m^2=-3 beta`, and `2mn=-3 beta^2`, with `m != 0`.
The resulting coefficient columns are independent. Hence the correspondence
serves the entire relevant rank-two character, not just a special source
line. This is an algebraic statement on a dense coefficient open; the
specialization is used only to prove the determinant is not identically zero.

The elliptic correspondence does **not** prove that the resulting forms on
the physical coefficient threefold have rational primitives. That is the
remaining obligation. In particular, rationality of the universal
coefficient parameterization `(a,beta,m,n)` does not prove rationality of its
pullback to the actual `(r,w,alpha)` coefficient family.

One can avoid `a^(1/3)` in every calculation by retaining the twist
`E_a: aX^3+Y^2=-1`. The corresponding column without `a^(1/3)` has the
rank-one connection `-(da)/(3a)`. The rational rank-two system below avoids
all coefficient extensions completely.

## 3. Exact Hermite reduction and connection

For every polynomial `R(U)`,

\[
d_U(R/v^5)=\frac{-P R'+(5/6)P'R}{v^{11}}dU.
\]

Define the following five-by-five polynomial matrix, whose columns are the
coefficients of `-P`, `-UP`, and the exact numerators for `R=1,U,U^2`:

\[
H=\begin{pmatrix}
-d&0&5c/6&-d&0\\
-c&-d&5b/3&-c/6&-2d\\
-b&-c&5a/2&2b/3&-7c/6\\
-a&-b&0&3a/2&-b/3\\
0&-a&0&0&a/2
\end{pmatrix},\qquad
\det H=\frac{125a\Delta}{216}.
\]

If `T=H^(-1)`, the complete universal Gauss--Manin matrices are

\[
M_a=\tfrac56 T_{0:2,3:5},\quad
M_b=\tfrac56 T_{0:2,2:4},\quad
M_c=\tfrac56 T_{0:2,1:3},\quad
M_d=\tfrac56 T_{0:2,0:2}.
\]

Indices here are zero based and upper endpoints are omitted. Columns index
the input differential; for a coefficient column `f`, the induced derivative
is `D_t f=partial_t f+M_t f`. The accompanying exact corrections are

\[
R_{t,j}(U)=\frac56\sum_{k=0}^2T_{k+2,e_t+j}U^k,
\quad(e_a,e_b,e_c,e_d)=(3,2,1,0),\quad j=0,1.
\]

Consequently the full relative identities, not just their cohomology classes,
are

\[
\partial_t\omega_j=\sum_i\omega_i(M_t)_{ij}
 +d_U(R_{t,j}/v^5).
\]

All entries and correction polynomials are recorded in
`rank2_primitive_system.json`. Their eight column identities and all six
curvature identities are checked by `rank2_primitive_system.py`.

The target reduces exactly as

\[
\frac{U^2dU}{v^{11}}=c_0\omega_0+c_1\omega_1+d_U(R/v^5),
\]

where

\[
c_0=\frac{27acd-12b^2d+bc^2}{5\Delta},\qquad
c_1=\frac{6a(3bd-c^2)}{5\Delta},
\]

\[
R=\frac{6d(9ad-bc)+6(3acd+2b^2d-bc^2)U+
12a(3bd-c^2)U^2}{5\Delta}.
\]

The connection determinant is particularly simple:

\[
\operatorname{tr}(M)=-\tfrac13d\log(a\Delta).
\]

The matrices have only first-order denominators in `a` and `Delta`.
At generic smooth points of either boundary component their residue
eigenvalues are `0,-1/3`. This statement concerns the displayed model on its
generic boundary; it does not assert that arbitrary singular intersections
or a compactification require no further analysis. The finite algebraic
trivialization above establishes finite monodromy of this subsystem.

## 4. The exact remaining rational system on three parameters

Pull back the connection to the protected coefficient map:

\[
\begin{aligned}
M_r&=6r^5M_a+\alpha(1+3r^2w)M_b+
       \alpha(\alpha^2-1)M_c/7,\\
M_w&=6w^5M_a+\alpha r^3M_b,\\
M_\alpha&=(r+r^3w)M_b+r(3\alpha^2-1)M_c/7+6\alpha^5M_d.
\end{aligned}
\]

A common connection denominator is `42a Delta` after substitution. This
records the poles of the operator and does **not** restrict the denominator
of a sought solution. In particular it is not a claim that the previously
excluded discriminant denominator will solve the original problem.

With residue convention `Res(dF/F wedge eta)=eta`, and base volume
`V=dr wedge dw wedge dalpha`, the double-pole source reduces to

\[
-\frac{5\alpha^3}{72}\frac{U^2dU}{v^{11}}\wedge V.
\]

Thus a sufficient exact primitive problem is to find arbitrary rational
columns `f_r,f_w,f_alpha` in `C(r,w,alpha)^2` satisfying

\[
\boxed{\sum_{t=r,w,\alpha}(\partial_t+M_t)f_t=g},
\qquad
g=\begin{pmatrix}
-\alpha^3(27acd-12b^2d+bc^2)/(72\Delta)\\
-\alpha^3a(3bd-c^2)/(12\Delta)
\end{pmatrix}.
\]

No low degree, pure character, fixed denominator, or zero quotient is imposed
in this formulation.

## 5. Absolute primitive reconstruction and legal trace

Let `rho_t=(R_{t,0},R_{t,1})/v^5`, pulled back using the coefficient-chain
rule to the three physical directions, and set `kappa=-5 alpha^3/72`.
If the displayed PDE is solved, the absolute rational three-form

\[
\Theta=-\sum_{t=r,w,\alpha}\omega f_t\wedge\iota_{\partial_t}V
 +\left(\kappa R/v^5-\sum_t\rho_t f_t\right)V
\]

satisfies the exact identity

\[
d\Theta=\kappa\,U^2dU/v^{11}\wedge V.
\]

The terms `rho_t f_t` are essential: they correct the passage from relative
Gauss--Manin identities to an absolute primitive. Directly dropping them
would leave unaccounted fibre-exact terms.

If a solution is instead found over any finite separable coefficient
extension `L/K`, normalized field trace descends it: differentiation commutes
with trace and every `M_t,g` is in `K`, so

\[
f_t^{\rm desc}=\frac1{[L:K]}\operatorname{Tr}_{L/K}(f_t)
\]

solves the same rational PDE. This gives legal finite trace without requiring
the final certificate coefficients to contain `a^(1/3)`.

The resulting primitive pulls back through the explicit `X`-sign quotient.
The standard local normal decomposition at `F_v=6v^5` then gives a rational
field regular at the generic point of `F=0`, whose certificate identity holds
modulo `F^2`; the quotient need not vanish. Homogenization with `Y1` and
denominator clearing give finite-degree homogeneous data in the original six
variables. The denominators used here are generically nonzero on `F=0`;
generic checks include `a Delta=27` at `r=w=alpha=0`. A completed solution
would still explicitly carry out and verify those clearing operations.

This rank-two PDE describes a sufficient compact-fibre construction. A
completely unrestricted certificate may use moving fibre poles and open-curve
residue extensions, so failure of this route must not be promoted to
unrestricted nonexistence.

## 6. Computation and limits

The exact verifier checks the protected coordinate equation and source,
the Hermite matrix determinant, all eight connection-column identities, six
curvature identities, the target reduction, the cubic/square incidence,
its Jacobian determinant, and the four parameter derivatives of the displayed
algebraic flat column.

The separate modular coefficient-matrix screen uses every monomial up to the
requested total degree in all six unknown component functions. It does not
impose extra parity. The screen is finite and reproducible. Its bounded
negative outcomes do not solve the unrestricted primitive problem.

## 7. Cleaner constant source on Y0=1

The parent agent identified the better source chart `Y0=1`. Write

\[
X_0=x,\ X_1=rx,\ X_2=wx,\ Y_1=t,\ Y_2=z,\ U=x^2.
\]

The coefficients now are

\[
a=1+r^6+w^6,\quad b=t(r+r^3w),\quad
c=rt(1-t^2)/7,\quad d=1+t^6.
\]

The sign of `c` must change; retaining the old sign would change the target
sextic. Since the omitted projective coordinate is `Y0`, the projective
volume has a minus sign. The full density and its reduced residue are

\[
-\frac{U^2}{2F^2}dU\wedge dr\wedge dw\wedge dt\wedge dz,
\qquad
\frac5{72}\frac{U^2dU}{z^{11}}\wedge dr\wedge dw\wedge dt.
\]

The preferred rational system is consequently

\[
\sum_{s=r,w,t}(\partial_s+M_s)f_s=
\begin{pmatrix}
(27acd-12b^2d+bc^2)/(72\Delta)\\
a(3bd-c^2)/(12\Delta)
\end{pmatrix},
\]

with

\[
\begin{aligned}
M_r&=6r^5M_a+t(1+3r^2w)M_b+t(1-t^2)M_c/7,\\
M_w&=6w^5M_a+tr^3M_b,\\
M_t&=(r+r^3w)M_b+r(1-3t^2)M_c/7+6t^5M_d.
\end{aligned}
\]

Use `kappa=5/72` in the absolute primitive formula of section 5. All
coefficient data for this preferred chart are in
`rank2_primitive_system_Y0.json`; its variable named `alpha` denotes `t`.

The precise bounded outcomes in this chart, using prime `1000003`, are:

| Rational coefficient ansatz | Coefficient rows | Unknowns | Augmented rank |
|---|---:|---:|---:|
| Every component polynomial of total degree at most 6 | 9982 | 504 | 505 |
| Every component `H/a`, with `deg H <= 6` | 15507 | 504 | 505 |

Because the augmented modular rank exceeds the total number of coefficient
columns, each computation supplies a nonzero augmented minor over the
integers and therefore excludes that exact bounded ansatz over `C` as well.
These statements do not exclude larger numerators, different denominators,
moving fibre poles, or the unrestricted certificate.

Reproduce with:

```sh
PYTHONPATH=/tmp/skew_math_deps python search_rank2_polynomial.py --chart Y0 --degree 6
PYTHONPATH=/tmp/skew_math_deps python search_rank2_polynomial.py --chart Y0 --degree 6 --denominator a
```

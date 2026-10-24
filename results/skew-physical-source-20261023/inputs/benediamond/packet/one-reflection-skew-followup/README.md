# A simpler physical cover for `one-reflection-skew`

**Status: a verified coordinate reduction, an explicit rational current, and
three precisely scoped negative results. No rational primitive of the full
three-direction equation, homogeneous certificate, or Lean solve is claimed.**

The starting point is the complete compact rank-two system in
[fqlx's discussion comment](https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19113830)
and its [replay packet](https://gist.github.com/fqlx/1d83052f07e2898ef493a52c86a2180b).
The full physical function field remains present below. The new base is
rational, and its degree-18 physical cover is independent of one base coordinate.

## 1. Source and conventions

On the chart `Y0=1`, put

\[
X_0=x,\quad X_1=rx,\quad X_2=wx,\quad Y_1=t,\quad Y_2=\nu,
\qquad U=x^2.
\]

The protected polynomial becomes

\[
\nu^6=-(a_0U^3+b_0U^2+c_0U+d_0),
\]

\[
a_0=1+r^6+w^6,\quad b_0=t(r+r^3w),\quad
c_0=rt(1-t^2)/7,\quad d_0=1+t^6.
\]

Write the fibre basis as \((dU/\nu^5,U\,dU/\nu^5)\), and let
\(\nabla=d+M\) be the pinned coefficient connection. Its columns index
the input basis. In the packet's global residue convention, the **raw** compact
source is

\[
B_0=\frac1{12}M_{b_0}e_0\,dr\wedge dw\wedge dt.
\]

This is not the remainder of an earlier current subtraction. The original
JSON uses `Y1=1`, `Y0=alpha`, and source
\(-\alpha^3M_b e_0/12\). Under \(t=1/\alpha\), the fibre basis gauge is
\(\operatorname{diag}(\alpha^{-3},\alpha^{-1})\), the source coefficient
becomes \(-\alpha^{-2}M_b e_0/12\), and
\(d\alpha=-\alpha^2dt\). This gives the displayed source and the displayed
sign of \(c_0\). The exact replay checks the whole connection transformation.

There is a harmless **global orientation choice**: standard projective
\(\Omega=\sum_i(-1)^iX_i\,dX_0\wedge\cdots\widehat{dX_i}\cdots\wedge dX_5\)
in the ordering \((X_0,X_1,X_2,Y_0,Y_1,Y_2)\), with the normal differential last,
gives the negative of the packet's source. All formulas here use the packet's
convention. Negating the source and current changes none of the solvability or
rank conclusions. `independent_peer_audit.py` derives this comparison from
the protected polynomial and verifies all eight fibre-reduction identities.

## 2. The simpler degree-18 physical cover

Change fibre and base coordinates by

\[
V=rU,\qquad v=r^{-1}+rw,\qquad w=(vr-1)/r^2.
\]

The new cubic coefficients are

\[
a=A(r,v)=r^3+r^{-3}+\frac{(vr-1)^6}{r^{15}},\qquad
b=tv,\qquad c=t(1-t^2)/7,\qquad d=1+t^6.
\]

Thus the physical function field over \(\mathbf Q(a,v,t)\) is given by

\[
\boxed{f(r)=r^{18}+r^{12}+(vr-1)^6-ar^{15}=0.}
\]

This polynomial has degree 18, is monic with constant term 1, and is
independent of \(t\). The rational map \(r\mapsto A(r,v)\) has degree 18,
so this change retains the full physical extension. Work on its generic
étale open; rational identities then hold in the full function field.

The fibre gauge is \(T=\operatorname{diag}(r^{-1},r^{-2})\). The old source
becomes \(r^{-3}M_b e_0/12\), and
\(dr\wedge dw\wedge dt=r^{-1}dr\wedge dv\wedge dt\). Since
\(f_r=r^{15}A_r\) on the cover, the complete source in the new base is

\[
\boxed{B=\frac{r^{11}}{f_r}\frac{M_b e_0}{12}
\,da\wedge dv\wedge dt.}
\]

The rank-two connection on this base is particularly small:

\[
N_a=M_a,\qquad N_v=tM_b,\qquad
N_t=vM_b+\frac{1-3t^2}{7}M_c+6t^5M_d.
\]

All universal matrices are evaluated at the displayed \((a,b,c,d)\).
The covering derivatives, which must also be retained, are

\[
r_a=\frac{r^{15}}{f_r},\qquad
r_v=-\frac{6r(vr-1)^5}{f_r},\qquad r_t=0.
\]

For an implementation over a rational base, the full trace-free basis is
\(e_i^{\mathrm{cov}}=r^i/f_r\), \(0\leq i\leq16\). Its two covering
connection matrices are computed by differentiating and reducing modulo
\(f\); its \(t\)-matrix is zero. Tensor with the rank-two connection above.
This gives an equivalent rank-34 rational system, with source only in covering
slot 11. Removing the scalar trace component of a current is legitimate
because the source has trace zero and trace commutes with the connection.
This trades the earlier rank-17 system on an algebraic CM base for a rank-34
system on this simpler rational base; it does not discard the physical cover.

## 3. An explicit current and the exact remaining source

The elementary codifferent identities are

\[
\frac{r^i}{f_r}=
\partial_a\left(\frac{r^{i-14}}{i-14}\right)\quad(i\ne14),
\qquad \frac{r^{14}}{f_r}=\partial_a\log r.
\]

The exceptional slot is genuinely logarithmic: at fixed \(v\), its
one-form is \(dr/r\), with residue 1 at \(r=0\). In particular, these
scalar identities do not by themselves integrate the rank-two twisted source.

Nevertheless the exact universal identity \(M_a e_0=M_b e_1\) gives a
short two-stage reduction. Let \(\psi=r^{-3}\), and take all its derivatives
at fixed new base coordinates. Define the rational current by its three fluxes

\[
X_a=\frac{\psi_v}{36t}e_0,\qquad
X_v=-\frac{\psi_a}{36t}e_0-\frac{\psi_v}{36t^2}e_1,\qquad X_t=0.
\]

Then, with \(\Xi=X_a\,dv\wedge dt+X_v\,dt\wedge da\),

\[
\boxed{
B=\nabla\Xi+
\frac{\psi_{vv}}{36t^2}e_1\,da\wedge dv\wedge dt.
}
\]

This is an actual rational current subtraction. The entire remaining source
has one fibre coordinate, and its scalar density separates as a rational
function of \((a,v,r)\) times \(t^{-2}\). It remains nonzero. In particular,
the remaining problem is the full twisted equation for this one-row source;
simply treating \(e_1\) as constant would lose the period connection.

For direct evaluation,

\[
\psi_{vv}=12r^{-5}r_v^2-3r^{-4}r_{vv},\qquad
r_{vv}=-\frac{f_{vv}+2f_{rv}r_v+f_{rr}r_v^2}{f_r}.
\]

The replay also proves a useful universal identity. With

\[
\beta=\begin{pmatrix}
dc-\frac c3d\log a-\frac{2c}{3}d\log d\\
db-\frac{2b}{3}d\log a-\frac b3d\log d
\end{pmatrix},
\qquad \nabla\beta=\frac16d\log d\wedge\beta.
\]

Consequently \(\beta/D\) is covariantly closed on \(D^6=d\).
This supplies a smaller ansatz for future currents, but no completeness or
exactness claim for that ansatz is made here.

## 4. Complete obstruction to a primitive in the new r direction

Fix generic \((v,t)\) and ask for a rational vector \(h(r)\) satisfying

\[
h_r+A_rM_a h=r^{-4}M_b e_0/12.
\]

This includes arbitrary new rational poles in \(r\). A local pole argument
gives a complete finite search:

* At a finite root of \(A\) or \(\Delta(A,b,c,d)\), the connection has a
  simple pole with residue eigenvalues \(0,-1/3\), and the source has at
  most a simple pole. A pole of order \(k\geq1\) in \(h\) would contribute
  leading coefficient \((R-kI)h_{-k}\); this is nonzero. Such poles are impossible.
* At every other finite nonzero point the connection and source are regular,
  so the derivative of a proposed pole cannot cancel. Thus no new support
  at such a point helps.
* At \(r=0\),
  \[
  rA_rM_a\longrightarrow
  \begin{pmatrix}5&0\\-5c/(6d)&10\end{pmatrix},
  \]
  while the source is \(O(r^{11})\). A pole can have order at most 10.
* At infinity,
  \[
  rA_rM_a\longrightarrow
  \begin{pmatrix}-1&0\\c/(6d)&-2\end{pmatrix},
  \]
  and the source is \(O(r^{-7})\). If the polynomial part of \(h\) had
  degree \(m>2\), its leading coefficient would be killed by
  \(mI+R_\infty\), which is invertible. Its degree is therefore at most 2.

Every rational solution is consequently in the 26-dimensional space
\(h_j=\sum_{k=-10}^{2}h_{jk}r^k\). At \((v,t)=(2,3)\), the degree-18
numerator of \(A\) and the degree-36 numerator of \(\Delta\) are squarefree,
coprime, and nonzero at zero, so the stated generic local situation holds.
Clearing denominators gives a 133-by-26 exact coefficient system. Modulo
32003 its coefficient rank is 26 and its augmented rank is 27.

This proves inconsistency in characteristic zero, and also over the generic
parameter field: the nonzero 26-column minor at this specialization makes any
hypothetical generic solution regular there by Cramer's rule. There is no
specialization-pole loophole. **An arbitrary rational current confined to this
single direction cannot solve the compact equation.** This says nothing
against a current using two or three physical directions.

The finite-pole eigenvalues follow from exact universal identities, also
checked in `vertical_r_test.py`:

\[
\left.aM_a\right|_{a=0}=
\begin{pmatrix}0&-c/(6b)\\0&-1/3\end{pmatrix},
\]

\[
\operatorname{tr}(\Delta M_a)=-\frac{\Delta}{3a}-\frac{\Delta_a}{3},
\qquad
\det(\Delta M_a)=\frac{\Delta(216ad^2-36bcd+7c^3)}{36a}.
\]

At a simple discriminant root the residue is
\((\Delta M_a)/\Delta_a\), hence has trace \(-1/3\) and determinant zero.
The squarefreeness and coprimality checks ensure that pullback to the finite
roots in \(r\) is unramified there. Thus the argument covers every such
root, not just a sample residue matrix.

## 5. The new one-row residual also requires more than the r direction

The obstruction in Section 4 concerns the original source. It does not settle
whether the residual from Section 3 has an \(r\)-direction primitive: the
current already subtracted there has a \(v\)-component. The residual can be
tested separately and completely.

Its density in \((r,v,t)\) is
\(A_r\psi_{vv}e_1/(36t^2)\), with \(v\)-derivatives of \(\psi\) still taken
at fixed \(a\). This scalar density has an explicit ordinary rational
primitive. Put

\[
K=-\frac{15v^4}{2r^{12}}+\frac{360v^3}{13r^{13}}
-\frac{270v^2}{7r^{14}}+\frac{24v}{r^{15}}-\frac{45}{8r^{16}},
\qquad
H=\frac{\psi_rA_v^2}{A_r}+K.
\]

The exact identities are

\[
\boxed{H_r=A_r\psi_{vv},\qquad
L:=A_rH=\psi_rA_v^2+A_rK.}
\]

Here \(\psi_r=-3r^{-4}\), and \(L\) is Laurent in \(r\). One direct
derivation is

\[
A_r\psi_{vv}=\partial_r(\psi_rA_v^2/A_r)-\psi_rA_{vv},
\qquad K_r=-\psi_rA_{vv}.
\]

Consequently subtracting the actual vector primitive candidate
\(H e_1/(36t^2)\) leaves the full twisted source

\[
\boxed{-\frac{L}{36t^2}M_a e_1.}
\]

This subtraction removes all poles arising from zeros of \(A_r\): the factor
\(A_r\) in the connection cancels the denominator in \(H\). At every finite
nonzero point the remaining equation therefore has the same pole restrictions
as Section 4. At zero its source has order \(-17\), so a rational solution's
pole order is at most 16. At infinity the source is \(O(r^{-13})\), and the
polynomial degree remains at most 2. Thus **every** rational solution of the
remaining twisted equation belongs to Laurent powers \(-16,\ldots,2\) in
both rows, a 38-dimensional space.

At the same good specialization \((v,t)=(2,3)\), the exact cleared system is
145-by-38. Modulo 32003 its coefficient rank is 38 and its augmented rank is
39. The full-column-rank specialization argument applies again. Therefore
the new residual itself has **no rational primitive confined to the
\(r\)-direction**, equivalently the \(a\)-direction at fixed \((v,t)\).
This is a new test with the actual twisted operator, not a consequence
asserted from the original-source obstruction. A successful continuation must
use the other base directions as well. The explicit \(H\) and Laurent \(L\)
give a further exact reduction that such a continuation may use.

## 6. A separate bounded exclusion on the original chart

The original-coordinate ansatz \(x_i=P_i/a_0\), with both fibre rows, all
three fluxes, and total numerator degree at most 9, is also inconsistent.
Average by \((r,t)\mapsto(-r,-t)\): the \(r,t\) flux numerators are odd and
the \(w\) flux numerators even. This leaves 660 coefficients.

The modular coefficient and augmented ranks are 659 and 660. An independently
checked nonzero exact kernel gives characteristic-zero coefficient rank at
most 659. Hence the rank jump proves a characteristic-zero exclusion for
this entire bounded ansatz. The kernel is the current
\(\alpha\wedge dt/t\), where
\(\alpha=(dc-c\,d\log(a_0)/3,\ db-2b\,d\log(a_0)/3)^T\).
Its six explicit polynomial numerators are in the replay receipt.

Unlike the one-direction result above, this is only a bounded denominator and
degree result. It does not bound all rational three-direction currents and
does not exclude additional supports or higher numerators.

## Replay and provenance

The package is self-contained. It requires Python, SymPy, and python-flint;
the tested dependency versions are pinned in `requirements.txt`.
Run, in any working directory:

```sh
python /path/to/skew_constructive/simple_cover_verify.py
python /path/to/skew_constructive/vertical_r_test.py
python /path/to/skew_constructive/residual_vertical_r_test.py
python /path/to/skew_constructive/independent_peer_audit.py
```

`simple-cover-report.json` records the coordinate maps, connection, exact
current, and 55 rational-identity checks. `vertical-r-report.json` records the
complete one-direction test. `independent-peer-audit.json` records the
independent source reduction, exact polynomial kernel, and modular bounded
search. `a_denominator_search.py` is the underlying degree-bounded search;
its modular output alone is deliberately not labeled a characteristic-zero
exclusion until the exact kernel audit is included.

`residual-vertical-r-report.json` separately records the rational ordinary
primitive, the exact remaining twisted source, and the complete 38-coefficient
test for the new residual.

The pinned connection SHA256 is
`a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d`;
the protected target SHA256 is
`fc7e070e4f459a521e3515c3b0d7e85fe4a557e345839f9cdb324491c289063f`.
Their verbatim inputs, plus the repository's parsed record, are under `inputs/`.

The new coordinate reduction, currents, and tests were developed with ChatGPT
on behalf of `benediamond`, including independent exact checks by parallel
agents. The starting compact connection, source reduction, and prior physical
and scalar formulations are credited to `fqlx` and the linked discussion.

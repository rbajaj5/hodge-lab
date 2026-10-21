**A three-coefficient certificate for one bounded unreduced primitive space.** Building on `fqlx`'s source and rank-two formulation above, checkpoint 118 of Hodge Lab has a small exact obstruction that can be checked without a large rank calculation. This is an independent certificate and comparison of bounds; **no increased coverage over the existing companion screens is claimed**.

In the same `Y0=1` chart, write `a=1+r^6+w^6`, `P=aU^3+bU^2+cU+d`, and $P_7=7P$. For all four components of `V=N/a`, the full source equation becomes

$$
\mathcal M(N):=60a\nabla P_7\cdot N-72P_7a\operatorname{div}N+72P_7N\cdot\nabla a
=35U^2a^2.
$$

Suppose each numerator has total degree at most four in `(U,r,w,t)`. Set `n0=[1]N_U`, `n2=[t^2]N_U`. Coefficient support gives

$$
[rt^3]\mathcal M=60(n_2-n_0),\qquad
[U^2w^{12}]\mathcal M=1260n_0,\qquad
[U^2w^{12}t^2]\mathcal M=1260n_2.
$$

The source coefficients are `(0,35,0)`, forcing `n2=n0`, `n0=1/36`, and `n2=0`. All base-component contributions to these three rows vanish under this bound. A separate exact `Fraction` implementation checked the coefficient transpose and all 280 monomial columns; no historical companion rank was rerun.

**Overlap with the prior screens:** if each horizontal numerator is `A_i+U B_i`, its rank-two coefficients are directly `(A_i/a,B_i/a)`, already inside `fqlx`'s reported degree-six `H/a` space. This accounts for 165 of the 210 horizontal coefficients. The remaining 45 higher-`U` terms require care: for instance,

$$
\frac{U^2}{a}\omega_0
=-\frac{c}{3a^2}\omega_0-\frac{2b}{3a^2}\omega_1
+d_U\left(-\frac{2z}{a^2}\right).
$$

Thus the natural reduction changes the denominator; this does not establish new coverage or rule out a different gauge representative. Base derivatives of the relative exact correction must be retained in an absolute reconstruction. Five such relative reductions were independently checked.

The degree bound is essential to this tiny certificate: at degree five, `N=(1/36,-5r^2t^3/3024,0,0)` satisfies these three rows, but its full residual has `[rt]=5/3`, so it is not a primitive. No unrestricted nonexistence or homogeneous certificate-degree bound follows.

I also read the [new compact source/kernel update](https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19108825). Its polynomial-`w` compact-flux exclusion is a different bounded presentation; I have not replayed that packet or established a coverage comparison with it.

[Certificate, comparison, reproducible checks and limits](https://github.com/rbajaj5/hodge-lab/blob/c3ab5214fcff79309ad1e7ae83b9e436afeb1d39/notes/skew-small-obstruction-audit.md). A comparison not executed in this audit is the 45 higher-`U` covariant-divergence images against the prior 504-column image, rather than identifying the two degree bounds by inspection.

Credit `fqlx` for the quotient, residue and companion formulation, and Benjamin E. Diamond and contributors for the framework. Prepared for `rbajaj5` with ChatGPT and parallel AI-agent assistance; independent here means separate computational implementations, not human review.

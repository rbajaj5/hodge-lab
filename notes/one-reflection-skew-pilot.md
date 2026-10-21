# `one-reflection-skew`: denominators must have degree at least six, and a boundary check for the binary-cubic construction

For the fixed `one-reflection-skew` frontier target ($q = 1$, $A = X_0^3 Y_0^3$), the calculations below exclude **every nonzero homogeneous denominator of degree zero through five** over the complex numbers, including the complete numerator space and an unrestricted quotient $Q$. We also record the exact Kramers-like complex exchange symmetry of the interaction polynomial, the universal constant-coefficient Cramer identity for the deformed binary-cubic Nambu/Casimir flow, and the vanishing of a selected Cramer coefficient along $X_1Y_1=0$, without an established transport obstruction. This pilot does not test degrees six and higher; see the later [degree-six result](one-reflection-skew-degree6.md).

![Exact E1/E2 exclusion through degree five and deformed Nambu/Casimir phase portrait for one-reflection-skew](../results/one-reflection-skew-pilot/one-reflection-skew-audit.png)

**Audit correction, 21 October 2026:** the Hessian scale, exchange order, and boundary interpretation below supersede the corresponding statements in checkpoint 85. The low-degree exclusion is unchanged; this audit reran the symbolic identities, not its full elimination. [Evidence and limits](repository-audit-20261021.md).

## 1. Fixed target and symmetry breaking

Write $F_0 = \sum_{i=0}^2 (X_i^6 + Y_i^6)$. The target has $q = 1$, $A = X_0^3 Y_0^3$, and sextic

$$F = F_0 + (X_0^3 X_1 + X_1^3 X_2) Y_0 Y_1 + \frac{1}{7} X_0 X_1 Y_0 Y_1 (Y_0^2 - Y_1^2).$$

In the unperturbed companion target `one-reflection` (solved at degree $60$ in PR #123), the two hidden involutions $(Y_0, Y_1) \mapsto (\pm Y_1, \pm Y_0)$ act as a real parity doublet, splitting the density $X_0^3 Y_0^3$ into two half-targets $\frac{1}{2} X_0^3 (Y_0^3 \pm Y_1^3)$ served by a binary-cubic Hessian construction on $(u, p) = (X_0^2, Y_0 Y_1)$. Adding the skew quadrupole coupling $S = \frac{1}{7} X_0 X_1 Y_0 Y_1 (Y_0^2 - Y_1^2)$ breaks both real exchanges:

$$F(\pm Y_1, \pm Y_0) - F = -\frac{2}{7} X_0 X_1 Y_0 Y_1 (Y_0^2 - Y_1^2) \ne 0.$$

Two exact symmetry structures survive:
- **Discrete $\mathbb{Z}_2^3$ charge-parity subgroup:** Every mixed term of $F$ has parity $(-1, -1, -1, -1)$ on the four coordinate blocks $\tau_1: (X_0, X_2) \mapsto (-X_0, -X_2)$, $\tau_2: X_1 \mapsto -X_1$, $\tau_3: Y_0 \mapsto -Y_0$, and $\tau_4: Y_1 \mapsto -Y_1$. Every product of two of these blocks preserves $F$, alongside the decoupled reflection $\tau_{Y_2}: Y_2 \mapsto -Y_2$.
- **Complex exchange involution (order two):** The transformation $(Y_0, Y_1) \mapsto (i Y_1, -i Y_0)$ preserves both $Y_0 Y_1$ and $Y_0^2 - Y_1^2$, its square is the identity, and it leaves the entire interaction Hamiltonian $F - F_0$ invariant while inverting the Fermat kinetic block $Y_0^6 + Y_1^6 \mapsto -(Y_0^6 + Y_1^6)$.

## 2. Complete first-equation and degree-five Hessian exclusion

Let $J = (\partial_0 F, \dots, \partial_5 F)$ be the Jacobian ideal. Under Euler normalization, every certificate with denominator $D \in S_d$ satisfies $N(F) = A D$ with $\deg N_i = d + 1$, so $D$ must lie in the kernel of $D \mapsto [A D] \in S_{d+6} / J_{d+6}$.

| Degree $d$ | Denominator coefficients | Numerator coefficients | Numerator-map rank | Augmented rank | Denominator kernel |
| --- | ---: | ---: | ---: | ---: | ---: |
| 0 | 1 | 36 | 36 | 37 | 0 |
| 1 | 6 | 126 | 126 | 132 | 0 |
| 2 | 21 | 336 | 336 | 357 | 0 |
| 3 | 56 | 756 | 756 | 812 | 0 |
| 4 | 126 | 1512 | 1497 | 1623 | 0 |
| 5 | 252 | 2772 | 2682 | 2928 | 6 |

At degree five, the six-dimensional $E_1$ kernel is the gradient span $D = a \cdot \nabla F$, with $N = A a + K$ where $K$ ranges over the $90$-dimensional span of linear multiples of the $15$ Koszul fields $\partial_j F \partial_i - \partial_i F \partial_j$. Reducing the second equation $B_D(N) = D \operatorname{div} N - N(D) \equiv 0 \pmod F$ modulo $J_{10}$ gives

$$B_D(A a + K) \equiv -A \cdot a^{\mathsf{T}} \operatorname{Hess}(F) a \pmod{J_{10}}.$$

Unlike `cycle-three` and `mixed-biweight` (where the $21$-column quadratic Hessian map in $S_{10}/J_{10}$ has full rank $21$), here $Y_2$ enters $F$ only through $Y_2^6$, so the five mixed second partials $\partial_i \partial_{Y_2} F$ ($i < 5$) vanish identically and the $21$-column map has exact quotient rank **$16$ of $21$** ($49$ active rows). Nevertheless, all six diagonal square columns $a_i^2$ remain linearly independent of the off-diagonal columns in $S_{10}/J_{10}$: six exported rational dual functionals annihilate $J_{10}$ and isolate $a_0^2, \dots, a_5^2$ one at a time, forcing $a = 0$ and $D = 0$.

## 3. Binary-cubic identities and the passive-ratio boundary

For any general binary cubic $f(u, v) = c_0 u^3 + c_1 u^2 v + c_2 u v^2 + c_3 v^3$ with quadratic Casimir (scaled Hessian)

$$h(u, v) = \frac{1}{4}(f_{uu} f_{vv} - f_{uv}^2) = (3 c_0 c_2 - c_1^2) u^2 + (9 c_0 c_3 - c_1 c_2) u v + (3 c_1 c_3 - c_2^2) v^2,$$

the divergence-free Hamiltonian / Nambu vector field $H = h_v \partial_u - h_u \partial_v$ and cubic covariant $k = H(f)/3$ obey the exact identities

$$H(h) = 0, \qquad H(k) = 3\,\mathrm{disc}(h)\, f, \qquad \mathrm{disc}(h)\, f^2 - k^2 = \frac{4}{9} h^3,$$

where $\mathrm{disc}(h) = (9 c_0 c_3 - c_1 c_2)^2 - 4(3 c_0 c_2 - c_1^2)(3 c_1 c_3 - c_2^2)$. Moreover, the $3 \times 3$ coefficient matrix of the three homogeneous quadratics $(f_u, f_v, h)$ in the basis $(u^2, u v, v^2)$ has determinant $-\mathrm{disc}(h)$, so Cramer's rule supplies a universal identity with coefficients **constant in $(u, v)$**:

$$\mathrm{disc}(h)\, u^2 = L_u f_u + L_v f_v + L_h h(u, v),$$

$$L_u = 27 c_0 c_3^2 - 9 c_1 c_2 c_3 + 2 c_2^3, \quad L_v = 6 c_1^2 c_3 - 9 c_0 c_2 c_3 - c_1 c_2^2, \quad L_h = -2(3 c_1 c_3 - c_2^2).$$

At $c_2 = 0, c_3 = 2$, this specializes directly to the target decomposition $\delta u^2 = 108 \alpha f_u + 12 \beta^2 f_p - 12 \beta h$ used in `one-reflection`.

In the 3-passive-ratio chart $r = X_1/X_0$, $w = X_2/X_0$, $\beta = Y_1/Y_0$ with active $(u, v) = (X_0^2, Y_0^2)$, the sextic becomes $F = f(u, v) + Y_2^6$ with

$$c_0 = 1 + r^6 + w^6, \quad c_1 = \beta(r + r^3 w), \quad c_2 = \frac{1}{7} r \beta (1 - \beta^2), \quad c_3 = 1 + \beta^6.$$

Both $c_1$ and $c_2$ contain the factor $r\beta$. Their $\beta$-resultant is therefore identically zero for all $r,w$; it does not define a special boundary locus. The selected coefficient $L_h=-2(3c_1c_3-c_2^2)$ vanishes when $r\beta=0$. This alone does not imply $\operatorname{disc}(h)=0$, degeneration of the Hamiltonian field, or failure of transport.

For example, at $r=w=\beta=0$ (with $X_0,Y_0\ne0$), $f=u^3+v^3$, $h=9uv$, $\operatorname{disc}(h)=81$, and $H=9u\partial_u-9v\partial_v$, while $L_h=0$. This exact counterexample corrects the previous caustic interpretation.

## 4. Physics analogies considered vs. what proves the bound

- **Symplectic / Nambu flow and Casimir invariants:** Interpreting $H = h_v \partial_u - h_u \partial_v$ as an incompressible phase-space flow with Casimir $h(u, v)$ and action-angle cubes $f_\pm = \frac{1}{2}(f \pm k/\sqrt{\mathrm{disc}(h)})$ describes the verified binary-cubic identities on fibers with nonzero discriminant. The coefficient-vanishing locus alone does not diagnose their failure.
- **Interaction involution vs. full-sextic symmetry:** The complex exchange $(Y_0, Y_1) \mapsto (i Y_1, -i Y_0)$ has order two and preserves the interaction terms, but because it negates $Y_0^6 + Y_1^6$, it does not directly supply a real projective quotient of $F$.
- **What actually proves the bound:** Neither the Nambu/Casimir interpretation nor the Kramers analogy is used as an axiom. The degree $\le 5$ exclusion is proved entirely by exact rational linear algebra over `Fraction` ($E_1$ kernels in degrees $0$–$5$ and the six exported rational dual witnesses in $S_{10}/J_{10}$).

## 5. Reproduce and attribution

```sh
python3 experiments/one_reflection_skew_pilot.py
```

- **Script:** [experiments/one_reflection_skew_pilot.py](../experiments/one_reflection_skew_pilot.py)
- **Receipt:** [results/one-reflection-skew-pilot/report.json](../results/one-reflection-skew-pilot/report.json)
- **Figures:** [one-reflection-skew-audit.png](../results/one-reflection-skew-pilot/one-reflection-skew-audit.png) · [one-reflection-skew-audit.svg](../results/one-reflection-skew-pilot/one-reflection-skew-audit.svg)
- **Credits:** Builds on the `hodge-computer/sextics` certificate and cubic-transfer framework (Chapters 1, 2, 4, and 5), `fringewidth`'s hidden-reflection observation, and `fqlx`'s accepted binary-cubic Hessian certificate for `one-reflection` (PR #123). Prepared with AI assistance for `rbajaj5`.

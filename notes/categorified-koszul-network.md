# Visual Categorification Beyond the Snake Lemma: Yang Equivariant Channels, Spivak Chain Maps & Buehler 2-Head Bilinear Attention

**Target:** `one-reflection-skew` ([Discussion #127](https://github.com/hodge-computer/sextics/discussions/127))  
**Reproducible script:** [`experiments/categorified_koszul_network.py`](../experiments/categorified_koszul_network.py)  
**Machine-readable summary:** [`results/categorified-koszul-network/summary.json`](../results/categorified-koszul-network/summary.json) (`sha256[:16] = 5ae2d057249eacc7`)  
**Visualizations:** [`categorified-koszul-network.png`](../results/categorified-koszul-network/categorified-koszul-network.png) · [`categorified-koszul-network.svg`](../results/categorified-koszul-network/categorified-koszul-network.svg)

![Visual Categorification on one-reflection-skew — Spivak Chain Maps, Yang Equivariant Channels & Buehler 2-Head Attention](../results/categorified-koszul-network/categorified-koszul-network.png)

---

## 1. Why This Is Not a Repeat of the Snake Lemma

A classical homological summary of a Koszul complex $K_\bullet(P; S)$ records static vector-space dimensions via rank–nullity:
$$\dim \ker(d_1)_d = \dim \operatorname{im}(d_2)_d + \dim H_1(K(P))_d, \qquad \dim H_0(K(P))_d = \dim S_d - \operatorname{rank}(d_1)_d.$$
While useful as a diagnostic (see [`notes/one-reflection-skew-koszul-homology.md`](one-reflection-skew-koszul-homology.md)), a table of numbers $(\dim H_0, \dim H_1)$ treats each equation set $P$ as an isolated box and discards the **morphisms between complexes**, the **equivariant representation channels**, and the **bilinear routing of tokens**.

In [`notes/categorical-syzygies.md`](categorical-syzygies.md) (line 102), we explicitly noted the missing categorical step:
> *"Construct explicit chain maps between Koszul complexes when a family is rebuilt, instead of comparing only dimension tables."*

This experiment implements that exact step and synthesizes three perspectives:
1. **David Spivak (*Applied Category Theory* / Polynomial Functors $\mathbf{Poly}$):** Operadic wiring diagrams whose boxes are graded Koszul complexes $K_\bullet(P; S)$ and whose wires are **explicit exterior-power chain maps** $f_k = \Lambda^k(T) \otimes \mathrm{id}_S: K_k(P; S) \to K_k(P'; S)$ satisfying $d'_k \circ f_k = f_{k-1} \circ d_k$ identically over $\mathbb{Q}$.
2. **David H. Yang (*$S_n$-equivariant sheaves and Koszul cohomology*, 2014):** Decomposition of the ambient polynomial ring $S = \mathbb{Q}[a_0, a_1, a_2, a_3, a_4]$ and the Koszul differentials into **Kramers-even ($\chi_+$)** and **Kramers-odd ($\chi_-$)** isotypic channels under the reflection $\sigma_{34}: a_3 \leftrightarrow a_4$.
3. **Markus J. Buehler (Categorification of Transformer Attention):** Decomposition of the second-order Hodge obstruction profunctor $\mathcal{B}: \mathcal{E}_1 \times \mathcal{E}_1 \to S_{14}/(J_{14} + F S_8)$ into two exact **bilinear attention heads**,
   $$\mathcal{B}(e_a, e_b) = \mathcal{A}_{\text{div}}(e_a, e_b) + \mathcal{A}_{\text{Lie}}(e_a, e_b),$$
   which separates **non-Jacobian E1 syzygy lifts** ($U_i \notin J_7(F)$, detected exclusively by Head 1 $\mathcal{A}_{\text{div}}$) from **Kähler–Hessian curvature** ($\nabla^2 F$, carried by Head 2 $\mathcal{A}_{\text{Lie}}$).

---

## 2. Spivak Operadic Wiring & Explicit Functorial Chain Maps $\Lambda^k(T)$

Given two quadratic generator tuples $P = (P_1, \dots, P_r)$ and $P' = (P'_1, \dots, P'_{r'})$ in $S = \mathbb{Q}[a_0, a_1, a_2, a_3, a_4]$ related by an $r' \times r$ rational transition matrix $T$ such that $P_j = \sum_{i=1}^{r'} T_{ij} P'_i$, the exterior powers $\Lambda^k(T): \Lambda^k(\mathbb{Q}^r) \to \Lambda^k(\mathbb{Q}^{r'})$ with entries given by $k \times k$ minors of $T$,
$$f_k(e_{j_1} \wedge \dots \wedge e_{j_k} \otimes m) = \sum_{1 \le i_1 < \dots < i_k \le r'} \det\bigl(T_{[i_1,\dots,i_k],[j_1,\dots,j_k]}\bigr)\, e'_{i_1} \wedge \dots \wedge e'_{i_k} \otimes m,$$
define a strict graded chain map $f_\bullet: K_\bullet(P; S) \to K_\bullet(P'; S)$ commuting with the Koszul differentials:
$$d'_k \circ f_k = f_{k-1} \circ d_k \qquad (\forall\, k \ge 1).$$

Because $P_{\text{full}} = (Q_1, \dots, Q_9)$ is in row-echelon form (REF) with leading pivot monomials
$$\mathrm{pivots} = \bigl((0,0),\, (0,1),\, (0,2),\, (0,3),\, (0,4),\, (1,1),\, (1,2),\, (1,3),\, (1,4)\bigr),$$
forward substitution along `ref_pivots` yields unique, exact rational transition matrices $T$ for every sub-ideal in the `one-reflection-skew` hierarchy:

- **$\Psi_\bullet: K_\bullet(P_{\text{Hess}}) \to K_\bullet(P_{\text{full}})$ ($9 \times 4$ transition matrix):** Maps $(Q_6, Q_{\text{Kramers}}, Q_{\text{bridge}}, Q_3)$ into $P_{\text{full}}$, with column 3 encoding the exact Koszul-lifted bridge identity:
  $$Q_{\text{bridge}} = Q_1 - Q_2 - Q_4 + \frac{1}{2} Q_5 - \frac{1}{2} Q_6 - \frac{13}{12} Q_7 + \frac{9}{4} Q_8 - \frac{17}{60} Q_9.$$
- **$\Phi_\bullet: K_\bullet(P_{\text{factored}}) \to K_\bullet(P_{\text{full}})$ ($9 \times 4$ transition matrix):** Maps $(Q_{\text{Kramers}}, Q_8, Q_3, Q_4)$ into $P_{\text{full}}$ via $Q_{\text{Kramers}} = Q_4 - Q_5$, transporting the 1-dimensional degree-3 Kramers factor cycle in $H_1(K(P_{\text{factored}}))_3$ directly into the 10-dimensional first Koszul homology $H_1(K(P_{\text{full}}))_3$.
- **$\iota_{\text{core}}: K_\bullet(P_{\text{core}}) \to K_\bullet(P_{\text{full}})$ ($9 \times 4$ inclusion):** Embeds the 4-variable complete intersection $(Q_6, Q_7, Q_8, Q_9) \subset \mathbb{Q}[a_1, a_2, a_3, a_4]$ into the 5-variable complex.
- **Functorial Composition ($\Psi_\bullet \circ \iota_1 = \iota_{\text{Cas}\to\text{full}}$):** Verified across **1,408 basis columns** ($k = 1, 2, 3, 4$, degrees $d = 2 \dots 6$) with zero discrepancy over $\mathbb{Q}$.

---

## 3. David H. Yang's Equivariant Kramers Channels ($S_d = S_d^{(+)} \oplus S_d^{(-)}$)

Under the Kramers coordinate reflection $\sigma_{34}: a_3 \leftrightarrow a_4$ (corresponding to $Y_0 \leftrightarrow Y_1$), the degree-$d$ polynomial space $S_d = \mathbb{Q}[a_0, a_1, a_2, a_3, a_4]_d$ splits into two canonical $\mathbb{Z}_2^{\text{Kramers}}$-isotypic channels:
- **Kramers-Even Channel $S_d^{(+)}$:** polynomials invariant under $a_3 \leftrightarrow a_4$,
- **Kramers-Odd Channel $S_d^{(-)} = (a_3 - a_4)\,S_{d-1}^{(+)}$:** polynomials anti-symmetric under $a_3 \leftrightarrow a_4$ (divisible by the linear factor $a_3 - a_4$).

| Degree $d$ | $\dim S_d$ | Kramers-Even $\dim S_d^{(+)}$ | Kramers-Odd $\dim S_d^{(-)}$ | Chain-Map Image Rank $\operatorname{rank}(\Phi_1: K_1(P_{\text{fac}})_d \to K_1(P_{\text{full}})_d)$ |
| :---: | :---: | :---: | :---: | :---: |
| $1$ | $5$ | $4$ | $1$ | — |
| $2$ | $15$ | $11$ | $4$ | $4$ |
| $3$ | $35$ | $24$ | $11$ | $20$ |
| $4$ | $70$ | $46$ | $24$ | $60$ |
| $5$ | $126$ | $80$ | $46$ | $140$ |
| $6$ | $210$ | $130$ | $80$ | — |

Because both $Q_{\text{Kramers}} = (a_3 - a_4)(a_0 + a_1 - a_3 - a_4)$ and $Q_8 = (a_3 - a_4)(a_1 - \frac{1}{3}a_2 - \frac{2}{3}a_3 + \frac{1}{3}a_4)$ belong strictly to the **Kramers-odd channel $S_2^{(-)}$**, their shared factor $(a_3 - a_4)$ generates the exact degree-3 Koszul cycle in $H_1(K(P_{\text{factored}}))_3$.

---

## 4. Markus J. Buehler's 2-Head Bilinear Attention Decomposition ($\mathcal{B} = \mathcal{A}_{\text{div}} + \mathcal{A}_{\text{Lie}}$)

In our second-order obstruction calculus, the E1 kernel category $\mathcal{E}_1$ consists of token pairs $e_a = (D_a, N_a)$ satisfying the first-order lift $A D_a = \nabla F \cdot N_a$. The symmetric second-order obstruction profunctor $\mathcal{B}: \mathcal{E}_1 \times \mathcal{E}_1 \to S_{2d+2}$ splits identically over $\mathbb{Q}[X_0, X_1, X_2, Y_0, Y_1, Y_2]$ into **two bilinear attention heads**:

$$\mathcal{B}(e_a, e_b) = \underbrace{\bigl(D_a\,\operatorname{div}(N_b) + D_b\,\operatorname{div}(N_a)\bigr)}_{\text{Head 1: Divergence-Gauge Attention }\mathcal{A}_{\text{div}}(e_a, e_b)} \;+\; \underbrace{\bigl(-N_b \cdot \nabla D_a - N_a \cdot \nabla D_b\bigr)}_{\text{Head 2: Lie-Curvature Attention }\mathcal{A}_{\text{Lie}}(e_a, e_b)}.$$

Evaluating both heads on a 10-token system in degree-7 sector `[1,1,1,0]` — consisting of **5 Jacobian Euler tokens** $X_0 E_0, \dots, X_0 E_4 \in J_7(F)$ and **5 non-Jacobian ("added") E1 kernel lifts** $U_0, \dots, U_4 \in \ker(E_1)_7 \setminus J_7(F)$ — reveals a striking structural theorem in the 44-dimensional base quotient $S_{14}^{(5)}[(1,0,1)] / (J_{14}^{(5)} + F^{(5)} S_8^{(5)})$:

1. **Head 1 ($\mathcal{A}_{\text{div}}$) is an Exact Detector of Non-Jacobian E1 Kernel Lifts:**
   Whenever both $e_a, e_b$ are Jacobian anchor tokens ($D_a, D_b \in J_7(F)$), $D_a\,\operatorname{div}(N_b) + D_b\,\operatorname{div}(N_a) \in J_7(F) \cdot S_7 \subset J_{14}(F)$. Consequently, **Head 1 ($\mathcal{A}_{\text{div}}$) has quotient rank $0/44$ on the entire $5 \times 5$ Jacobian–Jacobian block**, and lights up with **quotient rank $15/44$ exclusively on pairs involving the non-Jacobian syzygy lifts $U_0, \dots, U_4 \notin J_7(F)$** (Panel C, left heatmap).
2. **Head 2 ($\mathcal{A}_{\text{Lie}}$) is the Kähler–Hessian Curvature Head:**
   By Leibniz's rule on $D_a = m_a \partial_i F$, $\nabla D_a = (\nabla m_a)\partial_i F + m_a \nabla(\partial_i F)$. Modulo $J_{14}(F)$, the first term vanishes while $-N_b \cdot \nabla D_a$ projects directly onto the **Hessian curvature** $-m_a N_{b,j} \partial_j \partial_i F$, achieving **quotient rank $39/44$** across the 10-token system (Panel C, right heatmap).

---

## 5. What a Kähler Manifold Is in the Sense of Conformal Field Theory

Why does a polynomial Jacobian ring $S / J(F)$ and its Hessian curvature $\partial_i \partial_j F$ govern both classical Hodge cycles and conformal field theory? In two-dimensional quantum field theory, a **Kähler manifold** has a remarkably simple and foundational meaning:

### 5.1 Classical Differential Geometry vs. 2D Worldsheet Supersymmetry
Classically, a complex manifold $M$ of complex dimension $n$ with local holomorphic coordinates $(Z^1, \dots, Z^n)$ and Hermitian metric $g_{i\bar\jmath}\,dZ^i \otimes d\bar Z^{\bar\jmath}$ is **Kähler** if its fundamental $(1,1)$-form
$$\omega = \frac{i}{2} \sum_{i,\bar\jmath} g_{i\bar\jmath}(Z, \bar Z)\, dZ^i \wedge d\bar Z^{\bar\jmath}$$
is closed ($d\omega = 0$), which locally is equivalent to the existence of a real scalar **Kähler potential** $K(Z, \bar Z)$ such that
$$g_{i\bar\jmath}(Z, \bar Z) = \frac{\partial^2 K(Z, \bar Z)}{\partial Z^i \, \partial \bar Z^{\bar\jmath}}.$$

In **Conformal Field Theory (CFT)** and string theory, one studies maps $\Phi: \Sigma \to M$ from a 2D Riemann surface ("worldsheet") $\Sigma$ into the target space $M$ (a nonlinear sigma model). A fundamental theorem of **Bruno Zumino (1979)** and **Luis Alvarez-Gaumé & Daniel Z. Freedman (1981)** states:

> **CFT Definition of a Kähler Manifold:** A Riemannian manifold $(M, g)$ is a **Kähler manifold** *if and only if* the 2D supersymmetric nonlinear sigma model with target space $M$ admits **$\mathcal{N} = (2, 2)$ extended worldsheet supersymmetry** (two left-moving and two right-moving supercharges $Q_\pm, \bar Q_\pm$). Moreover, in $\mathcal{N}=(2,2)$ superspace $(z, \bar z, \theta^\pm, \bar\theta^\pm)$, the **Kähler potential $K(\Phi, \bar\Phi)$ is literally the Lagrangian density itself**:
> $$S_{\text{sigma}}[\Phi, \bar\Phi] = \int_\Sigma d^2z \, d^4\theta \; K(\Phi, \bar\Phi).$$
> Expanding the Grassmann integral $\int d^4\theta\, K(\Phi, \bar\Phi)$ automatically differentiates $K$ twice with respect to the chiral and antichiral superfields $\Phi^i, \bar\Phi^{\bar\jmath}$, producing the metric $g_{i\bar\jmath} = \partial_i \partial_{\bar\jmath} K$ and the Levi-Civita / Riemann curvature couplings!

### 5.2 The Hodge Decomposition as Worldsheet $U(1)_L \times U(1)_R$ R-Symmetry
In an $\mathcal{N}=(2,2)$ superconformal field theory (SCFT), the superconformal algebra contains two conserved $U(1)$ R-symmetry currents: a left-moving (holomorphic) current $J_L(z)$ and a right-moving (antiholomorphic) current $J_R(\bar z)$.
- Under Witten's supersymmetric identification of worldsheet fermions $\psi^i \leftrightarrow dZ^i$ and $\bar\psi^{\bar\jmath} \leftrightarrow d\bar Z^{\bar\jmath}$, a differential $(p,q)$-form $\alpha \in \Omega^{p,q}(M)$ is a quantum state carrying **left/right $U(1)_L \times U(1)_R$ R-charges $(q_L, q_R) = (p, q)$**.
- The four supercharges act as the Dolbeault operators $\bar\partial, \bar\partial^\dagger, \partial, \partial^\dagger$, and the worldsheet Hamiltonian $H = \{Q, Q^\dagger\}$ is the **Kähler–Hodge Laplacian** $\Delta_{\bar\partial} = \bar\partial\bar\partial^\dagger + \bar\partial^\dagger\bar\partial = \frac{1}{2}\Delta_d$.
- Consequently, **Hodge's $(p,q)$-cohomology groups $H^{p,q}(M)$ are literally the zero-energy supersymmetric ground states (Ramond vacua / chiral primaries)** of the CFT graded by their $(U(1)_L, U(1)_R)$ quantum numbers!
- Finally, when $M$ is a hypersurface $X = \{F(Z_0, \dots, Z_5) = 0\} \subset \mathbb{P}^5$ (such as our fourfold sextics in `hodge-computer/sextics`), the **Landau–Ginzburg / CFT correspondence** (Lerche–Vafa–Warner 1989, Witten 1993) realizes the Kähler sigma model on $X$ as the infrared fixed point of a 2D $\mathcal{N}=(2,2)$ Landau–Ginzburg theory with **holomorphic superpotential $W(Z) = F(Z)$**:
  $$S_{\text{LG}} = \int d^2z \, d^4\theta \, K(Z, \bar Z) + \left( \int d^2z \, d^2\theta \, F(Z) + \text{c.c.} \right).$$
  The classical equations of motion for the superpotential are $\partial_i F(Z) = 0$, so the **chiral primary ring** of operators surviving $Q$-cohomology is the **Jacobian (Milnor) ring**
  $$\mathcal{R}_{\text{chiral}} = \frac{\mathbb{C}[Z_0, \dots, Z_5]}{\bigl(\partial_0 F, \dots, \partial_5 F\bigr)} = \frac{S}{J(F)},$$
  matching **Phillip Griffiths' residue description** of primitive middle Hodge classes on $X$!

---

## 6. Scope and Verification Boundaries

- **What this picture establishes:** Exact rational commutativity $d'_k \circ \Lambda^k(T) = \Lambda^{k-1}(T) \circ d_k$ across **1,408 basis columns** of the `one-reflection-skew` Koszul network; exact $\mathbb{Z}_2^{\text{Kramers}}$ channel dimensions $S_d = S_d^{(+)} \oplus S_d^{(-)}$; and the exact 2-head bilinear attention decomposition $\mathcal{B} = \mathcal{A}_{\text{div}} + \mathcal{A}_{\text{Lie}}$ across all 55 pairs of the 10-token degree-7 `[1,1,1,0]` benchmark (showing $\operatorname{rank}(\mathcal{A}_{\text{div}}) = 0/44$ on $J_7 \times J_7$ and $15/44$ on non-Jacobian E1 lifts).
- **What it does not claim:** It does not invoke Yang's geometric theorem on $S_n$-equivariant vector bundles over Hilbert schemes of points, and it does not claim an existence certificate (`HasCertificate`) on `one-reflection-skew`.

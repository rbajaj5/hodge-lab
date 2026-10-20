# `one-reflection-skew`: Eisenbud Graded Strands & Finite Koszul Homology ($H_0$ vs. $H_1$ Contrast)

**Target (`hodge-computer/sextics`, Discussion #127):**
$$F = X_0^6 + X_1^6 + X_2^6 + Y_0^6 + Y_1^6 + Y_2^6 + X_0^3 X_1 Y_0 Y_1 + X_1^3 X_2 Y_0 Y_1 + \frac{1}{7} X_0 X_1 Y_0 Y_1 (Y_0^2 - Y_1^2), \qquad A = X_0^3 Y_0^3, \qquad q = 1.$$

This note records **Checkpoint 88**, applying the finite Koszul complex engine [`experiments/necessary_koszul_complex.py`](../experiments/necessary_koszul_complex.py) (`complex_at`) and the Eisenbud graded-syzygy / Eisenbud–Erman / David H. Yang framework ([`notes/categorical-syzygies.md`](categorical-syzygies.md), [`notes/added-character-homology.md`](added-character-homology.md)) to the quadratic $E_2$ obstruction ideals of `one-reflection-skew` across degrees $6$ and $7$. Every differential rank, $d_{k-1} \circ d_k = 0$ composition, Koszul boundary span $\mathrm{im}(d_2)$, homology quotient $H_1 = \ker(d_1)/\mathrm{im}(d_2)$, and coordinate-power quotient $H_0 = S_d / \mathrm{im}(d_1)$ is verified in exact rational arithmetic over $\mathbb{Q}$ via [`experiments/one_reflection_skew_koszul_homology.py`](../experiments/one_reflection_skew_koszul_homology.py).

![one-reflection-skew Eisenbud graded strands and finite Koszul homology](../results/one-reflection-skew-koszul/one-reflection-skew-koszul-homology.png)

*Figure 1 (`results/one-reflection-skew-koszul/one-reflection-skew-koszul-homology.png`, SVG companion `one-reflection-skew-koszul-homology.svg`). Panel A plots the zeroth Koszul homology $\dim_{\mathbb{Q}} H_0(K(P; S))_d = \dim(S/P)_d$ across degrees $d = 2,\dots,6$ for the five canonical quadratic ideals of `one-reflection-skew`, contrasting regular sequences in $\mathbb{P}^4$ ($\dim H_0 \to 2^4 = 16$) against the $4$-variable complete intersection $P_{\text{core}} = (Q_6, Q_7, Q_8, Q_9)$ ($\dim H_0 = \binom{4}{d} \to 0$ at $d=5$) and the full $9$-quadric diagonal ideal $P_{\text{full}}$ ($\dim H_0 = 0$ at $d=3, 4, 5$). Panel B decomposes the syzygy kernel $\ker(d_1)_d$ into automatic pairwise Koszul boundaries $\mathrm{im}(d_2)_d$ and genuine first Koszul homology $H_1(K(P; S))_d = \ker(d_1)_d / \mathrm{im}(d_2)_d$. Panel C displays the actual $35 \times 45$ sign pattern of the degree-$3$ first Koszul differential $d_1: K_{1,3} \to K_{0,3}$ for $P_{\text{full}}$ (`rank = 35/35`, $\dim H_0 = 0$, $\dim H_1 = 10$). Panel D summarizes the universal degree-$7$ $Z_k$-twisted Euler regular sequences and the full-rank degree-$2$ obstruction on all three non-Jacobian ("added") $E_1$ sub-blocks. Scope note: these are classical finite graded Koszul complexes $K_\bullet(P; S)$ over $\mathbb{Q}$; they do not establish David H. Yang's geometric Bridgeland–King–Reid / Hilbert-scheme theorem or an existence certificate.*

---

## 1. Motivation: Eisenbud's Syzygy Strands and the $H_0$ vs. $H_1$ Contrast

As documented in [`notes/categorical-syzygies.md`](categorical-syzygies.md) and [`notes/added-character-homology.md`](added-character-homology.md):
- David Eisenbud's graded syzygy theory and David Eisenbud & Daniel Erman's [*Categorified duality in Boij–Söderberg theory and invariants of free complexes*](https://ems.press/journals/jems/articles/14923) motivate retaining the actual graded differentials of the Koszul complex
  $$K_k(P; S) = S(-2k)^{\binom{r}{k}}, \qquad K_3 \xrightarrow{d_3} K_2 \xrightarrow{d_2} K_1 \xrightarrow{d_1} K_0 = S,$$
  rather than reducing an ideal $P = (P_1, \dots, P_r)$ to a single numerical rank.
- David H. Yang's [*$S_n$-equivariant sheaves and Koszul cohomology* (2014)](https://link.springer.com/article/10.1186/s40687-014-0010-9) motivates tracking equivariant symmetry sectors and reflection factors inside Koszul cohomology, while our earlier `holdout` experiments established a sharp operational distinction:
  1. **First Koszul homology $H_1(K(P; S))_d = \ker(d_1)_d / \mathrm{im}(d_2)_d$** measures **non-trivial syzygies among the quadratic generators** after removing the automatic pairwise Koszul boundaries $P_i e_j - P_j e_i \in \mathrm{im}(d_2)$. In particular, shared linear factors between generators create low-degree $H_1$ cycles (such as degree-$3$ linear syzygies where $K_{2,3} = 0$).
  2. **Zeroth Koszul homology $H_0(K(P; S))_d = S_d / \mathrm{im}(d_1)_d$** measures **how far the degree-$d$ Macaulay image $\mathrm{im}(d_1)_d$ is from spanning all degree-$d$ monomials**. When $\dim H_0(K(P; S))_d = 0$, $d_1$ is surjective in degree $d$, forcing every coordinate $d$-th power $a_i^d = 0$ over $\mathbb{C}$.

---

## 2. Five Canonical Quadratic Ideals in Degree 6 & Degree 7 (`[0,0,0,1]`)

After the two-step Hessian square cascade ($35 \to 7 \to 5$) in degree $6$ (and the isomorphic $13 \to 6 \to 5$ cascade in the degree-$7$ $Y_2$-twisted Euler sector `[0,0,0,1]` via $B_{Y_2 D_6}(Y_2 N_{6,0}) \equiv Y_2^2 B_{D_6}(N_{6,0})$), five canonical quadratic ideals govern the diagonal Euler parameters $(a_0, a_1, a_2, a_3, a_4)$:

| Ideal $P$ | Ambient Ring $S$ | Generators $r$ | $\dim H_0(K)_d$ ($d=2\dots 6$) | $\dim \ker(d_1)_d$ ($d=2\dots 6$) | $\dim \mathrm{im}(d_2)_d$ ($d=2\dots 6$) | $\dim H_1(K)_d$ ($d=2\dots 6$) | Algebraic & Geometric Structure |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`P_Cas`** | $\mathbb{Q}[a_0,\dots,a_4]$ | $3$ ($Q_{\text{node}}, Q_{\text{Kramers}}, Q_{\text{bridge}}$) | $(12, 20, 28, 36, 44)$ | $(0, 0, 3, 15, 44)$ | $(0, 0, 3, 15, 44)$ | $(0, 0, 0, 0, 0)$ | Regular sequence of length $3$ in $\mathbb{P}^4$ (curve of degree $8$) |
| **`P_Hess`** | $\mathbb{Q}[a_0,\dots,a_4]$ | $4$ ($Q_{\text{node}}, Q_{\text{Kramers}}, Q_{\text{bridge}}, Q_3$) | $(11, 15, 16, 16, 16)$ | $(0, 0, 6, 30, 86)$ | $(0, 0, 6, 30, 86)$ | $(0, 0, 0, 0, 0)$ | **Regular sequence of length $4$ in $\mathbb{P}^4$** ($2^4 = 16$ points with multiplicity) |
| **`P_factored`** | $\mathbb{Q}[a_0,\dots,a_4]$ | $4$ ($Q_{\text{Kramers}}, Q_8, Q_3, Q_4$) | $(11, 16, 20, 24, 28)$ | $(0, 1, 10, 38, 98)$ | $(0, 0, 6, 30, 86)$ | **$(0, 1, 4, 8, 12)$** | Shared Kramers factor $(a_3 - a_4)$ generates **explicit degree-$3$ $H_1$ cycle** |
| **`P_core`** | $\mathbb{Q}[a_1,a_2,a_3,a_4]$ | $4$ ($Q_6, Q_7, Q_8, Q_9$) | **$(6, 4, 1, 0, 0) = \binom{4}{d}$** | $(0, 0, 6, 24, 56)$ | $(0, 0, 6, 24, 56)$ | $(0, 0, 0, 0, 0)$ | **$4$-variable complete intersection** ($\dim H_0 = 0$ at $d=5 \implies a_i^5 = 0$) |
| **`P_full`** | $\mathbb{Q}[a_0,\dots,a_4]$ | $9$ ($Q_1,\dots,Q_9$) | **$(6, 0, 0, 0, -)$** | $(0, 10, 65, 189, -)$ | $(0, 0, 36, 179, -)$ | **$(0, 10, 29, 10, -)$** | **Full exclusion at $d=3, 4$** ($\dim H_0 = 0$; $65 = 36 + 29$ at $d=4$; $\dim H_2 = 1$ at $d=5$) |

### Key Structural Theorems from the Koszul Complex Table

1. **Why the Pure Hessian Quotient $S_{12}/J_{12}$ Stops at $\dim H_0 = 16$ (`P_Hess` Regular Sequence Theorem):**
   In `P_Hess`, all higher Koszul homology vanishes ($H_1 = H_2 = H_3 = H_4 = 0$ across $d = 2,\dots,6$; every cycle in $\ker(d_1)$ is an automatic Koszul boundary in $\mathrm{im}(d_2)$, e.g. $6=6$ at $d=4$, $30=30$ at $d=5$, $86=86$ at $d=6$). By Eisenbud's Koszul regularity theorem, $(Q_{\text{node}}, Q_{\text{Kramers}}, Q_{\text{bridge}}, Q_3)$ is a **regular sequence of length $4$ in the $5$-variable polynomial ring $\mathbb{Q}[a_0,\dots,a_4]$**, cutting out a $0$-dimensional projective scheme of degree $2^4 = 16$ in $\mathbb{P}^4_{\mathbb{C}}$ (a $1$-dimensional affine cone). Thus $\dim H_0(K(P_{\text{Hess}}))_d = 16$ for all $d \ge 4$, proving that Koszul syzygy lifting in the full $E_2$ quotient is algebraically essential to close the diagonal sector.

2. **Exact Complete Intersection on the $a_0$-Eliminated Core (`P_core = (Q_6, Q_7, Q_8, Q_9)`):**
   Eliminating the anchor variable $a_0$ from the full $9$-quadric RREF system isolates $P_{\text{core}} = (Q_6, Q_7, Q_8, Q_9) \subset \mathbb{Q}[a_1, a_2, a_3, a_4]$. Its finite Koszul complex has $H_1 = H_2 = H_3 = H_4 = 0$ in every degree and Hilbert series
   $$\sum_{d=0}^6 \dim_{\mathbb{Q}} H_0(K(P_{\text{core}}))_d\, t^d = 1 + 4t + 6t^2 + 4t^3 + t^4 = (1 + t)^4.$$
   Hence $(Q_6, Q_7, Q_8, Q_9)$ is a **regular sequence of length $4$ in $4$ variables** (an Artinian complete intersection of length $2^4 = 16$), whose degree-$5$ Koszul differential $d_1: \mathbb{Q}^{80} \to \mathbb{Q}^{56}$ has **full rank $56/56$** ($\dim H_0 = 0$), forcing $a_1^5 = a_2^5 = a_3^5 = a_4^5 = 0$ using only $Q_6,\dots,Q_9$.

3. **Explicit Degree-3 Kramers Reflection-Breaking Cycle in $H_1(K(P_{\text{factored}}; S))_3$:**
   Because the pure-Hessian Kramers mode $Q_{\text{Kramers}} = (a_3 - a_4)(a_0 + a_1 - a_3 - a_4)$ and the Koszul-lifted RREF quadric $Q_8 = \frac{1}{3}(a_3 - a_4)(3 a_1 - a_2 - 2 a_3 + a_4)$ share the reflection-breaking linear factor $(a_3 - a_4)$, they satisfy the degree-$3$ linear syzygy
   $$\Big(a_1 - \frac{1}{3}a_2 - \frac{2}{3}a_3 + \frac{1}{3}a_4\Big) Q_{\text{Kramers}} - (a_0 + a_1 - a_3 - a_4) Q_8 = 0.$$
   Since $K_{2,3} = 0$, this syzygy cannot be a Koszul boundary and spans the $1$-dimensional homology group $H_1(K(P_{\text{factored}}; S))_3 \cong \mathbb{Q}^1$ (directly analogous to the `(-u, v, 0)` cycle of B19 in [`notes/categorical-syzygies.md`](categorical-syzygies.md)).

4. **Boundary vs. Homology Split in `P_full` at Degrees $3, 4, 5$:**
   Adjoining $Q_1, \dots, Q_5$ to $P_{\text{core}}$ collapses $H_0(K(P_{\text{full}}))_d = 0$ already at degree $d = 3$ ($\mathrm{rank}(d_1) = 35/35$, $\dim H_1 = 10$). At degree $d = 4$ ($K_2 \to K_1 \to K_0$ of dimensions $36 \to 135 \to 70$), $\mathrm{rank}(d_1) = 70/70$ ($\dim H_0 = 0$) and $\mathrm{rank}(d_2) = 36/36$, splitting the $65$-dimensional syzygy space $\ker(d_1)_4$ into **$36$ Koszul boundaries** ($\mathrm{im}\, d_2$) and **$29$ genuine $H_1$ homology classes**. At degree $d = 5$ ($180 \to 315 \to 126$), $\mathrm{rank}(d_1) = 126/126$ ($\dim H_0 = 0$), $\ker(d_1)_5 = 189 = 179\text{ boundaries} + 10\text{ } H_1\text{ classes}$, and $\ker(d_2)_5$ acquires a **unique second-syzygy cycle** ($\dim H_2(K(P_{\text{full}}))_5 = 180 - 179 = 1$).

---

## 3. Degree-7 Universal $Z_k$-Twisted Euler Regular Sequences & Non-Jacobian ("Added") Sub-Blocks

1. **Universal $Z_k$-Twisted Euler Regular Sequence Across All Four $Y_2$-Even Sectors:**
   For each base coordinate $Z_k \in \{X_0, X_1, X_2, Y_0, Y_1\}$, the $5$-dimensional $Z_k$-twisted Euler family $\{Z_k Z_i \partial_i F\}_{i=0}^4$ in degree $7$ lies in sector $\chi(Z_k)$ (`[1,1,1,0]` for $X_0, X_2$; `[1,0,0,0]` for $X_1$; `[0,1,0,0]` for $Y_0$; `[0,0,1,0]` for $Y_1$). Projecting its $15$ quadratic forms modulo $J_{14}^{(5)}(F_5) + F_5 S_8^{(5)}$ in $S_{14}^{(5)}[(1,0,1)]$ ($44$-dimensional quotient) yields **exact quadratic rank $4$** and the **exact same Koszul complex invariants** $\dim H_0 = (11, 15, 16)$ and $\dim H_1 = (0, 0, 0)$ for $d = 2, 3, 4$ across every single coordinate $Z_k$ ($k = 0, \dots, 5$).

2. **Full-Rank Degree-2 Obstruction on the Pure Non-Jacobian ("Added") $E_1$ Sub-Blocks:**
   Following the added-character diagnostic of [`notes/added-character-homology.md`](added-character-homology.md), we isolate the $9$ non-Jacobian ("added") $E_1$ generators in degree $7$ (`+1` in `[0,0,1,0]`, `+1` in `[1,0,0,0]`, and `+7` in `[1,1,1,0]`):
   - In `[0,0,1,0]` ($1$ variable, $1$ quadratic column) and `[1,0,0,0]` ($1$ variable, $1$ quadratic column), the quadratic $E_2$ map into the $44$-dimensional base quotient has **rank $1/1$**, so $\dim H_0 = 0$ and $\dim H_1 = 0$ at $d = 2$, forcing $e_0^2 = 0$.
   - In `[1,1,1,0]` ($7$ variables $e_0, \dots, e_6$, $\binom{7+1}{2} = 28$ quadratic columns), the quadratic $E_2$ map into the $44$-dimensional base quotient has **full rank $28/28$**, so $\dim H_0 = 0$ and $\dim H_1 = 0$ at $d = 2$, forcing all $7$ pure non-Jacobian squares $e_0^2 = \dots = e_6^2 = 0$.
   - Consequently, no pure non-Jacobian degree-$7$ candidate exists in any sector; any degree-$7$ candidate in the $Y_2$-even sectors must couple the non-Jacobian subspace to the $Y_2 = 0$ Jacobian anchor block or the sector's degree-$8$ Koszul syzygies.

---

## 4. Reproducibility

Run the complete verification ($26$ finite Koszul complexes, $709$ verified $d_{k-1} \circ d_k = 0$ columns) and regenerate the figure from the repository root:
```bash
python experiments/one_reflection_skew_koszul_homology.py
```

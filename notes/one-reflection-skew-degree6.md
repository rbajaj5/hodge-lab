# `one-reflection-skew`: Complete Degree-6 $E_1 + E_2$ Exclusion over $\mathbb{C}$

**Target (`hodge-computer/sextics`, Discussion #127):**
$$F = X_0^6 + X_1^6 + X_2^6 + Y_0^6 + Y_1^6 + Y_2^6 + X_0^3 X_1 Y_0 Y_1 + X_1^3 X_2 Y_0 Y_1 + \frac{1}{7} X_0 X_1 Y_0 Y_1 (Y_0^2 - Y_1^2), \qquad A = X_0^3 Y_0^3, \qquad q = 1.$$

This note records **Checkpoint 86**, completing the degree-6 $E_1$ and $E_2$ obstruction analysis for `one-reflection-skew`. Every matrix rank, dual functional, Koszul syzygy lift, and Macaulay power identity is verified in exact rational arithmetic over $\mathbb{Q}$ via [`experiments/one_reflection_skew_degree6.py`](../experiments/one_reflection_skew_degree6.py).

![Complete degree-6 E1+E2 exclusion for one-reflection-skew](../results/one-reflection-skew-degree6/one-reflection-skew-degree6-exclusion.png)

*Figure 1 (`results/one-reflection-skew-degree6/one-reflection-skew-degree6-exclusion.png`, SVG companion `one-reflection-skew-degree6-exclusion.svg`). Panel A compares $\dim\ker(E_1)_d$ across $0 \le d \le 6$ against $\dim J_d(F)$ and the `cyclic`/`fano` degree-6 kernel ($38 = 36+2$). Panel B shows the 36-parameter Jacobian matrix $L_i = \sum_j M_{ij} Z_j$ color-coded by the stage at which each entry is eliminated. Panel C displays the exact rational $9 \times 15$ RREF coefficient table of the full diagonal $E_2$ quotient system after $a_5=0$ gauge. Panel D summarizes the factored Hessian Casimir/Kramers modes and the full-rank cubic ($35/35$) and quartic ($70/70$) Macaulay elimination over $\mathbb{C}$. Scope note: the figure encodes verified degree-$\le 6$ obstructions over $\mathbb{Q}$ and $\mathbb{C}$; it does not establish higher-degree ($d \ge 7$) behavior or an existence certificate.*

---

## 1. Executive Summary

1. **Complete Degree-6 $E_1$ Kernel Equals $J_6(F)$ ($\dim = 36$, $0$ Extra Directions):**
   In $S_{12}$ ($\dim = 6{,}188$), the degree-6 Jacobian multiplication map $J_{12}: (S_7)^6 \to S_{12}$ ($4{,}752$ columns) has exact rank $4{,}437$, and the augmented matrix $[J_{12} \mid A S_6]$ ($462$ denominator columns) has rank $4{,}863$. Thus the image of $D \mapsto [AD]$ in $S_{12}/J_{12}$ has rank $4{,}863 - 4{,}437 = 426$, and
   $$\dim\ker\big(S_6 \xrightarrow{D \mapsto [AD]} S_{12}/J_{12}\big) = 462 - 426 = 36 = \dim J_6(F).$$
   Unlike `cyclic` and `fano` (where $\dim\ker(E_1)_6 = 38$, leaving two non-Jacobian degree-6 directions), the coupled chain $X_0^3 X_1 Y_0 Y_1 + X_1^3 X_2 Y_0 Y_1$ and reflection-breaking term $\frac{1}{7}X_0 X_1 Y_0 Y_1(Y_0^2 - Y_1^2)$ close all non-Jacobian $E_1$ channels at degree 6. Every degree-6 solution of $AD = \nabla F \cdot N_0$ has the form
   $$D = \sum_{i,j=0}^5 M_{ij} Z_j \frac{\partial F}{\partial Z_i}, \qquad N_{0,i} = A \sum_{j=0}^5 M_{ij} Z_j + K_i, \qquad K \in \ker(J_{12}).$$

2. **Two-Step Hessian $E_2$ Cascade in $S_{12}/J_{12}$ (Kramers-Bridge Doublet at Step 2):**
   - **Koszul Syzygy Completeness at Degree 7:** The $15 \times 21 = 315$ quadratic multiples of the elementary Koszul fields $e_{ij} = (\partial_j F)\epsilon_i - (\partial_i F)\epsilon_j$ have exact rank $315 = 4{,}752 - 4{,}437 = \dim\ker(J_{12})$. Because every Koszul field annihilates $J_{12}$ in $S_{12}/J_{12}$ ($B_D(K) \equiv 0 \pmod{J_{12}}$ for $D \in J_6(F)$), the projection of $B_D(N_0)$ to $S_{12}/J_{12}$ depends purely quadratically on the 35 gauged matrix entries $M_{ij}$ ($(i,j) \ne (5,5)$ after Euler/$F$ gauge $M_{55} = 0$).
   - **Step 1 ($35 \to 7$ parameters):** On all $\binom{35+1}{2} = 630$ quadratic columns, the Hessian quotient map in $S_{12}/J_{12}$ has rank $236$ and exports **28** exact rational dual functionals isolating $M_{ij}^2 = 0$ for 28 of the 30 off-diagonal entries.
   - **Step 2 ($7 \to 5$ parameters, Kramers-Bridge Doublet):** The only two off-diagonal parameters surviving Step 1 are the **Kramers-bridge couplings**
     $$M_{13} \leftrightarrow (X_1, Y_0) \quad\text{and}\quad M_{14} \leftrightarrow (X_1, Y_1),$$
     which couple the linear bridge node $X_1$ directly to the Kramers doublet $(Y_0, Y_1)$ in both $X_0^3 X_1 Y_0 Y_1$ and $\frac{1}{7}X_0 X_1 Y_0 Y_1(Y_0^2 - Y_1^2)$. Once the other 28 off-diagonals vanish, restricting the Hessian quotient to the 7 surviving parameters ($\binom{7+1}{2} = 28$ quadratic columns) yields rank $15$ and exports **2** exact rational dual functionals isolating $M_{13}^2 = 0$ and $M_{14}^2 = 0$.
   - **Step 3 ($5$ diagonal parameters $a_0, a_1, a_2, a_3, a_4$):** All 30 off-diagonal entries $M_{ij}$ ($i \ne j$) vanish over $\mathbb{C}$, reducing $M = \mathrm{diag}(a_0, a_1, a_2, a_3, a_4, 0)$ to the diagonal ansatz.

3. **Factored Pure-Hessian Modes vs. Rank-9 Full Diagonal $E_2$ Quotient:**
   - In the pure Hessian quotient $S_{12}/J_{12}$ (before enforcing the 315 Koszul correction columns directly in $S_{12}$), the 15 diagonal quadratic columns $a_i a_j$ ($0 \le i \le j \le 4$) have rank **4**, spanned by three transparent algebraic/physical modes plus one anchor quadric:
     $$\begin{aligned}
     9\,Q_{\text{node}} &= (3 a_1 - a_2 - a_3 - a_4)^2 + 2\big[(a_2 - a_3)^2 + (a_3 - a_4)^2 + (a_4 - a_2)^2\big] = 0, \\
     Q_{\text{Kramers}} &= (a_3 - a_4)(a_0 + a_1 - a_3 - a_4) = 0, \\
     Q_{\text{bridge}} &= (a_0 - a_3)(a_0 - a_1 + a_3 - a_4) = 0.
     \end{aligned}$$
     Notice that over $\mathbb{R}$, the chain-node Casimir $Q_{\text{node}} = 0$ (arising from the $X_1^3 X_2 Y_0 Y_1$ vertex) is a **positive-definite sum of squares** in the relative weights $(a_2 - a_3, a_3 - a_4, 3a_1 - a_2 - a_3 - a_4)$, which by itself forces $a_1 = a_2 = a_3 = a_4$ over $\mathbb{R}$!
   - Retaining the full $E_2$ operator $B_D(N_0) \in F S_6$ in $S_{12}$ with all $462 + 6 \times 315 = 2{,}352$ correction columns (rank $1{,}486$) raises the necessary diagonal quadratic rank from $4$ to **$9$** (compared to $7$ in `cycle-three`).

4. **Full-Rank Cubic ($35/35$) and Quartic ($70/70$) Macaulay Elimination over $\mathbb{C}$:**
   - Multiplying the 9 gauged quadratic equations $Q_1, \dots, Q_9$ by the 5 linear variables $a_0, \dots, a_4$ yields $45$ rows in the $\binom{5+3-1}{3} = 35$ cubic monomials, achieving **full rank $35/35$** and forcing $a_0^3 = a_1^3 = a_2^3 = a_3^3 = a_4^3 = 0$.
   - Multiplying by the 15 quadratic monomials $a_i a_j$ yields $135$ rows in the $\binom{5+4-1}{4} = 70$ quartic monomials, achieving **full rank $70/70$** and exporting 5 verified quartic identities $a_0^4 = a_1^4 = a_2^4 = a_3^4 = a_4^4 = 0$ (`2,240` nonzero rational multiplier products verified).
   - Consequently, $a_0 = a_1 = a_2 = a_3 = a_4 = 0$ over $\mathbb{C}$, so $D = 6 a_5 F \in \mathbb{C}\cdot F$, violating coprimality ($\gcd(F, D) = 1$). **Degree $d = 6$ is unconditionally excluded over $\mathbb{C}$.**

---

## 2. Exact Dimensions and Verification Ledger

| Stage | Ambient Space | Columns | Rank | Kernel / Quotient | Verified Pairings | Packet Digest (`sha256[:16]`) |
| --- | --- | --- | --- | --- | --- | --- |
| **Stage 1: Complete $E_1$ ($d=6$)** | $S_{12}$ ($6{,}188$) | $4{,}752$ ($J_{12}$) + $462$ ($A S_6$) | $4{,}437 \to 4{,}863$ | $\dim\ker(E_1)_6 = 36 = \dim J_6(F)$ | $2{,}024{,}352$ | `e9bd6e4ebdb4f159` |
| **Stage 2: Hessian $E_2$ Step 1** | $S_{12}/J_{12}$ | $630$ ($35$ params) | $236$ | $28$ squares forced ($35 \to 7$) | $133{,}056$ | `5760378eb0b37575` |
| **Stage 2: Hessian $E_2$ Step 2** | $S_{12}/J_{12}$ | $28$ ($7$ params) | $15$ | $2$ squares forced ($M_{13}, M_{14} \to 0$) | $9{,}504$ | `5760378eb0b37575` |
| **Stage 2: Hessian $E_2$ Step 3** | $S_{12}/J_{12}$ | $15$ ($5$ diag params) | $4$ | $4$ pure-Hessian quadrics | — | `5760378eb0b37575` |
| **Stage 3: Full Diagonal $E_2$** | $S_{12}$ ($6{,}188$) | $2{,}352$ corr + $21$ quad | $1{,}486$ (corr) | **$9$** diagonal quadrics in $(a_0,\dots,a_4)$ | $21{,}168 + 189$ | `55a86e93759ddb83` |
| **Cubic Macaulay Elimination** | $\mathrm{Sym}^3(\mathbb{Q}^5)$ | $35$ cubic monos | **$35 / 35$** | $45$ rows $\implies a_0^3 = \dots = a_4^3 = 0$ | Exact over $\mathbb{Q}$ | `summary.json` |
| **Quartic Macaulay Elimination** | $\mathrm{Sym}^4(\mathbb{Q}^5)$ | $70$ quartic monos | **$70 / 70$** | $135$ rows $\implies a_0^4 = \dots = a_4^4 = 0$ | $2{,}240$ products | `55a86e93759ddb83` |

---

## 3. Explicit RREF System of the 9 Gauged Diagonal Quadrics ($a_5 = 0$)

In the Euler/$F$ gauge $a_5 = 0$, the 9 exact rational RREF equations exported in [`results/one-reflection-skew-degree6/one-reflection-skew/degree-6-diagonal.json`](../results/one-reflection-skew-degree6/one-reflection-skew/degree-6-diagonal.json) are:

$$\begin{aligned}
Q_1 &: \quad a_0^2 - \frac{4}{3}a_0 a_4 + \frac{5}{6}a_1 a_2 + \frac{1}{3}a_1 a_3 - a_1 a_4 - \frac{5}{18}a_2^2 - \frac{2}{9}a_2 a_3 + \frac{5}{18}a_2 a_4 + \frac{47}{36}a_3^2 - \frac{14}{9}a_3 a_4 + \frac{17}{9}a_4^2 = 0, \\[4pt]
Q_2 &: \quad a_0 a_1 + a_0 a_4 - \frac{1}{2}a_1^2 - \frac{1}{4}a_1 a_2 + \frac{1}{2}a_1 a_3 + \frac{5}{12}a_2^2 - \frac{1}{6}a_2 a_3 + \frac{1}{12}a_2 a_4 + \frac{5}{12}a_3^2 + \frac{5}{6}a_3 a_4 - \frac{5}{6}a_4^2 = 0, \\[4pt]
Q_3 &: \quad a_0 a_2 + \frac{1}{4}a_1 a_2 - \frac{5}{4}a_2^2 + a_2 a_3 + \frac{1}{4}a_2 a_4 = \frac{1}{4}a_2(4 a_0 + a_1 - 5 a_2 + 4 a_3 + a_4) = 0, \\[4pt]
Q_4 &: \quad a_0 a_3 + \frac{1}{4}a_1 a_3 + \frac{1}{4}a_2 a_3 - \frac{1}{2}a_3^2 + \frac{1}{4}a_3 a_4 = \frac{1}{4}a_3(4 a_0 + a_1 + a_2 - 2 a_3 + a_4) = 0, \\[4pt]
Q_5 &: \quad a_0 a_4 - \frac{3}{4}a_1 a_3 + a_1 a_4 + \frac{1}{4}a_2 a_3 + \frac{1}{2}a_3^2 + \frac{1}{4}a_3 a_4 - a_4^2 = 0, \\[4pt]
Q_6 &: \quad a_1^2 - \frac{2}{3}a_1(a_2 + a_3 + a_4) + \frac{5}{9}(a_2^2 + a_3^2 + a_4^2) - \frac{2}{9}(a_2 a_3 + a_2 a_4 + a_3 a_4) = 0, \\[4pt]
Q_7 &: \quad a_1 a_2 - a_1 a_4 - \frac{7}{3}a_2^2 + \frac{34}{15}a_2 a_3 + \frac{4}{5}a_2 a_4 - \frac{53}{30}a_3^2 - \frac{2}{3}a_3 a_4 + \frac{1}{5}a_4^2 = 0, \\[4pt]
Q_8 &: \quad a_1 a_3 - a_1 a_4 - \frac{1}{3}a_2 a_3 + \frac{1}{3}a_2 a_4 - \frac{2}{3}a_3^2 + a_3 a_4 - \frac{1}{3}a_4^2 = \frac{1}{3}(a_3 - a_4)(3 a_1 - a_2 - 2 a_3 + a_4) = 0, \\[4pt]
Q_9 &: \quad a_1 a_4 + \frac{28}{3}a_2^2 - \frac{206}{15}a_2 a_3 - \frac{13}{15}a_2 a_4 + \frac{427}{30}a_3^2 - \frac{2}{3}a_3 a_4 + \frac{13}{15}a_4^2 = 0.
\end{aligned}$$

Notice that in addition to $Q_3$, $Q_4$, and $Q_6 = Q_{\text{node}}$, equation $Q_8$ also factors cleanly over $\mathbb{Q}$ as
$$3\,Q_8 = (a_3 - a_4)(3 a_1 - a_2 - 2 a_3 + a_4) = 0,$$
providing a second independent reflection-splitting relation alongside $Q_{\text{Kramers}} = (a_3 - a_4)(a_0 + a_1 - a_3 - a_4) = 0$.

---

## 4. Reproducibility

Run the complete verification and figure generation from the repository root:
```bash
python experiments/one_reflection_skew_degree6.py
```
To recompute all three packets from scratch (~49 seconds):
```bash
python experiments/one_reflection_skew_degree6.py --recompute
```

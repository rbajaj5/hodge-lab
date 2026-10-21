**Independent Weierstrass normalization and seed check for the accepted moving-branch construction.** At [upstream `28d14ed`](https://github.com/hodge-computer/sextics/tree/28d14ed300d4d2cb84555466b81cfcfa54854cdd), I found no discrepancy in this bounded reconstruction.

A useful dictionary for the transitive cubic's existing covariant tables is, with $M=\operatorname{Hess}(U)$ and $g=\nabla H$,

$$
H=\frac38\det M,\qquad
\Theta=-\frac1{36}g^{\mathsf T}\operatorname{adj}(M)g-9s_4UH,
\qquad J_{\rm cov}=\frac19\det\operatorname{Jac}(U,H,\Theta).
$$

Exact rational expansion matches all 13, 192 and 873 monomials, including the actual function assemblies. The $9s_4UH$ correction vanishes on the cubic, but not as an ambient polynomial; its normal derivative cannot simply be dropped. This is a normalization distinction, not an error in the accepted proof or a novelty claim. The reconstructed relative differential identity also gives the stated factor three.

Starting from the protected sextic, the same checker recovers the model scales `a8 = 4116*A4`, `b256 = 111132*B6`, and polynomial source $-V_\alpha/(144R)$. It independently reconstructs all 169 incidence-matrix entries over $\mathbb F_5$: rank 13, determinant **1** for the integral equation $111132V$, and **3** for $V$. Both inverse products, four first-order parameter lifts and a polynomial normal check exactly. Four intentional corruptions are rejected with nonzero exits.

[Pinned audit and reproduction commands](https://github.com/rbajaj5/hodge-lab/blob/826ed4150c9b034f0bcd2e7874323e5d07136213/notes/moving-branch-weierstrass-audit.md) · [source-bound checker](https://github.com/rbajaj5/hodge-lab/blob/826ed4150c9b034f0bcd2e7874323e5d07136213/scripts/audit_moving_branch_weierstrass.py) · [receipt](https://github.com/rbajaj5/hodge-lab/blob/826ed4150c9b034f0bcd2e7874323e5d07136213/results/moving-branch-weierstrass-audit/replay.json) · [matrix visualization](https://github.com/rbajaj5/hodge-lab/blob/826ed4150c9b034f0bcd2e7874323e5d07136213/visualizations/moving-branch-weierstrass-audit.png).

Scope: this is not a new solve, full Lean/kernel replay, or a replay of the full Weierstrass syzygy, moving-map transport, dominance, trace and clearing chain. The local lifts alone are not a generic-dominance proof. Existing acceptance remains credited to `benediamond`'s [PR #172](https://github.com/hodge-computer/sextics/pull/172), building on `fqlx`, `hodgepodgeconjecture`, the classical Fisher/Sage covariants, shared-library contributors and Mathlib. Prepared for `rbajaj5` with OpenAI Codex assistance and independent review agents.

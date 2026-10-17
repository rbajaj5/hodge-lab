# Cubic multipliers exclude the coordinate-divisible quadratic family

The previously unresolved family

$$
v_i=x_i\ell_i(x),\qquad \ell_i(x)=\sum_{j=0}^4M_{ij}x_j,
\qquad E=v\cdot\nabla\Delta
$$

is now excluded for every nonzero complex $5\times5$ matrix $M$. This is a complete 25-parameter degree-seven denominator-family result for the fixed `cyclic-triple-fano` target. The full 75-parameter quadratic-direction family remains unresolved.

The [previous batch](cyclic-fano-quadratic-polars.md) found no individual square in a modular coefficient-rowspace screen for this subfamily. Polynomial multipliers now supply cubic identities, followed by an exact rebuild. The old failed screen remains valid as a record of the narrower method's limit.

![Cubic identities and the five-parameter rebuild](../results/cyclic-fano-divisible-multipliers-figures/cyclic-fano-divisible-multipliers.png)

The [companion map figure](../results/cyclic-fano-divisible-multipliers-figures/cyclic-fano-divisible-multipliers-maps.png) displays the actual necessary-equation and multiplier maps. A colored matrix entry is eliminated by a checked identity, not by a numerical optimization score.

## Preserve the full equations

The protected $F,q=1,A$ and the source pinned at `d96911d725077e66a8f10848908be01a643b1714` are unchanged. We use the same weighted quotient

$$
G=Z^2+Q(x)Z+H(x),\quad \Delta=Q^2-4H,
\quad x=(X_0,X_1,Y_0,Y_1,Y_2),\quad\beta=X_0Y_0^3/3.
$$

For $L=v\cdot\partial$, the particular E1 solution and its residual remain

$$
P^0_{x_i}=-4\beta v_i,\qquad P^0_Z=2\beta L(Q),
\qquad P^0(G)=\beta E,
$$

$$
R_v=4\bigl[\beta L^2(\Delta)-(L(\beta)+\beta\,\mathrm{div}(v))L(\Delta)\bigr].
$$

All 55 reflection-compatible Koszul correction types are retained, including the five mixed types that first appear at degree seven. The preceding source-bound proof reconstructs the complete 230 raw Koszul fields, 246 quotient directions, Euler normalization, and reflection projection. This batch binds that proof and freshly reconstructs the two restricted physical coefficient systems. It does not count reading the earlier receipt as rerunning every earlier projection check.

The 25 parameters are ordered row by row in $M$. For this direction family, $L(\beta)=\beta(\ell_{X_0}+3\ell_{Y_0})$, while $\mathrm{div}(v)=\sum_i\ell_i+\sum_iM_{ii}x_i$. These terms are included; no divergence-free assumption is imposed.

## First eliminate corrections, then use polynomial multipliers

The initial physical map has 1,228 active rows and 1,700 formal columns: 325 parameter-quadratic columns and $25\cdot55=1,375$ parameter/correction products. Its exact rational rank is 833; the correction block has rank 678. Eliminating that block leaves 155 necessary quadrics $q_r(M)$.

Each quadric has an explicit rational functional on the physical coefficient rows. It annihilates every correction column and returns that quadric on the particular residual. The mixed products are allowed as independent formal columns for this elimination. This relaxation only gives necessary equations, which is sufficient for an obstruction: every actual choice of shared correction constants still satisfies them.

There is no isolated coordinate square in the exact span of these 155 quadrics. We therefore multiply each quadric by every one of the 25 parameter coordinates. The resulting degree-three map has 3,875 generators and 2,925 cubic monomial rows, with exact rank 2,892. Twenty cube identities are supplied:

$$
M_{ij}^3=\sum_{r=1}^{155}\lambda_{ij,r}(M)q_r(M),
\qquad j\in\{0,1,3,4\},
$$

where each $\lambda_{ij,r}$ is linear. There are 588 nonzero multiplier terms in total. The checker multiplies and sums the rational polynomials explicitly. Hence all twenty entries outside the $Y_0$ column vanish over $\mathbb C$.

This is stronger than the initial rowspace test because multiplication by parameters produces new necessary consequences. No generic-rank assumption or numerical zero threshold enters the deduction.

## Rebuild the remaining five directions

After those twenty proved vanishings, write

$$v_i=a_i x_iY_0.$$

The physical equations are rebuilt with all 55 corrections still present. The new map has 851 active rows and 290 columns: 15 pure quadratic columns and $5\cdot55=275$ mixed columns. Its exact rank is 232, including correction rank 220, leaving twelve necessary quadrics $p_r(a)$. Merely restricting the original 155 quadrics leaves a rank-nine space. Exact span inclusion shows that the rebuild supplies three additional independent quadrics; it does more than substitute zeros into the previous consequences.

Linear multiples of these twelve quadrics span all 35 cubic monomials in five variables. The packet contains five further identities

$$a_i^3=\sum_{r=1}^{12}\mu_{ir}(a)p_r(a),\qquad i=0,\ldots,4.$$

Thus the remaining five coefficients vanish as well. The conclusion is $M=0$, contradicting an admissible denominator in this family. The prior 75-direction injectivity witness applies to this subset: every nonzero $M$ yields a nonzero base polynomial $E$ and therefore a nonzero remainder modulo the monic polynomial $G$.

| Stage | Physical or multiplier map | Exact consequence |
| --- | --- | --- |
| Initial physical system | 1,228 × 1,700, rank 833 | 155 correction-free necessary quadrics |
| Initial cubic multipliers | 2,925 × 3,875, rank 2,892 | Twenty matrix entries vanish |
| Five-variable physical rebuild | 851 × 290, rank 232 | Twelve rebuilt necessary quadrics |
| Final cubic multipliers | 35 × 60, rank 35 | All five remaining entries vanish |

Although the rebuilt denominators have a common $Y_0$ factor, their exclusion is established by the rebuilt complete equations. Adding that factor can change the support, so the result is not inferred from the older degree-six diagonal obstruction alone.

## Attempts and reproduction

The first exact correction elimination completed in about 4.53 seconds. The modular degree-three screen at prime 1009 found the twenty candidate cube identities in about 1.78 seconds. Their rational discovery and explicit replay completed in about 56.99 seconds. Those discovery commands had 120-second subprocess limits; no timeout occurred.

Degree four was not run: the cubic identities and rebuilt cubic system already closed the family. A preliminary five-parameter radial probe was run as a fallback. It is subsumed by this full 25-parameter result and is not counted as an additional theorem or publication.

The aggregate primary `run` and `verify` commands have a 300-second envelope to accommodate the full batch and slower CI hosts. Verification replays exported identities and recomputes exact ranks without rediscovering the large tracked multiplier basis. This aggregate limit is distinct from the 120-second individual discovery limits.

Final source-bound production passed in 57.49 seconds and primary replay in 20.63 seconds locally. Eight primary mutation controls reject altered equations, multipliers, retained correction counts, rebuild parameter sets, parameter ordering, and source bindings.

```text
python -S experiments/cyclic_fano_divisible_multipliers.py run
python -S experiments/cyclic_fano_divisible_multipliers.py verify
python -S experiments/check_cyclic_fano_divisible_multipliers.py
python experiments/plot_cyclic_fano_divisible_multipliers.py
```

The [packet](../results/cyclic-fano-divisible-multipliers/packet.json) contains the parameter order, all 167 physical coefficient functionals, both multiplier certificates, source hashes, and the explicit projection-proof dependency. The [primary receipt](../results/cyclic-fano-divisible-multipliers/validation.json) and [independent receipt](../results/cyclic-fano-divisible-multipliers/independent-validation.json) document separate replay. Earlier `necessary-probe.json`, `cubic-probe.json`, and `exact-cubic-probe.json` remain discovery records; the final verifier reconstructs the fixed source and checks the final witnesses directly.

Independent replay passed all 167 physical functionals with 266,980 coefficient pairings, all 25 cube identities, the exact ranks, and the rank-nine to rank-twelve inclusion check. It additionally reran all 17,250 raw projection identities, 246 quotient checks, and 10,575 Euler-normalization identities from source. Thirteen independent altered-input controls were rejected.

This result settles the coordinate-divisible 25-parameter subfamily, not the general 75-parameter quadratic-direction family or arbitrary degree-seven denominators. It supplies no geometric support, Lean `HasCertificate` proof, or solution to the instance. For each fixed excluded member, the $q=1$ prescribed-support theorem has the additional power corollary described in the [support audit](cyclic-fano-support-audit.md); that theorem dependency is separate from the arithmetic identities. Separate excluded supports cannot automatically be combined into an exclusion of their union.

Credit: the upstream certificate and prescribed-support framework, the earlier fixed-target Koszul and reflection computations, and the Eisenbud-inspired use of syzygies and graded polynomial multipliers. OpenAI Codex assisted the construction, independent arithmetic review, and visualizations. Upstream discussion remains reserved for a substantial consolidated batch.

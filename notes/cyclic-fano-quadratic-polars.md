# Quadratic-direction polars: five complete subfamilies excluded

**Later continuation:** the [polynomial-multiplier follow-up](cyclic-fano-divisible-multipliers.md)
excludes the coordinate-divisible 25-parameter family that remained open in
this checkpoint. The unrestricted 75-parameter family remains unresolved.
The original failed screens and figures below are preserved.

For each of the five base coordinates $x_i$, every nonzero denominator

$$E=f(x)\,\partial_i\Delta,$$

with $f$ an arbitrary homogeneous quadratic polynomial is excluded for the fixed `cyclic-triple-fano` target. Each result covers all 15 coefficients of $f$ simultaneously and retains the complete numerator correction space.

The full family $E=v\cdot\nabla\Delta$, with five arbitrary quadratic components of $v$, has 75 parameters and **remains unresolved**. The five exclusions below do not exclude sums of these directions. The initial square-rowspace screen for that full family failed to give the degree-six shortcut.

![Quadratic-polar family coverage and actual coefficient maps](../results/cyclic-fano-quadratic-polars-figures/cyclic-fano-quadratic-polars.png)

The figure distinguishes exact component-family exclusions from finite-field observations on the unresolved larger families. Its row patterns encode actual coefficient arrays, not a picture of a geometric solution.

The [companion figure](../results/cyclic-fano-quadratic-polars-figures/cyclic-fano-quadratic-polars-maps.png) displays the full map and the rebuilt component maps.

## Fixed target and degree-seven equations

Continue the [linear-direction calculation](cyclic-fano-linear-polars.md) with the same frozen upstream source at `d96911d725077e66a8f10848908be01a643b1714`. The protected sextic, $q=1$, and $A$ are unchanged. Use

$$
x=(X_0,X_1,Y_0,Y_1,Y_2),\qquad
G=Z^2+Q(x)Z+H(x),\qquad
\Delta=Q^2-4H,\qquad \beta=X_0Y_0^3/3.
$$

The base coordinates have weight one and $Z$ weight three. Let $v_i$ be homogeneous quadratics, $L=v\cdot\partial$, and $E=L(\Delta)$. An explicit normalized E1 lift is

$$
P^0_{x_i}=-4\beta v_i,\qquad P^0_Z=2\beta L(Q),
\qquad P^0(G)=\beta E.
$$

Every one of the 75 basis lifts is checked upstairs against the original sextic by the [Piola reduction](cyclic-fano-transfer.md). The residual is

$$
R_v=4\bigl[\beta L^2(\Delta)-(L(\beta)+\beta\,\mathrm{div}(v))L(\Delta)\bigr].
$$

The divergence term is included. For a single component $v=f\partial_i$, all derivatives of $f$ cancel:

$$
R_v=4f^2\bigl(\beta\Delta_{ii}-\beta_i\Delta_i\bigr).
$$

The producer checks this rescaling identity in all 600 parameter-quadratic coefficients across the five component families. It simplifies the particular residual; it does **not** permit dropping any alternative numerator correction.

## New corrections that appear at this degree

At degree seven the complete weighted Koszul space has 230 generators. There are 50 base/base generators with linear multipliers, 175 base/$Z$ generators with base cubic multipliers, and five base/$Z$ generators with multiplier $Z$. The quotient freedom has weight six and dimension 246: 210 base sextics, 35 terms $Z$ times a base cubic, and $Z^2$.

Set $t=2Z+Q$. Reflection averaging under $t\mapsto-t$ leaves **55** correction types. Writing

$$W_{ij}=\Delta_i\partial_j-\Delta_j\partial_i,$$

their compact E2 images can be normalized as

$$
E\,W_{ij}(x_k)-x_kW_{ij}(E)
\quad (50\text{ types}),
\qquad
E\Delta_i-2\Delta\partial_iE
\quad (5\text{ types}).
$$

The last five are new relative to degree six and are essential. Explicit physical representatives are $4x_k(G_j\partial_i-G_i\partial_j)$ and $2t(G_Z\partial_i-G_i\partial_Z)$. They are differentiated before taking the monic remainder and reflection average. Substituting $t^2=\Delta$ into a field before computing its divergence would give an incorrect map.

The source reconstructs all 230 raw fields and verifies their projected images for all 75 denominator directions: 17,250 exact identities. It also verifies all 246 quotient images, including terms with $Z^3$ and $Z^4$ before reduction. The regular-gradient-sequence and Euler-normalization argument is the same as in the preceding packet; modulo five, the weighted gradient becomes nonzero multiples of $Z,x_0^5,\ldots,x_4^5$. The complete correction space is preserved.

## Failed larger screens and exact component reductions

The full coefficient map has 2,850 pure parameter-quadratic columns and 4,125 products of direction parameters with the 55 correction constants. There are 1,799 active spatial rows out of 1,820 possible degree-twelve base monomials. The rank is 1,759 **modulo 1009**. No individual parameter square belongs to that finite-field rowspace.

We also tried the 25-parameter family $v_i=x_i\ell_i(x)$ with independent linear forms $\ell_i$. Its map has 1,228 active rows and 1,700 columns, with rank 833 modulo 1009. This screen likewise isolated no individual square. These are bounded failed search strategies, not characteristic-zero obstructions or evidence that a certificate exists. Polynomial-multiplier searches on the full mixed family were not performed in this batch.

For the five families $v=f\partial_i$, we set the other four vector components to zero and rebuild the complete system. No correction parameter is specialized. Each first-stage map has 120 pure quadratic columns and $15\cdot55=825$ mixed columns. Exact coefficient functionals force the five coefficients of $x_0^2,\ldots,x_4^2$ in $f$ to vanish. Rebuilding with the ten cross-term coefficients leaves 55 pure quadratic columns and $10\cdot55=550$ mixed columns. A second set of exact functionals forces those ten coefficients to vanish.

| Only nonzero component | First-stage active rows / columns / rank | Second-stage active rows / columns / rank |
| --- | --- | --- |
| $X_0$ | 1,477 / 945 / 489 | 1,325 / 605 / 395 |
| $X_1$ | 1,359 / 945 / 493 | 1,240 / 605 / 395 |
| $Y_0$ | 1,426 / 945 / 493 | 1,289 / 605 / 395 |
| $Y_1$ | 1,572 / 945 / 495 | 1,446 / 605 / 395 |
| $Y_2$ | 1,383 / 945 / 491 | 1,268 / 605 / 395 |

These ranks and all 75 square identities are rational and exact. The coefficient functionals have 296 nonzero entries in total. Each is paired with every column of its complete restricted system; the result is precisely the square of one direction coefficient. Over $\mathbb C$ the coefficient must vanish. The second round is conditional on the first round's already proved vanishings, not a generic-rank assumption.

All 75 original denominator directions are independent. Select the coefficient rows $x_i^5m$, where $m$ runs over the 15 quadratic monomials for component $i$. They are distinct, and their coefficient minor is the identity modulo five. Its determinant is therefore nonzero in characteristic zero. Every nonzero direction produces a nonzero base polynomial and hence a nonzero monic remainder modulo $G$; no excluded case is merely a zero-denominator artifact.

## Scope and reproducibility

The result is stronger than an obstruction for $\partial_i\Delta$ alone: an arbitrary quadratic factor $f$ can add support components. Its exclusion here comes from fresh complete equations. It is not inferred by treating the new factor as a power of the old denominator. Conversely, the five separate component-family exclusions do not rule out mixed directions or unions of other supports.

For each *fixed* excluded $f\partial_i\Delta$, the repository's $q=1$ prescribed-support theorem additionally excludes its positive powers, under the hypotheses recorded in the [support audit](cyclic-fano-support-audit.md). That geometric corollary is separate from the finite arithmetic calculation and is not formalized by the Python checker.

The primary producer and primary replay commands have a 120-second subprocess bound. The initial full probe completed in approximately 2.41 seconds total, including 2.02 seconds for map construction and 0.38 seconds for the modular screen. The first exact component reconstruction took 5.05 seconds, and the final source-bound production and replay took 11.50 and 11.74 seconds locally. No timeout occurred. Nine primary mutation controls reject missing directions, omitted raw or compact corrections, missing quotients, modified square identities or rebuild assumptions, a changed map digest, and a false injectivity witness.

```text
python -S experiments/cyclic_fano_quadratic_polars.py run
python -S experiments/cyclic_fano_quadratic_polars.py verify
python -S experiments/check_cyclic_fano_quadratic_polars.py
python experiments/plot_cyclic_fano_quadratic_polars.py
```

The [final packet](../results/cyclic-fano-quadratic-polars/packet.json) binds the source, producer, arithmetic dependencies, all parameter labels, projection identities, and exact functionals. The full 6,975-column matrix is reconstructed from those formulas and checked against its canonical coefficient digest rather than duplicated as a large JSON array. The [primary receipt](../results/cyclic-fano-quadratic-polars/validation.json) and [independent receipt](../results/cyclic-fano-quadratic-polars/independent-validation.json) distinguish the two implementations. Intermediate `probe.json`, `subfamily-modular-probe.json`, `component-modular-probe.json`, and `component-exact-probe.json` remain historical diagnostics; final verification does not trust them.

Independent replay passed all 75 lifts, 10,575 Euler-normalization identities, 17,250 raw projection identities, 246 quotient checks, 600 rescaling identities, and all 75 square functionals. It reconstructed the full coefficient digest, all ten exact restricted-stage ranks, and both unsuccessful modular screens. Nine independent altered-input controls were rejected.

This batch supplies five complete denominator-family exclusions and two unsuccessful larger screens. It supplies no certificate, Lean proof, or solved instance. The next mixed-direction question would require additional algebraic consequences or a different construction; that work is not counted here.

Credit: the upstream authors' certificate and support framework; the supplied Dolgachev polar constructions; the Shafarevich averaging discussion; and the Koszul-syzygy method used throughout the notebook. OpenAI Codex assisted the construction, separate arithmetic review, and figures. No upstream post accompanies this batch.

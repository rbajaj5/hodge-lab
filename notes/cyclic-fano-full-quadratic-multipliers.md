# Nine exact vanishings in the full quadratic-direction family

Polynomial multipliers and two exact rebuilds reduce the full 75-parameter quadratic-direction family to 66 remaining coordinates. Nine coefficients must vanish for every certificate in this family. The remaining family is unresolved: this is partial progress, not an exclusion of all degree-seven denominators or a solution of `cyclic-triple-fano`.

The previous [coordinate-divisible result](cyclic-fano-divisible-multipliers.md) concerned a 25-parameter subfamily. Here every homogeneous quadratic vector field in five base coordinates is allowed from the start. None of the old subfamily vanishings is imposed on this larger family.

![Nine exact coordinate vanishings](../results/cyclic-fano-full-quadratic-multipliers-figures/cyclic-fano-full-quadratic-multipliers.png)

The [companion figure](../results/cyclic-fano-full-quadratic-multipliers-figures/cyclic-fano-full-quadratic-multipliers-maps.png) shows the actual necessary-quadric and character-block maps. Their ranks describe linear coefficient maps; they are not dimensions of a geometric solution space.

## Fixed target and complete correction space

The protected $F,q=1,A$ remain unchanged at source commit `d96911d725077e66a8f10848908be01a643b1714`. We retain the weighted quotient and target numerator

$$
G=Z^2+Q(x)Z+H(x),\qquad \Delta=Q^2-4H,\qquad
x=(X_0,X_1,Y_0,Y_1,Y_2),\qquad \beta=X_0Y_0^3/3.
$$

Write $v_i$ as an arbitrary quadratic polynomial in these five coordinates, with 15 coefficients per component, and put $L=v\cdot\partial$, $E=L(\Delta)$. The particular numerator and its E2 residual are

$$
P^0_{x_i}=-4\beta v_i,\qquad P^0_Z=2\beta L(Q),\qquad P^0(G)=\beta E,
$$

$$
R_v=4\bigl[\beta L^2(\Delta)-(L(\beta)+\beta\,\mathrm{div}(v))L(\Delta)\bigr].
$$

The divergence term is included. Every nonzero direction gives a denominator not identically zero on the hypersurface: the 75 coefficient rows $x_i^5m$ of $m\partial_i\Delta$ give the identity matrix modulo 5, and a nonzero base polynomial has nonzero remainder modulo the monic polynomial $G$.

We retain all 55 reflection-compatible correction types. They are the 50 linear base-pair fields and the five mixed fields from the [degree-seven projection proof](cyclic-fano-quadratic-polars.md). That source-bound proof covers all 230 raw Koszul fields, 246 quotient directions, and Euler normalization. The primary replay binds it and reconstructs the current coefficient maps. The independent checker also reconstructs the earlier projection identities directly from the fixed source.

For $W_{ij}=\Delta_i\partial_j-\Delta_j\partial_i$, the two compact correction images are

$$
E W_{ij}(x_k)-x_kW_{ij}(E),\qquad E\Delta_i-2\Delta E_i.
$$

These are obtained by differentiating the physical fields before taking the reflection-even remainder. In particular, replacing $t^2$ by $\Delta$ before computing divergence would change the second image incorrectly.

## Exact necessary equations and the first eight cubes

The complete initial map has 1,799 active coefficient rows and 6,975 formal columns: 2,850 parameter-quadratic columns and $75\cdot55=4,125$ mixed parameter/correction columns. Its exact rational rank is 1,759; the correction block has rank 1,348. Eliminating that block gives 411 necessary quadrics. Each has a saved rational functional on the original coefficient rows which annihilates every correction column.

Allowing the mixed products to vary independently is a relaxation of the actual shared correction constants. It produces necessary conditions valid for every certificate, without a generic-rank assumption. There is no isolated coordinate square in the exact span of these 411 quadrics.

Multiplying selected short quadrics by the 75 parameter coordinates gives eight exact cube identities. A subset of 140 quadrics, each having at most 64 terms, suffices: its 10,500 cubic generators have exact rank 10,450. The eight identities contain 106 nonzero multiplier terms in total. For example, in the saved initial quadric order,

$$
q_{401}=\tfrac12 a_{61}^2+a_{60}a_{65},\qquad
q_{402}=a_{61}a_{65},\qquad
a_{61}^3=2a_{61}q_{401}-2a_{60}q_{402}.
$$

Thus these eight coordinates vanish over $\mathbb C$ with all other coefficients unrestricted. The parameter order is component first, then the descending exponent order of the 15 quadratic monomials; raw indices are zero-based.

| Raw index | Vector-field coefficient forced to zero | Round |
|---:|---|---:|
| 8 | $X_1Y_2\,\partial_{X_0}$ | 1 |
| 13 | $Y_1Y_2\,\partial_{X_0}$ | 1 |
| 26 | $Y_0Y_2\,\partial_{X_1}$ | 1 |
| 28 | $Y_1Y_2\,\partial_{X_1}$ | 1 |
| 38 | $X_1Y_2\,\partial_{Y_0}$ | 1 |
| 53 | $X_1Y_2\,\partial_{Y_1}$ | 1 |
| 56 | $Y_0Y_2\,\partial_{Y_1}$ | 1 |
| 61 | $X_0X_1\,\partial_{Y_2}$ | 1 |
| 66 | $X_1Y_0\,\partial_{Y_2}$ | 2 |

## Rebuilding produces one more vanishing, then stops

After the first eight proved zeros, we reconstruct the physical equations on all 67 surviving directions, still retaining every correction type. Simply restricting the old quadrics has rank 391. Fresh elimination produces 396 independent quadrics, containing that old restricted span and five additional independent conditions.

A selected 147-quadric subsystem with at most 64 terms per quadric gives one new cube identity, for raw coefficient 66. Its 9,849 cubic generators have exact rank 9,744. The identity has 24 multiplier terms. A wider 254-quadric subsystem with at most 128 terms gave the same single cube; it took 82.22 seconds, compared with 3.00 seconds for the smaller successful replay.

Removing raw coefficient 66 and rebuilding gives 66 parameters and 393 independent quadrics. This time the restricted preceding span already has rank 393 and equals the fresh span. The selected cubic search finds no further coordinate cube. A small quartic search also finds no coordinate fourth power; both are explicitly restricted searches.

| Stage | Parameters | Physical rows × columns | Exact total / correction rank | Necessary quadrics | New proved zeros |
|---|---:|---:|---:|---:|---:|
| Initial | 75 | 1,799 × 6,975 | 1,759 / 1,348 | 411 | 8 |
| First rebuild | 67 | 1,793 × 5,963 | 1,732 / 1,336 | 396 | 1 |
| Second rebuild | 66 | 1,792 × 5,841 | 1,728 / 1,335 | 393 | 0 |

All 1,200 physical functionals and the nine cube identities are retained. They prove the listed vanishings over characteristic zero. They do not exclude the remaining 66-parameter family.

All nine forced coefficients lie outside the earlier coordinate-divisible subspace. The remaining coordinates consist of its 25 parameters and 41 other directions. Proving those other 41 coefficients vanish would reduce the problem to the already excluded 25-parameter family. That is a concrete possible continuation, not a deduction from the nine identities proved here.

## Attempts that did not improve the result

The cyclic grading is useful for limiting the attempted cubic search. Base coordinate weights modulo 6 are $(0,4,1,1,5)$. The defining polynomial $F$ and $\Delta$ are invariant, while $A$ and $\beta$ have character 3. This is an equivariant grading of the equations, not a pointwise symmetry of the whole target. A parameter $m\partial_i$ has weight $\mathrm{wt}(m)-\mathrm{wt}(x_i)$; a physical row contributes a quadric of weight $\mathrm{wt}(\text{row})-3$.

Every individual cube lies in character 0 or 3, so only those blocks are needed for this particular query. The full cubic monomial space has 73,150 rows. The two relevant blocks have 12,195 and 12,241 rows, with 5,140 and 5,153 generators. Both blocks are connected as support graphs; no additional support-only splitting was found.

Four modular attempts, two monomial orders for each block, stopped at explicit sparse-work limits before processing all generators. The limits were three million stored pivot coefficients or 100 million coefficient updates, plus a 180-second subprocess bound. All four stopped at work limits after approximately 12–18 seconds; none was a completed rank computation of its full block. The recorded ranks are ranks of processed prefixes. Their eight candidate cubes were subsequently proved over $\mathbb Q$ by the smaller exact subsystems. A missed modular target gives no characteristic-zero nonmembership claim.

The exact sparse-cubic progression was:

| Stage | Maximum terms per selected quadric | Selected cubic generators | Exact rank | Coordinate cubes found |
|---|---:|---:|---:|---:|
| 75 parameters | 4 | 2,700 | 2,683 | 2 |
| 75 parameters | 16 | 6,225 | 6,187 | 7 |
| 75 parameters | 64 | 10,500 | 10,450 | 8 |
| 75 parameters | 128 | 15,225 | 15,174 | 8 |
| 67 parameters | 4 | 2,814 | 2,773 | 0 |
| 67 parameters | 16 | 5,561 | 5,469 | 0 |
| 67 parameters | 64 | 9,849 | 9,744 | 1 |
| 67 parameters | 128 | 17,018 | 16,889 | 1 |
| 66 parameters | 4 | 2,640 | 2,601 | 0 |
| 66 parameters | 16 | 5,412 | 5,322 | 0 |
| 66 parameters | 64 | 9,438 | 9,336 | 0 |

Finally, the 40 shortest quadrics in the 66-parameter stage were multiplied by all 2,211 quadratic parameter monomials. This restricted quartic space has 88,440 generators and exact rank 85,051, and contains none of the 66 individual fourth powers. It is not the full degree-four space of the 393-quadric ideal. A larger multiplier search, different linear combinations of parameters, or further relations involving corrections could still yield information.

## Reproduce and inspect

The [manifest](../results/cyclic-fano-full-quadratic-multipliers/packet.json) binds the three compact rational proof packets, multiplier identities, failed modular attempts, fixed target, producer, and frozen dependencies. Compact monomial pairs and deterministic gzip avoid committing the roughly 81 MB verbose discovery representation. Gzip files are hashed as raw bytes, without text newline normalization.

```sh
python -S experiments/cyclic_fano_full_quadratic_multipliers.py verify
python -S experiments/check_cyclic_fano_full_quadratic_multipliers.py
python experiments/plot_cyclic_fano_full_quadratic_multipliers.py
```

Discovery can be rerun with the producer's `necessary`, `compact`, `small --stage N --threshold T`, `rebuild --stage N --threshold T`, and `quartic --stage 2 --threshold 4` commands. The canonical rebuild chain uses threshold 64. `cubic0`, `cubic3`, `forward0`, and `forward3` reproduce the bounded modular attempts. Discovery writes timing-bearing records, so regenerating them changes their manifest hashes. The compact packets, rather than the archived verbose discovery file, are the checked portable evidence.

The primary verifier reconstructs all three physical maps, replays their rational functionals and ranks, verifies the selected cubic identities and selected-subspace plateaus, and checks the rebuild inclusions. It does not rerun the four failed modular discovery searches. Individual primary discovery operations have 120-second bounds, modular screens 180 seconds, and the small quartic test 30 seconds; the aggregate primary replay has a 600-second envelope. The independent checker and figure command have their own execution environment rather than this wrapper.

The final primary replay passed in 87.29 seconds: 1,200 physical functionals, 4,717,490 coefficient pairings, nine cube identities with 130 multiplier terms, all three selected cubic spaces, the small quartic space, and eight negative controls. Exact rational checks also confirm that none of the individual coordinate squares lies in any of the three complete necessary-quadric spans.

The [separate implementation](../results/cyclic-fano-full-quadratic-multipliers/independent-validation.json) also passed: all 1,200 physical identities, 208 exact square queries, nine cubes and 130 multiplier terms, the three physical ranks and both rebuild gains, all eleven retained sparse-cubic attempts, the four modular prefixes, the restricted quartic calculation, and thirteen negative controls.

An initial verifier-development run was interrupted because its rational rank calculation used unsorted rows and accumulated excessive fill. The final replay orders rows by sparsity and spatial label; the interrupted attempt is retained and supplies no mathematical conclusion.

The motivation is Eisenbud's graded-ideal viewpoint: when linear combinations of quadratic equations cannot isolate a coordinate square, multiply the equations and look for a higher power; then rebuild the physical map after rigorously proved vanishings. Dolgachev's polar construction and the earlier reflection calculation supply the family being tested. This experiment computes selected graded consequences, not a minimal free resolution. It constructs no support, Lean proof, or accepted solution, and adds no upstream discussion post.

Credit also belongs to the upstream authors' certificate framework and the prior source-bound Koszul and reflection calculations. OpenAI Codex assisted the construction, separate arithmetic implementation, and visualizations. Independent replay here means a separate implementation of the arithmetic checks; it is not external peer review.

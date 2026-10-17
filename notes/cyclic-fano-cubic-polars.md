# Cubic directions: five exact exclusions and a correction-space syzygy

The next polar family has 175 parameters: each of five vector-field components is an arbitrary cubic polynomial in five base coordinates. This batch excludes **five separate 35-parameter component families**, each with all other components set to zero. It also derives 25 exact relations among the 175 projected correction types, making their span at most 150-dimensional for any fixed denominator in this family.

The full mixed-component 175-parameter family remains open. Excluding five coordinate subspaces does not exclude their sums. The fixed `cyclic-triple-fano` target is unchanged, and no solution, Lean proof, or upstream contribution is claimed.

![Five conditional component exclusions and the correction-space relation](../results/cyclic-fano-cubic-polars-figures/cyclic-fano-cubic-polars.png)

The [map companion](../results/cyclic-fano-cubic-polars-figures/cyclic-fano-cubic-polars-maps.png) shows actual coefficient maps. The component restrictions are conditions on the experiment, not globally proved vanishings in the unrestricted family.

## The larger denominator family

Continue with the fixed source at `d96911d725077e66a8f10848908be01a643b1714` and the weighted quotient

$$
G=Z^2+Q(x)Z+H(x),\qquad \Delta=Q^2-4H,\qquad
x=(X_0,X_1,Y_0,Y_1,Y_2),\qquad \beta=X_0Y_0^3/3.
$$

The weight of $Z$ is three; the five base coordinates have weight one. For a cubic base vector field $v$, write $L=v\cdot\partial$ and set

$$
E=L(\Delta),\qquad P^0_{x_i}=-4\beta v_i,\qquad
P^0_Z=2\beta L(Q).
$$

The denominator has degree eight, and the exact first equation is $P^0(G)=\beta E$. Its Piola lift satisfies the original first certificate equation for the unchanged $F,q=1,A$. The second-equation residual is

$$
R_v=4\left[\beta L^2(\Delta)-\bigl(L(\beta)+\beta\,\mathrm{div}(v)\bigr)L(\Delta)\right].
$$

There are 35 cubic monomials in the five base variables, hence 175 parameters. The weighted monomial $Z$ is explicitly excluded from this direction basis. It is not a cubic polynomial in the base variables.

All nonzero direction vectors are admissible in the required sense: their denominator is not identically zero on the hypersurface. The 175 coefficient rows $x_i^5m$ of $m\partial_i\Delta$ give the identity matrix modulo 5. Their monomials are distinct because a degree-eight monomial cannot have exponent at least five in two coordinates. Thus the 175 polars are independent over $\mathbb Q$ and $\mathbb C$, and a nonzero base polynomial has nonzero remainder modulo the monic polynomial $G$.

## Re-deriving the complete correction space

The degree-seven calculation used 55 projected correction types. Reusing that count would be incorrect here. Degree eight has 525 raw Koszul fields: 150 base-pair fields with quadratic multipliers, 350 mixed fields with base-quartic multipliers, and 25 mixed fields with a $Z$ times linear multiplier. The quotient space has 636 monomials of weight eight.

Let

$$
W_{ij}=\Delta_i\partial_j-\Delta_j\partial_i.
$$

Reflection-even projection leaves 150 base-pair types, indexed by quadratic $h$, and 25 mixed types, indexed by a base coordinate $i$ and a linear $h$:

$$
C_{ij,h}(E)=E W_{ij}(h)-h W_{ij}(E),
$$

$$
M_{i,h}(E)=h\bigl(E\Delta_i-2\Delta E_i\bigr)
             +2\Delta E\,\partial_i h.
$$

The final derivative term is essential. It comes from differentiating the multiplier in the actual vector field. Projection is performed after differentiation; substituting $t^2=\Delta$, with $t=2Z+Q$, before taking divergence would alter the operator.

The producer checks the projected divergence and five base components of every raw field: 3,150 exact operator-coefficient identities. They establish the correction formula for every base denominator, without sampling 175 particular denominators. All 636 quotient directions project to zero. The weighted Euler identities are checked through 246 gauge monomials and the degree-eight homogeneity of all 175 denominators, implying all 43,050 normalization identities.

Completeness uses the regular gradient sequence already underlying the certificate normalization. The exact reduction modulo 5 is $G=Z^2+\sum_i x_i^6$; its gradient has only the origin as a common zero. The packet records this control, the exact first-equation lifts, projection, and normalization checks.

## A universal syzygy reduces 175 correction types to a span of at most 150

For each pair of base indices $i,k$, the correction operators satisfy

$$
\sum_j C_{ij,x_jx_k}(E)+3M_{i,x_k}(E)=0.
$$

Here $W_{ii}=0$ and reversing an ordered pair reverses its sign. Before using homogeneity, the left side is exactly

$$
x_k\Delta_i\left(8E-\sum_j x_jE_j\right).
$$

Euler's identity makes this zero for a homogeneous degree-eight $E$. Each relation expresses one mixed type in the span of the 150 base-pair types. The checks compare the constant and derivative coefficients of this operator identity; the claim holds for all degree-eight base polynomials, including mixed-component polars.

Thus 175 is the number of retained generator types, not an assertion of linear independence. The span has rank at most 150 for a fixed $E$. The component-family tests below still retain all 175 types. The exact relation makes this redundancy explicit instead of silently dropping corrections.

## Five component families, each reduced from 35 to zero

Fix one coordinate $i$ and allow an arbitrary cubic $f$ in

$$
v=f\partial_i,\qquad E=f\Delta_i.
$$

The derivatives of $f$ cancel in the particular residual:

$$
R_v=4f^2\bigl(\beta\Delta_{ii}-\beta_i\Delta_i\bigr).
$$

Every compatible numerator correction is nevertheless allowed; the particular residual alone is not the test. Allowing the parameter/correction products to vary independently gives a relaxed necessary system. Exact coefficient functionals eliminate all of its correction columns and produce rational quadrics in the 35 coefficients of $f$.

The first direct query fails in each family: no individual coordinate square belongs to the complete physical rowspace. These five exact failed queries are retained. Passing to polynomial multipliers changes the outcome. The reduced necessary quadrics have cube identities for all 25 coefficients whose cubic monomial contains a repeated coordinate: five pure cubes and twenty square-times-another-coordinate monomials.

Only ten squarefree cubic monomials remain. Reconstructing the complete physical map on these ten parameters gives 45 necessary quadrics, whose reduced basis contains all ten individual coordinate squares. They therefore vanish as well. The portable files use a uniform cubic-identity format; the final ten one-term identities are simply multiples of those simpler square equations.

| Component allowed | Initial rows × columns | Initial exact total / correction rank | Initial quadrics | Rebuilt rows × columns | Rebuilt exact total / correction rank |
|---|---:|---:|---:|---:|---:|
| $X_0$ | 2,793 × 6,755 | 1,687 / 1,479 | 208 | 2,348 × 1,805 | 1,019 / 974 |
| $X_1$ | 2,727 × 6,755 | 1,699 / 1,490 | 209 | 2,334 × 1,805 | 1,017 / 972 |
| $Y_0$ | 2,793 × 6,755 | 1,697 / 1,488 | 209 | 2,378 × 1,805 | 1,013 / 968 |
| $Y_1$ | 2,900 × 6,755 | 1,745 / 1,536 | 209 | 2,522 × 1,805 | 1,029 / 984 |
| $Y_2$ | 2,738 × 6,755 | 1,675 / 1,466 | 209 | 2,348 × 1,805 | 1,024 / 979 |

The first cubic multiplier spaces have 7,280 generators for $X_0$ and 7,315 for the other components; all have exact rank 5,590. Each final ten-parameter space has 450 cubic generators spanning all 220 cubic monomials. Across the five conditional proofs, 1,269 physical consequences and 175 cube identities with 344 multiplier terms are retained.

Unlike several earlier batches, these rebuilds add no independent quadratic condition: the restricted preceding quadrics already have rank 45 and span the fresh 45-dimensional space. Rebuilding checks the complete restricted physical equations and exposes a smaller system, but is not claimed to strengthen their eliminated span here.

These are five joint family exclusions, not 175 globally forced coefficients. In each proof the other four vector-field components were assumed zero from the outset. Mixed directions remain an open possibility. An arbitrary cubic factor can add a new support component, so the result is also more than merely retesting a higher power of an earlier fixed denominator.

## GPU tests and exact finite-field witnesses

![The fixed-direction GPU screen and its exact rank certificate](../results/cyclic-fano-cubic-polars-figures/cyclic-fano-cubic-gpu-shortcut.png)

The separate [GPU experiment](../results/cyclic-fano-cubic-gpu/report.json) tests 16 fixed directions, including five monomial controls and eleven mixed or seeded directions. For each, it builds the complete 175-column correction map and the actual residual. The CUDA calculation finds correction rank 150 and augmented rank 151 modulo 65,521; CPU modular calculations check the same ranks. Solvable right-hand-side controls have augmented rank 150.

The exact universal syzygies above supply a characteristic-zero upper bound of 150 on the correction rank. A nonzero augmented $151\times151$ minor modulo a prime of valid reduction supplies a characteristic-zero lower bound of 151 on the augmented rank. Together these are an exact fixed-direction obstruction over $\mathbb Q$ and $\mathbb C$. The modular minor and operator identities, rather than a floating-point rank estimate, are the evidence. The [separate replay](../results/cyclic-fano-cubic-polars/independent-validation.json) checks the source reconstruction, universal relations and exported minors. These finite tests do not settle the whole 175-parameter family.

Recorded elimination timings are approximately 0.192 seconds on the GPU versus 14.175 seconds for the NumPy modular path on the same 32 matrices. Source construction took about 16.894 seconds; compilation and transfers are excluded from those elimination timings. This is not a general end-to-end speedup claim. The GPU experiment is supplementary to the rational component-family proof and is not required for its replay.

## Bounds, failures, and reproduction

The [packet](../results/cyclic-fano-cubic-polars/packet.json) binds the unchanged target, all 175 direction labels and lifts, the complete projection operators, the ten physical-stage files, basis changes, multiplier identities, and 26 completed attempt records. The five initial square searches were unsuccessful despite completing exactly. No discovery timeout occurred in this batch. The longest recorded extraction took about 24.71 seconds, under its 120-second bound.

The unrestricted formal map would have 3,060 potential spatial rows and 46,025 columns: 15,400 parameter-quadratic and 30,625 mixed parameter/correction columns. That full map was not constructed in this bounded batch. No failed full-family search or full-family rank is inferred from its dimension count.

```sh
python -S experiments/cyclic_fano_cubic_polars.py verify
python -S experiments/check_cyclic_fano_cubic_polars.py
python experiments/plot_cyclic_fano_cubic_polars.py
```

Discovery commands are `component`, `necessary`, and `cubic`, with `--component 0` through `--component 4`; `--round 1` reconstructs or searches the surviving ten parameters. Each cubic search uses `--threshold 64`, which includes every reduced quadric in the corresponding saved stage. `projection` replays the operator calculations; `run` assembles source bindings. Individual primary commands have 120-second bounds, and aggregate primary verification has a 600-second envelope. The independent checker and figure commands are separate programs. Proof replay uses standard-library rational arithmetic and needs no external algebra system or GPU.

The [primary replay](../results/cyclic-fano-cubic-polars/validation.json) passed in 103.24 seconds on this run. It reconstructs the ten physical systems, checks all 1,269 necessary coefficient consequences and their equivalent bases, replays all 175 cube identities and multiplier-space ranks, verifies the initial square-query failures, and rejects 14 mutation controls. The [independent reconstruction](../results/cyclic-fano-cubic-polars/independent-validation.json) also passes: it reconstructs the complete source operators, all ten physical stages, all basis transformations and cube identities, the five failed initial square queries, and the zero-gain rebuild checks. It checks 7,458,345 physical coefficient pairings and rejects 53 altered inputs. Its separate fixed-direction audit verifies all sixteen exported augmented minors together with the exact rank upper bound.

The motivation remains Eisenbud's graded-ideal and syzygy viewpoint: linear coefficient queries can fail while polynomial combinations yield exact powers, and explicit relations explain redundancy in a correction module. Dolgachev's polar construction supplies the family; credit also belongs to the upstream certificate framework and the preceding weighted-quotient, Koszul, and reflection calculations. Codex assisted construction, a separate arithmetic implementation, GPU tests, and visualizations. Separate implementation checks are not external peer review.

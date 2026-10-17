# Closing the quadratic-direction polar family

Exact polynomial identities and complete coefficient-map rebuilds exclude the full **75-parameter homogeneous quadratic-direction polar family** for `cyclic-triple-fano`. The previous batch reduced it to 66 coordinates. This continuation proves 56 more coordinates vanish, then embeds the ten survivors into the previously excluded coordinate-divisible family and replays that proof.

This is an exclusion of a specified denominator family. It is not an exclusion of arbitrary degree-seven denominators, a certificate of existence, a Lean `HasCertificate` proof, or a solution of the instance. The fixed defining polynomial $F$, $q=1$, and target $A$ are unchanged. No upstream comment accompanies this batch.

![The exact reduction and final subfamily closure](../results/cyclic-fano-remaining66-multipliers-figures/cyclic-fano-remaining66-multipliers.png)

The [map companion](../results/cyclic-fano-remaining66-multipliers-figures/cyclic-fano-remaining66-multipliers-maps.png) shows coefficient maps and exact changes of equation basis. Matrix rank and search-space size are not dimensions of a geometric solution space.

## Family, source, and correction coverage

We use the unchanged source at `d96911d725077e66a8f10848908be01a643b1714`, with its weighted quotient

$$
G=Z^2+Q(x)Z+H(x),\qquad \Delta=Q^2-4H,\qquad
x=(X_0,X_1,Y_0,Y_1,Y_2),\qquad \beta=X_0Y_0^3/3.
$$

Each component of $v$ is an arbitrary homogeneous quadratic in the five base coordinates. Write $L=v\cdot\partial$ and $E=L(\Delta)$. There are 75 coefficients. A particular numerator satisfying $P^0(G)=\beta E$ is

$$
P^0_{x_i}=-4\beta v_i,\qquad P^0_Z=2\beta L(Q).
$$

Its residual is

$$
R_v=4\left[\beta L^2(\Delta)-\bigl(L(\beta)+\beta\,\mathrm{div}(v)\bigr)L(\Delta)\right].
$$

The divergence term is retained. The [degree-seven projection proof](cyclic-fano-quadratic-polars.md) covers all 230 raw Koszul fields, all 246 quotient directions, and Euler normalization. Every stage here retains all 55 surviving correction types: 50 linear base-pair fields and five mixed fields. Reflection is applied after differentiation, so the mixed corrections are not lost by prematurely reducing $t^2=\Delta$.

As proved in that source-bound calculation, the 75 denominator directions are independent: the coefficient minor on monomials $x_i^5m$, where $m$ runs through the quadratic monomials, is the identity modulo 5. Every nonzero $v$ therefore gives an $E$ not identically zero on the hypersurface; a nonzero base polynomial has nonzero remainder modulo the monic polynomial $G$.

The physical equations are quadratic in the denominator parameters and linear in products of denominator and correction parameters. For elimination, these mixed products are allowed to vary independently. This relaxes the system, giving necessary conditions for every genuine numerator. Consequently an impossibility in the relaxed system excludes the actual certificate family. No generic rank or special choice of correction coefficients is assumed.

## An equivalent equation basis unlocks the first reduction

The starting point is the frozen [66-parameter stage](cyclic-fano-full-quadratic-multipliers.md), with 393 necessary quadrics. Its selected cubic and small quartic searches had stopped without another vanishing. This time we first put the necessary quadrics in rational reduced row echelon form, saving every new equation as an exact combination of the original physical consequences.

This does not add a new equation to their span. It exposes more short equations: the number having at most four terms increases from 40 to 76. The total term count actually increases from 41,288 to 47,734, so this is not a uniform sparsity improvement. The useful change is the presence of short combinations that the previous threshold-based search did not select.

A cubic search using the reduced equations with at most 64 terms proves that raw parameter 46 has cube zero. The saved identity uses 131 multiplier terms and all 66 parameters remain unrestricted during its derivation. Here and below, a raw index refers to the original 75-parameter basis: component first, then the descending exponent order of the 15 quadratic monomials. Raw 46 is the coefficient of $X_0X_1\partial_{Y_1}$.

The original-basis threshold-128 cubic attempt timed out after 120 seconds without a completed rank. The reduced-basis threshold-64 search completed in about 1.75 seconds. These are recorded individual runs, not a general performance guarantee.

## Cubic and quartic identities, followed by complete rebuilds

For necessary quadrics $q_r(a)=0$, the packet records identities of the form

$$
a_i^3=\sum_r L_r(a)q_r(a),\qquad
a_i^4=\sum_r Q_r(a)q_r(a),
$$

with rational linear or quadratic multipliers. Multiplying and summing coefficients verifies each identity directly. Over $\mathbb C$, either identity forces $a_i=0$.

The larger quartic systems are searched with a sparse elimination history. A pivot stores its source generator and earlier pivot dependencies. Only the histories needed for successful coordinate powers are expanded into explicit multipliers. The verifier checks the expanded identities rather than trusting that search history.

After each proved set of zeros, the complete physical map is reconstructed with every correction type still present. Rebuilding matters because correction products attached to vanished denominator coordinates disappear before elimination. The resulting conditions can be stronger than merely restricting previously eliminated quadrics.

| Parameters before stage | Physical rows × columns | Exact total / correction rank | Necessary quadrics | Selected new powers | Parameters left |
|---:|---:|---:|---:|---|---:|
| 66 | 1,792 × 5,841 | 1,728 / 1,335 | 393 | 1 cube | 65 |
| 65 | 1,792 × 5,720 | 1,726 / 1,334 | 392 | 5 fourth powers | 60 |
| 60 | 1,778 × 5,130 | 1,677 / 1,289 | 388 | 4 cubes, 3 fourth powers | 53 |
| 53 | 1,693 × 4,346 | 1,516 / 1,190 | 326 | 5 cubes, 3 fourth powers | 45 |
| 45 | 1,655 × 3,510 | 1,434 / 1,120 | 314 | 8 cubes | 37 |
| 37 | 1,510 × 2,738 | 1,232 / 978 | 254 | 15 cubes, 1 fourth power | 21 |
| 21 | 1,187 × 1,386 | 774 / 656 | 118 | 11 cubes | 10 |

These 56 selected identities contain 2,467 multiplier terms. They are 44 cubes and 12 fourth powers. Higher degree is not always necessary: at the 45-parameter stage, raw $a_{35}^2$ is already a single reduced equation. The 37-parameter stage directly contains the squares of raw coordinates 24, 30, 43, 60, and 63, and the 21-parameter stage directly contains the square of raw coordinate 42. Their selected cubes are valid multiples of these simpler consequences.

The exact restricted-old ranks and fresh rebuilt ranks are respectively $391\to392$, $377\to388$, $319\to326$, $301\to314$, $228\to254$, and $98\to118$. In every case the old restricted span is contained in the fresh span. Thus the successive rebuilds add 1, 11, 7, 13, 26, and 20 independent quadratic conditions. These are gains in equation spaces, not a claim about the geometric codimension of their zero sets.

The first quartic success is concrete: at 65 parameters, the 94 reduced quadrics with at most eight terms, multiplied by all 2,145 quadratic parameter monomials, give 201,630 generators of exact rank 188,344. Five coordinate fourth powers have explicit identities, containing 543 terms in total. The complete correction space is retained in the physical consequences used by those identities.

## Closing the last ten using the earlier 25-parameter proof

The ten surviving raw coordinates are

$$
\{0,2,16,21,32,39,48,55,64,71\}.
$$

All lie in the [coordinate-divisible subfamily](cyclic-fano-divisible-multipliers.md), where $v_i=x_i\ell_i(x)$ and each $\ell_i$ is linear. Their positions in that proof's 25-coordinate ordering are

$$
\{0,2,5,7,10,12,15,17,20,22\}.
$$

The manifest binds the older packet and both its receipts, and records this embedding explicitly. The new primary replay checks its two physical maps again from the current fixed source, then replays the 20 initial cube identities and five final cube identities. The old argument excludes all 25 directions jointly, so it also excludes this ten-dimensional coordinate subspace; it is not an inference from separately testing ten denominators.

Together with the earlier nine vanishings, this closes the full 75-parameter quadratic-direction polar family. The prior partial-progress notes and failed runs remain unchanged as historical records. This conclusion does not say that arbitrary degree-seven supports fail, or that independently excluded supports can never contribute when combined in an untested way.

## Failed, slower, and supplementary attempts

The manifest retains all 25 attempt records: 22 completed searches or proof extractions and three timeouts. Completed search and proof files can refer to the same multiplier space; they are not counted as independent mathematical results.

- A full 393-quadric Singular search modulo 1009 with degree bound 3 stopped at a 60-second process limit, after about 65.64 seconds including WSL overhead. It exported no candidates. No full degree-four CAS computation was inferred or automatically repeated.
- The original 66-variable threshold-128 cubic search timed out at 120 seconds. The corresponding reduced-basis searches succeeded; this does not establish a general best monomial order.
- At 65 variables, the completed reduced cubic searches with thresholds 64 and 128 found no individual cube in their selected spaces. The quartic calculation supplied the next step.
- At 53 variables, the threshold-128 cubic search also timed out at 120 seconds. The smaller cubic search and the bounded quartic search supplied complementary exact powers.
- At 37 variables, cubic thresholds 16, 32, and 64 found the same 15 coordinate cubes. The recorded runs took about 2.10, 9.54, and 103.47 seconds respectively. The final proof selects short witnesses; a wider attempted space is not assumed to be more useful.

The separate checker also records a failed attempt to shorten the first cube proof through a particular cubic product. Its exact selected-space failures are diagnostic, not a claim that the product lies outside the whole ideal. A timeout supplies neither a rank nor a nonmembership theorem. A completed selected-space failure concerns only that explicitly specified span.

An additional [GPU screen](../results/cyclic-fano-powers-gpu/report.json) evaluates the 56 selected identities on an RTX 5070 Ti Laptop GPU at 4,096 sampled parameter points for each of two finite fields, of primes 65,521 and 65,519. All 458,752 evaluations vanish as required. Altering one multiplier coefficient by one is detected for every identity at both primes, and eight CPU points per identity per prime match the GPU. This is an independent computational path for sampled values, not the proof of the polynomial identities or of correction completeness. Its coverage is the 56 new identities; the older nine vanishings and final subfamily closure are checked separately by the rational verifiers. CUDA is optional and is not required by the exact verifier.

Run the [CUDA script](../experiments/gpu_cyclic_fano_powers.py) with
`python experiments/gpu_cyclic_fano_powers.py` in an environment with CuPy,
or supply `--deps PATH` for an existing isolated dependency directory.
The report records the GPU, seed, source hashes, coefficient mutations and
timings. Timing excludes compilation and transfers; no CPU speedup is claimed.

## Reproduce and inspect

The [manifest](../results/cyclic-fano-remaining66-multipliers/packet.json) binds the unchanged target, frozen prior inputs, all seven physical stages, exact changes of basis, chosen powers, closure embedding, and attempt records. Polynomial pairs and deterministic gzip keep the artifacts compact. Gzip hashes use raw bytes; the optional Singular source and log use explicitly declared LF-normalized text hashes.

```sh
python -S experiments/cyclic_fano_remaining66_multipliers.py verify
python -S experiments/check_cyclic_fano_remaining66_multipliers.py
python experiments/plot_cyclic_fano_remaining66_multipliers.py
```

The producer's `reduce`, `cubic`, `quartic`, `quartic-proof`, `combine`, and `rebuild` commands reproduce discovery stages. Use `--stage N --basis reduced --threshold T --bound 120` where applicable; `rebuild --degree 0` consumes the preceding selected union. The root's short cubic probes are reproducible with the same cubic command and `--bound 30`. Discovery records include elapsed times, so regenerating them changes their hashes. `run` assembles the manifest; it does not rediscover all searches.

Primary individual searches have explicit bounds, normally 120 seconds; the optional Singular run has 60 seconds, and the aggregate primary replay has a 900-second envelope. The independent checker and plotting commands are separate programs without that wrapper. Verification replays saved rational identities and completed subspace ranks, retaining the timeouts without rerunning them. No external CAS is needed for proof replay.

The [primary replay](../results/cyclic-fano-remaining66-multipliers/validation.json) passed in 298.14 seconds on this run. It checks all 2,185 physical consequences through 5,402,563 coefficient pairings, the seven equivalent equation bases, all 56 selected powers, and all 22 completed attempt spaces. It additionally replays the older 167 physical consequences and 25 cube identities needed for the final subfamily closure. Eighteen corrupted-proof or binding controls are rejected. The three discovery timeouts are preserved without being rerun.

The [separate implementation](../results/cyclic-fano-remaining66-multipliers/independent-validation.json) also passed: all seven physical stages, 2,185 necessary quadrics and their exact changes of basis, the 56 powers with 2,467 multiplier terms, all 25 retained attempt records, and a fresh replay of the older 167 physical consequences and 25 cubes establishing the final closure. It also rechecks the full projection and Euler-normalization identities from the fixed source and rejects 29 mutation controls. Both implementations agree on the full-family conclusion and its stated limits.

Eisenbud's syzygy and graded-ideal viewpoint motivates multiplying necessary equations and rebuilding after rigorously forced zeros. Dolgachev's polar construction supplies the denominator family; the upstream certificate framework, weighted quotient, and previous exact Koszul/reflection calculations supply the complete equations. This computes selected graded consequences, not a minimal free resolution. OpenAI Codex assisted construction, separate arithmetic implementation, and visualizations. Independent replay here means another implementation of the arithmetic checks, not external peer review.

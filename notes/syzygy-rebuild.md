# Rebuilding syzygies after proven vanishings

Published as [our fifth contribution to holdout Discussion 44](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18985755),
with [full CI passing on the immutable proof commit](https://github.com/rbajaj5/hodge-lab/actions/runs/38985896164).

**Family 115 is excluded.** Its characters are `(0,0,1)`, `(1,2,3)`,
and `(4,2,3)` in the Hodge Lab triple convention. This raises coverage to
**134/136** fixed-`X0/Y0` extensions, or **134/152** families in the original
combined selection. Families **16** and **137**, with third characters
`(0,1,0)` and `(5,3,0)`, remain unresolved. This is not an unrestricted
three-character exclusion: there are 428,536 possible triples. The degree
lower bound remains at least seven; no existence certificate, Lean
`HasCertificate` proof, solve PR, or leaderboard point is claimed.

![Proof dependencies and actual cancellation support](../results/degree7-syzygy-rebuild/syzygy-proof-map.png)

The picture is generated from the proof packet, not a geometric simulation.
Each heatmap row is a necessary relation; each column is an original physical
equation. Brightness counts multiplier monomials, capped at four for display.
It does not measure numerical conditioning, importance, or coefficient size.
The arrows summarize dependencies, not every intermediate substitution.

## Fixed system and inherited reductions

The protected target remains at upstream
`b8c4edeb80a82395ec07164caf445cfa43bbbd56`, with `q=1`, `A=X0^3 Y0^3`,
and the exact `F` from `sources/sextics/data/holdout/instance.rec`.
No existing upstream file is changed. We use the complete E1 denominator
space modulo `F*S1`, the complete numerator correction space allowed by the
order-36 stabilizer, and an unrestricted quotient by `F`.

After the verified first pass, the family has these 15 denominator directions:

```text
[6,42,56,88,102,111,114,115,133,168,211,234,271,285,288].
```

These are Hodge Lab zero-based raw basis indices. Let their coefficients be
`a0,...,a14`. Only `a0` and `a10` belong to the third character. All 58 relevant
Koszul corrections remain available. The system has 255 physical coefficient
equations. In each of the two normalized charts, the
[preceding packet](polynomial-syzygies.md) proves `a2=a9=0` by cubic identities.
It also supplies the affine denominator maps used here. Those dependencies
are replayed, not assumed from their reported outcome.

## Close chart 10 first

On `a10=1`, substitute the verified denominator maps into the full equations

```text
E(a,z) = R(a) z + b(a) = 0.
```

Recompute polynomial left syzygies of `R(a)`. The constant-multiplier baseline
has nine denominator-only equations. Allowing affine multipliers gives 121
linearly independent denominator consequences; thirteen extend the span of
affine multiples of the baseline. This is a bounded vector-space comparison,
not independence modulo the full ideal or radical. We retain all 121 exported
identities, while the proof uses the nine baseline plus thirteen selected
relations. The rebuilt system has eleven active denominator variables.

The degree-three and degree-four power searches still find no additional
coordinate vanishing. At **total product degree five**, exact combinations of
the 22 necessary equations give

```text
a4^2 = 0    (419 polynomial-multiplier monomials),
a5^2 = 0    (430 polynomial-multiplier monomials).
```

Thus `a4=a5=0` over C. After those substitutions, a degree-four combination
with 56 multiplier monomials gives `a1^4=0`. Thus `a1=0` as well. These three
identities use **905 multiplier monomials** in total. The degree bound refers
to each multiplied equation, not just its multiplier.

Apply those zeros to the original physical equations. Verified affine
elimination then gives a contradiction. In the resulting coordinates the
last identity is

```text
(-108/5) E13 + (108/5) E15 - (108/5) E34 - (108/5) E190 = 1.
```

The row numbers are zero based. This formula requires all preceding checked
substitutions; it is not asserted for the unreduced equations.

The normalized chart `a10=1` is therefore impossible. Homogeneity and
simultaneous scaling of `D,N` imply **a10=0 throughout this family**.

## Use the excluded chart to close chart 0

Now normalize `a0=1`. Replay its earlier denominator reductions and set
`a10=0`, justified by the newly excluded chart. The physical affine/square
routine closes directly: nine affine inferences followed by a 21-row rational
combination equal to 1. No new syzygy search is needed in this refined chart.

Both third-character coordinates vanish. The preceding complete `X0/Y0`
pair exclusion rules out the remaining denominator. The checker verifies
that the two charts cover exactly the third component, and refuses the
refinement if chart 10 has not already been proved impossible.

## The other families and failed approaches

Every remaining third-component chart was attempted in the two larger
families, retaining all 256 allowed corrections in each. Family 16 has pivots
`7,10,11,12,13`; family 137 has `8,11,13,16,17`. Each complete affine-multiplier
attempt hit its **120-second wall limit**. This is inconclusive. A checkpoint
export was added after the first four timeouts; six later runs retain partial
syzygy bases. Their multiplier lists are explicit, and none is claimed to
span the complete affine search space. The first four runs exported no packet.

Two retained checkpoints were continued: family 16 on `a13=1`, and family
137 on `a8=1`. Both prove local-coordinate `a1^3=a9^3=0`, using twenty
multiplier terms per chart. After these substitutions, the configured
degree-four search and physical check remain unresolved. Both polynomial
implementations replay these identities. These are **conditional chart
consequences**, not globally proved zeros throughout either family.

Other attempts are preserved in [the experiment log](../results/degree7-syzygy-rebuild/experiments.json)
and [archived inputs](../results/degree7-syzygy-rebuild/exploratory-inputs.zip):

- Rebuilding both family-115 charts and stopping at degree four failed to
  close either. The original failed packets remain alongside the continuation.
- Full necessary-ideal Gröbner computations reported a unit for both rebuilt
  charts, but their direct multiplier exports hit 120 seconds. The unit reports
  alone were not used as portable proof.
- A smaller seven-variable subsystem of chart 0 also has a CAS unit. Its
  complete multiplier export was about 39 MB. It was superseded before replay
  by the shorter chart-10-first argument. The source and output hash are saved;
  the unused large output remains local and is not part of the proof packet.
- After proving a squared linear form vanishes in that subsystem, coordinate
  power searches through degree six still found no further power or unit.
  This illustrates a limitation of that particular coordinate-based search.
- Two quadratic-multiplier syzygy searches were cancelled when the smaller
  affine necessary ideals supplied the more promising lead. A full chart-0
  degree-five search was cancelled once the excluded chart-10 coordinate
  closed chart 0 directly. Cancellations are not counted as exhausted bounds.

## Later small follow-up: two global family-16 zeros

This paragraph and its files were added after the immutable family-115 proof
commit `b366f33c5a9421532d452ec4d15588c5f9998b7f`; they are not part of the
fifth upstream post's packet. On family 16, composing the two cube identities
back to physical rows leaves multipliers of degree at most one. Homogenize
each multiplier to degree one using `a13`, then evaluate against the original
unnormalized quadratic equations. The results are exactly `a1^3` and `a9^3`,
with ten and eight physical equation products, respectively. The final
identities contain no factor of `a13`, so the conclusion is global in the
first-pass reduced family, including `a13=0`.

Both polynomial implementations check the 18 products directly and replay
the first-pass dependency. A damaged coefficient is rejected. Thus
`a1=a9=0` throughout family 16 at that stage. Family 16 is still unresolved;
its five charts have not yet been rebuilt after these global zeros. This
does not strengthen the separate family-137 chart result or add a sixth post.

```sh
python -S algebra/check_family16_global_cubes.py
```

## Reproduce

In a recursive checkout:

```sh
python -S algebra/degree7_e1.py --check
python -S algebra/degree7_x0_y0.py --check
python -S algebra/degree7_syzygy_rebuild.py --check
python -S algebra/degree7_syzygy_rebuild.py --check --independent
python -m unittest discover -s tests -v
python experiments/plot_syzygy_rebuild.py
```

Both new replays pass. For family 115 they verify 130 new cancellation
identities with 12,080 physical equation-multiplier terms, three power
identities with 905 terms, and 27 new chart inferences. They also replay the
inherited first-pass and syzygy reductions. The conditional larger-chart
packets add 114 cancellation identities, 16,405 physical products, four cube
identities with forty terms, and four chart inferences. Corrupt maps, corrupt
power identities, and an unjustified chart dependency are rejected.

The independent mode reconstructs the target, derivatives, Koszul fields and
physical coefficients using the second polynomial implementation and opposite
division ordering. It shares the small identity replayer. It is not independent
human review, a separate agent endorsement, or Lean acceptance. No separate
review agent was available in this batch.

Discovery uses optional `python-flint`; replay needs no third-party packages.
The successful search can be regenerated into a fresh path with:

```sh
python -m pip install python-flint
python algebra/discover_syzygy_rebuild.py --family 115 --pivot 10 --power-degree 5 --timeout 600 --output work/rebuilt-115-10.json.gz
```

The generator checkpoints cancellation identities before the slower power
search. Run the corresponding larger-family chart with `--timeout 120` to
reproduce a bounded attempt; timing and the last completed multiplier depend
on hardware. The verifier checks identities, not timing-dependent completeness.

## Braids, Hodge projection, and arithmetic as research tools

The existing [braid toolkit](https://github.com/rbajaj5/ginibre-braid-dynamics-conjectures)
tracks collision-free complex eigenvalue paths, and distinguishes full braid
information from scalar winding. A possible future experiment would continue
the kernel of `R(a)` around loops avoiding its rank-drop locus and test whether
monodromy organizes reusable relations. This needs an actual parameter family,
transport rule, and proof of compatibility; none is constructed here. Sorting
equations or changing a basis is not by itself a braid-group calculation.
The usual Hermitian Gram matrix has real eigenvalues; its spectrum does not
automatically supply the complex eigenvalue braids of the Ginibre experiments.

A more immediate connection is the braid toolkit's
[block elimination and Schur-complement calculation](https://github.com/rbajaj5/ginibre-braid-dynamics-conjectures/blob/main/BLOCK_PAIR_WINDING_THEOREMS.md#5-weak-coupling-and-the-exact-schur-complement).
We could eliminate an invertible block of `R(a)` while retaining its exact
coupling to the remaining block. Because the block determinant may vanish,
the singular locus must be handled separately; generic invertibility would
not exclude the whole denominator family. This is a proposed use of standard
block algebra, not an implemented braid-group action or a new result here.

The Hodge-projection viewpoint remains useful: polynomial left syzygies are
exact annihilators of the shared correction map. The heatmap shows their
support, while an eventual rank-stratification picture could show where the
kernel changes. No rank-stratification experiment is claimed in this batch.

The [supercongruence program](https://github.com/rbajaj5/a183068-supercongruence)
separates arithmetic mechanisms, exact checks, and exceptional cases. A
practical next step here is modular pilot elimination, followed by rational
reconstruction and exact identity replay, to control coefficient growth.
This is a proposed computational transfer, not an application of its
supercongruence theorem. The present proof uses rational arithmetic, not a
finite-prime inference. There is no need to abandon the successful syzygy
approach for a different conjecture.

Credit: the repository authors' certificate and normalization framework;
the bridge attributed there to Benjamin E. Diamond and Griffiths's residue
theory; fqlx's E1/Koszul, symmetry, and pair calculations; and the preceding
Hodge Lab pair/triple reductions. Yang's paper motivated the syzygy direction,
with the limitations explained in the [previous note](polynomial-syzygies.md).
Prepared with OpenAI Codex assistance on behalf of `rbajaj5`.

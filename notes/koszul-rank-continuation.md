# Koszul continuation closes the last two fixed-pair extensions

Families **16 and 137** of our degree-seven triple packet are excluded.
Together with the preceding results, this covers **136/136 third-character
extensions of the fixed pair `{chi_X0, chi_Y0}`** and **136/152** families in
the original combined selection. The other 16 selected triples remain open.
There are 428,536 unordered triples among the 138 characters; this is not an
exclusion of arbitrary three-character or degree-seven denominators.
Holdout remains unsolved, and the unconditional degree bound remains at
least seven. No Lean `HasCertificate` proof or leaderboard point is claimed.

The fixed target and all existing upstream files remain unchanged at
`b8c4edeb80a82395ec07164caf445cfa43bbbd56`. We keep `q=1`,
`A=X0^3 Y0^3`, and the exact eight-term `F` in `instance.rec`.
All calculations use rational identities valid over the complex numbers.

[Visual companion: the actual correction maps, a two-row obstruction,
and the ten-chart dependency diagram](koszul-map-visualizations.md).

## What the Koszul calculation means here

Let `S=Q[X0,X1,X2,Y0,Y1,Y2]` and `Fi=partial_i F`, of degree five.
The relevant degree-13 strand of the gradient Koszul complex is

```text
S_3^15  --d2-->  S_8^6  --d1-->  S_13,
d1(N) = sum_i Ni Fi,
d2(h e_i wedge e_j) = h (Fj e_i - Fi e_j).
```

There are `15*56=840` cubic-coefficient Koszul fields. The preceding E1
checks establish that these span the complete numerator-only kernel in
this degree; we do not assume completeness from the name of the complex.
For a denominator `D=sum ai Di`, choose its checked E1 lift `N0(a)` and
write `N=N0+K(z)`. The second normalized equation is

$$
N(F)=AD,\qquad B_D(N)=D\operatorname{div}N-N(D)\equiv0\pmod F.
$$

Reducing modulo `F` permits an unrestricted quotient. Projecting to the
character required by the denominator's stabilizer is exact: if a solution
exists, its projected numerator remains a solution. For each of these two
families the stabilizer has order six and retains **all 256** allowed Koszul
directions. The physical coefficient equations have the form

$$
E(a,z)=R(a)z+b(a)=0.
$$

A polynomial left syzygy `u(a)^T R(a)=0` gives a necessary equation
`u(a)^T b(a)=sum_j u_j(a)E_j(a,z)=0`. This is a concrete obstruction in the
cokernel of the correction map. It preserves the shared `a_i z_k` products.
We search affine multipliers, then seek explicit powers and unit identities
in the resulting denominator equations. We have not identified this
calculation with geometric `K_{p,q}(X,B;L)` or applied a line-bundle
vanishing theorem. [Literature and hypotheses](syzygy-literature-map.md).

## Two physical rows force a linear vanishing

The family numbers and basis indexing are exactly those in our earlier
[triple packet](three-character-families.md). After its verified first-pass
reductions, the denominator basis indices are:

```text
16:  [42,56,88,102,111,114,115,123,133,168,180,210,229,232,234,271,285,288]
137: [42,56,88,102,111,114,115,133,135,168,234,235,271,272,285,288,289,293]
```

In each line call the coefficients `a0,...,a17`. Define

$$
L_{16}=3a_6-6a_8+a_{14}+a_{16}+a_{17},\qquad
L_{137}=3a_6-6a_7+a_{10}+a_{14}+a_{15}.
$$

Using zero-based physical row indices, let `(j,k)=(1027,1125)` for family
16 and `(j,k)=(1033,1132)` for family 137. In both cases the correction
coordinate is global parameter 167: local `z149`, raw Koszul field 438.
The **unnormalized** rows satisfy

$$
E_j=4Lz,\qquad E_k=\frac23 Lz-\frac1{27}L^2,
\qquad L^2=\frac92E_j-27E_k.
$$

Thus `L=0` over C throughout the reduced family. No chart normalization,
division by a parameter, or family-16 cube identity is used in this step.
It includes exceptional rank cases. The initial discovery found the
augmented two-row determinant `-4 L^3/27`; the displayed two-row identity
is a smaller proof. For `L!=0`, this correction block has rank one and its
augmentation rank two. The remaining branch `L=0` is kept explicitly.
This is a local rank-block argument, not a full determinantal
stratification of `R(a)`.

The previously checked family-16 identities give `a1=a9=0` globally.
For family 137, after substituting `L137=0`, two new identities give
`a1^3=a9^3=0`, with **10 and 8 physical equation-multiplier products**.
They were found by composing chart consequences back to physical rows
and homogenizing their linear multipliers. The final verifier checks them
against the unnormalized equations directly; their validity is not
conditional on the chart used to discover them.

## Complete chart covers

If a third-character coefficient is nonzero, simultaneous scaling of
`D,N` normalizes it to one. Each family has five such charts. No independent
scaling of its character components is assumed.

For family 16, first close `a11=1` after the old cubes and new linear
vanishing. A degree-four unit identity contains 69 multiplier terms.
Consequently `a11=0` holds throughout the family. Rebuild the other four
charts with that new global zero:

| Family | Normalized chart | Final checked obstruction |
|---|---|---|
| 16 | `a11=1` | Degree-four unit identity, 69 terms |
| 16 | `a7=1`, with `a11=0` | Affine/square consequences of necessary syzygies |
| 16 | `a10=1`, with `a11=0` | Degree-three unit identity, 20 terms |
| 16 | `a12=1`, with `a11=0` | Physical affine/square closure |
| 16 | `a13=1`, with `a11=0` | Two cubes, 17 terms in total, then physical closure |
| 137 | `a13=1` | Degree-four unit identity, 65 terms |
| 137 | `a8=1`, with `a13=0` | Physical affine/square closure |
| 137 | `a11=1`, with `a13=0` | Two cubes, 30 terms in total, then physical closure |
| 137 | `a16=1`, with `a13=0` | Degree-three unit identity, 16 terms |
| 137 | `a17=1`, with `a13=0` | Two cubes, 30 terms in total, then physical closure |

The same sequence for family 137 starts with its global cubes and `L137=0`,
closes `a13=1`, and uses the resulting global `a13=0` in the four rebuilds.
Every unit identity is an explicit `sum Cr Pr=1`; every power identity is
an explicit polynomial combination, followed by the valid implication
`a_i^m=0 => a_i=0` over C. No real positivity is assumed.

All third-character coordinates therefore vanish: `{7,10,11,12,13}` in
family 16 and `{8,11,13,16,17}` in family 137. The remainder is supported on
the anchor pair `{(0,0,1),(1,2,3)}`, excluded by the separately established
[complete X0/Y0 theorem](x0-y0-exclusion.md). The checker verifies the full
chart cover and this character identification. Its refinement routines
reject using the pivotal-chart zero before that chart is proved closed.

## What failed, and what changed

The first rank pass completed all ten bounded local searches without
closing a chart. Each found the linear relation above but no next usable
factorable local minor. The bounds were 120 soft seconds, 30 nodes, branch
depth two, factor degree five, 300 terms, and 10,000 two-column row triples;
each supervisor had a 180-second hard limit. These archived rank packets
still correctly say **unresolved at that checkpoint**.

The next four full syzygy searches had 120-second hard limits. Family 16,
chart 11 completed; family 16, chart 13 and family 137, charts 8 and 11
timed out. Completed checkpoints were retained. Degree-three reanalysis
of the latter family supplied the small global cubes. After these zeros,
family 137, chart 13 completed within its 150-second limit, whereas its
unrefined chart 8 again timed out. All eight subsequent chart rebuilds
completed within their limits (120 seconds for family 16; 150 for 137).

The successful change was to **rebuild after proved vanishings**, preserving
every correction direction until an exact substitution eliminated it.
Timeouts and the absence of another small minor were not used as proof.
An exploratory nonzero-pivot pilot introduced parameter guards and did not
cover their exceptional loci; it was not used in any exclusion. A slower
full-matrix rank replay was replaced by replaying precisely the pivot rows
and claimed minor rows, retaining all columns in those rows. That is an
implementation optimization, not a new mathematical hypothesis.

[Search logs and proof packets](../results/degree7-rank-strata/) retain
the bounded failures. `exploratory-inputs.zip` contains the raw timeout
checkpoints and discovery pilots; those are not asserted to be proofs.
The published proof packets retain only the relations used in their
checked continuation, with original selection indices recorded.

## Reproduce and inspect

In a recursive checkout with Python 3.11, replay the key dependencies and
new packet using the standard library only:

```sh
python -S algebra/degree7_e1.py --check
python -S algebra/degree7_x0_y0.py --check
python -S algebra/degree7_triples.py --check
python -S algebra/degree7_triple_shared.py --check
python -S algebra/degree7_syzygies.py --check
python -S algebra/degree7_syzygy_rebuild.py --check
python -S algebra/check_family16_global_cubes.py
python -S algebra/degree7_rank_strata.py --check-all
python -S algebra/degree7_rank_strata.py --check-all --independent
python -S algebra/degree7_koszul_continuation.py
python -S algebra/degree7_koszul_continuation.py --independent
```

The two polynomial constructors rebuild the fixed-target equations with
different monic-division orderings. They share the small identity replayer;
this is not independent human review or Lean verification. The tests
reject damaged identities, unproved chart dependencies, nonconstant
pivots treated as units, and omitted factor branches. Do not use `-O`.

Both new full replays passed. Across the ten charts they check **685
syzygy identities**, **122,964 physical equation-multiplier products**, and
**ten power/unit identities containing 247 products**, as well as 197
affine/square chart inferences. The earlier first-pass reductions, global
linear identities, and global cubes are additional dependencies. All **34
unit tests** passed. [Standard replay](../results/degree7-rank-strata/koszul-validation.json)
and [second construction](../results/degree7-rank-strata/koszul-independent-validation.json)
give the per-chart counts.

Discovery uses optional `python-flint`, not required for replay. A portable
bounded runner refuses existing output paths and preserves checkpoints:

```sh
python -m pip install python-flint
python algebra/discover_koszul_continuation.py --family 16 --pivot 11 --stage rank-leaf --output work/16-11.json.gz --timeout 120
python algebra/discover_koszul_continuation.py --family 16 --pivot 12 --stage refined --output work/16-12.json.gz --timeout 120
python algebra/discover_koszul_continuation.py --family 137 --pivot 13 --stage reduced --output work/137-13.json.gz --timeout 150
python algebra/discover_koszul_continuation.py --family 137 --pivot 17 --stage refined --output work/137-17.json.gz --timeout 150
```

Timing and discovery success within a wall-clock limit depend on hardware.
Saved verification reports record what actually ran. These computations
use CPU exact arithmetic; no GPU or geometric simulation is credited with
the exclusions.

Credit: the repository authors' normalization and certificate framework;
the bridge attributed there to Benjamin E. Diamond and Griffiths's residue
theory; fqlx's E1/Koszul, symmetry, and pair calculations; and the preceding
Hodge Lab reductions. Yang's paper and Eisenbud's syzygy viewpoint motivated
the search. The newer fqlx support/elliptic-pencil work in the discussion
is complementary and is not a dependency of this packet. This work was
developed with OpenAI Codex assistance. No new independent-agent review is
claimed; the checks above specify the actual verification performed.

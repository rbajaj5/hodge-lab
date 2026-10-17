# 132 further triple exclusions around Y0/X1

**All 132 new degree-seven three-character families in this batch are
excluded.** Together with the preceding 284, this gives **416 selected
triple exclusions**. The batch completes the 136 third-character extensions
of Y0/X1, four of which were already covered. This remains a small specified
subset of the 428,536 unordered triples among the 138 retained characters.
Holdout is unsolved: no Lean `HasCertificate` proof, solve PR, leaderboard
point, or improvement to the unconditional degree bound is claimed.

The exact target is unchanged: `q=1`, `A=X0^3 Y0^3`, and `F` from
`sources/sextics/data/holdout/instance.rec` at
`b8c4edeb80a82395ec07164caf445cfa43bbbd56`. All existing upstream files
remain unchanged. A nonzero quotient modulo `F` is permitted throughout.

## Selection and method

The [manifest](../results/y0x1-extensions/blocks-plan.json) selects every
new triple containing `(0,1,0)=chi_X1` and `(1,2,3)=chi_Y0`, excluding the
284 triples already proved. It records the full raw basis support and a
global lexicographic triple index. We use the complete retained E1 character
eigenspaces after the previously verified character-preserving six-direction
`F*S1` gauge reduction, not an arbitrary truncation of each eigenspace.

**Y19, Y49, Y100 below belong to this new batch.** They are different from
the old X1/Y1 B19, B49, B100 in the [pattern comparison](graded-map-patterns.md).
Constraints proved in one family are not transferred to another.

Following the preceding Eisenbud-inspired computation, we construct exact
physical left annihilators of an enlarged correction-column space. The
resulting homogeneous quadratics are necessities for the full certificate
equations. Pure-character blocks are selected from those consequences;
other character coefficients are not silently set to zero. Explicit square
or higher-power identities force coordinates to vanish over C. We then
reconstruct the equations with those coordinates removed.

The first pass uses powers through degree four and reduces **123** new
families to the previously proved Y0/X1 pair. Nine survive. Full
shared-numerator systems retain the complete allowed Koszul correction
coset. Their normalized charts force further coordinate zeros; the
homogeneity of the original equations justifies those global conclusions.
No generic-rank division or invertible-minor assumption is used.

| New batch | Added character | Initial | After first pass | Final pair-subspace size | Route after first pass |
| --- | --- | ---: | ---: | ---: | --- |
| Y19 | (0,4,3) | 19 | 17 | 12 | Two chart zeros, then three rebuilt zeros |
| Y33 | (1,2,0) | 16 | 12 | 11 | One chart zero |
| Y46 | (1,5,0) | 20 | 15 | 12 | Two chart zeros; rebuild; one further chart zero |
| Y84 | (3,4,3) | 18 | 14 | 11 | Three chart zeros |
| Y96 | (4,1,4) | 16 | 14 | 12 | Two chart zeros |
| Y97 | (4,2,0) | 16 | 12 | 11 | One chart zero |
| Y100 | (4,2,3) | 17 | 13 | 6 | New cubic consequences, quartic powers, rebuild, two chart zeros |
| Y108 | (4,5,0) | 19 | 13 | 12 | One chart zero |
| Y132 | (5,5,4) | 16 | 14 | 12 | Two chart zeros |

For Y19 the first shared pass excludes `a159=1` and `a216=1`, while
`a7=1` and `a119=1` remain unresolved. Rebuilding after the two proved
zeros forces raw coordinates 7, 119, and 139 to vanish. In Y46 the
first charts force 117 and 177 to vanish but do not settle 125; after
rebuilding, the `a125=1` chart contradicts. These are examples where an
unsuccessful chart is still useful when other charts change the next system.

That continuation reaches **131/132**, with Y100 unresolved. Both its
failed third-coordinate charts and the
[131-family checkpoint image](../results/y0x1-extensions/checkpoint-131.png)
remain in the packet. The main `validation.json` intentionally records
this checkpoint; the additional Y100 closure is checked separately.

## Y100: polynomial multipliers supply the missing constraints

At the checkpoint Y100 has 13 denominator coordinates, 125 allowed
Koszul correction coordinates, and 652 physical equations
`E(a,z)=b(a)+M(a)z=0`. Multiply every equation by 1 and each of the thirteen
denominator coordinates, then eliminate all monomials involving `z`.
The exact calculation completes all fourteen multiplier blocks in 167.14
seconds under a declared 180-second limit.

It produces 13 quadratic and 198 cubic independent denominator relations.
The old quadratics and their linear multiples span dimension 172 within
this degree-two/three space; the combined span has dimension 211, adding
**39 cubic relations**. Every retained relation includes its explicit
polynomial multipliers against the physical equations. The checker expands
29,910 coefficient products, reconstructs the baseline, checks independence,
and rejects a deliberately altered multiplier.

The pure-X1 block has five variables and nine selected generators: two
quadratics and seven cubics. Use the correctly graded map

\[
\bigoplus_j S_{d-\deg P_j}\longrightarrow S_d,
\qquad (u_j)\longmapsto\sum_j u_jP_j.
\]

At degree three its rank is 17 out of 35 and it gives no coordinate zero.
At degree four its rank is 61 out of 70. Three explicit fourth-power
identities force **raw 123, 210, 229** to vanish. The Y0 and third-character
blocks still give no coordinate-power obstruction through degree four.

Reconstructing the physical equations with those three zeros supplies
third-power identities forcing **180 and 232** to vanish. The remaining
eight-coordinate system has two characters. Of its eight normalized
charts, those at **6 and 211** contradict. The other six are retained as
unsuccessful searches; they need not contradict under this inference method.
Removing 6 and 211 leaves the pure-Y0 directions

```
115, 133, 234, 271, 285, 288.
```

This support is a subspace of the already excluded Y0/X1 pair. The checker
replays that full pair proof and its single-X1 dependency. Thus Y100 is
excluded, completing the batch. The intermediate coordinate counts are
**13 -> 10 -> 8 -> 6 -> prior exclusion**. These counts are not dimensions
of a solution variety. Full rank of a whole graded strand is unnecessary:
membership of the needed individual powers suffices.

## Verification, unsuccessful searches, and bounds

The primary and second physical polynomial implementations both pass the
complete chain. They reconstruct the fixed-target equations separately but
share rational arithmetic and certificate-checking utilities; this is not
a claim of separate human review or two wholly unrelated proof systems.
No fresh independent-review agent was used for this batch.

The main checkpoint replay checks 6,142 physical duals, 665,146 correction
pairings, 169,375 quadratic pairings, 484 square identities, 80 graded maps,
and 20 charts with 799 inferences. Fifteen charts contradict; five remain
unresolved at their original stage. It rejects 133 altered power witnesses
and ten altered chart witnesses. Counts include inherited and rebuilt work,
not distinct discoveries. Y100 closure adds the mixed-degree power checks,
two rebuilt cubic-power identities, and eight charts with 21 inferences.

The block pass used two workers and a 300-second limit per chunk; the first
shared continuation used two workers and 120 seconds per family. All those
jobs completed. The multiplier job used one worker with 180 seconds.
Later Y100 closure was a finite exact replay/rebuild run without a separate
wall-clock cutoff. Bounds, logs, every unsuccessful strand and chart,
and all discovery checkpoints are retained. No timeout or failed bounded
search is treated as an impossibility proof.

From a recursive checkout, using Python 3.11 and its standard library:

```sh
python -S experiments/check_y0x1_extensions.py
python -S experiments/check_y0x1_extensions.py --independent
python -S experiments/y100_multipliers.py --check
python -S experiments/y100_multipliers.py --check --independent
python -S experiments/y100_multipliers.py --blocks --check
python -S experiments/y100_after_powers.py --check
python -S experiments/y100_after_powers.py --check --independent
python -S experiments/plot_y0x1_extensions.py --check
python -S experiments/graded_map_patterns.py --check
```

All pass locally with assertions enabled. The source-only checks require no
Singular, SymPy, numerical tolerance, or GPU. Discovery was also rational
linear algebra. Local success is not a Lean or upstream acceptance receipt.
The dedicated Linux job runs these same checks; remote status is recorded
separately after publication.

**Later CI receipt:** the [dedicated Linux job](https://github.com/rbajaj5/hodge-lab/actions/runs/39036721511/job/117407967073)
passed every listed check at proof commit
`840b88c22386687c745cf944c5c2a41c6b854d39`. Other workflow jobs were still
running when the [receipt](../results/y0x1-extensions/ci-y0x1.json) was saved.

![Complete batch and nine continuation paths](../results/y0x1-extensions/y0x1-extensions.png)

The image links every batch ID to its proof route and shows the successive
retained-coordinate counts. Its [data](../results/y0x1-extensions/visual-data.json)
are checked against the proof receipts and hashes of every compressed packet.
Rebuild it with `python experiments/plot_y0x1_extensions.py` (Matplotlib).
The separate [basis comparison](graded-map-patterns.md) preserves the user's
visual motivation and a rejected factorization; it adds no exclusion.

## Credit

Prepared with OpenAI Codex assistance on behalf of rbajaj5. This builds on
the repository authors' certificate/geometric-support framework, the bridge
attributed there to Benjamin E. Diamond, Griffiths's residue theory, and
fqlx's earlier exact E1/Koszul, symmetry, and one-/two-character calculations.
The terminating Y0/X1 proof is our
[previous pair-22 result](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18983276),
not a new result in this batch. The selection also builds on our preceding
X0/Y0 and X1/Y1 extension results, with fqlx's pair-30 result credited there.
Eisenbud's *The Geometry of Syzygies* supplies the graded-module viewpoint;
the particular finite computations and witnesses here are ours. We have not
derived a new theorem from the separate Dubedat/imaginary-geometry analogy.

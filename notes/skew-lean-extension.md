# One-reflection-skew: complete bounded Lean inputs and the mixed-polar comparison

21 October 2026 (EDT). **Lean now proves the existing degree-four exclusion for
arbitrary numerator polynomials satisfying the degree and variable hypotheses.**
The accepted mixed-polar proof provides a useful construction pattern, but its
specific ratio/square coordinates do not express the skew equation in the same
way. A separate source-bound Lean calculation verifies the obstruction to that
direct coordinate formula. No target primitive or new exclusion family is found.

[![Target symmetry comparison and the completed degree-four proof bridge](../visualizations/skew-extension.png)](../visualizations/skew-extension.svg)

The left panel reconstructs paired-sign defects from the protected polynomial
terms. The right panel shows the new formal completeness step feeding the
already checked obstruction. It is not a phase diagram or a proof that other
constructions cannot work. [Reproducible generator](../scripts/visualize_skew_extension.py).

## Pinned inputs and reused results

Notebook parent: [`c5862c4`](https://github.com/rbajaj5/hodge-lab/commit/c5862c4a2881cac1705f7937cd599bdcff6a8170).
Upstream: [`84f106e`](https://github.com/hodge-computer/sextics/commit/84f106ebf0731cbee1926833236361cddac0fc3f).
The upstream head remains unchanged since checkpoint 121. Six files were read
at that pin, with 45-second request bounds: both targets' protected REC and JSON
records, and mixed-polar's coordinate and clearing modules.
[Input paths, Git blobs and SHA256 hashes](../formal/results/skew-extension/inputs.json).

The variable order is `(X0,X1,X2,Y0,Y1,Y2)`, both targets have `q=1`, and the
coefficient field of the records is rational. The skew source is `X0^3 Y0^3`;
mixed-polar's source is `X0 X1 X2 Y0 Y1 Y2`. Skew's protected bytes are unchanged.
The verifier independently parses the REC expressions, compares their rational
coefficient dictionaries with the JSON terms, and checks the exact generated
Lean definitions of both F and A. [Source-binding receipt](../formal/results/skew-extension/source-binding.json).
This binding uses an external exact parser; it is not a Lean proof of GitHub
input parsing. Hash checks of upstream Lean files do not replay their proofs.

The checkpoint-120 coefficient proof, its selected rows and receipt are reused
unchanged. Its source hashes are checked by the new runner. The earlier source
transport and denominator derivation remain the checkpoint-117/118 calculations,
with fqlx's quotient/residue formulation and the checkpoint-119 independent
ChatGPT review attributed as before. No prior search or completed audit was rerun.

## What the accepted proof supplies, and what does not transfer

The accepted mixed-polar [coordinate module](https://github.com/hodge-computer/sextics/blob/84f106ebf0731cbee1926833236361cddac0fc3f/data/mixed-polar/PhysicalCoordinates.lean)
works with

$$
v=Y_0/X_0,\quad u=(Y_1/X_1)/v,\quad w=(Y_2/X_2)/v,
\quad x=X_0^2/X_2^2,\quad y=X_1^2/X_2^2,\quad R=X_2^2.
$$

Its [clearing theorem](https://github.com/hodge-computer/sextics/blob/84f106ebf0731cbee1926833236361cddac0fc3f/data/mixed-polar/PhysicalClearing.lean)
shows the useful architecture: an exact residue-divergence primitive on the
specified physical field feeds legal denominator clearing and homogenization.
The primitive, target field, nonzero normal, compatible derivations and common
representatives are substantive inputs. Reading that theorem does not supply
those inputs for skew, and this batch does not port it or replay PR #182.

Let `sigma_i` negate `(Xi,Yi)`. The new
[CoordinateComparison module](../formal/HodgeLab/OneReflectionSkew/CoordinateComparison.lean)
proves all three paired flips preserve mixed-polar's F. For skew it proves

$$
F\circ\sigma_0-F=F\circ\sigma_2-F=-2X_1^3X_2Y_0Y_1,
\qquad F\circ\sigma_1=F.
$$

Both sources A are invariant under all three paired flips. The obstacle here is
the sextic, not the scalar source's paired-sign character. These are scalar
polynomial statements; no differential-form transformation is inferred from
source invariance alone.

The same Lean module proves the six displayed coordinates are fixed by
`sigma_0`. At `p=(1,1,1,1,1,1)` and its flipped point, all displayed denominators
are nonzero and those coordinates agree, while skew F has values **8 and 6**.
Thus no single function of those coordinates represents F on the entire
displayed chart. This is a useful obstruction to the unchanged mixed-polar
coordinate formula. **The witness points are off F=0.** It proves neither
nonexistence of hypersurface correspondences nor a theorem about every rational
function with additional poles at the common coordinate image. Other covers,
additional coordinates and target-specific cubic constructions remain possible.

## The new degree-bound theorem

For `D=a=1+r^6+w^6`, reuse the scaled polynomial `P7=7P` from
[the base-derivative calculation](skew-base-derivatives.md). The full operator is

$$
\mathcal M(N)=\sum_{i\in\{U,r,w,t\}}
\left(60a\,\partial_iP7\,N_i-72P7a\,\partial_iN_i
+72P7N_i\,\partial_i a\right),\qquad s=35U^2a^2.
$$

All three terms remain present, including differentiation of the denominator.
[DegreeFour.lean](../formal/HodgeLab/OneReflectionSkew/DegreeFour.lean) proves:

1. The 70 listed monomials are distinct and cover the support of every polynomial
   of total degree at most four in `(U,r,w,t)`.
2. Every such polynomial equals the sum of those monomials with its own
   coefficients. This expansion theorem works over an arbitrary commutative
   semiring; the operator theorem uses a characteristic-zero field.
3. The full differential operator on four arbitrary such inputs equals the
   corresponding combination of the 280 already checked columns.
4. `no_degree_four_solution` excludes `M(N)=s` for all those inputs over every
   characteristic-zero field, using the existing integer dual `(21,1,-1)` and
   its nonzero source pairing 35.

The implementation uses `MvPolynomial (Fin 5) K` to reuse the existing library.
Its fifth coordinate must be absent from every supported monomial; this is an
explicit hypothesis, not an implicit gauge reduction. There is no assumption
that an arbitrary input is already supplied as a list of 280 scalar coefficients.
This closes the expansion gap recorded in checkpoint 120. It strengthens formal
verification of the same bounded space; it does not enlarge the searched family.

## Executed checks and reproduction

With the pinned dependencies installed, from `formal`:

```sh
python3 -O check_skew_extension.py
```

Then from the repository root:

```sh
python3 scripts/visualize_skew_extension.py
```

The [final receipt](../formal/results/skew-extension/validation.json) records
successful compilation on Lean 4.31.0 / mathlib
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`, **23 named theorem audits**, and default
kernel replay of the **two new modules**. Dependencies use only `propext`,
`Classical.choice` and `Quot.sound`. Imported mathlib and the reused coefficient
modules were not freshly replayed. The actual command logs, source hashes and
compiled artifact hashes are saved separately from the earlier receipt.

Three deliberate false claims were rejected with explicit false-proposition
diagnostics: skew paired-sign invariance at the witness, inclusion of `U^5` in
the degree-four list, and inclusion of the absent fifth variable. These controls
test the claimed restrictions; they do not test completeness of a rational
primitive search. The runner uses explicit failures even under Python `-O`,
starts with an `IN_PROGRESS` receipt and saves `FAIL` on an unsuccessful run.
The final run completed in **46.171 seconds**. Each command is capped at 120
seconds and the whole run at 600 seconds.

Development was bounded to 15 minutes for the expansion module, with 90-second
compile limits. A missing cached Omega import and two coordinate-elaboration
issues were fixed; no timeout occurred. [Preserved attempts](../formal/results/skew-extension/development).
A separate read-only review checked theorem scope and the verifier. The PNG
was rendered and visually inspected; its values are reconstructed from the
pinned polynomial data and checked against the current Lean receipt.

## Remaining limits and publication

The highest-priority remaining formal dependency is **protected source to chart
transport**. The new bindings of F/A and the old chart operator have not been
joined by a Lean theorem transporting the differential and its Jacobian factor.
The smallest next unit is the exact polynomial substitution identifying the
protected sextic with the displayed chart polynomial, followed by the differential
normalization as a separate step. Neither is prerequisite to the bounded
polynomial statement proved here.

There is no target primitive, `HasCertificate`, new accepted solve, comparison
of the 45 higher-U images with fqlx's 504-column space, or new denominator search.
The accepted mixed-polar proof remains credited to benediamond and its stated
contributors; this comparison does not transfer that solve credit.

This batch is published in Hodge Lab with checkpoint 122. No upstream post or
edit is part of this batch; related findings are retained for a substantial
future update. The contribution tally remains **29 discussion contributions,
one closed maintenance PR, zero accepted authored solves**.

## Follow-up — 21 October 2026, checkpoint 124

The [protected polynomial substitution](skew-chart-lean.md) is now proved in
Lean and bound to the actual existing `p7` and `a` definitions. The scalar
source restricts to x³. This closes the first small unit proposed above;
the differential/Jacobian/residue normalization remains a separate formal
dependency. The earlier statements, receipt and bounded exclusion are unchanged.

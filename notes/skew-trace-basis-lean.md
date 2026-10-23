# Trace-free basis with the leading coefficient retained

22 October 2026. Notebook parent fd33336945c499099cda55c740c9e9375073bdb5;
upstream snapshot 21fccb6b4f1d4070ddaa30195a78f268247569e6.

**Checked in Lean: the full split degree-18 quotient has a derivative-weighted
18-element basis, whose first 17 vectors form the kernel of its actual algebra
trace. The last vector has trace 1/a₁₈, not automatically 1.**
This completes the split-algebra unit. Descent to the original unsplit physical
coefficient field and binding a literal target source are not completed here.

![Full quotient and trace kernel](../visualizations/skew-trace-basis.png)

## Statement and assumptions

Let K be a field, a₁₈ ≠ 0, and let eighteen roots ρⱼ in K be pairwise distinct.
Put

\[
P(Z)=a_{18}\prod_{j=0}^{17}(Z-\rho_j),\qquad
B=K[Z]/(P),\qquad \delta=[Z].
\]

The algebra B need not be a field. Evaluation identifies the **entire**
quotient with K¹⁸; no factor or sheet is discarded. Lean proves that P′(δ)
is a unit and that the vectors bᵢ satisfy P′(δ)bᵢ = δⁱ for 0 ≤ i ≤ 17.
Thus division in bᵢ = δⁱ/P′(δ) is justified by a unit, not a field structure
imposed on a possibly reducible quotient. These vectors form a basis, and

\[
\operatorname{Tr}_{B/K}(b_i)=
\begin{cases}0&0\le i\le16,\\1/a_{18}&i=17.\end{cases}
\]

Consequently b₀,…,b₁₆ form an actual basis of the trace kernel, which has
dimension 17. A vector with basis coordinates cᵢ has trace c₁₇/a₁₈. In
particular b₁₁ has zero trace and is nonzero. Zero trace is not zero source
and does not establish exactness of a form.

The basis theorem works in any characteristic admitting the stated distinct
roots. Only the separate projection x ↦ x − Tr(x)1/18 uses characteristic
zero. The identity Tr(1)=18 need not be nonzero in other characteristics.
Lean's total division also lets the isolated trace formula hold at a₁₈=0,
when its displayed vectors vanish; **none of the basis, invertibility or
degree-18 claims permits that case**.

## Proof construction

- [TraceKernel.lean](../formal/HodgeLab/OneReflectionSkew/TraceKernel.lean)
  constructs the kernel basis for a functional supported on the last vector
  of an existing basis. Subsequent modules prove its hypotheses.
- [TraceFreeBasis.lean](../formal/HodgeLab/OneReflectionSkew/TraceFreeBasis.lean)
  uses Lagrange interpolation for the reciprocal-derivative trace identities,
  and a diagonal matrix times a Vandermonde matrix for the full basis.
  It proves that actual multiplication trace on K¹⁸ is the coordinate sum.
- [SplitTraceQuotient.lean](../formal/HodgeLab/OneReflectionSkew/SplitTraceQuotient.lean)
  constructs the evaluation equivalence from the actual polynomial quotient,
  proves trace invariance by conjugating multiplication maps, and transfers
  both bases. Its derivative identity and unit theorem bind the transferred
  vectors to the original polynomial derivative.

No monic normalization is hidden here. Replacing P by P/a₁₈ leaves the
ideal unchanged but multiplies these basis vectors by a₁₈. The control a₁₈=2
detects that distinction: the last trace is 1/2. No novel mathematical theorem
is claimed; this formalizes the standard interpolation/codifferent mechanism
motivated by the compact-source architecture.

## Executed verification and bounds

From formal/, run:

    python3 -O check_skew_trace_basis.py

The [source-bound receipt](../formal/results/skew-trace-basis/validation.json)
records Lean 4.31.0 and Mathlib fabf563a7c95a166b8d7b6efca11c8b4dc9d911f:

- **56 declaration audits**, including definitions and theorems, with only
  propext, Classical.choice and Quot.sound in their axiom dependencies.
- **Three new-module kernel replays**, plus successful compilation.
- **Seven positive controls** and **three rejected false claims**: omitting
  the leading coefficient, changing kernel dimension to 18, and identifying
  the trace-zero eleventh vector with zero. Each rejection reaches False,
  rather than failing on an import or unrelated elaboration error.
- The complete driver finished in **57.953 seconds**, within 120 seconds per
  process and 600 seconds total. Required failures raise under Python -O.
  No cache fetch or dependency upgrade was needed.

Only these three new modules were kernel-replayed. Mathlib remains imported;
the earlier chart, volume, residue, ambient-derivation and differential-form
proofs were not rerun. Selected context receipt hashes are recorded in
[inputs.json](../formal/results/skew-trace-basis/inputs.json). Hash agreement
is provenance, not a new mathematical replay.

[Development logs and snapshots](../formal/results/skew-trace-basis/development/README.md)
retain import/API/elaboration failures. An initial sandboxed WSL invocation
was denied; the permitted WSL route worked. These failures are not mathematical
counterexamples. An optional uncached Mathlib import was avoided by using the
elementary trace-conjugation proof from available imports, with attribution.
The final build has one nonsemantic simp/simpa style warning.

The [figure generator](../scripts/visualize_skew_trace_basis.py) reads the new
declarations and displays their statements and rational normalizations:

    python -B scripts/visualize_skew_trace_basis.py

The PNG and SVG were visually inspected. The figure does not sample physical
roots or provide independent proof evidence. CI is configured to run the
new checker; no remote CI outcome is claimed by the local receipt.

## New physical cover: separate instantiation

During this pass, [benediamond's comment 19129985](https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19129985)
introduced the monic equation

\[
f(r)=r^{18}+r^{12}+(vr-1)^6-ar^{15}.
\]

Here a is a base parameter, **not** our leading coefficient a₁₈. The
displayed f has a₁₈=1. Its scalar r¹¹/fᵣ matches the formal basis pattern
only after its own source and field/separability binding. Eighteen sheets
and a seventeen-dimensional trace kernel are compatible.

A separate Codex reviewer fetched the complete live Discussion 127 context
and executed **nine exact rational identities in 22.328 seconds**, under a
30-second timeout, with two nonzero mutation controls. They check the
transformed cubic coefficients, f=r¹⁵(A−a), the covering derivatives and
Hᵣ=Aᵣψᵥᵥ, with v differentiation at fixed a. Counts are separate from the
56 Lean audits. See the [checker](../results/skew-cover-followup-19129985/check_small_identities.py),
[receipt](../results/skew-cover-followup-19129985/small-identities.json) and
[scope review](../results/skew-cover-followup-19129985/review-scope.json).
The reply was created/updated at 18:15:28 UTC; its body SHA256 is
bbebae10b90520c5c3d4c6bd0a4f090c26a13bb5ae2feab45562a6589997b521.

We did **not** replay its ZIP, physical normalization/sign, full
connection/current, pole bounds, ranks 26/27 and 38/39, or generic
specialization argument. These remain author-reported here. The comment
explicitly claims no solve or Lean certificate; the multidirectional
primitive is still missing.

## Attribution, publication and next obligation

Credit fqlx/Ben Burns for the compact architecture and benediamond/Benjamin
Diamond for the newer cover/current, with their declared ChatGPT/agent
assistance; Mathlib contributors supply the interpolation, quotient, matrix,
trace and basis APIs. Codex and parallel agents constructed and checked
these modules. A separate agent reviewed the main trace and kernel modules;
the quotient author's review of that module is self-review.

The historical chain remains explicit: [rbajaj5's degree-seven contribution](https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19052407)
is linked and specifically credited in [fqlx's replay addendum](https://github.com/hodge-computer/sextics/discussions/127#discussioncomment-19080252).
That addendum labels itself separate from the twisted-companion construction.
The new reply credits fqlx's later connection/source. The thread establishes
reuse of rbajaj5's degree-seven calculation; it does not by itself establish
that the new cover/current directly depends on that separate bounded-degree
calculation. Previously recorded credit is not counted again.

The next smallest formal unit is a trace-compatible base-change/descent lemma
for a specified separable degree-18 polynomial over its original coefficient
field. Instantiation also requires the literal polynomial, nonzero leading
coefficient and separability proof. Connecting the eleventh basis vector to
the physical differential source remains separate. No primitive, connection
solution, homogeneous certificate, trace/clearing replay or HasCertificate
is claimed by this pass.

Hodge Lab publication only. No upstream post, reply, edit or PR. Posts remain
entries 1–29. Tally unchanged: **29 discussion contributions, one closed
maintenance PR, zero accepted authored solves**.

## CI follow-up — 23 October 2026

The saved local results above remain the checkpoint-132 evidence. The
[subsequent CI run](https://github.com/rbajaj5/hodge-lab/actions/runs/39832127430)
stopped before the trace-basis Lean commands: an earlier step regenerated
`formal/results/skew-forms/validation.json`, conflicting with this checker's
historical hash pin. This is an unresolved receipt-lifecycle issue, not a
failed mathematical goal or a successful CI replay. See the
[verified log, source diagnosis and next bounded check](upstream-status-20261023.md#a-verified-notebook-ci-failure-separate-from-the-upstream-cleanup).
No proof or historical receipt was changed during that review.

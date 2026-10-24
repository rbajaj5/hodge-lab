

### Checkpoint 142 — physical curve realization and compatible Kähler pullback, 24 October 2026 EDT

This bounded Pro unit starts from exact notebook parent
`e2182223a0395cfb758a2ee09e304eb940b7a67a`, with upstream
`e96be434bd55d6013d7a5854732cb317ca0e43e7`. The protected instance
SHA256 is `c6621c8845addf857ed30726f86449d5ea3310c7609641db9e326f9b85f10fbd`;
q=1 and A=X0^3 Y0^3. The source manifest pins the literal F and chart
polynomial through unchanged imported proofs and the protected record.

**Proved.** The new [PhysicalCurveRealization module](formal/HodgeLab/OneReflectionSkew/PhysicalCurveRealization.lean)
constructs B=Frac(Q[U,r,w,t]) and L=AlgebraicClosure B, preserving the
injective base map and algebraic independence of all four parameters.
It constructs z^6=-cubic(U,r,w,t), x^2=U and proves the original protected
point (x,rx,wx,1,t,z) satisfies F=0 and A=x^3. Thus the original square
cover is recovered, beyond the reflection-quotient U-chart.

The allowed common domain is S=Q[U,r,w,t,z][z^-1]. Actual Q-algebra maps
from S to both the old ambient field and L induce universal Kähler and
exterior maps. All five coordinate differential images are proved. The
same regular four-form maps to the old residueScalar • alpha and to the
normalized curve representative. The curve and square differential
relations are derived. This is not a map from the whole ambient field;
no_ambient_field_specialization proves the obstruction to killing its
nonzero G. G is not a unit in S, and the old normal derivation cannot
descend unchanged. G^-1 is never evaluated on the curve.

The generic realization has proved r,z,f_r,Delta nonzero. Exact cleared
polynomial identities establish the latter two: f_r has value -3 at the
all-one polynomial evaluation, and cleared Delta has value 9261 at zero.
These are polynomial nonvanishing certificates transferred through an
injective generic embedding, not claims about every specialization or
a physical chart at r=0. `realized_source_reduction` instantiates the
prior actual four-form theorem with no residual curve/chart hypotheses.
Both compact rows and the existing fibre-first orientation are retained.

**Executed checks.** The sole Pro Lean writer's final
[checker-02 receipt](results/skew-physical-curve-20261024/lean-development/checker-02/validation.json)
passes 81 declaration/axiom audits, one new-module kernel replay,
25 positive controls and eight intended False-goal controls in 31.691s.
Receipt SHA256: `6c719e214997ec6ca1293d3a613698564e2bacc26cd4bc27bb41f8b811a95bea`.
Module SHA256: `a74e478115cdf3808c365861c1313ee98698d1d3ed9aa8e8031355d4e69f5438`.
The checker runs under Python -O, rejects violated pins and invalid
requirements, and uses fresh output directories. Controls exercise the
concrete field/maps, the prior source reduction, parameter collapse,
zero z, the curve relation, illegal ambient-field specialization,
inverting G, coefficient sign, f_r sign and Delta clearing. All negative
controls fail with the intended mathematical False goal, not API errors.
Allowed axioms are only propext, Classical.choice and Quot.sound.

Five development attempts are saved with source snapshots and complete
stdout/stderr/exit/timing records. Attempts 1–4 failed on numeral mapping,
universal-map computation, ambient Q-algebra instance compatibility and
denominator normalization; attempt 5 passed. Checker-01 passed and is
preserved; checker-02 rechecked the final explicit UTF-8 decoding fix.
The expired toolchain/cache required restoration of imported artifacts,
not rerunning their old focused checkers. The initial sandbox network
failure and tar ownership warnings/nonzero extraction exit are preserved;
the restored pinned toolchain was verified before use. Lean 4.31.0,
Mathlib fabf563a7c95a166b8d7b6efca11c8b4dc9d911f, Python 3.12.14.

Separate AI math/API and adversarial evidence reviewers were read-only;
neither executed Lean or symbolic mathematics. The final evidence audit
ran under -O in 0.05445s and verified 37 source/context hashes, 42 command
streams, all declaration/control/replay receipts and the exact parent
ledger prefix. These are AI reviews, not independent human review.
The earlier successful CI40051515847 is reused historical evidence; no
new remote CI has run here. The focused CI step is added for coordinator
integration. Prior mathematical batches and receipts are not rewritten.

**Visualization and reproduction.** The [scoped note](notes/skew-physical-curve-realization.md)
records the exact maps, field choices and limits. The
[PNG/SVG figure](results/skew-physical-curve-20261024/visualization-02/physical-curve-pullback.png)
and generator bind the final receipt, source and output hashes. The first
render is retained; the second corrects label placement and explicitly
labels the image of the regular source. The final PNG was visually inspected.
Run from formal: `timeout 600 python3 -O check_skew_physical_curve.py
--output-dir results/runs/physical-curve-reproduction` using a fresh path.
Run the visualization generator with the saved checker-02 receipt and
a fresh --output-dir; full commands are in the note and handoff.

**Bounds and limits.** One implementation approach; mathematical work
started 09:39:45 UTC and stopped at the final receipt 09:58:13 UTC, within
the 45-minute limit. Each Lean command was bounded by 120s, each checker
by 600s, each network operation by 45s. No interrupted calculation is
counted as a result. Packaging has a separate five-minute limit.
L is a concrete algebraic-closure realization, not an identified whole
irreducible hypersurface function field or minimal component field.
The smallest next dependency toward the prior trace bridge is a proved
comparison for (aChart(r,w),vChart(r,w),t) with the earlier generic
Q(v)(t)(a) base and its extension maps. That transformed independence
and trace-tower comparison are not proved here. Scalar-only trace results
remain distinct from the full two-row source. A residue/cohomology or
Gauss–Manin source-class realization, primitive, global clearing,
certificate and solve are not claimed.

Publication is coordinator-owned: no worker commit, push, upstream post,
reply or PR. Posts 1–29 and tally 29 discussions/one closed maintenance
PR/zero accepted authored solves remain unchanged. The exact 430885-byte
parent ledger is preserved as a prefix, SHA256
`f4e1e853360368889cd83be8536d4f0c509a73464d391311c91639c326abbc66`.

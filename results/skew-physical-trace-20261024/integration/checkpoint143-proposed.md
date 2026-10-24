

### Checkpoint 143 — physical coefficient field and all-sheet trace bridge, 24 October 2026 EDT

**Result.** A new [Lean module](formal/HodgeLab/OneReflectionSkew/PhysicalTraceBridge.lean)
closes the coefficient-field/finite-algebra comparison between the existing
physical Curve and the earlier K=Q(v)(t)(a) trace tower. The physical chart
coordinates a=(1+r^6+w^6)/r^3, v=1/r+rw, t are proved independent. Their actual
embedding preserves Curve's existing rational-algebra structure; the
Q-scalar commuting diagram and scalar tower are proved. The proof uses
algebraicity of r over the transformed coordinate field, recovery of w,
and a transcendence-degree bound. It explicitly identifies the existing
nested rational-function field through its coordinate fraction field.
No independence or tower compatibility is assumed.

The existing quotient E=AdjoinRoot f is a finite free rank18 algebra, not
a declared field. Its physical evaluation sends theta to r, derivative
to literal f_r, derivative inverse to 1/f_r, and sourceScalar to the exact
nonzero r^11/(12*f_r). The coefficient of X^18 is1, distinct from parameter a.
The full existing splitting field embeds compatibly into Curve; all18 roots
remain distinct and exhaust the mapped polynomial's roots. A proved
physicalSheet matches r and its evaluation. Power slot11 is not sheet11.

An actual left Curve-algebra isomorphism compares T=Curve tensor_K E with
Curve^18: beta(l tensor e)_j=l*sigma_j(e). T is finite free rank18.
For every e:E, mapped Tr(E/K)(e)=Tr(T/Curve)(1 tensor e)=sum_j sigma_j(e).
For every z:T, trace equals the sum of beta(z)'s components. Arbitrary tensor
scalars are retained. The full scalar-source trace is0 while its physical
single-sheet value is nonzero. Evaluation1=1, trace1=18 and trace(2 tensor1)=36
are distinguished. No field trace of Curve/K or [Curve:K] multiplier appears.

**Pins and execution.** Exact parent 2bbbaa312642822c28483ba85cbbccf0af97d6dc; upstream
`e96be434bd55d6013d7a5854732cb317ca0e43e7`. The protected target record still has
q=1 and A=X0^3Y0^3; its raw SHA256 is
`c6621c8845addf857ed30726f86449d5ea3310c7609641db9e326f9b85f10fbd`.
The [source manifest](results/skew-physical-trace-20261024/source-pins.json)
pins31 local dependency/source files and records the actual local import graph.
All prior proof/result bytes are reused unchanged. Lean4.31.0, Mathlib
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`, Python3.12.14.

The sole writer's final [checker-03 receipt](results/skew-physical-trace-20261024/lean-development/checker-03/validation.json)
PASS records98 declarations/instances audited, one new-module kernel replay,
39 positive controls and10 intended mathematical False-goal controls in
36.357s. Allowed axioms are propext, Classical.choice and
Quot.sound only. Named local algebra instances and attributes are included
in the inventory. Imported cached proofs are not counted as new replays.
Every command has separate stdout/stderr, exit, bound, timing and hashes.
The checker uses explicit exceptions under Python -O and fresh output
paths, with before/after source-pin verification. Negative controls reject
collapsed coefficients, evaluation-as-trace, zero/sign/wrong-twelfth scalar,
normalized trace, dropped tensor multiplier, single-sheet trace and G inversion.

All12 development attempt records and11 actual source snapshots remain.
Attempt01 was a path/setup failure before a new source existed; attempts04,
10 and12 compiled successive stages. Other attempts retain import/API,
rational-instance and scalar-tower-search failures. The environment briefly
became unavailable during one pending run; that original run later returned
and the interruption is recorded. No interrupted calculation was counted.
Checker01 failed three caller rational-instance elaboration requirements
although build/audit/replay passed. Checker02 corrected the choices but
failed because those local instances required a noncomputable header.
Both failed receipts and exact source snapshots are preserved; checker03
uses the explicit named instances and noncomputable header. The mathematical
module was unchanged across these three focused checks.

Separate read-only AI mathematical/API and adversarial evidence reviewers
reviewed source and scope. Their files and any hash/log audit have their
own executor labels; neither ran Lean or symbolic mathematics. These are
AI reviews, not independent human review. The evidence reviewer separately executed a 0.052870366-second -O hash/log audit:38 source/context hashes,48 final command streams, all98 declarations,12 development attempts and11 source snapshots. It also verified both failed checker runs and the exact parent ledger prefix; this audit is not a Lean execution.
Prior full CI40084595344 and its
source-bound focused receipt are reused evidence only, not a new execution.
No new remote CI or publication occurred in this worker. The new focused
CI step uses results/runs/ci-skew-physical-trace. Coordinator owns integration,
normal push and full remote CI verification.

**Reproduction and figure.** The [scoped note](notes/skew-physical-trace-bridge.md)
contains the exact field/maps, hypotheses and command lines. From formal:
`timeout 600 python3 -O check_skew_physical_trace.py --output-dir
results/runs/physical-trace-reproduction`, using a fresh directory and pinned
toolchain. The [scientific diagram](results/skew-physical-trace-20261024/visualization-01/physical-trace-bridge.png)
shows coefficient/splitting/tensor maps, single-sheet versus full trace,
and the precise remaining form boundary. Its reproducible PNG/SVG generator
and receipt bind all inputs and outputs; the PNG is visually inspected.
The figure contains no transient CI status.

**Bounds and remaining dependency.** One mathematical approach; start
10:28:47UTC and final checker completion 2026-10-24T10:50:01.753599+00:00, within45minutes.
Lean120s/checker600s/network45s limits; a separate five-minute changed-file
packaging window. No exploration of another mathematical unit occurred.
The smallest next dependency is compatible allowed-domain physical-form
maps for all sheets fixing common compact V=rU and z, with U_j=V/r_j,
and proved curve/form/source compatibilities. That is not supplied by the
finite-cover scalar evaluations alone. Scalar trace zero does not establish
exactness of the full two-row source; rank34 still means17 slots times2 rows.
Four-form nonvanishing, whole/minimal hypersurface function-field identity,
cohomology/GM, primitive, global clearing, certificate and solve remain outside.
Checkpoint142's valid common domain P[z^-1] is preserved; there is no ambient
fraction-field specialization killing G and no evaluation of G^-1.

No worker commit/push, upstream post/reply/edit or PR. Posts1–29 and tally
29 discussion contributions/one closed maintenance PR/zero accepted authored
solves are unchanged. All440921 parent ledger bytes remain the exact prefix,
SHA256 `1da42f452082925e8d6983c37276a062f336fb4e0a0ca02920403e377fa2ec9f`.

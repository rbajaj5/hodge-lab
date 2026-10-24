

## Checkpoint 140 — 23 October 2026: trace-compatible scalar extension

**Pro mathematical-worker handoff for coordinator integration.** Live fetches
matched notebook parent `716174af1c83b45e4a7c3db8f97a11eb0a3126bb` and upstream
`b790130d43b49ec0ddc6865d0bdc949eeeee2319`. The user reports the new Goal active
in the original coordinator. This worker has no Goal-control or cross-chat
messaging tool; the coordinator owns publication and full remote CI. No commit,
push or upstream write was made by this worker.

The requested scalar-extension dependency is closed locally in Lean. For the
literal monic degree-18 f over K=Q(v)(t)(a), E is the actual AdjoinRoot quotient
K[X]/(f), L is the previously constructed full splitting field, and T=L tensor_K E
has its standard left L-algebra structure. Finite/free instances and both
dimension-18 proofs are explicit. No irreducibility or field assumption on E.

The actual L-algebra isomorphism beta:T→L^18 satisfies
beta(l tensor e)_j=l*sigma_j(e), beta(1 tensor theta)=roots, and
beta(l tensor1)=constant l. Each sigma_j is an evaluation K-algebra
homomorphism, not asserted injective. Interpolation gives surjectivity and
equal dimensions give injectivity. Composing with the existing evaluation
isomorphism gives the actual comparison with the split quotient; generator,
scalar and mapped-polynomial compatibility are explicit.

For every e in E, the proof establishes
baseToSplit(trace_K,E(e))=trace_L,T(1 tensor e)=sum_j sigma_j(e).
For every z in T, trace transports under both algebra isomorphisms.
Mathlib's multiplication-map base change and linear trace base change supply
the identity; it is not a hypothesis. There is no field trace L/K or [L:K]
multiplier. The controls prove trace_E(1)=18 and trace_T(2 tensor1)=36.

The optional explicit element transport fit the same route. Mapping the
separability/copimality relation proves f'(theta) is a unit in E. Its actual
ring inverse has the proved root-evaluation images. Thus quotientWeight_i
maps to the existing split codifferent vector, and its trace in E is 1 for
i=17 and 0 for all i<17, including i=11. This constructs the specified
elements in E; it does not claim arbitrary split-vector descent or construct
a new unsplit trace-kernel basis.

- [Scoped note, canonical maps, proof and limits](notes/skew-scalar-extension-trace.md).
- [New Lean module](formal/HodgeLab/OneReflectionSkew/ScalarExtensionTrace.lean) and [focused checker](formal/check_skew_scalar_extension.py).
- [Final executed receipt](results/skew-scalar-extension-20261023/lean-development/checker-02/validation.json) and [all writer attempts](results/skew-scalar-extension-20261023/lean-development/worker-summary-final.json).
- [Mathematical/API review](results/skew-scalar-extension-20261023/math-review/mathematical-review.json), [adversarial review](results/skew-scalar-extension-20261023/source-review/final-review.json), and [unchanged input pins](results/skew-scalar-extension-20261023/source-pins.json).
- [Reproducible visualization](results/skew-scalar-extension-20261023/visualization-02/scalar-extension-trace.png), [generator](scripts/visualize_skew_scalar_extension.py), and [input/output hashes](results/skew-scalar-extension-20261023/visualization-02/visualization.json).

The sole Lean writer executed the final focused check under Lean4.31.0,
compiler68218e876d2a38b1985b8590fff244a83c321783, Mathlib
fabf563a7c95a166b8d7b6efca11c8b4dc9d911f and Python3.12.3. It passed
51 public declaration/instance audits, one new-module kernel replay,
19 grouped positive controls and three intended false-goal controls in
18.815 seconds. Axioms stay within propext, Classical.choice and Quot.sound.
The negatives reject trace_E(1)=1, trace_T(2 tensor1)=18, and slot11 trace1.
New outputs use fresh directories and preserve immutable historical pins.
Imported notebook/Mathlib proofs are reused, not separately kernel-replayed.

The mathematical AI reviewer inspected the exact compiled source and APIs,
executing no Lean. The adversarial AI reviewer checked24 source/context
hashes,27 command-output hashes,51 audit names including four instances,
and all three intended failures in a0.381-second saved-evidence audit.
These are distinct AI roles, not independent human review. User-relayed
coordinator review remains reported support. Root rendered and visually
inspected the figure; it encodes actual algebra/trace maps and boundaries,
not sampled roots or independent proof evidence.

Retained failures are two numeral-map normalization attempts, one
Separable.map/IsCoprime.map ambiguity, and the first checker's positive-control
parser error. The corrected checker passes without changing the mathematical
source. A reviewer Git-diff false positive came from historical CRLF
attributes; raw and index bytes match the parent, and that file is excluded
from staging. The first figure command used the wrong receipt-schema key;
its exact failed generator/logs remain. A successful first render had layout
crowding, corrected in the final saved figure. No timeout or interrupted
calculation is counted as a result.

Bounds were45 minutes, at most two approaches,120 seconds per Lean command,
600 per checker,45 per network operation, followed by five minutes for
changed-file packaging. One approach was used. Mathematics/checking stopped
at2026-10-24 00:35:00.948569UTC,7m32s after the00:27:29UTC start
(23 October20:27:29EDT). No old focused mathematical checker was rerun.
The workflow adds one focused scalar-extension step and reuses the existing
fresh-artifact upload. A fresh read confirms earlier full CI40039653837
succeeded on3f73632; that is prior-unit evidence, not new remote CI.

The smallest remaining physical dependency is exact differential-source
normalization identifying the prescribed source with the intended quotient
element, including chart/scalar factors. The old Y0=1, X0!=0 and r!=0 chart
conditions and repeated-root specialization a=2,v=1 remain unchanged.
No primitive, global clearing, HasCertificate or target solve is claimed.
Credit benediamond/Benjamin Diamond for the cover, fqlx/Ben Burns for the
architecture, and Mathlib contributors for the APIs.

The complete407122-byte parent ledger prefix remains byte-identical, SHA256
e29180ed04214ae15f796a5fddffda2eff268c50022eb3b957ac84a431512d8c.
All prior result files remain untouched in the proposed staged tree.
The handoff is a binary-safe patch and changed-file ZIP with per-member
hashes and expected staged tree; unchanged parent files, Git databases,
expanded submodules and caches are excluded. The coordinator applies,
reviews and publishes normally, then records actual remote CI separately.
No upstream post, reply, edit or PR. Posts remain1–29; tally remains
29 discussion contributions, one closed maintenance PR, zero accepted
authored solves.

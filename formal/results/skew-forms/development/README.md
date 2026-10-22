# Bounded actual differential-form development

[Snapshots, commands, timings and logs](attempts.json) preserve five direct
Lean compilation attempts, each limited to 90 seconds. No timeout occurred.

- Attempt 1 exposed the missing scalar tower for polynomial restriction of
  the exterior-valued derivation. Its later errors depend on that missing instance.
- Attempt 2 could not load Mathlib.Algebra.GradedMonoid.olean. A targeted
  120-second cache request from the pinned Mathlib directory decompressed
  two already-cached files and exited successfully; no network download
  was needed. Cache setup is not a mathematical result.
- Attempt 3 used RingHom.toAlgebra, which requires a commutative target;
  our exterior algebra is noncommutative. Algebra.compHom correctly
  restricts its scalar algebra instead. The Module.Basis namespace was
  also made explicit. Error recovery warnings do not indicate accepted proofs.
- Attempt 4 left two basis simplifications unfinished: expanding Matrix.vecTail
  and applying the determinant of the basis to itself.
- Attempt 5 compiled the entire module. The final source removes its one
  unused simp argument; the full verifier then rebuilt it and passed.

The final [receipt](../validation.json) records 13 theorem audits, one
new-module kernel replay, five positive and three rejected false controls,
60.828 seconds, Python -O, 120 seconds/process and 600 seconds total.
Its imports reuse earlier verified work. The failures above are dependency
and elaboration failures, not counterexamples or mathematical exclusions.

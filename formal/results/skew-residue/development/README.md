# Bounded development attempts

[Archived source snapshots and logs](attempts.json) retain the implementation
attempts as UTF-8 strings, with original-byte hashes. No failure is presented
as a mathematical counterexample or a nonexistence result.

- NormalChart: first determinant simplification lacked the `Fin.succAbove`
  reduction; a second attempt passed with unused-hypothesis lint warnings.
  The final source removes those warnings and adds the actual normal-map
  Jacobian. Direct compilation and the targeted build passed.
- ResidueNormalization: early attempts exposed the missing rational-algebra
  instance and a need to state that the derivation kills rational integer
  constants. The derivative core then compiled. A later doc-comment/`omit`
  placement error was repaired before the final build. These are proof
  elaboration repairs, not alterations to force a numerical answer.
- The normal module was assigned an eight-minute development bound and the
  residue module twelve minutes; individual compilation commands were capped
  at 90 seconds. The final targeted build passed with cached imports.
- The complete final verifier passed on its first run in 36.593 seconds:
  19 axiom reports, two new-module kernel replays, eight true control
  statements in one file and five independently rejected false statements.
  Bounds were 120 seconds per process and 600 seconds overall; no timeout.
  Inherited modules emit previously recorded lint warnings; none changes
  the verification status or is claimed as a new failure.

The [validation receipt](../validation.json) records commands, versions,
source/input hashes, compiled-artifact hashes and output logs. Earlier
substitution and volume receipts are preserved and reused.

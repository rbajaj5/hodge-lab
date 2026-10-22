# Bounded ambient derivation development

[Source snapshots, command receipts and logs](attempts.json) preserve the
five direct compilation attempts. Each Lean command was limited to 90
seconds. The files record actual timings and exit statuses.

- Attempt 1 could not load a missing cached Mathlib dependency. The first
  targeted cache request used paths relative to the notebook and failed.
  Running it from the pinned Mathlib directory succeeded, decompressing
  262 already-cached files. Both requests had 120-second bounds. No new
  mathematical result follows from cache setup.
- Attempts 2 and 3 exposed an absent characteristic-zero import/instance
  and rational coefficient embedding/simplification issues. Narrowing
  `simp` to the needed identities preserved the 1/7 coefficient. Attempt
  4 compiled the complete construction and residue instantiation.
- Attempt 5 added a reciprocal-rule control and exposed a mismatch between
  `-1 / z^2` and `-(z^2)⁻¹` in the proof script. The
  [first verifier attempt](verifier-attempt01/validation.json) stopped at
  this same elaboration error; its logs are retained. An explicit
  `div_eq_mul_inv` rewrite resolves it without changing the statement.
- The final verifier passed in 40.047 seconds: 12 theorem axiom audits,
  one new-module kernel replay, seven positive controls and three false
  statements rejected at closed False goals. It ran under Python -O,
  with 120 seconds per process and 600 seconds total. No timeout occurred.

These are dependency and elaboration failures, not mathematical exclusions
or counterexamples. Earlier proof receipts remain unchanged. The final
checker is [check_skew_ambient.py](../../../check_skew_ambient.py).

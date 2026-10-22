# Bounded development and rejected verifier attempt

[Full source/output archive](attempts.json) preserves five Lean development
attempts and two failed verifier runs, including their checker sources and logs.
Each Lean development command was capped at 90 seconds, within a ten-minute
development budget. No timeout occurred.

- Attempts 01–02 needed the imported evaluation-negation lemma for the
  negative skew monomial. Attempt 03 compiled the six initial identities.
- Attempt 04 added the existing denominator bindings and left an addition
  associativity goal. Attempt 05 supplied `add_assoc`; all eight compiled.
- The first full verifier built, audited and kernel-replayed the new module,
  but its first negative control did not reduce the rational expression.
  The verifier returned FAIL rather than crediting an error as evidence.
- The second run returned FAIL at the sign control. Its previous control
  emitted a false-equality diagnostic after an incomplete true-value proof;
  accepting that individual control would have been unsound evidence.
  The final harness separately compiles all three true evaluations with
  the proved chart substitution and `norm_num`. Each negative then rewrites
  by its proved evaluation and rejects the false equality with `decide +kernel`.
  Exactly one error is allowed, and unrelated or stuck-reduction diagnostics
  fail the test. The sign control is scaled by seven to compare integers.

These are implementation failures, not mathematical counterexamples or
unsuccessful searches for a primitive. The final proof receipt is separate;
the earlier successful research receipts were not overwritten.

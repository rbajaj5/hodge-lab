# Bounded development history

The first module compile returned errors after 68.58 seconds: a documentation
comment preceded a `set_option`, and simplification commuted a polynomial
product before coefficient extraction. Its source and diagnostics are retained.
The terminal print then encountered Windows' default cp1252 encoding; the
UTF-8 log had already been saved. The development wrapper was corrected to
print UTF-8 explicitly. These are implementation failures, not counterexamples.

The second compile passed in 65.59 seconds under its 120-second limit.
The final verification script's first invocation could not find `lake` in the
non-login WSL PATH (exit 127). `runner01` retains that source and failure;
the script now uses a login shell with properly quoted arguments on Windows.

The final compile, axiom audit, kernel replay and mutation receipts are one
directory above. No failed attempt is reported as a mathematical result.

Review of `verifier01-validation.json` found that its wrong-source-sign test
accepted a stuck `decide` reduction as a negative result. The independently
proved changed coefficient (60) and pairing (2520) were sound, but this log
did not establish the intended test outcome. That receipt is superseded.
The final checker rewrites with the proved coefficient identity, requires
an explicit `is false` diagnostic, and invalidates its receipt at run start
and on any failure. The old script, receipt and diagnostic remain here.

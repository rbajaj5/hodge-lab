# Coordinate comparison development

The first 90-second-bounded compile returned exit 1 in 9.165 seconds:
`Fintype (Fin 6)` was unavailable for `fin_cases`, and the all-one evaluation
left vector indexing goals. Added `Mathlib.Data.Fintype.Fin` and derived the
second value from the already proved symbolic defect with `linear_combination`.
The next 90-second-bounded compile passed in 9.522 seconds, with a harmless
unnecessary-sequence linter warning. These are implementation attempts, not
mathematical counterexamples. The final verifier separately builds and replays
the completed sources. Tool-output timings are recorded here as development
notes; no fresh raw process log is claimed for these two exploratory commands.

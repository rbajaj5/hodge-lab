# Reproduction and execution boundaries

Parent: `84f294e0235c3fd4b5d4849e565536172a74329c`.
Upstream dispatch pin, reused from the human: `27f4bb9ad8757e5841f884d9d30124a3c97a847d`.
The connection is an immutable parent input, SHA256
`a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d`.

Mathematical work started 2026-10-24T15:18:39Z and stopped 2026-10-24T15:32:59Z,
before the authorized 16:00Z deadline. All symbolic child processes had 60-second
external timeouts. No old mathematical batch, Lean module, or remote CI was run.
Export reproduction and figure rendering after that stop introduce no new search.

Python 3.12.14, SymPy 1.14.0, NumPy 2.5.4 were used. Matplotlib is used only
for the optional figure. The scratch dependency path in original receipts is
environment-specific; install matching packages in another environment.

Run from the repository root, always with a fresh output name:

```sh
python3 -O results/skew-mixed-construction-20261024/lead/run_bounded.py \
  results/skew-mixed-construction-20261024/lead/physical_laurent_search.py \
  results/skew-mixed-construction-20261024/lead/REPLAY-NEW

python3 -O results/skew-mixed-construction-20261024/checker/run_bounded.py \
  results/skew-mixed-construction-20261024/checker/check_physical_laurent.py REPLAY-NEW
```

The independent checker binds to the saved author inputs. Its fresh replay
reconstructs them from the literal source, then checks the independent minor.
The following small fallback needs only the pinned parent JSON and NumPy; it
does not require any downloadable result CSV, old archive, or local cache:

```sh
timeout 60s python3 -O results/skew-mixed-construction-20261024/reproduce_laurent.py \
  results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json
```

Expected stdout: prime 32003, 702 coefficient columns, 703-square minor,
determinant 13884. A nonzero augmented minor proves inconsistency over Q for
the declared finite family, regardless of denominators in hypothetical unknown
rational coefficients. It proves nothing about a larger current space.

The `alternate/HANDOFF.txt` contains exact commands for the universal first-jet
family, and `checker/REVIEW.md` distinguishes executed checks from source review.
`lead/triangular-02` is a 60-second timeout, not a completed generic expansion.
The corrected triangular candidate is rejected by the independently executed
finite-jet check in `checker/translation-current-02` instead.

All failures are retained. Parent README, LEDGER, Posts, team board, formal code,
and historical results are not part of this patch. No Git commit or push was made.

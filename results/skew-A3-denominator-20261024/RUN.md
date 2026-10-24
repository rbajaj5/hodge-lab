# Fresh reproduction commands

Run from a notebook checkout containing the unchanged pinned JSON and this
added payload. Intended integration parent2dff6afddab993a216ba3f262197ae69aeb9143a;
the executed worker checkout was cachedfc4f38a338b47addf62d1bf699783302285378fe.
Live and cached source bytes were compared exactly. No newer full checkout
or resulting Git tree is claimed.

Python3.12.14; NumPy2.5.4; SymPy1.14.0 for author; Matplotlib3.10.8 for figure.
The checker uses NumPy and standard-library integer-AST evaluation. Exact
commands, sources, environment and versions actually used are in receipts.
Choose output paths that do not already exist. Every wrapper limits the
subprocess to60 seconds and saves UTF-8 logs, source and exit/timing evidence.

```sh
python3 -O results/skew-A3-denominator-20261024/lead/run_bounded.py \
  results/skew-A3-denominator-20261024/lead/search_A3_sum.py \
  /tmp/A3-author-NEW
python3 -O results/skew-A3-denominator-20261024/checker/run_bounded.py \
  results/skew-A3-denominator-20261024/checker/reconstruct_A3.py \
  /tmp/A3-reconstruct-NEW /tmp/A3-author-NEW/result
python3 -O results/skew-A3-denominator-20261024/checker/run_bounded.py \
  results/skew-A3-denominator-20261024/checker/determinant_A3.py \
  /tmp/A3-determinant-NEW /tmp/A3-author-NEW/result \
  /tmp/A3-reconstruct-NEW/result
python3 -O results/skew-A3-denominator-20261024/lead/run_bounded.py \
  results/skew-A3-denominator-20261024/render.py /tmp/A3-figure-NEW
```

See MATRIX-SPEC.md for the deterministic seed, basis, sample and row order.
Expected coefficient/augmented ranks2400/2401, and determinant13752 modulo
32003 for the first2401 augmented rows. The full delivered raw CSV supports
direct equality checks; a file/hash check is not another mathematical replay.
The original2808-parameter exclusion additionally uses the credited imported
highest-pole/support theorem. No lower tangent restriction is imposed.

The above are reproduction instructions, not additional executions. After
the decisive pass the worker runs only figure rendering and packaging checks.
Do not overwrite frozen result directories or historical receipts.

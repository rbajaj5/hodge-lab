# Fresh reproduction

Use Python3.12, NumPy2.5.4 and SymPy1.14.0 for the author, NumPy for checker
and standalone verifier, Matplotlib3.10.8 for the figure. Exact versions and
commands actually executed are in the receipts. All text is UTF-8.

From the repository root, choose output directories that do not yet exist:

```sh
python3 -O results/skew-A2-denominator-20261024/lead/run_bounded.py \
  results/skew-A2-denominator-20261024/lead/search_A2_sum.py \
  /tmp/A2-author-NEW
python3 -O results/skew-A2-denominator-20261024/checker/run_bounded.py \
  results/skew-A2-denominator-20261024/checker/check_A2_sum.py \
  /tmp/A2-checker-NEW /tmp/A2-author-NEW/result
timeout 60s python3 -O results/skew-A2-denominator-20261024/reproduce_minor.py \
  results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json
python3 -O results/skew-A2-denominator-20261024/lead/run_bounded.py \
  results/skew-A2-denominator-20261024/render.py /tmp/A2-figure-NEW
```

The two wrappers enforce60 seconds and save source, stdout, stderr, exit,
time and hashes. Fresh-directory gates and explicit exceptions remain active
under -O. The author saves879 samples and the1758×1699 augmented matrix.
The checker independently rebuilds every entry and uses Bareiss elimination.
The standalone fallback recreates the decisive first1699 rows from seed
2026102432 and the source JSON; it requires no saved matrix. Expected
determinant14098 modulo32003, coefficient columns1698.

The original2106-parameter-family conclusion additionally uses the explicitly
credited structural theorem; the executable minor alone excludes the1698
reduced family. P1 stays unrestricted throughout. Current rank is full, so
there is no missing kernel certificate. No old computation is part of these
commands. The figure encodes the same boundary and saves input/output hashes.

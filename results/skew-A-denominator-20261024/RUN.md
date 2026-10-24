# Reproduction

Exact parent: aa5a30dff2fd70994c48c484845981c141e77ef9. Python3.12.14,
SymPy1.14.0 and NumPy2.5.4 were used for the new search; the independent and
plaintext minor verifiers require NumPy only. Every mathematical process had
an external60-second limit. No old result was replayed.

From the repository root, with a fresh output directory:

```sh
python3 -O results/skew-A-denominator-20261024/lead/run_bounded.py \
  results/skew-A-denominator-20261024/lead/search_A_sum.py \
  results/skew-A-denominator-20261024/lead/REPLAY-NEW
```

The independent checker consumes the saved author input directory. Its runner
command is recorded verbatim in checker/reduced-sum-01/execution.json; use a
fresh output path. It reconstructs every entry before checking the minor.

Minimal export-independent verification:

```sh
timeout 60s python3 -O results/skew-A-denominator-20261024/reproduce_minor.py \
  results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json
```

Expected: prime32003, columns996, minor997, determinant26947.
This executable establishes the reduced-family exclusion. The extension to
the original1404 family uses STRUCTURAL-DEPENDENCY.md, whose source theorem
was supplied and checked coordinator-side; those old/external execution counts
are not silently included in this worker's results.

Original receipts name a scratch PYTHONPATH. Reinstall the listed versions or
use an equivalent environment; that transient path is not a required input.
The figure needs Matplotlib3.10.8 and must be rendered to a fresh output path.
No credentials, network access, old archive, complete repository dump or
expanded submodule is required for these checks.

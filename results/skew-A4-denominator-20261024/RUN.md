# Reproduction and delivery binding

Use the actual integration parent a773c34804b3d0e1e6db2e1b6e31d89f3c3455cf
with the added payload files. Original source JSON remains at the protected
packet path recorded in source-pins.json; the supplied exact snapshot is
also in inputs/source-rank2-connection.json. Do not overwrite any saved run.

Runtime used: Python3.12.14, NumPy2.5.4, SymPy1.14.0, Matplotlib3.10.8.
No FLINT dependency is needed for these two Pro phases. The exact determinant
was separately executed by the coordinator using python-flint0.9.0.

From the repository root, choose unused output directories:

```sh
a4base=results/skew-A4-denominator-20261024
python -O "$a4base/lead/run_bounded.py" "$a4base/lead/assemble_A4.py" "$a4base/replay-author-NEW"
python -O "$a4base/checker/run_bounded.py" "$a4base/checker/reconstruct_A4.py" replay-checker-NEW "$a4base/replay-author-NEW/result"
```

Each wrapper launches a single -O process with a60-second watchdog, saves
source/runner snapshots, stdout/stderr, exit, elapsed time and hashes, and
rejects existing output directories. The checker wrapper places its named
run beneath checker/. The saved original executions are
lead/matrix-01 and checker/reconstruction-01. A replay is not required for
integration; these commands are supplied for reproducibility only.

For the planned coordinator IO-only binding (no determinant or coefficient
recomputation), supply its frozen NPY with SHA256
8a79cf56d9f01acd1e09e14a8e6b0d7a40db6f945288fb04a0a89008be54efc3:

```sh
python -O "$a4base/bind_local_minor.py" "$a4base/lead/matrix-01/result/augmented-matrix.u16.bin" /absolute/path/to/frozen-local-minor.npy /absolute/path/to/fresh-binding-result
```

This compares the full-matrix prefix with all9,628,609 frozen minor entries.
It requires both exact file hashes and the exact dimensions. It has not
been run in Pro because the coordinator's NPY is not in this environment.
Do not replace the coordinator's frozen determinant evidence with a claim
that this IO comparison recomputed it.

To reproduce the figure from frozen receipts, choose a fresh destination:

```sh
python -O "$a4base/render.py" "$a4base/figure-replay-NEW"
```

The actual figure execution uses the same60-second wrapper and is labeled
presentation-only. Its PNG was inspected. No CI-pending label is embedded.

Delivery: apply only the files beneath payload/, according to MANIFEST.sha256.
The small review ZIP excludes only the bulky matrix, with its exact hash in
omitted-artifacts.json. For the original full ZIP, concatenate numbered
2,000,000-byte parts in numeric order with no separators, then check the
original total length and SHA256 in HANDOFF.txt. The original full archive
and manifest remain immutable; all slices are exact byte ranges.

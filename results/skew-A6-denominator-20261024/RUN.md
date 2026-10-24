# A6 reproduction and delivery binding

Apply only the added payload to integration parent
a5087f7601b0d5047c55add75b5c020251b8a09b. The original connection stays at
the packet path in source-pins.json, with an exact unchanged snapshot under
inputs/. Runtime: Python 3.12.14, NumPy 2.5.4, SymPy 1.14.0, Matplotlib 3.10.8.
The Pro phases require no FLINT. No failed setup route was retried.

From the repository root, choose unused names:

```sh
a6base=results/skew-A6-denominator-20261024
python -O "$a6base/lead/run_bounded.py" "$a6base/lead/assemble_A6.py" "$a6base/replay-author-NEW"
python -O "$a6base/checker/run_bounded.py" "$a6base/checker/reconstruct_A6.py" reconstruction-replay-NEW "$a6base/replay-author-NEW/result"
```

Both wrappers enforce 60-second watchdogs, save source/runner snapshots,
commands, versions, stdout/stderr, exits, timings and hashes, and reject
existing output directories. The checker wrapper places its named run under
checker/. Original executions are lead/matrix-01 and checker/reconstruction-01.
These are reproduction instructions; no extra replay is required for integration.

For optional IO-only matrix matching to the coordinator's frozen NPY:

```sh
python -O "$a6base/bind_local_minor.py" "$a6base/lead/matrix-01/result/augmented-matrix.u16.bin" /absolute/path/to/frozen-A6-minor.npy /absolute/path/to/fresh-A6-binding
```

This checks the exact two hashes and all 20,313,049 decisive entries, without
reconstructing coefficients or recomputing a determinant. The coordinator
separately compares inputs.json domain/basis records. Receiver matching is
pending at freeze; the coordinator's local NPY is not available in Pro.

Full binary: row-major little-endian uint16, no header, 4560×4507,
41,103,840 bytes. Load with numpy.fromfile(path,dtype='<u2').reshape(4560,4507).
Inputs.json records prime65521, seed2026102486, 2280 domain/sample records,
every basis label, rejected points and conventions.

Render the figure from frozen receipts to a fresh directory:

```sh
python -O "$a6base/render.py" "$a6base/figure-replay-NEW"
```

The actual rendering is presentation-only, and its PNG is inspected before
delivery. No previous figure is repackaged as new mathematical evidence.

## Manifest prefixes and archive layout

The full ZIP contains payload/<repository-relative-path>, HANDOFF.txt and
MANIFEST.sha256. The root manifest lists **payload/** paths. Verify it from
the unpacked archive root, then apply the contents of payload/ to the
repository. External ADDED-FILES.txt lists repository-relative additions;
it is not an expected Git tree.

The small review ZIP retains every non-matrix payload byte unchanged.
Its own root MANIFEST.sha256 covers the actual review members. The full
original manifest and handoff are under **original-delivery/**, and
omitted-artifacts.json identifies the one bulky matrix omission. The full
original archive and its slices contain that matrix.

PARTS.sha256 entries begin with **parts/**, relative to the delivery
directory. Concatenate part001, part002, ... numerically as raw bytes,
without separators. Verify the full ZIP byte count and SHA256 in DELIVERY.json.
Each part is at most 2,000,000 bytes. Original ZIP and slice bytes are immutable.

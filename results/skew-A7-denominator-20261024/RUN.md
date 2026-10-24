# A7 reproduction and delivery binding

Apply only added payload contents to integration parent
`030d13b75270f6ad1a774e9c11321038fe6305e9`.
The original literal connection remains at the path in source-pins.json;
an identical snapshot is saved under inputs/. Runtime: Python3.12.14,
NumPy2.5.4, SymPy1.14.0, Matplotlib3.10.8. Pro requires no FLINT.

From the repository root, choose unused run names:

```sh
a7base=results/skew-A7-denominator-20261024
python -O "$a7base/lead/run_bounded.py" "$a7base/lead/assemble_A7.py" "$a7base/replay-author-NEW"
python -O "$a7base/checker/run_bounded.py" "$a7base/checker/reconstruct_A7.py" reconstruction-replay-NEW "$a7base/replay-author-NEW/result"
```

Both wrappers enforce 60-second watchdogs, reject existing output directories,
and preserve source/runner snapshots, commands, versions, stdout/stderr,
exits, timings and hashes. The checker wrapper places its named run under
checker/. Original runs are lead/matrix-01 and checker/reconstruction-01.
These are reproduction instructions, not a request for another integration replay.

The full raw matrix is row-major little-endian uint16, no header,
5280×5209, 55,007,040 bytes. Load with
`numpy.fromfile(path,dtype='<u2').reshape(5280,5209)`.
Inputs.json records prime65519, seed2026102497, all2640 sample/domain records,
the full basis, rejected points and conventions. Final column is positive source.

The coordinator independently computes the first5209-square minor with exact
FLINT; this worker did not run a determinant. That reported execution and its
hashes are recorded in coordinator-reported.json. For IO-only delivery binding:

```sh
python -O "$a7base/bind_local_minor.py" "$a7base/lead/matrix-01/result/augmented-matrix.u16.bin" /absolute/path/to/frozen-A7-array /absolute/path/to/fresh-A7-binding
```

The helper checks both pinned hashes, recognizes NPY by its magic header
(otherwise interprets raw uint16), and compares all27,133,681 decisive entries.
It reconstructs no coefficients and computes no determinant. The coordinator
separately matches domain/basis records. It was not run by Pro; the original
coordinator array is not available here.

Render the scientific figure from frozen receipts:

```sh
python -O "$a7base/render.py" "$a7base/figure-replay-NEW"
```

Actual figure generation was presentation-only, exit0. Its PNG is inspected;
input/output hashes and generator are saved. No old figure is counted as new evidence.

## Packaging and manifest prefixes

`package.py DESTINATION` produces a fresh immutable delivery directory from
only this batch's note and result directory; destination must not exist.
No mathematics is run by that script.

Full ZIP layout:

```text
payload/<repository-relative-added-path>
MANIFEST.sha256
HANDOFF.txt
```

The full root manifest lists **payload/** paths. Verify from the unpacked
archive root, then apply the contents of payload/ to the repository.
ADDED-FILES.txt lists repository-relative additions, not a combined Git tree.

The small review ZIP preserves all non-matrix payload bytes unchanged.
Its root MANIFEST.sha256 covers its actual members. The original full
manifest and handoff are retained under **original-delivery/**;
omitted-artifacts.json identifies the one matrix omission. That matrix is
present in the full ZIP and its slices.

PARTS.sha256 uses **parts/** prefixes relative to the delivery directory.
Concatenate part001,part002,... in numeric order as raw bytes without
separators. Each part is <=2,000,000 bytes. Verify the original ZIP byte count
and SHA256 in DELIVERY.json. That JSON and SHA256SUMS.txt also identify both
archives, manifests and handoff. ZIP bytes and slices are immutable after creation.

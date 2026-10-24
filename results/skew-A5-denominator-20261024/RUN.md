# A5 reproduction and delivery binding

Apply only the added payload files to actual integration parent
ce22ec3a0636e9c2dbe7e90e1a36ae63f5f4b44a. The exact source JSON stays at the
packet path in source-pins.json, with a new unchanged snapshot in inputs/.
Runtime used: Python 3.12.14, NumPy 2.5.4, SymPy 1.14.0, Matplotlib 3.10.8.
No FLINT is needed for the Pro phases; its unavailable installation route
was not attempted. The coordinator's determinant uses its existing FLINT.

From the repository root, choose fresh run names:

```sh
a5base=results/skew-A5-denominator-20261024
python -O "$a5base/lead/run_bounded.py" "$a5base/lead/assemble_A5.py" "$a5base/replay-author-NEW"
python -O "$a5base/checker/run_bounded.py" "$a5base/checker/reconstruct_A5.py" reconstruction-replay-NEW "$a5base/replay-author-NEW/result"
```

Both wrappers enforce a 60-second watchdog and reject existing output
directories. The checker wrapper places its named run under checker/.
They preserve exact source/runner snapshots, command, versions, stdout/stderr,
exit, timing and hashes. Original runs are lead/matrix-01 and
checker/reconstruction-01. These commands are reproducibility instructions;
no extra mathematical replay is required for integration or was run here.

For an IO-only matrix comparison with the coordinator's already frozen NPY:

```sh
python -O "$a5base/bind_local_minor.py" "$a5base/lead/matrix-01/result/augmented-matrix.u16.bin" /absolute/path/to/frozen-A5-minor.npy /absolute/path/to/fresh-A5-binding
```

The helper checks exact file hashes and all 14,478,025 entries of the
first 3805 rows. It does not regenerate coefficients or compute a determinant.
The coordinator separately compares inputs.json basis/domain records with
its independently generated records. These receiver checks are pending at
packet freeze; no local coordinator NPY is available in Pro.

The full binary has no header: row-major little-endian uint16, 3860×3805,
29,374,600 bytes. Use numpy.fromfile(path,dtype='<u2').reshape(3860,3805).
Inputs.json records prime 65519, seed 2026102475, 1930 sample/domain records,
all basis labels, rejections and row/source conventions.

The figure can be rendered from frozen receipts into a fresh destination:

```sh
python -O "$a5base/render.py" "$a5base/figure-replay-NEW"
```

Its actual execution is presentation-only and the PNG was inspected. No
figure or script from an older batch is repackaged as new evidence.

## Archive and manifest prefixes

The full archive contains payload/<repository-relative-path>, HANDOFF.txt
and MANIFEST.sha256. The root manifest lists **payload/** paths. Verify it
from the unpacked archive root; then apply the contents of payload/ to the
repository. ADDED-FILES.txt is an external repository-relative inventory,
not an expected Git tree.

The small review archive retains every non-matrix payload byte unchanged.
Its own root MANIFEST.sha256 covers its actual members; the full original
manifest and handoff are under original-delivery/. The matrix omission is
explicit in omitted-artifacts.json. Do not mistake that deliberate review
omission for missing data from the full original archive.

PARTS.sha256 lists paths starting with **parts/**, relative to the delivery
directory. Concatenate part001,part002,... in numeric order as raw bytes,
without separators, and verify the full ZIP length and SHA256 in DELIVERY.json.
Each part is at most 2,000,000 bytes. Original ZIP and slice bytes are frozen.

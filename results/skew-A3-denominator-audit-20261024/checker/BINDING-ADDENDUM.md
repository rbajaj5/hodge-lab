# Delivered matrix binding addendum

The prepared `bind_delivered_packet.py` executed successfully after the original checker freeze. In **0.735 seconds**, this I/O-only check confirmed that the delivered Pro CSV's **first 2401 rows** equal all **5764801** entries of the independently reconstructed frozen minor. It also compared all **2400** basis labels and the first **1201** sample/domain records exactly. The delivered matrix has 2460 rows; this local comparison does not cover its other 59 rows or remaining 29 point records.

The original `README.md`, `publication-manifest.json`, and `freeze-manifest.json` preserve their historical delivery-pending state. Their statements that the binder was unexecuted describe that earlier freeze, not the present status. No original frozen file, mathematical report, or mathematical receipt was changed. This addendum and the new binding evidence supersede only the delivery-status statements.

The binder did not evaluate a connection, differentiate a coefficient, reconstruct a matrix, compute a determinant, or perform a search. It read and compared existing files. There was no timeout. The independently obtained determinant remains **13752 modulo 32003**; the characteristic-zero exclusion and its finite-family limits are unchanged.

The following delivered hashes are now verified by readback:

| File | SHA-256 |
| --- | --- |
| Uncompressed `augmented-matrix.csv` | `81a5ac8ee1b82bf1e5149e06fe0389c67c6371a058b70f59a84dbfbe256de17b` |
| `inputs.json` | `ffbb8171c6480c39960a60bb63e9d974fa4924999e8e536635061f1a512cec8a` |
| Frozen local `regenerated-minor.npy` | `4ac42e04498fa932c89b32a8e8b9943ae792ce6582a43b39dc5853f604e40298` |
| Frozen mathematical report `A3-minor.json` | `6c2ed5fc2d425e6c3121ffd481d21b742e335fad9c29754f7bb36f497fa57cfc` |
| New `packet-binding.json` | `f35f9cab38ac35305302d8b92ca7a12bb0973f5cade155da57d39c82f9a62966` |
| Executed, previously prepared binder | `a34d8206d9fd74d546317d09bd7d76acb30599a68e553f71f41508e3c3b0b8ec` |

New evidence files are `packet-binding.json`, `packet-binding-receipt.json`, `packet-binding.stdout.log`, `packet-binding.stderr.log`, this addendum, and `binding-addendum-manifest.json`. The latter inventories the new files and binds the original freeze manifest. Raw subprocess streams preserve their actual UTF-8 bytes.

The source hash remains `a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d`, already bound by the independent mathematical report. The author archive extraction and whole-payload manifest checks are coordinator evidence, separate from this checker's CSV/input readback.

Reproduction in a copy containing the frozen local array:

```powershell
python bind_delivered_packet.py --result 'C:/path/to/skew-A3-denominator-20261024/lead/sum-01/result'
```

If the local array is omitted from a published payload, run `audit_A3_regenerated_minor.py` first as documented in the original README. The array can then be compared to the published CSV with this binder.

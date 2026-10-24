# Delivered A-fifth-power matrix binding

The frozen binder executed successfully against the delivered Pro packet in **0.829 seconds**, with no timeout. It verified the announced file hashes and compared all **14478025** entries in the first **3805** rows, all **3804** basis labels and the first **1903** sample/domain records exactly.

The delivered matrix is raw row-major little-endian uint16, shape **3860 by 3805**, with exactly **29374600 bytes**. The binder requires the explicit shape and reads the bytes directly. It does not independently reconstruct the remaining 55 rows or remaining 27 point records. The delivered files were not renamed, converted or modified.

The original ten checker files remain unchanged. The README and original freeze manifest preserve their earlier delivery-pending status; this addendum updates only that historical status. The formerly prepared `bind_delivered_packet.py` was executed without modification. Its receipt and streams are new files.

This was strictly an I/O comparison. No connection or source evaluation, derivative, matrix reconstruction, determinant or search was repeated. The determinant **31971 modulo 65519** remains the independent local FLINT result recorded in `A5-minor.json`. The binding adds no second determinant computation and leaves the finite-family scope and limits unchanged.

| Evidence | SHA-256 |
| --- | --- |
| Delivered `augmented-matrix.u16.bin` | `63a48714c2f7a7ce3a20829540a8573607b5ced164b2203922604e60d9fa342e` |
| Delivered `inputs.json` | `518c96338bbafe294cbbba12d38299c3efb9c22c5daf681f3738972ebe44173a` |
| Frozen `regenerated-minor.npy` | `10dcc8f2d407fb8098eab61fa1f36eeed9ecfc495000f2eb79a99268f760c3b4` |
| Frozen mathematical report | `3ead7fda7eb606548b1b12604324a781ab452fb38395f13e112cfe631c36437f` |
| Executed frozen binder | `8eb82e7e4875f108b2934515b75b40b0fd46d49cfe381bf46514095eea6abbba` |
| New `packet-binding.json` | `998dd2f4ccdbb6da1555af6b91807895b4fa211a7397ad9d7b0696f6e10fa860` |

`packet-binding-receipt.json` binds the command, runtime and raw UTF-8 stdout/stderr bytes. `binding-addendum-manifest.json` inventories the new files, binds the unchanged original freeze manifest and records verification of every original payload. Whole-packet import verification belongs to the coordinator's separate evidence; this checker read the matrix and inputs.

Reproduce in a copy containing the frozen independent array:

```powershell
python bind_delivered_packet.py --matrix 'C:/path/to/augmented-matrix.u16.bin' --inputs 'C:/path/to/inputs.json' --matrix-sha256 63a48714c2f7a7ce3a20829540a8573607b5ced164b2203922604e60d9fa342e --inputs-sha256 518c96338bbafe294cbbba12d38299c3efb9c22c5daf681f3738972ebe44173a --raw-rows 3860 --raw-columns 3805
```

If a publication omits the independent array, first regenerate it using the mathematical script and pinned inputs described in the original README. No general rational-current obstruction or solution of the protected target is claimed.

# Delivered A-sixth-power matrix binding

The frozen binder executed successfully against the delivered Pro packet in **0.484 seconds**, with no timeout. It verified the announced file hashes and compared all **20313049** entries in the first **4507** rows, all **4506** basis labels and the first **2254** sample/domain records exactly.

The delivered matrix is raw row-major little-endian uint16, shape **4560 by 4507**, with exactly **41103840 bytes**. The binder requires the explicit shape and reads the bytes directly. It does not independently reconstruct the remaining 53 rows or remaining 26 point records. The delivered files were not renamed, converted or modified.

The original ten checker files remain unchanged. The README and original freeze manifest preserve their earlier delivery-pending status; this addendum updates only that historical status. The formerly prepared `bind_delivered_packet.py` was executed without modification. Its receipt and streams are new files.

This was strictly an I/O comparison. No connection or source evaluation, derivative, matrix reconstruction, determinant or search was repeated. The determinant **60070 modulo 65521** remains the independent local FLINT result recorded in `A6-minor.json`. The binding adds no second determinant computation and leaves the finite-family scope and limits unchanged.

| Evidence | SHA-256 |
| --- | --- |
| Delivered `augmented-matrix.u16.bin` | `a9dc98a238c3fabc1d19f7fded3ea59c69f836e8c20c9824dafeab3597f45838` |
| Delivered `inputs.json` | `9bf8f320d34d485987866280c3f7925e0d4d1502e48462f2642a96ecf977d627` |
| Frozen `regenerated-minor.npy` | `c12a14314359c8ba92f967238cf55e4d88e89b01b160e0af8be8039e8bea9817` |
| Frozen mathematical report | `e76ec5b025e4b60e1cff69539b3cc9030f366ebf32e58d7ca55d2764f9bf0d5a` |
| Executed frozen binder | `7891aed75260c84fa08f569d1783bead44ed850d45844322ebc25f2faaadb95a` |
| New `packet-binding.json` | `a32ca249fbc084f9adeea7537ba99f41c615b710c26102193d6732c68eef5f99` |

`packet-binding-receipt.json` binds the command, runtime and raw UTF-8 stdout/stderr bytes. `binding-addendum-manifest.json` inventories the new files, binds the unchanged original freeze manifest and records verification of every original payload. Whole-packet import verification belongs to the coordinator's separate evidence; this checker read the matrix and inputs.

Reproduce in a copy containing the frozen independent array:

```powershell
python bind_delivered_packet.py --matrix 'C:/path/to/augmented-matrix.u16.bin' --inputs 'C:/path/to/inputs.json' --matrix-sha256 a9dc98a238c3fabc1d19f7fded3ea59c69f836e8c20c9824dafeab3597f45838 --inputs-sha256 9bf8f320d34d485987866280c3f7925e0d4d1502e48462f2642a96ecf977d627 --raw-rows 4560 --raw-columns 4507
```

If a publication omits the independent array, first regenerate it using the mathematical script and pinned inputs described in the original README. No general rational-current obstruction or solution of the protected target is claimed.

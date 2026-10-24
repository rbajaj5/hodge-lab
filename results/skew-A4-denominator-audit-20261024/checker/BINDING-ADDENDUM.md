# Delivered raw matrix binding

The delivered Pro matrix and inputs are now bound to the frozen independent result. The I/O-only comparison passed in **0.375 seconds**, with no timeout. All **9628609** entries in the first **3103** rows, all **3102** basis labels and the first **1552** sample/domain records agree exactly.

The delivered matrix is raw row-major little-endian uint16 with shape **3160 by 3103**. The binder requires that explicit shape and the exact file byte count. It compares the first 3103 rows with the frozen independently reconstructed NPY minor; it does not independently reconstruct the other 57 rows or remaining 28 sample records. No delivered file was renamed, converted or modified.

The original README and freeze manifest preserve their earlier delivery-pending state. This addendum supersedes only that historical status. All original frozen files remain byte-for-byte unchanged. The mathematical determinant **28764 modulo 65521** is the independently executed local FLINT computation in `A4-minor.json`; this binding performed no second determinant computation, source evaluation, differentiation or search. Pro's larger matrix reconstruction is separate evidence, not an additional executed determinant attributed to Pro.

## Filename adaptation and preserved preparation

The frozen `bind_delivered_packet.py` supports CSV, CSV.gz, NPY and NPZ and remains unexecuted. The subsequently prepared `bind_delivered_raw_u16.py` adds raw `.u16` support and also remains unexecuted. The actual delivered name ends `.u16.bin`, so a separate `bind_delivered_u16_bin.py` adds exactly that filename recognition and was executed. Both earlier prepared scripts are preserved. There was one successful I/O child run and no failed or timed-out binding run.

| Evidence | SHA-256 |
| --- | --- |
| Delivered `augmented-matrix.u16.bin` | `e5822b368f62ac144256f9c3ff933c9ef6fd4002853f7f4fd084c67fb013322c` |
| Delivered `inputs.json` | `c721aa1e0b40997fd50f3467b8eb4d2ab702eba171999866bf07007226af1421` |
| Frozen `regenerated-minor.npy` | `8a79cf56d9f01acd1e09e14a8e6b0d7a40db6f945288fb04a0a89008be54efc3` |
| Frozen mathematical report | `c39d7b4ee6207b1ca65f0c545bfd7925d7fc847a1b9ea7cf987d008e9dadb36d` |
| Prepared raw `.u16` binder | `8b783528b22a01034f92fee1a318b635dea7a062a4c483029828f2b2618c4d48` |
| Executed `.u16.bin` binder | `580b05e60897a32bdd6c1118b1547861116101643b446ed63ec9843d21353cc5` |
| New `packet-binding.json` | `4fcc5a04edea639c30dcfc2217488a3f0555bace0a2eff55d40009f38625dbf3` |

`packet-binding-receipt.json` records the exact executed command, runtime, source hash and raw UTF-8 stream hashes. `binding-addendum-manifest.json` inventories the new files and binds the unchanged original freeze manifest. Whole-archive extraction and verification of all Pro payload files are coordinator evidence, distinct from this matrix/input comparison.

Reproduce in a copy containing the frozen local array:

```powershell
python bind_delivered_u16_bin.py --matrix 'C:/path/to/augmented-matrix.u16.bin' --inputs 'C:/path/to/inputs.json' --matrix-sha256 e5822b368f62ac144256f9c3ff933c9ef6fd4002853f7f4fd084c67fb013322c --inputs-sha256 c721aa1e0b40997fd50f3467b8eb4d2ab702eba171999866bf07007226af1421 --raw-rows 3160 --raw-columns 3103
```

If the independently generated array is omitted from a publication, first regenerate it with the mathematical script as documented in the original README. This I/O binding leaves the finite-family exclusion and its limits unchanged; it adds no general rational-current obstruction or target solution.

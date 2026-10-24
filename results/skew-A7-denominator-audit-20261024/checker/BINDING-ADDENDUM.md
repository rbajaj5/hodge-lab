# Delivered A-seventh-power matrix binding

The frozen binder executed successfully against the delivered Pro packet in **0.453 seconds**, with no timeout. It verified the announced file hashes and compared all **27133681** entries in the first **5209** rows, all **5208** basis labels and the first **2605** sample/domain records exactly.

The delivered matrix is raw row-major little-endian uint16, shape **5280 by 5209**, with exactly **55007040 bytes**. The binder requires the explicit shape and reads the bytes directly. It does not independently reconstruct the remaining 71 rows or remaining 35 point records. The delivered files were not renamed, converted or modified.

The original ten checker files remain unchanged. The README and original freeze manifest preserve their earlier delivery-pending status; this addendum updates only that historical status. The formerly prepared `bind_delivered_packet.py` was executed without modification. Its receipt and streams are new files.

This was strictly an I/O comparison. No connection or source evaluation, derivative, matrix reconstruction, determinant or search was repeated. The determinant **56940 modulo 65519** remains the independent local FLINT result recorded in `A7-minor.json`. The binding adds no second determinant computation and leaves the finite-family scope and limits unchanged.

The checked global metadata agrees: prime 65519, seed 2026102497, full matrix shape 5280 by 5209, 2640 author sample records, the full ordered basis and the first 2605 point/domain records. No mismatch was found in those checked fields.

P1 wording clarification: the frozen mutation text says "A^6-scaled P1 column." Its A^6 refers to the factor on the ordinary P1 operator; the whole equation is multiplied by A^7. The precise mutation is to omit `-A^5 A_i u` from `A^6(partial_i+N_i)u-A^5 A_i u`. The executed coefficient and equation normalization are correct. This clarification changes no executed bytes and involved no mathematical rerun.

| Evidence | SHA-256 |
| --- | --- |
| Delivered `augmented-matrix.u16.bin` | `7ab80831f8757663bc208ecb4a391509ab18080b0a6f776d0a4b57695c9e2230` |
| Delivered `inputs.json` | `4d67271f1607894a72afab28a39d3ee0e2e1752da414f3e85b6b32f418ee4ded` |
| Frozen `regenerated-minor.npy` | `8f4a48490018861c4599e08ae1e6da0e279b874c260e96d6350af74110f81b28` |
| Frozen mathematical report | `9ab4f9b0617984a5780e5e042f5b660bd86c4dfb0395df24e4a5a411dc655526` |
| Executed frozen binder | `cac89d874b2c3b415a3e4472062cc13563fe22e4689b5375a22ccf7b6fbeec61` |
| New `packet-binding.json` | `fef08259f6d061c2a3eb235720c8ace9f403e1297bde6a2d28e5cec0c40b54b5` |

`packet-binding-receipt.json` binds the command, runtime and raw UTF-8 stdout/stderr bytes. `binding-addendum-manifest.json` inventories the new files, binds the unchanged original freeze manifest and records verification of every original payload. Whole-packet import verification belongs to the coordinator's separate evidence; this checker read the matrix and inputs.

Reproduce in a copy containing the frozen independent array:

```powershell
python bind_delivered_packet.py --matrix 'C:/path/to/augmented-matrix.u16.bin' --inputs 'C:/path/to/inputs.json' --matrix-sha256 7ab80831f8757663bc208ecb4a391509ab18080b0a6f776d0a4b57695c9e2230 --inputs-sha256 4d67271f1607894a72afab28a39d3ee0e2e1752da414f3e85b6b32f418ee4ded --raw-rows 5280 --raw-columns 5209
```

If a publication omits the independent array, first regenerate it using the mathematical script and pinned inputs described in the original README. No general rational-current obstruction or solution of the protected target is claimed.

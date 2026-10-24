# A8 delivered-packet binding addendum

The prepared binder ran once after delivery and passed in **0.437 seconds**. This was an I/O-only comparison: no differentiation, source evaluation, reconstruction, determinant, elimination, or search was repeated. The child exited 0; neither the 60-second outer limit nor the 58-second internal watchdog expired.

The delivered headerless, row-major little-endian uint16 matrix has shape 6000 by 5911 and 70,932,000 bytes. Every entry in its first 5911 rows equals the frozen independent minor: **34,939,921 entries**. All **5,910 basis labels** and the first **2,956 sample/domain records** also match exactly. The checked prime (65521), seed (2026102508), declared shapes and sample counts agree. There was no mismatch in these checked fields. The remaining 89 author rows and 44 sample records were not independently reconstructed or compared.

The original nine payloads and their freeze manifest (ten original files total) remain byte-identical. The original README and freeze manifest describe the historical state before delivery; their pending-binding wording is superseded by this separate addendum and the new binding receipt. The previously computed local determinant remains **30337 modulo 65521**; this binding computes no second determinant. The finite-family scope and all limitations in the original README remain unchanged. In particular, the A8 equation uses ordinary P1 factor A7 and quotient correction minus A6 times Ai, with all lower sectors free.

The input files are `results/skew-A8-denominator-20261024/lead/matrix-01/result/augmented-matrix.u16.bin` and the adjacent `inputs.json`. Whole-archive verification is a separate coordinator action.

| Artifact | SHA-256 |
| --- | --- |
| Delivered matrix | `760a3e5cc7c7e0e941a482f2f554cf372f5145371ebf48ff5498300af20da9b3` |
| Delivered inputs | `1e635a3e0c6e5be593ce954e638bd37f2453b882110d7da41ce268709772d9c4` |
| Frozen independent minor | `1c41301ad2a113d530bbd3b13c4ee004ac22fb55219b8bab99ae9850d46ac9e6` |
| Frozen mathematical report | `a9cbcfece3df8b8cd9c1813d685dbb0ad193838292b4212029f6c9c149fb92ff` |
| Executed binder | `e87416360079bfd6a53ea14575fe9e999ddd6977d1d263efa6675bd0c49383f0` |
| New binding report | `cccc43f583dea1298a5b3815eea9f858adde57148cbbdf90bc2e7d3bc229576c` |
| Original freeze manifest | `19fb6f76e71f33d3a8caaa0dc9a7850b96e551368532024cc5c9ac9c97360f69` |

`packet-binding-receipt.json` records the actual command, duration, limits and raw UTF-8 stdout/stderr hashes. `binding-addendum-manifest.json` binds this addendum and the four new binding outputs, without changing the original freeze.

Reproduction from the repository root (I/O only):

```powershell
python results/skew-A8-denominator-audit-20261024/checker/bind_delivered_packet.py --matrix results/skew-A8-denominator-20261024/lead/matrix-01/result/augmented-matrix.u16.bin --inputs results/skew-A8-denominator-20261024/lead/matrix-01/result/inputs.json --matrix-sha256 760a3e5cc7c7e0e941a482f2f554cf372f5145371ebf48ff5498300af20da9b3 --inputs-sha256 1e635a3e0c6e5be593ce954e638bd37f2453b882110d7da41ce268709772d9c4 --raw-rows 6000 --raw-columns 5911
```

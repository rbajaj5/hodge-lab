# Bounded implementation attempts

The [archive](attempts.json) preserves source snapshots, logs and metadata as
UTF-8 JSON strings, with hashes of the original bytes. These are implementation
failures and repairs, not failed mathematical candidates or nonexistence results.

- Coordinate volume: an initial import failed because cached `Sym2.Init` was
  missing. Two local dependencies were built in 5.426 seconds; no network
  fetch was needed. A second attempt exposed finite-index simplification and
  determinant-sign proof goals. The third compiled in 6.881 seconds.
- Density: the first attempt lacked the `field_simp` tactic import. Adding
  `Mathlib.Tactic.FieldSimp` compiled; its unreachable trailing `ring` was
  removed before the final verifier. The first development driver also hit a
  Windows console-encoding error after saving its actual Lean log and receipt.
  Subsequent console output explicitly used UTF-8; the mathematical failure
  and source snapshot were retained.
- Development commands were capped at 90 seconds. The coordinate-module
  work was assigned a 12-minute bound. No timeout supplies evidence here.
- The final [verification](../validation.json) completed in 66.219 seconds,
  with 120 seconds per process and 600 seconds overall. It builds the final
  sources, audits 16 theorems, kernel-replays both new modules, compiles four
  true values, and rejects four corresponding false statements. Its logs are
  separate from these development records.

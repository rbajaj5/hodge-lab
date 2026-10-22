# Preserved development attempts

These are implementation diagnostics, not mathematical counterexamples.

- trace-kernel-dev: finite-index and basis-API elaboration failures, followed
  by successful build and declaration audit.
- trace-free-dev: three failed snapshots record equality orientation,
  summation and matrix/basis API issues; the fourth build passed.
- split-trace-quotient-dev: missing parent olean, optional uncached import,
  then API elaboration issues. Final attempts passed. The optional import
  was replaced by the trace-conjugation proof, with attribution in source.

Development commands were bounded at 90 or 120 seconds. The final source-bound
driver is the authoritative receipt, with a 600-second total budget. No timeout
was treated as a mathematical result. An initial sandboxed WSL call failed
with Wsl/E_ACCESSDENIED before using the authorized execution route.
Historical *.lean.txt snapshots are not compiled project modules.

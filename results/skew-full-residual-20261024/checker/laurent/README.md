# Frozen bounded Laurent-family check

Both executions passed. The supplied Pro verifier gives determinant **13884 modulo 32003** for a 703 by 703 augmented minor. A separately authored audit reconstructs all **494209 entries** of that decisive minor and obtains the same determinant using a different elimination algorithm. This excludes exactly the declared 702-parameter family of six physical flux components. It does not solve the full one-reflection-skew problem or exclude arbitrary rational currents.

## Source, operator, and family

The input is `source-rank2-connection.json` from the public one-reflection-skew-followup packet. Its SHA-256 is:

`a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d`

Write `A = r^3 + r^-3 + (v*r-1)^6/r^15`, `c = t(1-t^2)/7`, and `d = 1+t^6`. The coefficient map is `(a,b,c,d) = (A,t*v,c,d)`. The physical connection is

```
N_r = A_r M_a
N_v = A_v M_a + t M_b
N_t = v M_b + c' M_c + d' M_d.
```

The checked equation is

```
(partial_r + N_r) J_r + (partial_v + N_v) J_v
    + (partial_t + N_t) J_t = r^-4 M_b e0 / 12.
```

Each of the six scalar entries of `(J_r,J_v,J_t)` belongs to

```
span_Q { r^m v^n t^k : -10 <= m <= 2, 0 <= n <= 2, 0 <= k <= 2 }.
```

There are 117 monomials per scalar entry and 702 independent constant coefficients. The source uses the packet's positive orientation. The audit obtains the connection through symbolic differentiation of the coefficient map and obtains all monomial derivatives by symbolic differentiation in physical `r,v,t` coordinates. Thus the `A_v M_a` term, both output rows, and all three flux directions are present.

The sampled points avoid every denominator in the input evaluation, including the connection's ordinary-locus restrictions. Sample points and basis order are fixed in `capture.json`; the decisive matrix is `augmented-minor.npy`.

## Distinct provenance of the two executions

1. **Pro-code replay:** `pro_reproduce_laurent.py` is a byte-for-byte copy of the supplied verifier. `run_pro_replay.py` executes it unchanged and passively captures its matrix before elimination. Its AST evaluator and modular Bareiss algorithm belong to the supplied Pro code. This replay is not an independently authored reconstruction. It completed in 3.360 seconds, exit code 0.
2. **Independent decisive-minor audit:** `audit_laurent_minor.py` uses a separately written rational-polynomial numerator/denominator evaluator, symbolic coefficient Jacobians and symbolic monomial derivatives. It verifies equality of every matrix entry, then computes the determinant by normalized-pivot Gaussian elimination with pivot-product accumulation. It does not use Pro's AST evaluator or Bareiss recurrence. It completed in 2.687 seconds, exit code 0.

The negative control deliberately omits `A_v M_a`: at sample 0, matrix row 0, column 324, the correct value 2666 changes to 12617 modulo 32003. The control is detected.

Each wrapper enforces a 60-second child-process limit and records UTF-8 stdout plus stderr. Its timeout handler preserves any partial streams. Neither recorded execution timed out. Reports and receipts bind executed code, source, logs, and matrix metadata by SHA-256.

## Why this gives a characteristic-zero exclusion

The finite-field sample points have ordinary integer lifts. Every evaluated rational input denominator is a unit modulo 32003, so the exact rational augmented determinant at those lifts reduces to 13884. It is therefore nonzero over the rationals. The 703 augmented columns are linearly independent, whereas the coefficient matrix has only 702 columns. No rational constant coefficient vector can satisfy these necessary evaluations of a rational-function identity.

This argument does not reduce a hypothetical coefficient vector modulo the prime, so denominators of unknown coefficients do not invalidate the conclusion. The same rational rank obstruction persists after any characteristic-zero extension of the constant field.

The conclusion is confined to the displayed monomial support. Additional current denominators, larger exponents, general rational compact currents, and arbitrary fibre-dependent sextic functions are outside this test. Only the decisive first 703 rows are independently reconstructed here; the larger 762-row search matrix and the separate first-jet obstruction in Pro's report are not replayed or certified by this directory.

## Files and hashes

| Artifact | Role | SHA-256 |
| --- | --- | --- |
| `pro_reproduce_laurent.py` | Supplied Pro verifier | `96eed72f71c5aeb9ef03511fb19a3a1e6dde826b368e033444ba085ee2ed68dc` |
| `run_pro_replay.py` | Bounded replay and passive capture | `0b7b128bc604386e6a855e1a19f428a2637d037128939f458d252d14ff82f5c1` |
| `pro-replay.log` | Replay stdout and stderr | `90caa062c702010c76cb2abd9f4c42875f4ce35216ebbcc5f6b597b285c97abf` |
| `augmented-minor.npy` | Captured 703 by 703 matrix | `e893878a7c0ef84fd1ff95ee0e2628cca73460ca0273eaf3d7bc63c5d2541360` |
| `capture.json` | Sample points, basis, provenance | `0a33f20f56e3895aad71956b3020d9fda1499a8fb76797174a1bacd952c1ccaa` |
| `audit_laurent_minor.py` | Independently authored audit | `dd7417f43bd8f7cb6442a84bdda909d32103ffc72a42aca243a3d97fbb5513d4` |
| `independent-audit.log` | Audit stdout and stderr | `88ba8075801ecec5bd55451ce598a83445ad0e6566e7065b86b4078bda576962` |
| `independent-audit.json` | Audit result and scope | `6b8050de2e4575b79b785ed779363ce87365c692bfafea1fb9b0a02d4393c35c` |

Execution receipts: `pro-replay-receipt.json` and `independent-audit-receipt.json`.

## Reproduction

Use Python with NumPy and SymPy; the recorded audit used Python 3.11.9, NumPy 2.4.6, and SymPy 1.14.0. Copy this directory before replaying so the frozen logs and receipts remain intact. From that copy, supply the connection packet explicitly:

```powershell
python run_pro_replay.py --connection 'C:/path/to/source-rank2-connection.json'
python audit_laurent_minor.py --connection 'C:/path/to/source-rank2-connection.json'
```

The first command regenerates the captured matrix and metadata; the second audits them. Each script also has a default source path for the original workspace. No repository files were edited for this check. The directory is frozen after this README was added; no further search or mathematical rerun is part of this handoff.

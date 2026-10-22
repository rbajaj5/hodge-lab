# Target status snapshot after mixed-biweight acceptance

**Date:** 21 October 2026  
**Upstream:** hodge-computer/sextics @ `be8ec0395eccbb0cc8b0a293e638396a3e486822`

## Catalogue

78 targets total: **64 solved**, **14 open**.

Confirmed open targets include:
- one-reflection-skew
- cycle-q2
- off-paired
- mixed-polar
- dense-rational
- polarized-k3-remainder
- klein-coupled-character
- symmetric-sextic-residual
- rank-one-biquartic
- four-plus-two-residual
- quadric-contact-residual
- holdout-moving-branch
- reflection-coupled-residual
- cyclic-triple-residual

## Independent check performed

For **one-reflection-skew**, the reported line
\[
[s:t:6s+2t:3s+2t:2s:7s+8t]
\]
over \(\mathbb{F}_{11}\) was substituted into the defining sextic (after clearing the factor of 7). The resulting form vanishes identically modulo 11, confirming the line lies on the sextic hypersurface. The restriction of the source monomial \(X_0^3 Y_0^3\) to the line is not identically zero. See [one-reflection-skew-line-check.md](one-reflection-skew-line-check.md).

No new rational primitives, full certificates, or accepted solves are claimed. Upstream contribution tally remains unchanged (zero accepted authored solves by rbajaj5).

This note records the verification scope of the present update.


## Later status notice — 22 October 2026, 00:08 UTC

The catalogue and open list above are preserved as the snapshot at `be8ec039`.
The later [monitoring update](upstream-status-20261022.md) records mixed-polar's
acceptance through PR #182 and the current 82-target catalogue (66 solved,
16 open). Holdout-moving-branch's acceptance is already documented in the
[completed transport audit](physical-source-transport-audit.md). These later
statuses do not alter the scope of the line check recorded above.

# Independent \(\mathbb{F}_{11}\) line check for one-reflection-skew

**Date:** 21 October 2026  
**Target:** one-reflection-skew (open)  
**Upstream:** hodge-computer/sextics @ be8ec039

## Defining equation

From `data/one-reflection-skew/record.json`:

\[
F = X_0^6 + X_0^3 X_1 Y_0 Y_1 + \frac{1}{7} X_0 X_1 Y_0^3 Y_1 - \frac{1}{7} X_0 X_1 Y_0 Y_1^3 + X_1^6 + X_1^3 X_2 Y_0 Y_1 + X_2^6 + Y_0^6 + Y_1^6 + Y_2^6
\]

Target source \( A = X_0^3 Y_0^3 \).

## Reported line

\[
[s : t : 6s+2t : 3s+2t : 2s : 7s+8t]
\]

over \(\mathbb{F}_{11}\).

## Independent verification

Substitution of the parametric line into \( 7F \) (clearing the denominator) yields a homogeneous degree-6 polynomial in \( s,t \) that is identically zero modulo 11. The line therefore lies on the skew sextic over \(\mathbb{F}_{11}\).

The source \( A \) does not vanish on the same line.

This confirms the geometric incidence claim in the feedback audit. Rank and minor claims remain author-reported and were not re-computed.

No full certificate or rational primitive is claimed.

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
\ell(s,t) = [s : t : 6s+2t : 3s+2t : 2s : 7s+8t]
\]

over \(\mathbb{F}_{11}\).

## Independent verification

Substitution of the parametric line into \( 7F \) (clearing the denominator) yields a homogeneous degree-6 polynomial in \( s,t \) whose coefficients, ordered as \( s^6, s^5 t, \dots, t^6 \), are all zero modulo 11:

\[
(0,0,0,0,0,0,0) \pmod{11}.
\]

Since 7 is invertible modulo 11, the line lies on the skew sextic hypersurface over \(\mathbb{F}_{11}\).

The restriction of \( A \) to the line is

\[
A|_\ell = s^3 (3s+2t)^3 \equiv 5s^6 + 10 s^5 t + 3 s^4 t^2 + 8 s^3 t^3 \pmod{11},
\]

which is not identically zero (for example, its value at \([s:t]=[1:0]\) is 5). It does vanish at some individual points.

This confirms the previously reported finite-field incidence. Endpoint conditions, characteristic-zero constructions, and the rational primitive remain separate obligations. Rank and minor claims remain author-reported and were not re-computed.

Executable checker: [`experiments/check_one_reflection_skew_line.py`](../experiments/check_one_reflection_skew_line.py)  
Saved output: [`results/one-reflection-skew-line/output.txt`](../results/one-reflection-skew-line/output.txt)

No full certificate or rational primitive is claimed.

**Later focused audit — 21 October 2026:** both line matrices have now been independently reconstructed from the protected target. The fixed-endpoint rank-four kernel consists exactly of two parameterization directions. The new audit also distinguishes the scalar and differential-form characters and replays the small twisted-companion packet. Earlier statements above about unexecuted checks remain historical. [Fresh checks, corrections and remaining obligations](one-reflection-skew-mathematical-audit.md).

# Bounded physical curve realization

24 October 2026 EDT. Start09:39:45UTC, deadline10:24:45UTC.
One sole Lean writer, separate read-only math/API and source/evidence AI reviewers.
At most two implementation approaches;120s per Lean process,600s per focused
checker,45s per network operation; then at most five minutes packaging.

Approach1: preserve independent U,r,w,t in a rational function field; embed
in an algebraically closed field and choose a root of Z^6+cubic. Construct
polynomial and z-localized maps, universal Kähler/exterior pullbacks, then
instantiate prior normalization with exact remaining nonzero hypotheses.
This is the reflection-quotient chart until x²=U is actually constructed.
No homomorphism from the whole old ambient fraction field killing nonzeroG;
no G inverse evaluation or unchanged normal derivation on the curve.

Stop a route at the limit; save exact errors and source. If a second approach
is needed, document it before execution. No placeholder proof, no assumed
source identity, no irreducible whole-hypersurface claim. No old mathematical
checker rerun. No residue/deRham/cohomology theory, primitive or solve.
Coordinator owns commit/push/full remoteCI; this worker packages only.

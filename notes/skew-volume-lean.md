# One-reflection-skew: ordered coordinate volume in Lean

21 October 2026 EDT / 22 October UTC. This closes the coordinate-Jacobian
and signed ambient-volume coefficient step left by checkpoint 124. It does
not take a residue or construct a rational primitive.

![The actual Euler-volume matrix, its sign, and the square-coordinate factor](../visualizations/skew-volume.png)

## Pins and reused evidence

Notebook parent: [`25047b5`](https://github.com/rbajaj5/hodge-lab/commit/25047b538e33dd5e76874744d2ac22cb8483cf08).
Fresh upstream: [`d5e9ef2`](https://github.com/hodge-computer/sextics/tree/d5e9ef223a2cd210517f35c071e9a5108a15e025).
The [protected record](https://github.com/hodge-computer/sextics/blob/d5e9ef223a2cd210517f35c071e9a5108a15e025/data/one-reflection-skew/record.json),
REC equation and provenance were fetched under 45-second request bounds.
Their Git blob and SHA-256 pins are in [inputs.json](../formal/results/skew-volume/inputs.json).
They agree with the completed chart proof's inputs: variable order
`(X0,X1,X2,Y0,Y1,Y2)`, rational coefficients, q=1, source A=X0³Y0³.

The [chart proof and source-binding receipt](skew-chart-lean.md) are reused,
not rerun. In particular, they identify the literal protected polynomial
with the existing Lean `p7/7`, retaining the factor seven. The new runner
hash-checks those proof sources, inputs and the prior passing receipt before
and after verification. This batch makes no new acceptance-status audit.

## Maps, orders, and orientation

Work on the representative Y0=1, with parameter order `(x,r,w,t,z)`:

\[
\varphi=(x,rx,wx,1,t,z),\qquad U=x^2,
\quad G(U,r,w,t,z)=z^6+aU^3+bU^2+cU+d,
\]

where a=1+r⁶+w⁶, b=rt(1+r²w), c=rt(1−t²)/7 and d=1+t⁶.
The reused Lean identities give F(φ)=G(x²,r,w,t,z) and A(φ)=x³.

The new [CoordinateVolume module](../formal/HodgeLab/OneReflectionSkew/CoordinateVolume.lean)
defines the six coordinates as `MvPolynomial (Fin 5) K`, differentiates
them using `MvPolynomial.pderiv`, and evaluates those derivatives. The
matrix entries are proved from those definitions, not assumed as a matrix
with the desired determinant. The affine output order is
`(X0,X1,X2,Y1,Y2)`; its Jacobian determinant is x². The square-coordinate
map has output order `(U,r,w,t,z)` and determinant 2x.

The ordered Euler-volume coefficient is represented algebraically by
`det [φ, ∂xφ, ∂rφ, ∂wφ, ∂tφ, ∂zφ]`. This is the alternating determinant
coefficient convention for the Euler contraction of the six-coordinate
volume. With the protected row order, its matrix is

\[
\begin{pmatrix}
x&1&0&0&0&0\\
rx&r&x&0&0&0\\
wx&w&0&x&0&0\\
1&0&0&0&0&0\\
t&0&0&0&1&0\\
z&0&0&0&0&1
\end{pmatrix}.
\]

Lean identifies the Y0-row/first-column minor with the actual affine
Jacobian, then expands along that row. Its zero-based index is 3, so the
coefficient is **(−1)³x²=−x²**. An odd permutation of either ordered volume
reverses the sign; the stated order is part of this result.

This is a formal algebraic coefficient model. It does not instantiate a
general differential-form pullback, Kähler differential, or analytic
derivative API. The notation Ω below refers to the stated determinant
convention, whose coefficient is what the module proves.

## Source coefficient and precise chart hypotheses

The [VolumeDensity module](../formal/HodgeLab/OneReflectionSkew/VolumeDensity.lean)
combines the actual protected source and denominator with that coefficient:

\[
c_x=\frac{A(\varphi)\det[\varphi,D\varphi]}{F(\varphi)^2}
=-\frac{x^5}{G(x^2,r,w,t,z)^2},\qquad
c_U(U)=-\frac{U^2}{2G(U,r,w,t,z)^2}.
\]

Lean proves the forward coefficient identity `c_U(x²) · det S = c_x`
under G(x²,r,w,t,z)≠0. Recovering `c_U(x²)=c_x/det S` additionally uses
x≠0. This proves the minus sign and factor 1/2 of the ordered ambient
coefficient of AΩ/F² in U-coordinates. The 1/2 comes from dU=2x dx; it
is not a trace or covering-average factor.

| Statement | Hypotheses and boundary |
| --- | --- |
| Coordinate evaluations and determinants x², 2x, −x² | Any field; forward polynomial identities also hold at x=0 |
| Source/denominator comparison and normalized coefficient | Characteristic-zero field, matching the rational protected record |
| Affine Jacobian nonsingular iff x≠0 | Any field |
| Square Jacobian nonsingular iff x≠0 | Characteristic-zero field |
| Rational-volume interpretation | G≠0 is the ambient complement **before residue**, not a hypothesis imposed on points of G=0 |
| Recovery by inverse square Jacobian | x≠0 and G≠0; the forward equality needs no x≠0 |

Lean's scalar division is totalized, so `xCoefficient_eq` is also a scalar
identity when its denominator vanishes. This is not an assertion that the
rational form is defined there. No a≠0, z≠0 or discriminant assumption is
needed for this unit. Recovering r=X1/X0 and w=X2/X0 likewise requires
x≠0; no global chart-inverse or coverage theorem is claimed.

## Executed checks and bounded failures

The [passing receipt](../formal/results/skew-volume/validation.json) records
**16 theorem audits**, **two new-module kernel replays**, **four true point
evaluations compiled in a separate positive-control file**, and **four rejected false statements**.
Only `propext`, `Classical.choice` and `Quot.sound` appear in the listed
axiom reports. Earlier modules and mathlib are trusted imports; this is
not a fresh replay of all dependencies or a separate kernel implementation.

The [independent exact reconstruction](../formal/results/skew-volume/independent.json)
uses Python rational sparse polynomials and permutation determinants. It
rebuilds all 30 physical and 25 square-map partial entries, both Jacobians,
the six Euler-cofactor summands, and the source numerator directly from
the pinned record. At `(x,r,w,t,z)=(2,0,0,0,0)`, it obtains G=65,
affine determinant 4, square determinant 4, volume coefficient −4,
c_x=−32/4225 and c_U=−8/4225. This external arithmetic check is distinct
from the Lean proofs.

The controls reverse the orientation, omit one affine x factor, omit
the square-map factor two, and assert a nonzero square Jacobian at x=0.
Each true value compiles first. Each false statement must then fail with
exactly one explicit false-proposition diagnostic and no unrelated error.
The checker exits unsuccessfully on any failed requirement, including
under Python `-O`.

Final verification: **66.219 seconds**, 120 seconds per process, 600 seconds
overall. Lean 4.31.0; mathlib
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`; Python 3.11.9.
No timeout. [Development attempts](../formal/results/skew-volume/development/README.md)
preserve missing-cache/import and proof-simplification failures; none is
treated as a mathematical counterexample. All commands and output hashes
are in the receipt. CI is wired to rerun the checker; this report describes
local execution, not an unobserved CI outcome.

```sh
# From formal/, with the pinned dependencies already installed:
python3 -O check_skew_volume.py
# From the repository root, using Matplotlib:
python3 scripts/visualize_skew_volume.py
```

The [diagram generator](../scripts/visualize_skew_volume.py) reads the
reconstructed matrix and checks its receipt and source hashes. The rendered
PNG was inspected. It displays actual coefficients and assumptions; it
does not prove a primitive or a global transport statement.

## Remaining dependency and attribution

The next distinct formal obligation is the residue reduction of this
ambient double-pole coefficient to the previously computed curve source,
including its normalization and normal-coordinate assumptions. This batch
does not prove the earlier 5/72 residue factor. It also does not establish
global descent, finite trace, denominator clearing, a rational primitive,
`HasCertificate`, new denominator/degree coverage or the 45-versus-504 image
comparison. The existing bounded exclusion is unchanged.

Recent upstream residue-transport support was read in a
[separate pinned context check](../formal/results/skew-volume/upstream-context.json).
Its signed density/Piola result has inverse, chain-rule, mixed-partial and
nonzero-normal hypotheses. We have not instantiated or replayed that
framework here. Its availability does not discharge those hypotheses.

Credit: Benjamin E. Diamond and the upstream contributors for the protected
target and framework; fqlx for the physical quotient/source reduction and
companion formulation cited in the earlier notebook. This work formalizes
that notebook coordinate step; it makes no novelty or solve claim. An
independent read-only reviewer checked theorem and verifier scope. Published
in Hodge Lab only, with no upstream post, reply, edit or PR. Tally unchanged:
**29 discussion contributions, one closed maintenance PR, zero accepted
authored solves**.


## Follow-up — checkpoint 126

The subsequent [local residue-coefficient proof](skew-residue-lean.md) checks
the +5/72 factor using actual normal differentiation and alternating signs.
The ambient derivative theorem has an explicit coordinate-derivation
hypothesis; constructing that derivation and a general residue operator
remain separate. The preceding checkpoint-125 scope is retained as history.

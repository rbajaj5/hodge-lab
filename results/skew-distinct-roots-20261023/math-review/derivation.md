# Independent mathematical derivation: generic distinct roots

**Reviewer:** `distinct_derivation`, an AI mathematical specialist working
separately from the Lean implementation writer. This is not independent
human review. This file records the selected first approach and an exact
integer-polynomial check; it does not claim that any Lean file was compiled
by this reviewer.

## Statement and fields

Let `k` be a characteristic-zero field, let `v` belong to `k`, and let
`K = k(a)` be the rational-function field in one formal indeterminate `a`
over `k`. Embed `k` in `K` by the constants map. Then

\[
f(X)=X^{18}+X^{12}+(vX-1)^6-aX^{15}\in K[X]
\]

is separable. For the physical generic coefficient field, take explicitly

\[
V=\mathbb Q(v),\qquad k=V(t),\qquad K=k(a).
\]

Each successive field is a rational-function field in a new formal
indeterminate over the preceding field. Thus `v` is transcendental over
`Q`, `t` is transcendental over `Q(v)`, and `a` is transcendental over
`Q(v)(t)`. This tower is the intended iterated presentation of the generic
field `Q(a,v,t)`; it makes the algebraic-independence assumption explicit.
The separability proof only uses the last transcendence statement and
allows arbitrary `v` in `k`.

Set `L = SplittingField(f)`, with its canonical injective field map
`K → L`. All appearances of `a`, `v`, and `t` in `L` mean their images
through the indicated field embeddings. The canonical splitting-field
construction supplies splitting; the argument below supplies separability.
The existing proof `physical_degree` supplies degree eighteen. Consequently
the root set in `L` has eighteen elements, and an equivalence from `Fin 18`
to that root set, followed by its subtype inclusion into `L`, supplies an
injective tuple `rho : Fin 18 → L` of roots. Such an enumeration uses choice;
no canonical ordering of algebraic roots is claimed.

The existing `physical_eq_split_cover`, `physical_trace_last`, and
`physical_trace_slot_eleven` then apply in `L` to the embedded parameters
and this tuple. Root membership must be transported from evaluation of
`f.map (algebraMap K L)` to the literal polynomial over `L`; this uses the
coefficient-map identity for the same literal expression. It is not a new
physical coordinate or differential normalization.

## Selected elimination argument

Write

\[
P(X)=X^{18}+X^{12}+(vX-1)^6,
\qquad f(X)=P(X)-aX^{15}.
\]

The combination

\[
\begin{aligned}
D(X)&=Xf'(X)-15f(X)\\
&=3X^{18}-3X^{12}+(vX-1)^5(15-9vX)
\end{aligned}
\]

has coefficients in `k` because the two terms involving `a` cancel
exactly. Its constant term is `-15`, which is nonzero in characteristic
zero, so `D` is a nonzero polynomial in `k[X]`.

Suppose `r` in a field extension `E/K` were a common root of `f` and `f'`.
Then `D(r)=0`, so `r` is algebraic over `k`. Since `f(0)=1`, `r` is
nonzero. The root equation gives

\[
a=\frac{P(r)}{r^{15}}.
\]

The right-hand side is algebraic over `k`, as it is obtained from the
algebraic element `r` and elements of `k` by field operations. Therefore
the image of `a` in `E` is algebraic over `k`. Injectivity of the embedding
`K → E` then makes `a` algebraic over `k` in `K`, contradicting its
transcendence. Thus `f` and `f'` have no common root in any extension and
are coprime; equivalently, `f` is separable.

For the Mathlib coprimality API, the same reasoning works in an arbitrary
commutative domain algebra `A/K`. It need not be a field: `r^15` is a
nonzero divisor, `r^15` is algebraic over `k`, and
`r^15 * image(a) = P(r)` is algebraic over `k`.
`IsAlgebraic.of_mul` gives algebraicity of `image(a)` without introducing
an inverse. The scalar tower `k → K → A` must be made explicit. This is
the same first mathematical approach, not a second approach.

## Exact check executed by this reviewer

`check_elimination.py` uses only Python's standard library and exact
integer arithmetic in sparse `Z[a,v,x]`. Its runner requires a fresh output
directory and imposes a 30-second process bound. The one new execution is
saved in `exact-01/`; it exited zero in approximately 0.040 seconds with
empty stderr under Python 3.12.14. The exact runtime is in `receipt.json`.

The output verifies both the factored identity above and the complete
sparse coefficient table

\[
\begin{aligned}
D(X)={}&3X^{18}-3X^{12}-9v^6X^6+60v^5X^5-165v^4X^4\\
&+240v^3X^3-195v^2X^2+84vX-15.
\end{aligned}
\]

It checks the absence of `a`, `D(0)=-15`, `f(0)=1`, and the exact recovery
identity `f + aX^15 = P`. Three controlled mutations have the intended
nonzero obstruction:

| Mutation | Exact obstruction |
| --- | --- |
| Replace multiplier `15` by `14` in `X f' - 15 f` | Residual coefficient `-1` of `a X^15` |
| Replace `-a X^15` by `-a X^14` but keep multiplier `15` | Residual coefficient `1` of `a X^14` |
| Replace `15-9vX` by `15+9vX` in the asserted eliminant | Nonzero difference `18vX(vX-1)^5` |

These controls validate the selected exact algebraic calculation. They
do not establish separability without the field argument, and they do
not themselves prove that the literal polynomial is a physical source
normalization. The existing source binding and current authoritative
source comparison remain separate evidence.

Reproduce into a new directory, from the notebook root:

```bash
python3 results/skew-distinct-roots-20261023/math-review/run_exact_review.py \
  --output-dir /tmp/hodge-distinct-math-review-reproduction
```

The fresh directory must not already exist. The deterministic `stdout.json`
hash is `171308d662e060be8e28bf960ea784324389d383d807bf98177be4544d3f8a28`.
Runtime metadata necessarily changes on a reproduction.

## Reused repeated-root control and scope boundary

The previous immutable derivation receipt
`results/ci-receipt-physical-cover-20261023/math-review/derivation-review.json`
has raw SHA256
`83eddfdd118095a73e2cd9a978e37b75db09ec42abad841ec5b01b6b5bfe5840`.
It already established exactly that, at `a=2`, `v=1`,

\[
f(X)=X^{12}(X^3-1)^2+(X-1)^6,
\qquad f(1)=f'(1)=0,\qquad f''(1)=18.
\]

That specialization has an exactly double root at `1` over `Q`.
The prior focused Lean checker also rejected its universal-simple-root
negative control. This reviewer inspected and reused those saved receipts;
the old calculation and old Lean checker were not rerun. Their historical
scope and hashes remain unchanged.

The generic theorem does not conflict with this specialization. Its
hypothesis that `a` is transcendental over `k` fails when `a=2`. There is
also no homomorphism from the whole rational-function field `k(a)` to
`k` that sends `a` to `2`: it would send the nonzero invertible element
`a-2` to zero. Polynomial specialization can be meaningful, but it is not
the injective field embedding used by this theorem.

No transfer from a squarefree specialization is used. No expanded
discriminant, unsplit descent, physical chart derivation, source
normalization, primitive, clearing, `HasCertificate`, or solve is claimed.
The original physical chart restrictions remain those of the previous
binding note: the `X0 ≠ 0` chart for coordinate ratios and `r ≠ 0` for the
stated change involving `r⁻¹`. This separability unit does not prove those
geometric chart assumptions.

## Inspected pinned Mathlib APIs

These are source-inspection findings at Mathlib commit
`fabf563a7c95a166b8d7b6efca11c8b4dc9d911f`; this reviewer has not independently
compiled their proposed use.

| Purpose | API and source |
| --- | --- |
| Coprimality from absence of a common root in domain algebras | `Polynomial.isCoprime_iff_aeval_ne_zero`, `Mathlib/FieldTheory/SplittingField/Construction.lean` |
| Recover algebraicity of a factor using an algebraic nonzero divisor | `IsAlgebraic.of_mul`, `Mathlib/RingTheory/Algebraic/Integral.lean` |
| Pull algebraicity back through an injective extension map | `isAlgebraic_algebraMap_iff`, `Mathlib/RingTheory/Algebraic/Basic.lean` |
| Transcendence of the generic final indeterminate | `RatFunc.transcendental_X`, `Mathlib/FieldTheory/RatFunc/AsPolynomial.lean` |
| Root count from separability and splitting | `Polynomial.card_rootSet_eq_natDegree`, `Mathlib/FieldTheory/Separable.lean` |
| Enumerate a root set of the certified cardinality | `Fintype.equivFinOfCardEq`, `Mathlib/Data/Fintype/EquivFin.lean` |
| Recover evaluation-zero evidence from root-set membership | `Polynomial.aeval_eq_zero_of_mem_rootSet`, `Mathlib/Algebra/Polynomial/Roots.lean` |

## Assessment

The mathematical argument is complete for the stated generic field and
supplies the desired distinct-root data in the specified splitting field.
Its formal completion must be established by the sole Lean writer's actual
compiled declarations, axiom report, kernel replay, and focused controls.
The exact script execution and this mathematical review are separate from
those Lean executions and from any later remote CI run.

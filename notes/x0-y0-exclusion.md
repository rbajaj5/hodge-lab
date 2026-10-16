# Excluding the degree-seven X0/Y0 pair

This closes family **13** in [fqlx's prior mixed-family packet](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18982957).
Together with our earlier family-22 exclusion and [fqlx's newly published family-30 proof](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18983962), reproduced here, it completes the **9,453 of 9,453 two-character families** in that degree-seven scan. It does not exclude general degree-seven denominators.

Keep

```text
F = X0^6 + X1^6 + X2^6 + Y0^6 + Y1^6 + Y2^6
    + X0^3 X1 Y0 Y1 + X1^3 X2 Y1 Y2,
A = X0^3 Y0^3, q = 1.
```

The Euler-normalized certificate equations are `N(F)=AD` and
`B(D,N)=D div(N)-N(D)=FC`. Degree-seven denominators are considered modulo
the full `F S_1` gauge. The pinned public E1 calculation proves that its 295
denominator coordinates and 840 Koszul fields span the complete spaces, with
289 denominator coordinates left after removing the six gauge directions.

For `chi_X0=(0,0,1)` and `chi_Y0=(1,2,3)`, the kernel of their difference in
the order-216 diagonal group has order 36. Projection of the numerator with
the denominator fixed retains 58 Koszul fields. The complete denominator pair
has 13 coordinates, `a0,...,a12`. Exact division by `F` yields 244 physical
equations. The quotient `C` is unrestricted; numerator correction coefficients
are shared across the equations.

The proof has four steps.

1. Exact affine chart contradictions force `a1=a8=0`. The packet retains all
   13 initial charts, including the unresolved ones, and the checker replays
   each recorded inference.
2. An exact linear combination of the actual physical equations equals `L^2`,
   where `L=3a6-6a7+a9+a11+a12`. Hence `L=0` over the complex numbers. Solve for
   `a6`; this uses no positivity assumption.
3. Eleven exact linear combinations of the transformed physical equations
   eliminate every numerator variable. They are necessary quadratic equations
   in the two groups
   `u=(a0,a2,a3,a4,a5)` and `v=(a7,a9,a10,a11,a12)`. Each equation is
   bihomogeneous in `(u,v)`, with bidegree `(2,0)`, `(1,1)`, or `(0,2)`.
   The checker verifies this property explicitly.
4. If both groups were nonzero, some `u_i` and `v_j` would be nonzero.
   Bihomogeneity permits normalizing those two coordinates separately in the
   necessary equations. For each of the 25 charts, the packet supplies rational
   polynomials `h_k` satisfying exactly `sum_k h_k f_k = 1`, where `f_k` are the
   eleven normalized necessary equations. Therefore no such chart has a common
   complex zero. One entire character component must vanish, and the previously
   checked single-character theorem excludes the remainder.

Separate normalization in step 4 is used only for the explicitly checked
bihomogeneous necessary equations. It does not assume that the original full
numerator equations are invariant under independent rescaling of the two
denominator components.

The exact checker verified 17 initial inferences, one square identity, 11
necessary relations, and 25 chart identities containing 31,974 multiplier terms
of degree at most five. A second polynomial implementation reconstructed 845
columns and 16,608 nonzero physical coefficients, using the opposite division
ordering and an independent subgroup test. It also rejected a corrupted chart
identity and replayed all 138 existing single-character families, comprising
289 charts and 460 inferences.

## Discovery and failed approaches

Factoring the necessary quadrics suggested the linear square relation. Testing
individual coordinate cubes and fourth powers did not yield new vanishings.
Testing squares of the 25 mixed products also failed to produce a witness in
the tested degree-four row space; a larger tracked degree-six calculation was
stopped after a more direct route succeeded. Those failures have no general
nonexistence implication.

Singular's radical calculation suggested that every product `u_i v_j` vanishes.
Rather than trusting that returned radical as the proof, the saved certificate
uses the 25 explicit affine contradictions. Its generator used rational
Groebner bases and transformation matrices; see the
[Singular reference](https://github.com/Singular/Singular/blob/spielwiese/doc/reference.doc)
for `lift` and `liftstd`. The supplied verifier does not depend on those
algorithms or their reported ranks.

Before fqlx's new packet arrived, our `{chi_X1, chi_Y1}` calculation had a rational unit-ideal
calculation on five charts. A full-system transformation-matrix export exceeded
its 50-second limit, while the corresponding basis calculation completed.
In 48 bounded subset tests, the first chart was reduced from 223 equations to
63 while retaining a rational unit-ideal result. This is a smaller subsystem,
not a proved minimum. Its transformation-matrix export also exceeded 50 seconds
and returned no multipliers. Both failed export attempts and the successful
basis computations are preserved in the provisional calculation bundle.
No modular computation or timeout is treated as an exact exclusion certificate.

That export gap was subsequently filled by **fqlx's distinct family-30 proof**,
which selects 41 consequences independent of the second denominator component.
We downloaded revision `d69313fe578843f8341e6ed557c425bc7755c1d7`, checked all 20
file hashes, and ran both its source-only verifier and independent audit with
`python -S`. Both passed, including the five identities with 44,681 coefficient
products. The [manifest](../references/fqlx-pair30.json) and
[replay logs](../results/upstream-pair30/replay.json) retain that attribution.
Our earlier full-system and 63-row export timeouts remain failed attempts;
they are not presented as the source of that proof.

## Reproduce and attribution

In a recursive checkout of this repository:

```sh
python -S algebra/degree7_e1.py --check
python -S algebra/degree7_x0_y0.py --check
python -S experiments/reproduce_pair30.py --fetch
```

The first two commands are offline checks. The third fetches the pinned
upstream packet and executes both of its checkers. See our
[checker](../algebra/degree7_x0_y0.py),
[exact packet](../results/degree7-x0-y0/certificate.json.gz),
[report](../results/degree7-x0-y0/report.json), and
[local validation](../results/degree7-x0-y0/validation.txt).

Credit: fqlx supplied the prior 9,450 pair exclusions, single-character result,
complete E1/Koszul calculations, symmetry strategy, residual-family list, and
new family-30 proof. The repository authors' Euler normalization and complete
correction framework underlie this work; their exposition attributes the
certificate bridge to Benjamin E. Diamond and the residue framework to
Griffiths. This family-13 continuation and its code were developed with OpenAI
Codex assistance for `rbajaj5`. The two polynomial implementations are
computational cross-checks, not independent human review.

## Boundary of the conclusion

Our new exclusion concerns only the stated two-character degree-seven family.
The combined count of 9,453 uses the explicitly attributed prior work above.
It does not prove nonexistence in degree seven generally, does not raise
the unconditional denominator lower bound beyond seven, and does not solve the
holdout's existence problem. Priority beyond the identified sources has not
been established by a fresh literature search.

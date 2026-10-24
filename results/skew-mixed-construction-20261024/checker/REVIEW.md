# Independent AI checker: new mixed-current batch

Parent: `84f294e0235c3fd4b5d4849e565536172a74329c`.
Pinned connection: `a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d`.
No Lean, network requests, historical result edits, commits, or publication by this worker.
All executed symbolic checks use `python3 -O`, a fresh run directory, and an external 60-second limit.

## Executed checks

1. `triangular-gauge-01`: the literal connection satisfies coefficient scaling,
   fibre scaling, and translation identities. The resulting mixed gauge field
   has triangular connection matrix. This supplies a candidate family, not a solution.
2. `translation-current-01`: **failed mathematical gate**. The originally supplied
   signs of the `K=C^2-3tvD` terms did not give the claimed tangent field. The failed
   source and exact nonzero matrix are retained.
3. `translation-current-02`: the corrected field has
   `G_t=-2tK`, `G_v=-tvw+3a q+2vK`. Its full two-row current is rejected at two
   exact physical points. Independent truncated Taylor arithmetic includes every
   required coefficient derivative and physical `chi_v,chi_vv`; the full
   residual equals the predicted `chi*Cvec`. Four controls at each point reject
   omitted cover motion, omitted t differentiation, omitted t connection, and
   transposed connection matrices. No scalar trace computation is used.
4. `first-jet-system-01`: **implementation failure** caused by multiplication of
   a SymPy rational and a Python boolean. The failed source/log is retained.
5. `first-jet-system-02`: independently reconstructs the alternate worker's
   52-by-30 coefficient system by the coefficient recurrence
   `A[(i,n),(j,k)] = coeff(N_ij,n-k)+(2k-n-1) coeff(Delta,n-k+1) delta_ij`.
   The reconstructed matrix and right hand side exactly match the supplied
   system. A separately constructed integer left-null vector has `w*A=0`
   and `w*rhs!=0`. Coefficient rank is 30, augmented rank is 31.
   Operator checks reject omission of the denominator derivative and connection
   transposition.

## Read-only review, separate from executions

The alternate worker's `first-jet-cert-02` provides its own executed generic
jet, residue, and infinity-order checks. I inspected those sources and the
logical argument; I did not rerun them. Their argument bounds a rational
`K` by `K=(P0,P1)/Delta`, with numerator degrees at most 15 and 13:

- At a regular point, a rational solution cannot have a pole.
- At a simple discriminant root the residue eigenvalues are 0 and -1/3,
  and the source has at most a double pole, so K has at most a simple pole.
- The gauge `diag(t^-3,t^-1)` has connection O(t^-2) and gauged source
  O(t^-6), bounding the polynomial part at infinity.

The generic-to-specialized exclusion is justified here by a fixed finite
system and full column rank, not by specialization alone. Its coefficients
are regular at `(a,v)=(3,2)` and a 30-by-30 minor is nonzero there. Any generic
solution would be regular at that point by Cramer's rule, contradicting the
independently checked augmented rank 31.

The conclusion is confined to the displayed universal first-jet current with
`K in Q(a,v,t)^2`. It does not exclude arbitrary mixed currents, prove source
exactness, produce a primitive, or solve the target. The base coefficient
calculation does not silently freeze the moving cover root in the physical
current's derivatives.

## Direct physical Laurent search: executed independent certificate

`physical-laurent-01` reconstructs all 535,686 entries of the lead's
762-by-703 augmented matrix from the pinned connection JSON. Its restricted
integer AST evaluator differs from the lead's SymPy polynomial evaluator.
The chart derivatives are explicit:

```
A = r^3 + r^-3 + (vr-1)^6 r^-15
A_r = 3r^2 - 3r^-4 + 6v(vr-1)^5 r^-15 - 15(vr-1)^6 r^-16
A_v = 6(vr-1)^5 r^-14
Nphysical = (A_r M_a, A_v M_a + t M_b, N_t)
target = r^-4 M_b e0 / 12
```

Both compact rows and all six flux components are retained. Every derivative
of a basis monomial is independently computed by lowering its exponent.
All 381 sample domain records agree. Four controls detect an omitted A_v
chain term, missing source factor 1/12, reversed source sign, and a wrong
Laurent derivative sign.

A separate modular Bareiss calculation gives determinant **13884 modulo
32003** for the saved 703-by-703 augmented minor. All arithmetic is integral;
the explicit signed-int64 intermediate bound is 65,548,288,768,016 < 2^63.
Thus the rational augmented sample matrix has rank at least 703, whereas
there are only 702 coefficient columns. This is an exact rational exclusion
of the family in which all six flux components independently span

```
r^m v^n t^k,  m=-10,...,2, n=0,1,2, k=0,1,2.
```

This inference does not require unknown rational solution coefficients to
have denominators prime to 32003: it uses a nonzero minor of the given
rational sample matrix. It does not exclude any larger rational-current
space or provide a primitive.

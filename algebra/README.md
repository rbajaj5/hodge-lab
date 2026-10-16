# The actual holdout: a complete degree-six model and bounded search

This directory works on the fixed `holdout` instance in the pinned `hodge-computer/sextics` submodule. It is not a solution of the instance.

**Frontier update:** fqlx's complete degree-six exclusion has now been reproduced, and our search has moved to degree seven. All 138 single-character degree-seven families are excluded by exact chart certificates in this repository; mixed-character families remain open. See the [degree-seven argument and checks](../notes/degree-seven.md). The degree-six calculations below are retained as earlier experiments and reusable verification machinery.

The cleared certificate equation at `q=1` is

```text
A D^2 - D sum_i N_i F_i
  + F (D sum_i partial_i N_i - sum_i N_i D_i) = F^2 Q.
```

We consider homogeneous `deg D=6`, `deg N_i=7`, and allow an arbitrary quotient of the required degree. A legal denominator must be nonzero and coprime to `F`. Normalizing with the Euler vector field gives

```text
E1: sum_i N_i F_i = A D,
E2: D div(N) - N(D) = 0 modulo F.
```

For completeness of this normalization: reduction of the original equation modulo `F` and coprimality imply `N(F)-AD=F T`. Replacing `N` by `N-(T/6) Euler` enforces E1 and transforms the original equation into E2. Here `deg T=deg D=6`. The allowed quotient is retained by reducing modulo `F`, not by setting the divergence expression to zero.

The exact E1 map has 4,752 numerator columns, rank 4,437, and kernel dimension 315. Its denominator projection has dimension 109. All 315 quadratic-coefficient Koszul fields form the complete correction kernel. These dimensions were already reported by **fqlx** in [Discussion 44](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18980950); this code independently reproduces them and claims no priority.

Removing the denominator's `F` component leaves 108 coordinates. This is a gauge, not an extra ansatz: `D -> D+cF`, `N -> N+c A Euler/6` preserves the normalized problem modulo `F`. Indeed the divergence expression changes by a multiple of `F` when E1 holds. A legal denominator has a nonzero class modulo `F` in this degree. Smoothness of this particular sextic follows from the strict diagonal dominance of its partial derivatives at a coordinate of maximal complex modulus: mixed coefficient sums are `(3,4,1,1,2,1)`, all less than six. Hence its projective hypersurface is smooth and `F` is irreducible.

`degree6_full_e2_model.json.gz` stores all 5,886 quadratic denominator columns and all 34,020 denominator/correction columns. `degree6_verify_all_coefficients.py` independently reconstructs every column from polynomial derivatives and exact division by `F`, checking 283,126 nonzero rational coefficients. It also checks all 109 E1 lifts.

## Search performed

The subsequent [denominator Gram experiment](../notes/denominator-ranking.md) compares geometric rankings across five pools of 768 candidates and exports 254 further distinct fixed-direction rejection certificates. Its check command is `python experiments/denominator_gram_search.py --check`. Lower numerical residuals did not produce an exact solve.

`fixed_denominator_search.py` tests the 108 basis directions and 12 seeded integer combinations of the five retained directions appearing in the basis expansion of `F`. For each fixed denominator, it solves for all 315 correction coefficients over the rationals.

When a candidate fails, the report stores a rational functional `L` with

```text
L(M_column) = 0 for every correction column,
L(b) = 1.
```

Thus `M z + b = 0` is inconsistent even over the complex numbers for that fixed direction. This is stronger than an unsuccessful numerical optimizer. The scan itself excludes only the recorded candidates and their nonzero scalar multiples. The later upstream argument excludes the entire degree-six problem, as documented above. The individual-direction scan is also a reproduction of an approach already discussed upstream.

```sh
python algebra/degree6_e1.py
python algebra/degree6_verify_all_coefficients.py
python algebra/fixed_denominator_search.py --check
```

To regenerate the tensor, run `python algebra/degree6_e2_model.py` after regenerating the E1 basis. Regeneration may change gzip metadata and corresponding hashes; regenerate dependent packets together. Checkers use Python exact rational arithmetic. No Lean proof or challenge acceptance is claimed.

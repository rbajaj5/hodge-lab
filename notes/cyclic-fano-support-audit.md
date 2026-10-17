# Reuse support obstructions before searching higher powers

The earlier degree-twelve `S2` search timed out. **Its support is now excluded by a theorem-based deduction from the already checked degree-six `S` obstruction.** This closes the last unresolved entry in that particular list of 26 products. It does not supply a new degree-twelve dual, finish the timed-out calculation, or solve cyclic-triple-fano.

The useful idea comes from [fqlx / Ben Burns's discussion of reduced pole support](https://github.com/hodge-computer/sextics/discussions/44#discussioncomment-18989248) and the repository's [prescribed-support theorem, pinned source](https://github.com/hodge-computer/sextics/blob/d96911d725077e66a8f10848908be01a643b1714/docs/01-certificates.md#prescribed-support-and-pole-multiplicity). The theorem transfers to our target; holdout's degree-seven lower bound does not.

![Support and multiplicity audit of the actual tested products](../results/cyclic-fano-support-audit-figures/cyclic-fano-support-audit.png)

## The deduction at q = 1

Keep the protected sextic, numerator and `q=1` fixed. Let `D` be one of our nonzero homogeneous denominators, coprime to `F`. Applying the cited theorem upstairs, in the original six variables, gives this implication:

1. If a certificate has poles confined to `V(D)`, a certificate exists over its squarefree equation `D_red`.
2. Multiplying that numerator by `D/D_red` gives a certificate over `D`.
3. Therefore a complete fixed-`D` obstruction rules out every certificate whose poles are confined to that support, including every positive power of `D`.

The second step also follows directly from the normalized equations. Writing `D = h D_red` and `N = h N_red`, differentiation gives

$$
N(F)=hN_{\mathrm{red}}(F),\qquad
B_{hD_{\mathrm{red}}}(hN_{\mathrm{red}})
=h^2B_{D_{\mathrm{red}}}(N_{\mathrm{red}}).
$$

Thus a nonzero quotient remains allowed. We do not need to factor the denominator computationally to use this existence implication. A smaller pole support is covered too. The theorem includes arbitrary homogeneous denominators when no field-parity restriction is imposed; that clause is needed for these coupled cyclic-Fano candidates. Its hypotheses hold upstairs: the sextic is smooth by its Fermat reduction modulo five, the target has the prescribed degree, and the fixed-denominator checks established admissibility. We are applying a mathematical theorem documented by the project, not claiming to have formalized its mixed-Hodge-module proof in our Python checker.

## What changes in our experiment record

The [guided tests](cyclic-fano-guided-denominators.md) completely excluded the sextic

$$S=C^2+\gamma L^6.$$

The new audit independently reconstructs and replays its full **1,185-column** system: 1,110 numerator columns and 75 quotient columns. It checks the exact obstruction and two altered-input controls. The saved product is checked coefficientwise to be precisely `S*S`, using two polynomial arithmetic implementations.

Consequently `S2` is excluded by the support theorem. Its original **120.0556-second timeout** is retained unchanged, and no statement is made about whether a direct first-equation calculation for `S2` would succeed or fail. The old computational total remains **25 direct exclusions and one timeout**; the current theorem-assisted coverage is **26 of those 26 specified products**.

The same deduction applies to all powers of every previously excluded fixed denominator. It also strengthens the [constant-polar family result](cyclic-fano-polar-family.md): for each fixed nonzero constant vector `v`, every power of `E_v = partial_v Delta` is excluded. No uniform bound on the degree of an unknown successful support follows.

This corrects the earlier conservative wording that higher powers remained open. The failed runs, their timing and their original exact packets remain part of the record. Their repetition taught us about the correction maps, but the theorem now makes further tests of those same supports unnecessary.

## What the picture and bookkeeping establish

The audit reads the actual 26 exponent vectors in the generators `T,C,S,R,J`. It checks each saved polynomial and binds the prior witnesses by normalized source hashes. Their 16 formal factor sets are a bookkeeping device, **not 16 proved distinct geometric supports**: the generators need not be irreducible or independent, and `R` already has a factor proportional to `T`.

For nonnegative exponent vectors `a,b`, the checker can certify support containment by finding an integer `k` with `a <= k*b` coordinatewise. The resulting identity is an exact divisibility witness. Controls reject attempts to infer coverage after adding an uncovered factor.

In particular, separate failures on `D1` and `D2` do not rule out `D1*D2`. Their union may support a class neither carries alone. Products adding support components, polynomial-direction polars, and other new geometric constructions need their own complete equations. Our next degree-six linear-direction polar calculation changes the support and retains the additional Koszul corrections that appear at that degree.

## Reproduce and distinguish the evidence

```sh
python -S experiments/cyclic_fano_support_audit.py run
python -S experiments/cyclic_fano_support_audit.py verify
python experiments/plot_cyclic_fano_support_audit.py
```

The [packet](../results/cyclic-fano-support-audit/packet.json) records the theorem dependency, source bindings, fresh `S` replay, exact product identity, all 26 candidate bindings, containment witnesses and the historical timeout. It binds the other 25 saved exclusion witnesses; their full arithmetic replay remains documented in the unchanged [product validation](../results/cyclic-fano-branch-products/independent-validation.json). Reading those receipts is not reported as executing those 25 proofs again.

Credit: the repository authors' prescribed-support theorem and its cited Hodge-filtration inputs; Ben Burns (`fqlx`) for emphasizing reduced support in the discussion; the earlier exact cyclic character/Piola and Koszul calculations. OpenAI Codex assisted this audit and its separate review. No upstream comment accompanies this notebook batch, and no Lean proof or accepted solution is claimed.

import Mathlib.LinearAlgebra.FiniteDimensional.Basic

/-!
# The rank-gap implication used by the cubic-polar experiment

This file proves a generic implication between dimensions and span membership.
It does not encode the experiment's matrices, modular minors, or certificate
equations. The two dimension inequalities are explicit hypotheses.
-/

namespace HodgeLab

variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]

/-- Adding a vector already in the correction span cannot increase its dimension.
Thus an augmented dimension at least `n + 1`, together with correction dimension
at most `n`, excludes that vector from the correction span. -/
theorem not_mem_of_finrank_gap (corrections : Set V) (target : V) (n : ℕ)
    (upper : Module.finrank K (Submodule.span K corrections) ≤ n)
    (lower : n + 1 ≤ Module.finrank K (Submodule.span K (insert target corrections))) :
    target ∉ Submodule.span K corrections := by
  intro member
  have sameSpan : Submodule.span K (insert target corrections) =
      Submodule.span K corrections := Submodule.span_insert_eq_span member
  rw [sameSpan] at lower
  exact (Nat.not_succ_le_self n) (le_trans lower upper)

/-- The numerical bounds used in the current cubic-polar rank certificates. -/
theorem not_mem_of_finrank_150_151 (corrections : Set V) (target : V)
    (upper : Module.finrank K (Submodule.span K corrections) ≤ 150)
    (lower : 151 ≤ Module.finrank K (Submodule.span K (insert target corrections))) :
    target ∉ Submodule.span K corrections :=
  not_mem_of_finrank_gap corrections target 150 upper lower

/-- If each proposed corrected target belongs to the correction span, the same
rank gap rules out equality with any of them. This is the linear-system form of
the obstruction, with no assumption about independence of the generators. -/
theorem no_correction_solution_of_finrank_gap {I : Type*}
    (corrections : Set V) (candidate : I → V) (target : V) (n : ℕ)
    (candidate_mem : ∀ i, candidate i ∈ Submodule.span K corrections)
    (upper : Module.finrank K (Submodule.span K corrections) ≤ n)
    (lower : n + 1 ≤ Module.finrank K (Submodule.span K (insert target corrections))) :
    ¬ ∃ i, candidate i = target := by
  rintro ⟨i, equality⟩
  apply not_mem_of_finrank_gap corrections target n upper lower
  rw [← equality]
  exact candidate_mem i

end HodgeLab

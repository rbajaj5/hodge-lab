import HodgeLab.OneReflectionSkew.ThreeCoefficient
import Mathlib.Algebra.MvPolynomial.Degrees
import Lean.Elab.Tactic.Omega
import Mathlib.Tactic.Ring

/-! Completeness of the encoded numerator space for the degree-four chart ansatz.
The fifth variable is absent explicitly; the source-to-chart transport is separate. -/

open scoped BigOperators
namespace HodgeLab.OneReflectionSkew
open HodgeLab.SparsePolynomial

set_option maxRecDepth 100000 in
set_option maxHeartbeats 8000000 in
theorem monomial_injective : Function.Injective monomial := by
  decide +kernel

theorem exponent_monomial_injective : Function.Injective (fun k => exponent (monomial k)) := by
  intro i j h
  exact monomial_injective ((exponent_eq _ _).mp h)

theorem support_degree_four_coverage {K : Type*} [CommSemiring K]
    (p : MvPolynomial (Fin 5) K) (degree : p.totalDegree ≤ 4)
    (absent : ∀ d ∈ p.support, d 4 = 0)
    {d : Fin 5 →₀ ℕ} (hd : d ∈ p.support) :
    ∃ k : Fin 70, exponent (monomial k) = d := by
  have hs := (MvPolynomial.le_totalDegree hd).trans degree
  have hz := absent d hd
  have hsum : d 0 + d 1 + d 2 + d 3 ≤ 4 := by
    simpa [Finsupp.sum_fintype, Fin.sum_univ_succ, hz, Nat.add_assoc] using hs
  let u : Fin 5 := ⟨d 0, by omega⟩
  let r : Fin 5 := ⟨d 1, by omega⟩
  let w : Fin 5 := ⟨d 2, by omega⟩
  let t : Fin 5 := ⟨d 3, by omega⟩
  obtain ⟨k, hk⟩ := (monomial_coverage u r w t).mp hsum
  refine ⟨k, ?_⟩
  ext i
  have hi := congrFun hk i
  fin_cases i <;> simpa [exp, u, r, w, t, hz] using hi

/-- Every degree-four polynomial in the four chart variables has exactly the
encoded monomial expansion, with coefficients in an arbitrary semiring. -/
theorem degree_four_expansion {K : Type*} [CommSemiring K]
    (p : MvPolynomial (Fin 5) K) (degree : p.totalDegree ≤ 4)
    (absent : ∀ d ∈ p.support, d 4 = 0) :
    p = ∑ k : Fin 70, MvPolynomial.monomial (exponent (monomial k))
      (MvPolynomial.coeff (exponent (monomial k)) p) := by
  classical
  ext d
  simp only [MvPolynomial.coeff_sum, MvPolynomial.coeff_monomial]
  by_cases h : ∃ k : Fin 70, exponent (monomial k) = d
  · obtain ⟨k, rfl⟩ := h
    rw [Finset.sum_eq_single k]
    · simp
    · intro j hj hne
      simp [show exponent (monomial j) ≠ exponent (monomial k) from
        fun heq => hne (exponent_monomial_injective heq)]
    · simp
  · have hc : MvPolynomial.coeff d p = 0 := by
      by_contra hn
      exact h (support_degree_four_coverage p degree absent
        (MvPolynomial.mem_support_iff.mpr hn))
    rw [hc]
    symm
    apply Finset.sum_eq_zero
    intro k hk
    simp [show exponent (monomial k) ≠ d from fun heq => h ⟨k, heq⟩]

noncomputable def basisOver (K : Type*) [CommSemiring K] (k : Fin 70) :
    MvPolynomial (Fin 5) K := MvPolynomial.monomial (exponent (monomial k)) 1

noncomputable def aOver (K : Type*) [Field K] [CharZero K] : MvPolynomial (Fin 5) K :=
  MvPolynomial.map (Rat.castHom K) a

noncomputable def p7Over (K : Type*) [Field K] [CharZero K] : MvPolynomial (Fin 5) K :=
  MvPolynomial.map (Rat.castHom K) p7

/-- The full first-order operator on one arbitrary numerator component. -/
noncomputable def componentOperator (K : Type*) [Field K] [CharZero K]
    (i : Fin 4) (p : MvPolynomial (Fin 5) K) : MvPolynomial (Fin 5) K :=
  MvPolynomial.C 60 * ((aOver K * MvPolynomial.pderiv (direction (i,0)) (p7Over K)) * p) +
  MvPolynomial.C (-72) * ((p7Over K * aOver K) * MvPolynomial.pderiv (direction (i,0)) p) +
  MvPolynomial.C 72 * ((p7Over K * p) * MvPolynomial.pderiv (direction (i,0)) (aOver K))

theorem componentOperator_basis (K : Type*) [Field K] [CharZero K]
    (i : Fin 4) (k : Fin 70) :
    componentOperator K i (basisOver K k) = columnOver K (i,k) := by
  simp [componentOperator, columnOver, column_formula, aOver, p7Over,
    basisOver, basisSparse, eval, MvPolynomial.pderiv_map, direction]

theorem componentOperator_C_mul (K : Type*) [Field K] [CharZero K]
    (i : Fin 4) (c : K) (p : MvPolynomial (Fin 5) K) :
    componentOperator K i (MvPolynomial.C c * p) =
      MvPolynomial.C c * componentOperator K i p := by
  simp only [componentOperator, MvPolynomial.pderiv_C_mul]
  ring

theorem componentOperator_sum (K : Type*) [Field K] [CharZero K]
    {I : Type*} (s : Finset I) (i : Fin 4) (f : I → MvPolynomial (Fin 5) K) :
    componentOperator K i (∑ k ∈ s, f k) = ∑ k ∈ s, componentOperator K i (f k) := by
  simp [componentOperator, map_sum, Finset.mul_sum, Finset.sum_mul, Finset.sum_add_distrib]

theorem componentOperator_degree_four (K : Type*) [Field K] [CharZero K]
    (i : Fin 4) (p : MvPolynomial (Fin 5) K) (degree : p.totalDegree ≤ 4)
    (absent : ∀ d ∈ p.support, d 4 = 0) :
    componentOperator K i p = ∑ k : Fin 70,
      MvPolynomial.C (MvPolynomial.coeff (exponent (monomial k)) p) * columnOver K (i,k) := by
  conv_lhs => rw [degree_four_expansion p degree absent]
  rw [componentOperator_sum]
  apply Finset.sum_congr rfl
  intro k hk
  have hm : MvPolynomial.monomial (exponent (monomial k))
      (MvPolynomial.coeff (exponent (monomial k)) p) =
      MvPolynomial.C (MvPolynomial.coeff (exponent (monomial k)) p) * basisOver K k := by
    simp [basisOver, MvPolynomial.C_mul_monomial]
  rw [hm, componentOperator_C_mul, componentOperator_basis]

/-- The chart differential equation for four arbitrary numerator polynomials. -/
noncomputable def fullOperator (K : Type*) [Field K] [CharZero K]
    (N : Fin 4 → MvPolynomial (Fin 5) K) : MvPolynomial (Fin 5) K :=
  ∑ i, componentOperator K i (N i)

theorem fullOperator_degree_four (K : Type*) [Field K] [CharZero K]
    (N : Fin 4 → MvPolynomial (Fin 5) K)
    (degree : ∀ i, (N i).totalDegree ≤ 4)
    (absent : ∀ i d, d ∈ (N i).support → d 4 = 0) :
    fullOperator K N = ∑ j : Column,
      MvPolynomial.C (MvPolynomial.coeff (exponent (monomial j.2)) (N j.1)) * columnOver K j := by
  simp only [fullOperator, Fintype.sum_prod_type]
  apply Finset.sum_congr rfl
  intro i hi
  exact componentOperator_degree_four K i (N i) (degree i) (absent i)

/-- The bounded exclusion now accepts arbitrary degree-four polynomials, not
only an input already presented as coefficients of the encoded columns. -/
theorem no_degree_four_solution (K : Type*) [Field K] [CharZero K] :
    ¬ ∃ N : Fin 4 → MvPolynomial (Fin 5) K,
      (∀ i, (N i).totalDegree ≤ 4) ∧
      (∀ i d, d ∈ (N i).support → d 4 = 0) ∧
      fullOperator K N = rhsOver K := by
  rintro ⟨N, degree, absent, equation⟩
  apply no_polynomial_solution K
  refine ⟨fun j => MvPolynomial.coeff (exponent (monomial j.2)) (N j.1), ?_⟩
  rw [← fullOperator_degree_four K N degree absent]
  exact equation

end HodgeLab.OneReflectionSkew

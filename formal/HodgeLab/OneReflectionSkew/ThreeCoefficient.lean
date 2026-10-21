import HodgeLab.SparsePolynomial
import HodgeLab.RowCertificate
import Mathlib.Data.Fin.VecNotation

/-!
# Three coefficients obstruct the degree-four chart ansatz

The first four variables are U,r,w,t; the unused fifth coordinate is zero
in every exponent. The encoded space consists of four components, each
with the 70 monomials of total degree at most four. This formalizes the
chart polynomial operator, not the geometric source transport.
-/

open scoped BigOperators
namespace HodgeLab.OneReflectionSkew
open HodgeLab.SparsePolynomial

def exp (u r w t : ℕ) : Exponent := ![u,r,w,t,0]
def monomials : List Exponent := [exp 0 0 0 0,
    exp 0 0 0 1,
    exp 0 0 0 2,
    exp 0 0 0 3,
    exp 0 0 0 4,
    exp 0 0 1 0,
    exp 0 0 1 1,
    exp 0 0 1 2,
    exp 0 0 1 3,
    exp 0 0 2 0,
    exp 0 0 2 1,
    exp 0 0 2 2,
    exp 0 0 3 0,
    exp 0 0 3 1,
    exp 0 0 4 0,
    exp 0 1 0 0,
    exp 0 1 0 1,
    exp 0 1 0 2,
    exp 0 1 0 3,
    exp 0 1 1 0,
    exp 0 1 1 1,
    exp 0 1 1 2,
    exp 0 1 2 0,
    exp 0 1 2 1,
    exp 0 1 3 0,
    exp 0 2 0 0,
    exp 0 2 0 1,
    exp 0 2 0 2,
    exp 0 2 1 0,
    exp 0 2 1 1,
    exp 0 2 2 0,
    exp 0 3 0 0,
    exp 0 3 0 1,
    exp 0 3 1 0,
    exp 0 4 0 0,
    exp 1 0 0 0,
    exp 1 0 0 1,
    exp 1 0 0 2,
    exp 1 0 0 3,
    exp 1 0 1 0,
    exp 1 0 1 1,
    exp 1 0 1 2,
    exp 1 0 2 0,
    exp 1 0 2 1,
    exp 1 0 3 0,
    exp 1 1 0 0,
    exp 1 1 0 1,
    exp 1 1 0 2,
    exp 1 1 1 0,
    exp 1 1 1 1,
    exp 1 1 2 0,
    exp 1 2 0 0,
    exp 1 2 0 1,
    exp 1 2 1 0,
    exp 1 3 0 0,
    exp 2 0 0 0,
    exp 2 0 0 1,
    exp 2 0 0 2,
    exp 2 0 1 0,
    exp 2 0 1 1,
    exp 2 0 2 0,
    exp 2 1 0 0,
    exp 2 1 0 1,
    exp 2 1 1 0,
    exp 2 2 0 0,
    exp 3 0 0 0,
    exp 3 0 0 1,
    exp 3 0 1 0,
    exp 3 1 0 0,
    exp 4 0 0 0]
theorem monomials_length : monomials.length = 70 := by decide +kernel
def monomial (k : Fin 70) : Exponent :=
  monomials[k.val]'(by simpa [monomials_length] using k.isLt)

set_option maxRecDepth 100000 in
set_option maxHeartbeats 4000000 in
/-- A finite completeness check, including the degree and unused-coordinate conventions. -/
theorem monomial_coverage : ∀ u r w t : Fin 5,
    u.val + r.val + w.val + t.val ≤ 4 ↔
      ∃ k : Fin 70, monomial k = exp u.val r.val w.val t.val := by
  decide +kernel

def aSparse : Sparse := [(exp 0 0 0 0,1),(exp 0 6 0 0,1),(exp 0 0 6 0,1)]
def p7Sparse : Sparse := [
  (exp 3 0 0 0,7),(exp 3 6 0 0,7),(exp 3 0 6 0,7),
  (exp 2 1 0 1,7),(exp 2 3 1 1,7),
  (exp 1 1 0 1,1),(exp 1 1 0 3,-1),
  (exp 0 0 0 0,7),(exp 0 0 0 6,7)]

abbrev Column := Fin 4 × Fin 70
def direction (j : Column) : Fin 5 := ⟨j.1.val, Nat.lt_trans j.1.isLt (by decide)⟩
def basisSparse (j : Column) : Sparse := [(monomial j.2,1)]

/-- Full column, retaining the derivative of the denominator a. -/
def columnSparse (j : Column) : Sparse :=
  scale 60 (multiply (multiply aSparse (derivative (direction j) p7Sparse)) (basisSparse j)) ++
  scale (-72) (multiply (multiply p7Sparse aSparse) (derivative (direction j) (basisSparse j))) ++
  scale 72 (multiply (multiply p7Sparse (basisSparse j)) (derivative (direction j) aSparse))
def rhsSparse : Sparse := scale 35 (multiply [(exp 2 0 0 0,1)] (multiply aSparse aSparse))
noncomputable def a : MvPolynomial (Fin 5) ℚ := eval aSparse
noncomputable def p7 : MvPolynomial (Fin 5) ℚ := eval p7Sparse
noncomputable def column (j : Column) : MvPolynomial (Fin 5) ℚ := eval (columnSparse j)
noncomputable def rhs : MvPolynomial (Fin 5) ℚ := eval rhsSparse

theorem column_formula (j : Column) : column j =
    MvPolynomial.C 60 * ((a * MvPolynomial.pderiv (direction j) p7) * eval (basisSparse j)) +
    MvPolynomial.C (-72) * ((p7 * a) * MvPolynomial.pderiv (direction j) (eval (basisSparse j))) +
    MvPolynomial.C 72 * ((p7 * eval (basisSparse j)) * MvPolynomial.pderiv (direction j) a) := by
  simp [column, columnSparse, a, p7, add_assoc]

theorem rhs_formula : rhs = MvPolynomial.C 35 * (eval [(exp 2 0 0 0,1)] * (a * a)) := by
  simp [rhs, rhsSparse, a]

def rowExponent (r : Fin 3) : Exponent :=
  ![exp 0 1 0 3,exp 2 0 12 0,exp 2 0 12 2] r
def matrix (r : Fin 3) (j : Column) : ℤ :=
  if j.1 = 0 ∧ monomial j.2 = exp 0 0 0 0 then ![-60,1260,0] r
  else if j.1 = 0 ∧ monomial j.2 = exp 0 0 0 2 then ![60,0,1260] r
  else 0
def target : Fin 3 → ℤ := ![0,35,0]
def dual : Fin 3 → ℤ := ![21,1,-1]

set_option maxRecDepth 100000 in
set_option maxHeartbeats 8000000 in
theorem computed_columns : ∀ r : Fin 3, ∀ j : Column,
    coefficient (rowExponent r) (columnSparse j) = (matrix r j : ℚ) := by
  intro r ⟨i,k⟩
  fin_cases r <;> fin_cases i <;> fin_cases k <;> decide +kernel

set_option maxRecDepth 100000 in
theorem computed_target : ∀ r : Fin 3,
    coefficient (rowExponent r) rhsSparse = (target r : ℚ) := by
  intro r; fin_cases r <;> decide +kernel

theorem annihilates : ∀ j : Column, ∑ r, dual r * matrix r j = 0 := by
  intro j
  simp only [matrix]
  split_ifs <;> decide +kernel

theorem separates : ∑ r, dual r * target r ≠ 0 := by decide +kernel

theorem no_matrix_solution (K : Type*) [Field K] [CharZero K] :
    ¬ ∃ c : Column → K, ∀ r, ∑ j, (matrix r j : K) * c j = (target r : K) :=
  HodgeLab.no_solution_of_integer_row_certificate matrix target dual annihilates separates

theorem column_coefficients (r : Fin 3) (j : Column) :
    MvPolynomial.coeff (exponent (rowExponent r)) (column j) = (matrix r j : ℚ) := by
  exact (coefficient_eval (rowExponent r) (columnSparse j)).trans (computed_columns r j)

theorem target_coefficients (r : Fin 3) :
    MvPolynomial.coeff (exponent (rowExponent r)) rhs = (target r : ℚ) := by
  exact (coefficient_eval (rowExponent r) rhsSparse).trans (computed_target r)

noncomputable def columnOver (K : Type*) [Field K] [CharZero K] (j : Column) :
    MvPolynomial (Fin 5) K := MvPolynomial.map (Rat.castHom K) (column j)
noncomputable def rhsOver (K : Type*) [Field K] [CharZero K] :
    MvPolynomial (Fin 5) K := MvPolynomial.map (Rat.castHom K) rhs

theorem column_coefficients_over (K : Type*) [Field K] [CharZero K]
    (r : Fin 3) (j : Column) :
    MvPolynomial.coeff (exponent (rowExponent r)) (columnOver K j) = (matrix r j : K) := by
  have h := congrArg (Rat.castHom K) (column_coefficients r j)
  simpa [columnOver, MvPolynomial.coeff_map] using h

theorem target_coefficients_over (K : Type*) [Field K] [CharZero K] (r : Fin 3) :
    MvPolynomial.coeff (exponent (rowExponent r)) (rhsOver K) = (target r : K) := by
  have h := congrArg (Rat.castHom K) (target_coefficients r)
  simpa [rhsOver, MvPolynomial.coeff_map] using h

theorem polynomial_equation_implies_matrix (K : Type*) [Field K] [CharZero K]
    (c : Column → K) (equation : ∑ j, MvPolynomial.C (c j) * columnOver K j = rhsOver K) :
    ∀ r, ∑ j, (matrix r j : K) * c j = (target r : K) := by
  intro r
  have h := congrArg (MvPolynomial.coeff (exponent (rowExponent r))) equation
  have h' : ∑ j, c j * (matrix r j : K) = (target r : K) := by
    simpa only [MvPolynomial.coeff_sum, MvPolynomial.coeff_C_mul,
      column_coefficients_over, target_coefficients_over] using h
  simpa only [mul_comm] using h'

/-- No constant-coefficient combination of the 280 encoded polynomial columns solves the source. -/
theorem no_polynomial_solution (K : Type*) [Field K] [CharZero K] :
    ¬ ∃ c : Column → K, ∑ j, MvPolynomial.C (c j) * columnOver K j = rhsOver K := by
  rintro ⟨c, equation⟩
  exact no_matrix_solution K ⟨c, polynomial_equation_implies_matrix K c equation⟩

end HodgeLab.OneReflectionSkew

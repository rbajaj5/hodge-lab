import HodgeLab.RowCertificate
import Mathlib.Data.Fintype.BigOperators
import Mathlib.Tactic.FinCases

/-!
Exact integer selected-row data for cyclic-Fano fixed case 08.
All 175 columns are included; unspecified entries are zero.
The correspondence to the polynomial coefficient rows is checked separately.
-/

open scoped BigOperators

namespace HodgeLab.CyclicFano.Case08

def matrix (row : Fin 2) (column : Fin 175) : ℤ :=
  match row.val, column.val with
  | 0, 84 => -1
  | 1, 84 => 405
  | _, _ => 0

def target (row : Fin 2) : ℤ :=
  match row.val with
  | 0 => 0
  | 1 => -196
  | _ => 0

def dual (row : Fin 2) : ℤ :=
  match row.val with
  | 0 => 405
  | 1 => 1
  | _ => 0

set_option maxRecDepth 100000 in
set_option maxHeartbeats 2000000 in
theorem annihilates : ∀ column : Fin 175,
    ∑ row, dual row * matrix row column = 0 := by
  intro column
  fin_cases column <;> decide

set_option maxRecDepth 100000 in
set_option maxHeartbeats 2000000 in
theorem separates : ∑ row, dual row * target row ≠ 0 := by decide

/-- Inconsistency of the actual encoded integer rows over every
characteristic-zero field. Source-coefficient identification is external. -/
theorem no_solution {K : Type*} [Field K] [CharZero K] :
    ¬ ∃ coefficients : Fin 175 → K,
      ∀ row : Fin 2, ∑ column, (matrix row column : K) * coefficients column =
        (target row : K) :=
  HodgeLab.no_solution_of_integer_row_certificate matrix target dual annihilates separates

end HodgeLab.CyclicFano.Case08

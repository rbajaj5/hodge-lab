import HodgeLab.RowCertificate
import Mathlib.Data.Fintype.BigOperators
import Mathlib.Tactic.FinCases

/-!
Exact integer selected-row data for cyclic-Fano fixed case 15.
All 175 columns are included; unspecified entries are zero.
The correspondence to the polynomial coefficient rows is checked separately.
-/

open scoped BigOperators

namespace HodgeLab.CyclicFano.Case15

def matrix (row : Fin 16) (column : Fin 175) : ℤ :=
  match row.val, column.val with
  | 0, 68 => -180
  | 0, 74 => -90
  | 0, 96 => -90
  | 0, 99 => 180
  | 0, 164 => -60
  | 0, 172 => -30
  | 1, 86 => 25
  | 1, 89 => -25
  | 1, 95 => -2940
  | 1, 96 => 5880
  | 1, 99 => -2940
  | 1, 171 => -980
  | 1, 172 => 1960
  | 2, 65 => -17640
  | 2, 68 => -8820
  | 2, 74 => -8820
  | 2, 84 => 75
  | 2, 86 => -75
  | 2, 89 => 75
  | 2, 161 => -5880
  | 2, 164 => -2940
  | 3, 83 => 15
  | 3, 89 => 15
  | 3, 95 => 3528
  | 3, 96 => -1764
  | 3, 99 => -3528
  | 3, 169 => 5
  | 3, 171 => 1176
  | 3, 172 => -588
  | 4, 81 => 75
  | 4, 83 => -75
  | 4, 86 => 75
  | 4, 89 => 150
  | 4, 167 => 25
  | 4, 169 => -25
  | 5, 65 => -8820
  | 5, 68 => -8820
  | 5, 74 => -8820
  | 5, 81 => -75
  | 5, 83 => 75
  | 5, 84 => 75
  | 5, 86 => 150
  | 5, 89 => 150
  | 5, 161 => -2940
  | 5, 164 => -2940
  | 5, 167 => -25
  | 5, 169 => 25
  | 6, 5 => 81
  | 6, 8 => -282
  | 6, 14 => -141
  | 6, 68 => 45
  | 6, 74 => 30
  | 6, 80 => 252
  | 6, 83 => -252
  | 6, 89 => -126
  | 6, 151 => -27
  | 6, 154 => 94
  | 6, 164 => 15
  | 6, 166 => 84
  | 6, 169 => -84
  | 7, 95 => -3
  | 7, 96 => -6
  | 7, 171 => -1
  | 7, 172 => -2
  | 8, 5 => 69
  | 8, 8 => 72
  | 8, 14 => 15
  | 8, 65 => 15
  | 8, 68 => 15
  | 8, 74 => -30
  | 8, 83 => 45
  | 8, 89 => 30
  | 8, 151 => -23
  | 8, 154 => -24
  | 8, 161 => 5
  | 8, 164 => 5
  | 8, 169 => 15
  | 9, 80 => 3
  | 9, 83 => 3
  | 9, 89 => -6
  | 9, 166 => 1
  | 9, 169 => 1
  | 10, 80 => -75
  | 10, 81 => 75
  | 10, 83 => 150
  | 10, 86 => -150
  | 10, 89 => -150
  | 10, 166 => -25
  | 10, 167 => 25
  | 10, 169 => 50
  | 11, 65 => -8820
  | 11, 68 => -8820
  | 11, 80 => 75
  | 11, 81 => 150
  | 11, 83 => 150
  | 11, 84 => -150
  | 11, 86 => -150
  | 11, 161 => -2940
  | 11, 164 => -2940
  | 11, 166 => 25
  | 11, 167 => 50
  | 11, 169 => 50
  | 12, 5 => 72
  | 12, 8 => 57
  | 12, 65 => -69
  | 12, 68 => -72
  | 12, 74 => -15
  | 12, 80 => -81
  | 12, 83 => 282
  | 12, 89 => 141
  | 12, 151 => -24
  | 12, 154 => -19
  | 12, 161 => -23
  | 12, 164 => -24
  | 12, 166 => -27
  | 12, 169 => 94
  | 13, 5 => -84
  | 13, 8 => -42
  | 13, 80 => -69
  | 13, 83 => -72
  | 13, 89 => -15
  | 13, 151 => 28
  | 13, 154 => 14
  | 13, 166 => -23
  | 13, 169 => -24
  | 14, 84 => 210
  | 14, 86 => 420
  | 14, 89 => 420
  | 15, 65 => 84
  | 15, 68 => 42
  | 15, 80 => -72
  | 15, 83 => -57
  | 15, 161 => 28
  | 15, 164 => 14
  | 15, 166 => -24
  | 15, 169 => -19
  | _, _ => 0

def target (row : Fin 16) : ℤ :=
  match row.val with
  | 0 => -1
  | 1 => 196
  | 2 => -392
  | 3 => 0
  | 4 => -294
  | 5 => 588
  | 6 => 0
  | 7 => 0
  | 8 => 0
  | 9 => 0
  | 10 => -686
  | 11 => 98
  | 12 => 0
  | 13 => 0
  | 14 => -1957
  | 15 => 0
  | _ => 0

def dual (row : Fin 16) : ℤ :=
  match row.val with
  | 0 => 475282433905916
  | 1 => 13430272857624
  | 2 => 9915018310274
  | 3 => 13057209722690
  | 4 => 8879211079998
  | 5 => -14580762445116
  | 6 => -7041443913000
  | 7 => 2193611233411920
  | 8 => -66189572782200
  | 9 => 337036034050800
  | 10 => -13283019918910
  | 11 => -5088476803102
  | 12 => 10059205590000
  | 13 => -52537793767200
  | 14 => -1968289096915
  | 15 => 36966209540400
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
      ∀ row : Fin 16, ∑ column, (matrix row column : K) * coefficients column =
        (target row : K) :=
  HodgeLab.no_solution_of_integer_row_certificate matrix target dual annihilates separates

end HodgeLab.CyclicFano.Case15

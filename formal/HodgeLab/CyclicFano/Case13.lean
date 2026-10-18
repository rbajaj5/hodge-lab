import HodgeLab.RowCertificate
import Mathlib.Data.Fintype.BigOperators
import Mathlib.Tactic.FinCases

/-!
Exact integer selected-row data for cyclic-Fano fixed case 13.
All 175 columns are included; unspecified entries are zero.
The correspondence to the polynomial coefficient rows is checked separately.
-/

open scoped BigOperators

namespace HodgeLab.CyclicFano.Case13

def matrix (row : Fin 16) (column : Fin 175) : ℤ :=
  match row.val, column.val with
  | 0, 68 => 180
  | 0, 74 => -180
  | 0, 96 => -180
  | 0, 99 => -90
  | 0, 164 => 60
  | 0, 172 => -60
  | 1, 86 => -75
  | 1, 89 => -75
  | 1, 95 => -8820
  | 1, 96 => -4410
  | 1, 99 => 8820
  | 1, 171 => -2940
  | 1, 172 => -1470
  | 2, 65 => 17640
  | 2, 68 => -17640
  | 2, 74 => 8820
  | 2, 84 => -150
  | 2, 86 => -150
  | 2, 89 => -75
  | 2, 161 => 5880
  | 2, 164 => -5880
  | 3, 83 => -15
  | 3, 89 => -15
  | 3, 95 => -882
  | 3, 96 => 1764
  | 3, 99 => -882
  | 3, 169 => -5
  | 3, 171 => -294
  | 3, 172 => 588
  | 4, 81 => -150
  | 4, 83 => -150
  | 4, 86 => -150
  | 4, 89 => -75
  | 4, 167 => -50
  | 4, 169 => -50
  | 5, 65 => -3528
  | 5, 68 => 1764
  | 5, 74 => 1764
  | 5, 81 => -30
  | 5, 83 => -15
  | 5, 84 => -30
  | 5, 86 => -15
  | 5, 89 => -30
  | 5, 161 => -1176
  | 5, 164 => 588
  | 5, 167 => -10
  | 5, 169 => -5
  | 6, 5 => -312
  | 6, 8 => -96
  | 6, 14 => 141
  | 6, 68 => 60
  | 6, 74 => -30
  | 6, 80 => -252
  | 6, 83 => -252
  | 6, 89 => 126
  | 6, 151 => 104
  | 6, 154 => 32
  | 6, 164 => 20
  | 6, 166 => -84
  | 6, 169 => -84
  | 7, 95 => 6
  | 7, 96 => -3
  | 7, 171 => 2
  | 7, 172 => -1
  | 8, 5 => 114
  | 8, 8 => -27
  | 8, 14 => -15
  | 8, 65 => -30
  | 8, 68 => -30
  | 8, 74 => -15
  | 8, 83 => 60
  | 8, 89 => -30
  | 8, 151 => -38
  | 8, 154 => 9
  | 8, 161 => -10
  | 8, 164 => -10
  | 8, 169 => 20
  | 9, 80 => -6
  | 9, 83 => -6
  | 9, 89 => -3
  | 9, 166 => -2
  | 9, 169 => -2
  | 10, 80 => -150
  | 10, 81 => -150
  | 10, 83 => -75
  | 10, 86 => -75
  | 10, 89 => 150
  | 10, 166 => -50
  | 10, 167 => -50
  | 10, 169 => -25
  | 11, 65 => 8820
  | 11, 68 => 8820
  | 11, 80 => -75
  | 11, 81 => -75
  | 11, 83 => -150
  | 11, 84 => -75
  | 11, 86 => 150
  | 11, 161 => 2940
  | 11, 164 => 2940
  | 11, 166 => -25
  | 11, 167 => -25
  | 11, 169 => -50
  | 12, 5 => -27
  | 12, 8 => -57
  | 12, 65 => -114
  | 12, 68 => 27
  | 12, 74 => 15
  | 12, 80 => 312
  | 12, 83 => 96
  | 12, 89 => -141
  | 12, 151 => 9
  | 12, 154 => 19
  | 12, 161 => -38
  | 12, 164 => 9
  | 12, 166 => 104
  | 12, 169 => 32
  | 13, 5 => -42
  | 13, 8 => 42
  | 13, 80 => -114
  | 13, 83 => 27
  | 13, 89 => 15
  | 13, 151 => 14
  | 13, 154 => -14
  | 13, 166 => -38
  | 13, 169 => 9
  | 14, 84 => -15
  | 14, 86 => 15
  | 14, 89 => 15
  | 15, 65 => 42
  | 15, 68 => -42
  | 15, 80 => 27
  | 15, 83 => 57
  | 15, 161 => 14
  | 15, 164 => -14
  | 15, 166 => 9
  | 15, 169 => 19
  | _, _ => 0

def target (row : Fin 16) : ℤ :=
  match row.val with
  | 0 => 1
  | 1 => 392
  | 2 => -196
  | 3 => 0
  | 4 => 882
  | 5 => -98
  | 6 => 0
  | 7 => 0
  | 8 => 0
  | 9 => 0
  | 10 => 588
  | 11 => -294
  | 12 => 0
  | 13 => 0
  | 14 => 1
  | 15 => 0
  | _ => 0

def dual (row : Fin 16) : ℤ :=
  match row.val with
  | 0 => 6496721743568
  | 1 => 464051553112
  | 2 => 34344998004
  | 3 => 3977584740960
  | 4 => -857623117057
  | 5 => 462278992890
  | 6 => -521633028000
  | 7 => 1266860739995760
  | 8 => -4903350463200
  | 9 => 126505182448475
  | 10 => 788927310070
  | 11 => -47519983182
  | 12 => -2544823986600
  | 13 => -7798147629300
  | 14 => -1030408049910
  | 15 => 23975960129100
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

end HodgeLab.CyclicFano.Case13

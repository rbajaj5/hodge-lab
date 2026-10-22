import Mathlib.Data.Fin.VecNotation
import Mathlib.Tactic.Ring
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.FinCases
import Mathlib.Data.Fintype.Fin
import Mathlib.Tactic.LinearCombination

/-! Exact target comparison. Definitions below are generated from pinned protected
record.json terms in (X0,X1,X2,Y0,Y1,Y2) order; the Python runner checks the binding.
No source-transport or hypersurface correspondence theorem is asserted here. -/
namespace HodgeLab.OneReflectionSkew.CoordinateComparison
variable {K : Type*} [Field K]

def skewF (p : Fin 6 → K) : K :=
  (1 : K) * p 0 ^ 6 +
  (1 : K) * p 0 ^ 3 * p 1 * p 3 * p 4 +
  ((1 : K) / 7) * p 0 * p 1 * p 3 ^ 3 * p 4 +
  ((-1 : K) / 7) * p 0 * p 1 * p 3 * p 4 ^ 3 +
  (1 : K) * p 1 ^ 6 +
  (1 : K) * p 1 ^ 3 * p 2 * p 3 * p 4 +
  (1 : K) * p 2 ^ 6 +
  (1 : K) * p 3 ^ 6 +
  (1 : K) * p 4 ^ 6 +
  (1 : K) * p 5 ^ 6

def skewA (p : Fin 6 → K) : K :=
  (1 : K) * p 0 ^ 3 * p 3 ^ 3

def mixedF (p : Fin 6 → K) : K :=
  (1 : K) * p 0 ^ 6 +
  ((1 : K) / 2) * p 0 ^ 3 * p 1 * p 3 * p 4 +
  ((1 : K) / 3) * p 0 * p 1 * p 3 * p 4 ^ 3 +
  (1 : K) * p 1 ^ 6 +
  ((1 : K) / 2) * p 1 ^ 3 * p 2 * p 4 * p 5 +
  (1 : K) * p 2 ^ 6 +
  (1 : K) * p 3 ^ 6 +
  (1 : K) * p 4 ^ 6 +
  (1 : K) * p 5 ^ 6

def mixedA (p : Fin 6 → K) : K :=
  (1 : K) * p 0 * p 1 * p 2 * p 3 * p 4 * p 5

def flip0 (p : Fin 6 → K) : Fin 6 → K := ![-p 0,p 1,p 2,-p 3,p 4,p 5]
def flip1 (p : Fin 6 → K) : Fin 6 → K := ![p 0,-p 1,p 2,p 3,-p 4,p 5]
def flip2 (p : Fin 6 → K) : Fin 6 → K := ![p 0,p 1,-p 2,p 3,p 4,-p 5]

theorem mixed_flip0 (p : Fin 6 → K) : mixedF (flip0 p) = mixedF p := by
  simp [mixedF, flip0]; ring
theorem mixed_flip1 (p : Fin 6 → K) : mixedF (flip1 p) = mixedF p := by
  simp [mixedF, flip1]; ring
theorem mixed_flip2 (p : Fin 6 → K) : mixedF (flip2 p) = mixedF p := by
  simp [mixedF, flip2]; ring
theorem skew_flip0_defect (p : Fin 6 → K) :
    skewF (flip0 p) - skewF p = -2 * p 1 ^ 3 * p 2 * p 3 * p 4 := by
  simp [skewF, flip0]; ring
theorem skew_flip1 (p : Fin 6 → K) : skewF (flip1 p) = skewF p := by
  simp [skewF, flip1]; ring
theorem skew_flip2_defect (p : Fin 6 → K) :
    skewF (flip2 p) - skewF p = -2 * p 1 ^ 3 * p 2 * p 3 * p 4 := by
  simp [skewF, flip2]; ring
theorem source_flip0 (p : Fin 6 → K) :
    skewA (flip0 p) = skewA p ∧ mixedA (flip0 p) = mixedA p := by
  constructor <;> simp [skewA, mixedA, flip0] <;> ring
theorem source_flip1 (p : Fin 6 → K) :
    skewA (flip1 p) = skewA p ∧ mixedA (flip1 p) = mixedA p := by
  constructor <;> simp [skewA, mixedA, flip1] <;> ring
theorem source_flip2 (p : Fin 6 → K) :
    skewA (flip2 p) = skewA p ∧ mixedA (flip2 p) = mixedA p := by
  constructor <;> simp [skewA, mixedA, flip2] <;> ring

/-- The accepted mixed-polar coordinates, ordered (v,u,w,x,y,R). -/
def coordinates (p : Fin 6 → K) : Fin 6 → K :=
  ![p 3 / p 0, (p 4 / p 1) / (p 3 / p 0),
    (p 5 / p 2) / (p 3 / p 0), p 0 ^ 2 / p 2 ^ 2,
    p 1 ^ 2 / p 2 ^ 2, p 2 ^ 2]
theorem coordinates_flip0 (p : Fin 6 → K) : coordinates (flip0 p) = coordinates p := by
  funext i; fin_cases i <;> simp [coordinates, flip0]

def chart (p : Fin 6 → K) : Prop := p 0 ≠ 0 ∧ p 1 ≠ 0 ∧ p 2 ≠ 0 ∧ p 3 ≠ 0
def seed : Fin 6 → K := fun _ => 1
theorem seed_chart : chart (seed : Fin 6 → K) ∧ chart (flip0 seed : Fin 6 → K) := by
  simp [chart, seed, flip0]

variable [CharZero K]
theorem seed_values : skewF (seed : Fin 6 → K) = 8 ∧ skewF (flip0 seed : Fin 6 → K) = 6 := by
  have h0 : skewF (seed : Fin 6 → K) = 8 := by norm_num [skewF, seed]
  constructor
  · exact h0
  · have h := skew_flip0_defect (seed : Fin 6 → K)
    simp only [seed, one_pow, mul_one, h0] at h
    linear_combination h

/-- No single function of these invariants gives F on the entire displayed
chart. The witness is off F=0; this is not a nonexistence theorem for maps
between hypersurfaces, or for rational expressions with additional poles. -/
theorem no_pointwise_factorization :
    ¬ ∃ H : (Fin 6 → K) → K, ∀ p, chart p → H (coordinates p) = skewF p := by
  rintro ⟨H, h⟩
  have h1 := h seed (seed_chart (K:=K)).1
  have h2 := h (flip0 seed) (seed_chart (K:=K)).2
  rw [coordinates_flip0] at h2
  have he : skewF (seed : Fin 6 → K) = skewF (flip0 seed : Fin 6 → K) := h1.symm.trans h2
  rw [(seed_values (K:=K)).1, (seed_values (K:=K)).2] at he
  norm_num at he

end HodgeLab.OneReflectionSkew.CoordinateComparison

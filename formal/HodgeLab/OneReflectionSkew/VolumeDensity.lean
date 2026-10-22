import HodgeLab.OneReflectionSkew.CoordinateVolume
import Mathlib.Tactic.FieldSimp

/-! Coefficients of the ordered ambient rational volume before taking residue.
The nonzero denominator hypotheses describe the complement of the sextic.
No residue, global descent or primitive theorem is asserted. -/

namespace HodgeLab.OneReflectionSkew.VolumeDensity
open CoordinateComparison ChartSubstitution CoordinateVolume
variable {K : Type*} [Field K] [CharZero K]

def chartDenominator (U r w t z : K) : K := z^6 + cubic U r w t

noncomputable def xCoefficient (x r w t z : K) : K :=
  skewA (physicalPoint x r w t z) * (omegaMatrix x r w t z).det /
    (skewF (physicalPoint x r w t z))^2

def uCoefficient (U r w t z : K) : K :=
  -(U^2) / (2 * (chartDenominator U r w t z)^2)

theorem xCoefficient_eq (x r w t z : K) :
    xCoefficient x r w t z = -(x^5) / (chartDenominator (x^2) r w t z)^2 := by
  rw [xCoefficient, protected_source_substitution, omegaMatrix_det, protected_substitution]
  unfold chartDenominator
  ring

/-- Forward pullback through U=x²; x may vanish, but the rational volume
is considered on the complement of its pole divisor. -/
theorem square_pullback (x r w t z : K)
    (hG : chartDenominator (x^2) r w t z ≠ 0) :
    uCoefficient (x^2) r w t z * (squareJacobian x r w t z).det =
      xCoefficient x r w t z := by
  rw [squareJacobian_det, xCoefficient_eq]
  unfold uCoefficient
  field_simp [hG]

omit [CharZero K] in
theorem affine_nonsingular_iff (x r w t z : K) :
    (affineJacobian x r w t z).det ≠ 0 ↔ x ≠ 0 := by
  rw [affineJacobian_det]
  constructor
  · intro h hx
    apply h
    rw [hx]
    norm_num
  · intro hx
    exact pow_ne_zero 2 hx

theorem square_nonsingular_iff (x r w t z : K) :
    (squareJacobian x r w t z).det ≠ 0 ↔ x ≠ 0 := by
  rw [squareJacobian_det]
  simp

/-- Recovering the coefficient by division uses the nonzero square-map
Jacobian. This is scalar normalization, not a field-trace statement. -/
theorem coefficient_recovery (x r w t z : K) (hx : x ≠ 0)
    (hG : chartDenominator (x^2) r w t z ≠ 0) :
    xCoefficient x r w t z / (squareJacobian x r w t z).det =
      uCoefficient (x^2) r w t z := by
  rw [← square_pullback x r w t z hG]
  exact mul_div_cancel_right₀ _ ((square_nonsingular_iff x r w t z).mpr hx)

theorem protected_pole_condition (x r w t z : K) :
    skewF (physicalPoint x r w t z) ≠ 0 ↔
      chartDenominator (x^2) r w t z ≠ 0 := by
  rw [protected_substitution]
  rfl

end HodgeLab.OneReflectionSkew.VolumeDensity

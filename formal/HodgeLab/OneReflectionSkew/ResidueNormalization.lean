import HodgeLab.OneReflectionSkew.NormalChart
import Mathlib.RingTheory.Derivation.Basic

/-! Local scalar coefficient calculus for the pole reduction. A coordinate
derivation is an explicit hypothesis; existence in a particular function field
is not supplied. The ambient calculation has G nonzero. Normalization of the
remaining simple-pole numerator will not require G nonzero. -/

namespace HodgeLab.OneReflectionSkew.ResidueNormalization
open ChartSubstitution VolumeDensity NormalChart
variable {K : Type*} [Field K] [CharZero K]

def betaCoefficient (U r w t z : K) : K :=
  U^2 / (12*z^5*chartDenominator U r w t z)

def poleNumerator (U z : K) : K := 5*U^2/(12*z^6)

variable [Algebra ℚ K]

omit [CharZero K] in
theorem cubic_derivative_zero (D : Derivation ℚ K K) (U r w t : K)
    (hU : D U = 0) (hr : D r = 0) (hw : D w = 0) (ht : D t = 0) :
    D (cubic U r w t) = 0 := by
  have h7 : D (7 : K) = 0 := D.map_natCast 7
  simp [cubic, aCoeff, bCoeff, cCoeff, dCoeff, map_add, map_sub,
    D.leibniz_div, hU, hr, hw, ht, h7]

omit [CharZero K] in
theorem chartDenominator_derivative (D : Derivation ℚ K K) (U r w t z : K)
    (hU : D U = 0) (hr : D r = 0) (hw : D w = 0) (ht : D t = 0)
    (hzD : D z = 1) :
    D (chartDenominator U r w t z) = 6*z^5 := by
  simp [chartDenominator, map_add, cubic_derivative_zero D U r w t hU hr hw ht,
    hzD, smul_eq_mul]

omit [CharZero K] in
theorem beta_denominator_derivative (D : Derivation ℚ K K) (U r w t z : K)
    (hU : D U = 0) (hr : D r = 0) (hw : D w = 0) (ht : D t = 0)
    (hzD : D z = 1) :
    D (12*z^5*chartDenominator U r w t z) =
      60*z^4*chartDenominator U r w t z + 72*z^10 := by
  have h12 : D (12 : K) = 0 := D.map_natCast 12
  simp [chartDenominator_derivative D U r w t z hU hr hw ht hzD,
    hzD, smul_eq_mul, h12]
  ring

theorem beta_derivative (D : Derivation ℚ K K) (U r w t z : K)
    (hU : D U = 0) (hr : D r = 0) (hw : D w = 0) (ht : D t = 0)
    (hzD : D z = 1) (hz : z ≠ 0) (hG : chartDenominator U r w t z ≠ 0) :
    D (betaCoefficient U r w t z) =
      uCoefficient U r w t z - poleNumerator U z / chartDenominator U r w t z := by
  rw [betaCoefficient, D.leibniz_div]
  simp only [Derivation.leibniz_pow, hU, smul_zero]
  rw [beta_denominator_derivative D U r w t z hU hr hw ht hzD]
  simp only [smul_eq_mul]
  unfold uCoefficient poleNumerator
  field_simp [hz, hG]
  ring

/-- Coefficient identity in the ordered model alpha wedge dz, where alpha
has degree four. It is not a general exterior-derivative or residue theorem. -/
theorem ambient_reduction (D : Derivation ℚ K K) (U r w t z : K)
    (hU : D U = 0) (hr : D r = 0) (hw : D w = 0) (ht : D t = 0)
    (hzD : D z = 1) (hz : z ≠ 0) (hG : chartDenominator U r w t z ≠ 0) :
    uCoefficient U r w t z = D (betaCoefficient U r w t z) +
      poleNumerator U z / chartDenominator U r w t z := by
  rw [beta_derivative D U r w t z hU hr hw ht hzD hz hG]
  ring

/-- Division of the simple-pole numerator by the actual evaluated normal
partial derivative. This is a scalar normalization, not a residue operator. -/
noncomputable def normalizedPoleCoefficient (U r w t z : K) : K :=
  poleNumerator U z / normalDerivative U r w t z

omit [Algebra ℚ K] in
/-- No assumption G nonzero is used here. In particular, the identity can
be specialized on G=0 when z is nonzero, independently of the ambient proof. -/
theorem normalizedPoleCoefficient_eq (U r w t z : K) (hz : z ≠ 0) :
    normalizedPoleCoefficient U r w t z = 5*U^2/(72*z^11) := by
  rw [normalizedPoleCoefficient, normalDerivative_eq]
  unfold poleNumerator
  field_simp [hz]
  ring

omit [Algebra ℚ K] in
/-- Factoring the ambient simple pole into the logarithmic normal factor
G_z/G and its normalized coefficient; all denominator conditions are explicit. -/
theorem simple_pole_factorization (U r w t z : K) (hz : z ≠ 0)
    (hG : chartDenominator U r w t z ≠ 0) :
    poleNumerator U z / chartDenominator U r w t z =
      (normalDerivative U r w t z / chartDenominator U r w t z) *
        normalizedPoleCoefficient U r w t z := by
  rw [normalizedPoleCoefficient, normalDerivative_eq]
  field_simp [hz, hG]

theorem ambient_normal_factorization (D : Derivation ℚ K K) (U r w t z : K)
    (hU : D U = 0) (hr : D r = 0) (hw : D w = 0) (ht : D t = 0)
    (hzD : D z = 1) (hz : z ≠ 0) (hG : chartDenominator U r w t z ≠ 0) :
    uCoefficient U r w t z = D (betaCoefficient U r w t z) +
      (normalDerivative U r w t z / chartDenominator U r w t z) *
        normalizedPoleCoefficient U r w t z := by
  rw [← simple_pole_factorization U r w t z hz hG]
  exact ambient_reduction D U r w t z hU hr hw ht hzD hz hG

end HodgeLab.OneReflectionSkew.ResidueNormalization

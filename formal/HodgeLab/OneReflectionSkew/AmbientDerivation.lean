import HodgeLab.OneReflectionSkew.ResidueNormalization
import Mathlib.RingTheory.Etale.Kaehler
import Mathlib.RingTheory.Localization.FractionRing
import Mathlib.Algebra.CharP.Algebra

/-! Construct the z-coordinate derivation on the rational ambient chart.
The localization of differentials supplies the extension; no derivation
on the hypersurface quotient is asserted. -/

namespace HodgeLab.OneReflectionSkew.AmbientDerivation

open MvPolynomial
open ChartSubstitution VolumeDensity NormalChart ResidueNormalization

abbrev P := MvPolynomial (Fin 5) ℚ
abbrev K := FractionRing P

instance : CharZero K := charZero_of_injective_algebraMap (IsFractionRing.injective P K)

noncomputable def coord (i : Fin 5) : K := algebraMap P K (X i)

noncomputable def polynomialD : Derivation ℚ P K :=
  (Algebra.linearMap P K).compDer (pderiv (4 : Fin 5))

noncomputable instance : Algebra.FormallyEtale P K :=
  Algebra.FormallyEtale.of_isLocalization (Rₘ := K) (nonZeroDivisors P)

noncomputable def ambientD : Derivation ℚ K K :=
  ((polynomialD.liftKaehlerDifferential.liftBaseChange K).comp
    (KaehlerDifferential.tensorKaehlerEquivOfFormallyEtale ℚ P K).symm.toLinearMap).compDer
      (KaehlerDifferential.D ℚ K)

theorem ambientD_algebraMap (p : P) :
    ambientD (algebraMap P K p) = algebraMap P K (pderiv (4 : Fin 5) p) := by
  change (polynomialD.liftKaehlerDifferential.liftBaseChange K)
    ((KaehlerDifferential.tensorKaehlerEquivOfFormallyEtale ℚ P K).symm
      (KaehlerDifferential.D ℚ K (algebraMap P K p))) = _
  rw [KaehlerDifferential.tensorKaehlerEquivOfFormallyEtale_symm_D_algebraMap]
  simp [polynomialD]

theorem ambientD_coord (i : Fin 5) :
    ambientD (coord i) = if i = 4 then 1 else 0 := by
  rw [coord, ambientD_algebraMap]
  fin_cases i <;> simp

theorem coord_ne_zero (i : Fin 5) : coord i ≠ 0 := by
  exact (map_ne_zero_iff (algebraMap P K) (IsFractionRing.injective P K)).mpr
    (MvPolynomial.X_ne_zero i)

theorem ambientD_quotient (p q : P) :
    ambientD (algebraMap P K p / algebraMap P K q) =
      (algebraMap P K (pderiv (4 : Fin 5) p) * algebraMap P K q -
        algebraMap P K p * algebraMap P K (pderiv (4 : Fin 5) q)) /
        (algebraMap P K q)^2 := by
  rw [ambientD.leibniz_div, ambientD_algebraMap, ambientD_algebraMap]
  simp only [smul_eq_mul]
  ring

theorem reciprocal_derivative : ambientD ((coord 4)⁻¹) = -((coord 4)^2)⁻¹ := by
  have h := ambientD_quotient (1 : P) (X 4)
  simpa [coord, div_eq_mul_inv] using h

theorem scaled_reciprocal_derivative : (coord 4)^2 * ambientD ((coord 4)⁻¹) = -1 := by
  rw [reciprocal_derivative]
  field_simp [coord_ne_zero]

noncomputable def G : K := chartDenominator (coord 0) (coord 1) (coord 2) (coord 3) (coord 4)

theorem G_eq_algebraMap : G = algebraMap P K (chartPolynomial (K := ℚ)) := by
  have hC : algebraMap P K (C (1 / 7 : ℚ)) = 1 / 7 := by
    change algebraMap P K (algebraMap ℚ P (1 / 7)) = _
    rw [← IsScalarTower.algebraMap_apply ℚ P K]
    norm_num
  simp only [G, chartDenominator, cubic, aCoeff, bCoeff, cCoeff, dCoeff,
    chartPolynomial, coord, map_add, map_mul, map_pow, map_sub, map_one, hC]
  ring

theorem ambientD_G : ambientD G = 6 * (coord 4)^5 := by
  exact chartDenominator_derivative ambientD _ _ _ _ _
    (by simp [ambientD_coord]) (by simp [ambientD_coord])
    (by simp [ambientD_coord]) (by simp [ambientD_coord]) (by simp [ambientD_coord])

theorem G_ne_zero : G ≠ 0 := by
  intro h
  have hD := ambientD_G
  rw [h, map_zero] at hD
  exact (mul_ne_zero (by norm_num : (6 : K) ≠ 0) (pow_ne_zero _ (coord_ne_zero 4))) hD.symm

theorem concrete_ambient_reduction :
    uCoefficient (coord 0) (coord 1) (coord 2) (coord 3) (coord 4) =
      ambientD (betaCoefficient (coord 0) (coord 1) (coord 2) (coord 3) (coord 4)) +
        poleNumerator (coord 0) (coord 4) / G := by
  exact ambient_reduction ambientD _ _ _ _ _
    (by simp [ambientD_coord]) (by simp [ambientD_coord])
    (by simp [ambientD_coord]) (by simp [ambientD_coord]) (by simp [ambientD_coord])
    (coord_ne_zero 4) G_ne_zero

theorem concrete_normal_factorization :
    uCoefficient (coord 0) (coord 1) (coord 2) (coord 3) (coord 4) =
      ambientD (betaCoefficient (coord 0) (coord 1) (coord 2) (coord 3) (coord 4)) +
        ((6 * (coord 4)^5) / G) * (5 * (coord 0)^2 / (72 * (coord 4)^11)) := by
  rw [concrete_ambient_reduction]
  have h := simple_pole_factorization (coord 0) (coord 1) (coord 2) (coord 3) (coord 4)
    (coord_ne_zero 4) G_ne_zero
  rw [normalDerivative_eq, normalizedPoleCoefficient_eq _ _ _ _ _ (coord_ne_zero 4)] at h
  exact congrArg (fun v => ambientD (betaCoefficient (coord 0) (coord 1) (coord 2) (coord 3) (coord 4)) + v) h

/-- A derivation with these coordinate values cannot also live on G=0,z≠0.
This is a normal-direction obstruction, not a nonexistence result for primitives. -/
theorem no_unchanged_derivation_on_divisor {L : Type*} [Field L] [CharZero L] [Algebra ℚ L]
    (D : Derivation ℚ L L) (U r w t z : L)
    (hU : D U = 0) (hr : D r = 0) (hw : D w = 0) (ht : D t = 0)
    (hzD : D z = 1) (hz : z ≠ 0) (hG : chartDenominator U r w t z = 0) : False := by
  have h := chartDenominator_derivative D U r w t z hU hr hw ht hzD
  rw [hG, map_zero] at h
  exact (mul_ne_zero (by norm_num : (6 : L) ≠ 0) (pow_ne_zero _ hz)) h.symm

end HodgeLab.OneReflectionSkew.AmbientDerivation

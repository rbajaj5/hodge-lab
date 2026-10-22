import HodgeLab.OneReflectionSkew.AmbientDerivation
import Mathlib.LinearAlgebra.ExteriorAlgebra.Basic
import Mathlib.Tactic.NoncommRing
import Mathlib.RingTheory.Kaehler.Polynomial
import Mathlib.LinearAlgebra.TensorProduct.Basis
import Mathlib.LinearAlgebra.ExteriorAlgebra.OfAlternating
import Mathlib.LinearAlgebra.Determinant

/-! Actual Kähler one-forms and their exterior products over the ambient
rational-function field. We prove the standard expression d(f) wedge alpha
for the specific decomposable four-form f alpha, not a general exterior
differential, de Rham complex or residue map. -/

namespace HodgeLab.OneReflectionSkew.DifferentialForms
open AmbientDerivation ChartSubstitution VolumeDensity ResidueNormalization
open Module

abbrev Omega := KaehlerDifferential ℚ K
abbrev E := ExteriorAlgebra K Omega

noncomputable instance : Algebra P E :=
  Algebra.compHom E (algebraMap P K)

instance : IsScalarTower P K E := IsScalarTower.of_algebraMap_eq' rfl

noncomputable def oneForm (f : K) : E :=
  ExteriorAlgebra.ι K (KaehlerDifferential.D ℚ K f)

noncomputable def alpha : E :=
  oneForm (coord 0) * (oneForm (coord 1) * (oneForm (coord 2) * oneForm (coord 3)))

noncomputable def volume : E := alpha * oneForm (coord 4)

theorem base_wedge_zero (i : Fin 4) : oneForm (coord i.castSucc) * alpha = 0 := by
  have h := ExteriorAlgebra.ι_mul_prod_list (R := K)
    (fun j : Fin 4 => KaehlerDifferential.D ℚ K (coord j.castSucc)) i
  simpa [oneForm, alpha, List.ofFn_succ, mul_assoc] using h

theorem coordinate_swap (i j : Fin 5) :
    oneForm (coord i) * oneForm (coord j) = -(oneForm (coord j) * oneForm (coord i)) := by
  apply eq_neg_of_add_eq_zero_left
  exact ExteriorAlgebra.ι_add_mul_swap _ _

theorem normal_first_orientation : oneForm (coord 4) * alpha = volume := by
  let a := oneForm (coord 0)
  let b := oneForm (coord 1)
  let c := oneForm (coord 2)
  let d := oneForm (coord 3)
  let z := oneForm (coord 4)
  have h0 : z*a = -(a*z) := coordinate_swap 4 0
  have h1 : z*b = -(b*z) := coordinate_swap 4 1
  have h2 : z*c = -(c*z) := coordinate_swap 4 2
  have h3 : z*d = -(d*z) := coordinate_swap 4 3
  change z*(a*(b*(c*d))) = (a*(b*(c*d)))*z
  calc
    z*(a*(b*(c*d))) = -(a*(z*(b*(c*d)))) := by rw [← mul_assoc, h0]; noncomm_ring
    _ = a*(b*(z*(c*d))) := by rw [← mul_assoc z b, h1]; noncomm_ring
    _ = -(a*(b*(c*(z*d)))) := by rw [← mul_assoc z c, h2]; noncomm_ring
    _ = (a*(b*(c*d)))*z := by rw [h3]; noncomm_ring

noncomputable def wedgeDerivation : Derivation ℚ K E :=
  ((LinearMap.mulRight K alpha).comp (ExteriorAlgebra.ι K)).compDer (KaehlerDifferential.D ℚ K)

noncomputable def normalDerivation : Derivation ℚ K E :=
  (LinearMap.toSpanSingleton K E volume).compDer ambientD

theorem wedgeDerivation_apply (f : K) : wedgeDerivation f = oneForm f * alpha := rfl

theorem normalDerivation_apply (f : K) : normalDerivation f = ambientD f • volume := rfl

theorem polynomial_derivations_eq :
    wedgeDerivation.compAlgebraMap P = normalDerivation.compAlgebraMap P := by
  apply MvPolynomial.derivation_ext
  intro i
  change oneForm (coord i) * alpha = ambientD (coord i) • volume
  fin_cases i
  · simpa [ambientD_coord] using base_wedge_zero 0
  · simpa [ambientD_coord] using base_wedge_zero 1
  · simpa [ambientD_coord] using base_wedge_zero 2
  · simpa [ambientD_coord] using base_wedge_zero 3
  · simpa [ambientD_coord] using normal_first_orientation

theorem derivations_eq : wedgeDerivation = normalDerivation := by
  ext f
  obtain ⟨p,q,hq,rfl⟩ := IsFractionRing.div_surjective P f
  rw [wedgeDerivation.leibniz_div, normalDerivation.leibniz_div]
  have hp := Derivation.congr_fun polynomial_derivations_eq p
  have hq' := Derivation.congr_fun polynomial_derivations_eq q
  change wedgeDerivation (algebraMap P K p) = normalDerivation (algebraMap P K p) at hp
  change wedgeDerivation (algebraMap P K q) = normalDerivation (algebraMap P K q) at hq'
  rw [hp, hq']

theorem differential_wedge (f : K) : oneForm f * alpha = ambientD f • volume := by
  exact Derivation.congr_fun derivations_eq f

noncomputable def differentialBasis : Basis (Fin 5) K Omega :=
  ((KaehlerDifferential.mvPolynomialBasis ℚ (Fin 5)).baseChange K).map
    (KaehlerDifferential.tensorKaehlerEquivOfFormallyEtale ℚ P K)

theorem differentialBasis_apply (i : Fin 5) :
    differentialBasis i = KaehlerDifferential.D ℚ K (coord i) := by
  rw [differentialBasis, Basis.map_apply, Basis.baseChange_apply,
    KaehlerDifferential.mvPolynomialBasis_apply]
  apply (KaehlerDifferential.tensorKaehlerEquivOfFormallyEtale ℚ P K).symm.injective
  rw [LinearEquiv.symm_apply_apply]
  exact (KaehlerDifferential.tensorKaehlerEquivOfFormallyEtale_symm_D_algebraMap ℚ P K
    (MvPolynomial.X i)).symm

noncomputable def alternatingFamily (n : ℕ) : Omega [⋀^Fin n]→ₗ[K] K :=
  if h : n = 5 then by subst n; exact differentialBasis.det else 0

noncomputable def topCoefficient : E →ₗ[K] K := ExteriorAlgebra.liftAlternating alternatingFamily

theorem volume_eq_multi : volume = ExteriorAlgebra.ιMulti K 5 differentialBasis := by
  simp [volume, alpha, ExteriorAlgebra.ιMulti_apply, Matrix.vecTail,
    differentialBasis_apply, oneForm, mul_assoc]

theorem topCoefficient_volume : topCoefficient volume = 1 := by
  rw [volume_eq_multi, topCoefficient, ExteriorAlgebra.liftAlternating_apply_ιMulti]
  simp only [alternatingFamily]
  exact differentialBasis.det_self

theorem volume_ne_zero : volume ≠ 0 := by
  intro h
  have h' := topCoefficient_volume
  rw [h, map_zero] at h'
  exact zero_ne_one h'

noncomputable def betaScalar : K := betaCoefficient (coord 0) (coord 1) (coord 2) (coord 3) (coord 4)
noncomputable def psiScalar : K := uCoefficient (coord 0) (coord 1) (coord 2) (coord 3) (coord 4)
noncomputable def residueScalar : K := 5*(coord 0)^2/(72*(coord 4)^11)

/-- Standard differential expression of betaScalar dU wedge dr wedge dw wedge dt.
No general exterior differential on arbitrary exterior-algebra elements is defined. -/
noncomputable def betaDifferential : E := oneForm betaScalar * alpha

noncomputable def logarithmicNormal : E := G⁻¹ • oneForm G

theorem actual_form_reduction :
    psiScalar • volume = betaDifferential + residueScalar • (logarithmicNormal * alpha) := by
  rw [betaDifferential, differential_wedge, logarithmicNormal, smul_mul_assoc,
    differential_wedge, ambientD_G, smul_smul, smul_smul, ← add_smul]
  apply congrArg (fun c : K => c • volume)
  simpa [psiScalar, betaScalar, residueScalar, div_eq_mul_inv, mul_comm, mul_left_comm, mul_assoc]
    using concrete_normal_factorization

end HodgeLab.OneReflectionSkew.DifferentialForms

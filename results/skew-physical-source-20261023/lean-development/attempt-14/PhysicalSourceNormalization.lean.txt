import HodgeLab.OneReflectionSkew.DifferentialForms
import HodgeLab.OneReflectionSkew.ScalarExtensionTrace
import Mathlib.Tactic.Module

/-!
Exact coordinate, scalar and exterior-form factors in the physical cover.
The period/cohomology interpretation of the packet connection is separate.
-/
noncomputable section

namespace HodgeLab.OneReflectionSkew.PhysicalSourceNormalization

open Polynomial ChartSubstitution PhysicalCoverBinding

variable {K : Type*} [Field K] [CharZero K]

def vChart (r w : K) : K := r⁻¹ + r*w
def aChart (r w : K) : K := aCoeff r w / r^3
def coverA (r v : K) : K := r^3 + r⁻¹^3 + (v*r-1)^6/r^15
def aR (r w : K) : K := 6*r^5/r^3 - 3*aCoeff r w/r^4
def aW (r w : K) : K := 6*w^5/r^3
def vR (r w : K) : K := w-r⁻¹^2
def jacobian (r w : K) : K := aR r w*r - aW r w*vR r w
def fR (r w : K) : K :=
  (physicalPolynomial (aChart r w) (vChart r w)).derivative.eval r

theorem vChart_inverse (r w : K) (hr : r ≠ 0) :
    (vChart r w*r-1)/r^2 = w := by
  unfold vChart
  field_simp <;> ring

theorem aChart_eq_coverA (r w : K) (hr : r ≠ 0) :
    aChart r w = coverA r (vChart r w) := by
  have hv : vChart r w*r-1 = r^2*w := by
    unfold vChart
    field_simp
    ring
  rw [coverA, hv]
  unfold aChart aCoeff
  field_simp <;> ring

theorem physical_cover_equation (r w : K) (hr : r ≠ 0) :
    (physicalPolynomial (aChart r w) (vChart r w)).eval r = 0 := by
  have hv : vChart r w*r-1 = r^2*w := by
    unfold vChart
    field_simp
    ring
  simp only [physicalPolynomial, eval_sub, eval_add, eval_pow, eval_mul, eval_C,
    eval_X, eval_one]
  rw [hv]
  unfold aChart aCoeff
  field_simp <;> ring

theorem cubic_coordinate_change (V r w t : K) (hr : r ≠ 0) :
    cubic (V/r) r w t =
      aChart r w*V^3 + (t*vChart r w)*V^2 + (t*(1-t^2)/7)*V + (1+t^6) := by
  unfold cubic aChart vChart aCoeff bCoeff cCoeff dCoeff
  field_simp <;> ring

theorem fR_expanded (r w : K) :
    fR r w = 18*r^17 + 12*r^11 +
      6*vChart r w*(vChart r w*r-1)^5 - 15*aChart r w*r^14 := by
  simp [fR, physicalPolynomial, derivative_pow]
  ring

theorem jacobian_eq (r w : K) (hr : r ≠ 0) :
    jacobian r w = fR r w/r^14 := by
  rw [fR_expanded]
  have hv : vChart r w*r-1 = r^2*w := by
    unfold vChart
    field_simp
    ring
  rw [hv]
  unfold jacobian aR aW vR aChart aCoeff vChart
  field_simp <;> ring

section Forms

variable [Algebra ℚ K]
abbrev Forms := ExteriorAlgebra K (KaehlerDifferential ℚ K)

def formD : Derivation ℚ K (Forms (K := K)) :=
  (ExteriorAlgebra.ι K).compDer (KaehlerDifferential.D ℚ K)

def d (x : K) : Forms (K := K) := formD x

theorem d_mul (x y : K) : d (x*y) = x • d y + y • d x := formD.leibniz x y

theorem d_square_zero (x : K) : d x*d x = 0 :=
  ExteriorAlgebra.ι_sq_zero _

theorem d_swap (x y : K) : d x*d y = -(d y*d x) := by
  apply eq_neg_of_add_eq_zero_left
  exact ExteriorAlgebra.ι_add_mul_swap _ _

theorem d_vChart (r w : K) : d (vChart r w) = vR r w • d r + r • d w := by
  change formD (r⁻¹+r*w) = _
  rw [map_add, formD.leibniz_inv, formD.leibniz]
  unfold vR d
  module

theorem d_aChart (r w : K) (hr : r ≠ 0) :
    d (aChart r w) = aR r w • d r + aW r w • d w := by
  change formD ((1+r^6+w^6)/r^3) = _
  rw [formD.leibniz_div]
  simp only [map_add, Derivation.map_one_eq_zero, formD.leibniz_pow]
  simp only [Nat.reduceSub, zero_add, ← Nat.cast_smul_eq_nsmul K]
  unfold aR aW aCoeff d
  simp only [smul_add, smul_sub, smul_smul]
  have h1 : (r^3)⁻¹^2*(r^3*(6*r^5) - (1+r^6+w^6)*(3*r^2)) =
      6*r^5/r^3 - 3*(1+r^6+w^6)/r^4 := by field_simp <;> ring
  have h2 : (r^3)⁻¹^2*(r^3*(6*w^5)) = 6*w^5/r^3 := by field_simp <;> ring
  rw [← h1, ← h2]
  simp only [inv_pow]
  module

theorem two_form_change (r w : K) (hr : r ≠ 0) :
    d (aChart r w)*d (vChart r w) = jacobian r w • (d r*d w) := by
  rw [d_aChart r w hr, d_vChart]
  simp only [add_mul, mul_add, smul_mul_assoc, mul_smul_comm, smul_smul,
    d_square_zero, smul_zero, add_zero, zero_add]
  rw [d_swap w r]
  simp only [smul_neg]
  unfold jacobian
  module

def oldFourForm (U r w t : K) : Forms (K := K) := d U*(d r*(d w*d t))
def newFourForm (V a v t : K) : Forms (K := K) := d V*(d a*(d v*d t))

theorem fibre_gauge (U r w t : K) :
    d (r*U)*(d r*(d w*d t)) = r • oldFourForm U r w t := by
  rw [d_mul]
  simp only [add_mul, smul_mul_assoc]
  rw [← mul_assoc (d r) (d r), d_square_zero, zero_mul, smul_zero, add_zero]
  rfl

theorem four_form_jacobian (U r w t : K) (hr : r ≠ 0) :
    newFourForm (r*U) (aChart r w) (vChart r w) t =
      (fR r w/r^13) • oldFourForm U r w t := by
  unfold newFourForm
  rw [← mul_assoc (d (aChart r w)), two_form_change r w hr,
    smul_mul_assoc, mul_smul_comm, mul_assoc, fibre_gauge, smul_smul, jacobian_eq r w hr]
  congr 1
  field_simp <;> ring

theorem source_form_transport (U r w t z : K) (hr : r ≠ 0)
    (hz : z ≠ 0) (hf : fR r w ≠ 0) :
    (5*U^2/(72*z^11)) • oldFourForm U r w t =
      ((5/72:K)*(r^11/fR r w)*((r*U)^2/z^11)) •
        newFourForm (r*U) (aChart r w) (vChart r w) t := by
  rw [four_form_jacobian U r w t hr, smul_smul]
  congr 1
  field_simp <;> ring

theorem fibre_last_orientation (V a v t : K) :
    newFourForm V a v t = -(d a*(d v*(d t*d V))) := by
  unfold newFourForm
  rw [← mul_assoc (d V), d_swap V a]
  rw [neg_mul, mul_assoc, ← mul_assoc (d V), d_swap V v]
  rw [neg_mul, mul_neg, neg_neg, mul_assoc, d_swap V t]
  simp only [mul_neg]

theorem normalized_source_form_transport (U r w t z : K) (hr : r ≠ 0)
    (hz : z ≠ 0) (hf : fR r w ≠ 0) :
    ResidueNormalization.normalizedPoleCoefficient U r w t z • oldFourForm U r w t =
      ((5/72:K)*(r^11/fR r w)*((r*U)^2/z^11)) •
        newFourForm (r*U) (aChart r w) (vChart r w) t := by
  rw [ResidueNormalization.normalizedPoleCoefficient_eq U r w t z hz]
  exact source_form_transport U r w t z hr hz hf

end Forms

section FibreColumn

def fibreP (a b c d0 V : K) : K := a*V^3+b*V^2+c*V+d0
def fibrePPrime (a b c V : K) : K := 3*a*V^2+2*b*V+c
def delta (a b c d0 : K) : K :=
  27*a^2*d0^2-18*a*b*c*d0+4*a*c^3+4*b^3*d0-b^2*c^2
def n0 (a b c d0 : K) : K := 27*a*c*d0-12*b^2*d0+b*c^2
def n1 (a b c d0 : K) : K := a*(3*b*d0-c^2)
def rNumerator (a b c d0 V : K) : K :=
  2*n1 a b c d0*V^2+(3*a*c*d0+2*b^2*d0-b*c^2)*V+(9*a*d0^2-b*c*d0)
def rNumeratorPrime (a b c d0 V : K) : K :=
  4*n1 a b c d0*V+(3*a*c*d0+2*b^2*d0-b*c^2)
def bColumn0 (a b c d0 : K) : K := n0 a b c d0/(6*delta a b c d0)
def bColumn1 (a b c d0 : K) : K := n1 a b c d0/delta a b c d0
def correction (a b c d0 V : K) : K := rNumerator a b c d0 V/delta a b c d0
def correctionPrime (a b c d0 V : K) : K := rNumeratorPrime a b c d0 V/delta a b c d0

/-- The one packet b-column identity, checked as an exact polynomial identity. -/
theorem b_column_cleared (a b c d0 V : K) :
    5*delta a b c d0*V^2 =
      -fibreP a b c d0 V*(n0 a b c d0+6*n1 a b c d0*V)
      -6*fibreP a b c d0 V*rNumeratorPrime a b c d0 V
      +5*fibrePPrime a b c V*rNumerator a b c d0 V := by
  simp only [delta, fibreP, fibrePPrime, n0, n1, rNumerator, rNumeratorPrime]
  ring

theorem b_column_rational (a b c d0 V : K) (hΔ : delta a b c d0 ≠ 0) :
    (5/6:K)*V^2 =
      -fibreP a b c d0 V*(bColumn0 a b c d0+bColumn1 a b c d0*V)
      -fibreP a b c d0 V*correctionPrime a b c d0 V
      +(5/6:K)*fibrePPrime a b c V*correction a b c d0 V := by
  unfold bColumn0 bColumn1 correction correctionPrime
  field_simp
  linear_combination b_column_cleared a b c d0 V

variable [Algebra ℚ K]

theorem b_variation (D : Derivation ℚ K K) (a b c d0 V z : K)
    (ha : D a = 0) (hb : D b = 1) (hc : D c = 0) (hq : D d0 = 0)
    (hV : D V = 0) (hz : z ≠ 0) (hcurve : z^6+fibreP a b c d0 V = 0) :
    D (z⁻¹^5) = (5/6:K)*V^2/z^11 := by
  have h := congrArg D hcurve
  simp [fibreP, ha, hb, hc, hq, hV, smul_eq_mul] at h
  have hzD : D z = -V^2/(6*z^5) := by
    field_simp
    linear_combination h
  rw [D.leibniz_pow, D.leibniz_inv, hzD]
  simp only [smul_eq_mul, nsmul_eq_mul]
  norm_num
  field_simp

/-- The numerical normalization linking the old coefficient to the b variation. -/
theorem twelve_factor (V z : K) (hz : z ≠ 0) :
    5*V^2/(72*z^11) = (1/12:K)*((5/6:K)*V^2/z^11) := by
  field_simp
  ring

/-- Exact relative fibre reduction of the single b-column; no cohomology space is postulated. -/
theorem b_column_relative_reduction (D : Derivation ℚ K K) (a b c d0 V z : K)
    (ha : D a = 0) (hb : D b = 0) (hc : D c = 0) (hd : D d0 = 0)
    (hV : D V = 1) (hz : z ≠ 0) (hΔ : delta a b c d0 ≠ 0)
    (hcurve : z^6+fibreP a b c d0 V = 0) :
    (5/6:K)*V^2/z^11 =
      (bColumn0 a b c d0+bColumn1 a b c d0*V)/z^5 +
        D (correction a b c d0 V/z^5) := by
  have h2 : D (2 : K) = 0 := D.map_natCast 2
  have h3 : D (3 : K) = 0 := D.map_natCast 3
  have h4 : D (4 : K) = 0 := D.map_natCast 4
  have h9 : D (9 : K) = 0 := D.map_natCast 9
  have h18 : D (18 : K) = 0 := D.map_natCast 18
  have h27 : D (27 : K) = 0 := D.map_natCast 27
  have h := congrArg D hcurve
  simp [fibreP, ha, hb, hc, hd, hV, smul_eq_mul] at h
  have hzD : D z = -fibrePPrime a b c V/(6*z^5) := by
    unfold fibrePPrime
    field_simp
    linear_combination h
  have hΔD : D (delta a b c d0) = 0 := by
    simp [delta, ha, hb, hc, hd, smul_eq_mul, h2, h3, h4, h9, h18, h27]
  have hND : D (rNumerator a b c d0 V) = rNumeratorPrime a b c d0 V := by
    simp [rNumerator, rNumeratorPrime, n1, ha, hb, hc, hd, hV, smul_eq_mul, h2, h3, h4, h9, h18, h27]
    ring
  have hRD : D (correction a b c d0 V) = correctionPrime a b c d0 V := by
    rw [correction, D.leibniz_div_const _ _ hΔD, hND]
    simp only [correctionPrime, smul_eq_mul]
    ring
  have hquot : D (correction a b c d0 V/z^5) =
      correctionPrime a b c d0 V/z^5 +
      (5/6:K)*correction a b c d0 V*fibrePPrime a b c V/z^11 := by
    rw [D.leibniz_div, D.leibniz_pow, hRD, hzD]
    simp only [smul_eq_mul, nsmul_eq_mul]
    norm_num
    field_simp
    ring
  rw [hquot]
  have hred := b_column_rational a b c d0 V hΔ
  have hP : fibreP a b c d0 V = -z^6 := by linear_combination hcurve
  rw [hP] at hred
  field_simp [hz]
  linear_combination 6*hred

end FibreColumn

section ModuleReduction
variable [Algebra ℚ K] {M : Type*} [AddCommGroup M] [Module K M] [Module ℚ M]
  [IsScalarTower ℚ K M]

/-- The same relative identity for an arbitrary module-valued derivation. -/
theorem b_column_module_reduction (D : Derivation ℚ K M) (a b c d0 V z : K)
    (ha : D a = 0) (hb : D b = 0) (hc : D c = 0) (hd : D d0 = 0)
    (hz : z ≠ 0) (hΔ : delta a b c d0 ≠ 0)
    (hcurve : z^6+fibreP a b c d0 V = 0) :
    ((5/6:K)*V^2/z^11) • D V =
      ((bColumn0 a b c d0+bColumn1 a b c d0*V)/z^5) • D V +
        D (correction a b c d0 V/z^5) := by
  have h2 : D (2 : K) = 0 := D.map_natCast 2
  have h3 : D (3 : K) = 0 := D.map_natCast 3
  have h4 : D (4 : K) = 0 := D.map_natCast 4
  have h9 : D (9 : K) = 0 := D.map_natCast 9
  have h18 : D (18 : K) = 0 := D.map_natCast 18
  have h27 : D (27 : K) = 0 := D.map_natCast 27
  have h := congrArg D hcurve
  simp only [map_add, map_zero, fibreP, D.leibniz, D.leibniz_pow, ha, hb, hc, hd,
    zero_smul, smul_zero, add_zero, zero_add, Nat.reduceSub, ← Nat.cast_smul_eq_nsmul K,
    smul_smul] at h
  have hlinear : (6*z^5) • D z = -fibrePPrime a b c V • D V := by
    rw [neg_smul]
    apply eq_neg_of_add_eq_zero_left
    convert h using 1 <;> unfold fibrePPrime <;> module
  have hzD : D z = (-fibrePPrime a b c V/(6*z^5)) • D V := by
    calc
      D z = (6*z^5)⁻¹ • ((6*z^5) • D z) := by
        rw [smul_smul, inv_mul_cancel₀ (mul_ne_zero (by norm_num) (pow_ne_zero _ hz)), one_smul]
      _ = _ := by rw [hlinear, smul_smul]; congr 1; ring
  have hΔD : D (delta a b c d0) = 0 := by
    simp [delta, ha, hb, hc, hd, h4, h18, h27]
  have hND : D (rNumerator a b c d0 V) = rNumeratorPrime a b c d0 V • D V := by
    simp only [rNumerator, rNumeratorPrime, n1, map_add, map_sub, D.leibniz,
      D.leibniz_pow, ha, hb, hc, hd, h2, h3, h9, zero_smul, smul_zero, add_zero,
      zero_add, sub_zero, Nat.reduceSub, ← Nat.cast_smul_eq_nsmul K, smul_smul]
    module
  have hRD : D (correction a b c d0 V) = correctionPrime a b c d0 V • D V := by
    rw [correction, D.leibniz_div_const _ _ hΔD, hND, smul_smul]
    congr 1
    unfold correctionPrime
    ring
  have hquot : D (correction a b c d0 V/z^5) =
      (correctionPrime a b c d0 V/z^5 +
        (5/6:K)*correction a b c d0 V*fibrePPrime a b c V/z^11) • D V := by
    rw [D.leibniz_div, D.leibniz_pow, hRD, hzD]
    simp only [Nat.reduceSub, ← Nat.cast_smul_eq_nsmul K, smul_smul, smul_sub, ← sub_smul]
    congr 1
    field_simp
    ring
  rw [hquot, ← add_smul]
  congr 1
  have hred := b_column_rational a b c d0 V hΔ
  have hP : fibreP a b c d0 V = -z^6 := by linear_combination hcurve
  rw [hP] at hred
  field_simp [hz]
  linear_combination 6*hred

end ModuleReduction

section AbsoluteFourForm
variable [Algebra ℚ K]

/-- Wedge of an actual Kähler differential with the three base differentials. -/
def baseWedge (a v t : K) : Derivation ℚ K (Forms (K := K)) :=
  (LinearMap.mulRight K (d a*(d v*d t))).compDer formD

theorem baseWedge_apply (a v t h : K) :
    baseWedge a v t h = d h*(d a*(d v*d t)) := rfl

theorem baseWedge_a (a v t : K) : baseWedge a v t a = 0 := by
  rw [baseWedge_apply, ← mul_assoc, d_square_zero, zero_mul]

theorem baseWedge_v (a v t : K) : baseWedge a v t v = 0 := by
  rw [baseWedge_apply, ← mul_assoc, d_swap v a, neg_mul, mul_assoc,
    ← mul_assoc (d v), d_square_zero, zero_mul, mul_zero, neg_zero]

theorem baseWedge_t (a v t : K) : baseWedge a v t t = 0 := by
  rw [baseWedge_apply, ← mul_assoc, d_swap t a, neg_mul, mul_assoc,
    ← mul_assoc (d t), d_swap t v, neg_mul, mul_assoc, d_square_zero,
    mul_zero, neg_zero, mul_zero, neg_zero]

theorem chart_base_three (r w t : K) (hr : r ≠ 0) :
    d (aChart r w)*(d (vChart r w)*d t) = jacobian r w • (d r*(d w*d t)) := by
  rw [← mul_assoc, two_form_change r w hr, smul_mul_assoc, mul_assoc]

theorem baseWedge_r (r w t : K) (hr : r ≠ 0) :
    baseWedge (aChart r w) (vChart r w) t r = 0 := by
  rw [baseWedge_apply, chart_base_three r w t hr, mul_smul_comm,
    ← mul_assoc (d r), d_square_zero, zero_mul, smul_zero]

/-- The entire scalar multiplying the b column is constant along the fibre wedge derivation. -/
theorem baseWedge_factor (r w t : K) (hr : r ≠ 0) :
    baseWedge (aChart r w) (vChart r w) t (r^11/fR r w/12) = 0 := by
  let D := baseWedge (aChart r w) (vChart r w) t
  have hrD : D r = 0 := baseWedge_r r w t hr
  have haD : D (aChart r w) = 0 := baseWedge_a _ _ _
  have hvD : D (vChart r w) = 0 := baseWedge_v _ _ _
  have h6 : D (6:K) = 0 := D.map_natCast 6
  have h12 : D (12:K) = 0 := D.map_natCast 12
  have h15 : D (15:K) = 0 := D.map_natCast 15
  have h18 : D (18:K) = 0 := D.map_natCast 18
  have hfD : D (fR r w) = 0 := by
    rw [fR_expanded]
    simp [hrD, haD, hvD, h6, h12, h15, h18]
  change D _ = 0
  simp [D.leibniz_div, hrD, hfD, h12]

/-- Actual four-form representative and one exact correction in the physical chart.
The displayed exact term is d(H) wedge da wedge dv wedge dt; no quotient by exact forms is defined. -/
theorem source_four_form_reduction (U r w t z : K) (hr : r ≠ 0) (hz : z ≠ 0)
    (hf : fR r w ≠ 0)
    (hΔ : delta (aChart r w) (t*vChart r w) (t*(1-t^2)/7) (1+t^6) ≠ 0)
    (hcurve : z^6+cubic U r w t = 0) :
    ResidueNormalization.normalizedPoleCoefficient U r w t z • oldFourForm U r w t =
      ((r^11/fR r w/12)*
        ((bColumn0 (aChart r w) (t*vChart r w) (t*(1-t^2)/7) (1+t^6) +
          bColumn1 (aChart r w) (t*vChart r w) (t*(1-t^2)/7) (1+t^6)*(r*U))/z^5)) •
          newFourForm (r*U) (aChart r w) (vChart r w) t +
      baseWedge (aChart r w) (vChart r w) t
        ((r^11/fR r w/12)*
          (correction (aChart r w) (t*vChart r w) (t*(1-t^2)/7) (1+t^6) (r*U)/z^5)) := by
  let D := baseWedge (aChart r w) (vChart r w) t
  have ha : D (aChart r w) = 0 := baseWedge_a _ _ _
  have hv : D (vChart r w) = 0 := baseWedge_v _ _ _
  have ht : D t = 0 := baseWedge_t _ _ _
  have h7 : D (7:K) = 0 := D.map_natCast 7
  have hb : D (t*vChart r w) = 0 := by simp [ht, hv]
  have hc : D (t*(1-t^2)/7) = 0 := by simp [D.leibniz_div, ht, h7]
  have hd : D (1+t^6) = 0 := by simp [ht]
  have hcancel : (r*U)/r = U := by field_simp
  have hP : cubic U r w t =
      fibreP (aChart r w) (t*vChart r w) (t*(1-t^2)/7) (1+t^6) (r*U) := by
    simpa only [hcancel, fibreP] using cubic_coordinate_change (r*U) r w t hr
  have hnew : z^6+fibreP (aChart r w) (t*vChart r w) (t*(1-t^2)/7) (1+t^6) (r*U) = 0 := by
    rw [← hP]
    exact hcurve
  have hred := b_column_module_reduction D (aChart r w) (t*vChart r w)
    (t*(1-t^2)/7) (1+t^6) (r*U) z ha hb hc hd hz hΔ hnew
  have hfactor : D (r^11/fR r w/12) = 0 := baseWedge_factor r w t hr
  have hexact : D ((r^11/fR r w/12)*
      (correction (aChart r w) (t*vChart r w) (t*(1-t^2)/7) (1+t^6) (r*U)/z^5)) =
      (r^11/fR r w/12) • D
        (correction (aChart r w) (t*vChart r w) (t*(1-t^2)/7) (1+t^6) (r*U)/z^5) := by
    rw [D.leibniz, hfactor, smul_zero, add_zero]
  rw [normalized_source_form_transport U r w t z hr hz hf]
  change _ = _ + D _
  rw [hexact]
  have heq : ((5/72:K)*(r^11/fR r w)*((r*U)^2/z^11)) =
      (r^11/fR r w/12)*((5/6:K)*(r*U)^2/z^11) := by ring
  rw [heq, ← smul_smul]
  change (r^11/fR r w/12) • (((5/6:K)*(r*U)^2/z^11) • D (r*U)) = _
  rw [hred, smul_add, smul_smul]
  rfl

end AbsoluteFourForm

/-- Inverse base-chart coordinate at a root of the physical polynomial. -/
def recoverW (r v : K) : K := (v*r-1)/r^2

theorem vChart_recover (r v : K) (hr : r ≠ 0) : vChart r (recoverW r v) = v := by
  unfold vChart recoverW
  field_simp
  ring

theorem aChart_recover (a v r : K) (hr : r ≠ 0)
    (hroot : (physicalPolynomial a v).eval r = 0) :
    aChart r (recoverW r v) = a := by
  rw [aChart_eq_coverA r _ hr, vChart_recover r v hr]
  simp only [physicalPolynomial, eval_sub, eval_add, eval_pow, eval_mul, eval_C,
    eval_X, eval_one] at hroot
  unfold coverA
  field_simp
  linear_combination hroot

theorem fR_recover (a v r : K) (hr : r ≠ 0)
    (hroot : (physicalPolynomial a v).eval r = 0) :
    fR r (recoverW r v) = (physicalPolynomial a v).derivative.eval r := by
  rw [fR, aChart_recover a v r hr hroot, vChart_recover r v hr]

section QuotientScalar
open GenericDistinctRoots ScalarExtensionTrace

def rootW (j : Fin 18) : SplitField := recoverW (roots j) (baseToSplit genericV)

theorem root_vChart (j : Fin 18) : vChart (roots j) (rootW j) = baseToSplit genericV :=
  vChart_recover _ _ (roots_ne_zero j)

theorem root_aChart (j : Fin 18) : aChart (roots j) (rootW j) = baseToSplit genericA :=
  aChart_recover _ _ _ (roots_ne_zero j) (roots_eval j)

theorem root_fR (j : Fin 18) :
    fR (roots j) (rootW j) =
      (physicalPolynomial (baseToSplit genericA) (baseToSplit genericV)).derivative.eval (roots j) :=
  fR_recover _ _ _ (roots_ne_zero j) (roots_eval j)

theorem root_fR_ne_zero (j : Fin 18) : fR (roots j) (rootW j) ≠ 0 := by
  rw [root_fR]
  exact roots_derivative_ne_zero j

/-- The normalized derivative-weighted quotient element; this is a scalar, not a vector source. -/
def sourceScalar : E := (1/12 : BaseField) • quotientWeight 11

theorem sourceScalar_image (j : Fin 18) :
    sigma j sourceScalar = (roots j)^11/(12*fR (roots j) (rootW j)) := by
  rw [sourceScalar, map_smul]
  simp only [quotientWeight, map_mul, map_pow, sigma_theta, sigma_derivativeInverse]
  rw [root_fR]
  simp only [Algebra.smul_def, map_div₀, map_one, map_ofNat]
  norm_num
  rw [map_ofNat (algebraMap BaseField SplitField) 12]
  ring

theorem sourceScalar_trace : Algebra.trace BaseField E sourceScalar = 0 := by
  rw [sourceScalar, map_smul, trace_slot_eleven, smul_zero]

end QuotientScalar

end HodgeLab.OneReflectionSkew.PhysicalSourceNormalization

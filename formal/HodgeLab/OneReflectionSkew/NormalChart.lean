import HodgeLab.OneReflectionSkew.VolumeDensity

/-! The actual chart polynomial and its normal derivative. The determinant
coefficient model uses the ordered variables (U,r,w,t,z); no base variable
is frozen. It records the sign of a covector wedged before dU,dr,dw,dt.
No general differential-form or residue API is asserted. -/

namespace HodgeLab.OneReflectionSkew.NormalChart
open ChartSubstitution CoordinateVolume VolumeDensity
variable {K : Type*} [Field K] [CharZero K]

noncomputable def chartPolynomial : MvPolynomial (Fin 5) K :=
  (MvPolynomial.X 4)^6 +
  (1 + (MvPolynomial.X 1)^6 + (MvPolynomial.X 2)^6) * (MvPolynomial.X 0)^3 +
  MvPolynomial.X 1 * MvPolynomial.X 3 *
    (1 + (MvPolynomial.X 1)^2 * MvPolynomial.X 2) * (MvPolynomial.X 0)^2 +
  MvPolynomial.C ((1 : K)/7) * MvPolynomial.X 1 * MvPolynomial.X 3 *
    (1 - (MvPolynomial.X 3)^2) * MvPolynomial.X 0 +
  (1 + (MvPolynomial.X 3)^6)

theorem chartPolynomial_eval (U r w t z : K) :
    MvPolynomial.eval (chartPoint U r w t z) chartPolynomial =
      chartDenominator U r w t z := by
  simp [chartPolynomial, chartPoint, chartDenominator, cubic,
    aCoeff, bCoeff, cCoeff, dCoeff]
  ring

omit [CharZero K] in
theorem chartPolynomial_pderiv :
    MvPolynomial.pderiv (4 : Fin 5) (chartPolynomial (K := K)) =
      6 * (MvPolynomial.X 4)^5 := by
  simp [chartPolynomial]

noncomputable def normalDerivative (U r w t z : K) : K :=
  MvPolynomial.eval (chartPoint U r w t z)
    (MvPolynomial.pderiv (4 : Fin 5) chartPolynomial)

omit [CharZero K] in
theorem normalDerivative_eq (U r w t z : K) :
    normalDerivative U r w t z = 6*z^5 := by
  rw [normalDerivative, chartPolynomial_pderiv]
  simp [chartPoint]

/-- The determinant is the alternating coefficient of a covector followed
by the four ordered base-coordinate covectors. -/
def coefficientMatrix (v : Fin 5 → K) : Matrix (Fin 5) (Fin 5) K :=
  !![v 0,v 1,v 2,v 3,v 4;
     1,0,0,0,0; 0,1,0,0,0; 0,0,1,0,0; 0,0,0,1,0]

omit [CharZero K] in
theorem coefficientMatrix_det (v : Fin 5 → K) :
    (coefficientMatrix v).det = v 4 := by
  simp [coefficientMatrix, Matrix.det_succ_row_zero, Fin.sum_univ_succ,
    Matrix.submatrix, Matrix.det_unique, Fin.succAbove]
  ring

/-- All four base partials remain in this actual gradient. -/
noncomputable def gradient (U r w t z : K) : Fin 5 → K :=
  fun i => MvPolynomial.eval (chartPoint U r w t z)
    (MvPolynomial.pderiv i chartPolynomial)

omit [CharZero K] in
theorem gradient_volume_coefficient (U r w t z : K) :
    (coefficientMatrix (gradient U r w t z)).det = 6*z^5 := by
  rw [coefficientMatrix_det]
  exact normalDerivative_eq U r w t z

omit [CharZero K] in
theorem coefficientMatrix_scaled (c : K) (v : Fin 5 → K) :
    (coefficientMatrix (fun i => c * v i)).det = c * v 4 := by
  rw [coefficientMatrix_det]

omit [CharZero K] in
theorem base_covector_vanishes (v : Fin 5 → K) (hv : v 4 = 0) :
    (coefficientMatrix v).det = 0 := by
  rw [coefficientMatrix_det, hv]

noncomputable def normalCoordinates : Fin 5 → MvPolynomial (Fin 5) K :=
  ![MvPolynomial.X 0, MvPolynomial.X 1, MvPolynomial.X 2,
    MvPolynomial.X 3, chartPolynomial]

noncomputable def normalJacobian (U r w t z : K) : Matrix (Fin 5) (Fin 5) K :=
  fun i j => MvPolynomial.eval (chartPoint U r w t z)
    (MvPolynomial.pderiv j (normalCoordinates i))

omit [CharZero K] in
theorem normalJacobian_entries (U r w t z : K) :
    normalJacobian U r w t z =
      !![1,0,0,0,0; 0,1,0,0,0; 0,0,1,0,0; 0,0,0,1,0;
         gradient U r w t z 0, gradient U r w t z 1,
         gradient U r w t z 2, gradient U r w t z 3,
         gradient U r w t z 4] := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [normalJacobian, normalCoordinates, gradient, chartPoint]

omit [CharZero K] in
theorem normalJacobian_det (U r w t z : K) :
    (normalJacobian U r w t z).det = 6*z^5 := by
  rw [normalJacobian_entries]
  simp [Matrix.det_succ_row_zero, Fin.sum_univ_succ, Matrix.submatrix,
    Matrix.det_unique]
  exact normalDerivative_eq U r w t z

theorem normalDerivative_ne_zero_iff (U r w t z : K) :
    normalDerivative U r w t z ≠ 0 ↔ z ≠ 0 := by
  rw [normalDerivative_eq]
  simp

theorem normalJacobian_ne_zero_iff (U r w t z : K) :
    (normalJacobian U r w t z).det ≠ 0 ↔ z ≠ 0 := by
  rw [normalJacobian_det]
  simp

end HodgeLab.OneReflectionSkew.NormalChart

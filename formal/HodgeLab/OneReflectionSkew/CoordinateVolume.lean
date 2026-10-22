import HodgeLab.OneReflectionSkew.ChartSubstitution
import Mathlib.LinearAlgebra.Matrix.Determinant.Basic

/-! Coordinate volume identities from differentiated coordinate polynomials.
The variables are (x,r,w,t,z), physical rows are (X0,X1,X2,Y0,Y1,Y2).
No inverse-chart or residue theorem is asserted. -/

namespace HodgeLab.OneReflectionSkew.CoordinateVolume
open ChartSubstitution
variable {K : Type*} [Field K]

def chartPoint (x r w t z : K) : Fin 5 → K := ![x,r,w,t,z]

noncomputable def physicalCoordinates : Fin 6 → MvPolynomial (Fin 5) K :=
  ![MvPolynomial.X 0, MvPolynomial.X 1 * MvPolynomial.X 0,
    MvPolynomial.X 2 * MvPolynomial.X 0, 1, MvPolynomial.X 3, MvPolynomial.X 4]

theorem physicalCoordinates_eval (x r w t z : K) :
    (fun i => MvPolynomial.eval (chartPoint x r w t z) (physicalCoordinates i)) =
      physicalPoint x r w t z := by
  funext i
  fin_cases i <;> simp [physicalCoordinates, chartPoint, physicalPoint]

noncomputable def physicalJacobian (x r w t z : K) : Matrix (Fin 6) (Fin 5) K :=
  fun i j => MvPolynomial.eval (chartPoint x r w t z)
    (MvPolynomial.pderiv j (physicalCoordinates i))

theorem physicalJacobian_entries (x r w t z : K) :
    physicalJacobian x r w t z =
      !![1,0,0,0,0; r,x,0,0,0; w,0,x,0,0; 0,0,0,0,0;
         0,0,0,1,0; 0,0,0,0,1] := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [physicalJacobian, physicalCoordinates, chartPoint]

def affineRows : Fin 5 → Fin 6 := ![0,1,2,4,5]
noncomputable def affineJacobian (x r w t z : K) : Matrix (Fin 5) (Fin 5) K :=
  (physicalJacobian x r w t z).submatrix affineRows id

theorem affineJacobian_entries (x r w t z : K) :
    affineJacobian x r w t z =
      !![1,0,0,0,0; r,x,0,0,0; w,0,x,0,0; 0,0,0,1,0; 0,0,0,0,1] := by
  rw [affineJacobian, physicalJacobian_entries]
  ext i j
  fin_cases i <;> fin_cases j <;> simp [affineRows, Matrix.submatrix]

theorem affineJacobian_det (x r w t z : K) :
    (affineJacobian x r w t z).det = x^2 := by
  rw [affineJacobian_entries]
  simp [Matrix.det_succ_row_zero, Fin.sum_univ_succ, Matrix.submatrix, Matrix.det_unique]
  ring

noncomputable def squareCoordinates : Fin 5 → MvPolynomial (Fin 5) K :=
  ![(MvPolynomial.X 0)^2, MvPolynomial.X 1, MvPolynomial.X 2,
    MvPolynomial.X 3, MvPolynomial.X 4]

theorem squareCoordinates_eval (x r w t z : K) :
    (fun i => MvPolynomial.eval (chartPoint x r w t z) (squareCoordinates i)) =
      ![x^2,r,w,t,z] := by
  funext i
  fin_cases i <;> simp [squareCoordinates, chartPoint]

noncomputable def squareJacobian (x r w t z : K) : Matrix (Fin 5) (Fin 5) K :=
  fun i j => MvPolynomial.eval (chartPoint x r w t z)
    (MvPolynomial.pderiv j (squareCoordinates i))

theorem squareJacobian_entries (x r w t z : K) :
    squareJacobian x r w t z = Matrix.diagonal ![2*x,1,1,1,1] := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [squareJacobian, squareCoordinates, chartPoint, Matrix.diagonal]

theorem squareJacobian_det (x r w t z : K) :
    (squareJacobian x r w t z).det = 2*x := by
  rw [squareJacobian_entries, Matrix.det_diagonal]
  simp [Fin.prod_univ_succ]

/-- The projective Euler volume evaluated on the point and five coordinate
tangent columns, in the protected physical row order. -/
noncomputable def omegaMatrix (x r w t z : K) : Matrix (Fin 6) (Fin 6) K :=
  fun i j => Fin.cases
    (MvPolynomial.eval (chartPoint x r w t z) (physicalCoordinates i))
    (fun k => physicalJacobian x r w t z i k) j

theorem omegaMatrix_entries (x r w t z : K) :
    omegaMatrix x r w t z =
      !![x,1,0,0,0,0; r*x,r,x,0,0,0; w*x,w,0,x,0,0;
         1,0,0,0,0,0; t,0,0,0,1,0; z,0,0,0,0,1] := by
  ext i j
  simp only [omegaMatrix, physicalJacobian_entries]
  have h := congrFun (physicalCoordinates_eval x r w t z) i
  rw [h]
  fin_cases i <;> fin_cases j <;> rfl

theorem omegaMatrix_minor (x r w t z : K) :
    (omegaMatrix x r w t z).submatrix (3 : Fin 6).succAbove Fin.succ =
      affineJacobian x r w t z := by
  rw [omegaMatrix_entries, affineJacobian_entries]
  ext i j
  fin_cases i <;> fin_cases j <;> simp [Matrix.submatrix, Fin.succAbove]

theorem omegaMatrix_det (x r w t z : K) :
    (omegaMatrix x r w t z).det = -(x^2) := by
  rw [Matrix.det_succ_row _ (3 : Fin 6)]
  have hrow : ∀ j : Fin 6, omegaMatrix x r w t z 3 j = if j = 0 then 1 else 0 := by
    intro j
    rw [omegaMatrix_entries]
    fin_cases j <;> simp
  simp only [hrow]
  simp [omegaMatrix_minor, affineJacobian_det]
  ring

end HodgeLab.OneReflectionSkew.CoordinateVolume

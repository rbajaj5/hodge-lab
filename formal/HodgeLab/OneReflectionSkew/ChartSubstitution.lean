import HodgeLab.OneReflectionSkew.CoordinateComparison
import HodgeLab.OneReflectionSkew.DegreeFour
import Mathlib.Algebra.MvPolynomial.CommRing

/-! Polynomial substitution from the protected one-reflection-skew equation
to the actual chart polynomial used by the degree-four Lean obstruction.
This is a coordinate identity, not a differential-form normalization. -/

namespace HodgeLab.OneReflectionSkew.ChartSubstitution
open HodgeLab.SparsePolynomial
open CoordinateComparison

variable {K : Type*} [Field K] [CharZero K]

def physicalPoint (x r w t z : K) : Fin 6 → K := ![x,r*x,w*x,1,t,z]
def polynomialPoint (U r w t : K) : Fin 5 → K := ![U,r,w,t,0]

def aCoeff (r w : K) : K := 1 + r^6 + w^6
def bCoeff (r w t : K) : K := r*t*(1+r^2*w)
def cCoeff (r t : K) : K := r*t*(1-t^2)/7
def dCoeff (t : K) : K := 1+t^6

def cubic (U r w t : K) : K :=
  aCoeff r w * U^3 + bCoeff r w t * U^2 + cCoeff r t * U + dCoeff t

theorem eval_a (U r w t : K) :
    MvPolynomial.eval₂ (Rat.castHom K) (polynomialPoint U r w t) a =
      aCoeff r w := by
  simp [a, aSparse, eval, MvPolynomial.eval₂_monomial,
    Finsupp.prod_fintype, Fin.prod_univ_succ, exp, polynomialPoint, aCoeff, add_assoc]

theorem eval_aOver (U r w t : K) :
    MvPolynomial.eval (polynomialPoint U r w t) (aOver K) = aCoeff r w := by
  rw [aOver, MvPolynomial.eval_map]
  exact eval_a U r w t

/-- Binding to the existing sparse polynomial, including its normalization by seven. -/
theorem eval_p7 (U r w t : K) :
    MvPolynomial.eval₂ (Rat.castHom K) (polynomialPoint U r w t) p7 =
      7 * cubic U r w t := by
  simp [p7, p7Sparse, eval, MvPolynomial.eval₂_monomial, MvPolynomial.eval₂_neg,
    Finsupp.prod_fintype, Fin.prod_univ_succ, exp, polynomialPoint,
    cubic, aCoeff, bCoeff, cCoeff, dCoeff]
  ring

theorem protected_substitution (x r w t z : K) :
    skewF (physicalPoint x r w t z) = z^6 + cubic (x^2) r w t := by
  simp [skewF, physicalPoint, cubic, aCoeff, bCoeff, cCoeff, dCoeff]
  ring

omit [CharZero K] in
theorem protected_source_substitution (x r w t z : K) :
    skewA (physicalPoint x r w t z) = x^3 := by
  simp [skewA, physicalPoint]

/-- The protected sextic is bound to the exact polynomial used in the prior
Lean operator, rather than merely to another displayed cubic formula. -/
theorem protected_substitution_p7 (x r w t z : K) :
    7 * skewF (physicalPoint x r w t z) =
      7*z^6 + MvPolynomial.eval₂ (Rat.castHom K)
        (polynomialPoint (x^2) r w t) p7 := by
  rw [eval_p7, protected_substitution]
  ring

theorem eval_p7Over (U r w t : K) :
    MvPolynomial.eval (polynomialPoint U r w t) (p7Over K) =
      7 * cubic U r w t := by
  rw [p7Over, MvPolynomial.eval_map]
  exact eval_p7 U r w t

theorem protected_substitution_p7Over (x r w t z : K) :
    7 * skewF (physicalPoint x r w t z) =
      7*z^6 + MvPolynomial.eval (polynomialPoint (x^2) r w t) (p7Over K) := by
  rw [eval_p7Over, protected_substitution]
  ring

end HodgeLab.OneReflectionSkew.ChartSubstitution

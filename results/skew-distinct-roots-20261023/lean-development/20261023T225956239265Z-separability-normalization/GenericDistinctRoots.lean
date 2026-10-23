import HodgeLab.OneReflectionSkew.PhysicalCoverBinding
import Mathlib.FieldTheory.RatFunc.AsPolynomial
import Mathlib.FieldTheory.IsAlgClosed.AlgebraicClosure
import Mathlib.FieldTheory.SplittingField.Construction
import Mathlib.RingTheory.Algebraic.Integral
import Mathlib.Data.Fintype.EquivFin

/-!
Generic distinct roots for the physical degree-18 cover.  The explicit base is
Q(v)(t)(a), constructed by three rational-function fields.  Separability is
proved from transcendence of a by eliminating a from f and its derivative.
This does not assert distinctness in every specialization.
-/
noncomputable section

namespace HodgeLab.OneReflectionSkew.GenericDistinctRoots

open Polynomial PhysicalCoverBinding TraceFreeBasis SplitTraceQuotient

section Eliminant

variable {k : Type*} [Field k]

def eliminant (v : k) : k[X] :=
  3 * X ^ 18 - 3 * X ^ 12 + (C v * X - 1) ^ 5 * (15 - 9 * C v * X)

theorem eliminant_identity (a v : k) :
    X * (physicalPolynomial a v).derivative - 15 * physicalPolynomial a v = eliminant v := by
  simp only [physicalPolynomial, eliminant, derivative_add, derivative_sub, derivative_pow,
    derivative_mul, derivative_C, derivative_X, derivative_one]
  simp only [map_natCast]
  norm_num
  ring

theorem eliminant_at_zero (v : k) : (eliminant v).eval 0 = -15 := by
  norm_num [eliminant]

theorem eliminant_ne_zero [CharZero k] (v : k) : eliminant v ≠ 0 := by
  intro h
  have := congrArg (Polynomial.eval (0 : k)) h
  rw [eliminant_at_zero, eval_zero] at this
  norm_num at this

variable {L : Type*} [Field L] [Algebra k L]

theorem eliminant_map (v : k) :
    (eliminant v).map (algebraMap k L) = eliminant (algebraMap k L v) := by
  simp [eliminant]

/-- A common root makes the parameter algebraic over the field of v. -/
theorem common_root_parameter_algebraic [CharZero k] (a : L) (v : k) (r : L)
    (hr : (physicalPolynomial a (algebraMap k L v)).eval r = 0)
    (hdr : (physicalPolynomial a (algebraMap k L v)).derivative.eval r = 0) :
    IsAlgebraic k a := by
  have hr0 : r ≠ 0 := by
    intro h
    subst r
    norm_num [physicalPolynomial] at hr
  have hd : aeval r (eliminant v) = 0 := by
    rw [← eval_map_algebraMap, eliminant_map, ← eliminant_identity a]
    simp only [eval_sub, eval_mul, eval_X, hr, hdr, mul_zero, sub_self]
  have halg : IsAlgebraic k r := ⟨eliminant v, eliminant_ne_zero v, hd⟩
  have hv : IsAlgebraic k (algebraMap k L v) := isAlgebraic_algebraMap v
  have heq : r ^ 15 * a = r ^ 18 + r ^ 12 + (algebraMap k L v * r - 1) ^ 6 := by
    simp only [physicalPolynomial, eval_sub, eval_add, eval_pow, eval_mul, eval_C,
      eval_X, eval_one] at hr
    linear_combination -hr
  apply IsAlgebraic.of_mul (mem_nonZeroDivisors_of_ne_zero (pow_ne_zero 15 hr0)) (halg.pow 15)
  rw [heq]
  exact ((halg.pow 18).add (halg.pow 12)).add (((hv.mul halg).sub isAlgebraic_one).pow 6)

/-- Transcendence of a rules out a root shared by f and f'. -/
theorem root_derivative_ne_zero [CharZero k] (a : L) (v : k)
    (ha : Transcendental k a) (r : L)
    (hr : (physicalPolynomial a (algebraMap k L v)).eval r = 0) :
    (physicalPolynomial a (algebraMap k L v)).derivative.eval r ≠ 0 := by
  intro hdr
  exact ha (common_root_parameter_algebraic a v r hr hdr)

end Eliminant

section Separability

variable {k K L : Type*} [Field k] [Field K] [Field L]

theorem physical_map (φ : K →+* L) (a v : K) :
    (physicalPolynomial a v).map φ = physicalPolynomial (φ a) (φ v) := by
  simp [physicalPolynomial]

/-- The parameter a is transcendental; v may be any element of k. -/
theorem physical_separable_of_transcendental [CharZero k] [Algebra k K]
    (a : K) (v : k) (ha : Transcendental k a) :
    (physicalPolynomial a (algebraMap k K v)).Separable := by
  rw [separable_def]
  apply (isCoprime_iff_aeval_ne_zero_of_isAlgClosed (AlgebraicClosure K) _ _).2
  intro r
  by_cases hr : aeval r (physicalPolynomial a (algebraMap k K v)) = 0
  · right
    have ha' : Transcendental k (algebraMap K (AlgebraicClosure K) a) :=
      (transcendental_algebraMap_iff (RingHom.injective _)).2 ha
    have hr' : (physicalPolynomial (algebraMap K (AlgebraicClosure K) a)
        (algebraMap k (AlgebraicClosure K) v)).eval r = 0 := by
      simpa only [← eval_map_algebraMap, physical_map,
        ← IsScalarTower.algebraMap_apply k K (AlgebraicClosure K)] using hr
    have hd := root_derivative_ne_zero (algebraMap K (AlgebraicClosure K) a) v ha' r hr'
    simpa only [← eval_map_algebraMap, ← derivative_map, physical_map,
      ← IsScalarTower.algebraMap_apply k K (AlgebraicClosure K)] using hd
  · exact Or.inl hr

end Separability

end HodgeLab.OneReflectionSkew.GenericDistinctRoots

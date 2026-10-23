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
  apply (isCoprime_iff_aeval_ne_zero_of_isAlgClosed K (AlgebraicClosure K) _ _).2
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

/-- The innermost independent indeterminate is v. -/
abbrev VField := RatFunc ℚ
/-- The middle independent indeterminate is t; k = Q(v)(t). -/
abbrev CoeffField := RatFunc VField
/-- The outer independent indeterminate is a; K = Q(v)(t)(a). -/
abbrev BaseField := RatFunc CoeffField

def vInVField : VField := RatFunc.X
def tInCoeffField : CoeffField := RatFunc.X
def vInCoeffField : CoeffField := algebraMap VField CoeffField vInVField
def genericA : BaseField := RatFunc.X
def genericV : BaseField := algebraMap CoeffField BaseField vInCoeffField
def genericT : BaseField := algebraMap CoeffField BaseField tInCoeffField

theorem v_transcendental : Transcendental ℚ vInVField := by
  have h := RatFunc.transcendental_X (K := ℚ)
  convert h using 1
theorem t_transcendental : Transcendental VField tInCoeffField := RatFunc.transcendental_X
theorem a_transcendental : Transcendental CoeffField genericA := RatFunc.transcendental_X

def genericPolynomial : BaseField[X] := physicalPolynomial genericA genericV

theorem generic_separable : genericPolynomial.Separable :=
  physical_separable_of_transcendental genericA vInCoeffField a_transcendental

theorem generic_degree : genericPolynomial.natDegree = 18 :=
  physical_degree genericA genericV

/-- The full splitting field of f over K, not a single-root extension. -/
abbrev SplitField := genericPolynomial.SplittingField

def coefficientToBase : CoeffField →+* BaseField := algebraMap CoeffField BaseField
def baseToSplit : BaseField →+* SplitField := algebraMap BaseField SplitField
def coefficientToSplit : CoeffField →+* SplitField := algebraMap CoeffField SplitField

private theorem field_embedding_injective {F E : Type*} [Field F] [Field E]
    (φ : F →+* E) : Function.Injective φ := RingHom.injective φ

theorem coefficientToBase_injective : Function.Injective coefficientToBase :=
  field_embedding_injective _
theorem baseToSplit_injective : Function.Injective baseToSplit := field_embedding_injective _
theorem coefficientToSplit_injective : Function.Injective coefficientToSplit :=
  field_embedding_injective _

theorem coefficient_map_compatibility (c : CoeffField) :
    coefficientToSplit c = baseToSplit (coefficientToBase c) :=
  IsScalarTower.algebraMap_apply CoeffField BaseField SplitField c

theorem a_transcendental_in_split :
    Transcendental CoeffField (baseToSplit genericA) :=
  (transcendental_algebraMap_iff (field_embedding_injective (algebraMap BaseField SplitField))).2
    a_transcendental

theorem generic_splits : (genericPolynomial.map baseToSplit).Splits :=
  Polynomial.SplittingField.splits genericPolynomial

theorem physical_polynomial_map :
    genericPolynomial.map baseToSplit =
      physicalPolynomial (baseToSplit genericA) (baseToSplit genericV) :=
  physical_map baseToSplit genericA genericV

theorem generic_root_card : Fintype.card (genericPolynomial.rootSet SplitField) = 18 := by
  rw [card_rootSet_eq_natDegree generic_separable generic_splits]
  exact generic_degree

def rootEquiv : genericPolynomial.rootSet SplitField ≃ Fin 18 :=
  Fintype.equivFinOfCardEq generic_root_card

/-- Noncomputable enumeration of all eighteen distinct roots in the specified splitting field. -/
def roots (j : Fin 18) : SplitField := (rootEquiv.symm j).val

theorem roots_injective : Function.Injective roots :=
  Subtype.val_injective.comp rootEquiv.symm.injective

theorem roots_aeval (j : Fin 18) : aeval (roots j) genericPolynomial = 0 :=
  aeval_eq_zero_of_mem_rootSet (rootEquiv.symm j).property

theorem roots_eval (j : Fin 18) :
    (physicalPolynomial (baseToSplit genericA) (baseToSplit genericV)).eval (roots j) = 0 := by
  rw [← physical_polynomial_map, baseToSplit, eval_map_algebraMap]
  exact roots_aeval j

theorem roots_ne_zero (j : Fin 18) : roots j ≠ 0 := by
  intro h
  have hr := roots_eval j
  rw [h] at hr
  norm_num [physicalPolynomial] at hr

theorem roots_derivative_ne_zero (j : Fin 18) :
    (physicalPolynomial (baseToSplit genericA) (baseToSplit genericV)).derivative.eval
      (roots j) ≠ 0 := by
  rw [← physical_polynomial_map, derivative_map, baseToSplit, eval_map_algebraMap]
  exact generic_separable.aeval_derivative_ne_zero (roots_aeval j)

/-- The previous conditional physical binding is instantiated by the constructed tuple. -/
theorem generic_eq_split_cover :
    physicalPolynomial (baseToSplit genericA) (baseToSplit genericV) =
      coverPolynomial 1 roots :=
  physical_eq_split_cover _ _ roots roots_injective roots_eval

/-- Reuse of the previous trace-one corollary over the specified splitting field. -/
theorem generic_trace_last :
    Algebra.trace SplitField (SplitAlgebra SplitField)
      (fun j => roots j ^ 17 /
        (physicalPolynomial (baseToSplit genericA) (baseToSplit genericV)).derivative.eval
          (roots j)) = 1 :=
  physical_trace_last _ _ roots roots_injective roots_eval

/-- This is a trace-zero vector, with no differential source normalization claim. -/
theorem generic_trace_slot_eleven :
    Algebra.trace SplitField (SplitAlgebra SplitField)
      (fun j => roots j ^ 11 /
        (physicalPolynomial (baseToSplit genericA) (baseToSplit genericV)).derivative.eval
          (roots j)) = 0 :=
  physical_trace_slot_eleven _ _ roots roots_injective roots_eval

/-- A retained specialization obstruction: generic distinctness is not universal. -/
theorem repeated_specialization :
    (physicalPolynomial (2 : ℚ) 1).eval 1 = 0 ∧
    (physicalPolynomial (2 : ℚ) 1).derivative.eval 1 = 0 := by
  constructor <;> norm_num [physicalPolynomial, derivative_pow]

theorem repeated_specialization_not_separable :
    ¬ (physicalPolynomial (2 : ℚ) 1).Separable := by
  intro h
  exact h.eval₂_derivative_ne_zero (RingHom.id ℚ) repeated_specialization.1
    repeated_specialization.2

end HodgeLab.OneReflectionSkew.GenericDistinctRoots

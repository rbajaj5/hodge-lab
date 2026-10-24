import HodgeLab.OneReflectionSkew.PhysicalCurveRealization
import Mathlib.RingTheory.AlgebraicIndependent.TranscendenceBasis
import Mathlib.RingTheory.AlgebraicIndependent.AlgebraicClosure
import Mathlib.RingTheory.AlgebraicIndependent.Adjoin
import Mathlib.FieldTheory.RatFunc.IntermediateField
import Mathlib.Algebra.Module.Rat

/-! Actual coefficient-field and finite-algebra bridge to the physical curve.
The regular-localization/form boundary of PhysicalCurveRealization is unchanged. -/
set_option backward.isDefEq.respectTransparency false
noncomputable section
namespace HodgeLab.OneReflectionSkew.PhysicalTraceBridge
open Polynomial PhysicalCoverBinding PhysicalSourceNormalization
open PhysicalCurveRealization
open scoped TensorProduct BigOperators

abbrev L := PhysicalCurveRealization.Curve

def physicalA : L := aChart r w
def physicalV : L := vChart r w

def transformed : Fin 4 → L := ![U,physicalA,physicalV,t]
abbrev ChartField := IntermediateField.adjoin ℚ (Set.range transformed)

theorem original_basis : IsTranscendenceBasis ℚ param := by
  letI : Algebra.IsAlgebraic BasePoly Base :=
    IsLocalization.isAlgebraic Base (nonZeroDivisors BasePoly)
  have h := ((IsTranscendenceBasis.mvPolynomial (Fin 4) ℚ).algebraMap_comp
    (A := Base)).algebraMap_comp (A := L)
  convert h using 1
  funext i
  exact (IsScalarTower.algebraMap_apply BasePoly Base L (MvPolynomial.X i)).symm

theorem transformed_mem (i : Fin 4) : transformed i ∈ ChartField :=
  IntermediateField.subset_adjoin ℚ _ ⟨i,rfl⟩

def chartA : ChartField := ⟨physicalA, transformed_mem 1⟩
def chartV : ChartField := ⟨physicalV, transformed_mem 2⟩

theorem physical_r_root : (physicalPolynomial physicalA physicalV).eval r = 0 :=
  physical_cover_equation r w (param_ne_zero 1)

theorem r_algebraic_chart : IsAlgebraic ChartField r := by
  refine ⟨physicalPolynomial chartA chartV, (physical_monic _ _).ne_zero, ?_⟩
  rw [← eval_map_algebraMap, GenericDistinctRoots.physical_map]
  exact physical_r_root

theorem w_algebraic_chart : IsAlgebraic ChartField w := by
  have hv : IsAlgebraic ChartField physicalV := isAlgebraic_algebraMap chartV
  have h := ((hv.mul r_algebraic_chart).sub isAlgebraic_one).mul
    (IsAlgebraic.inv_iff.mpr (r_algebraic_chart.pow 2))
  rw [← div_eq_mul_inv, show (physicalV*r-1)/r^2=w from vChart_inverse r w (param_ne_zero 1)] at h
  exact h

theorem parameters_algebraic_chart (i : Fin 4) : IsAlgebraic ChartField (param i) := by
  fin_cases i
  · exact isAlgebraic_algebraMap (⟨U,transformed_mem 0⟩ : ChartField)
  · exact r_algebraic_chart
  · exact w_algebraic_chart
  · exact isAlgebraic_algebraMap (⟨t,transformed_mem 3⟩ : ChartField)

theorem transformed_basis : IsTranscendenceBasis ℚ transformed := by
  letI : Algebra.IsAlgebraic ChartField L := original_basis.isAlgebraic_iff.mpr parameters_algebraic_chart
  letI : Algebra.IsAlgebraic (Algebra.adjoin ℚ (Set.range transformed)) L :=
    IntermediateField.isAlgebraic_adjoin_iff_top.mp inferInstance
  exact Algebra.IsAlgebraic.isTranscendenceBasis_of_le_trdeg_of_finite ℚ transformed
    parameters_independent.cardinalMk_le_trdeg

theorem transformed_independent : AlgebraicIndependent ℚ transformed := transformed_basis.1

def physicalBaseCoords : Fin 3 → L := ![physicalA,physicalV,t]

theorem physical_base_independent : AlgebraicIndependent ℚ physicalBaseCoords := by
  have h := transformed_independent.comp (fun i : Fin 3 => i.succ) (Fin.succ_injective 3)
  simpa [transformed,physicalBaseCoords,Function.comp_def] using h



open GenericDistinctRoots

local instance vRationalAlgebra : Algebra ℚ VField := RatFunc.instAlgebraOfPolynomial ℚ ℚ
local instance coeffRationalAlgebra : Algebra ℚ CoeffField := RatFunc.instAlgebraOfPolynomial VField ℚ
local instance baseRationalAlgebra : Algebra ℚ BaseField := RatFunc.instAlgebraOfPolynomial CoeffField ℚ
instance qVCoeffTower : IsScalarTower ℚ VField CoeffField := IsScalarTower.rat
instance qCoeffBaseTower : IsScalarTower ℚ CoeffField BaseField := IsScalarTower.rat (R := CoeffField) (M := BaseField)
instance qVBaseTower : IsScalarTower ℚ VField BaseField := IsScalarTower.rat (R := VField) (M := BaseField)

def genericBaseCoords : Fin 3 → BaseField := ![genericA,genericV,genericT]

def coordinateIndex : Fin 3 → Fin 1 ⊕ (Fin 1 ⊕ Fin 1) :=
  ![Sum.inl 0,Sum.inr (Sum.inr 0),Sum.inr (Sum.inl 0)]

theorem coordinateIndex_injective : Function.Injective coordinateIndex := by
  intro i j h
  fin_cases i <;> fin_cases j <;> simp_all [coordinateIndex]

theorem generic_base_independent : AlgebraicIndependent ℚ genericBaseCoords := by
  have hv : AlgebraicIndependent ℚ ![vInVField] :=
    algebraicIndependent_iff_transcendental.mpr RatFunc.transcendental_X
  have ht : AlgebraicIndependent VField ![tInCoeffField] :=
    algebraicIndependent_iff_transcendental.mpr t_transcendental
  have ha : AlgebraicIndependent CoeffField ![genericA] :=
    algebraicIndependent_iff_transcendental.mpr a_transcendental
  have h := (hv.sumElim_comp ht).sumElim_comp ha
  have hh := h.comp coordinateIndex coordinateIndex_injective
  convert hh using 1
  ext i
  fin_cases i <;> simp [genericBaseCoords,coordinateIndex,Function.comp_def,
    genericV,genericT,vInCoeffField]

/-- A subfield containing coefficients and X contains every rational function. -/
theorem ratfunc_image_mem {F M : Type*} [Field F] [Field M]
    (S : Subfield M) (φ : RatFunc F →+* M)
    (hc : ∀ c : F, φ (algebraMap F (RatFunc F) c) ∈ S)
    (hx : φ RatFunc.X ∈ S) (x : RatFunc F) : φ x ∈ S := by
  have h : (IntermediateField.adjoin F ({RatFunc.X} : Set (RatFunc F))).toSubfield ≤
      S.comap φ := IntermediateField.adjoin_le_subfield F _
        (by rintro _ ⟨c,rfl⟩; exact hc c) (by rintro _ rfl; exact hx)
  rw [RatFunc.adjoin_X] at h
  exact h (by trivial)

abbrev GenericCoordinateField := IntermediateField.adjoin ℚ (Set.range genericBaseCoords)

theorem generic_coordinate_mem (i : Fin 3) : genericBaseCoords i ∈ GenericCoordinateField :=
  IntermediateField.subset_adjoin ℚ _ ⟨i,rfl⟩

theorem generic_vfield_mem (x : VField) :
    algebraMap VField BaseField x ∈ GenericCoordinateField := by
  apply ratfunc_image_mem GenericCoordinateField.toSubfield (algebraMap VField BaseField)
  · intro c
    rw [RingHom.map_rat_algebraMap]
    exact GenericCoordinateField.algebraMap_mem c
  · change (algebraMap VField BaseField) RatFunc.X ∈ GenericCoordinateField
    have h := generic_coordinate_mem 1
    change algebraMap CoeffField BaseField (algebraMap VField CoeffField RatFunc.X) ∈
      GenericCoordinateField at h
    rwa [← IsScalarTower.algebraMap_apply] at h

theorem generic_coefffield_mem (x : CoeffField) :
    algebraMap CoeffField BaseField x ∈ GenericCoordinateField := by
  apply ratfunc_image_mem GenericCoordinateField.toSubfield (algebraMap CoeffField BaseField)
  · intro c
    rw [← IsScalarTower.algebraMap_apply]
    exact generic_vfield_mem c
  · exact generic_coordinate_mem 2

theorem generic_coordinate_field_top : GenericCoordinateField = ⊤ := by
  apply top_unique
  intro x _
  exact ratfunc_image_mem GenericCoordinateField.toSubfield (RingHom.id BaseField)
    generic_coefffield_mem (generic_coordinate_mem 0) x

abbrev CoordinateFractions := FractionRing (MvPolynomial (Fin 3) ℚ)
local instance coordinateFractionRationalAlgebra : Algebra ℚ CoordinateFractions := OreLocalization.instAlgebra
local instance genericCoordinateRationalAlgebra : Algebra ℚ GenericCoordinateField := GenericCoordinateField.algebra'
local instance topBaseRationalAlgebra : Algebra ℚ (⊤ : IntermediateField ℚ BaseField) :=
  (⊤ : IntermediateField ℚ BaseField).algebra'
local instance physicalCoordinateRationalAlgebra : Algebra ℚ
    (IntermediateField.adjoin ℚ (Set.range physicalBaseCoords)) :=
  (IntermediateField.adjoin ℚ (Set.range physicalBaseCoords)).algebra'


/-- Identification with the existing nested rational-function field, not a replacement base. -/
def genericCoordinateEquiv : CoordinateFractions ≃+* BaseField :=
  generic_base_independent.aevalEquivField.toRingEquiv.trans
    ((IntermediateField.equivOfEq generic_coordinate_field_top).toRingEquiv.trans
      IntermediateField.topEquiv.toRingEquiv)

theorem genericCoordinateEquiv_X (i : Fin 3) :
    genericCoordinateEquiv (algebraMap (MvPolynomial (Fin 3) ℚ) CoordinateFractions
      (MvPolynomial.X i)) = genericBaseCoords i := by
  change (generic_base_independent.aevalEquivField
    (algebraMap (MvPolynomial (Fin 3) ℚ) CoordinateFractions (MvPolynomial.X i))).val = _
  simp

/-- The underlying ring embedding is assembled without changing either Q-algebra. -/
def baseToCurveRing : BaseField →+* L :=
  ((IntermediateField.val _).toRingHom.comp
    physical_base_independent.aevalEquivField.toRingHom).comp genericCoordinateEquiv.symm.toRingHom

/-- Actual Q-algebra embedding from the existing K into the existing Curve. -/
def baseToCurve : BaseField →ₐ[ℚ] L :=
  { baseToCurveRing with commutes' := RingHom.map_rat_algebraMap baseToCurveRing }

theorem baseToCurve_coordinates (i : Fin 3) : baseToCurve (genericBaseCoords i) =
    physicalBaseCoords i := by
  rw [← genericCoordinateEquiv_X i]
  simp [baseToCurve,baseToCurveRing]

theorem baseToCurve_a : baseToCurve genericA = physicalA := baseToCurve_coordinates 0
theorem baseToCurve_v : baseToCurve genericV = physicalV := baseToCurve_coordinates 1
theorem baseToCurve_t : baseToCurve genericT = t := baseToCurve_coordinates 2

theorem field_map_injective {F M : Type*} [Field F] [Field M] (φ : F →+* M) :
    Function.Injective φ := RingHom.injective φ

theorem baseToCurve_injective : Function.Injective baseToCurve := field_map_injective baseToCurveRing

instance curveBaseAlgebra : Algebra BaseField L := baseToCurve.toRingHom.toAlgebra
instance curveQBaseTower : IsScalarTower ℚ BaseField L := IsScalarTower.rat

theorem baseToCurve_rational (q : ℚ) :
    baseToCurve (algebraMap ℚ BaseField q) = algebraMap ℚ L q := baseToCurve.commutes q

theorem curve_scalar_tower (q : ℚ) :
    algebraMap BaseField L (algebraMap ℚ BaseField q) = algebraMap ℚ L q :=
  (IsScalarTower.algebraMap_apply ℚ BaseField L q).symm



open ScalarExtensionTrace TraceFreeBasis SplitTraceQuotient

theorem mapped_polynomial : genericPolynomial.map baseToCurve.toRingHom =
    physicalPolynomial physicalA physicalV := by
  rw [genericPolynomial, GenericDistinctRoots.physical_map]
  change physicalPolynomial (baseToCurve genericA) (baseToCurve genericV) = _
  rw [baseToCurve_a,baseToCurve_v]

theorem physical_r_aeval : aeval r genericPolynomial = 0 := by
  rw [← eval_map_algebraMap]
  change (genericPolynomial.map baseToCurve.toRingHom).eval r = 0
  rw [mapped_polynomial]
  exact physical_r_root

/-- Evaluation at the physical root; no injectivity or trace claim is attached to this map. -/
def physicalEval : E →ₐ[BaseField] L :=
  AdjoinRoot.liftAlgHom genericPolynomial (Algebra.ofId BaseField L) r physical_r_aeval

theorem physicalEval_theta : physicalEval theta = r := by simp [physicalEval,theta]

theorem physicalEval_derivative : physicalEval derivativeElement = fR r w := by
  change physicalEval (aeval theta genericPolynomial.derivative) = _
  rw [← Polynomial.aeval_algHom_apply,physicalEval_theta,← eval_map_algebraMap,← derivative_map]
  change (genericPolynomial.map baseToCurve.toRingHom).derivative.eval r = _
  rw [mapped_polynomial]
  rfl

theorem physicalEval_inverseDerivative : physicalEval derivativeInverse = (fR r w)⁻¹ := by
  have h := congrArg physicalEval derivative_mul_inverse
  rw [map_mul,map_one,physicalEval_derivative] at h
  apply mul_left_cancel₀ cover_derivative_ne_zero
  rw [h,mul_inv_cancel₀ cover_derivative_ne_zero]

theorem physicalEval_sourceScalar : physicalEval sourceScalar = r^11/(12*fR r w) := by
  rw [sourceScalar,map_smul]
  simp only [quotientWeight,map_mul,map_pow,physicalEval_theta,physicalEval_inverseDerivative]
  simp only [Algebra.smul_def,map_div₀,map_one,map_ofNat]
  norm_num
  rw [map_ofNat (algebraMap BaseField L) 12]
  ring

theorem physical_sourceScalar_ne_zero : physicalEval sourceScalar ≠ 0 := by
  rw [physicalEval_sourceScalar]
  exact div_ne_zero (pow_ne_zero 11 (param_ne_zero 1))
    (mul_ne_zero (by norm_num) cover_derivative_ne_zero)

theorem physical_source_factor : physicalEval sourceScalar = r^11/fR r w/12 := by
  rw [physicalEval_sourceScalar]
  ring

/-- Extension of the coefficient embedding to the existing full splitting field. -/
def splitToCurve : SplitField →ₐ[BaseField] L :=
  Polynomial.SplittingField.lift genericPolynomial (IsAlgClosed.splits _)

theorem splitToCurve_injective : Function.Injective splitToCurve :=
  field_map_injective splitToCurve.toRingHom

theorem split_base_compatibility (k : BaseField) :
    splitToCurve (baseToSplit k) = baseToCurve k := splitToCurve.commutes k

def curveRoots (j : Fin 18) : L := splitToCurve (roots j)

theorem curveRoots_injective : Function.Injective curveRoots :=
  splitToCurve_injective.comp roots_injective

theorem curveRoots_aeval (j : Fin 18) : aeval (curveRoots j) genericPolynomial = 0 := by
  have h := congrArg splitToCurve (roots_aeval j)
  rw [map_zero,← Polynomial.aeval_algHom_apply] at h
  exact h

theorem curveRoots_eval (j : Fin 18) :
    (physicalPolynomial physicalA physicalV).eval (curveRoots j) = 0 := by
  have h := curveRoots_aeval j
  rw [← eval_map_algebraMap] at h
  change (genericPolynomial.map baseToCurve.toRingHom).eval (curveRoots j) = 0 at h
  rwa [mapped_polynomial] at h

theorem physical_eq_full_split : physicalPolynomial physicalA physicalV =
    coverPolynomial 1 curveRoots :=
  physical_eq_split_cover _ _ curveRoots curveRoots_injective curveRoots_eval

theorem curveRoots_exhaust (y : L) (hy : aeval y genericPolynomial = 0) :
    ∃ j : Fin 18, curveRoots j = y := by
  have hm : y ∈ genericPolynomial.rootSet L := generic_monic.mem_rootSet.mpr hy
  rw [← generic_splits.image_rootSet splitToCurve] at hm
  obtain ⟨x,hx,hxy⟩ := hm
  refine ⟨rootEquiv ⟨x,hx⟩,?_⟩
  simpa [curveRoots,GenericDistinctRoots.roots] using hxy

/-- A proved matching sheet; slot 11 below remains a power index, not this sheet index. -/
def physicalSheet : Fin 18 := (curveRoots_exhaust r physical_r_aeval).choose

theorem physicalSheet_root : curveRoots physicalSheet = r :=
  (curveRoots_exhaust r physical_r_aeval).choose_spec

def curveSigma (j : Fin 18) : E →ₐ[BaseField] L := splitToCurve.comp (sigma j)

theorem curveSigma_theta (j : Fin 18) : curveSigma j theta = curveRoots j := by
  simp [curveSigma,sigma_theta,curveRoots]

theorem physicalEval_eq_sheet : physicalEval = curveSigma physicalSheet := by
  apply AdjoinRoot.algHom_ext
  change physicalEval theta = curveSigma physicalSheet theta
  rw [physicalEval_theta,curveSigma_theta,physicalSheet_root]

/-- The degree-18 algebra over Curve, with its standard LEFT Curve scalar structure. -/
abbrev CurveTensor := L ⊗[BaseField] E
instance finiteCurveTensor : Module.Finite L CurveTensor := inferInstance
instance freeCurveTensor : Module.Free L CurveTensor := inferInstance

def curveTensorBasis : Module.Basis (Fin genericPolynomial.natDegree) L CurveTensor :=
  Algebra.TensorProduct.basis L quotientBasis

theorem curveTensor_finrank : Module.finrank L CurveTensor = 18 := by
  rw [Module.finrank_eq_card_basis curveTensorBasis]
  simpa using generic_degree

instance curveSplitScalarTower : IsScalarTower BaseField L (SplitAlgebra L) where
  smul_assoc a b c := by
    funext j
    exact smul_assoc a b (c j)

def curveAllEvaluations : E →ₐ[BaseField] SplitAlgebra L :=
  Pi.algHom BaseField (fun _ : Fin 18 => L) curveSigma

def curveBetaHom : CurveTensor →ₐ[L] SplitAlgebra L :=
  Algebra.TensorProduct.lift (Algebra.ofId L (SplitAlgebra L)) curveAllEvaluations
    (fun _ _ => Commute.all _ _)

theorem curveBetaHom_tmul (l : L) (e : E) (j : Fin 18) :
    curveBetaHom (l ⊗ₜ[BaseField] e) j = l*curveSigma j e := rfl

theorem curveBetaHom_theta : curveBetaHom (1 ⊗ₜ[BaseField] theta) = curveRoots := by
  ext j
  simp [curveBetaHom_tmul,curveSigma_theta]

theorem curveBetaHom_surjective : Function.Surjective curveBetaHom := by
  intro y
  refine ⟨aeval (1 ⊗ₜ[BaseField] theta) (Lagrange.interpolate Finset.univ curveRoots y),?_⟩
  rw [← Polynomial.aeval_algHom_apply,curveBetaHom_theta]
  ext j
  rw [Polynomial.aeval_pi_apply₂]
  exact Lagrange.eval_interpolate_at_node y curveRoots_injective.injOn (Finset.mem_univ j)

theorem curveBetaHom_bijective : Function.Bijective curveBetaHom := by
  have hd : Module.finrank L CurveTensor = Module.finrank L (SplitAlgebra L) := by
    rw [curveTensor_finrank]
    simp [SplitAlgebra]
  exact ⟨(LinearMap.injective_iff_surjective_of_finrank_eq_finrank hd
    (f := curveBetaHom.toLinearMap)).mpr curveBetaHom_surjective,curveBetaHom_surjective⟩

def curveBeta : CurveTensor ≃ₐ[L] SplitAlgebra L :=
  AlgEquiv.ofBijective curveBetaHom curveBetaHom_bijective

theorem curveBeta_tmul (l : L) (e : E) (j : Fin 18) :
    curveBeta (l ⊗ₜ[BaseField] e) j = l*curveSigma j e := curveBetaHom_tmul l e j

theorem curveBeta_scalar (l : L) : curveBeta (l ⊗ₜ[BaseField] (1:E)) = fun _ => l := by
  ext j
  simp [curveBeta_tmul]

/-- Arbitrary-element trace base change, not the field trace of Curve over K. -/
theorem trace_curve_baseChange (e : E) : baseToCurve (Algebra.trace BaseField E e) =
    Algebra.trace L CurveTensor (1 ⊗ₜ[BaseField] e) := by
  change algebraMap BaseField L (LinearMap.trace BaseField E (Algebra.lmul BaseField E e)) =
    LinearMap.trace L CurveTensor (Algebra.lmul L CurveTensor (1 ⊗ₜ[BaseField] e))
  rw [← Algebra.baseChange_lmul,LinearMap.trace_baseChange]

theorem trace_curveBeta (z : CurveTensor) : Algebra.trace L CurveTensor z =
    Algebra.trace L (SplitAlgebra L) (curveBeta z) :=
  (Algebra.trace_eq_of_algEquiv curveBeta z).symm

theorem trace_curve_sum (z : CurveTensor) : Algebra.trace L CurveTensor z =
    ∑ j, curveBeta z j := by rw [trace_curveBeta,algebra_trace_eq_sum]

/-- Compatibility with the previously proved trace tower, retaining all eighteen sheets. -/
theorem trace_allSheets (e : E) : baseToCurve (Algebra.trace BaseField E e) =
    ∑ j, curveSigma j e := by
  have h := congrArg splitToCurve (trace_evaluations e)
  simpa only [split_base_compatibility,map_sum,curveSigma,AlgHom.comp_apply] using h

theorem trace_curve_tmul (l : L) (e : E) :
    Algebra.trace L CurveTensor (l ⊗ₜ[BaseField] e) =
      l*baseToCurve (Algebra.trace BaseField E e) := by
  rw [trace_curve_sum,trace_allSheets]
  simp [curveBeta_tmul,Finset.mul_sum]

theorem trace_curve_sourceScalar :
    Algebra.trace L CurveTensor (1 ⊗ₜ[BaseField] sourceScalar) = 0 := by
  rw [← trace_curve_baseChange,sourceScalar_trace,map_zero]

theorem trace_curve_two :
    Algebra.trace L CurveTensor ((2:L) ⊗ₜ[BaseField] (1:E)) = 36 := by
  rw [trace_curve_tmul,trace_one,map_ofNat]
  norm_num

theorem physical_evaluation_not_trace :
    physicalEval (1:E) ≠ baseToCurve (Algebra.trace BaseField E 1) := by
  rw [map_one,trace_one,map_ofNat]
  norm_num

end HodgeLab.OneReflectionSkew.PhysicalTraceBridge

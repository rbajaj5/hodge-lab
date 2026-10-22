import HodgeLab.OneReflectionSkew.TraceFreeBasis
import Mathlib.RingTheory.AdjoinRoot
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas

/-!
The actual quotient by the split degree-18 polynomial is identified with all
eighteen evaluation components. No irreducibility or quotient-field structure
is assumed. Descent from a splitting field and physical source binding remain
separate tasks.
-/
noncomputable section

namespace HodgeLab.OneReflectionSkew.SplitTraceQuotient

open scoped BigOperators
open Polynomial Module TraceFreeBasis

variable {K : Type*} [Field K]

abbrev CoverAlgebra (a : K) (roots : Fin 18 → K) :=
  AdjoinRoot (coverPolynomial a roots)

theorem cover_eval_root (a : K) (roots : Fin 18 → K) (j : Fin 18) :
    (coverPolynomial a roots).eval (roots j) = 0 := by
  simp [coverPolynomial, Lagrange.eval_nodal_at_node]

def evaluation (a : K) (roots : Fin 18 → K) :
    CoverAlgebra a roots →ₐ[K] SplitAlgebra K :=
  Pi.algHom K (fun _ : Fin 18 => K) fun j =>
    AdjoinRoot.liftAlgHom (coverPolynomial a roots) (AlgHom.id K K)
      (roots j) (by simpa using cover_eval_root a roots j)

theorem evaluation_mk (a : K) (roots : Fin 18 → K) (p : K[X]) (j : Fin 18) :
    evaluation a roots (AdjoinRoot.mk (coverPolynomial a roots) p) j =
      p.eval (roots j) := by
  simp [evaluation, AdjoinRoot.liftAlgHom_mk]

theorem evaluation_root (a : K) (roots : Fin 18 → K) :
    evaluation a roots (AdjoinRoot.root (coverPolynomial a roots)) = roots := by
  ext j
  simp [evaluation]

theorem evaluation_surjective (a : K) (roots : Fin 18 → K)
    (hr : Function.Injective roots) : Function.Surjective (evaluation a roots) := by
  intro f
  refine ⟨AdjoinRoot.mk (coverPolynomial a roots)
    (Lagrange.interpolate Finset.univ roots f), ?_⟩
  ext j
  rw [evaluation_mk]
  exact Lagrange.eval_interpolate_at_node f hr.injOn (Finset.mem_univ j)

theorem cover_ne_zero (a : K) (ha : a ≠ 0) (roots : Fin 18 → K) :
    coverPolynomial a roots ≠ 0 := by
  intro h
  have hd := cover_degree a ha roots
  rw [h, Polynomial.natDegree_zero] at hd
  contradiction

theorem evaluation_bijective (a : K) (ha : a ≠ 0) (roots : Fin 18 → K)
    (hr : Function.Injective roots) : Function.Bijective (evaluation a roots) := by
  let pb := AdjoinRoot.powerBasis (cover_ne_zero a ha roots)
  letI := pb.basis.finiteDimensional_of_finite
  have hd : finrank K (CoverAlgebra a roots) = finrank K (SplitAlgebra K) := by
    rw [pb.finrank]
    simp [pb, AdjoinRoot.powerBasis, cover_degree a ha roots, SplitAlgebra]
  have hs := evaluation_surjective a roots hr
  exact ⟨(LinearMap.injective_iff_surjective_of_finrank_eq_finrank hd
    (f := (evaluation a roots).toLinearMap)).mpr hs, hs⟩

def evaluationEquiv (a : K) (ha : a ≠ 0) (roots : Fin 18 → K)
    (hr : Function.Injective roots) : CoverAlgebra a roots ≃ₐ[K] SplitAlgebra K :=
  AlgEquiv.ofBijective (evaluation a roots) (evaluation_bijective a ha roots hr)

theorem evaluationEquiv_apply (a : K) (ha : a ≠ 0) (roots : Fin 18 → K)
    (hr : Function.Injective roots) (x : CoverAlgebra a roots) :
    evaluationEquiv a ha roots hr x = evaluation a roots x := rfl

theorem evaluationEquiv_root (a : K) (ha : a ≠ 0) (roots : Fin 18 → K)
    (hr : Function.Injective roots) :
    evaluationEquiv a ha roots hr (AdjoinRoot.root (coverPolynomial a roots)) = roots :=
  evaluation_root a roots

theorem trace_transport (a : K) (ha : a ≠ 0) (roots : Fin 18 → K)
    (hr : Function.Injective roots) (x : CoverAlgebra a roots) :
    Algebra.trace K (CoverAlgebra a roots) x =
      Algebra.trace K (SplitAlgebra K) (evaluationEquiv a ha roots hr x) := by
  -- The same conjugation argument as Mathlib's `Algebra.trace_eq_of_algEquiv`,
  -- using the already imported trace definitions rather than its larger import.
  let e := evaluationEquiv a ha roots hr
  have hm : e.toLinearEquiv.conj (Algebra.lmul K (CoverAlgebra a roots) x) =
      Algebra.lmul K (SplitAlgebra K) (e x) := by
    ext y
    simp
  change LinearMap.trace K _ (Algebra.lmul K (CoverAlgebra a roots) x) =
    LinearMap.trace K _ (Algebra.lmul K (SplitAlgebra K) (e x))
  rw [← hm]
  exact (LinearMap.trace_conj' _ e.toLinearEquiv).symm

def quotientCodifferent (a : K) (ha : a ≠ 0) (roots : Fin 18 → K)
    (hr : Function.Injective roots) (i : Fin 18) : CoverAlgebra a roots :=
  (evaluationEquiv a ha roots hr).symm (codifferent a roots i)

def quotientCodifferentBasis (a : K) (ha : a ≠ 0) (roots : Fin 18 → K)
    (hr : Function.Injective roots) : Basis (Fin 18) K (CoverAlgebra a roots) :=
  (codifferentBasis a ha roots hr).map (evaluationEquiv a ha roots hr).symm.toLinearEquiv

theorem quotientCodifferentBasis_apply (a : K) (ha : a ≠ 0) (roots : Fin 18 → K)
    (hr : Function.Injective roots) (i : Fin 18) :
    quotientCodifferentBasis a ha roots hr i = quotientCodifferent a ha roots hr i := by
  simp [quotientCodifferentBasis, quotientCodifferent, codifferentBasis_apply]

theorem trace_quotientCodifferent (a : K) (ha : a ≠ 0) (roots : Fin 18 → K)
    (hr : Function.Injective roots) (i : Fin 18) :
    Algebra.trace K (CoverAlgebra a roots) (quotientCodifferent a ha roots hr i) =
      (if (i : ℕ) = 17 then 1 else 0) / a := by
  rw [trace_transport a ha roots hr]
  simp only [quotientCodifferent, AlgEquiv.apply_symm_apply]
  exact trace_codifferent a roots hr i

theorem derivative_mul_quotientCodifferent (a : K) (ha : a ≠ 0) (roots : Fin 18 → K)
    (hr : Function.Injective roots) (i : Fin 18) :
    aeval (AdjoinRoot.root (coverPolynomial a roots))
        (coverPolynomial a roots).derivative * quotientCodifferent a ha roots hr i =
      AdjoinRoot.root (coverPolynomial a roots) ^ (i : ℕ) := by
  apply (evaluationEquiv a ha roots hr).injective
  rw [map_mul, map_pow, ← Polynomial.aeval_algHom_apply,
    evaluationEquiv_root]
  simp only [quotientCodifferent, AlgEquiv.apply_symm_apply]
  ext j
  simp only [Pi.mul_apply, Pi.pow_apply, codifferent]
  rw [Polynomial.aeval_pi_apply₂]
  change derivativeValue a roots j *
    (roots j ^ (i : ℕ) / derivativeValue a roots j) = roots j ^ (i : ℕ)
  exact mul_div_cancel₀ _ (derivative_value_ne_zero a ha roots hr j)

theorem quotient_derivative_isUnit (a : K) (ha : a ≠ 0) (roots : Fin 18 → K)
    (hr : Function.Injective roots) :
    IsUnit (aeval (AdjoinRoot.root (coverPolynomial a roots))
      (coverPolynomial a roots).derivative) := by
  apply isUnit_iff_exists_inv.mpr
  refine ⟨quotientCodifferent a ha roots hr 0, ?_⟩
  simpa using derivative_mul_quotientCodifferent a ha roots hr (0 : Fin 18)

theorem trace_quotient_basis_initial (a : K) (ha : a ≠ 0) (roots : Fin 18 → K)
    (hr : Function.Injective roots) (i : Fin 17) :
    Algebra.trace K (CoverAlgebra a roots)
      (quotientCodifferentBasis a ha roots hr i.castSucc) = 0 := by
  rw [quotientCodifferentBasis_apply, trace_quotientCodifferent]
  have hi : (i : ℕ) ≠ 17 := Nat.ne_of_lt i.isLt
  simp [hi]

theorem trace_quotient_basis_last (a : K) (ha : a ≠ 0) (roots : Fin 18 → K)
    (hr : Function.Injective roots) :
    Algebra.trace K (CoverAlgebra a roots)
      (quotientCodifferentBasis a ha roots hr (Fin.last 17)) = a⁻¹ := by
  rw [quotientCodifferentBasis_apply, trace_quotientCodifferent]
  simp

def quotientTraceFreeBasis (a : K) (ha : a ≠ 0) (roots : Fin 18 → K)
    (hr : Function.Injective roots) :
    Basis (Fin 17) K (LinearMap.ker (Algebra.trace K (CoverAlgebra a roots))) :=
  TraceKernel.kernelBasis (quotientCodifferentBasis a ha roots hr)
    (Algebra.trace K (CoverAlgebra a roots))
    (trace_quotient_basis_initial a ha roots hr)
    (trace_quotient_basis_last a ha roots hr) (inv_ne_zero ha)

theorem quotientTraceFreeBasis_apply (a : K) (ha : a ≠ 0) (roots : Fin 18 → K)
    (hr : Function.Injective roots) (i : Fin 17) :
    ((quotientTraceFreeBasis a ha roots hr i) : CoverAlgebra a roots) =
      quotientCodifferent a ha roots hr i.castSucc := by
  rw [quotientTraceFreeBasis, TraceKernel.kernelBasis_apply,
    quotientCodifferentBasis_apply]

theorem quotient_traceFree_finrank (a : K) (ha : a ≠ 0) (roots : Fin 18 → K)
    (hr : Function.Injective roots) :
    Module.finrank K (LinearMap.ker (Algebra.trace K (CoverAlgebra a roots))) = 17 :=
  Module.finrank_eq_card_basis (quotientTraceFreeBasis a ha roots hr)

end HodgeLab.OneReflectionSkew.SplitTraceQuotient

import Mathlib.LinearAlgebra.Basis.Defs
import Mathlib.LinearAlgebra.LinearIndependent.Basic
import Mathlib.Algebra.BigOperators.Fin

/-! A basis for the kernel of a linear functional supported on the last basis vector.

This file is generic linear algebra. An application must establish its own
basis and the displayed values of its trace functional.
-/

noncomputable section

namespace HodgeLab.OneReflectionSkew.TraceKernel

open scoped BigOperators
open Module

variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
variable {n : ℕ} (b : Basis (Fin (n + 1)) K V) (T : V →ₗ[K] K)
variable {c : K} (hzero : ∀ i : Fin n, T (b i.castSucc) = 0)
variable (hlast : T (b (Fin.last n)) = c) (hc : c ≠ 0)

include hzero hlast in
/-- The functional is its last coordinate multiplied by its value on the last vector. -/
theorem trace_eq_last_coefficient (v : V) :
    T v = b.repr v (Fin.last n) * c := by
  calc
    T v = T (∑ i, b.repr v i • b i) := congrArg T (b.sum_repr v).symm
    _ = b.repr v (Fin.last n) * c := by
      rw [map_sum, Fin.sum_univ_castSucc]
      simp [map_smul, hzero, hlast, smul_eq_mul]

include hzero hlast hc in
/-- Membership in the kernel is exactly vanishing of the last basis coordinate. -/
theorem mem_ker_iff_last_coefficient_eq_zero (v : V) :
    v ∈ LinearMap.ker T ↔ b.repr v (Fin.last n) = 0 := by
  rw [LinearMap.mem_ker, trace_eq_last_coefficient b T hzero hlast]
  simp [mul_eq_zero, hc]

/-- Retain the first `n` coordinates of a vector in the kernel. -/
def kernelCoordinates : LinearMap.ker T →ₗ[K] (Fin n → K) where
  toFun v i := b.repr v.val i.castSucc
  map_add' v w := by
    funext i
    simp
  map_smul' a v := by
    funext i
    simp

include hzero hlast hc in
theorem kernelCoordinates_injective :
    Function.Injective (kernelCoordinates b T) := by
  intro v w h
  apply Subtype.ext
  apply b.repr.injective
  ext i
  refine Fin.lastCases ?_ (fun j => ?_) i
  · have hv := (mem_ker_iff_last_coefficient_eq_zero b T hzero hlast hc v.val).mp v.property
    have hw := (mem_ker_iff_last_coefficient_eq_zero b T hzero hlast hc w.val).mp w.property
    rw [hv, hw]
  · exact congrFun h j

include hzero in
theorem kernelCoordinates_surjective :
    Function.Surjective (kernelCoordinates b T) := by
  intro a
  refine ⟨⟨∑ i : Fin n, a i • b i.castSucc, ?_⟩, ?_⟩
  · change T (∑ i : Fin n, a i • b i.castSucc) = 0
    simp [map_sum, hzero]
  · funext i
    simp [kernelCoordinates, map_sum, map_smul, Finsupp.single_apply,
      Fin.castSucc_inj, Finset.sum_apply, smul_eq_mul]

/-- The first `n` coordinates identify the kernel with `K^n`. -/
def kernelEquiv : LinearMap.ker T ≃ₗ[K] (Fin n → K) :=
  LinearEquiv.ofBijective (kernelCoordinates b T)
    ⟨kernelCoordinates_injective b T hzero hlast hc,
      kernelCoordinates_surjective b T hzero⟩

/-- The first `n` vectors of `b`, regarded as a basis of the kernel. -/
def kernelBasis : Basis (Fin n) K (LinearMap.ker T) :=
  Basis.ofEquivFun (kernelEquiv b T hzero hlast hc)

@[simp] theorem kernelBasis_repr (v : LinearMap.ker T) (i : Fin n) :
    (kernelBasis b T hzero hlast hc).repr v i = b.repr v.val i.castSucc := by
  exact Basis.ofEquivFun_repr_apply (kernelEquiv b T hzero hlast hc) v i

/-- The constructed basis has exactly the original first `n` ambient vectors. -/
@[simp] theorem kernelBasis_apply (i : Fin n) :
    ((kernelBasis b T hzero hlast hc) i : V) = b i.castSucc := by
  apply b.repr.injective
  ext j
  refine Fin.lastCases ?_ (fun k => ?_) j
  · have hv :=
      (mem_ker_iff_last_coefficient_eq_zero b T hzero hlast hc
        ((kernelBasis b T hzero hlast hc) i : V)).mp
        ((kernelBasis b T hzero hlast hc) i).property
    simpa using hv
  · rw [← kernelBasis_repr b T hzero hlast hc]
    simp [Finsupp.single_apply, Fin.castSucc_inj]

/-- A directly usable seventeen-dimensional kernel basis in the eighteen-slot case. -/
def kernelBasisSeventeen (b : Basis (Fin 18) K V) (T : V →ₗ[K] K)
    (hzero : ∀ i : Fin 17, T (b i.castSucc) = 0)
    (hlast : T (b (Fin.last 17)) = c) (hc : c ≠ 0) :
    Basis (Fin 17) K (LinearMap.ker T) :=
  kernelBasis b T hzero hlast hc

/-- Slot eleven is in the kernel when all seventeen nonfinal slots have zero trace.
An application must separately identify its physical source with this slot. -/
theorem slot_eleven_mem_ker (b : Basis (Fin 18) K V) (T : V →ₗ[K] K)
    (hzero : ∀ i : Fin 17, T (b i.castSucc) = 0) :
    b (11 : Fin 18) ∈ LinearMap.ker T := by
  exact hzero (11 : Fin 17)

end HodgeLab.OneReflectionSkew.TraceKernel

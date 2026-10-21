import HodgeLab.OneReflectionSkew.ThreeCoefficient

/-! Exact sensitivity checks. None asserts that a degree-five primitive exists. -/
namespace HodgeLab.OneReflectionSkew
open HodgeLab.SparsePolynomial

/-- Reverse the sign of the U*r*t^3 coefficient only. -/
def changedP7 : Sparse := p7Sparse.map fun term =>
  if term.1 = exp 1 1 0 3 then (term.1, -term.2) else term
def changedConstantColumn : Sparse :=
  scale 60 (multiply aSparse (derivative 0 changedP7)) ++
  scale 72 (multiply changedP7 (derivative 0 aSparse))

set_option maxRecDepth 100000 in
theorem changed_coefficient :
    coefficient (rowExponent 0) changedConstantColumn = 60 := by decide +kernel

set_option maxRecDepth 100000 in
theorem changed_pairing :
    21 * coefficient (rowExponent 0) changedConstantColumn +
    coefficient (rowExponent 1) changedConstantColumn -
    coefficient (rowExponent 2) changedConstantColumn = 2520 := by decide +kernel

end HodgeLab.OneReflectionSkew

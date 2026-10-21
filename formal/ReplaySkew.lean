import LeanChecker

/-! Default replay trusts imported declarations, as does the LeanChecker CLI.
This is not a fresh replay of mathlib. No proof declaration is added here. -/
#eval do
  Lean.initSearchPath (← Lean.findSysroot)
  for module in [`HodgeLab.SparsePolynomial, `HodgeLab.RowCertificate,
      `HodgeLab.OneReflectionSkew.ThreeCoefficient,
      `HodgeLab.OneReflectionSkew.Controls] do
    replayFromImports module
    IO.println s!"PASS {module}"
    (← IO.getStdout).flush

import LeanChecker

-- Only the new module is replayed. Prior proofs and Mathlib are trusted imports.
#eval do
  Lean.initSearchPath (← Lean.findSysroot)
  replayFromImports `HodgeLab.OneReflectionSkew.DifferentialForms
  IO.println "PASS HodgeLab.OneReflectionSkew.DifferentialForms"
  (← IO.getStdout).flush

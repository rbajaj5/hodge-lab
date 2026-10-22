import LeanChecker

-- Default replay checks the new module and trusts imported modules.
#eval do
  Lean.initSearchPath (← Lean.findSysroot)
  replayFromImports `HodgeLab.OneReflectionSkew.ChartSubstitution
  IO.println "PASS HodgeLab.OneReflectionSkew.ChartSubstitution"
  (← IO.getStdout).flush

import LeanChecker

-- Replay only the new module; imported modules are dependency evidence.
#eval do
  Lean.initSearchPath (← Lean.findSysroot)
  replayFromImports `HodgeLab.OneReflectionSkew.PhysicalCurveRealization
  IO.println "PASS HodgeLab.OneReflectionSkew.PhysicalCurveRealization"
  (← IO.getStdout).flush

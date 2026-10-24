import LeanChecker

-- Replay only the new module; imported modules are dependency evidence.
#eval do
  Lean.initSearchPath (← Lean.findSysroot)
  replayFromImports `HodgeLab.OneReflectionSkew.PhysicalTraceBridge
  IO.println "PASS HodgeLab.OneReflectionSkew.PhysicalTraceBridge"
  (← IO.getStdout).flush

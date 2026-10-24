import LeanChecker

-- Replay only the new source-normalization module; all imported modules are reused.
#eval do
  Lean.initSearchPath (← Lean.findSysroot)
  replayFromImports `HodgeLab.OneReflectionSkew.PhysicalSourceNormalization
  IO.println "PASS HodgeLab.OneReflectionSkew.PhysicalSourceNormalization"
  (← IO.getStdout).flush

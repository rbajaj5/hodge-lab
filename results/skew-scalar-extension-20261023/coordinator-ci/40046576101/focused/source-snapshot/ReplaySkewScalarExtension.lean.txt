import LeanChecker

-- Replay the new bridge only. Imported mathematical modules are reused.
#eval do
  Lean.initSearchPath (← Lean.findSysroot)
  replayFromImports `HodgeLab.OneReflectionSkew.ScalarExtensionTrace
  IO.println "PASS HodgeLab.OneReflectionSkew.ScalarExtensionTrace"
  (← IO.getStdout).flush

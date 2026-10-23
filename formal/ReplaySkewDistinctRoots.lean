import LeanChecker

-- Replay only the new generic distinct-root module; prior proofs are reused.
#eval do
  Lean.initSearchPath (← Lean.findSysroot)
  replayFromImports `HodgeLab.OneReflectionSkew.GenericDistinctRoots
  IO.println "PASS HodgeLab.OneReflectionSkew.GenericDistinctRoots"
  (← IO.getStdout).flush

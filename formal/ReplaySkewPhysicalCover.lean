import LeanChecker

-- Replay only the new binding module; imported proofs are reused.
#eval do
  Lean.initSearchPath (← Lean.findSysroot)
  replayFromImports `HodgeLab.OneReflectionSkew.PhysicalCoverBinding
  IO.println "PASS HodgeLab.OneReflectionSkew.PhysicalCoverBinding"
  (← IO.getStdout).flush

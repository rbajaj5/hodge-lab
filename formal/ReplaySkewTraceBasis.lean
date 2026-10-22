import LeanChecker

-- Replay each new module; Mathlib imports remain trusted.
#eval do
  Lean.initSearchPath (← Lean.findSysroot)
  replayFromImports `HodgeLab.OneReflectionSkew.TraceKernel
  IO.println "PASS HodgeLab.OneReflectionSkew.TraceKernel"
  (← IO.getStdout).flush
  replayFromImports `HodgeLab.OneReflectionSkew.TraceFreeBasis
  IO.println "PASS HodgeLab.OneReflectionSkew.TraceFreeBasis"
  (← IO.getStdout).flush
  replayFromImports `HodgeLab.OneReflectionSkew.SplitTraceQuotient
  IO.println "PASS HodgeLab.OneReflectionSkew.SplitTraceQuotient"
  (← IO.getStdout).flush

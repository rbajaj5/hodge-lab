import LeanChecker

-- Default kernel replay trusts imported modules; no fresh mathlib replay.
#eval do
  Lean.initSearchPath (← Lean.findSysroot)
  for module in [`HodgeLab.OneReflectionSkew.DegreeFour,
      `HodgeLab.OneReflectionSkew.CoordinateComparison] do
    replayFromImports module
    IO.println s!"PASS {module}"
    (← IO.getStdout).flush

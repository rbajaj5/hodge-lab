import LeanChecker

-- Default kernel replay trusts imports; the earlier chart proof is reused.
#eval do
  Lean.initSearchPath (← Lean.findSysroot)
  for m in [`HodgeLab.OneReflectionSkew.NormalChart,
      `HodgeLab.OneReflectionSkew.ResidueNormalization] do
    replayFromImports m
    IO.println s!"PASS {m}"
    (← IO.getStdout).flush

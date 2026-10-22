import LeanChecker

-- Default kernel replay trusts imports; the prior residue proof is reused.
#eval do
  Lean.initSearchPath (← Lean.findSysroot)
  replayFromImports `HodgeLab.OneReflectionSkew.AmbientDerivation
  IO.println "PASS HodgeLab.OneReflectionSkew.AmbientDerivation"
  (← IO.getStdout).flush

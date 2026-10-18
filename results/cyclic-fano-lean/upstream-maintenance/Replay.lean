import LeanChecker

#eval do
  Lean.initSearchPath (← Lean.findSysroot)
  replayFromImports `HodgeTestbed.RowCertificate
  IO.println "PASS HodgeTestbed.RowCertificate"
  replayFromImports `HodgeTestbed.RowCertificateExample
  IO.println "PASS HodgeTestbed.RowCertificateExample"

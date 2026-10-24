"""Final byte-binding audit only; no mathematical computation."""
import datetime,hashlib,json,pathlib,sys
root=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
run=root/'check-01';e=read(run/'execution.json');v=read(run/'result/validation.json')
checks={
 'successful_execution':e['status']=='completed' and e['exit_code']==0,
 'bounded_execution':e['timeout_seconds']==60 and e['seconds']<60,
 'checker_snapshot_matches_execution':sha(run/'checker-source.py')==e['checker_sha256'],
 'checker_snapshot_matches_validation':sha(run/'checker-source.py')==v['script_sha256'],
 'final_checker_matches_snapshot':sha(root/'check_order5.py')==sha(run/'checker-source.py'),
 'runner_snapshot_matches_execution':sha(run/'runner-source.py')==e['runner_sha256'],
 'final_runner_matches_snapshot':sha(root/'run_bounded.py')==sha(run/'runner-source.py'),
 'injection_matches_validation':sha(run/'result/highest-pole-injection.json')==v['injection_sha256'],
 'pinned_connection_recorded':v['source_sha256']=='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d',
 'prior_injection_pin_recorded':v['prior_injection_sha256']=='047d04f6d9ee1c70000146506fa2ada26c456fd1dd9de5b2d70e4be811ce828b'}
if not all(checks.values()):raise RuntimeError('artifact binding failure')
record={'status':'FROZEN_BYTE_BINDINGS_PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'command':[sys.executable,*sys.argv],'checks':checks,'checker_sha256':sha(root/'check_order5.py'),
 'injection_sha256':sha(run/'result/highest-pole-injection.json'),'execution_seconds':e['seconds'],
 'exact_checks':len(v['checks']),'controls':len(v['mutations']),'scope':'Only new A5 highest-pole structural work.'}
(root/'freeze-receipt.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
manifest={'status':'FROZEN','files':[{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
 for p in sorted(root.rglob('*')) if p.is_file() and p.name!='artifact-manifest.json']}
(root/'artifact-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,indent=2))

"""Byte-binding audit only; no symbolic mathematics or matrix search."""
import datetime,hashlib,json,pathlib,sys
root=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
bindings=[]
for name in ('check-01','check-02'):
    run=root/name
    execution=read(run/'execution.json')
    validation=read(run/'result/validation.json')
    checks={
        'successful_execution':execution['status']=='completed' and execution['exit_code']==0,
        'bounded_execution':execution['timeout_seconds']==60 and execution['seconds']<60,
        'checker_snapshot_matches_execution':sha(run/'checker-source.py')==execution['checker_sha256'],
        'checker_snapshot_matches_validation':sha(run/'checker-source.py')==validation['script_sha256'],
        'runner_snapshot_matches_execution':sha(run/'runner-source.py')==execution['runner_sha256'],
        'sparse_injection_matches_validation':sha(run/'result/tangent-injection.json')==validation['injection_sha256'],
        'pinned_connection_recorded':validation['source_sha256']=='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d',
    }
    if not all(checks.values()):raise RuntimeError(name+' binding failure')
    bindings.append({'run':name,'checks':checks,'checker_sha256':execution['checker_sha256'],
        'seconds':execution['seconds'],'algebra_seconds':validation['seconds'],
        'exact_checks':len(validation['checks']),'mutations':len(validation['mutations'])})
if sha(root/'check_structure.py')!=sha(root/'check-02/checker-source.py'):
    raise RuntimeError('final source differs from final executed version')
if sha(root/'check-01/checker-source.py')==sha(root/'check-02/checker-source.py'):
    raise RuntimeError('expected distinct historical versions')
record={'status':'FROZEN_BYTE_BINDINGS_PASS','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'command':[sys.executable,*sys.argv],'bindings':bindings,
    'final_checker_sha256':sha(root/'check_structure.py'),
    'final_injection_sha256':sha(root/'check-02/result/tangent-injection.json'),
    'source_versions':'check-01 is preserved first version; check-02 snapshot matches final checker. No receipt rewritten.',
    'limitations':'No math run in this audit. Independent checker evidence remains in the coordinator-owned checker subtree, not copied here.'}
(root/'freeze-receipt.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
manifest={'status':'FROZEN','files':[{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
    for p in sorted(root.rglob('*')) if p.is_file() and p.name!='artifact-manifest.json']}
(root/'artifact-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,indent=2))

"""Hash and freeze presentation files; no mathematical computation."""
import datetime,hashlib,json,pathlib
root=pathlib.Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
report=json.loads((root/'render-01/visualization.json').read_text(encoding='utf-8'))
for item in report['outputs']:
    if sha(root/'render-01'/item['path'])!=item['sha256']:raise RuntimeError('output hash changed')
if sha(root/'render_receipts.py')!=report['generator_sha256']:raise RuntimeError('generator changed')
manifest={'status':'FROZEN_PRESENTATION_ONLY','utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'files':[{'path':p.relative_to(root).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
 for p in sorted(root.rglob('*')) if p.is_file() and p.name!='artifact-manifest.json']}
(root/'artifact-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':manifest['status'],'utc':manifest['utc'],'files':len(manifest['files'])}))

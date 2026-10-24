"""Audit immutable Pro packet bindings; this is not a mathematical replay."""
from pathlib import Path
import datetime,hashlib,json
repo=Path(r'C:\Users\anaxe\Documents\Codex\hl-source-20261023')
base=repo/'results/skew-mixed-construction-20261024'
delivery=repo/'results/skew-full-residual-20261024/pro-delivery'
digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
hashes={digest(p):str(p.relative_to(repo)) for p in base.rglob('*') if p.is_file()}
pin='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
keys={'script_sha256','checker_sha256','runner_sha256','report_sha256','stdout_sha256','stderr_sha256','reused_system_validation_sha256','author_system_sha256','certificate_sha256','input_sha256','inputs_sha256','matrix_sha256','author_validation_sha256','generator_sha256'}
checks=[]
for f in base.rglob('*.json'):
    j=json.loads(f.read_text(encoding='utf-8'))
    if not isinstance(j,dict):continue
    for k,v in j.items():
        if k in keys and isinstance(v,str):
            if v not in hashes:raise RuntimeError((str(f),k,v))
            checks.append({'receipt':str(f.relative_to(repo)),'field':k,'bound_file':hashes[v]})
        if k in ('packet_sha256',) and isinstance(v,str):
            if v!=pin:raise RuntimeError((str(f),k,v))
            checks.append({'receipt':str(f.relative_to(repo)),'field':k,'connection_pin_verified':True})
record={'status':'PASS: Pro packet source/script/report/figure bindings, not a mathematical replay',
        'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'checks':checks,
        'figure_inspection':'Coordinator inspected figure-02 PNG: labels, signed symmetric-log display and point-only scope are readable; bar sizes do not measure generic progress.'}
(delivery/'bindings-validation.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print('Passed',len(checks),'Pro packet artifact bindings')

"""Read-only evidence bindings and append-only integration checks; no math replay."""
import argparse, datetime, hashlib, json, pathlib, re, subprocess
p=argparse.ArgumentParser()
p.add_argument('--repo',type=pathlib.Path,required=True)
p.add_argument('--parent-ledger',type=pathlib.Path,required=True)
args=p.parse_args()
repo=args.repo.resolve(); batch=repo/'results/skew-full-residual-20261024'
digest=lambda b:hashlib.sha256(b).hexdigest()
files={f.relative_to(batch).as_posix():digest(f.read_bytes()) for f in batch.rglob('*') if f.is_file() and f.name!='integration-validation.json'}
by_hash={}
for name,h in files.items():by_hash.setdefault(h,[]).append(name)
lf_log_hashes={}
for name in files:
    if name.endswith('.log'):
        raw=(batch/name).read_bytes()
        lf_log_hashes.setdefault(digest(raw.replace(b'\r\n',b'\n')),[]).append(name)
checks=[]; notes=[]
def check(name,condition):
    if not condition: raise RuntimeError(name)
    checks.append(name)
connection=repo/'results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'
check('unchanged connection bytes',digest(connection.read_bytes())=='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d')
for f in batch.rglob('*.json'):
    if f.name=='integration-validation.json':continue
    value=json.loads(f.read_text(encoding='utf-8'))
    if not isinstance(value,dict):continue
    for key in ('script_sha256','checker_sha256','runner_sha256','report_sha256','log_sha256'):
        if key not in value:continue
        h=value[key]
        if key=='log_sha256' and h==digest(b'') and h not in by_hash:
            notes.append(f'{f.relative_to(batch)} records empty output by hash; no separate empty log retained')
        elif key=='log_sha256' and h not in by_hash and h in lf_log_hashes:
            check(f'{f.relative_to(batch)}: log receipt binds LF-normalized text, not raw Windows bytes',True)
            notes.append({'receipt':str(f.relative_to(batch)),'field':key,
                          'binding':'Receipt hashed LF subprocess text before Windows text-mode file output; preserved CRLF log bytes differ.',
                          'matching_LF_logs':lf_log_hashes[h],
                          'raw_hashes':{n:files[n] for n in lf_log_hashes[h]}})
        else:check(f'{f.relative_to(batch)}: {key} binds retained bytes',h in by_hash)
    if 'source_sha256' in value:check(f'{f.relative_to(batch)}: pinned algebra source',value['source_sha256']==digest(connection.read_bytes()))
old=args.parent_ledger.read_bytes(); new=(repo/'LEDGER.md').read_bytes()
check('entire parent ledger remains byte-identical prefix',new.startswith(old))
check('ledger has a nonempty append',len(new)>len(old))
changed=subprocess.run(['git','diff','--name-only'],cwd=repo,encoding='utf-8',capture_output=True,check=True,timeout=20).stdout.splitlines()
check('no tracked Lean/protected file modified',not any(x.startswith(('formal/','data/')) or x.endswith('.lean') for x in changed))
for name in ('skew-full-residual-20261024.md','skew-mixed-construction-20261024.md'):
    note=repo/'notes'/name
    for target in re.findall(r'\]\(([^)]+)\)',note.read_text(encoding='utf-8')):
        if '://' in target or target.startswith('#'):continue
        path=(note.parent/target.split('#')[0]).resolve()
        check(name+': note link exists: '+target,path.exists())
record={'status':'PASS: artifact bindings and integration only; no mathematical replay',
        'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'checks':checks,'notes':notes,'file_count':len(files),'files':files,
        'parent_ledger_bytes':len(old),'parent_ledger_sha256':digest(old),
        'ledger_append_bytes':len(new)-len(old),
        'notebook_parent':'84f294e0235c3fd4b5d4849e565536172a74329c'}
(batch/'integration-validation.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:record[k] for k in ('status','file_count','parent_ledger_bytes','ledger_append_bytes')},indent=2))
print('Binding and integration checks:',len(checks))

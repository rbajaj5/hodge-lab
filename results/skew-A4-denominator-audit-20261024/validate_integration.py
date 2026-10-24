"""Artifact and notebook checks only; no mathematical replay."""
from pathlib import Path
import datetime, hashlib, json, re, subprocess

repo=Path('C:/Users/anaxe/Documents/Codex/hl-source-20261023')
work=Path(__file__).resolve().parent
audit=repo/'results/skew-A4-denominator-audit-20261024'
parent='a773c34804b3d0e1e6db2e1b6e31d89f3c3455cf'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*a): return subprocess.run(['git',*a],cwd=repo,capture_output=True,check=True,timeout=30).stdout
checks=[]
def check(name,condition):
    if not condition: raise RuntimeError(name)
    checks.append(name)

check('unchanged integration parent',git('rev-parse','HEAD').decode('utf-8').strip()==parent)
prior=git('show',f'{parent}:LEDGER.md')
current=(repo/'LEDGER.md').read_bytes()
check('all parent ledger bytes preserved',current.startswith(prior) and len(current)>len(prior))
check('checkpoint 154 appended once',current[len(prior):].count(b'### Checkpoint 154 ')==1)
connection=repo/'results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'
check('connection source pin',sha(connection)=='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d')
record=json.loads((audit/'pro-delivery/import-validation.json').read_text(encoding='utf-8'))
for name,h in record['files'].items(): check('Pro original bytes: '+name,sha(repo/name)==h)
pins=json.loads((repo/'results/skew-A4-denominator-20261024/source-pins.json').read_text(encoding='utf-8'))
for item in pins['read_only_connector_snapshots']:
    original=git('show',f"{parent}:{item['path']}")
    snapshot=repo/'results/skew-A4-denominator-20261024'/item['snapshot']
    check('actual Git parent snapshot: '+item['path'],snapshot.read_bytes()==original)
for name in ['algebra/artifact-manifest.json','checker/freeze-manifest.json']:
    manifest=audit/name
    for item in json.loads(manifest.read_text(encoding='utf-8'))['files']:
        check('frozen evidence: '+name+' -> '+item['path'],sha(manifest.parent/item['path'])==item['sha256'])
for name in ['notes/skew-A4-denominator-audit-20261024.md','notes/skew-A4-denominator-20261024.md']:
    p=repo/name
    for link in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
        if '://' in link or link.startswith('#'): continue
        path=link.split('#',1)[0].replace('%20',' ')
        check('local link: '+name+' -> '+link,(p.parent/path).exists())
for name in ['AGENTS.md','formal/README.md']:
    check('unchanged '+name,(repo/name).read_bytes()==git('show',f'{parent}:{name}'))
check('separate local report preserved',sha(audit/'checker/A4-minor.json')=='c39d7b4ee6207b1ca65f0c545bfd7925d7fc847a1b9ea7cf987d008e9dadb36d')
check('separate local mathematical script preserved',sha(audit/'checker/audit_A4_regenerated_minor.py')=='cefa9592c78c0ccb8b5c1d9ff5e6e6f8473410d43b19484e1fbf9ba013d17faa')
check('local algebra script preserved',sha(audit/'algebra/check_top_pole.py')=='7ca72b6082aeb6cd75a75062b24068a1520345e08c46ebe179284e79acd11364')
git('diff','--check')
out={'status':'PASS: source bindings, delivered original bytes, local links, scoped artifacts and append-only ledger',
     'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'parent':parent,
     'parent_ledger_bytes':len(prior),'appended_ledger_bytes':len(current)-len(prior),
     'mathematical_replay':False,'checks':checks}
(audit/'integration-validation.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='checks'},indent=2))

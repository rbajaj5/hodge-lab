"""Artifact/notebook checks only; no mathematical replay."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess
repo=Path('C:/Users/anaxe/Documents/Codex/hl-source-20261023')
audit=repo/'results/skew-A7-denominator-audit-20261024'
parent='030d13b75270f6ad1a774e9c11321038fe6305e9'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*a):return subprocess.run(['git',*a],cwd=repo,capture_output=True,check=True,timeout=30).stdout
checks=[]
def check(name,condition):
 if not condition:raise RuntimeError(name)
 checks.append(name)
check('unchanged integration parent',git('rev-parse','HEAD').decode('utf-8').strip()==parent)
prior=git('show',parent+':LEDGER.md');current=(repo/'LEDGER.md').read_bytes()
check('all parent ledger bytes preserved',current.startswith(prior) and len(current)>len(prior))
check('checkpoint 157 appended once',current[len(prior):].count(b'### Checkpoint 157 ')==1)
connection=repo/'results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'
check('connection source pin',sha(connection)=='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d')
record=json.loads((audit/'pro-delivery/import-validation.json').read_text(encoding='utf-8'))
for name,h in record['files'].items():check('Pro original bytes: '+name,sha(repo/name)==h)
pins=json.loads((repo/'results/skew-A7-denominator-20261024/source-pins.json').read_text(encoding='utf-8'))
check('Pro actual integration parent',pins['integration_parent']==parent)
for item in pins['read_only_connector_snapshots']:
 original=git('show',f"{parent}:{item['path']}")
 snapshot=repo/'results/skew-A7-denominator-20261024'/item['stored_as']
 check('actual Git parent snapshot: '+item['path'],snapshot.read_bytes()==original)
for name in ['algebra/artifact-manifest.json','checker/freeze-manifest.json']:
 manifest=audit/name
 for item in json.loads(manifest.read_text(encoding='utf-8'))['files']:
  check('frozen evidence: '+name+' -> '+item['path'],sha(manifest.parent/item['path'])==item['sha256'])
for name in ['notes/skew-A7-denominator-audit-20261024.md','notes/skew-A7-denominator-20261024.md']:
 path=repo/name
 for link in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
  if '://' in link or link.startswith('#'):continue
  check('local link: '+name+' -> '+link,(path.parent/link.split('#',1)[0].replace('%20',' ')).exists())
for name in ['AGENTS.md','formal/README.md']:
 check('unchanged '+name,(repo/name).read_bytes()==git('show',parent+':'+name))
check('separate local report preserved',sha(audit/'checker/A7-minor.json')=='9ab4f9b0617984a5780e5e042f5b660bd86c4dfb0395df24e4a5a411dc655526')
check('separate local script preserved',sha(audit/'checker/audit_A7_regenerated_minor.py')=='07ddcf92422a9147799d31bfc623f54c81f9df498f2421f0953eb9b2c09725e0')
check('local algebra script preserved',sha(audit/'algebra/check_order7.py')=='aca70673f8a5273e56bbe4f60066102678c3a7157199c8fde29415455c7a1cab')
git('diff','--check')
out={'status':'PASS: source bindings, delivered original bytes, local links, scoped artifacts and append-only ledger',
 'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'parent':parent,'parent_ledger_bytes':len(prior),
 'appended_ledger_bytes':len(current)-len(prior),'mathematical_replay':False,'checks':checks}
(audit/'integration-validation.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='checks'},indent=2))

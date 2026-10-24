"""Artifact/notebook checks only; no mathematical replay."""
from pathlib import Path
import datetime,hashlib,json,re,subprocess
repo=Path('C:/Users/anaxe/Documents/Codex/hl-source-20261023')
audit=repo/'results/skew-A5-denominator-audit-20261024'
parent='ce22ec3a0636e9c2dbe7e90e1a36ae63f5f4b44a'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def git(*a):return subprocess.run(['git',*a],cwd=repo,capture_output=True,check=True,timeout=30).stdout
checks=[]
def check(name,condition):
 if not condition:raise RuntimeError(name)
 checks.append(name)
check('unchanged integration parent',git('rev-parse','HEAD').decode('utf-8').strip()==parent)
prior=git('show',parent+':LEDGER.md');current=(repo/'LEDGER.md').read_bytes()
check('all parent ledger bytes preserved',current.startswith(prior) and len(current)>len(prior))
check('checkpoint 155 appended once',current[len(prior):].count(b'### Checkpoint 155 ')==1)
connection=repo/'results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'
check('connection source pin',sha(connection)=='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d')
record=json.loads((audit/'pro-delivery/import-validation.json').read_text(encoding='utf-8'))
for name,h in record['files'].items():check('Pro original bytes: '+name,sha(repo/name)==h)
pins=json.loads((repo/'results/skew-A5-denominator-20261024/source-pins.json').read_text(encoding='utf-8'))
check('Pro actual integration parent',pins['integration_parent']==parent)
for item in pins['read_only_connector_snapshots']:
 original=git('show',f"{parent}:{item['path']}")
 snapshot=repo/'results/skew-A5-denominator-20261024'/item['snapshot']
 check('actual Git parent snapshot: '+item['path'],snapshot.read_bytes()==original)
for name in ['algebra/artifact-manifest.json','checker/freeze-manifest.json']:
 manifest=audit/name
 for item in json.loads(manifest.read_text(encoding='utf-8'))['files']:
  check('frozen evidence: '+name+' -> '+item['path'],sha(manifest.parent/item['path'])==item['sha256'])
for name in ['notes/skew-A5-denominator-audit-20261024.md','notes/skew-A5-denominator-20261024.md']:
 path=repo/name
 for link in re.findall(r'\]\(([^)]+)\)',path.read_text(encoding='utf-8')):
  if '://' in link or link.startswith('#'):continue
  check('local link: '+name+' -> '+link,(path.parent/link.split('#',1)[0].replace('%20',' ')).exists())
for name in ['AGENTS.md','formal/README.md']:
 check('unchanged '+name,(repo/name).read_bytes()==git('show',parent+':'+name))
check('separate local report preserved',sha(audit/'checker/A5-minor.json')=='3ead7fda7eb606548b1b12604324a781ab452fb38395f13e112cfe631c36437f')
check('separate local script preserved',sha(audit/'checker/audit_A5_regenerated_minor.py')=='83f4b0e432d20fc769100f57c13c5909db9327bbe3b799024537394f2bb49404')
check('local algebra script preserved',sha(audit/'algebra/check_order5.py')=='bad3f26c1f1f07c944024b6acdfa91f0c4953951a3c8f434ebd66b24850e8d8c')
git('diff','--check')
out={'status':'PASS: source bindings, delivered original bytes, local links, scoped artifacts and append-only ledger',
 'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'parent':parent,'parent_ledger_bytes':len(prior),
 'appended_ledger_bytes':len(current)-len(prior),'mathematical_replay':False,'checks':checks}
(audit/'integration-validation.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='checks'},indent=2))

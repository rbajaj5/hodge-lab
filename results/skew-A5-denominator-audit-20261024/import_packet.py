"""Import only new verified manifest files; preserve original payload bytes."""
from pathlib import Path
import argparse,datetime,hashlib,json,shutil
p=argparse.ArgumentParser();p.add_argument('--manifest-sha256',required=True);args=p.parse_args()
base=Path(__file__).resolve().parent
repo=Path('C:/Users/anaxe/Documents/Codex/hl-source-20261023')
record=json.loads((base/'packet-receipt.json').read_text(encoding='utf-8'))
src=Path(record['payload_root'])
assert record['manifest_sha256']==args.manifest_sha256
for name,h in record['files'].items():
    assert name=='notes/skew-A5-denominator-20261024.md' or name.startswith('results/skew-A5-denominator-20261024/'),name
    f=(src/name).resolve();dest=(repo/name).resolve()
    assert f.is_relative_to(src.resolve()) and dest.is_relative_to(repo.resolve())
    assert hashlib.sha256(f.read_bytes()).hexdigest()==h,name
    assert not dest.exists(),str(dest)
for name in record['files']:
    dest=repo/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src/name,dest)
delivery=repo/'results/skew-A5-denominator-audit-20261024/pro-delivery'
delivery.mkdir()
for name in ('HANDOFF.txt','MANIFEST.sha256'):
    shutil.copyfile(Path(record['metadata_root'])/name,delivery/name)
shutil.copyfile(base/'packet-receipt.json',delivery/'archive-verification.json')
(repo/'results/skew-A5-denominator-20261024/.gitattributes').write_text('* -text whitespace=cr-at-eol\n*.svg -whitespace\n*.log -whitespace\n',encoding='utf-8')
record.update({'imported_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'method':'Verified and copied only new manifest files; shared files integrated separately, no patch applied.',
 'mathematical_replay':False})
(delivery/'import-validation.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print('Imported',len(record['files']),'new hash-verified Pro payload files; not a mathematical replay.')

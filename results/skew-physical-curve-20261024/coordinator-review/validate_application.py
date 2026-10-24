from pathlib import Path
import hashlib
import json
import subprocess

root=Path(__file__).resolve().parent
handoff=Path('C:/Users/anaxe/Documents/Codex/pcf-handoff')
repo=Path('C:/Users/anaxe/Documents/Codex/hl-source-20261023')
def require(ok,message):
    if not ok:
        raise RuntimeError(message)
meta=json.loads((handoff/'handoff.json').read_text(encoding='utf-8'))
require(meta['parent']=='e2182223a0395cfb758a2ee09e304eb940b7a67a','Wrong parent')
files=set()
for line in (handoff/'MANIFEST.sha256').read_text(encoding='utf-8').splitlines():
    digest,name=line.split('  ',1)
    require(hashlib.sha256((handoff/name).read_bytes()).hexdigest()==digest,'Manifest mismatch: '+name)
    files.add(name)
actual={p.relative_to(handoff).as_posix() for p in handoff.rglob('*') if p.is_file()}
require(actual==files|{'MANIFEST.sha256'},'Unmanifested/missing archive members')
tree=subprocess.check_output(['git','write-tree'],cwd=repo,timeout=30).decode('ascii').strip()
require(tree==meta['expected_staged_tree'],'Applied tree differs from handoff')
for name in meta['changed_paths']:
    require((repo/name).read_bytes()==(handoff/'payload'/name).read_bytes(),'Payload mismatch: '+name)
receipt={'status':'PASS','parent':meta['parent'],'expected_tree':meta['expected_staged_tree'],
         'actual_tree':tree,'manifest_members_verified':len(files),
         'payload_files_verified':len(meta['changed_paths']),
         'patch_sha256':hashlib.sha256((handoff/'physical-curve-realization.patch').read_bytes()).hexdigest(),
         'scope':'Exact source payload and intermediate staged tree before coordinator evidence additions'}
(root/'patch-application.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
print(json.dumps(receipt))

"""Final five-minute handoff: changed files, binary-safe patch and SHA256s.

No full-parent archive, expanded submodules, proof replay or patch-application
audit. The coordinator owns final application, review and publication.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[2]
BASE = 'bf0c69287865ba00d3e651cdbc4d0f881deba4db'
BATCH = ROOT/'results/skew-distinct-roots-20261023'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    before = time.monotonic()
    out = Path(sys.argv[1]).resolve()
    out.mkdir(parents=True,exist_ok=False)
    commands = []
    def git(arguments):
        cp = subprocess.run(['git',*arguments],cwd=ROOT,capture_output=True,timeout=60)
        commands.append({'command':['git',*arguments],'exit_code':cp.returncode,
                         'stdout_sha256':sha(cp.stdout),'stderr_sha256':sha(cp.stderr)})
        if cp.returncode:
            raise RuntimeError('Git command failed; no retry: '+repr(arguments))
        return cp.stdout
    parent = git(['rev-parse','HEAD']).decode().strip()
    if parent != BASE:
        raise RuntimeError('Unexpected parent')
    tree = git(['write-tree']).decode().strip()
    names = [p.decode() for p in git(['diff','--cached','--name-only','-z',BASE]).split(b'\0') if p]
    patch = out/'hodge-distinct-roots-bf0c692.patch'
    patch.write_bytes(git(['diff','--cached','--binary','--full-index',BASE]))
    (out/'HANDOFF.md').write_bytes((BATCH/'HANDOFF.md').read_bytes())
    (out/'hodge-distinct-roots.png').write_bytes((BATCH/'visualization-02/generic-distinct-roots.png').read_bytes())
    metadata = {'status':'READY_FOR_COORDINATOR_APPLICATION','parent':BASE,
        'upstream':'b790130d43b49ec0ddc6865d0bdc949eeeee2319','staged_tree':tree,
        'changed_files':len(names),'patch_sha256':sha(patch.read_bytes()),
        'scope':'Changed-file payload only; unchanged parent files and submodule contents omitted per coordinator instruction',
        'mathematical_result':'Generic distinct-root dependency closed locally in Lean',
        'proof_sha256':'7edbe6bde88a36cc68e33cb270cc8a349449ab45e4699df91d806be94138f08b',
        'final_lean_receipt_sha256':'8042bce23d5f79de6f3265da9b43ba0dcae9f42654d8a8b60a076dfb105d1835',
        'initial_patch_application':'PASS before final packaging-only additions; evidence preserved',
        'final_patch_application':'Delegated to coordinator; not rerun under final five-minute bound',
        'full_archive_attempt':'Stopped; exact failure and script preserved in payload/integration record',
        'new_remote_ci':'Not executed','commit_or_push_by_this_chat':False,
        'commands':commands}
    (out/'handoff.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    members = {}
    for rel in names:
        members['payload/'+rel] = git(['show',':'+rel])
    for path in [patch,out/'HANDOFF.md',out/'hodge-distinct-roots.png',out/'handoff.json']:
        members[path.name] = path.read_bytes()
    manifest = ''.join(sha(data)+'  '+name+'\n' for name,data in sorted(members.items()))
    (out/'MANIFEST.sha256').write_text(manifest,encoding='utf-8')
    archive_path = out/'hodge-distinct-roots-bf0c692.zip'
    with zipfile.ZipFile(archive_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as archive:
        for name,data in sorted(members.items()):
            info = zipfile.ZipInfo(name,(2026,10,23,23,7,2))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644<<16
            archive.writestr(info,data)
        archive.writestr('MANIFEST.sha256',manifest.encode('utf-8'))
    report = {'status':'PACKAGED','parent':BASE,'staged_tree':tree,'changed_files':len(names),
        'elapsed_seconds':time.monotonic()-before,'zip_bytes':archive_path.stat().st_size,
        'patch_bytes':patch.stat().st_size,'additional_audits_run':False,
        'files_sha256':{p.name:sha(p.read_bytes()) for p in [archive_path,patch,out/'HANDOFF.md',
            out/'MANIFEST.sha256',out/'hodge-distinct-roots.png',out/'handoff.json']}}
    (out/'package-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    checksums = dict(report['files_sha256'])
    checksums['package-report.json'] = sha((out/'package-report.json').read_bytes())
    (out/'SHA256SUMS').write_text(''.join(h+'  '+name+'\n' for name,h in sorted(checksums.items())),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()

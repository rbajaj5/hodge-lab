"""Package the staged proposal and verify its binary-safe patch in a new worktree.

This performs no commit, push, fetch or remote write. It requires a fresh
absolute output directory and a fresh local verification-worktree path.
All Git commands and outputs are retained in the package. The ZIP includes
the entire staged repository tree, without .git or build caches, plus the
patch, handoff instructions, parent pin and a per-member SHA256 manifest.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import tarfile
import time
import zipfile

ROOT = Path(__file__).resolve().parents[2]
BASE = 'bf0c69287865ba00d3e651cdbc4d0f881deba4db'
BATCH = ROOT/'results/skew-distinct-roots-20261023'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--verify-worktree', type=Path, required=True)
    args = parser.parse_args()
    out, verify = args.output_dir.resolve(), args.verify_worktree.resolve()
    require(not verify.exists(), 'Verification worktree must be fresh')
    out.mkdir(parents=True, exist_ok=False)
    logs = out/'packaging'; logs.mkdir()
    commands = []
    started = time.monotonic()

    def git(label, arguments, cwd=ROOT):
        before = time.monotonic()
        cp = subprocess.run(['git', *arguments], cwd=cwd, capture_output=True, timeout=120)
        (logs/(label+'.stdout.log')).write_bytes(cp.stdout)
        (logs/(label+'.stderr.log')).write_bytes(cp.stderr)
        commands.append({'label':label, 'command':['git', *arguments], 'cwd':str(cwd),
            'exit_code':cp.returncode, 'elapsed_seconds':time.monotonic()-before,
            'timeout_seconds':120, 'stdout_sha256':sha(cp.stdout), 'stderr_sha256':sha(cp.stderr)})
        (logs/'commands.json').write_text(json.dumps(commands,indent=2)+'\n',encoding='utf-8')
        require(cp.returncode == 0, 'Git command failed; no retry: '+label)
        return cp.stdout

    require(git('parent', ['rev-parse','HEAD']).decode().strip() == BASE, 'Unexpected parent')
    require(not git('unstaged-diff', ['diff','--name-only']).strip(), 'Unstaged tracked changes remain')
    require(not git('untracked', ['ls-files','--others','--exclude-standard']).strip(),
            'Untracked deliverables remain')
    tree = git('proposal-tree', ['write-tree']).decode().strip()
    patch = out/'hodge-distinct-roots-bf0c692.patch'
    patch.write_bytes(git('binary-patch', ['diff','--cached','--binary','--full-index',BASE]))
    git('isolated-apply-checkout', ['worktree','add','--detach',str(verify),BASE])
    git('patch-check', ['apply','--check','--index',str(patch)], verify)
    git('patch-apply', ['apply','--index',str(patch)], verify)
    applied_tree = git('applied-tree', ['write-tree'], verify).decode().strip()
    require(applied_tree == tree, 'Applied patch tree differs from staged proposal')
    history = json.loads((BATCH/'historical-files-sha256.json').read_text())
    changed_history = [p for p,h in history.items() if sha((verify/p).read_bytes()) != h]
    require(not changed_history, 'Patch application changed historical result bytes')
    baseline = json.loads((BATCH/'bootstrap-preservation.json').read_text())
    applied_ledger = (verify/'LEDGER.md').read_bytes()
    require(sha(applied_ledger[:baseline['ledger_bytes']]) == baseline['ledger_sha256'],
            'Patch application changed ledger prefix')
    patch_verification = {'status':'PASS','executor':'Pro chat root','parent':BASE,
        'staged_tree':tree,'applied_tree':applied_tree,'patch_sha256':sha(patch.read_bytes()),
        'historical_files_unchanged':len(history),'ledger_prefix_bytes':baseline['ledger_bytes'],
        'ledger_prefix_sha256':baseline['ledger_sha256'],
        'commands_file':'packaging/commands.json','no_commit_or_remote_write':True}
    (logs/'patch-verification.json').write_text(json.dumps(patch_verification,indent=2)+'\n',encoding='utf-8')

    entries = []
    for line in git('tree-entries',['ls-tree','-r','-z',tree]).split(b'\0'):
        if line:
            header, path = line.split(b'\t',1)
            mode, kind, object_id = header.decode('ascii').split()
            entries.append({'path':path.decode('utf-8'), 'mode':mode,
                            'type':kind, 'object_id':object_id})
    gitlinks = [entry for entry in entries if entry['mode']=='160000']
    expected_repo_count = sum(entry['type']=='blob' for entry in entries)
    (out/'SUBMODULES.json').write_text(json.dumps({'scope':'Exact existing Git-link entries; submodule worktrees are not materialized or fetched',
        'gitlinks':gitlinks},indent=2)+'\n',encoding='utf-8')
    metadata = {'parent':BASE,'upstream':'b790130d43b49ec0ddc6865d0bdc949eeeee2319',
        'staged_tree':tree,'patch_sha256':sha(patch.read_bytes()),
        'proof_sha256':'7edbe6bde88a36cc68e33cb270cc8a349449ab45e4699df91d806be94138f08b',
        'final_checker_receipt_sha256':'8042bce23d5f79de6f3265da9b43ba0dcae9f42654d8a8b60a076dfb105d1835',
        'local_result':'Generic distinct-root dependency closed over Q(v)(t)(a) in its full splitting field',
        'new_remote_ci':'Not executed; awaiting coordinator publication',
        'prior_remote_ci':'40026828482 succeeded on 5d216691981cdb248073209bdc80df86021412d4',
        'publication_owner':'Original Goal coordinator 01a145f0-1bc3-7321-8c36-83a883bf061f',
        'archive_scope':'All staged repository blobs plus exact existing submodule Git-link pins, patch/instructions/logs; no Git object database, expanded submodules or Lean/Mathlib build cache',
        'manifest_scope':'Every regular-file ZIP member except MANIFEST.sha256 itself; empty Git-link directories are described in SUBMODULES.json',
        'limits':['No universal specialization claim','No unsplit descent','No physical differential-source normalization',
                  'No primitive, global clearing, HasCertificate or solve','No commit, push or upstream publication by this chat']}
    (out/'handoff.json').write_text(json.dumps(metadata,indent=2)+'\n',encoding='utf-8')
    (out/'PARENT_SHA').write_text(BASE+'\n',encoding='ascii')
    guide = (BATCH/'HANDOFF.md').read_bytes()
    (out/'HANDOFF.md').write_bytes(guide)
    shutil.copyfile(BATCH/'visualization-02/generic-distinct-roots.png',out/'hodge-distinct-roots.png')
    zip_path = out/'hodge-distinct-roots-bf0c692.zip'
    manifest = {}
    directory_names = set()
    stamp = (2026,10,23,23,7,2)

    with zipfile.ZipFile(zip_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as archive:
        def add(name, data, mode=0o644):
            info = zipfile.ZipInfo(name,stamp)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o100000|mode)<<16
            info.create_system = 3
            archive.writestr(info,data)
            manifest[name] = sha(data)

        proc = subprocess.Popen(['git','archive','--format=tar',tree],cwd=ROOT,
                                stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        with tarfile.open(fileobj=proc.stdout,mode='r|') as source:
            for member in source:
                if member.isdir():
                    continue
                require(member.isfile(), 'Unexpected non-file in repository archive: '+member.name)
                data = source.extractfile(member).read()
                require(not member.name.startswith('/') and '..' not in Path(member.name).parts,
                        'Unsafe archive path')
                add('repository/'+member.name,data,member.mode)
                if member.name in history:
                    require(sha(data)==history[member.name], 'Git archive changed historical bytes')
        require(proc.wait(timeout=120)==0, 'Git archive failed')
        require(not proc.stderr.read(), 'Unexpected Git archive diagnostics')
        actual_repo_count = sum(p.startswith('repository/') for p in manifest)
        require(actual_repo_count==expected_repo_count, 'Incomplete repository archive')
        for entry in gitlinks:
            info = zipfile.ZipInfo('repository/'+entry['path']+'/',stamp)
            info.external_attr = (0o040755<<16)|0x10
            info.create_system = 3
            archive.writestr(info,b'')
            directory_names.add(info.filename)
        for path in [patch,out/'handoff.json',out/'PARENT_SHA',out/'HANDOFF.md',out/'SUBMODULES.json',out/'hodge-distinct-roots.png']:
            add(path.name,path.read_bytes())
        for path in sorted(logs.rglob('*')):
            if path.is_file():
                add(path.relative_to(out).as_posix(),path.read_bytes())
        manifest_text = ''.join(h+'  '+name+'\n' for name,h in sorted(manifest.items()))
        (out/'MANIFEST.sha256').write_text(manifest_text,encoding='utf-8')
        info = zipfile.ZipInfo('MANIFEST.sha256',stamp)
        info.compress_type = zipfile.ZIP_DEFLATED
        archive.writestr(info,manifest_text.encode('utf-8'))

    with zipfile.ZipFile(zip_path) as archive:
        for name, expected in manifest.items():
            require(sha(archive.read(name))==expected, 'Archive verification failed: '+name)
        require(set(archive.namelist())==set(manifest)|directory_names|{'MANIFEST.sha256'}, 'Unexpected archive member')
    report = {'status':'PASS','parent':BASE,'staged_tree':tree,'applied_tree':applied_tree,
        'zip_members':len(manifest)+len(directory_names)+1,'repository_files':actual_repo_count,'preserved_gitlinks':len(gitlinks),
        'manifested_members':len(manifest),'elapsed_seconds':time.monotonic()-started,
        'archive_bytes':zip_path.stat().st_size,'patch_bytes':patch.stat().st_size,
        'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'git_commit_created':False,'remote_write_attempted':False,
        'files_sha256':{p.name:sha(p.read_bytes()) for p in [zip_path,patch,out/'MANIFEST.sha256',
                        out/'HANDOFF.md',out/'hodge-distinct-roots.png',out/'handoff.json']}}
    (out/'package-report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    checksums = dict(report['files_sha256'])
    checksums['package-report.json'] = sha((out/'package-report.json').read_bytes())
    (out/'SHA256SUMS').write_text(''.join(h+'  '+name+'\n' for name,h in sorted(checksums.items())),encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__ == '__main__':
    main()

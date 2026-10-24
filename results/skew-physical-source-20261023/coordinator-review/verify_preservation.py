"""Verify immutable prior bytes, append-only ledger, and staged text."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--repo', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    args = p.parse_args()
    here = Path(__file__).resolve().parent
    prior = json.loads((here/'prior-bytes.json').read_text(encoding='utf-8'))
    for name, expected in prior.items():
        if hashlib.sha256((args.repo/name).read_bytes()).hexdigest() != expected:
            raise RuntimeError('Prior bytes changed: '+name)
    parent = subprocess.check_output(['git','show','bbb8aa406cd2a8b5ddb06d6e14358781b9c215e9:LEDGER.md'],cwd=args.repo,timeout=15)
    if hashlib.sha256(parent).hexdigest() != 'e636477a85bfbdedbaac88202bb2c461cec32db5c914d186fdaffeb8977a3193':
        raise RuntimeError('Parent ledger pin differs')
    current = (args.repo/'LEDGER.md').read_bytes()
    if not current.startswith(parent):
        raise RuntimeError('Ledger history changed')
    appended = current[len(parent):].decode('utf-8', errors='strict')
    if '\ufffd' in appended:
        raise RuntimeError('Replacement character in ledger append')
    names = subprocess.check_output(['git','diff','--cached','--name-only','-z'],cwd=args.repo,timeout=15).decode('utf-8').split('\0')
    texts = 0
    for name in filter(None,names):
        path = args.repo/name
        if path.suffix.lower() in ['.md','.py','.lean','.json','.yml','.yaml','.toml'] and path.exists():
            path.read_bytes().decode('utf-8',errors='strict')
            texts += 1
    proc = subprocess.run(['git','diff','--cached','--check','--','README.md','LEDGER.md','notes','formal','scripts','.github'],cwd=args.repo,timeout=20,capture_output=True,text=True,encoding='utf-8',check=True)
    receipt = {'status':'PASS','prior_files_unchanged':len(prior),
               'parent_ledger_bytes':len(parent),'appended_ledger_bytes':len(current)-len(parent),
               'parent_ledger_sha256':hashlib.sha256(parent).hexdigest(),
               'staged_text_files_utf8':texts,'whitespace_check':proc.stdout,
               'scope':'Historical-byte, UTF-8 and staged-whitespace review; no mathematics'}
    args.output.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()

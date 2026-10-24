"""Check historical bytes and the actual staged ledger; no mathematical replay."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parent
PARENT = 'e2182223a0395cfb758a2ee09e304eb940b7a67a'
LEDGER_SHA = 'f4e1e853360368889cd83be8536d4f0c509a73464d391311c91639c326abbc66'


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()

    def git(*command):
        return subprocess.check_output(['git', *command], cwd=args.repo, timeout=30)

    prior = json.loads((ROOT / 'prior-bytes.json').read_text(encoding='utf-8'))
    staged_blobs = {}
    for entry in filter(None, git('ls-files', '--stage', '-z').decode('utf-8').split('\0')):
        metadata, path = entry.split('\t', 1)
        mode, blob, stage = metadata.split()
        require(stage == '0', 'Unresolved index entry: ' + path)
        staged_blobs[path] = blob
    for path, expected in prior.items():
        require(hashlib.sha256((args.repo / path).read_bytes()).hexdigest() == expected['sha256'],
                'Historical worktree bytes changed: ' + path)
        require(staged_blobs.get(path) == expected['git_blob'],
                'Historical staged bytes changed: ' + path)

    parent = git('show', PARENT + ':LEDGER.md')
    require(hashlib.sha256(parent).hexdigest() == LEDGER_SHA, 'Wrong ledger parent')
    staged = git('show', ':LEDGER.md')
    require(staged == (args.repo / 'LEDGER.md').read_bytes(), 'Unstaged ledger changes')
    require(staged.startswith(parent), 'Ledger history changed')
    append = staged[len(parent):].decode('utf-8', errors='strict')
    require('\ufffd' not in append, 'Replacement character in ledger append')
    names = list(filter(None, git('diff', '--cached', '--name-only', '-z').decode('utf-8').split('\0')))
    texts = {}
    for name in names:
        if Path(name).suffix.lower() in {'.md', '.py', '.lean', '.json', '.yml', '.yaml', '.toml', '.svg', '.txt'}:
            raw = git('show', ':' + name)
            text = raw.decode('utf-8', errors='strict')
            require('\ufffd' not in text, 'Replacement character in staged text: ' + name)
            texts[name] = hashlib.sha256(raw).hexdigest()
    whitespace = subprocess.run(['git', 'diff', '--cached', '--check'], cwd=args.repo,
                                timeout=30, capture_output=True, encoding='utf-8')
    subprocess.run(['git', 'diff', '--cached', '--check', '--', '.', ':(exclude)**/*.log'],
                   cwd=args.repo, timeout=30, check=True)
    receipt = {
        'status': 'PASS', 'parent': PARENT,
        'prior_files_unchanged': len(prior), 'parent_ledger_bytes': len(parent),
        'parent_ledger_sha256': LEDGER_SHA, 'appended_ledger_bytes': len(staged)-len(parent),
        'staged_text_files_utf8': len(texts), 'staged_text_sha256': texts,
        'unfiltered_whitespace_exit': whitespace.returncode,
        'unfiltered_whitespace_output': whitespace.stdout+whitespace.stderr,
        'preserved_log_whitespace': 'Raw execution logs retain original whitespace; all non-log staged files pass git diff --check.',
        'scope': 'Historical worktree/index bytes, append-only ledger, staged UTF-8 and whitespace; no mathematics',
    }
    args.output.write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: v for k, v in receipt.items() if k != 'staged_text_sha256'}))


if __name__ == '__main__':
    main()

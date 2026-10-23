"""Check this batch's authoritative upstream snapshot; no prior mathematics rerun.

Run from the repository root with --output-dir pointing to a new directory.
Relative output paths are relative to formal, as for the Lean checkers.
"""
from pathlib import Path
import datetime
import hashlib
import json
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
FORMAL = ROOT / 'formal'
sys.path.insert(0, str(FORMAL))
from fresh_receipts import fresh_output_dir

BATCH = Path(__file__).resolve().parent
OUT = None


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def fields(path):
    lines = path.read_text(encoding='utf-8').splitlines()
    result = {}
    for key in ('id', 'F', 'q', 'A'):
        matches = [i for i, line in enumerate(lines) if line.startswith(key + ':')]
        require(len(matches) == 1, 'Missing or duplicate target field: ' + key)
        i = matches[0]
        value = [lines[i].split(':', 1)[1].strip()]
        for line in lines[i + 1:]:
            if not line.startswith((' ', '\t')):
                break
            value.append(line.strip())
        result[key] = ' '.join(value)
    return result


def main():
    global OUT
    started = time.monotonic()
    OUT = fresh_output_dir(FORMAL, 'skew-distinct-source', [BATCH / 'inputs',
        ROOT / 'results/ci-receipt-physical-cover-20261023',
        FORMAL / 'results/skew-physical-cover'])
    manifest = BATCH / 'source-pins.json'
    pins = json.loads(manifest.read_text(encoding='utf-8'))
    checked = {manifest.relative_to(ROOT).as_posix(): sha(manifest),
               Path(__file__).relative_to(ROOT).as_posix(): sha(Path(__file__)),
               'formal/fresh_receipts.py': sha(FORMAL / 'fresh_receipts.py')}
    for pin in pins['pins']:
        path = ROOT / pin['path']
        raw = path.read_bytes()
        require(hashlib.sha256(raw).hexdigest() == pin['sha256'], 'Snapshot hash changed')
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        require(blob == pin['git_blob'], 'Snapshot Git blob changed')
        checked[pin['path']] = sha(path)
    for name, expected in pins['historical_context_raw_sha256'].items():
        require(sha(ROOT / name) == expected, 'Historical context changed: ' + name)
        checked[name] = expected
    old = fields(ROOT / pins['historical_instance_path'])
    current = fields(ROOT / pins['current_instance_path'])
    require(old == current, 'Literal protected target fields changed')
    require(current['id'] == 'one-reflection-skew', 'Wrong target')
    for name, expected in checked.items():
        require(sha(ROOT / name) == expected, 'Input changed during source check')
    receipt = {'status': 'PASS', 'completed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'command': [sys.executable, '-O', *sys.argv], 'elapsed_seconds': time.monotonic() - started,
        'external_bound_seconds': 60, 'upstream_commit': pins['upstream_commit'],
        'source_sha256': checked, 'literal_protected_fields': current,
        'scope': 'Single-target authoritative instance snapshot and immutable context correspondence only.',
        'reused_evidence': 'Prior literal physical-polynomial binding and remote CI success are reused, not rerun.',
        'limits': ['No new geometric source derivation', 'No generated record.json used as current authority',
                   'No separability proof is supplied by this source check']}
    (OUT / 'validation.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'status': 'PASS', 'output': str(OUT), 'elapsed_seconds': receipt['elapsed_seconds']}))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        if OUT is not None:
            (OUT / 'validation.json').write_text(json.dumps({'status': 'FAIL', 'error': str(error)}, indent=2) + '\n')
        raise

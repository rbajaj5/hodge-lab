"""Check pinned target bytes across the 2026-10-22 atlas update; no math replay."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'results' / 'atlas-monitor-20261022'


def require(ok, message):
    if not ok:
        raise ValueError(message)


def without_render(text):
    lines = text.splitlines(keepends=True)
    require(sum(line.rstrip() == 'render:' for line in lines) == 1, 'render block count')
    kept, skipping = [], False
    for line in lines:
        if line.rstrip() == 'render:':
            skipping = True
            continue
        if skipping and line.strip() and not line[0].isspace():
            skipping = False
        if not skipping:
            kept.append(line)
    return ''.join(kept)


def main():
    receipt = json.loads((DATA / 'fetch-receipt.json').read_text(encoding='utf-8'))
    require(receipt['status'] == 'COMPLETED', 'fetch incomplete')
    require(len(receipt['inputs']) == 8, 'input coverage')
    for entry in receipt['inputs']:
        raw = (DATA / entry['file']).read_bytes()
        require(hashlib.sha256(raw).hexdigest() == entry['sha256'], 'SHA256: ' + entry['file'])
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
        require(blob == entry['git_blob'], 'Git blob: ' + entry['file'])
        raw.decode('utf-8')
    checks = []
    for target in ['one-reflection-skew', 'cyclic-triple-fano']:
        records = [json.loads((DATA / f'{receipt[k][:7]}-{target}-record.json').read_text(encoding='utf-8'))
                   for k in ['old', 'new']]
        a, b = records
        changed = sorted(k for k in a.keys() | b.keys() if a.get(k) != b.get(k))
        require(changed == ['render'], target + ': unexpected record change')
        texts = [(DATA / f'{receipt[k][:7]}-{target}-instance.rec').read_text(encoding='utf-8')
                 for k in ['old', 'new']]
        require(without_render(texts[0]) == without_render(texts[1]), target + ': non-render rec changed')
        require(all(k in b for k in ['F', 'A', 'q']), 'missing mathematical fields')
        checks.append({'target': target, 'record_changed_fields': changed,
                       'instance_rec_non_render_bytes_equal_after_utf8_decoding': True,
                       'F_A_q_and_all_other_record_fields_equal': True})
    result = {'status': 'PASS', 'old': receipt['old'], 'new': receipt['new'],
              'input_files_checked': 8, 'checks': checks,
              'scope': 'Two target records; no mathematical, Lean, mesh or acceptance replay.'}
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()

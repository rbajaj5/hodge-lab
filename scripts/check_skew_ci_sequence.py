"""Replay only the affected forms -> trace CI sequence, preserving history.

Usage: python3 scripts/check_skew_ci_sequence.py NEW_OUTPUT_DIRECTORY
Requires the repository-pinned Lean/Mathlib environment already installed.
No network or earlier accepted research checkers are run here.
"""
from pathlib import Path
import datetime
import hashlib
import json
import os
import platform
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent.parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = Path(sys.argv[1]).resolve()
    output.mkdir(parents=True, exist_ok=False)
    paths = [ROOT / p for p in subprocess.check_output(
        ['git', 'ls-files', '-z', 'formal/results', 'results'], cwd=ROOT
    ).decode().split('\0') if p]
    before = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    records = []
    receipt = {'status': 'IN_PROGRESS', 'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
               'parent': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
               'python': sys.version, 'platform': platform.platform(), 'commands': records,
               'source_sha256': {p: sha(ROOT / p) for p in [
                   'scripts/check_skew_ci_sequence.py', 'formal/fresh_receipts.py',
                   'formal/test_receipt_lifecycle.py', 'formal/check_skew_forms.py',
                   'formal/check_skew_trace_basis.py', '.github/workflows/lean.yml']},
               'scope': 'Affected lifecycle regression and forms then trace, not the entire workflow.'}
    def save():
        (output / 'sequence.json').write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    save()
    try:
        for label, command, bound in [
            ('lifecycle', [sys.executable, '-O', 'test_receipt_lifecycle.py'], 60),
            ('forms', [sys.executable, '-O', 'check_skew_forms.py', '--output-dir', str(output / 'forms')], 610),
            ('trace', [sys.executable, '-O', 'check_skew_trace_basis.py', '--output-dir', str(output / 'trace')], 610)]:
            start = time.monotonic()
            log = output / (label + '.log')
            try:
                with log.open('w', encoding='utf-8') as handle:
                    completed = subprocess.run(command, cwd=ROOT / 'formal', stdout=handle,
                                               stderr=subprocess.STDOUT, timeout=bound)
                code = completed.returncode
            except subprocess.TimeoutExpired:
                code = 124
            records.append({'label': label, 'command': command, 'cwd': 'formal', 'bound_seconds': bound,
                            'exit_code': code, 'elapsed_seconds': time.monotonic() - start,
                            'log': log.name, 'log_sha256': sha(log)})
            save()
            print(json.dumps(records[-1]), flush=True)
            if code:
                raise RuntimeError(label + ' failed or was interrupted; see saved log')
            if label != 'lifecycle':
                checked = json.loads((output / label / 'validation.json').read_text(encoding='utf-8'))
                if checked['status'] != 'PASS':
                    raise RuntimeError(label + ' did not produce a fresh PASS')
        receipt['status'] = 'PASS'
    except Exception as error:
        receipt.update(status='FAIL', error=str(error))
        raise
    finally:
        after = {str(p.relative_to(ROOT)): sha(p) for p in paths}
        changed = [p for p in before if before[p] != after[p]]
        receipt['historical_files_checked'] = len(before)
        receipt['historical_files_changed'] = changed
        receipt['completed_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        if changed:
            receipt['status'] = 'FAIL'
        save()
        if changed:
            raise RuntimeError('Historical evidence changed: ' + repr(changed))


if __name__ == '__main__':
    main()

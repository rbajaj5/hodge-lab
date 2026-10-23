"""Read-only verification of the proposed distinct-root handoff.

No Lean, old checker, mathematical calculation, network write or publication.
Requires a Git checkout at the pinned parent with the proposal staged.
The verification output must be fresh; its own generated receipt is not
part of the staged input it verifies. A package manifest covers that receipt.
"""
from pathlib import Path
import datetime
import hashlib
import json
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
BATCH = ROOT / 'results/skew-distinct-roots-20261023'
BASE = 'bf0c69287865ba00d3e651cdbc4d0f881deba4db'
sys.path.insert(0, str(ROOT / 'formal'))
from fresh_receipts import fresh_output_dir


def sha(data):
    return hashlib.sha256(data).hexdigest()


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, timeout=60)


def read_json(path):
    return json.loads(path.read_text(encoding='utf-8'))


def main():
    started = time.monotonic()
    out = fresh_output_dir(ROOT/'formal', 'skew-distinct-delivery', [
        ROOT/'formal/results/skew-distinct-roots', BATCH/'inputs',
        ROOT/'results/ci-receipt-physical-cover-20261023'])
    report = {'status': 'IN_PROGRESS', 'executor': 'Pro chat root',
              'scope': 'Saved source/log/pin, staged content, UTF-8, links and preservation audit; no proof execution.'}
    try:
        require(git('rev-parse', 'HEAD').decode().strip() == BASE, 'Unexpected Git parent')
        bootstrap = read_json(BATCH/'bootstrap-preservation.json')
        history = read_json(BATCH/'historical-files-sha256.json')
        changed_history = [p for p, h in history.items() if sha((ROOT/p).read_bytes()) != h]
        require(not changed_history, 'Historical result bytes changed: '+repr(changed_history))
        original_ledger = git('show', BASE+':LEDGER.md')
        require(len(original_ledger) == bootstrap['ledger_bytes'] and
                sha(original_ledger) == bootstrap['ledger_sha256'], 'Ledger baseline mismatch')
        append = (BATCH/'checkpoint139-append.md').read_bytes()
        require((ROOT/'LEDGER.md').read_bytes() == original_ledger+append,
                'Ledger is not the exact original prefix followed by the proposed append')
        require(b'## Checkpoint 139 ' in append, 'Missing checkpoint139 heading')

        staged = [p.decode('utf-8') for p in git('diff', '--cached', '--name-only', '-z', BASE).split(b'\0') if p]
        require(bool(staged), 'Proposal has not been staged')
        old_paths = set(p.decode('utf-8') for p in git('ls-tree', '-rz', '--name-only', BASE).split(b'\0') if p)
        changed_old = sorted(set(staged) & old_paths)
        require(changed_old == ['.github/workflows/lean.yml', 'LEDGER.md', 'README.md'],
                'Unexpected modification of a pre-existing file: '+repr(changed_old))
        source_sha = {}
        utf8_count, binary = 0, []
        for rel in staged:
            path = ROOT/rel
            require(path.is_file() and not path.is_symlink(), 'Non-regular staged path: '+rel)
            data = path.read_bytes()
            require(data == git('show', ':'+rel), 'Index/working-byte mismatch: '+rel)
            source_sha[rel] = sha(data)
            if path.suffix == '.png':
                require(data.startswith(b'\x89PNG\r\n\x1a\n'), 'Unexpected PNG signature: '+rel)
                binary.append(rel)
            else:
                data.decode('utf-8', errors='strict')
                require(b'\0' not in data, 'NUL in text artifact: '+rel)
                utf8_count += 1

        final = read_json(BATCH/'lean-development/checker-02/validation.json')
        require(final['status'] == 'PASS', 'Final focused checker is not PASS')
        for rel, expected in final['source_lf_sha256'].items():
            actual = sha((ROOT/'formal'/rel).read_bytes().replace(b'\r\n', b'\n'))
            require(actual == expected, 'Final executed source differs: '+rel)
        require(final['new_public_declarations_audited'] == 48 and
                final['new_modules_replayed'] == 1 and final['positive_controls'] == 9 and
                final['negative_controls'] == 3, 'Unexpected focused scope')
        for command in final['commands']:
            for key, hash_key in [('stdout', 'stdout_sha256'), ('stderr', 'stderr_sha256')]:
                require(sha((BATCH/'lean-development/checker-02'/command[key]).read_bytes())
                        == command[hash_key], 'Saved command log changed')
            require(command['bound_seconds'] <= 120 and command['elapsed_seconds'] < 120,
                    'Lean command bound exceeded')
            require(command['exit_code'] == (1 if command['expected_failure'] else 0),
                    'Unexpected command exit')
        require(final['elapsed_seconds'] < 600, 'Focused checker exceeded bound')
        require(all(set(axioms) <= {'propext','Classical.choice','Quot.sound'}
                    for axioms in final['declaration_axioms'].values()), 'Unexpected axiom')

        review = read_json(BATCH/'source-review/final-review.json')
        require(review['status'] == 'PASS_READ_ONLY_AI_REVIEW_GENERIC_DISTINCT_ROOT_DEPENDENCY_CLOSED',
                'Final adversarial review missing')
        for rel, expected in review['scoped_documentation_and_ci_review']['raw_sha256'].items():
            require(sha((ROOT/rel).read_bytes()) == expected, 'Reviewed document changed: '+rel)
        require(review['verified_saved_lean_receipt']['sha256'] ==
                sha((BATCH/'lean-development/checker-02/validation.json').read_bytes()),
                'Review no longer binds final execution')
        source_pins = read_json(BATCH/'source-pins.json')
        pin_count = 0
        for pin in source_pins['pins']:
            data = (ROOT/pin['path']).read_bytes()
            require(sha(data) == pin['sha256'], 'Current source pin changed')
            blob = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
            require(blob == pin['git_blob'], 'Current source Git blob changed')
            pin_count += 1
        for rel, expected in source_pins['historical_context_raw_sha256'].items():
            require(sha((ROOT/rel).read_bytes()) == expected, 'Historical context pin changed')
            pin_count += 1
        figure = read_json(BATCH/'visualization-02/visualization.json')
        for rel, expected in figure['input_sha256'].items():
            require(sha((ROOT/rel).read_bytes()) == expected, 'Figure input changed: '+rel)
        for rel, expected in figure['output_sha256'].items():
            require(sha((BATCH/'visualization-02'/rel).read_bytes()) == expected, 'Figure output changed')
        require(sha((ROOT/figure['generator']).read_bytes()) == figure['generator_sha256'],
                'Figure generator changed')
        require(read_json(BATCH/'visualization-02/visual-review.json')['status'] == 'PASS',
                'Final figure not visually accepted')

        links = []
        for rel, anchor in [('README.md', ROOT),
                            ('notes/skew-generic-distinct-roots.md', ROOT/'notes'),
                            ('results/skew-distinct-roots-20261023/checkpoint139-append.md', ROOT)]:
            text = (ROOT/rel).read_text(encoding='utf-8')
            for link in re.findall(r'\]\(([^)]+)\)', text):
                if link.startswith(('http:', 'https:', 'mailto:', '#')):
                    continue
                path = (anchor/link.split('#')[0]).resolve()
                require(path.exists(), 'Broken local link '+rel+': '+link)
                links.append({'document':rel, 'target':link})
        edited_source_paths = [p for p in staged if
            (p.endswith(('.py','.lean')) and '/inputs/' not in p and
             '/source-snapshot/' not in p and '/lean-development/' not in p and
             '/visualization-01/' not in p and '/visualization-02/' not in p) or
            p in ['.github/workflows/lean.yml','README.md','LEDGER.md','notes/skew-generic-distinct-roots.md']]
        git('diff', '--cached', '--check', BASE, '--', *edited_source_paths)
        report.update(status='PASS', completed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
            parent=BASE, elapsed_seconds=time.monotonic()-started,
            historical_result_files_checked=len(history), historical_result_files_changed=changed_history,
            ledger_original_bytes=len(original_ledger), ledger_original_sha256=sha(original_ledger),
            ledger_append_bytes=len(append), ledger_append_sha256=sha(append),
            staged_files_checked=len(staged), staged_raw_sha256=source_sha,
            modified_existing_files=changed_old, utf8_text_files_checked=utf8_count,
            binary_png_files=binary, local_links_checked=len(links), local_links=links,
            current_and_historical_source_pins_checked=pin_count,
            final_checker_receipt_sha256=sha((BATCH/'lean-development/checker-02/validation.json').read_bytes()),
            adversarial_review_sha256=sha((BATCH/'source-review/final-review.json').read_bytes()),
            source_diff_whitespace='PASS; captured raw logs and source snapshots are preserved, not normalized',
            posts='Entries1–29 retained in byte-identical original ledger prefix; no post made',
            tally='29 discussion contributions /1 closed maintenance PR /0 accepted authored solves; unchanged',
            remote_writes='None', new_remote_ci='Not executed')
    except Exception as exc:
        report.update(status='FAIL', error=repr(exc), elapsed_seconds=time.monotonic()-started)
        (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        raise
    (out/'validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'status':report['status'], 'historical_files':len(history),
                      'staged_files':len(staged), 'links':len(links),
                      'elapsed_seconds':report['elapsed_seconds']}))


if __name__ == '__main__':
    main()

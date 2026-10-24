"""Review one saved CI receipt against a pinned Git commit; no Lean execution."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import time


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--receipt-dir', type=Path, required=True)
    parser.add_argument('--run-json', type=Path, required=True)
    parser.add_argument('--jobs-json', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--run-id', type=int, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'Refusing to replace an existing receipt')
    start = time.monotonic()
    commit = 'a6cf349bba45ecaaf2f8723479c0e179e97f36bc'
    run = json.loads(args.run_json.read_text(encoding='utf-8'))
    jobs = json.loads(args.jobs_json.read_text(encoding='utf-8'))
    require(run['head_sha'] == commit, 'Run is for a different commit')
    require(run['id'] == args.run_id and run['conclusion'] == 'success', 'Expected full Lean run has not succeeded')
    require(run['name'] == 'Notebook Lean proofs' and run['path'] == '.github/workflows/lean.yml', 'Wrong workflow')
    require(bool(jobs['jobs']), 'No jobs returned')
    require(all(j['run_id'] == run['id'] and j['head_sha'] == commit for j in jobs['jobs']), 'Jobs are not bound to this run and commit')
    require(all(j['conclusion'] == 'success' for j in jobs['jobs']), 'A job did not succeed')
    require(any(s['name'] == 'Check physical coefficient field and all-sheet trace bridge'
                and s['conclusion'] == 'success' for j in jobs['jobs'] for s in j['steps']),
            'New focused step did not succeed')
    raw = (args.receipt_dir / 'validation.json').read_bytes()
    receipt = json.loads(raw)
    require(receipt['status'] == 'PASS' and receipt['worker'] == 'GitHub Actions', 'Wrong executor or failed receipt')
    counts = {k: receipt[k] for k in ['new_public_declarations_audited', 'new_modules_replayed', 'positive_controls', 'negative_controls']}
    require(list(counts.values()) == [98, 1, 39, 10], 'Unexpected focused coverage')
    require(receipt['elapsed_seconds'] < 600, 'Focused budget exceeded')
    allowed = {'propext', 'Classical.choice', 'Quot.sound'}
    require(len(receipt['declaration_axioms']) == 98, 'Declaration coverage differs')
    for name, axioms in receipt['declaration_axioms'].items():
        require(set(axioms) <= allowed, 'Unexpected axioms: ' + name)
    checked = {}
    def bind(path, expected, size=None):
        content = subprocess.check_output(['git', 'show', commit + ':' + path], cwd=args.repo, timeout=10)
        digest = hashlib.sha256(content).hexdigest()
        require(digest == expected, 'Committed bytes mismatch: ' + path)
        require(size is None or len(content) == size, 'Committed size mismatch: ' + path)
        checked[path] = digest
    for name, digest in receipt['source_sha256'].items():
        bind('formal/' + name, digest)
    for name, record in receipt['pinned_files'].items():
        bind(name, record['sha256'], record['bytes'])
    bind('formal/results/skew-physical-trace/inputs.json', receipt['inputs_sha256'])
    pin = receipt['source_pins_manifest']
    bind(pin['path'], pin['sha256'])
    stream_count = 0
    negative_count = 0
    for command in receipt['commands']:
        for name_key, hash_key in [('log', 'log_lf_sha256'), ('stdout', 'stdout_sha256'), ('stderr', 'stderr_sha256')]:
            content = (args.receipt_dir / command[name_key]).read_bytes()
            if name_key == 'log':
                content = content.replace(b'\r\n', b'\n')
            require(hashlib.sha256(content).hexdigest() == command[hash_key], 'Command stream mismatch')
            stream_count += 1
        require(0 < command['bound_seconds'] <= 120, 'Unexpected command bound')
        require(command['elapsed_seconds'] <= command['bound_seconds'], 'Command bound exceeded')
        require(command['exit_code'] != 124, 'Timeout is not an intended failure')
        if command['expected_failure']:
            negative_count += 1
            log = (args.receipt_dir / command['log']).read_text(encoding='utf-8')
            require(command['exit_code'] != 0 and log.count('error:') == 1 and
                    'unsolved goals' in log and '\u22a2 False' in log and
                    'failed to synthesize' not in log and 'unknown' not in log.lower(),
                    'Negative did not reach intended False goal')
        else:
            require(command['exit_code'] == 0, 'Positive command failed')
    require(stream_count == 48 and negative_count == 10, 'Unexpected command coverage')
    result = {
        'status': 'PASS', 'review_executor': 'Codex coordinator; receipt/source validation, no local Lean execution',
        'proof_commit': commit, 'run_id': run['id'], 'run_url': run['html_url'],
        'remote_executor': receipt['worker'], 'focused_counts': counts,
        'focused_elapsed_seconds': receipt['elapsed_seconds'],
        'receipt_sha256': hashlib.sha256(raw).hexdigest(),
        'unique_committed_file_bindings': len(checked), 'committed_file_sha256': checked,
        'command_stream_hashes_verified': stream_count,
        'intended_negative_failures_verified': negative_count,
        'lean_version': receipt['lean_version'], 'python_version': receipt['python_version'],
        'mathlib_commit': receipt['mathlib_commit'],
        'review_elapsed_seconds': time.monotonic() - start,
        'reviewer_script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'limits': 'Full notebook workflow succeeded; this focused kernel replay covers the new module only. The existing generic coefficient field embeds in the physical curve field; physical evaluation and the full eighteen-component tensor trace are checked. All-sheet physical form/source-class compatibility, four-form nonvanishing, whole hypersurface/minimal-field identification, cohomology, primitive, global clearing and certificate remain outside this replay.'
    }
    args.output.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({k: v for k, v in result.items() if k != 'committed_file_sha256'}))


if __name__ == '__main__':
    main()

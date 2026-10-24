"""Read-only review of new saved evidence; executes no Lean or old mathematics."""
from pathlib import Path
import argparse, datetime, hashlib, json, re, subprocess, sys, time

ROOT = Path(__file__).resolve().parents[3]
FORMAL = ROOT / 'formal'
PARENT = 'bbb8aa406cd2a8b5ddb06d6e14358781b9c215e9'
MODULE = 'HodgeLab.OneReflectionSkew.PhysicalSourceNormalization'
ALLOWED_AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}

def require(condition, message):
    if not condition:
        raise RuntimeError(message)

def digest(path, lf=False):
    data = path.read_bytes()
    return hashlib.sha256(data.replace(b'\r\n', b'\n') if lf else data).hexdigest()

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, timeout=20)

def main():
    started = time.monotonic()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', required=True, type=Path)
    args = parser.parse_args()
    receipt_path = (ROOT / args.receipt).resolve()
    require(receipt_path.is_relative_to(ROOT), 'Receipt escapes repository')
    require(git('rev-parse', 'HEAD').decode().strip() == PARENT, 'Unexpected parent')
    receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
    require(receipt['status'] == 'PASS', 'Receipt does not report PASS')
    require(bool(receipt['worker']), 'Missing execution attribution')
    require(receipt['new_modules_replayed'] == 1, 'Expected only one new-module replay')
    require(receipt['elapsed_seconds'] < receipt['total_budget_seconds'] <= 600, 'Checker budget exceeded')
    formal_hashes = 0
    for path, expected in receipt['source_sha256'].items():
        require(digest(FORMAL / path) == expected, 'Source hash mismatch: ' + path)
        formal_hashes += 1
    for path, pin in receipt['pinned_files'].items():
        require(digest(ROOT / path) == pin['sha256'], 'Reused source/receipt hash mismatch: ' + path)
        require((ROOT / path).stat().st_size == pin['bytes'], 'Reused byte count mismatch: ' + path)
        formal_hashes += 1
    manifest = receipt['source_pins_manifest']
    require(digest(ROOT / manifest['path']) == manifest['sha256'], 'Source pin manifest mismatch')
    formal_hashes += 1
    inputs = FORMAL / 'results/skew-physical-source/inputs.json'
    require(digest(inputs) == receipt['inputs_sha256'], 'Input manifest mismatch')
    snapshot = receipt_path.parent / 'source-snapshot'
    for path, expected in receipt['source_sha256'].items():
        require(digest(snapshot / (path + '.txt')) == expected,
                'Saved source snapshot mismatch: ' + path)
    require(digest(snapshot / 'inputs.json.txt') == receipt['inputs_sha256'],
            'Saved input snapshot mismatch')
    source = FORMAL / (MODULE.replace('.', '/') + '.lean')
    text = source.read_text(encoding='utf-8')
    require(not re.search(r'\b(sorry|admit|axiom|native_decide)\b', text), 'Forbidden proof token')
    declarations = re.findall(r'^(?:noncomputable )?(?:def|abbrev|theorem|lemma|instance) (\w+)', text, re.M)
    names = {MODULE + '.' + name for name in declarations}
    require(len(names) == len(declarations) == receipt['new_public_declarations_audited'],
            'Declaration count mismatch')
    require(set(receipt['declaration_axioms']) == names, 'Declaration audit missing/extra names')
    require(all(set(a) <= ALLOWED_AXIOMS for a in receipt['declaration_axioms'].values()),
            'Unexpected axiom dependency')
    audit_text = (FORMAL / 'AuditSkewPhysicalSource.lean').read_text(encoding='utf-8')
    require(set(re.findall(r'^#print axioms (\S+)', audit_text, re.M)) == names, 'Audit source names mismatch')
    replay_text = (FORMAL / 'ReplaySkewPhysicalSource.lean').read_text(encoding='utf-8')
    require(re.findall(r'replayFromImports\s+`(\S+)', replay_text) == [MODULE],
            'Replay source does not isolate the new module')
    commands = receipt['commands']
    require(json.loads((receipt_path.parent / 'commands.json').read_text(encoding='utf-8')) == commands,
            'Command transcript differs from receipt')
    require(len({c['label'] for c in commands}) == len(commands), 'Duplicate command labels')
    output_hashes = 0
    negatives = []
    replay_marker = False
    for command in commands:
        label = command['label']
        require(0 <= command['elapsed_seconds'] <= command['bound_seconds'] + 2,
                'Command elapsed exceeds bound: ' + label)
        require(command['bound_seconds'] <= 120, 'Command bound above 120 seconds: ' + label)
        for key, hash_key, lf in [('log', 'log_lf_sha256', True),
                                  ('stdout', 'stdout_sha256', False),
                                  ('stderr', 'stderr_sha256', False)]:
            path = (receipt_path.parent / command[key]).resolve()
            require(path.is_relative_to(receipt_path.parent), 'Log escapes receipt directory')
            require(digest(path, lf) == command[hash_key], 'Output hash mismatch: ' + str(path))
            output_hashes += 1
        log = (receipt_path.parent / command['log']).read_text(encoding='utf-8')
        if command['expected_failure']:
            require(command['exit_code'] == 1, 'Unexpected negative-control exit: ' + label)
            require(log.count('error:') == 1 and 'unsolved goals' in log and '⊢ False' in log,
                    'Negative did not expose intended false goal: ' + label)
            require('failed to synthesize' not in log and 'unknown' not in log.lower(),
                    'Negative failed for unrelated API/typeclass reason: ' + label)
            negatives.append(label)
        else:
            require(command['exit_code'] == 0, 'Positive command failed: ' + label)
        if label == 'kernel-replay':
            require('PASS ' + MODULE in log, 'New-module replay marker missing')
            replay_marker = True
    require(replay_marker, 'No kernel-replay command')
    require(len(negatives) == receipt['negative_controls'], 'Negative count mismatch')
    require(len(negatives) >= 2, 'Missing source/scalar/orientation negative controls')
    for label in ['positive-controls'] + negatives:
        require((receipt_path.parent / (label + '.lean.txt')).is_file(),
                'Missing reproducible control source: ' + label)
    positive_source = (receipt_path.parent / 'positive-controls.lean.txt').read_text(encoding='utf-8')
    require(len(re.findall(r'^example', positive_source, re.M)) == receipt['positive_controls'],
            'Positive control source count mismatch')
    binding_path = receipt_path.parent / receipt['packet_binding_receipt']
    require(digest(binding_path) == receipt['packet_binding_receipt_sha256'],
            'Packet binding receipt hash mismatch')
    binding = json.loads(binding_path.read_text(encoding='utf-8'))
    require(binding['status'] == 'PASS' and binding['reused_exact_check_rerun'] is False,
            'Packet binding execution scope differs')
    require(len(binding['literal_definition_bindings']) == receipt['literal_packet_definition_bindings'] == 11,
            'Literal packet definition count differs')
    require(len(binding['mutation_controls']) == receipt['packet_binding_mutation_controls'] == 3,
            'Packet binding mutation count differs')
    require(digest(ROOT / binding['checker']['path']) == binding['checker']['sha256'],
            'Packet binding checker hash mismatch')
    for path, expected in binding['pinned_inputs'].items():
        require(digest(ROOT / path) == expected, 'Packet binding input hash mismatch: ' + path)
    historical_changes = git('diff', '--name-only', PARENT).decode().splitlines()
    allowed_changes = {'README.md', 'LEDGER.md', '.github/workflows/lean.yml'}
    normalization_only = []
    for path in historical_changes:
        if path not in allowed_changes:
            require((ROOT / path).read_bytes() == git('show', PARENT + ':' + path),
                    'Historical raw bytes changed: ' + path)
            require(git('show', ':' + path) == git('show', PARENT + ':' + path),
                    'Historical staged bytes changed: ' + path)
            normalization_only.append(path)
    old_ledger = git('show', PARENT + ':LEDGER.md')
    ledger = (ROOT / 'LEDGER.md').read_bytes()
    require(len(old_ledger) == 418118 and ledger.startswith(old_ledger), 'Historical ledger prefix changed')
    attempts = []
    development = ROOT / 'results/skew-physical-source-20261023/lean-development'
    for record_path in sorted(development.glob('attempt-*/execution.json')):
        record = json.loads(record_path.read_text(encoding='utf-8'))
        require(record['timeout_seconds'] <= 120, 'Development command limit exceeded')
        for path, expected in record['files_sha256'].items():
            require(digest(record_path.parent / path) == expected, 'Development artifact hash mismatch')
        attempts.append({'attempt': record_path.parent.name, 'exit_code': record['exit_code'],
                         'elapsed_seconds': record['elapsed_seconds']})
    checker_attempts = []
    for record_path in sorted(development.glob('checker-*/validation.json')):
        saved = json.loads(record_path.read_text(encoding='utf-8'))
        require(saved['status'] in {'PASS', 'FAIL'}, 'Checker attempt still in progress')
        source_record = json.loads((record_path.parent / 'source-inputs.json').read_text(encoding='utf-8'))
        for path, expected in source_record['source_sha256'].items():
            require(digest(record_path.parent / 'source-snapshot' / (path + '.txt')) == expected,
                    'Checker attempt source snapshot mismatch: ' + path)
        require(digest(record_path.parent / 'source-snapshot/inputs.json.txt') == source_record['inputs_sha256'],
                'Checker attempt input snapshot mismatch')
        require(json.loads((record_path.parent / 'commands.json').read_text(encoding='utf-8')) == saved['commands'],
                'Checker attempt command transcript mismatch')
        for command in saved['commands']:
            require(command['bound_seconds'] <= 120 and command['elapsed_seconds'] <= command['bound_seconds'] + 2,
                    'Saved checker attempt exceeded command bound')
            for key, hash_key, lf in [('log', 'log_lf_sha256', True),
                                      ('stdout', 'stdout_sha256', False),
                                      ('stderr', 'stderr_sha256', False)]:
                require(digest(record_path.parent / command[key], lf) == command[hash_key],
                        'Saved checker attempt output hash mismatch')
        checker_attempts.append({'attempt': record_path.parent.name, 'status': saved['status'],
                                 'error': saved.get('error'), 'commands': len(saved['commands'])})
    print(json.dumps({'status': 'PASS_SAVED_EVIDENCE_AUDIT',
        'worker': 'Pro adversarial source/receipt AI reviewer',
        'completed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'python_version': sys.version,
        'elapsed_seconds': time.monotonic() - started,
        'parent': PARENT, 'receipt': str(receipt_path.relative_to(ROOT)),
        'receipt_sha256': digest(receipt_path), 'module_sha256': digest(source),
        'source_context_hashes_checked': formal_hashes, 'output_hashes_checked': output_hashes,
        'public_declarations': len(names), 'new_modules_replayed_by_writer': 1,
        'positive_controls_reported_by_writer': receipt['positive_controls'],
        'literal_packet_definition_bindings_reported_by_writer': len(binding['literal_definition_bindings']),
        'packet_binding_mutations_reported_by_writer': binding['mutation_controls'],
        'negative_controls_verified': negatives, 'development_attempts': attempts,
        'checker_attempts': checker_attempts,
        'parent_ledger_bytes': len(old_ledger), 'parent_ledger_sha256': hashlib.sha256(old_ledger).hexdigest(),
        'modified_preexisting_paths': [p for p in historical_changes if p not in normalization_only],
        'raw_identical_normalization_only_git_diff': normalization_only,
        'scope': 'Read-only source/receipt/hash audit, not a Lean replay or remote CI run; old mathematics not executed.'}, indent=2))

if __name__ == '__main__':
    main()

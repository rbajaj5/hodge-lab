"""Fresh compilation, axiom audit and replay for the polynomial bridge.

The exported manifest names exact sources and declarations; it is not a
substitute for running Lean. The independent Python checker audits provenance.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parent
OUT = ROOT / 'results/polynomial-bridge-check'
MANIFEST = ROOT / 'results/polynomial-bridge-export.json'
ALLOWED = {'propext', 'Classical.choice', 'Quot.sound'}
RECEIPT = {
    'schema': 'hodge-lab-polynomial-bridge-lean-v1',
    'status': 'IN_PROGRESS', 'commands': [], 'negative_controls': [],
    'replay_scope': 'Sequential official leanchecker invocations; standard imported environment trusted, not a fresh replay of mathlib or an independent kernel.',
}


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def checkpoint():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'validation.json').write_text(json.dumps(RECEIPT, indent=2) + '\n', encoding='utf-8', newline='\n')


def inputs():
    data = json.loads(MANIFEST.read_text(encoding='utf-8'))
    for name, digest in data['source_lf_sha256'].items():
        assert sha(REPO / name) == digest, 'Changed input: ' + name
    for module in data['modules']:
        path = ROOT / (module.replace('.', '/') + '.lean')
        assert path.relative_to(REPO).as_posix() in data['source_lf_sha256']
        assert not re.search(r'\b(sorry|admit|axiom|native_decide|unsafe)\b', path.read_text(encoding='utf-8'))
    assert len(data['modules']) == len(set(data['modules']))
    assert len(data['theorem_names']) == len(set(data['theorem_names']))
    assert data['modules'] and data['theorem_names'] and data['negative_controls']
    for control in data['negative_controls']:
        assert control['file'] in data['source_lf_sha256']
    pins = json.loads((ROOT / 'lake-manifest.json').read_text(encoding='utf-8'))
    assert (ROOT / 'lean-toolchain').read_text().strip() == 'leanprover/lean4:v4.31.0'
    assert next(x for x in pins['packages'] if x['name'] == 'mathlib')['rev'] == 'fabf563a7c95a166b8d7b6efca11c8b4dc9d911f'
    extra = ['formal/lean-toolchain', 'formal/lakefile.toml', 'formal/lake-manifest.json',
             'formal/check_polynomial_bridge.py', 'formal/results/polynomial-bridge-export.json',
             '.github/workflows/lean-polynomial-bridge.yml']
    hashes = dict(data['source_lf_sha256'])
    hashes.update({name: sha(REPO / name) for name in extra})
    return data, pins, hashes


def artifact_parts(module):
    stem = ROOT / '.lake/build/lib/lean' / module.replace('.', '/')
    parts = {}
    for suffix in ('.olean', '.olean.server', '.olean.private'):
        path = stem.with_name(stem.name + suffix)
        if path.exists():
            parts[path.relative_to(ROOT).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    assert stem.with_name(stem.name + '.olean').exists(), module
    return parts


def run(label, command, bound=600, expected_failure=False):
    record = {'label': label, 'command': command, 'bound_seconds': bound,
              'expected_failure': expected_failure, 'status': 'RUNNING', 'exit_code': None}
    RECEIPT['commands'].append(record)
    checkpoint()
    env = os.environ.copy()
    env.pop('LEAN_PATH', None)
    env.pop('LEAN_SRC_PATH', None)
    start = time.perf_counter()
    output = ''
    try:
        result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True,
                                text=True, encoding='utf-8', timeout=bound)
        output = result.stdout + result.stderr
        record['exit_code'] = result.returncode
        if expected_failure:
            assert result.returncode != 0 and 'error:' in output, output
            assert 'decide' in output, 'Expected coefficient-decision diagnostic: ' + output
        else:
            assert result.returncode == 0, output
        record['status'] = 'PASS'
    except subprocess.TimeoutExpired as error:
        def decode(value):
            return value.decode('utf-8', errors='replace') if isinstance(value, bytes) else (value or '')
        output = decode(error.stdout) + decode(error.stderr)
        record['status'] = 'TIMEOUT'
        raise
    except BaseException:
        record['status'] = 'FAIL'
        raise
    finally:
        path = OUT / (label + '.log')
        path.write_text(output, encoding='utf-8', newline='\n')
        record.update(elapsed_seconds=round(time.perf_counter() - start, 3),
                      log=path.relative_to(ROOT).as_posix(), log_lf_sha256=sha(path))
        checkpoint()
        print(json.dumps({k: record[k] for k in ('label', 'status', 'elapsed_seconds')}), flush=True)
    return output, record


def main():
    assert __debug__, 'Run without Python optimization; the audit uses assertions.'
    parser = argparse.ArgumentParser()
    parser.add_argument('--check-inputs-only', action='store_true')
    parser.add_argument('--fetch-cache', action='store_true')
    args = parser.parse_args()
    data, pins, hashes = inputs()
    if args.check_inputs_only:
        print(json.dumps({'status': 'INPUTS_PASS', 'source_bindings': len(hashes), 'lean_executed': False}))
        return
    RECEIPT.update(source_lf_sha256=hashes, modules=data['modules'],
                   github_run_id=os.environ.get('GITHUB_RUN_ID'), github_sha=os.environ.get('GITHUB_SHA'),
                   scope=data['scope'])
    checkpoint()
    version, _ = run('version', ['lake', 'env', 'lean', '--version'], bound=60)
    assert re.search(r'\bversion 4\.31\.0,', version)
    RECEIPT['lean_version'] = version.strip()
    if args.fetch_cache:
        run('dependency-cache', ['lake', 'exe', 'cache', 'get'], bound=600)
    packages = {}
    for package in pins['packages']:
        output, _ = run('dependency-' + package['name'],
                        ['git', '-C', str(ROOT / '.lake/packages' / package['name']), 'rev-parse', 'HEAD'], bound=30)
        assert output.strip() == package['rev'], package['name']
        packages[package['name']] = output.strip()
    RECEIPT['dependency_commits'] = packages
    assert inputs()[2] == hashes
    artifacts = {}
    for index, module in enumerate(data['modules']):
        _, record = run(f'build-{index:02d}', ['lake', 'build', module])
        artifacts[module] = artifact_parts(module)
        record['artifact_raw_sha256'] = artifacts[module]
        checkpoint()
    audit_path = ROOT / '.lake/polynomial-bridge-audit.lean'
    audit_source = '\n'.join('import ' + module for module in data['modules']) + '\n\n'
    audit_source += '\n'.join('#print axioms ' + theorem for theorem in data['theorem_names']) + '\n'
    audit_path.write_text(audit_source, encoding='utf-8', newline='\n')
    RECEIPT['audit_source'] = audit_source
    audit, _ = run('axioms', ['lake', 'env', 'lean', str(audit_path)])
    matches = re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", audit)
    declarations = {name: [x.strip() for x in values.split(',') if x.strip()] for name, values in matches}
    assert len(matches) == len(data['theorem_names']) and set(declarations) == set(data['theorem_names'])
    assert all(set(values) <= ALLOWED for values in declarations.values())
    RECEIPT['theorem_axioms'] = declarations
    for index, module in enumerate(data['modules']):
        assert artifact_parts(module) == artifacts[module]
        _, record = run(f'kernel-{index:02d}', ['lake', 'env', 'leanchecker', module])
        assert artifact_parts(module) == artifacts[module]
        record['artifact_raw_sha256'] = artifacts[module]
        checkpoint()
    scratch = ROOT / '.lake/polynomial-bridge-negative'
    scratch.mkdir(parents=True, exist_ok=True)
    false_goals = {
        'scale': 'rowScale (0 : Fin 2) * coefficient (rowExponent 0) (columnSparse 119) ≠ (Case05.matrix 0 119 : ℚ)',
        'density': 'rowScale (1 : Fin 2) * coefficient (rowExponent 1) rhsSparse ≠ (Case05.target 1 : ℚ)',
    }
    assert {control['label'] for control in data['negative_controls']} == set(false_goals)
    for control in data['negative_controls']:
        original = (REPO / control['file']).read_text(encoding='utf-8')
        assert original.count(control['before']) == 1, control['label']
        changed = original.replace(control['before'], control['after'], 1)
        assert changed != original
        path = scratch / (control['label'] + '.lean')
        path.write_text(changed, encoding='utf-8', newline='\n')
        # An unsuccessful tactic is not itself a proof that its goal is false.
        # Compile the actual negation separately, using the same mutated inputs.
        prefix, separator, _ = changed.partition('set_option maxRecDepth')
        assert separator and 'theorem computed_column_coefficients' not in prefix
        theorem = 'mutation_' + control['label'] + '_is_false'
        full_name = 'HodgeLab.CyclicFano.Case05Polynomial.' + theorem
        probe = prefix + 'set_option maxRecDepth 100000 in\nset_option maxHeartbeats 4000000 in\n'
        probe += 'theorem ' + theorem + ' :\n    ' + false_goals[control['label']] + ' := by\n  decide +kernel\n'
        probe += '#print axioms ' + theorem + '\nend HodgeLab.CyclicFano.Case05Polynomial\n'
        probe_path = scratch / (control['label'] + '-false.lean')
        probe_path.write_text(probe, encoding='utf-8', newline='\n')
        probe_log, probe_record = run('negative-proof-' + control['label'], ['lake', 'env', 'lean', str(probe_path)])
        probe_axioms = re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", probe_log)
        assert len(probe_axioms) == 1 and probe_axioms[0][0] == full_name
        assert {x.strip() for x in probe_axioms[0][1].split(',') if x.strip()} <= ALLOWED
        _, record = run('negative-' + control['label'], ['lake', 'env', 'lean', str(path)], expected_failure=True)
        RECEIPT['negative_controls'].append({'label': control['label'], 'mutated_source_lf_sha256': sha(path),
                                            'log': record['log'], 'rejected_mutated_source': True,
                                            'false_goal': false_goals[control['label']],
                                            'false_goal_proof_source': probe,
                                            'false_goal_proof_lf_sha256': sha(probe_path),
                                            'false_goal_proof_log': probe_record['log'],
                                            'false_goal_compiled': True})
    assert inputs()[2] == hashes
    assert all(artifact_parts(module) == parts for module, parts in artifacts.items())
    RECEIPT['status'] = 'PASS'
    checkpoint()
    print(json.dumps({'status': 'PASS', 'modules': len(data['modules']),
                      'declarations': len(declarations), 'negative_controls': len(RECEIPT['negative_controls'])}))


if __name__ == '__main__':
    try:
        main()
    except BaseException as error:
        RECEIPT['status'] = 'FAIL'
        RECEIPT['error'] = type(error).__name__ + ': ' + str(error)
        checkpoint()
        raise

"""Verify downloaded CI receipts against the published commit; no Lean execution.

Run with Python -O from any directory. Prints JSON and fails on any mismatch.
The sibling remote-ci folder contains API metadata and fresh artifact entries.
"""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / 'remote-ci'
COMMIT = '5d216691981cdb248073209bdc80df86021412d4'


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def read(path):
    return json.loads(path.read_text(encoding='utf-8'))


def sha(raw, lf=False):
    return hashlib.sha256(raw.replace(b'\r\n', b'\n') if lf else raw).hexdigest()


cache = {}


def source(path):
    if path not in cache:
        cache[path] = subprocess.check_output(
            ['git', 'show', COMMIT + ':' + path], cwd=ROOT, timeout=15)
    return cache[path]


def check_sources(pins, prefix='', lf=False):
    for name, expected in pins.items():
        require(sha(source(prefix + name), lf) == expected,
                'Source mismatch: ' + prefix + name)


run = read(OUT / 'run.json')
require(run['head_sha'] == COMMIT and run['conclusion'] == 'success',
        'Wrong commit or unsuccessful workflow')
jobs = read(OUT / 'jobs.json')['jobs']
require(len(jobs) == 1 and jobs[0]['conclusion'] == 'success', 'Unsuccessful job')
require(all(s['conclusion'] == 'success' for s in jobs[0]['steps']), 'Unsuccessful step')
artifact = read(OUT / 'artifacts.json')['artifacts']
require(any(a['name'] == 'concrete-lean-verification' and not a['expired']
            for a in artifact), 'Artifact unavailable at recorded observation')
allowed = {'propext', 'Classical.choice', 'Quot.sound'}
results = []
log_count = 0
for label, historical in [('forms', 'skew-forms'), ('trace-basis', 'skew-trace-basis'),
                          ('physical-cover', 'skew-physical-cover')]:
    directory = OUT / 'receipts' / ('ci-skew-' + label)
    d = read(directory / 'validation.json')
    require(d['status'] == 'PASS', 'Failed checker: ' + label)
    check_sources(d['source_lf_sha256'], 'formal/', True)
    check_sources(d.get('reused_source_lf_sha256', {}), 'formal/', True)
    check_sources(d.get('historical_context_lf_sha256', {}), lf=True)
    check_sources(d.get('physical_source_sha256', {}))
    if 'inputs_lf_sha256' in d:
        require(sha(source('formal/results/' + historical + '/inputs.json'), True)
                == d['inputs_lf_sha256'], 'Input manifest mismatch')
    if 'input_lf_sha256' in d:
        check_sources({k: v for k, v in d['input_lf_sha256'].items()
                       if k != 'inputs.json'}, lf=True)
        require(sha(source('formal/results/' + historical + '/inputs.json'), True)
                == d['input_lf_sha256']['inputs.json'], 'Forms input mismatch')
    if 'prior_receipt_lf_sha256' in d:
        # Earlier workflow steps produce this runtime ambient receipt. Its
        # recorded hash is not substituted for the immutable committed one.
        require(sha((OUT / 'prior-runtime-ambient.json').read_bytes(), True)
                == d['prior_receipt_lf_sha256'], 'Runtime ambient context mismatch')
    axioms = d.get('declaration_axioms', d.get('theorem_axioms', {}))
    require(bool(axioms) and all(set(a) <= allowed for a in axioms.values()),
            'Unapproved or missing declaration audits')
    for command in d['commands']:
        raw = (directory / command['log']).read_bytes()
        require(sha(raw, True) == command['log_lf_sha256'], 'Log hash mismatch')
        expected = 1 if command['expected_failure'] else 0
        require(command['exit_code'] == expected, 'Unexpected command exit')
        if command['expected_failure']:
            text = raw.decode('utf-8')
            require(text.count('error:') == 1 and 'unsolved goals' in text
                    and '⊢ False' in text, 'Wrong negative-control diagnostic')
        log_count += 1
    results.append({'checker': label, 'status': d['status'],
                    'declarations': len(axioms),
                    'positive_controls': d['positive_controls'],
                    'negative_controls': d['negative_controls'],
                    'elapsed_seconds': d['elapsed_seconds'],
                    'receipt_sha256': sha((directory / 'validation.json').read_bytes())})

binding = read(OUT / 'receipts/ci-skew-physical-source/validation.json')
require(binding['status'] == 'PASS' and len(binding['mutations']) == 5,
        'Source gate incomplete')
check_sources(binding['source_sha256'])
print(json.dumps({'status': 'PASS', 'commit': COMMIT, 'run': run['html_url'],
                  'scope': 'Coordinator verification of remote execution receipts, sources and logs; no local Lean rerun',
                  'checks': results, 'source_gate_mutations': 5,
                  'matched_published_source_files': len(cache),
                  'matched_command_logs': log_count,
                  'limits': ['No new mathematical claims beyond the checked conditional theorem',
                             'Full CPU workflow observed separately; not inferred from Lean success',
                             'Runtime ambient receipt handled separately from immutable historical evidence']}, indent=2))

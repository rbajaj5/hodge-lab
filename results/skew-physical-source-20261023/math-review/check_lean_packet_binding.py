#!/usr/bin/env python3
"""Bind the frozen Lean definitions to the already checked packet expressions.

This performs no new symbolic calculation and runs no Lean command.  It checks
the exact declaration bodies and reuses the immutable exact-check receipt.
"""
from pathlib import Path
import argparse
import datetime
import hashlib
import json
import re
import sys
import time

ROOT = Path(__file__).resolve().parents[3]
LEAN = ROOT / 'formal/HodgeLab/OneReflectionSkew/PhysicalSourceNormalization.lean'
PACKET = ROOT / 'results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'
REVIEW = Path(__file__).resolve().parent
EXACT_SCRIPT = REVIEW / 'check_selected_normalization.py'
EXACT_RECEIPT = REVIEW / 'check-02/validation.json'
PINS = {
    PACKET: 'a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d',
    EXACT_SCRIPT: 'c5aac719297e09a67143c227316ded7e7600395308a28c19e3ab6c9f66e05eec',
    EXACT_RECEIPT: 'f0b0f738d34975281bb3acbaabf1cd5596c0cd98593368238e974b5387d56ecd',
}
EXPECTED = {
    'fibreP': 'a*V^3+b*V^2+c*V+d0',
    'fibrePPrime': '3*a*V^2+2*b*V+c',
    'delta': '27*a^2*d0^2-18*a*b*c*d0+4*a*c^3+4*b^3*d0-b^2*c^2',
    'n0': '27*a*c*d0-12*b^2*d0+b*c^2',
    'n1': 'a*(3*b*d0-c^2)',
    'rNumerator': '2*n1 a b c d0*V^2+(3*a*c*d0+2*b^2*d0-b*c^2)*V+(9*a*d0^2-b*c*d0)',
    'rNumeratorPrime': '4*n1 a b c d0*V+(3*a*c*d0+2*b^2*d0-b*c^2)',
    'bColumn0': 'n0 a b c d0/(6*delta a b c d0)',
    'bColumn1': 'n1 a b c d0/delta a b c d0',
    'correction': 'rNumerator a b c d0 V/delta a b c d0',
    'correctionPrime': 'rNumeratorPrime a b c d0 V/delta a b c d0',
}


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compact(expression):
    return ''.join(expression.split())


def bind(text):
    bindings = []
    for name, expected in EXPECTED.items():
        pattern = rf'^def\s+{re.escape(name)}\b[^\n]*:=([^\n]*(?:\n[ \t]+[^\n]*)*)'
        found = re.findall(pattern, text, flags=re.MULTILINE)
        require(len(found) == 1, 'Missing or duplicate Lean declaration: ' + name)
        require(compact(found[0]) == compact(expected), 'Lean expression mismatch: ' + name)
        bindings.append({'declaration': name, 'expression': expected})
    return bindings


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lean-sha256', required=True)
    parser.add_argument('--output-dir', required=True)
    args = parser.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=False)
    began = datetime.datetime.now(datetime.timezone.utc).isoformat()
    start = time.monotonic()
    require(re.fullmatch('[0-9a-f]{64}', args.lean_sha256) is not None,
            'Expected a full lowercase SHA256 for the frozen Lean module')
    require(sha(LEAN) == args.lean_sha256, 'Frozen Lean module hash differs')
    for path, expected in PINS.items():
        require(sha(path) == expected, 'Historical reviewer input changed: ' + str(path))
    prior = json.loads(EXACT_RECEIPT.read_text(encoding='utf-8'))
    require(prior['status'] == 'PASS', 'Prior exact check did not pass')
    require(len(prior['checks']) == 10 and len(prior['mutation_controls']) == 5,
            'Prior exact-check scope differs')
    packet = json.loads(PACKET.read_text(encoding='utf-8'))
    require(packet['convention'] == 'columns index input basis; coefficient derivative is partial_t+M_t',
            'Packet matrix convention differs')
    text = LEAN.read_text(encoding='utf-8')
    bindings = bind(text)
    mutations = []
    controls = [
        ('first-row numerator sign', '27*a*c*d0-12*b^2*d0+b*c^2',
         '27*a*c*d0+12*b^2*d0+b*c^2'),
        ('first-row scalar denominator', 'n0 a b c d0/(6*delta a b c d0)',
         'n0 a b c d0/(12*delta a b c d0)'),
        ('first-row input-column numerator', 'n0 a b c d0/(6*delta a b c d0)',
         'n1 a b c d0/(6*delta a b c d0)'),
    ]
    for label, original, replacement in controls:
        require(text.count(original) == 1, 'Mutation target is not unique: ' + label)
        try:
            bind(text.replace(original, replacement))
        except RuntimeError:
            mutations.append(label)
        else:
            raise RuntimeError('Mutation was accepted: ' + label)
    require(time.monotonic()-start < 600, 'Binding-checker budget exceeded')
    sources = [LEAN, PACKET, EXACT_SCRIPT, EXACT_RECEIPT, Path(__file__)]
    result = {
        'status': 'PASS',
        'executor': 'Pro source_math AI reviewer',
        'started_utc': began,
        'completed_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'elapsed_seconds': time.monotonic()-start,
        'budget_seconds': 600,
        'python_version': sys.version,
        'source_sha256': {str(p.relative_to(ROOT)): sha(p) for p in sources},
        'literal_definition_bindings': bindings,
        'mutation_controls': mutations,
        'reused_evidence': {
            'receipt': str(EXACT_RECEIPT.relative_to(ROOT)),
            'status': 'PASS',
            'identities': 10,
            'mutations': 5,
            'rerun': False,
        },
        'variable_mapping': {'Lean d0': 'packet d', 'Lean V': 'packet U'},
        'scope': 'Exact literal Lean-body binding to formulas in the prior packet-bound symbolic check; no new mathematics or Lean execution',
        'limits': [
            'Whitespace is ignored; otherwise declaration bodies must match exactly',
            'This source-binding receipt is not a Lean kernel-validation receipt',
            'Only b input column zero is bound; no other connection column is audited',
        ],
    }
    encoded = json.dumps(result, indent=2) + '\n'
    (out/'validation.json').write_text(encoded, encoding='utf-8')
    print(encoded, end='')


if __name__ == '__main__':
    main()

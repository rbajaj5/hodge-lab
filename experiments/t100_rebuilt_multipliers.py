"""Bounded exact multiplier search on T100 after the proved a56=0 reduction.

This is a new attempt.  It leaves the earlier thirteen-direction T100 packet
unchanged, rebuilds the physical shared-numerator system on the surviving
twelve denominator directions, and checkpoints only fully processed
constant/linear multiplier blocks.  Exported denominator relations are
necessary conditions; a finite multiplier span is not the full elimination
ideal and a failed search does not prove existence.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse
import copy
import json
import subprocess
import sys
import time

import typed_rewrite_families as h
import typed100_continuation as old
import family151_multipliers as fm
import degree7_syzygies as syz


OUT = h.OUT / 't100-rebuilt-multipliers'
SOURCE = h.OUT / 't100' / 'closure.json.gz'
EXPECTED = [6, 42, 88, 102, 111, 114, 135, 211, 235, 272, 289, 293]


def build(model):
    closure = h.q.load(SOURCE)
    assert closure['completed'] and closure['status'] == 'unresolved'
    assert closure['forced'] == [56] and closure['remaining'] == EXPECTED
    item = h.selection(model)[99]
    desc, equations = h.build(model, item, closure['remaining'])
    assert desc['basis_indices'] == EXPECTED
    assert [EXPECTED[i] for i in desc['pivots']] == [6, 211]
    return desc, equations, h.digest(SOURCE)


def produce():
    start = time.perf_counter()
    desc, equations, source_hash = build(h.t.Model())
    nD = len(desc['basis_indices'])
    multipliers = [()] + [(i,) for i in range(nD)]
    span = h.t.base.Elimination()
    packet = {
        'family': 'T100',
        'global_family': desc['family'],
        'system': desc,
        'source_sha256': source_hash,
        'proved_reduction': {'raw_coordinate': 56, 'value': 0},
        'multiplier_degree_bound': 1,
        'requested_multipliers': [list(m) for m in multipliers],
        'completed_multipliers': [],
        'baseline': [],
        'relations': [],
        'selected_new': [],
        'checkpoints': [],
        'completed': False,
    }
    path = OUT / 'relations.json.gz'
    h.q.save(path, packet)
    for mon in multipliers:
        block_start = time.perf_counter()
        for equation_index, row in enumerate(equations):
            lifted = {
                (0 if any(i >= nD for i in m + mon) else 1, tuple(sorted(m + mon))): c
                for m, c in row.items()
            }
            span.insert(lifted, {(equation_index, mon): Q(1)})
        packet['relations'] = fm.relations(span)
        if not mon:
            packet['baseline'] = packet['relations'][:]
        old_rank, selected, combined_rank = syz.select_new(
            packet['baseline'], packet['relations'], list(range(nD)))
        packet['selected_new'] = selected
        packet['completed_multipliers'].append(list(mon))
        packet['checkpoints'].append({
            'multiplier': list(mon),
            'equation_rank': len(span.basis),
            'relations': len(packet['relations']),
            'additional': len(selected),
            'baseline_multiple_rank': old_rank,
            'combined_rank': combined_rank,
            'block_seconds': time.perf_counter() - block_start,
            'elapsed_seconds': time.perf_counter() - start,
        })
        packet['seconds'] = time.perf_counter() - start
        h.q.save(path, packet)
        print(mon, len(packet['relations']), len(selected),
              round(packet['seconds'], 3), flush=True)
    packet['completed'] = True
    h.q.save(path, packet)


def check(independent=False):
    if independent:
        from check_degree7_triples import IndependentModel
        model = IndependentModel()
    else:
        model = h.t.Model()
    start = time.perf_counter()
    desc, equations, source_hash = build(model)
    packet = h.q.load(OUT / 'relations.json.gz')
    plan = json.loads((OUT / 'plan.json').read_text(encoding='utf-8'))
    attempt = json.loads((OUT / 'attempt.json').read_text(encoding='utf-8'))
    nD = len(desc['basis_indices'])
    expected = [[]] + [[i] for i in range(nD)]
    assert packet['system'] == desc and packet['source_sha256'] == source_hash
    assert packet['proved_reduction'] == {'raw_coordinate': 56, 'value': 0}
    assert packet['requested_multipliers'] == expected
    assert packet['completed_multipliers'] == expected[:len(packet['completed_multipliers'])]
    assert packet['completed_multipliers']
    if packet['completed']:
        assert packet['completed_multipliers'] == expected
    assert plan['system'] == desc and plan['source_sha256'] == source_hash
    assert plan['multipliers'] == expected and plan['workers'] == 1
    assert plan['physical_equation_count'] == len(equations)
    assert 0 < plan['seconds'] == attempt['limit'] <= 300
    assert attempt['status'] in ['completed', 'timeout', 'error']
    if attempt['status'] == 'completed':
        assert attempt['exit_code'] == 0 and packet['completed']
    elif attempt['status'] == 'timeout':
        assert attempt['exit_code'] is None
    else:
        assert isinstance(attempt['exit_code'], int) and attempt['exit_code'] != 0
    baseline, _ = syz.necessary_relations(equations, nD, [()])
    assert baseline == packet['baseline']
    independence = h.t.base.Elimination()
    for relation in packet['relations']:
        polynomial = h.cert.decode(relation['polynomial'])
        assert polynomial and max(map(len, polynomial)) <= 3
        assert independence.insert(polynomial) is None
        assert all(list(mon) in packet['completed_multipliers']
                   for _, mon, _ in relation['products'])
    assert [row['multiplier'] for row in packet['checkpoints']] == packet['completed_multipliers']
    products = sum(syz.verify_relation(equations, nD, list(range(nD)), relation)
                   for relation in packet['baseline'] + packet['relations'])
    old_rank, selected, combined_rank = syz.select_new(
        packet['baseline'], packet['relations'], list(range(nD)))
    assert selected == packet['selected_new']
    assert old_rank == packet['checkpoints'][-1]['baseline_multiple_rank']
    assert combined_rank == packet['checkpoints'][-1]['combined_rank']
    broken = copy.deepcopy(packet['relations'][0])
    broken['products'][0][2] = str(Q(broken['products'][0][2]) + 1)
    try:
        syz.verify_relation(equations, nD, list(range(nD)), broken)
    except AssertionError:
        pass
    else:
        raise AssertionError('Altered multiplier witness accepted')
    report = {
        'status': 'PASS',
        'independent_physical_polynomials': independent,
        'completed': packet['completed'],
        'physical_equations': len(equations),
        'denominator_directions': nD,
        'requested_blocks': len(expected),
        'completed_blocks': len(packet['completed_multipliers']),
        'baseline_relations': len(packet['baseline']),
        'relations': len(packet['relations']),
        'additional_relations': len(selected),
        'coefficient_products': products,
        'mutation_rejected': True,
        'seconds': time.perf_counter() - start,
        'scope': ('Necessary relations in a bounded constant/linear multiplier span on the '
                  'rebuilt T100 system; no exclusion, certificate, or full elimination-ideal claim.'),
    }
    name = ('independent-' if independent else '') + 'validation.json'
    (OUT / name).write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2), flush=True)


def run(limit):
    assert 0 < limit <= 300
    OUT.mkdir(parents=True, exist_ok=True)
    assert not (OUT / 'plan.json').exists(), 'Preserve the first bounded attempt'
    desc, equations, source_hash = build(h.t.Model())
    expected = [[]] + [[i] for i in range(len(desc['basis_indices']))]
    plan = {
        'family': 'T100',
        'seconds': limit,
        'workers': 1,
        'multiplier_degree_bound': 1,
        'multipliers': expected,
        'source_sha256': source_hash,
        'system': desc,
        'physical_equation_count': len(equations),
        'checkpoint_scope': ('Only fully processed multiplier blocks survive interruption; '
                             'the preceding thirteen-direction attempt is unchanged.'),
    }
    (OUT / 'plan.json').write_text(json.dumps(plan, indent=2) + '\n', encoding='utf-8')
    start = time.perf_counter()
    try:
        completed = subprocess.run(
            [sys.executable, '-S', str(Path(__file__).resolve()), '--produce'],
            capture_output=True, text=True, encoding='utf-8', timeout=limit)
        output = completed.stdout + completed.stderr
        code = completed.returncode
        status = 'completed' if code == 0 else 'error'
    except subprocess.TimeoutExpired as ex:
        def decode(value):
            return value.decode('utf-8', errors='replace') if isinstance(value, bytes) else value or ''
        output = decode(ex.stdout) + decode(ex.stderr)
        code = None
        status = 'timeout'
    (OUT / 'attempt.log').write_text(output, encoding='utf-8')
    result = {
        'status': status,
        'exit_code': code,
        'seconds': time.perf_counter() - start,
        'limit': limit,
    }
    (OUT / 'attempt.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(result), output, flush=True)


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Run without -O.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--produce', action='store_true')
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--independent', action='store_true')
    parser.add_argument('--limit', type=int, default=240)
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if args.produce:
        produce()
    elif args.check:
        check(args.independent)
    else:
        run(args.limit)

"""Rebuild and close T100 after the exact degree-five Y1 vanishings."""
from collections import Counter
from pathlib import Path
import argparse
import json
import subprocess
import sys
import time

import typed_rewrite_families as h
import t100_rebuilt_blocks as blocks


OUT = blocks.OUT / 'closure'
SOURCE = blocks.OUT / 'blocks.json.gz'


def forced_from_packet():
    packet = h.q.load(SOURCE)
    assert packet['completed']
    return sorted({packet['system']['basis_indices'][power['coordinate']]
                   for block in packet['blocks'] for strand in block['strands']
                   for power in strand['powers']})


def produce():
    model = h.t.Model()
    forced = forced_from_packet()
    assert forced == [135, 235, 272, 289, 293]
    desc, _, _ = blocks.rebuilt.build(model)
    item = h.selection(model)[99]
    ids = [raw for raw in desc['basis_indices'] if raw not in forced]
    packet = {
        'family': 'T100',
        'source_sha256': h.digest(SOURCE),
        'forced_raw_ids': forced,
        'starting_indices': ids[:],
        'cycles': [],
        'remaining': ids[:],
        'completed': False,
    }
    path = OUT / 'closure.json.gz'
    h.q.save(path, packet)
    for cycle in range(len(ids) + 1):
        block_path = OUT / f'power-rebuilt-{cycle}.json.gz'
        h.x.family(model, item, initial=ids, destination=block_path, finish=h.terminal)
        stage = {
            'before': ids[:],
            'block_file': block_path.name,
            'block_sha256': h.digest(block_path),
        }
        ids = h.q.load(block_path)['remaining']
        packet['cycles'].append(stage)
        packet['remaining'] = ids[:]
        h.q.save(path, packet)
        if h.terminal(model, ids):
            break
        system, equations = h.build(model, item, ids)
        stage['system'] = system
        stage['charts'] = []
        nvars = len(ids) + len(system['Koszul_indices'])
        for pivot in system['pivots']:
            chart = h.cert.prove_chart(equations, nvars, pivot)
            h.cert.verify_chart(equations, nvars, chart)
            stage['charts'].append(chart)
            h.q.save(path, packet)
            print('cycle', cycle, 'chart', ids[pivot], chart['excluded'], flush=True)
        removed = [ids[chart['pivot']] for chart in stage['charts'] if chart['excluded']]
        stage['removed'] = removed
        ids = [raw for raw in ids if raw not in removed]
        packet['remaining'] = ids[:]
        h.q.save(path, packet)
        if not removed:
            break
    else:
        raise AssertionError('Successful cycles strictly decrease directions')
    packet.update(completed=True, status=h.terminal(model, ids) or 'unresolved', remaining=ids)
    h.q.save(path, packet)
    print('T100', packet['status'], ids, flush=True)


def replay_blocks(model):
    desc, equations, groups, products = blocks.setup(model)
    packet = h.q.load(SOURCE)
    assert packet['completed'] and packet['system'] == desc
    forced = set()
    counts = Counter(relation_products=products)
    for block, group in zip(packet['blocks'], groups):
        for key, value in group.items():
            assert block[key] == value
        small = [equations[j] for j in group['equation_indices']]
        for stored in block['strands']:
            assert blocks.strand(small, group['ids'], stored['degree']) == stored
            counts['graded_maps'] += 1
            counts['finite_field_rank_comparisons'] += len(blocks.PRIMES)
            for power in stored['powers']:
                forced.add(desc['basis_indices'][power['coordinate']])
                counts['power_identities'] += 1
                counts['power_products'] += len(power['products'])
    return desc, sorted(forced), counts


def check(independent=False):
    from check_x1y1_extensions import replay_stages
    from check_quartic_exclusions import single_character
    from check_typed_rewrite_families import replay_pair
    if independent:
        from check_degree7_triples import IndependentModel
        model = IndependentModel()
    else:
        model = h.t.Model()
    start = time.perf_counter()
    desc, forced, counts = replay_blocks(model)
    assert forced == [135, 235, 272, 289, 293]
    item = h.selection(model)[99]
    ids = [raw for raw in desc['basis_indices'] if raw not in forced]
    packet = h.q.load(OUT / 'closure.json.gz')
    plan = json.loads((OUT / 'plan.json').read_text(encoding='utf-8'))
    attempt = json.loads((OUT / 'attempt.json').read_text(encoding='utf-8'))
    assert packet['source_sha256'] == plan['source_sha256'] == h.digest(SOURCE)
    assert packet['forced_raw_ids'] == forced and packet['starting_indices'] == ids
    assert plan['starting_indices'] == ids and plan['workers'] == 1
    assert 0 < plan['seconds'] == attempt['limit'] <= 300
    assert attempt['status'] in ['completed', 'timeout', 'error']
    if attempt['status'] == 'completed':
        assert attempt['exit_code'] == 0 and packet['completed']
    elif attempt['status'] == 'timeout':
        assert attempt['exit_code'] is None
    else:
        assert isinstance(attempt['exit_code'], int) and attempt['exit_code'] != 0
    cycles = []
    for cycle, stage in enumerate(packet['cycles']):
        assert stage['before'] == ids and stage['block_file'] == f'power-rebuilt-{cycle}.json.gz'
        block_path = OUT / stage['block_file']
        assert h.digest(block_path) == stage['block_sha256']
        block = h.q.load(block_path)
        for key, value in item.items():
            assert block[key] == value
        assert block['starting_indices'] == ids and block['completed']
        ids, zeros, _, stage_counts = replay_stages(model, block, ids, finish=h.terminal)
        counts.update(stage_counts)
        detail = {'before': stage['before'], 'block_zeros': zeros,
                  'after_blocks': ids[:], 'charts': []}
        if 'system' in stage:
            assert not h.terminal(model, ids)
            system, equations = h.build(model, item, ids)
            assert system == stage['system']
            assert [chart['pivot'] for chart in stage['charts']] == system['pivots'][:len(stage['charts'])]
            if packet['completed'] or 'removed' in stage:
                assert [chart['pivot'] for chart in stage['charts']] == system['pivots']
            nvars = len(ids) + len(system['Koszul_indices'])
            removed = []
            for chart in stage['charts']:
                counts['chart_inferences'] += h.cert.verify_chart(equations, nvars, chart)
                counts['charts'] += 1
                detail['charts'].append({'raw': ids[chart['pivot']], 'excluded': chart['excluded']})
                if chart['excluded']:
                    removed.append(ids[chart['pivot']])
                    counts['excluded_charts'] += 1
            if 'removed' in stage:
                assert stage['removed'] == removed
                ids = [raw for raw in ids if raw not in removed]
        detail['after'] = ids[:]
        cycles.append(detail)
    assert packet['remaining'] == ids
    ending = h.terminal(model, ids)
    dependency = None
    if packet['completed']:
        assert packet['status'] == (ending or 'unresolved')
    if ending == 'x0_y1_dependency':
        dependency, extra = replay_pair(model)
        counts.update(extra)
    elif ending == 'single_character_dependency':
        dependency = single_character(model, model.dc[ids[0]], ids)
    report = {
        'status': 'PASS',
        'independent_physical_polynomials': independent,
        'completed': packet['completed'],
        'excluded': ending is not None,
        'ending': ending,
        'forced_raw_ids': forced,
        'remaining': ids,
        'cycles': cycles,
        'checks': dict(counts),
        'dependency': dependency,
        'seconds': time.perf_counter() - start,
        'scope': ('T100 only. Exact rational power identities and rebuilt chart proofs; '
                  'finite-field ranks are diagnostics and are not used as exclusion witnesses.'),
    }
    name = ('independent-' if independent else '') + 'validation.json'
    (OUT / name).write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2), flush=True)


def run(limit):
    assert 0 < limit <= 300
    OUT.mkdir(parents=True, exist_ok=True)
    assert not (OUT / 'plan.json').exists(), 'Preserve the first bounded attempt'
    desc, _, _ = blocks.rebuilt.build(h.t.Model())
    forced = forced_from_packet()
    ids = [raw for raw in desc['basis_indices'] if raw not in forced]
    plan = {
        'family': 'T100',
        'seconds': limit,
        'workers': 1,
        'source_sha256': h.digest(SOURCE),
        'forced_raw_ids': forced,
        'starting_indices': ids,
        'scope': 'Rebuild after exact rational vanishings, then test every available chart.',
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
    if args.produce:
        produce()
    elif args.check:
        check(args.independent)
    else:
        run(args.limit)

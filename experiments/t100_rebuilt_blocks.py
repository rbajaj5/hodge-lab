"""Exact graded blocks and finite-field rank screens for rebuilt T100.

The finite-field ranks are diagnostic screens.  Coordinate vanishings are
reported only when an exact rational witness expands to the requested pure
power.  This is not an application of p-adic Hodge theory.
"""
from collections import Counter
from fractions import Fraction as Q
from math import comb
from pathlib import Path
import argparse
import copy
import json
import subprocess
import sys
import time

import typed_rewrite_families as h
import t100_rebuilt_multipliers as rebuilt
import family151_cubic_blocks as cb
import degree7_syzygies as syz


OUT = rebuilt.OUT / 'graded-blocks'
SOURCE = rebuilt.OUT / 'relations.json.gz'
DEGREES = [3, 4, 5, 6]
PRIMES = [1009, 1013, 1019]


def is_prime(value):
    if value < 2:
        return False
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 1
    return True


def setup(model, verify_relations=True):
    packet = h.q.load(SOURCE)
    desc, physical, source_hash = rebuilt.build(model)
    assert packet['system'] == desc and packet['source_sha256'] == source_hash
    selected = packet['baseline'] + [packet['relations'][i] for i in packet['selected_new']]
    products = 0
    if verify_relations:
        products = sum(syz.verify_relation(physical, len(desc['basis_indices']),
                                           list(range(len(desc['basis_indices']))), relation)
                       for relation in selected)
    equations = [h.cert.decode(relation['polynomial']) for relation in selected]
    groups = []
    for character in sorted({model.dc[i] for i in desc['basis_indices']}):
        ids = [j for j, raw in enumerate(desc['basis_indices']) if model.dc[raw] == character]
        chosen = [j for j, polynomial in enumerate(equations)
                  if all(i in ids for monomial in polynomial for i in monomial)]
        groups.append({
            'character': list(character),
            'ids': ids,
            'raw_ids': [desc['basis_indices'][i] for i in ids],
            'equation_indices': chosen,
        })
    return desc, equations, groups, products


def modular_rank(rows, prime):
    span = h.t.base.Elimination(prime=prime)
    for row in rows:
        span.insert({m: c.numerator * pow(c.denominator, -1, prime) % prime
                     for m, c in row.items()})
    return len(span.basis)


def strand(equations, ids, degree):
    labels, rows = cb.mac_map(equations, ids, degree)
    span = h.t.base.Elimination()
    for k, row in enumerate(rows):
        span.insert(dict(row), {k: Q(1)})
    powers = []
    for coordinate in ids:
        residual = {(coordinate,) * degree: Q(1)}
        weights = {}
        while residual:
            pivot = min(residual)
            if pivot not in span.basis:
                break
            coefficient = residual[pivot]
            row, representation = span.basis[pivot]
            residual = h.t.base.padd(residual, row, -coefficient)
            weights = h.t.base.padd(weights, representation, coefficient)
        if not residual:
            powers.append({
                'coordinate': coordinate,
                'power': degree,
                'products': [[labels[k][0], list(labels[k][1]), str(c)]
                             for k, c in sorted(weights.items())],
            })
    rank = len(span.basis)
    return {
        'degree': degree,
        'domain': len(rows),
        'codomain': comb(len(ids) + degree - 1, degree),
        'rank_Q': rank,
        'quotient_dimension_Q': comb(len(ids) + degree - 1, degree) - rank,
        'rank_mod_p': [[prime, modular_rank(rows, prime)] for prime in PRIMES],
        'powers': powers,
        'tested_coordinates': ids,
    }


def produce():
    assert all(is_prime(p) for p in PRIMES)
    OUT.mkdir(parents=True, exist_ok=True)
    desc, equations, groups, _ = setup(h.t.Model(), verify_relations=False)
    packet = {
        'family': 'T100',
        'source_sha256': h.digest(SOURCE),
        'system': desc,
        'degrees': DEGREES,
        'screening_primes': PRIMES,
        'blocks': [],
        'completed': False,
    }
    path = OUT / 'blocks.json.gz'
    h.q.save(path, packet)
    for group in groups:
        block = {**group, 'strands': []}
        packet['blocks'].append(block)
        small = [equations[j] for j in group['equation_indices']]
        for degree in DEGREES:
            record = strand(small, group['ids'], degree)
            block['strands'].append(record)
            h.q.save(path, packet)
            print(group['raw_ids'], degree, record['rank_Q'], '/', record['codomain'],
                  'mod', record['rank_mod_p'], 'powers',
                  [desc['basis_indices'][p['coordinate']] for p in record['powers']], flush=True)
    packet['completed'] = True
    h.q.save(path, packet)


def check(independent=False):
    if independent:
        from check_degree7_triples import IndependentModel
        model = IndependentModel()
    else:
        model = h.t.Model()
    start = time.perf_counter()
    assert all(is_prime(p) for p in PRIMES)
    desc, equations, groups, products = setup(model)
    packet = h.q.load(OUT / 'blocks.json.gz')
    plan = json.loads((OUT / 'plan.json').read_text(encoding='utf-8'))
    attempt = json.loads((OUT / 'attempt.json').read_text(encoding='utf-8'))
    assert packet['source_sha256'] == h.digest(SOURCE) and packet['system'] == desc
    assert packet['degrees'] == plan['degrees'] == DEGREES
    assert packet['screening_primes'] == plan['screening_primes'] == PRIMES
    assert plan['workers'] == 1 and 0 < plan['seconds'] == attempt['limit'] <= 300
    assert attempt['status'] in ['completed', 'timeout', 'error']
    if attempt['status'] == 'completed':
        assert attempt['exit_code'] == 0 and packet['completed']
    elif attempt['status'] == 'timeout':
        assert attempt['exit_code'] is None
    else:
        assert isinstance(attempt['exit_code'], int) and attempt['exit_code'] != 0
    assert len(packet['blocks']) <= len(groups)
    if packet['completed']:
        assert len(packet['blocks']) == len(groups)
    counts = Counter(relation_products=products)
    details = []
    forced = set()
    for block, group in zip(packet['blocks'], groups):
        for key, value in group.items():
            assert block[key] == value
        degrees = [record['degree'] for record in block['strands']]
        assert degrees == DEGREES[:len(degrees)]
        if packet['completed']:
            assert degrees == DEGREES
        small = [equations[j] for j in group['equation_indices']]
        detail = {**group, 'strands': []}
        for stored in block['strands']:
            recomputed = strand(small, group['ids'], stored['degree'])
            assert recomputed == stored
            counts['graded_maps'] += 1
            counts['finite_field_rank_comparisons'] += len(PRIMES)
            assert all(rank == stored['rank_Q'] for _, rank in stored['rank_mod_p'])
            for power in stored['powers']:
                target = {(power['coordinate'],) * power['power']: Q(1)}
                assert h.e.expand_products(small, power['products']) == target
                forced.add(desc['basis_indices'][power['coordinate']])
                counts['power_identities'] += 1
                counts['power_products'] += len(power['products'])
                broken = copy.deepcopy(power['products'])
                broken[0][2] = str(Q(broken[0][2]) + 1)
                assert h.e.expand_products(small, broken) != target
                counts['altered_powers_rejected'] += 1
            detail['strands'].append({k: stored[k] for k in
                ['degree', 'domain', 'codomain', 'rank_Q', 'quotient_dimension_Q', 'rank_mod_p']})
        detail['forced_raw_ids'] = sorted({desc['basis_indices'][p['coordinate']]
            for record in block['strands'] for p in record['powers']})
        details.append(detail)
    report = {
        'status': 'PASS',
        'independent_physical_polynomials': independent,
        'completed': packet['completed'],
        'forced_raw_ids': sorted(forced),
        'blocks': details,
        'checks': dict(counts),
        'seconds': time.perf_counter() - start,
        'scope': ('Exact rational pure-character maps through degree six, with finite-field '
                  'rank screens only. No p-adic Hodge-theory or T100-exclusion claim.'),
    }
    name = ('independent-' if independent else '') + 'validation.json'
    (OUT / name).write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2), flush=True)


def run(limit):
    assert 0 < limit <= 300
    OUT.mkdir(parents=True, exist_ok=True)
    assert not (OUT / 'plan.json').exists(), 'Preserve the first bounded attempt'
    desc, equations, groups, _ = setup(h.t.Model(), verify_relations=False)
    plan = {
        'family': 'T100',
        'seconds': limit,
        'workers': 1,
        'source_sha256': h.digest(SOURCE),
        'system': desc,
        'degrees': DEGREES,
        'screening_primes': PRIMES,
        'groups': groups,
        'scope': ('Exact rational membership and rank, plus modular rank screens. '
                  'A modular screen alone cannot force a rational identity.'),
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

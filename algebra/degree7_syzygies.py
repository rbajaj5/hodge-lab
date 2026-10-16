"""Bounded polynomial left-syzygies of the actual shared E2 correction map.

On three fixed charts, seek multipliers affine in the denominator coordinates
which cancel every numerator coordinate. Discovery uses exact row reduction;
replay multiplies the original equations over Fraction, with no CAS required.
These are necessary conditions, not a claim that the projected system suffices.
"""
from collections import Counter
from itertools import combinations_with_replacement
from pathlib import Path
import argparse, copy, gzip, json, time

import degree7_triples as triples
import degree7_triple_shared as shared
import degree7_character_search as cert

OUT = triples.ROOT / 'results/degree7-syzygies'
CASES = ((87, 2), (115, 0), (115, 10))


def necessary_relations(rows, nD, multipliers):
    """Eliminate all z-containing monomials before denominator monomials.

    Each row carries its expression as sum u_j(a) E_j(a,z). Including the
    b(a) part throughout does not relax the shared z coefficients.
    """
    span = triples.base.Elimination()
    for mon in multipliers:
        assert all(0 <= i < nD for i in mon)
        for j, row in enumerate(rows):
            value = {(0 if any(i >= nD for i in m + mon) else 1,
                      tuple(sorted(m + mon))): c for m, c in row.items()}
            span.insert(value, {(j, mon): triples.Q(1)})
    return [
        {'polynomial': cert.encode({m: c for (_, m), c in row.items()}),
         'products': [[j, list(mon), str(c)] for (j, mon), c in sorted(track.items())]}
        for pivot, (row, track) in sorted(span.basis.items()) if pivot[0] == 1
    ], len(span.basis)


def select_new(baseline, relations, variables):
    """Linear independence modulo affine multiples of the degree-zero output.

    This is a vector-space comparison, NOT a test of membership in the full
    polynomial ideal or its radical.
    """
    span = triples.base.Elimination()
    for r in baseline:
        for mon in [()] + [(i,) for i in variables]:
            span.insert(cert.product(cert.decode(r['polynomial']), {mon: triples.Q(1)}))
    old_rank = len(span.basis)
    new = []
    for j, r in enumerate(relations):
        if span.insert(cert.decode(r['polynomial'])) is None:
            new.append(j)
    return old_rank, new, len(span.basis)


def construct(model, number, pivot):
    family = shared.read_packet()['families'][number - 1]
    description, equations = shared.construct(model, family)
    assert pivot in description['pivots']
    rows = [cert.substitute(p, {pivot: {(): triples.Q(1)}}) for p in equations]
    nD = len(description['basis_indices'])
    return description, rows, [i for i in range(nD) if i != pivot]


def produce(number, pivot):
    start = time.perf_counter()
    description, rows, variables = construct(triples.Model(), number, pivot)
    nD = len(description['basis_indices'])
    baseline, base_rank = necessary_relations(rows, nD, [()])
    relations, expanded_rank = necessary_relations(rows, nD, [()] + [(i,) for i in variables])
    baseline_rank, new, total_rank = select_new(baseline, relations, variables)
    packet = {'family': number, 'pivot': pivot, 'system': description,
              'variables': variables, 'multiplier_degree_bound': 1,
              'baseline': baseline, 'relations': relations, 'selected_new': new,
              'discovery': {'physical_rows': len(rows),
                            'expanded_rows': len(rows) * (1 + len(variables)),
                            'baseline_equation_rank': base_rank,
                            'expanded_equation_rank': expanded_rank,
                            'baseline_multiple_rank': baseline_rank,
                            'denominator_relation_rank': total_rank,
                            'seconds': time.perf_counter() - start}}
    packet['continuation'] = continue_search(rows, packet)
    OUT.mkdir(parents=True, exist_ok=True)
    with gzip.open(OUT / f'chart-{number}-{pivot}.json.gz', 'wt', encoding='utf-8') as f:
        json.dump(packet, f, separators=(',', ':'))
    return packet


def continue_search(rows, packet, max_degree=4):
    """Bounded coordinate-power propagation, followed by the full physical test."""
    nD = len(packet['system']['basis_indices'])
    nvars = nD + len(packet['system']['Koszul_indices'])
    pivot = packet['pivot']
    necessary = [cert.decode(r['polynomial']) for r in packet['baseline']]
    necessary += [cert.decode(packet['relations'][j]['polynomial']) for j in packet['selected_new']]
    proof = cert.prove_chart(necessary, nD, pivot)
    assert not proof['excluded']  # Current three cases; no generic claim.
    maps = chart_maps(nD, pivot, proof)
    result = {'family': packet['family'], 'pivot': pivot,
              'denominator_chart': proof, 'power_stages': [], 'attempts': []}
    for iteration in range(nD):
        current = [cert.substitute(p, maps) for p in necessary]
        active = sorted({i for p in current for m in p for i in m})
        found = []
        for degree in range(3, max_degree + 1):
            start = time.perf_counter(); expanded = []; labels = []
            for j, p in enumerate(current):
                if not p:
                    continue
                for size in range(degree - max(map(len, p)) + 1):
                    for mon in combinations_with_replacement(active, size):
                        expanded.append(cert.product(p, {mon: triples.Q(1)})); labels.append((j, mon))
            witness, _, rank = cert.reduce_span(expanded)
            def terms(w):
                return [[labels[j][0], list(labels[j][1]), c] for j, c in w['equation_weights']]
            w = witness({(): triples.Q(1)})
            if w:
                found.append({'constant': True, 'products': terms(w)})
            else:
                for i in active:
                    for power in range(1, degree + 1):
                        w = witness({(i,) * power: triples.Q(1)})
                        if w is not None:
                            found.append({'coordinate': i, 'power': power, 'products': terms(w)})
                            break
            result['attempts'].append({'iteration': iteration, 'degree': degree,
                                       'active_variables': len(active), 'rows': len(expanded),
                                       'rank': rank, 'identities_found': len(found),
                                       'seconds': time.perf_counter() - start})
            if found:
                result['power_stages'].append({'degree': degree, 'claims': found})
                break
        if found and found[0].get('constant'):
            result['excluded'] = True
            break
        if found:
            changes = {r['coordinate']: {} for r in found}
            maps = {i: cert.substitute(p, changes) for i, p in maps.items()}
        physical = cert.prove_chart([cert.substitute(p, maps) for p in rows], nvars, pivot)
        result['physical_closure'] = physical
        result['excluded'] = physical['excluded']
        if physical['excluded'] or not found:
            break
    return result


def verify_relation(rows, nD, variables, relation):
    claimed = cert.decode(relation['polynomial'])
    assert claimed and all(all(i in variables for i in m) for m in claimed)
    actual = {}
    for j, mon, coefficient in relation['products']:
        assert 0 <= j < len(rows) and len(mon) <= 1
        assert all(i in variables for i in mon)
        actual = triples.base.padd(actual, cert.product(rows[j], {tuple(mon): triples.Q(coefficient)}))
    assert actual == claimed
    assert all(all(i < nD for i in m) for m in actual)
    return len(relation['products'])


def chart_maps(nD, pivot, proof):
    maps = {i: ({(): triples.Q(1)} if i == pivot else {(i,): triples.Q(1)})
            for i in range(nD)}
    for stage in proof['stages']:
        changes = {int(i): cert.decode(p) for i, p in stage['changes'].items()}
        maps = {i: cert.substitute(p, changes) for i, p in maps.items()}
    return maps


def verify_continuation(rows, packet):
    continuation = packet['continuation']
    assert (continuation['family'], continuation['pivot']) == (packet['family'], packet['pivot'])
    nD = len(packet['system']['basis_indices'])
    nvars = nD + len(packet['system']['Koszul_indices'])
    necessary = [cert.decode(r['polynomial']) for r in packet['baseline']]
    necessary += [cert.decode(packet['relations'][j]['polynomial']) for j in packet['selected_new']]
    proof = continuation['denominator_chart']
    assert proof['pivot'] == packet['pivot'] and not proof['excluded']
    counts = Counter(chart_inferences=cert.verify_chart(necessary, nD, proof))
    maps = chart_maps(nD, packet['pivot'], proof)
    contradiction = False
    for stage in continuation['power_stages']:
        assert not contradiction and stage['claims'] and 3 <= stage['degree'] <= 5
        current = [cert.substitute(p, maps) for p in necessary]
        active = {i for p in current for m in p for i in m}
        removed = set()
        for claim in stage['claims']:
            actual = {}
            for j, mon, coefficient in claim['products']:
                assert 0 <= j < len(current) and all(i in active for i in mon)
                term = cert.product(current[j], {tuple(mon): triples.Q(coefficient)})
                assert all(len(m) <= stage['degree'] for m in term)
                actual = triples.base.padd(actual, term)
                counts['power_equation_products'] += 1
            if claim.get('constant'):
                assert actual == {(): triples.Q(1)}
                contradiction = True
            else:
                i, power = claim['coordinate'], claim['power']
                assert i in active and i not in removed and 1 <= power <= stage['degree']
                assert actual == {(i,) * power: triples.Q(1)}
                removed.add(i)
            counts['power_identities'] += 1
        # Over C (indeed any field), a nonzero positive power vanishes only
        # when its coordinate vanishes. No real-positivity assumption is used.
        changes = {i: {} for i in removed}
        maps = {i: cert.substitute(p, changes) for i, p in maps.items()}
    if not contradiction:
        proof = continuation['physical_closure']
        assert proof['pivot'] == packet['pivot']
        current = [cert.substitute(p, maps) for p in rows]
        counts['chart_inferences'] += cert.verify_chart(current, nvars, proof)
        contradiction = proof['excluded']
    assert contradiction == continuation['excluded']
    counts['excluded_charts'] = int(contradiction)
    return counts


def verify(model, packet):
    description, rows, variables = construct(model, packet['family'], packet['pivot'])
    assert description == packet['system'] and variables == packet['variables']
    assert packet['multiplier_degree_bound'] == 1
    nD = len(description['basis_indices'])
    baseline, rank = necessary_relations(rows, nD, [()])
    assert baseline == packet['baseline']
    counts = Counter()
    for relation in packet['baseline'] + packet['relations']:
        counts['equation_products'] += verify_relation(rows, nD, variables, relation)
        counts['identities'] += 1
    old_rank, new, total_rank = select_new(baseline, packet['relations'], variables)
    assert new == packet['selected_new']
    discovery = packet['discovery']
    assert discovery['physical_rows'] == len(rows)
    assert discovery['expanded_rows'] == len(rows) * (1 + len(variables))
    assert discovery['baseline_equation_rank'] == rank
    assert discovery['baseline_multiple_rank'] == old_rank
    assert discovery['denominator_relation_rank'] == total_rank == len(packet['relations'])
    # Expanded matrix rank/timing are discovery telemetry. Replay establishes
    # each displayed identity and its independence, not full syzygy completeness.
    counts['new_independent_relations'] = len(new)
    if 'continuation' in packet:
        counts.update(verify_continuation(rows, packet))
    return counts


def check(independent=False):
    if independent:
        from check_degree7_triples import IndependentModel
        model = IndependentModel()
    else:
        model = triples.Model()
    start = time.perf_counter(); counts = Counter(); charts = []
    for number, pivot in CASES:
        with gzip.open(OUT / f'chart-{number}-{pivot}.json.gz', 'rt', encoding='utf-8') as f:
            packet = json.load(f)
        assert (packet['family'], packet['pivot']) == (number, pivot)
        checked = verify(model, packet); counts.update(checked)
        charts.append({'family': number, 'pivot': pivot, **checked})
    # Replay the earlier reductions which establish the retained denominator
    # spaces, and check that the successful family has a complete chart cover.
    first_pass = shared.read_packet()['families']
    for number in sorted({n for n, _ in CASES}):
        triples.verify_family(model, first_pass[number - 1])
    closed = []
    for number in sorted({n for n, _ in CASES}):
        expected, _, _ = construct(model, number, next(p for n, p in CASES if n == number))
        attempted = {c['pivot'] for c in charts if c['family'] == number}
        if attempted == set(expected['pivots']) and all(c['excluded_charts'] for c in charts if c['family'] == number):
            closed.append(number)
    bad = copy.deepcopy(packet)
    bad['relations'][0]['products'][0][2] = str(triples.Q(bad['relations'][0]['products'][0][2]) + 1)
    try:
        verify(model, bad)
    except AssertionError:
        pass
    else:
        raise AssertionError('Damaged relation was accepted')
    bad_power = copy.deepcopy(packet)
    bad_power['continuation']['power_stages'][0]['claims'][0]['products'][0][2] = '0'
    _, original_rows, _ = construct(model, packet['family'], packet['pivot'])
    try:
        verify_continuation(original_rows, bad_power)
    except AssertionError:
        pass
    else:
        raise AssertionError('Damaged coordinate-power identity was accepted')
    result = {'status': 'PASS', 'charts': charts, **counts,
              'fully_excluded_families': closed,
              'corrupted_identity_rejected': True,
              'corrupted_power_identity_rejected': True,
              'independent_polynomial_construction': independent,
              'seconds': time.perf_counter() - start}
    print(json.dumps(result, indent=2), flush=True)
    return result


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Run without -O.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--independent', action='store_true')
    parser.add_argument('--family', type=int)
    parser.add_argument('--pivot', type=int)
    parser.add_argument('--continue', dest='continue_only', action='store_true',
                        help='Reuse archived syzygies and regenerate bounded power continuation.')
    args = parser.parse_args()
    if args.check:
        check(args.independent)
    else:
        if (args.family, args.pivot) not in CASES:
            parser.error('Choose --family/--pivot from 87/2, 115/0, 115/10.')
        if args.continue_only:
            path = OUT / f'chart-{args.family}-{args.pivot}.json.gz'
            with gzip.open(path, 'rt', encoding='utf-8') as f:
                result = json.load(f)
            _, rows, _ = construct(triples.Model(), args.family, args.pivot)
            result['continuation'] = continue_search(rows, result)
            with gzip.open(path, 'wt', encoding='utf-8') as f:
                json.dump(result, f, separators=(',', ':'))
        else:
            result = produce(args.family, args.pivot)
        print(json.dumps({'discovery': result['discovery'],
                          'continuation_excluded': result['continuation']['excluded']}, indent=2), flush=True)

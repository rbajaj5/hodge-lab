"""Exact degree-three strands of the remaining selected necessary ideals.

The quadratics come from physical left annihilators of the enlarged Koszul
correction space. This is a necessary ideal, not the full certificate scheme.
No CAS is needed. Run with -S; --check reconstructs and replays the packet.
"""
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations_with_replacement as monomials
from math import comb
from pathlib import Path
import argparse, copy, gzip, hashlib, json, sys, time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'algebra'))
import degree7_triples as t

OUT = ROOT / 'results/eisenbud-linear-strand'
NUMBERS = [1, 2, 4, 5, 6, 7, 8, 9, 10, 15, 17, 39, 149, 150, 151, 152]
MAX_STAGES = 6


def original():
    with gzip.open(t.OUT / 'certificates.json.gz', 'rt', encoding='utf-8') as f:
        data = json.load(f)
    selected = [r for r in data['families'] if r['number'] in NUMBERS]
    assert [r['number'] for r in selected] == NUMBERS
    return selected


def source_hashes():
    paths = ['results/degree7-triples/certificates.json.gz',
             'algebra/degree7_e1_basis.json', 'sources/sextics/data/holdout/instance.rec']
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}


def mac_map(equations, ids, degree):
    labels = [(j, m) for j in range(len(equations))
              for m in monomials(ids, degree - 2)]
    rows = [t.cert.product(equations[j], {m: Q(1)}) for j, m in labels]
    return labels, rows


def strand(equations, ids, degree):
    labels, rows = mac_map(equations, ids, degree)
    span = t.base.Elimination(); dependencies = []
    for k, row in enumerate(rows):
        rel = span.insert(dict(row), {k: Q(1)})
        if rel is not None:
            dependencies.append([[j, str(c)] for j, c in sorted(rel.items())])
    found = []
    for i in ids:
        residual = {(i,) * degree: Q(1)}; weights = {}
        while residual:
            pivot = min(residual)
            if pivot not in span.basis: break
            c = residual[pivot]; row, rep = span.basis[pivot]
            residual = t.base.padd(residual, row, -c)
            weights = t.base.padd(weights, rep, c)
        if not residual:
            found.append({'coordinate': i, 'power': degree,
                          'products': [[labels[j][0], list(labels[j][1]), str(c)]
                                       for j, c in sorted(weights.items())]})
    rank = len(span.basis)
    return {'degree': degree, 'domain': len(rows), 'codomain': comb(len(ids)+degree-1, degree),
            'rank': rank, 'kernel': len(rows)-rank,
            'quotient_dimension': comb(len(ids)+degree-1, degree)-rank,
            'dependencies': dependencies, 'vanishings': found,
            'tested_coordinates': ids}


def decode_weights(items): return {i: Q(c) for i, c in items}


def expand_products(equations, products):
    # Separate coefficient-by-coefficient multiplication; no generator product API.
    total = {}
    for j, mon, c in products:
        for term, value in equations[j].items():
            key = tuple(sorted(tuple(mon) + term))
            total[key] = total.get(key, Q(0)) + Q(c) * value
    return {m: c for m, c in total.items() if c}


def check_strand(equations, ids, record):
    degree = record['degree']; labels, rows = mac_map(equations, ids, degree)
    # A different field gives a rank lower bound; the rational elimination gives
    # the exact rank. Agreement is a check, not a standalone characteristic-zero proof.
    exact = t.base.Elimination(); modular = t.base.Elimination(prime=1000003)
    for row in rows:
        exact.insert(dict(row))
        modular.insert({m: (c.numerator * pow(c.denominator, -1, 1000003)) % 1000003
                        for m, c in row.items()})
    assert len(exact.basis) == len(modular.basis) == record['rank']
    assert record['domain'] == len(rows)
    assert record['codomain'] == comb(len(ids)+degree-1, degree)
    assert record['kernel'] == len(rows)-record['rank'] == len(record['dependencies'])
    assert record['quotient_dimension'] == record['codomain']-record['rank']
    previous = -1
    for relation in record['dependencies']:
        weights = decode_weights(relation)
        assert weights and max(weights) > previous and weights[max(weights)] == 1
        previous = max(weights)  # Distinct final pivots prove independence.
        assert all(0 <= k < len(labels) for k in weights)
        products = [[labels[k][0], labels[k][1], c] for k, c in weights.items()]
        assert not expand_products(equations, products)
    assert record['tested_coordinates'] == ids
    expected = []
    for i in ids:
        if not t.normal({(i,)*degree: Q(1)}, exact): expected.append(i)
    assert [p['coordinate'] for p in record['vanishings']] == expected
    for proof in record['vanishings']:
        assert proof['power'] == degree
        assert all(len(m) == degree-2 and all(i in ids for i in m)
                   for _, m, _ in proof['products'])
        assert expand_products(equations, proof['products']) == {(proof['coordinate'],)*degree: Q(1)}


def check_physical(model, stage):
    ids = stage['active']; checks = Counter()
    for necessity in stage['necessary']:
        target = tuple(necessity['target']); dual = t.e1.decode(necessity['dual'])
        assert dual and all(sum(m) == 14 and m[0] < 6 and t.e1.character(m) == target for m in dual)
        for i in ids:
            for _, column in model.corrections(i, target):
                assert t.dot(dual, column) == 0
                checks['correction_pairings'] += 1
        expected = {}
        for i, j in monomials(ids, 2):
            if model.target(i, j) != target: continue
            c = t.dot(dual, model.quadratic(i, j))
            if c: expected[(i, j)] = c
            checks['quadratic_pairings'] += 1
        assert expected == t.cert.decode(necessity['polynomial']) and expected
        checks['physical_duals'] += 1
    return checks


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    model = t.Model(); families = []
    for initial in original():
        start = time.perf_counter(); ids = initial['remaining'][:]; stages = []
        necessary = copy.deepcopy(initial['stages'][-1]['necessary'])
        for _ in range(MAX_STAGES):
            equations = [t.cert.decode(r['polynomial']) for r in necessary]
            strands = [strand(equations, ids, d) for d in (2, 3)]
            removed = sorted({p['coordinate'] for s in strands for p in s['vanishings']})
            stages.append({'active': ids[:], 'necessary': necessary, 'strands': strands,
                           'removed': removed})
            print(initial['number'], len(stages), len(ids), 'parameters', len(equations),
                  'quadratics', 'linear syzygies', strands[1]['kernel'], 'removed', removed, flush=True)
            if not removed: break
            ids = [i for i in ids if i not in removed]
            if len({model.dc[i] for i in ids}) < 3: break
            necessary, _ = model.necessities(ids)
        stop = ('at_most_two_characters' if len({model.dc[i] for i in ids}) < 3 else
                'no_coordinate_power_through_degree_three' if not stages[-1]['removed'] else 'stage_limit')
        families.append({'number': initial['number'], 'characters': initial['characters'],
                         'initial_active': initial['remaining'], 'stages': stages,
                         'remaining': ids, 'stop': stop, 'seconds': time.perf_counter()-start})
        with gzip.open(OUT / 'certificates.json.gz', 'wt', encoding='utf-8') as f:
            json.dump({'sources': source_hashes(), 'max_stages': MAX_STAGES, 'families': families}, f,
                      separators=(',', ':'))


def check(independent=False):
    start = time.perf_counter()
    with gzip.open(OUT / 'certificates.json.gz', 'rt', encoding='utf-8') as f: packet = json.load(f)
    assert packet['sources'] == source_hashes() and packet['max_stages'] == MAX_STAGES
    assert [f['number'] for f in packet['families']] == NUMBERS
    if independent:
        from check_degree7_triples import IndependentModel
        model = IndependentModel()
    else:
        model = t.Model()
    counts = Counter(); summary = []
    for before, family in zip(original(), packet['families']):
        counts.update(t.verify_family(model, before))
        assert family['characters'] == before['characters']
        ids = before['remaining'][:]
        assert family['initial_active'] == ids
        assert family['stages'][0]['necessary'] == before['stages'][-1]['necessary']
        assert 1 <= len(family['stages']) <= MAX_STAGES
        for stage in family['stages']:
            assert stage['active'] == ids
            counts.update(check_physical(model, stage))
            equations = [t.cert.decode(r['polynomial']) for r in stage['necessary']]
            assert all(len(m) == 2 for p in equations for m in p)
            assert [s['degree'] for s in stage['strands']] == [2, 3]
            for s in stage['strands']:
                check_strand(equations, ids, s)
                counts['strand_maps'] += 1
                counts['replayed_syzygies'] += s['kernel']
                counts['new_power_identities'] += len(s['vanishings'])
            assert stage['strands'][0]['kernel'] == 0  # Minimal quadratic generators.
            removed = sorted({p['coordinate'] for s in stage['strands'] for p in s['vanishings']})
            assert stage['removed'] == removed
            ids = [i for i in ids if i not in removed]
        assert family['remaining'] == ids
        expected_stop = ('at_most_two_characters' if len({model.dc[i] for i in ids}) < 3 else
                         'no_coordinate_power_through_degree_three' if not family['stages'][-1]['removed']
                         else 'stage_limit')
        assert family['stop'] == expected_stop
        summary.append({'number': family['number'], 'initial': len(family['initial_active']),
                        'remaining': len(ids), 'removed': sorted(set(family['initial_active'])-set(ids)),
                        'stages': [{'variables': len(s['active']), 'quadratics': len(s['necessary']),
                                    'linear_syzygies': s['strands'][1]['kernel'],
                                    'cubic_rank': s['strands'][1]['rank'],
                                    'cubic_quotient': s['strands'][1]['quotient_dimension'],
                                    'removed': s['removed']} for s in family['stages']], 'stop': expected_stop})
        print('checked family', family['number'], flush=True)
    # Deliberately damage a real discovered identity; the independent expansion must reject it.
    stage = next(s for f in packet['families'] for s in f['stages'] if s['removed'])
    proof = copy.deepcopy(next(p for s in stage['strands'] for p in s['vanishings']))
    proof['products'][0][2] = str(Q(proof['products'][0][2])+1)
    equations = [t.cert.decode(r['polynomial']) for r in stage['necessary']]
    assert expand_products(equations, proof['products']) != {(proof['coordinate'],)*proof['power']: Q(1)}
    report = {'status': 'PASS', 'sources': source_hashes(), 'families': summary, 'checks': dict(counts),
              'corrupted_identity_rejected': True, 'seconds': time.perf_counter()-start,
              'independent_physical_polynomials': independent,
              'scope': 'Degree 2/3 pieces of necessary ideals; not a full free resolution, not a certificate.'}
    name = 'independent-validation.json' if independent else 'validation.json'
    (OUT / name).write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ['families','sources']}, indent=2))


if __name__ == '__main__':
    if not __debug__: raise RuntimeError('Run without -O.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--independent', action='store_true', help='Use with --check: separate physical polynomial API.')
    args = parser.parse_args()
    if args.independent and not args.check: parser.error('--independent requires --check')
    check(args.independent) if args.check else run()

"""Systematic necessary-condition tests of complete three-character D7 families.

Extends fqlx's enlarged-correction pair test to three characters. We eliminate
each B(D_i,K_j) independently, a relaxation of the shared numerator correction.
A rejection is valid; survival is NOT a certificate. Exact physical duals and
polynomial multipliers make every reported vanishing replayable without a CAS.
"""
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
from itertools import combinations, combinations_with_replacement
from pathlib import Path
import argparse, copy, gzip, hashlib, json, time

import degree6_e1 as base
import degree7_e1 as e1
import degree7_character_search as cert
from degree6_e2_model import modF
from degree6_quadratic_structure import B

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/degree7-triples'


def plus(a, b): return tuple((x + y) % 6 for x, y in zip(a, b))
def minus(a, b): return tuple((x - y) % 6 for x, y in zip(a, b))
def pairkey(i, j): return tuple(sorted((i, j)))


def selected_families(data):
    groups = {tuple(f['character']): f['basis_indices'] for f in data['character_families']}
    coordinates = [tuple(w[i] for w in e1.WEIGHTS) for i in range(6)]
    anchor = (coordinates[0], coordinates[3])
    families = {tuple(sorted((*anchor, c))) for c in groups if c not in anchor}
    families.update(combinations(sorted(coordinates), 3))
    assert len(families) == 152
    return groups, sorted(families)


def normal(p, span):
    p = dict(p)
    for pivot, (row, _) in sorted(span.basis.items()):
        if pivot in p: p = base.padd(p, row, -p[pivot])
    return p


def dual_for(m, span):
    """Coefficient m of the normal form as a functional on the input."""
    dual = {m: Q(1)}
    for pivot, (row, _) in sorted(span.basis.items(), reverse=True):
        c = -sum(v * dual.get(n, 0) for n, v in row.items() if n != pivot)
        if c: dual[pivot] = c
    return dual


def dot(dual, p): return sum(c * p.get(m, 0) for m, c in dual.items())


class Model:
    def __init__(self):
        self.data, self.pairs = e1.load()
        self.fields, _ = e1.koszul_fields()
        self.groups, self.families = selected_families(self.data)
        self.dc = {i: c for c, ids in self.groups.items() for i in ids}
        self.alpha = e1.character(next(iter(base.A)))
        self.kgroups = {}
        for k, field in enumerate(self.fields):
            weights = e1.field_characters(field)
            assert len(weights) == 1
            self.kgroups.setdefault(weights.pop(), []).append(k)

    def target(self, i, j): return plus(self.alpha, plus(self.dc[i], self.dc[j]))

    @lru_cache(None)
    def quadratic(self, i, j):
        D, N = self.pairs[i]; E, P = self.pairs[j]
        p = B(D, P)
        if i != j: p = base.padd(p, B(E, N))
        return modF(p)

    @lru_cache(None)
    def corrections(self, i, target):
        return [(k, modF(B(self.pairs[i][0], self.fields[k])))
                for k in self.kgroups.get(minus(target, self.dc[i]), [])]

    def necessities(self, ids):
        targets = sorted({self.target(i, j) for i, j in combinations_with_replacement(ids, 2)})
        result = []; ranks = []
        for target in targets:
            span = base.Elimination()
            for i in ids:
                for _, column in self.corrections(i, target): span.insert(dict(column))
            ranks.append([list(target), len(span.basis)])
            physical = {}
            for i, j in combinations_with_replacement(ids, 2):
                if self.target(i, j) != target: continue
                for m, c in normal(self.quadratic(i, j), span).items():
                    physical.setdefault(m, {})[(i, j)] = c
            # Retain an independent subset of physical coefficient equations;
            # the associated physical duals still refer to the original E2.
            independent = base.Elimination()
            for m, p in sorted(physical.items()):
                if independent.insert(dict(p)) is not None: continue
                result.append({'target': list(target), 'polynomial': cert.encode(p),
                               'dual': base.poly_json(dual_for(m, span))})
        return result, ranks


def power_witnesses(equations, ids):
    # Bounded deterministic search. The record distinguishes failure at these
    # degrees from absence of higher-degree polynomial consequences.
    attempted = []
    for degree in [2] + ([3] if len(ids) <= 12 else []) + ([4] if len(ids) <= 8 else []):
        rows = []; labels = []
        for j, p in enumerate(equations):
            for mon in combinations_with_replacement(ids, degree - 2):
                rows.append(cert.product(p, {mon: Q(1)})); labels.append((j, mon))
        witness, _, rank = cert.reduce_span(rows)
        found = []
        for i in ids:
            w = witness({(i,) * degree: Q(1)})
            if w:
                found.append({'coordinate': i, 'power': degree,
                              'products': [[labels[j][0], list(labels[j][1]), c]
                                           for j, c in w['equation_weights']]})
        attempted.append({'degree': degree, 'rows': len(rows), 'rank': rank})
        if found: return found, attempted
    return [], attempted


def run_family(model, chars, number):
    start = time.perf_counter()
    original = sorted(i for c in chars for i in model.groups[c]); ids = original[:]
    stages = []
    while ids and len({model.dc[i] for i in ids}) == 3:
        necessary, ranks = model.necessities(ids)
        equations = [cert.decode(r['polynomial']) for r in necessary]
        vanishings, attempted = power_witnesses(equations, ids)
        stages.append({'active': ids[:], 'necessary': necessary, 'correction_ranks': ranks,
                       'power_search': attempted, 'vanishings': vanishings})
        if not vanishings: break
        removed = {w['coordinate'] for w in vanishings}
        ids = [i for i in ids if i not in removed]
    status = ('excluded_directly' if not ids else 'reduced_to_at_most_two_characters'
              if len({model.dc[i] for i in ids}) <= 2 else 'unresolved_three_characters')
    row = {'number': number, 'characters': [list(c) for c in chars], 'basis_indices': original,
           'stages': stages, 'remaining': ids, 'status': status, 'seconds': time.perf_counter() - start}
    print(number, [list(c) for c in chars], len(original), '->', len(ids), status,
          round(row['seconds'], 2), 's', flush=True)
    return row


def verify_family(model, row):
    chars = tuple(tuple(c) for c in row['characters'])
    ids = sorted(i for c in chars for i in model.groups[c])
    assert ids == row['basis_indices']
    checks = Counter()
    for stage in row['stages']:
        assert stage['active'] == ids and len({model.dc[i] for i in ids}) == 3
        equations = []
        for necessity in stage['necessary']:
            target = tuple(necessity['target']); dual = e1.decode(necessity['dual'])
            assert dual and all(sum(m) == 14 and m[0] < 6 and e1.character(m) == target for m in dual)
            for i in ids:
                for _, p in model.corrections(i, target):
                    assert dot(dual, p) == 0
                    checks['correction_pairings'] += 1
            expected = {}
            for i, j in combinations_with_replacement(ids, 2):
                if model.target(i, j) != target: continue
                c = dot(dual, model.quadratic(i, j))
                if c: expected[(i, j)] = c
                checks['quadratic_pairings'] += 1
            assert cert.decode(necessity['polynomial']) == expected and expected
            equations.append(expected); checks['physical_duals'] += 1
        removed = set()
        for claim in stage['vanishings']:
            i, power = claim['coordinate'], claim['power']
            assert i in ids and i not in removed and power in (2, 3, 4)
            total = {}
            for j, mon, c in claim['products']:
                assert 0 <= j < len(equations) and len(mon) == power - 2 and all(k in ids for k in mon)
                total = base.padd(total, cert.product(equations[j], {tuple(mon): Q(c)}))
            assert total == {(i,) * power: Q(1)}
            removed.add(i); checks['power_identities'] += 1
        ids = [i for i in ids if i not in removed]
    assert row['remaining'] == ids
    status = ('excluded_directly' if not ids else 'reduced_to_at_most_two_characters'
              if len({model.dc[i] for i in ids}) <= 2 else 'unresolved_three_characters')
    assert row['status'] == status
    if status == 'reduced_to_at_most_two_characters':
        # This batch has one explicit closure dependency, already archived
        # and replayed in CI: the complete X0/Y0 pair, including its subspaces.
        assert {model.dc[i] for i in ids} <= {(0, 0, 1), (1, 2, 3)}
    return checks


def summary(families):
    return {'families': len(families), 'statuses': dict(Counter(r['status'] for r in families)),
            'initial_parameters': dict(Counter(len(r['basis_indices']) for r in families)),
            'remaining_parameters': dict(Counter(len(r['remaining']) for r in families)),
            'vanishing_identities': sum(len(s['vanishings']) for r in families for s in r['stages'])}


def run(limit=None):
    start = time.perf_counter(); model = Model(); families = []
    OUT.mkdir(parents=True, exist_ok=True)
    for number, chars in enumerate(model.families[:limit], 1):
        row = run_family(model, chars, number)
        verify_family(model, row); families.append(row)
        # One checkpoint is valid even if a later family exceeds resources.
        packet = {'basis_sha256': hashlib.sha256(e1.BASIS.read_bytes()).hexdigest(),
                  'selection': 'all 136 X0/Y0 extensions plus 20 coordinate-character triples; 4 overlaps',
                  'families': families}
        pending = OUT / 'certificates.json.gz.tmp'
        with gzip.open(pending, 'wt', encoding='utf-8') as f:
            json.dump(packet, f, separators=(',', ':'))
        pending.replace(OUT / 'certificates.json.gz')
    report = {**summary(families), 'complete_selection': len(families) == 152,
              'total_three_character_families': 428536, 'seconds': time.perf_counter() - start,
              'scope': 'Full retained E1 eigenspaces, not isolated denominators. Corrections are enlarged independently; survival is inconclusive. Reduction to <=2 characters uses the separately established pair exclusions, not a new proof of them. No HasCertificate proof.'}
    (OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, indent=2), flush=True)


def check():
    start = time.perf_counter(); model = Model(); counts = Counter()
    with gzip.open(OUT / 'certificates.json.gz', 'rt', encoding='utf-8') as f: packet = json.load(f)
    assert packet['basis_sha256'] == hashlib.sha256(e1.BASIS.read_bytes()).hexdigest()
    assert len(packet['families']) == 152
    for number, (chars, row) in enumerate(zip(model.families, packet['families']), 1):
        assert row['number'] == number and row['characters'] == [list(c) for c in chars]
        counts.update(verify_family(model, row))
    # A changed polynomial or multiplier must not be accepted.
    broken = copy.deepcopy(next(r for r in packet['families'] if any(s['vanishings'] for s in r['stages'])))
    claim = next(s['vanishings'][0] for s in broken['stages'] if s['vanishings'])
    claim['products'][0][2] = str(2 * Q(claim['products'][0][2]))
    try: verify_family(model, broken)
    except AssertionError: pass
    else: raise AssertionError('Corrupted identity was accepted.')
    report = json.loads((OUT / 'report.json').read_text())
    for key, value in summary(packet['families']).items():
        assert json.dumps(report[key], sort_keys=True) == json.dumps(value, sort_keys=True)
    result = {'status': 'PASS', **counts, 'corrupted_identity_rejected': True,
              'seconds': time.perf_counter() - start}
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    if not __debug__: raise RuntimeError('Run without -O.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--limit', type=int, help='Discovery pilot only; full check requires all 152.')
    args = parser.parse_args()
    if args.check: check()
    else: run(args.limit)

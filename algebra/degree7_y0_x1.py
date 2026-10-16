"""Exact closure of the degree-seven {chi_Y0, chi_X1} denominator family.

This is family 22 of fqlx's published list of 35 mixed residuals, one of
three left open there. The construction starts with the complete two-character
E1 space modulo F*S1, retaining the full subgroup-projected numerator kernel.
All saved inferences are checked by exact original-equation combinations.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations_with_replacement, product
import argparse
import copy
import gzip
import hashlib
import json
import time
import degree6_e1 as base
import degree7_e1 as e1
import degree7_character_search as cert
from degree6_e2_model import modF
from degree6_quadratic_structure import B

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'results/degree7-y0-x1'
CHARACTERS = ((0, 1, 0), (1, 2, 3))


def plus(a, b):
    return tuple((x + y) % 6 for x, y in zip(a, b))


def construct():
    data, lifts = e1.load()
    fields, _ = e1.koszul_fields()
    alpha = e1.character(next(iter(base.A)))
    w, z = CHARACTERS
    delta = tuple((b-a) % 6 for a, b in zip(w, z))
    cyclic = {tuple(k*x % 6 for x in delta) for k in range(6)}
    group = list(product(range(6), repeat=3))
    subgroup = [g for g in group if sum(x*y for x, y in zip(g, delta)) % 6 == 0]
    annihilator = {c for c in group if all(sum(x*y for x, y in zip(c, g)) % 6 == 0 for g in subgroup)}
    assert annihilator == cyclic and len(subgroup) == 36
    wanted = {plus(plus(alpha, w), c) for c in cyclic}
    ids = [i for f in data['character_families'] if tuple(f['character']) in CHARACTERS
           for i in f['basis_indices']]
    ks = [k for k, field in enumerate(fields) if e1.field_characters(field) <= wanted]
    assert len(ids) == 14 and len(ks) == 60
    physical = {}

    def append(polynomial, parameter):
        for m, c in modF(polynomial).items():
            physical.setdefault(m, {})[parameter] = c

    for i, j in combinations_with_replacement(range(len(ids)), 2):
        D, N = lifts[ids[i]]
        E, P = lifts[ids[j]]
        value = B(D, P)
        if i != j:
            value = base.padd(value, B(E, N))
        append(value, (i, j))
    for i, original in enumerate(ids):
        for j, k in enumerate(ks):
            append(B(lifts[original][0], fields[k]), (i, len(ids)+j))
    monomials = sorted(physical)
    equations = [physical[m] for m in monomials]
    description = {
        'basis_sha256': hashlib.sha256(e1.BASIS.read_bytes()).hexdigest(),
        'characters': [list(c) for c in CHARACTERS],
        'denominator_basis_indices': ids, 'Koszul_indices': ks,
        'subgroup_order': len(subgroup),
        'physical_monomials': [list(m) for m in monomials],
        'equations': [cert.encode(p) for p in equations],
    }
    return description, equations


def transformed(equations, maps):
    return [cert.substitute(p, maps) for p in equations]


def verify_proof(equations, description, proof):
    nD = len(description['denominator_basis_indices'])
    nvars = nD + len(description['Koszul_indices'])
    maps = {i: {(i,): Q(1)} for i in range(nvars)}
    free = set(range(nD))
    assert [p['pivot'] for p in proof['initial_charts']] == list(range(nD))
    initial_exclusions = []
    inferences = 0
    for chart in proof['initial_charts']:
        inferences += cert.verify_chart(equations, nvars, chart)
        if chart['excluded']:
            initial_exclusions.append(chart['pivot'])
            maps[chart['pivot']] = {}
            free.remove(chart['pivot'])
    batches = []
    for step in proof['steps']:
        rows = transformed(equations, maps)
        if step['kind'] == 'linear_square':
            linear = cert.decode(step['linear'])
            assert linear and all(len(m) == 1 and m[0] in free for m in linear)
            actual = {}
            for index, coefficient in step['witness']['equation_weights']:
                assert 0 <= index < len(rows)
                actual = base.padd(actual, rows[index], Q(coefficient))
            assert actual == cert.product(linear, linear)
            assert cert.decode(step['witness']['polynomial']) == actual
            pivot = step['pivot']
            assert pivot in free and (pivot,) in linear
            changes = {pivot: {m: -c/linear[(pivot,)] for m, c in linear.items() if m != (pivot,)}}
            free.remove(pivot)
            inferences += 1
        else:
            assert step['kind'] == 'chart_batch'
            pivots = [p['pivot'] for p in step['proofs']]
            assert len(pivots) == len(set(pivots)) and set(pivots) <= free
            for chart in step['proofs']:
                assert chart['excluded']
                inferences += cert.verify_chart(rows, nvars, chart)
            changes = {i: {} for i in pivots}
            free -= set(pivots)
            batches.append(pivots)
        maps = {i: cert.substitute(p, changes) for i, p in maps.items()}
    assert proof['final_maps'] == {str(i): cert.encode(p) for i, p in maps.items()}
    assert proof['free_denominator_coordinates'] == sorted(free)
    data, lifts = e1.load()
    remaining = {e1.character(m) for i, original in enumerate(description['denominator_basis_indices'])
                 if maps[i] for m in lifts[original][0]}
    assert remaining == {(0, 1, 0)}
    assert proof['remaining_character'] == [0, 1, 0]
    # Completeness of the final exclusion comes from the separately replayed
    # single-character theorem, not from the mere vanishing of some coordinates.
    return {'initial_excluded_coordinates': initial_exclusions,
            'subsequent_exclusion_batches': batches,
            'remaining_free_denominator_coordinates': sorted(free),
            'remaining_character': [0, 1, 0], 'exact_inferences': inferences,
            'single_character_theorem_required': True}


def generate():
    start = time.perf_counter()
    description, equations = construct()
    nD = len(description['denominator_basis_indices'])
    nvars = nD + len(description['Koszul_indices'])
    initial = [cert.prove_chart(equations, nvars, i) for i in range(nD)]
    maps = {i: {(i,): Q(1)} for i in range(nvars)}
    free = set(range(nD))
    for chart in initial:
        cert.verify_chart(equations, nvars, chart)
        if chart['excluded']:
            maps[chart['pivot']] = {}
            free.remove(chart['pivot'])
    assert sorted(set(range(nD))-free) == [1, 6, 9]
    # Discovered by factoring necessary quadrics. Only the exact square
    # identity below is used as evidence; no numerical positivity is assumed.
    linear = {(7,): Q(3), (8,): Q(-6), (10,): Q(1), (12,): Q(1), (13,): Q(1)}
    witness, _, _ = cert.reduce_span(transformed(equations, maps))
    square = witness(cert.product(linear, linear))
    assert square
    steps = [{'kind': 'linear_square', 'linear': cert.encode(linear), 'witness': square, 'pivot': 7}]
    changes = {7: {m: -c/3 for m, c in linear.items() if m != (7,)}}
    maps = {i: cert.substitute(p, changes) for i, p in maps.items()}
    free.remove(7)
    for expected in ([11], [8, 10, 12, 13]):
        rows = transformed(equations, maps)
        charts = [cert.prove_chart(rows, nvars, i) for i in sorted(free)]
        excluded = [p for p in charts if p['excluded']]
        assert [p['pivot'] for p in excluded] == expected
        steps.append({'kind': 'chart_batch', 'proofs': excluded})
        changes = {i: {} for i in expected}
        maps = {i: cert.substitute(p, changes) for i, p in maps.items()}
        free -= set(expected)
    proof = {'initial_charts': initial, 'steps': steps,
             'final_maps': {str(i): cert.encode(p) for i, p in maps.items()},
             'free_denominator_coordinates': sorted(free), 'remaining_character': [0, 1, 0]}
    result = verify_proof(equations, description, proof)
    OUT.mkdir(parents=True, exist_ok=True)
    with gzip.open(OUT/'certificate.json.gz', 'wt', encoding='utf-8') as handle:
        json.dump({'system': description, 'proof': proof}, handle, separators=(',', ':'))
    report = {**result, 'degree': 7, 'denominator_coordinates': nD, 'Koszul_coordinates': len(description['Koszul_indices']),
              'physical_equations': len(equations), 'basis_sha256': description['basis_sha256'],
              'seconds': time.perf_counter()-start,
              'scope': 'The complete {chi_Y0, chi_X1} denominator family modulo F*S1 only. No certificate of existence and no general degree-seven exclusion.',
              'prior_work': 'fqlx Discussion 44 comment 18982957; this is the remaining family numbered 22 in that package.'}
    (OUT/'report.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, indent=2), flush=True)


def independent_equations(description):
    """Second physical-polynomial API, opposite division order, subgroup test."""
    import degree7_verify_polynomials as independent
    poly = independent.poly
    target = poly.load_target(ROOT/'sources/sextics/data/holdout')
    F, A = target['F'], target['A']
    assert F == base.F and A == base.A and target['q'] == 1
    data, lifts = e1.load()
    partials = [poly.derivative(F, i) for i in range(6)]
    W = data['character_generators']
    char = lambda m: tuple(sum(a*b for a, b in zip(row, m)) % 6 for row in W)
    w, z = CHARACTERS
    subgroup = [g for g in product(range(6), repeat=3)
                if sum((b-a)*c for a, b, c in zip(w, z, g)) % 6 == 0]
    required = plus(char(next(iter(A))), w)
    fields = []
    selected = []
    for k, (i, j, m) in enumerate(data['koszul_labels']):
        field = [{} for _ in range(6)]
        field[i] = poly.mul({tuple(m): Q(1)}, partials[j])
        field[j] = poly.scale(poly.mul({tuple(m): Q(1)}, partials[i]), -1)
        weights = {tuple((a-row[c]) % 6 for a, row in zip(char(n), W))
                   for c, p in enumerate(field) for n in p}
        assert len(weights) == 1
        weight = weights.pop()
        if all(sum((a-b)*c for a, b, c in zip(weight, required, g)) % 6 == 0 for g in subgroup):
            selected.append(k)
        fields.append(field)
    assert selected == description['Koszul_indices']
    ids = description['denominator_basis_indices']
    actual = {}
    columns = coefficients = 0
    def append(p, parameters):
        nonlocal columns, coefficients
        reduced = independent.remainder(p, F)
        columns += 1
        coefficients += len(reduced)
        for m, c in reduced.items():
            actual.setdefault(m, {})[parameters] = c
    for i, j in combinations_with_replacement(range(len(ids)), 2):
        D, N = lifts[ids[i]]
        E, P = lifts[ids[j]]
        value = independent.B(D, P)
        if i != j:
            value = poly.add(value, independent.B(E, N))
        append(value, (i, j))
    for i, original in enumerate(ids):
        for j, k in enumerate(selected):
            append(independent.B(lifts[original][0], fields[k]), (i, len(ids)+j))
    expected = {tuple(m): cert.decode(p) for m, p in zip(description['physical_monomials'], description['equations'])}
    assert actual == expected
    return {'columns_reconstructed': columns, 'coefficients_checked': coefficients,
            'opposite_physical_monomial_division': True, 'subgroup_selection_checked_independently': True}


def check():
    description, equations = construct()
    with gzip.open(OUT/'certificate.json.gz', 'rt', encoding='utf-8') as handle:
        packet = json.load(handle)
    assert description == packet['system']
    result = verify_proof(equations, description, packet['proof'])
    report = json.loads((OUT/'report.json').read_text())
    for key, value in result.items():
        assert report[key] == value
    independent = independent_equations(description)
    corrupted = copy.deepcopy(packet['proof'])
    square = next(step for step in corrupted['steps'] if step['kind'] == 'linear_square')
    square['witness']['equation_weights'][0][1] = str(2*Q(square['witness']['equation_weights'][0][1]))
    try:
        verify_proof(equations, description, corrupted)
    except AssertionError:
        pass
    else:
        raise AssertionError('Corrupted linear-square witness was accepted.')
    cert.check()
    print(json.dumps({**result, **independent, 'corrupted_square_rejected': True}, indent=2))


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Run without -O: assertions are part of verification.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    if parser.parse_args().check:
        check()
    else:
        generate()

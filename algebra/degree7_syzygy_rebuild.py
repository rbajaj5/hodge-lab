"""Family 115: rebuild after proven zeros, close chart 10, then refine chart 0.

Replay uses only the Python standard library and explicit rational identities.
This excludes one restricted degree-seven denominator family, not holdout.
"""
from collections import Counter
from pathlib import Path
import argparse, copy, gzip, hashlib, json, time

import degree7_syzygies as s

c = s.cert
OUT = s.triples.ROOT / 'results/degree7-syzygy-rebuild'


def read(path):
    with gzip.open(path, 'rt', encoding='utf-8') as f:
        return json.load(f)


def initial_maps(packet):
    """Use only the old denominator reductions, not mixed numerator maps."""
    nD = len(packet['system']['basis_indices'])
    maps = s.chart_maps(nD, packet['pivot'], packet['continuation']['denominator_chart'])
    for stage in packet['continuation']['power_stages']:
        assert all(not claim.get('constant') for claim in stage['claims'])
        changes = {claim['coordinate']: {} for claim in stage['claims']}
        maps = {i: c.substitute(p, changes) for i, p in maps.items()}
    return maps


def encode_maps(maps):
    return {str(i): c.encode(p) for i, p in maps.items()}


def verify_rebuilt_chart(rows, description, maps, packet):
    assert packet['system'] == description
    assert packet['family'] == 115 and packet['pivot'] == 10
    assert packet['maps'] == encode_maps(maps)
    nD = len(description['basis_indices'])
    current = [c.substitute(p, maps) for p in rows]
    variables = sorted({i for p in current for m in p for i in m if i < nD})
    assert variables == packet['variables']
    baseline, rank = s.necessary_relations(current, nD, [()])
    assert baseline == packet['baseline'] and rank == packet['baseline_rank']
    counts = Counter()
    for relation in packet['baseline'] + packet['relations']:
        counts['new_syzygy_products'] += s.verify_relation(current, nD, variables, relation)
        counts['new_syzygy_identities'] += 1
    _, new, _ = s.select_new(baseline, packet['relations'], variables)
    assert new == packet['selected_new']
    counts.update(s.verify_continuation(current, packet))
    assert packet['continuation']['excluded']
    return counts


def refine_maps(maps, excluded_pivots):
    changes = {pivot: {} for pivot in excluded_pivots}
    return {i: c.substitute(p, changes) for i, p in maps.items()}


def verify_refinement(rows, description, maps, packet, excluded_pivots):
    # A chart may force its normalized coordinate to zero globally only once
    # that chart has been proved impossible. Do not accept a claimed zero.
    removed = packet['additional_zero']
    assert removed == packet['dependency_closed_chart']
    assert removed in excluded_pivots
    maps = refine_maps(maps, [removed])
    assert packet['maps'] == encode_maps(maps)
    proof = packet['physical']
    assert proof['pivot'] == 0 and proof['excluded']
    nvars = len(description['basis_indices']) + len(description['Koszul_indices'])
    return c.verify_chart([c.substitute(p, maps) for p in rows], nvars, proof)


def verify_partial(model, number, pivot):
    """Replay two conditional chart improvements, without family closure."""
    family = s.shared.read_packet()['families'][number - 1]
    s.triples.verify_family(model, family)
    desc, rows, _ = s.construct(model, number, pivot)
    old = read(s.shared.OUT / f'family-{number}.json.gz')
    proof = next(p for p in old['charts'] if p['pivot'] == pivot)
    nD = len(desc['basis_indices']); nv = nD + len(desc['Koszul_indices'])
    c.verify_chart(rows, nv, proof)
    maps = s.chart_maps(nv, pivot, proof)
    packet = read(OUT / f'partial-{number}-{pivot}.json.gz')
    assert packet['system'] == desc and packet['maps'] == encode_maps(maps)
    assert (packet['family'], packet['pivot']) == (number, pivot)
    assert all(all(j < nD for m in maps[i] for j in m) for i in range(nD))
    current = [c.substitute(p, maps) for p in rows]
    variables = sorted({i for p in current for m in p for i in m if i < nD})
    assert variables == packet['variables']
    assert packet['selected_new'] == list(range(len(packet['relations'])))
    counts = Counter()
    for relation in packet['baseline'] + packet['relations']:
        counts['syzygy_products'] += s.verify_relation(current, nD, variables, relation)
        counts['syzygy_identities'] += 1
    counts.update(s.verify_continuation(current, packet))
    assert not packet['continuation']['excluded']
    return {'family': number, 'pivot': pivot, **counts, 'scope': 'Conditional chart consequences only; no global coordinate vanishing or family exclusion.'}


def check(independent=False):
    start = time.perf_counter()
    if independent:
        from check_degree7_triples import IndependentModel
        model = IndependentModel()
    else:
        model = s.triples.Model()
    dependencies = json.loads((OUT / 'dependencies.json').read_text(encoding='utf-8'))
    for name, expected in dependencies.items():
        assert hashlib.sha256((s.triples.ROOT / name).read_bytes()).hexdigest() == expected
    family = s.shared.read_packet()['families'][114]
    first = s.triples.verify_family(model, family)
    inherited = Counter(); counts = Counter(); systems = {}; oldmaps = {}; rows_by_pivot = {}
    excluded = set()
    for pivot in [10, 0]:
        description, rows, _ = s.construct(model, 115, pivot)
        assert description['pivots'] == [0, 10]
        old = read(s.OUT / f'chart-115-{pivot}.json.gz')
        inherited.update(s.verify(model, old))
        maps = initial_maps(old)
        systems[pivot] = description; oldmaps[pivot] = maps; rows_by_pivot[pivot] = rows
        if pivot == 10:
            packet = read(OUT / 'chart-115-10.json.gz')
            counts.update(verify_rebuilt_chart(rows, description, maps, packet))
        else:
            packet = json.loads((OUT / 'chart-115-0-refined.json').read_text(encoding='utf-8'))
            counts['refined_chart_inferences'] = verify_refinement(rows, description, maps, packet, excluded)
        excluded.add(pivot)
    assert excluded == set(systems[0]['pivots'])
    # Explicitly ensure every coordinate outside the two pivots belongs to
    # the already excluded X0/Y0 pair, which is checked separately in CI.
    assert all(model.dc[index] in s.shared.ANCHOR for i, index in enumerate(systems[0]['basis_indices']) if i not in excluded)

    bad = read(OUT / 'chart-115-10.json.gz')
    bad['maps']['2'] = [[[2], '1']]
    try:
        verify_rebuilt_chart(rows_by_pivot[10], systems[10], oldmaps[10], bad)
    except AssertionError:
        map_control = True
    else:
        raise AssertionError('An unproved map was accepted.')
    refined = json.loads((OUT / 'chart-115-0-refined.json').read_text(encoding='utf-8'))
    try:
        verify_refinement(rows_by_pivot[0], systems[0], oldmaps[0], refined, set())
    except AssertionError:
        dependency_control = True
    else:
        raise AssertionError('A zero from an unproved chart was accepted.')
    bad = read(OUT / 'chart-115-10.json.gz')
    claim = bad['continuation']['power_stages'][0]['claims'][0]
    claim['products'][0][2] = str(s.triples.Q(claim['products'][0][2]) + 1)
    current = [c.substitute(p, oldmaps[10]) for p in rows_by_pivot[10]]
    try:
        s.verify_continuation(current, bad)
    except AssertionError:
        power_control = True
    else:
        raise AssertionError('A corrupt power identity was accepted.')
    partials = [verify_partial(model, number, pivot) for number, pivot in [(16, 13), (137, 8)]]
    report = {'status': 'PASS', 'independent_polynomials': independent,
              'family': 115, 'excluded_pivots_in_proof_order': [10, 0],
              'new_checks': dict(counts), 'prior_syzygy_checks': dict(inherited),
              'first_pass_checks': dict(first),
              'corrupt_map_rejected': map_control,
              'unproved_chart_dependency_rejected': dependency_control,
              'corrupt_power_rejected': power_control,
              'unresolved_chart_progress': partials,
              'seconds': time.perf_counter() - start,
              'scope': 'Family 115 only, with the prior X0/Y0 exclusion as an explicit closure dependency; no HasCertificate proof.'}
    print(json.dumps(report, indent=2), flush=True)
    return report


if __name__ == '__main__':
    if not __debug__:
        raise RuntimeError('Run without -O.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    parser.add_argument('--independent', action='store_true')
    args = parser.parse_args()
    if not args.check:
        parser.error('Use --check; discovery commands are documented in notes/syzygy-rebuild.md.')
    check(args.independent)

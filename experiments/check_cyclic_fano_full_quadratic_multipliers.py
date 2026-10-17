#!/usr/bin/env python3
"""Independent source and character checks for the full quadratic-polar search.

Only frozen independent arithmetic is imported; no producer is executed.
"""
from collections import Counter
from itertools import combinations_with_replacement, product
from pathlib import Path
from fractions import Fraction as Q
import argparse
import copy
import gzip
import hashlib
import json
import check_cyclic_fano_divisible_multipliers as I

C, L, A = I.C, I.L, I.A
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/cyclic-fano-full-quadratic-multipliers'
WEIGHTS_MOD6 = (0, 4, 0, 1, 1, 5)


def character(monomial, weights=WEIGHTS_MOD6):
    return sum(a * b for a, b in zip(monomial, weights)) % 6


def source():
    exact = C.derive()
    system = I.restricted_system(exact, range(75))
    assert len(system['rows']) == 1799 and len(system['columns']) == 6975
    assert sum(k[0] == 'a*a' for k in system['keys']) == 2850
    assert sum(k[0] == 'a*c' for k in system['keys']) == 4125
    return system


def symmetry(system):
    exact = system['exact']
    # Normalize the common scalar by fixing the X0 diagonal factor. Pure sixth
    # powers imply that all four remaining relative factors are sixth roots.
    admissible = []
    for tail in product(range(6), repeat=4):
        weights = (0, tail[0], 0, tail[1], tail[2], tail[3])
        if all(character(m, weights) == 0 for m in exact['Delta']):
            admissible.append(weights)
    expected = sorted(tuple(k * w % 6 for w in WEIGHTS_MOD6) for k in range(6))
    assert sorted(admissible) == expected
    for name in ('Q', 'H', 'Delta'):
        assert all(character(m) == 0 for m in exact[name])
    assert {character(m) for m in exact['beta']} == {3}
    parameters = [(character(m) - WEIGHTS_MOD6[i]) % 6 for i, m in C.PARAMETERS]
    corrections = []
    for label in exact['correction_labels']:
        if label[0] == 'linear_base_pair':
            _, i, j, k = label
            corrections.append((WEIGHTS_MOD6[k] - WEIGHTS_MOD6[i] - WEIGHTS_MOD6[j] - 3) % 6)
        else:
            corrections.append((-WEIGHTS_MOD6[label[1]] - 3) % 6)
    column_characters = []
    for key, column in zip(system['keys'], system['columns']):
        kind, p, r = key
        charge = (parameters[p] + (parameters[r] if kind == 'a*a' else corrections[r])) % 6
        assert all((character(m) - 3) % 6 == charge for m in column)
        column_characters.append(charge)
    quadratic_counts = Counter((parameters[i] + parameters[j]) % 6
                               for i, j in combinations_with_replacement(range(75), 2))
    cubic_counts = Counter(sum(parameters[i] for i in triple) % 6
                           for triple in combinations_with_replacement(range(75), 3))
    cube_targets = Counter(3 * charge % 6 for charge in parameters)
    assert [cubic_counts[k] for k in range(6)] == [12195, 12200, 12164, 12241, 12157, 12193]
    assert cube_targets == Counter({0: 36, 3: 39})
    return dict(base_weights=[WEIGHTS_MOD6[i] for i in C.BASE], modulus=6,
        relative_diagonal_group_order=6, parameter_characters=parameters,
        parameter_counts=[parameters.count(k) for k in range(6)],
        correction_characters=corrections,
        physical_row_counts=[sum((character(m) - 3) % 6 == k for m in system['rows']) for k in range(6)],
        physical_column_counts=[column_characters.count(k) for k in range(6)],
        quadratic_monomial_counts=[quadratic_counts[k] for k in range(6)],
        cubic_monomial_counts=[cubic_counts[k] for k in range(6)],
        coordinate_cube_target_counts=[cube_targets[k] for k in range(6)],
        cube_search_characters=[0, 3])


def modular_ranks(system, prime=1009):
    pure = sum(key[0] == 'a*a' for key in system['keys'])
    mixed_rows = {m: {j: c for j, c in row.items() if j >= pure}
                  for m, row in system['rows'].items()}
    mixed = len(L.row_basis(mixed_rows, prime))
    full = len(L.row_basis(system['rows'], prime))
    return dict(prime=prime, physical_rank=full, correction_rank=mixed,
                necessary_quadric_dimension_mod_prime=full - mixed)


def decode_parameters(terms, dimension=75):
    if not terms or 'powers' in terms[0]:
        return L.decode(terms, dimension)
    result = {}
    for term in terms:
        indices = term['indices']
        assert indices == sorted(indices) and all(i in range(dimension) for i in indices)
        powers = tuple(indices.count(i) for i in range(dimension))
        coefficient = Q(term['coefficient'])
        assert powers not in result
        if coefficient:
            result[powers] = (coefficient, Q(0))
    return result


def equation_and_dual(entry, dimension=75):
    if 'polynomial' in entry:
        return decode_parameters(entry['polynomial'], dimension), L.decode(entry['dual'])
    equation = decode_parameters([dict(indices=[i, j], coefficient=c) for i, j, c in entry['terms']], dimension)
    dual = L.decode([dict(powers=m, coefficient=c) for m, c in entry['dual']])
    return equation, dual


def check_necessary_stage(stage, system, ranks, grading):
    assert stage['active_raw_parameter_indices'] == system['active']
    n = len(system['active'])
    pure, mixed = n * (n + 1) // 2, 55 * n
    assert (stage['rows'], stage['columns'], stage['pure_columns'], stage['mixed_columns']) == (len(system['rows']), len(system['columns']), pure, mixed)
    assert stage['rank'] == ranks['rank']
    assert stage['mixed_rank'] == ranks['mixed_rank']
    assert len(stage['equations']) == ranks['rank'] - ranks['mixed_rank']
    local_characters = [grading['parameter_characters'][i] for i in system['active']]
    equations, charges = [], []
    for entry in stage['equations']:
        equation, dual = equation_and_dual(entry, n)
        assert all(m[2] == 0 and sum(m) == 12 for m in dual)
        assert equation and all(sum(m) == 2 for m in equation)
        assert I.necessary_quadric(dual, system) == equation
        charge = {sum(a * b for a, b in zip(m, local_characters)) % 6 for m in equation}
        assert len(charge) == 1
        assert {(character(m) - 3) % 6 for m in dual} == charge
        if 'charge' in entry:
            assert entry['charge'] in charge
        equations.append(equation); charges.append(charge.pop())
    assert len(L.row_basis({j: {m: c[0] for m, c in q.items()} for j, q in enumerate(equations)})) == len(equations)
    return equations, charges


def verify_cube(identity, equations, dimension=75):
    index = identity['parameter_index']
    assert index in range(dimension) and identity['power'] == 3
    total = {}
    for term in identity['multipliers']:
        q = term['equation_index']; j = term['linear_variable']
        assert q in range(len(equations)) and j in range(dimension)
        m = tuple(int(k == j) for k in range(dimension))
        total = A.add(total, A.mul(equations[q], {m: (Q(term['coefficient']), Q(0))}))
    assert total == {tuple(3 * int(k == index) for k in range(dimension)): A.ONE}


def exact_square_queries(equations, dimension):
    pivots = L.row_basis({j: {m: c[0] for m, c in q.items()}
                         for j, q in enumerate(equations)})
    return [j for j in range(dimension) if not I.reduce_sparse(
        {tuple(2 * int(k == j) for k in range(dimension)): Q(1)}, pivots)]


def verify_small_proof(proof, equations, active):
    n = len(active)
    assert proof['status'] == 'completed' and proof['coefficient_field'] == 'Q'
    assert proof['active_raw_parameter_indices'] == active
    threshold = proof['term_threshold']
    assert isinstance(threshold, int) and threshold > 0
    selected = [i for i, q in enumerate(equations) if len(q) <= threshold]
    assert proof['equation_indices'] == selected
    rows = {}
    for i in selected:
        pairs = [([j for j, e in enumerate(m) for _ in range(e)], c[0])
                 for m, c in equations[i].items()]
        for j in range(n):
            rows[i, j] = {tuple(sorted(pair + [j])): c for pair, c in pairs}
    assert proof['columns'] == len(rows)
    pivots = L.row_basis(rows)
    assert proof['rank'] == len(pivots)
    expected = [j for j in range(n) if not I.reduce_sparse({(j, j, j): Q(1)}, pivots)]
    assert [identity['parameter_index'] for identity in proof['identities']] == expected
    for identity in proof['identities']:
        assert all(t['equation_index'] in selected for t in identity['multipliers'])
        verify_cube(identity, equations, n)
    assert proof['remaining_local_parameters'] == [j for j in range(n) if j not in expected]
    return dict(term_threshold=threshold, selected_quadrics=len(selected),
                multiplier_generators=len(rows), exact_rank=len(pivots),
                forced_local_parameters=expected, forced_raw_parameters=[active[j] for j in expected],
                multiplier_terms=sum(len(e['multipliers']) for e in proof['identities']),
                remaining_local_parameters=proof['remaining_local_parameters'])


def restriction_gain(old_equations, old_active, new_equations, new_active):
    positions = [old_active.index(i) for i in new_active]
    selected = set(positions)
    restricted = [{tuple(m[j] for j in positions): c[0]
        for m, c in equation.items() if all(not e or j in selected for j, e in enumerate(m))}
        for equation in old_equations]
    old_pivots = L.row_basis(dict(enumerate(restricted)))
    fresh_pivots = L.row_basis({j: {m: c[0] for m, c in q.items()}
                              for j, q in enumerate(new_equations)})
    assert all(not I.reduce_sparse(q, fresh_pivots) for q in restricted)
    return dict(restricted_initial_rank=len(old_pivots), fresh_rank=len(fresh_pivots),
                additional_quadrics=len(fresh_pivots) - len(old_pivots), span_inclusion=True)


def verify_small_quartic(proof, equations, active):
    n = len(active)
    assert proof['status'] == 'completed' and proof['degree'] == 4
    assert proof['active_raw_parameter_indices'] == active
    selected = [i for i, q in enumerate(equations) if len(q) <= proof['term_threshold']]
    assert proof['equation_indices'] == selected
    rows = {}
    for i in selected:
        pairs = [([j for j, e in enumerate(m) for _ in range(e)], c[0])
                 for m, c in equations[i].items()]
        for j, k in combinations_with_replacement(range(n), 2):
            rows[i, j, k] = {tuple(sorted(pair + [j, k])): c for pair, c in pairs}
    assert proof['columns'] == len(rows)
    pivots = L.row_basis(rows)
    assert proof['rank'] == len(pivots)
    found = [j for j in range(n) if not I.reduce_sparse({(j,) * 4: Q(1)}, pivots)]
    if 'coordinate_fourth_powers_found' in proof:
        assert proof['coordinate_fourth_powers_found'] == found
    identities = proof.get('identities', [])
    assert [e['parameter_index'] for e in identities] == found
    for identity in identities:
        i = identity['parameter_index']
        assert identity['raw_parameter_index'] == active[i] and identity['power'] == 4
        total = {}
        for t in identity['multipliers']:
            j, k = t['quadratic_variables']; key = (t['equation_index'], j, k)
            assert key in rows
            for m, c in rows[key].items():
                new = total.get(m, Q(0)) + Q(t['coefficient']) * c
                if new:
                    total[m] = new
                else:
                    total.pop(m, None)
        assert total == {(i,) * 4: Q(1)}
    return dict(degree=4, term_threshold=proof['term_threshold'], selected_quadrics=len(selected),
                multiplier_generators=len(rows), exact_rank=len(pivots),
                coordinate_fourth_powers=found,
                limit='Nonmembership is for this selected-quadrics multiplier space only.')


def verify_modular_prefix(attempt, equations, charges, grading):
    """Replay the reported finite prefix, not an unreported completed search."""
    prime, charge = attempt['prime'], attempt['charge']
    assert prime == 1009 and charge in (0, 3)
    order = attempt.get('monomial_order', 'reverse_packed_sorted_triples')
    assert order in ('forward_packed_sorted_triples', 'reverse_packed_sorted_triples')
    sign = 1 if order.startswith('forward') else -1
    weights = grading['parameter_characters']
    generators = {}; all_monomials = set()
    for qindex, equation in enumerate(equations):
        pairs = []
        for m, (real, imag) in equation.items():
            assert not imag
            pair = [j for j, e in enumerate(m) for _ in range(e)]
            assert len(pair) == 2
            value = real.numerator * pow(real.denominator, -1, prime) % prime
            if value:
                pairs.append((pair, value))
        for j in range(75):
            if (charges[qindex] + weights[j]) % 6 != charge:
                continue
            # Signed tuples replay the monomial order independently of the
            # producer's integer bit-packing implementation.
            row = {tuple(sign * k for k in sorted(pair + [j])): value for pair, value in pairs}
            generators[qindex, j] = row
            all_monomials.update(row)
    assert attempt['columns'] == len(generators)
    assert attempt['potential_rows'] == grading['cubic_monomial_counts'][charge]
    assert attempt['active_rows'] == len(all_monomials)
    forest = {m: m for m in all_monomials}
    def find(m):
        while forest[m] != m:
            forest[m] = forest[forest[m]]
            m = forest[m]
        return m
    for row in generators.values():
        if row:
            root = find(next(iter(row)))
            for m in row:
                other = find(m)
                if other != root:
                    forest[other] = root
    components = len({find(m) for m in all_monomials})
    assert components == 1
    n = attempt['processed_generators']
    assert 0 < n <= len(generators)
    selected = dict(sorted(generators.items(), key=lambda item: (len(item[1]), item[0]))[:n])
    pivots = L.row_basis(selected, prime)
    assert attempt['rank_mod_prime'] == len(pivots)
    targets = [j for j, c in enumerate(weights) if 3 * c % 6 == charge]
    assert attempt['coordinate_cube_targets'] == targets
    found = [j for j in targets if not I.reduce_sparse({(sign * j,) * 3: 1}, pivots, prime)]
    assert attempt['coordinate_cubes_found_mod_prime'] == found
    if attempt['status'] == 'completed':
        assert n == len(generators) and attempt['rank_scope'] == 'full_block'
    else:
        assert attempt['status'] == 'sparse_fill_limit'
        assert attempt['rank_scope'] == 'processed_generator_prefix'
        assert attempt['pivot_nonzero_entries'] > 3000000 or attempt['update_operations'] > 100000000
    return dict(charge=charge, prime=prime, monomial_order=order,
                processed_generators=n, columns=len(generators),
                rank_mod_prime=len(pivots), coordinate_cubes_found_mod_prime=found,
                support_graph_components=components, scope=attempt['rank_scope'])


def same(left, right):
    assert left == right


def binary_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_path(name):
    assert name == Path(name).name
    return OUT / name


def load_bound_stage(info):
    path = local_path(info['quadrics_file'])
    assert binary_sha(path) == info['quadrics_sha256']
    raw = gzip.decompress(path.read_bytes())
    assert hashlib.sha256(raw).hexdigest() == info['quadrics_uncompressed_sha256']
    return json.loads(raw)


def check_bindings(packet):
    assert packet['schema'] == 'cyclic-fano-full-quadratic-multipliers-v1'
    assert packet['status'] == 'checked_partial_progress'
    assert (packet['instance'], packet['q'], packet['degree']) == ('cyclic-triple-fano', 1, 7)
    assert packet['source_commit'] == 'd96911d725077e66a8f10848908be01a643b1714'
    assert packet['source_instance_sha256'] == A.I.sha(L.C.SOURCE / 'source/instance.rec')
    assert packet['producer_sha256'] == A.I.sha(ROOT / 'experiments/cyclic_fano_full_quadratic_multipliers.py')
    assert packet['dependencies'] == {name: A.I.sha(ROOT / 'experiments' / name) for name in
        ('cyclic_fano_divisible_multipliers.py', 'cyclic_fano_quadratic_polars.py',
         'cyclic_fano_linear_polars.py', 'cyclic_fano_transfer.py', 'quadric_contact_pilot.py')}
    prior = packet['prior_projection_proof']
    assert prior['packet'] == 'results/cyclic-fano-quadratic-polars/packet.json'
    assert prior['packet_sha256'] == A.I.sha(C.OUT / 'packet.json')
    assert prior['primary_receipt_sha256'] == A.I.sha(C.OUT / 'validation.json')
    assert prior['independent_receipt_sha256'] == A.I.sha(C.OUT / 'independent-validation.json')
    assert (prior['raw_Koszul_fields'], prior['compact_correction_types'], prior['quotient_directions']) == (230, 55, 246)
    assert packet['base_variables'] == ['X0', 'X1', 'Z', 'Y0', 'Y1', 'Y2']
    assert packet['parameter_order'] == [dict(component=i, quadratic_powers=list(m),
        charge=(character(m) - WEIGHTS_MOD6[i]) % 6) for i, m in C.PARAMETERS]
    grading = packet['symmetry']
    assert (grading['modulus'], grading['spatial_weights'], grading['beta_and_A_charge'],
            grading['physical_row_to_quadric_charge_shift'], grading['target_cube_charges']) == (6, list(WEIGHTS_MOD6), 3, -3, [0, 3])
    assert len(packet['stages']) == 3


def main():
    assert __debug__, 'Run without -O'
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUT / 'independent-validation.json')
    args = parser.parse_args()
    packet_path = OUT / 'packet.json'; packet = A.I.load(packet_path)
    check_bindings(packet)
    full = source(); grading = symmetry(full)
    prepared, summaries, gains = [], [], []
    remaining = list(range(75)); forced_all = []; selected_proofs = {}
    print('Independent full source and character decomposition: PASS', flush=True)
    for index, info in enumerate(packet['stages']):
        assert info['index'] == index
        stage = load_bound_stage(info)
        assert stage['active_raw_parameter_indices'] == remaining
        system = I.restricted_system(full['exact'], remaining)
        ranks = I.prepare_ranks(system)
        equations, charges = check_necessary_stage(stage, system, ranks, grading)
        assert info['parameters'] == len(remaining)
        assert (info['physical_rows'], info['physical_columns'], info['rank'],
                info['mixed_rank'], info['necessary_quadrics']) == (
                    len(system['rows']), len(system['columns']), ranks['rank'], ranks['mixed_rank'], len(equations))
        squares = exact_square_queries(equations, len(remaining))
        assert not squares
        proof_path = local_path(info['cube_proof_file'])
        assert binary_sha(proof_path) == info['cube_proof_sha256']
        proof = A.I.load(proof_path)
        small = verify_small_proof(proof, equations, remaining)
        selected_proofs[proof_path.name] = small
        assert info['newly_forced_raw_parameters'] == small['forced_raw_parameters']
        if index:
            old = prepared[-1]
            gain = restriction_gain(old['equations'], old['system']['active'], equations, remaining)
            gains.append(dict(stage=index, **gain))
        prepared.append(dict(stage=stage, system=system, equations=equations, charges=charges, proof=proof))
        summaries.append(dict(index=index, parameters=len(remaining), physical_rows=len(system['rows']),
            physical_columns=len(system['columns']), **ranks, exact_square_queries=len(remaining),
            isolated_squares=squares, selected_cubic_space=small,
            quadrics_binary_sha256=info['quadrics_sha256'],
            physical_coefficient_sha256=I.coefficient_digest(system['keys'], system['columns']),
            physical_dual_terms=sum(len(e['dual']) for e in stage['equations'])))
        forced_all.extend(small['forced_raw_parameters'])
        remaining = [remaining[j] for j in small['remaining_local_parameters']]
        print('Independent stage', index, 'PASS:', len(equations), 'quadrics;', len(remaining), 'remaining parameters', flush=True)
    assert [s['parameters'] for s in summaries] == [75, 67, 66]
    assert forced_all == [8, 13, 26, 28, 38, 53, 56, 61, 66]
    assert packet['remaining_raw_parameter_indices'] == remaining
    expected_gains = [dict(stage=g['stage'], restricted_old_rank=g['restricted_initial_rank'],
        rebuilt_rank=g['fresh_rank'], added_independent_quadrics=g['additional_quadrics'],
        span_inclusion=g['span_inclusion']) for g in gains]
    assert packet['rebuild_diagnostics'] == expected_gains and len(gains) == 2
    attempt_summaries = []
    seen_files = set()
    for binding in packet['attempts']:
        name = binding['file']; assert name not in seen_files; seen_files.add(name)
        path = local_path(name)
        assert binary_sha(path) == binding['sha256']
        attempt = A.I.load(path); assert attempt['status'] == binding['status']
        if name.startswith('charge'):
            result = verify_modular_prefix(attempt, prepared[0]['equations'], prepared[0]['charges'], grading)
        elif 'quartic' in name and attempt['status'] == 'completed':
            stage_index = attempt['stage']; data = prepared[stage_index]
            result = verify_small_quartic(attempt, data['equations'], data['system']['active'])
        elif '-small-' in name and attempt['status'] == 'completed':
            stage_index = int(name.split('-')[1]); data = prepared[stage_index]
            result = selected_proofs.get(name)
            if result is None:
                result = verify_small_proof(attempt, data['equations'], data['system']['active'])
        elif attempt['status'] == 'interrupted':
            assert name == 'replay-unsorted-attempt.json'
            assert attempt['operation'] == 'initial primary replay development'
            assert attempt['scope'] == 'Implementation performance failure; no mathematical result inferred.'
            result = dict(status='recorded_interruption', scope=attempt['scope'])
        else:
            assert attempt['status'] == 'timeout'
            assert attempt['bound_seconds'] > 0
            result = dict(status='recorded_timeout', scope='No new exact rank or nonmembership inferred.')
        attempt_summaries.append(dict(file=name, sha256=binding['sha256'], **result))
        print('Independent attempt replay PASS:', name, flush=True)
    required_attempts = set()
    for pattern in ('charge*-probe.json', 'stage-??-small-*.json', '*quartic*.json', '*-timeout.json', '*-attempt.json'):
        required_attempts.update(path.name for path in OUT.glob(pattern))
    assert seen_files == required_attempts
    controls = []
    for field in ('source_instance_sha256', 'producer_sha256', 'status'):
        bad = copy.deepcopy(packet); bad[field] = None
        controls.append(lambda p=bad: check_bindings(p))
    bad = copy.deepcopy(packet); bad['prior_projection_proof']['compact_correction_types'] = 50
    controls.append(lambda p=bad: check_bindings(p))
    bad = copy.deepcopy(packet); bad['symmetry']['beta_and_A_charge'] = 0
    controls.append(lambda p=bad: check_bindings(p))
    bad = copy.deepcopy(packet['stages'][0]); bad['quadrics_sha256'] = '0' * 64
    controls.append(lambda p=bad: load_bound_stage(p))
    for item in prepared:
        entry = copy.deepcopy(item['stage']['equations'][0])
        entry['dual'][0][1] = str(Q(entry['dual'][0][1]) + 1)
        equation, dual = equation_and_dual(entry, len(item['system']['active']))
        controls.append(lambda d=dual, e=equation, s=item['system']: same(I.necessary_quadric(d, s), e))
        if item['proof']['identities']:
            bad = copy.deepcopy(item['proof']['identities'][0])
            bad['multipliers'][0]['coefficient'] = str(Q(bad['multipliers'][0]['coefficient']) + 1)
            controls.append(lambda p=bad, e=item['equations'], n=len(item['system']['active']): verify_cube(p, e, n))
    controls.append(lambda: same(packet['remaining_raw_parameter_indices'][:-1], remaining))
    bad_gain = copy.deepcopy(packet['rebuild_diagnostics']); bad_gain[0]['added_independent_quadrics'] += 1
    controls.append(lambda: same(bad_gain, expected_gains))
    rejected = sum(A.I.rejects(fn) for fn in controls)
    assert rejected == len(controls) == 13
    primary_path = OUT / 'validation.json'; primary = A.I.load(primary_path)
    assert primary['status'] == 'PASS' and primary['packet_sha256'] == A.I.sha(packet_path)
    assert primary['producer_sha256'] == packet['producer_sha256']
    receipt = dict(schema='cyclic-fano-full-quadratic-multipliers-independent-v1', status='PASS',
        checker_lf_sha256=A.I.sha(Path(__file__)), packet_lf_sha256=A.I.sha(packet_path),
        primary_validation_lf_sha256=A.I.sha(primary_path),
        source_instance_lf_sha256=A.I.sha(L.C.SOURCE / 'source/instance.rec'),
        independent_arithmetic_dependencies={Path(p).name: A.I.sha(Path(p)) for p in
            (I.__file__, C.__file__, L.__file__, L.C.__file__, A.__file__, A.I.__file__)},
        source_E1_and_Piola_lifts_replayed=75, full_raw_Koszul_fields=230,
        raw_projection_identities_replayed=17250, retained_correction_types=55,
        quotient_directions_replayed=246, Euler_normalization_identities_replayed=full['exact']['euler_checks'],
        symmetry=grading, stages=summaries, rebuild_diagnostics=gains,
        necessary_quadric_identities=sum(len(item['equations']) for item in prepared),
        physical_coefficient_pairings=sum(len(item['equations']) * len(item['system']['columns']) for item in prepared),
        exact_failed_square_queries=sum(len(item['system']['active']) for item in prepared),
        coordinate_cube_identities=len(forced_all), forced_raw_parameter_indices=forced_all,
        cube_multiplier_terms=sum(s['selected_cubic_space']['multiplier_terms'] for s in summaries),
        remaining_raw_parameter_indices=remaining, attempt_checks=attempt_summaries,
        negative_controls_rejected=rejected)
    receipt['conclusion'] = ('Nine exact coordinate-cube identities reduce the full75-parameter quadratic '
        'direction family to66 parameters, with complete numerator correction and quotient spaces retained. '
        'The first rebuild adds five necessary quadrics beyond restriction; the second adds none.')
    receipt['limits'] = ('The66-parameter family remains unresolved. Selected sparse cubic and quartic '
        'nonmembership checks concern only their stated generator subsets. Modular block ranks describe '
        'processed prefixes, not completed blocks. No full-family exclusion, geometric support, Lean '
        'HasCertificate proof or solution is claimed. Runtime figures are producer observations rather '
        'than mathematical evidence.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(status='PASS', exact_cube_identities=len(forced_all), remaining_parameters=len(remaining),
        necessary_quadric_identities=receipt['necessary_quadric_identities'], negative_controls=rejected,
        receipt_sha256=A.I.sha(args.output))))


if __name__ == '__main__':
    main()

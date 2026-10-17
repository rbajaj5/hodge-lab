#!/usr/bin/env python3
"""Independent exact audit of the remaining-66 polar multiplier continuation.

Imports only prior independent arithmetic, never the new producer.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations_with_replacement
import argparse
import copy
import gzip
import hashlib
import json
import check_cyclic_fano_full_quadratic_multipliers as F

I, C, L, A = F.I, F.C, F.L, F.A
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/cyclic-fano-remaining66-multipliers'
PRIOR = F.OUT


def binary_sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_gzip(path):
    return json.loads(gzip.decompress(path.read_bytes()))


def pair_equations(stage):
    n = len(stage['active_raw_parameter_indices'])
    equations = []
    for entry in stage['equations']:
        row = {}
        for i, j, coefficient in entry['terms']:
            assert 0 <= i <= j < n and (i, j) not in row
            value = Q(coefficient)
            assert value
            row[i, j] = value
        assert row
        equations.append(row)
    return equations


def parameter_equations(stage):
    n = len(stage['active_raw_parameter_indices'])
    return [F.decode_parameters([dict(indices=[i, j], coefficient=c)
                                 for i, j, c in entry['terms']], n)
            for entry in stage['equations']]


def combination(equations, coefficients):
    result = {}
    assert len({i for i, c in coefficients}) == len(coefficients)
    for i, coefficient in coefficients:
        assert i in range(len(equations))
        coefficient = Q(coefficient)
        assert coefficient
        for m, value in equations[i].items():
            total = result.get(m, Q(0)) + coefficient * value
            if total:
                result[m] = total
            else:
                result.pop(m, None)
    return result


def audit_reduced_basis(original, reduced):
    active = original['active_raw_parameter_indices']
    assert reduced['active_raw_parameter_indices'] == active
    old_rows, new_rows = pair_equations(original), pair_equations(reduced)
    assert reduced['rank'] == len(old_rows) == len(new_rows)
    assert reduced['original_term_count'] == sum(map(len, old_rows))
    assert reduced['reduced_term_count'] == sum(map(len, new_rows))
    transformation_terms = 0
    charges = [(F.character(m) - F.WEIGHTS_MOD6[i]) % 6 for i, m in C.PARAMETERS]
    for entry, row in zip(reduced['equations'], new_rows):
        assert combination(old_rows, entry['combination']) == row
        transformation_terms += len(entry['combination'])
        assert {(charges[active[i]] + charges[active[j]]) % 6 for i, j in row} == {entry['charge']}
    pivots = [min(row) for row in new_rows]
    assert pivots == sorted(pivots) and len(set(pivots)) == len(pivots)
    pivot_set = set(pivots)
    for pivot, row in zip(pivots, new_rows):
        assert row[pivot] == 1 and set(row).intersection(pivot_set) == {pivot}
    # Distinct normalized pivot columns certify independence without sharing
    # the producer's elimination algorithm.
    return dict(rank=len(pivots), exact_linear_combinations=len(new_rows),
                transformation_terms=transformation_terms,
                original_term_count=sum(map(len, old_rows)),
                reduced_term_count=sum(map(len, new_rows)),
                same_quadric_span=True, reduced_row_echelon_form=True)


def audit_short_combinations(stage):
    rows = pair_equations(stage)
    active = stage['active_raw_parameter_indices']
    examples = [
        dict(raw_parameter_pair=[46, 59], combination=[[379, '1'], [391, '-7182/5'], [386, '171/28']]),
        dict(raw_parameter_pair=[46, 50], combination=[[377, '1'], [383, '-102218/875'], [387, '-24024/25']]),
    ]
    for example in examples:
        pair = tuple(sorted(active.index(i) for i in example['raw_parameter_pair']))
        assert combination(rows, example['combination']) == {pair: Q(1)}
    return examples


def audit_short_target_queries(reduced):
    """A failed attempt to shorten the successful 131-term cube witness."""
    equations = pair_equations(reduced)
    active = reduced['active_raw_parameter_indices']
    i, j = active.index(46), active.index(65)
    target = {tuple(sorted((i, i, j))): Q(1)}
    bridge = [[351, 46, '1'], [377, 23, '-1'], [377, 41, '-1/4'],
              [377, 45, '5/9'], [377, 58, '-1/4'], [377, 74, '3/2'],
              [379, 65, '3/2']]
    total = {}
    for equation, raw_variable, coefficient in bridge:
        variable = active.index(raw_variable)
        for pair, c in equations[equation].items():
            m = tuple(sorted((*pair, variable)))
            total[m] = total.get(m, Q(0)) + Q(coefficient) * c
    total = {m: c for m, c in total.items() if c}
    assert total == {(i, i, i): -Q(5, 18), tuple(sorted((i, i, j))): Q(14, 9)}
    attempts = []
    for threshold in (4, 8, 16, 32):
        rows = {(e, k): {tuple(sorted((u, v, k))): c for (u, v), c in q.items()}
                for e, q in enumerate(equations) if len(q) <= threshold
                for k in range(len(active))}
        pivots = L.row_basis(rows)
        found = not I.reduce_sparse(target, pivots)
        assert not found
        attempts.append(dict(term_threshold=threshold, multiplier_generators=len(rows),
                             exact_rank=len(pivots), target_in_selected_span=found))
    return dict(target_raw_parameter_indices=[46, 46, 65], attempts=attempts,
                bridge_multipliers_equation_raw_variable_coefficient=bridge,
                bridge_result='-5/18*a46^3 + 14/9*a46^2*a65',
                scope='Exact nonmembership only in each selected-quadrics cubic multiplier space; '
                      'the full cubic ideal has the target as a consequence of the checked cube.')


def audit_prior_binding():
    packet = A.I.load(PRIOR / 'packet.json')
    receipt = A.I.load(PRIOR / 'independent-validation.json')
    assert receipt['status'] == 'PASS'
    assert receipt['packet_lf_sha256'] == A.I.sha(PRIOR / 'packet.json')
    assert receipt['checker_lf_sha256'] == A.I.sha(Path(F.__file__))
    F.check_bindings(packet)
    original = F.load_bound_stage(packet['stages'][2])
    assert len(original['active_raw_parameter_indices']) == 66
    assert len(original['equations']) == 393
    assert original['active_raw_parameter_indices'] == receipt['remaining_raw_parameter_indices']
    # Recheck the nine short positive identities in the bound prior packets,
    # without repeating their old modular or unsuccessful discovery runs.
    forced = []
    for info in packet['stages']:
        stage = F.load_bound_stage(info)
        path = PRIOR / info['cube_proof_file']
        assert binary_sha(path) == info['cube_proof_sha256']
        proof = A.I.load(path)
        equations = parameter_equations(stage)
        active = stage['active_raw_parameter_indices']
        assert proof['active_raw_parameter_indices'] == active
        for identity in proof['identities']:
            F.verify_cube(identity, equations, len(active))
            forced.append(active[identity['parameter_index']])
    assert forced == [8, 13, 26, 28, 38, 53, 56, 61, 66]
    return packet, receipt, original


def audit_physical_stage(stage, full, grading):
    system = I.restricted_system(full['exact'], stage['active_raw_parameter_indices'])
    ranks = I.prepare_ranks(system)
    equations, charges = F.check_necessary_stage(stage, system, ranks, grading)
    isolated_squares = F.exact_square_queries(equations, len(system['active']))
    assert ranks['necessary_quadrics'] == len(equations)
    summary = dict(parameters=len(system['active']), physical_rows=len(system['rows']),
                   physical_columns=len(system['columns']), **ranks,
                   isolated_squares=isolated_squares,
                   exact_square_queries=len(system['active']),
                   physical_dual_terms=sum(len(e['dual']) for e in stage['equations']),
                   physical_coefficient_sha256=I.coefficient_digest(system['keys'], system['columns']))
    return dict(system=system, equations=equations, charges=charges, summary=summary)


def audit_quartic(proof, reduced):
    equations = pair_equations(reduced)
    active = reduced['active_raw_parameter_indices']
    assert proof['status'] == 'completed' and proof['degree'] == 4
    assert proof['coefficient_field'] == 'Q'
    assert proof['active_raw_parameter_indices'] == active
    selected = [i for i, q in enumerate(equations) if len(q) <= proof['term_threshold']]
    assert proof['equation_indices'] == selected
    rows = {(e, i, j): {tuple(sorted((*m, i, j))): c for m, c in equations[e].items()}
            for e in selected for i, j in combinations_with_replacement(range(len(active)), 2)}
    assert len(rows) == proof['columns']
    pivots = L.row_basis(rows)
    assert len(pivots) == proof['rank']
    found = [i for i in range(len(active)) if not I.reduce_sparse({(i,) * 4: Q(1)}, pivots)]
    if 'coordinate_fourth_powers_found' in proof:
        assert proof['coordinate_fourth_powers_found'] == found
    identities = proof.get('identities', [])
    if 'identities' in proof:
        assert [identity['parameter_index'] for identity in identities] == found
    for identity in identities:
        index = identity['parameter_index']
        assert identity['power'] == 4
        if 'raw_parameter_index' in identity:
            assert identity['raw_parameter_index'] == active[index]
        total = {}
        for term in identity['multipliers']:
            i, j = term['quadratic_variables']
            key = (term['equation_index'], i, j)
            assert key in rows
            for m, c in rows[key].items():
                value = total.get(m, Q(0)) + Q(term['coefficient']) * c
                if value:
                    total[m] = value
                else:
                    total.pop(m, None)
        assert total == {(index,) * 4: Q(1)}
    if 'remaining_local_parameters' in proof:
        assert proof['remaining_local_parameters'] == [i for i in range(len(active)) if i not in found]
    return dict(degree=4, term_threshold=proof['term_threshold'], selected_quadrics=len(selected),
                multiplier_generators=len(rows), exact_rank=len(pivots),
                coordinate_fourth_powers=found, forced_raw_parameters=[active[i] for i in found],
                explicit_power_identities=len(identities),
                multiplier_terms=sum(len(i['multipliers']) for i in identities),
                limit='Nonmembership is for this selected-quadrics multiplier space only.')


def audit_rebuild(previous, current):
    return F.restriction_gain(previous['equations'], previous['system']['active'],
                              current['equations'], current['system']['active'])


def verify_fourth_identity(identity, equations, active):
    index = identity['parameter_index']
    assert index in range(len(active)) and identity['power'] == 4
    if 'raw_parameter_index' in identity:
        assert identity['raw_parameter_index'] == active[index]
    total = {}
    for term in identity['multipliers']:
        equation = term['equation_index']
        i, j = term['quadratic_variables']
        assert equation in range(len(equations)) and 0 <= i <= j < len(active)
        for pair, coefficient in equations[equation].items():
            m = tuple(sorted((*pair, i, j)))
            value = total.get(m, Q(0)) + Q(term['coefficient']) * coefficient
            if value:
                total[m] = value
            else:
                total.pop(m, None)
    assert total == {(index,) * 4: Q(1)}


def audit_power_union(proof, reduced):
    active = reduced['active_raw_parameter_indices']
    assert proof['status'] == 'completed' and proof['basis'] == 'reduced'
    assert proof['active_raw_parameter_indices'] == active
    equations, pairs = parameter_equations(reduced), pair_equations(reduced)
    indices = [identity['parameter_index'] for identity in proof['identities']]
    assert len(set(indices)) == len(indices) and indices == sorted(indices)
    sources = []
    for identity in proof['identities']:
        if identity['power'] == 3:
            F.verify_cube(identity, equations, len(active))
        else:
            verify_fourth_identity(identity, pairs, active)
        if 'source_attempt' in identity:
            name = identity['source_attempt']
            assert name == Path(name).name
            source_proof = A.I.load(OUT / name)
            matching = [v for v in source_proof['identities']
                        if v['parameter_index'] == identity['parameter_index']]
            assert len(matching) == 1
            assert {k: v for k, v in identity.items() if k != 'source_attempt'} == matching[0]
            sources.append(name)
    assert proof['remaining_local_parameters'] == [i for i in range(len(active)) if i not in indices]
    return dict(degree='mixed', explicit_power_identities=len(indices),
                degree3_identities=sum(v['power'] == 3 for v in proof['identities']),
                degree4_identities=sum(v['power'] == 4 for v in proof['identities']),
                forced_raw_parameters=[active[i] for i in indices],
                multiplier_terms=sum(len(v['multipliers']) for v in proof['identities']),
                source_attempts=sorted(set(sources)))


def bound_path(name, expected_hash):
    assert name == Path(name).name
    path = OUT / name
    assert binary_sha(path) == expected_hash
    return path


def audit_chain(packet, original):
    full = F.source()
    grading = F.symmetry(full)
    print('Independent physical source, projections, and grading: PASS', flush=True)
    active = original['active_raw_parameter_indices']
    stages, gains, forced, proof_checks = [], [], [], {}
    for index, info in enumerate(packet['stages']):
        assert info['index'] == index
        if info['physical_file'] is None:
            assert index == 0
            stage = original
            assert info['physical_sha256'] == binary_sha(PRIOR / 'stage-02-quadrics.json.gz')
        else:
            stage = load_gzip(bound_path(info['physical_file'], info['physical_sha256']))
        assert stage['active_raw_parameter_indices'] == active
        physical = audit_physical_stage(stage, full, grading)
        summary = physical['summary']
        for name in ('parameters', 'physical_rows', 'physical_columns', 'rank', 'mixed_rank', 'necessary_quadrics'):
            assert info[name] == summary[name]
        reduced_path = bound_path(info['reduced_file'], info['reduced_sha256'])
        reduced = load_gzip(reduced_path)
        basis_check = audit_reduced_basis(stage, reduced)
        equations = parameter_equations(reduced)
        if index:
            gain = audit_rebuild(stages[-1]['physical'], physical)
            gains.append(dict(stage=index, **gain))
        if info['power_proof_file'] is None:
            assert index == len(packet['stages']) - 1
            power_check = None
            newly_forced = []
        else:
            proof_path = OUT / info['power_proof_file']
            if 'power_proof_sha256' in info:
                assert binary_sha(proof_path) == info['power_proof_sha256']
            proof = A.I.load(proof_path)
            assert proof.get('stage', 0) == index and proof['basis'] == 'reduced'
            if 'columns' not in proof:
                power_check = audit_power_union(proof, reduced)
                degrees = sorted({identity['power'] for identity in proof['identities']})
                expected_degree = degrees[0] if len(degrees) == 1 else 'mixed' if degrees else None
                assert info['power_degree'] == expected_degree
            elif info['power_degree'] == 3:
                power_check = F.verify_small_proof(proof, equations, active)
                power_check['degree'] = 3
                power_check['explicit_power_identities'] = len(proof['identities'])
            elif info['power_degree'] == 4:
                power_check = audit_quartic(proof, reduced)
                assert power_check['explicit_power_identities'] == len(power_check['forced_raw_parameters'])
            else:
                assert info['power_degree'] in (0, 'mixed', None)
                power_check = audit_power_union(proof, reduced)
            newly_forced = power_check['forced_raw_parameters']
            assert newly_forced or index == len(packet['stages']) - 1
            proof_checks[proof_path.name] = power_check
        assert newly_forced == info['newly_forced_raw_parameters']
        stages.append(dict(info=info, stage=stage, reduced=reduced, equations=equations,
                           physical=physical, basis_check=basis_check, power_check=power_check))
        forced.extend(newly_forced)
        active = [i for i in active if i not in newly_forced]
        print('Independent stage', index, 'PASS:', summary['parameters'],
              'parameters;', len(newly_forced), 'new proved zeros', flush=True)
    assert packet['remaining_raw_parameter_indices'] == active
    expected_gains = [dict(stage=g['stage'], restricted_old_rank=g['restricted_initial_rank'],
                           rebuilt_rank=g['fresh_rank'], added_independent_quadrics=g['additional_quadrics'],
                           span_inclusion=g['span_inclusion']) for g in gains]
    assert packet['rebuild_diagnostics'] == expected_gains
    return dict(full=full, grading=grading, stages=stages, rebuild_diagnostics=gains,
                forced_raw_parameters=forced, remaining_raw_parameters=active,
                proof_checks=proof_checks)


def audit_attempts(packet, chain):
    results, seen = [], set()
    for binding in packet['attempts']:
        name = binding['file']
        assert name not in seen
        seen.add(name)
        path = bound_path(name, binding['sha256'])
        attempt = A.I.load(path)
        assert attempt['status'] == binding['status']
        if attempt['status'] == 'timeout':
            assert attempt.get('bound_seconds', attempt.get('timeout_seconds', 0)) > 0
            result = dict(status='recorded_timeout', scope='No rank, new zero, or nonmembership inferred.')
        elif attempt['status'] == 'completed':
            index = attempt.get('stage', 0)
            assert index in range(len(chain['stages']))
            item = chain['stages'][index]
            basis_name = attempt['basis']
            assert basis_name in ('original', 'reduced')
            basis = item[basis_name if basis_name == 'reduced' else 'stage']
            result = chain['proof_checks'].get(name)
            if result is None:
                if attempt.get('degree', 3) == 4:
                    result = audit_quartic(attempt, basis)
                else:
                    result = F.verify_small_proof(attempt, parameter_equations(basis), basis['active_raw_parameter_indices'])
                    result['degree'] = 3
            assert attempt['bound_seconds'] > 0
        else:
            raise AssertionError('Unsupported attempt status: ' + str(attempt['status']))
        results.append(dict(file=name, sha256=binding['sha256'], **result))
        print('Independent attempt PASS:', name, flush=True)
    required = set()
    for pattern in ('cubic-*.json', 'quartic-*.json', 'stage-??-cubic-*.json', 'stage-??-quartic-*.json', 'cas-*.json'):
        required.update(p.name for p in OUT.glob(pattern))
    assert seen == required
    return results


def mathematical_mutation_controls(chain):
    controls = []
    for item in chain['stages']:
        bad = copy.deepcopy(item['reduced'])
        bad['equations'][0]['combination'][0][1] = str(Q(bad['equations'][0]['combination'][0][1]) + 1)
        controls.append(lambda b=bad, s=item['stage']: audit_reduced_basis(s, b))
        entry = copy.deepcopy(item['stage']['equations'][0])
        entry['dual'][0][1] = str(Q(entry['dual'][0][1]) + 1)
        equation, dual = F.equation_and_dual(entry, len(item['physical']['system']['active']))
        controls.append(lambda d=dual, e=equation, s=item['physical']['system']:
                        F.same(I.necessary_quadric(d, s), e))
        proof_file = item['info']['power_proof_file']
        if proof_file is not None and A.I.load(OUT / proof_file)['identities']:
            bad = copy.deepcopy(A.I.load(OUT / proof_file)['identities'][0])
            bad['multipliers'][0]['coefficient'] = str(Q(bad['multipliers'][0]['coefficient']) + 1)
            if bad['power'] == 3:
                controls.append(lambda b=bad, e=item['equations'], n=len(item['physical']['system']['active']):
                                F.verify_cube(b, e, n))
            else:
                controls.append(lambda b=bad, e=pair_equations(item['reduced']), a=item['physical']['system']['active']:
                                verify_fourth_identity(b, e, a))
    expected = chain['remaining_raw_parameters']
    controls.append(lambda: F.same(expected[:-1] if expected else [999], expected))
    if chain['rebuild_diagnostics']:
        bad = copy.deepcopy(chain['rebuild_diagnostics'])
        bad[0]['additional_quadrics'] += 1
        controls.append(lambda b=bad: F.same(b, chain['rebuild_diagnostics']))
    assert all(A.I.rejects(fn) for fn in controls)
    return len(controls)


def audit_divisible_closure(chain, binding):
    """Optional exact closure by embedding into the previously excluded25 family."""
    path = ROOT / 'results/cyclic-fano-divisible-multipliers/packet.json'
    directory = path.parent
    assert binding['packet'] == 'results/cyclic-fano-divisible-multipliers/packet.json'
    assert binding['packet_sha256'] == A.I.sha(path)
    assert binding['primary_receipt_sha256'] == A.I.sha(directory / 'validation.json')
    assert binding['independent_receipt_sha256'] == A.I.sha(directory / 'independent-validation.json')
    old = A.I.load(path)
    active = [p for p, (i, m) in enumerate(C.PARAMETERS) if m[i]]
    assert len(active) == 25 and set(chain['remaining_raw_parameters']).issubset(active)
    embedding = [dict(raw_parameter_index=p, old_local_parameter_index=active.index(p))
                 for p in chain['remaining_raw_parameters']]
    assert binding['embedding'] == embedding
    # Reconstruct both old physical systems and all their positive witnesses
    # using the current independently derived source, rather than importing
    # either producer or taking the old success receipt as a proof.
    system = I.restricted_system(chain['full']['exact'], active)
    prepared = I.prepare(old, system)
    checked = I.validate(old, system, prepared)
    assert not old['final_cubic_stage']['remaining_parameter_indices']
    return dict(status='PASS', embedding=embedding,
                packet_lf_sha256=A.I.sha(path),
                independent_receipt_lf_sha256=A.I.sha(directory / 'independent-validation.json'),
                necessary_quadric_identities=167, coordinate_cube_identities=25,
                full_correction_types=55, quotient_directions=246, **checked,
                conclusion='The surviving subfamily embeds in the exactly excluded 25-parameter family.')


def make_receipt(packet, chain, attempts, controls, output):
    primary_path = OUT / 'validation.json'
    primary = A.I.load(primary_path)
    assert primary['status'] == 'PASS'
    assert primary['packet_sha256'] == A.I.sha(OUT / 'packet.json')
    assert primary['producer_sha256'] == packet['producer_sha256']
    summaries = []
    for item in chain['stages']:
        info = item['info']
        summaries.append(dict(index=info['index'], **item['physical']['summary'],
            reduced_basis=item['basis_check'], selected_powers=item['power_check'],
            physical_packet_binary_sha256=info['physical_sha256'],
            reduced_basis_binary_sha256=info['reduced_sha256']))
    initial = chain['stages'][0]
    short = audit_short_combinations(initial['stage'])
    simplification = audit_short_target_queries(initial['reduced'])
    receipt = dict(schema='cyclic-fano-remaining66-multipliers-independent-v1', status='PASS',
        checker_lf_sha256=A.I.sha(Path(__file__)), packet_lf_sha256=A.I.sha(OUT / 'packet.json'),
        primary_validation_lf_sha256=A.I.sha(primary_path),
        source_instance_lf_sha256=A.I.sha(L.C.SOURCE / 'source/instance.rec'),
        prior_packet_lf_sha256=A.I.sha(PRIOR / 'packet.json'),
        prior_independent_validation_lf_sha256=A.I.sha(PRIOR / 'independent-validation.json'),
        prior_coordinate_cube_identities_replayed=9,
        independent_arithmetic_dependencies={Path(p).name: A.I.sha(Path(p)) for p in
            (F.__file__, I.__file__, C.__file__, L.__file__, L.C.__file__, A.__file__, A.I.__file__)},
        source_E1_and_Piola_lifts_replayed=75, full_raw_Koszul_fields=230,
        raw_projection_identities_replayed=17250, retained_correction_types=55,
        quotient_directions_replayed=246,
        Euler_normalization_identities_replayed=chain['full']['exact']['euler_checks'],
        stages=summaries, rebuild_diagnostics=chain['rebuild_diagnostics'],
        necessary_quadric_identities=sum(len(item['physical']['equations']) for item in chain['stages']),
        basis_transformation_identities=sum(item['basis_check']['exact_linear_combinations'] for item in chain['stages']),
        exact_square_queries=sum(len(item['physical']['system']['active']) for item in chain['stages']),
        new_power_identities=len(chain['forced_raw_parameters']),
        multiplier_terms=sum(item['power_check']['multiplier_terms'] for item in chain['stages'] if item['power_check']),
        newly_forced_raw_parameter_indices=chain['forced_raw_parameters'],
        remaining_raw_parameter_indices=chain['remaining_raw_parameters'],
        exact_short_combinations=short, failed_simplification=simplification,
        attempt_checks=attempts, negative_controls_rejected=controls)
    receipt['coordinate_divisible_closure'] = chain['coordinate_divisible_closure']
    receipt['conclusion'] = (str(len(chain['forced_raw_parameters'])) + ' further coefficient powers vanish in the '
        'remaining 66-parameter family. The ' + str(len(chain['remaining_raw_parameters'])) +
        ' surviving parameters embed in the independently replayed, excluded 25-parameter subfamily. '
        'Together with the inherited nine vanishings this excludes the full 75-parameter '
        'quadratic-direction polar family, with all correction spaces retained.')
    receipt['limits'] = ('The prior75-to66 proof is an explicitly bound dependency. This run reconstructs the '
        'new physical stages and does not rerun old failed searches. Power identities give set-theoretic '
        'vanishing over characteristic zero; failure to isolate other powers concerns only the stated '
        'selected multiplier spaces. No general denominator exclusion, geometric support, Lean '
        'HasCertificate proof, or accepted solution is claimed.')
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(status='PASS', new_power_identities=receipt['new_power_identities'],
        remaining_before_subfamily_closure=len(chain['remaining_raw_parameters']),
        full_quadratic_direction_family_excluded=True, negative_controls=controls,
        receipt_sha256=A.I.sha(output))), flush=True)


def check_bindings(packet):
    assert packet['schema'] == 'cyclic-fano-remaining66-multipliers-v1'
    assert packet['status'] == 'full_quadratic_direction_family_excluded'
    assert 'coordinate_divisible_closure' in packet
    assert (packet['instance'], packet['q'], packet['degree']) == ('cyclic-triple-fano', 1, 7)
    assert packet['source_commit'] == 'd96911d725077e66a8f10848908be01a643b1714'
    assert packet['source_instance_sha256'] == A.I.sha(L.C.SOURCE / 'source/instance.rec')
    assert packet['producer_sha256'] == A.I.sha(ROOT / 'experiments/cyclic_fano_remaining66_multipliers.py')
    names = ('cyclic_fano_full_quadratic_multipliers.py', 'cyclic_fano_divisible_multipliers.py',
             'cyclic_fano_quadratic_polars.py', 'cyclic_fano_linear_polars.py',
             'cyclic_fano_transfer.py', 'quadric_contact_pilot.py')
    assert packet['dependencies'] == {name: A.I.sha(ROOT / 'experiments' / name) for name in names}
    prior = packet['prior_proof']
    assert prior['packet'] == 'results/cyclic-fano-full-quadratic-multipliers/packet.json'
    assert prior['packet_sha256'] == A.I.sha(PRIOR / 'packet.json')
    assert prior['independent_receipt_sha256'] == A.I.sha(PRIOR / 'independent-validation.json')
    assert prior['primary_receipt_sha256'] == A.I.sha(PRIOR / 'validation.json')
    assert prior['physical_file'] == 'results/cyclic-fano-full-quadratic-multipliers/stage-02-quadrics.json.gz'
    assert prior['physical_sha256'] == binary_sha(PRIOR / 'stage-02-quadrics.json.gz')
    assert prior['initial_parameters'] == 66
    assert prior['prior_forced_raw_parameters'] == [8, 13, 26, 28, 38, 53, 56, 61, 66]
    assert packet['parameter_order'] == [dict(component=i, quadratic_powers=list(m),
        charge=(F.character(m) - F.WEIGHTS_MOD6[i]) % 6) for i, m in C.PARAMETERS]
    assert (packet['complete_correction_types'], packet['complete_raw_Koszul_fields'],
            packet['quotient_directions']) == (55, 230, 246)
    auxiliary = set()
    for binding in packet['auxiliary_files']:
        path = bound_path(binding['file'], binding['sha256'])
        assert path.suffix != '.json' and path.name.startswith('cas-')
        auxiliary.add(path.name)
    assert auxiliary == {path.name for path in OUT.glob('cas-*') if path.suffix != '.json'}


def audit_union_selection(packet, chain):
    """The selected powers must be exactly the union of checked proof attempts."""
    for index, item in enumerate(chain['stages']):
        selected, keys = {}, {}
        relevant = []
        for binding in packet['attempts']:
            attempt = A.I.load(OUT / binding['file'])
            if (attempt['status'] != 'completed' or attempt.get('stage', 0) != index
                    or attempt.get('basis') != 'reduced' or 'identities' not in attempt):
                continue
            relevant.append((binding['file'], attempt))
        # Cubic attempts precede quartic proof attempts; thresholds resolve
        # ties before filenames, without using the producer's elimination.
        relevant.sort(key=lambda x: ('quartic' in x[0], x[0]))
        for name, attempt in relevant:
            for identity in attempt['identities']:
                i = identity['parameter_index']
                key = (identity['power'], len(identity['multipliers']), attempt['term_threshold'])
                if i not in keys or key < keys[i]:
                    keys[i] = key
                    selected[i] = dict(identity, source_attempt=name)
        proof_file = item['info']['power_proof_file']
        assert proof_file is not None
        proof = A.I.load(OUT / proof_file)
        assert proof['identities'] == [selected[i] for i in sorted(selected)]


def main():
    assert __debug__, 'Run without -O'
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUT / 'independent-validation.json')
    parser.add_argument('--diagnostic-only', action='store_true',
                        help='Replay only the exact short products and the bounded failed simplification.')
    args = parser.parse_args()
    _, _, original = audit_prior_binding()
    if args.diagnostic_only:
        reduced = load_gzip(OUT / 'reduced-quadrics.json.gz')
        basis = audit_reduced_basis(original, reduced)
        print(json.dumps(dict(status='PASS', basis=basis,
            short_combinations=audit_short_combinations(original),
            failed_simplification=audit_short_target_queries(reduced)), indent=2))
        return
    packet = A.I.load(OUT / 'packet.json')
    check_bindings(packet)
    chain = audit_chain(packet, original)
    chain['coordinate_divisible_closure'] = audit_divisible_closure(
        chain, packet['coordinate_divisible_closure'])
    print('Independent closure through the prior 25-parameter subfamily: PASS', flush=True)
    attempts = audit_attempts(packet, chain)
    audit_union_selection(packet, chain)
    controls = mathematical_mutation_controls(chain)
    bad_closure = copy.deepcopy(packet['coordinate_divisible_closure'])
    bad_closure['embedding'][0]['old_local_parameter_index'] += 1
    assert A.I.rejects(lambda: audit_divisible_closure(chain, bad_closure))
    controls += 1
    for field in ('source_instance_sha256', 'producer_sha256', 'status'):
        bad = copy.deepcopy(packet)
        bad[field] = None
        assert A.I.rejects(lambda p=bad: check_bindings(p))
        controls += 1
    bad = copy.deepcopy(packet)
    bad['complete_correction_types'] = 50
    assert A.I.rejects(lambda: check_bindings(bad))
    controls += 1
    bad = copy.deepcopy(packet)
    bad['prior_proof']['physical_sha256'] = '0' * 64
    assert A.I.rejects(lambda: check_bindings(bad))
    controls += 1
    make_receipt(packet, chain, attempts, controls, args.output)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Independent physical replay of coordinate-divisible polar consequences.

Uses the frozen independent quadratic-polar reconstruction. The producer and
its arithmetic are never imported. Failed modular queries remain modular.
"""
from fractions import Fraction as Q
from pathlib import Path
import argparse
import copy
import hashlib
import json
from math import comb
import check_cyclic_fano_quadratic_polars as C

A, L = C.A, C.L
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/cyclic-fano-divisible-multipliers'
ZERO, ONE = A.ZERO, A.ONE


def source():
    exact = C.derive()
    active = [p for p, (i, m) in enumerate(C.PARAMETERS) if m[i]]
    assert len(active) == 25
    keys, columns = C.select_columns(exact, active)
    rows = L.columns_to_rows(columns)
    assert len(keys) == 1700 and len(rows) == 1228
    assert sum(kind == 'a*a' for kind, _, _ in keys) == 325
    assert sum(kind == 'a*c' for kind, _, _ in keys) == 1375
    return dict(exact=exact, active=active, keys=keys, columns=columns, rows=rows)


def restricted_system(exact, active):
    keys, columns = C.select_columns(exact, active)
    return dict(exact=exact, active=list(active), keys=keys, columns=columns,
                rows=L.columns_to_rows(columns))


def prepare_ranks(system):
    # Mixed columns come first so later pivots are correction-free equations.
    mixed = [j for j, key in enumerate(system['keys']) if key[0] == 'a*c']
    pure = [j for j, key in enumerate(system['keys']) if key[0] == 'a*a']
    order = mixed + pure
    lookup = {old: new for new, old in enumerate(order)}
    rows = {m: {lookup[j]: c for j, c in row.items()}
            for m, row in system['rows'].items()}
    pivots = L.row_basis(rows)
    modular_pivots = L.row_basis(rows, 1009)
    result = dict(rank=len(pivots), rank_mod_1009=len(modular_pivots),
                  mixed_rank=sum(j < len(mixed) for j in pivots),
                  pure_columns=len(pure), mixed_columns=len(mixed))
    result['necessary_quadrics'] = result['rank'] - result['mixed_rank']
    return result


def combine_rows(dual, rows):
    result = {}
    for m, (coefficient, imag) in dual.items():
        assert imag == 0 and m in rows
        for j, value in rows[m].items():
            new = result.get(j, Q(0)) + coefficient * value
            if new:
                result[j] = new
            else:
                result.pop(j, None)
    return result


def coefficient_digest(keys, columns):
    digest = hashlib.sha256()
    for (kind, p, r), column in zip(keys, columns):
        polynomial = [{'powers': list(m), 'coefficient': str(c[0])}
                      for m, c in sorted(column.items())]
        encoded = dict(label=dict(kind=kind, indices=[p, r]), polynomial=polynomial)
        digest.update((json.dumps(encoded, sort_keys=True, separators=(',', ':')) + '\n').encode())
    return digest.hexdigest()


def necessary_quadric(dual, system):
    row = combine_rows(dual, system['rows'])
    result = {}
    for j, coefficient in row.items():
        kind, p, r = system['keys'][j]
        assert kind == 'a*a', 'A proposed correction-free consequence retains correction variables'
        a, b = system['active'].index(p), system['active'].index(r)
        powers = tuple(int(k == a) + int(k == b) for k in range(len(system['active'])))
        result[powers] = (coefficient, Q(0))
    return result


def validate_equations(stage, system, ranks):
    assert stage['active_raw_parameter_indices'] == system['active']
    assert stage['rows'] == len(system['rows'])
    assert stage['columns'] == len(system['keys'])
    for key in ('rank', 'mixed_rank', 'pure_columns', 'mixed_columns'):
        assert stage[key] == ranks[key], key
    assert len(stage['equations']) == ranks['necessary_quadrics']
    equations = []
    for entry in stage['equations']:
        dual = L.decode(entry['dual'])
        equation = L.decode(entry['polynomial'], len(system['active']))
        assert dual and equation
        assert all(sum(m) == 12 and m[2] == 0 for m in dual)
        assert all(sum(m) == 2 for m in equation)
        assert necessary_quadric(dual, system) == equation
        equations.append(equation)
    independent_rank = len(L.row_basis({i: {m: c[0] for m, c in eq.items()}
                                       for i, eq in enumerate(equations)}))
    assert independent_rank == len(equations)
    return equations


def reduce_sparse(row, pivots, prime=None):
    row = dict(row)
    while row:
        j = min(row)
        if j not in pivots:
            return row
        coefficient = row[j]
        for k, value in pivots[j].items():
            updated = row.get(k, 0) - coefficient * value
            if prime is not None:
                updated %= prime
            if updated:
                row[k] = updated
            else:
                row.pop(k, None)
    return row


def prepare_cubic(equations, dimension):
    rows = {}
    for index, equation in enumerate(equations):
        for j in range(dimension):
            monomial = tuple(int(k == j) for k in range(dimension))
            polynomial = A.mul(equation, {monomial: ONE})
            rows[index, j] = {m: c[0] for m, c in polynomial.items()}
    pivots = L.row_basis(rows)
    remaining = [j for j in range(dimension)
                 if reduce_sparse({tuple(3 * int(k == j) for k in range(dimension)): Q(1)}, pivots)]
    quadratic_pivots = L.row_basis({i: {m: c[0] for m, c in equation.items()}
                                    for i, equation in enumerate(equations)})
    isolated_squares = [j for j in range(dimension)
                       if not reduce_sparse({tuple(2 * int(k == j) for k in range(dimension)): Q(1)}, quadratic_pivots)]
    modular_pivots = L.row_basis(rows, 1009)
    modular_remaining = [j for j in range(dimension)
                         if reduce_sparse({tuple(3 * int(k == j) for k in range(dimension)): 1},
                                          modular_pivots, 1009)]
    return dict(rank=len(pivots), rows=comb(dimension + 2, 3), columns=len(rows),
                remaining_parameter_indices=remaining, isolated_squares=isolated_squares,
                rank_mod_1009=len(modular_pivots),
                remaining_parameter_indices_mod_1009=modular_remaining)


def validate_cubic(stage, equations, dimension, prepared):
    assert stage['degree'] == 3
    for key in ('rank', 'rows', 'columns', 'remaining_parameter_indices'):
        assert stage[key] == prepared[key], key
    expected = set(range(dimension)) - set(prepared['remaining_parameter_indices'])
    seen = set(); terms = 0
    for identity in stage['identities']:
        index = identity['parameter_index']
        assert index in expected and index not in seen
        seen.add(index)
        assert identity['power'] == 3
        total = {}
        for multiplier in identity['multipliers']:
            q = multiplier['equation_index']; j = multiplier['linear_variable']
            assert q in range(len(equations)) and j in range(dimension)
            coefficient = Q(multiplier['coefficient'])
            monomial = tuple(int(k == j) for k in range(dimension))
            total = A.add(total, A.mul(equations[q], {monomial: (coefficient, Q(0))}))
            terms += 1
        target = {tuple(3 * int(k == index) for k in range(dimension)): ONE}
        assert total == target
    assert seen == expected
    return dict(identities=len(seen), multiplier_terms=terms)


def prepare(packet, system):
    ranks = prepare_ranks(system)
    equations = validate_equations(packet['initial_stage'], system, ranks)
    cubic = prepare_cubic(equations, 25)
    assert cubic['remaining_parameter_indices'] == [2, 7, 12, 17, 22]
    active = [system['active'][j] for j in cubic['remaining_parameter_indices']]
    assert all(C.PARAMETERS[p][1][3] for p in active)
    rebuilt = restricted_system(system['exact'], active)
    rebuilt_ranks = prepare_ranks(rebuilt)
    rebuilt_equations = validate_equations(packet['rebuild_stage'], rebuilt, rebuilt_ranks)
    final_cubic = prepare_cubic(rebuilt_equations, 5)
    surviving = cubic['remaining_parameter_indices']
    restricted_equations = []
    for equation in equations:
        restricted_equations.append({tuple(m[j] for j in surviving): c[0]
            for m, c in equation.items() if all(not exponent or j in surviving
                                               for j, exponent in enumerate(m))})
    old_restricted_pivots = L.row_basis(dict(enumerate(restricted_equations)))
    fresh_pivots = L.row_basis({j: {m: c[0] for m, c in q.items()}
                              for j, q in enumerate(rebuilt_equations)})
    assert len(old_restricted_pivots) == 9 and len(fresh_pivots) == 12
    assert all(not reduce_sparse(q, fresh_pivots) for q in restricted_equations)
    rebuilding_gain = dict(restricted_old_rank=9, rebuilt_rank=12,
                           added_independent_constraints=3, span_inclusion=True)
    assert ranks['rank'] == 833 and ranks['mixed_rank'] == 678
    assert rebuilt_ranks['rank'] == 232 and rebuilt_ranks['mixed_rank'] == 220
    assert cubic['rank'] == 2892 and final_cubic['rank'] == 35
    assert not cubic['isolated_squares'] and not final_cubic['isolated_squares']
    assert not final_cubic['remaining_parameter_indices']
    return dict(initial_ranks=ranks, initial_cubic=cubic, rebuilt=rebuilt,
                rebuilt_ranks=rebuilt_ranks, final_cubic=final_cubic,
                rebuilding_gain=rebuilding_gain)


def validate(packet, system, prepared):
    assert packet['schema'] == 'cyclic-fano-divisible-multipliers-v1'
    assert packet['status'] == 'PASS'
    assert (packet['instance'], packet['q'], packet['degree']) == ('cyclic-triple-fano', 1, 7)
    assert packet['source_commit'] == 'd96911d725077e66a8f10848908be01a643b1714'
    assert packet['source_instance_sha256'] == A.I.sha(L.C.SOURCE / 'source/instance.rec')
    assert packet['producer_sha256'] == A.I.sha(ROOT / 'experiments/cyclic_fano_divisible_multipliers.py')
    assert packet['dependencies'] == {name: A.I.sha(ROOT / 'experiments' / name) for name in
        ('cyclic_fano_quadratic_polars.py', 'cyclic_fano_linear_polars.py',
         'cyclic_fano_transfer.py', 'quadric_contact_pilot.py')}
    prior = packet['prior_projection_proof']
    assert prior['packet'] == 'results/cyclic-fano-quadratic-polars/packet.json'
    assert prior['packet_sha256'] == A.I.sha(C.OUT / 'packet.json')
    assert prior['primary_receipt_sha256'] == A.I.sha(C.OUT / 'validation.json')
    assert prior['independent_receipt_sha256'] == A.I.sha(C.OUT / 'independent-validation.json')
    assert (prior['raw_Koszul_fields'], prior['compact_correction_types'], prior['quotient_directions']) == (230, 55, 246)
    assert packet['base_variables'] == ['X0', 'X1', 'Y0', 'Y1', 'Y2']
    assert len(packet['parameter_order']) == 25
    for k, (p, entry) in enumerate(zip(system['active'], packet['parameter_order'])):
        component, m = C.PARAMETERS[p]
        rest = list(m); rest[component] -= 1
        j = next(j for j in C.BASE if rest[j])
        assert entry == dict(raw_parameter_index=p, matrix_row=C.BASE.index(component),
                             matrix_column=C.BASE.index(j), quadratic_powers=list(m))
        assert (entry['matrix_row'], entry['matrix_column']) == divmod(k, 5)
    equations = validate_equations(packet['initial_stage'], system, prepared['initial_ranks'])
    initial_checked = validate_cubic(packet['cubic_stage'], equations, 25, prepared['initial_cubic'])
    remaining = packet['cubic_stage']['remaining_parameter_indices']
    assert packet['rebuild_stage']['active_raw_parameter_indices'] == [system['active'][j] for j in remaining]
    rebuilt_equations = validate_equations(packet['rebuild_stage'], prepared['rebuilt'], prepared['rebuilt_ranks'])
    final_checked = validate_cubic(packet['final_cubic_stage'], rebuilt_equations, 5, prepared['final_cubic'])
    gain = prepared['rebuilding_gain']
    assert packet['rebuild_diagnostic'] == dict(
        initial_quadrics_after_restriction_rank=gain['restricted_old_rank'],
        fresh_rebuilt_quadrics_rank=gain['rebuilt_rank'],
        additional_independent_quadrics=gain['added_independent_constraints'],
        restricted_initial_span_contained_in_rebuilt_span=gain['span_inclusion'])
    attempts = packet['attempts']
    assert [(e['stage'], e['status']) for e in attempts] == [
        ('degree2', 'no_individual_square'), ('degree3_modular', 'partial_discovery'),
        ('degree3_rational', '20_coordinate_cubes_verified'),
        ('five_variable_rebuild', 'five_final_cubes_verified'), ('degree4', 'not_run')]
    modular = attempts[1]
    assert (modular['prime'], modular['rows'], modular['columns'], modular['rank_mod_prime']) == (1009, 2925, 3875, prepared['initial_cubic']['rank_mod_1009'])
    assert prepared['initial_cubic']['remaining_parameter_indices_mod_1009'] == remaining
    return dict(initial_cube_identities=initial_checked['identities'],
                initial_multiplier_terms=initial_checked['multiplier_terms'],
                final_cube_identities=final_checked['identities'],
                final_multiplier_terms=final_checked['multiplier_terms'],
                initial_dual_terms=sum(len(entry['dual']) for entry in packet['initial_stage']['equations']),
                rebuilt_dual_terms=sum(len(entry['dual']) for entry in packet['rebuild_stage']['equations']))


def main():
    assert __debug__, 'Run without -O'
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUT / 'independent-validation.json')
    args = parser.parse_args()
    packet_path = OUT / 'packet.json'; packet = A.I.load(packet_path)
    system = source(); prepared = prepare(packet, system)
    checked = validate(packet, system, prepared)
    negatives = []
    bad = copy.deepcopy(packet); bad['source_instance_sha256'] = '0' * 64; negatives.append(bad)
    bad = copy.deepcopy(packet); bad['prior_projection_proof']['compact_correction_types'] = 50; negatives.append(bad)
    bad = copy.deepcopy(packet); bad['parameter_order'][0]['matrix_column'] = 1; negatives.append(bad)
    bad = copy.deepcopy(packet); bad['initial_stage']['equations'][0]['dual'][0]['coefficient'] = '0'; negatives.append(bad)
    bad = copy.deepcopy(packet); bad['initial_stage']['equations'][0]['polynomial'][0]['coefficient'] = '0'; negatives.append(bad)
    bad = copy.deepcopy(packet); bad['cubic_stage']['identities'][0]['multipliers'][0]['coefficient'] = '0'; negatives.append(bad)
    bad = copy.deepcopy(packet); bad['cubic_stage']['rank'] -= 1; negatives.append(bad)
    bad = copy.deepcopy(packet); bad['cubic_stage']['remaining_parameter_indices'].pop(); negatives.append(bad)
    bad = copy.deepcopy(packet); bad['rebuild_stage']['active_raw_parameter_indices'].pop(); negatives.append(bad)
    bad = copy.deepcopy(packet); bad['rebuild_stage']['equations'][0]['dual'][0]['coefficient'] = '0'; negatives.append(bad)
    bad = copy.deepcopy(packet); bad['final_cubic_stage']['identities'][0]['multipliers'][0]['coefficient'] = '0'; negatives.append(bad)
    bad = copy.deepcopy(packet); bad['attempts'][1]['rank_mod_prime'] -= 1; negatives.append(bad)
    bad = copy.deepcopy(packet); bad['rebuild_diagnostic']['initial_quadrics_after_restriction_rank'] = 8; negatives.append(bad)
    rejected = sum(A.I.rejects(lambda p=p: validate(p, system, prepared)) for p in negatives)
    assert rejected == len(negatives) == 13
    primary_path = OUT / 'validation.json'; primary = A.I.load(primary_path)
    assert primary['status'] == 'PASS' and primary['packet_sha256'] == A.I.sha(packet_path)
    assert primary['producer_sha256'] == packet['producer_sha256']
    receipt = dict(schema='cyclic-fano-divisible-multipliers-independent-v1', status='PASS',
        checker_lf_sha256=A.I.sha(Path(__file__)), packet_lf_sha256=A.I.sha(packet_path),
        primary_validation_lf_sha256=A.I.sha(primary_path),
        source_instance_lf_sha256=A.I.sha(L.C.SOURCE / 'source/instance.rec'),
        independent_arithmetic_dependencies={Path(p).name: A.I.sha(Path(p)) for p in
                                            (C.__file__, L.__file__, L.C.__file__, A.__file__, A.I.__file__)},
        full_source_E1_and_Piola_lifts_replayed=75, family_parameters=25,
        full_raw_Koszul_fields=230, full_raw_projection_identities_replayed=17250,
        retained_correction_types=55, quotient_directions_replayed=246,
        Euler_normalization_identities_replayed=system['exact']['euler_checks'],
        initial_physical_map=dict(rows=1228, columns=1700, **prepared['initial_ranks'],
                                  coefficient_sha256=coefficient_digest(system['keys'], system['columns'])),
        initial_cubic_map=prepared['initial_cubic'],
        rebuilt_physical_map=dict(rows=851, columns=290, **prepared['rebuilt_ranks'],
            active_raw_parameter_indices=prepared['rebuilt']['active'],
            coefficient_sha256=coefficient_digest(prepared['rebuilt']['keys'], prepared['rebuilt']['columns'])),
        final_cubic_map=prepared['final_cubic'],
        rebuilding_gain=prepared['rebuilding_gain'],
        necessary_quadric_identities=167, physical_coefficient_pairings=155 * 1700 + 12 * 290,
        exact_failed_square_queries=30, negative_controls_rejected=rejected, **checked)
    receipt['conclusion'] = ('Every nonzero complex coordinate-divisible quadratic vector field '
        'v_i=x_i*sum_j M_ij*x_j produces an excluded degree-seven polar denominator. '
        'Twenty rational cubic identities force every column except Y0 to zero; '
        'five further cubic identities in the rebuilt system force the remaining coefficients to zero. '
        'All55 correction types and the full246-dimensional quotient freedom were retained.')
    receipt['limits'] = ('This excludes the25-parameter subfamily, not the full75-parameter quadratic '
        'direction family, arbitrary degree-seven denominators or unions of separately excluded supports. '
        'The original modular probes were discovery evidence; the conclusion here uses rational physical '
        'duals and polynomial identities. No degree-four multiplier search was needed or run, and no '
        'certificate, formal Lean proof or solve is claimed. The separate q=1 support theorem, not '
        'this arithmetic checker, supplies any extension to powers of a fixed rejected denominator.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(status='PASS', exact_quadrics=167, exact_cube_identities=25,
                          physical_coefficient_pairings=receipt['physical_coefficient_pairings'],
                          negative_controls=rejected, receipt_sha256=A.I.sha(args.output))))


if __name__ == '__main__':
    main()

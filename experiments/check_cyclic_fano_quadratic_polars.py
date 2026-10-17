#!/usr/bin/env python3
"""Independent reconstruction of quadratic-direction polars and exact partial proofs.

No producer is imported. Only frozen independent sparse arithmetic is reused.
"""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import argparse
import copy
import hashlib
import json
import check_cyclic_fano_linear_polars as L

A = L.A
BASE = L.BASE
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/cyclic-fano-quadratic-polars'
ZERO, ONE = A.ZERO, A.ONE
QUADRATICS = tuple(sorted(A.monomials(2), reverse=True))
PARAMETERS = tuple((i, m) for i in BASE for m in QUADRATICS)
decode, times = L.decode, L.times


def derive():
    F, alpha, G, beta = A.target()
    q, h, delta = L.C.split_G(G)
    gradient = [A.derivative(G, i) for i in range(6)]
    delta_gradient = [A.derivative(delta, i) for i in range(6)]
    denominators, fields = [], []
    for i, m in PARAMETERS:
        f = {m: ONE}; e = A.mul(f, delta_gradient[i])
        p = [{} for _ in range(6)]
        p[i] = times(A.mul(beta, f), -4)
        p[2] = times(A.mul(A.mul(beta, f), A.derivative(q, i)), 2)
        assert A.contraction(p, G) == A.mul(beta, e)
        assert A.contraction(A.lift(p), F) == A.mul(alpha, A.pullback(e))
        assert not A.add(times(p[2], 2), A.total(A.mul(A.derivative(q, k), p[k]) for k in BASE))
        assert A.divergence(p) == times(A.derivative(A.mul(beta, f), i), -4)
        denominators.append(e); fields.append(p)
    residuals = {}
    for p in range(75):
        for r in range(p, 75):
            residual = A.B(denominators[p], fields[r])
            if p != r:
                residual = A.add(residual, A.B(denominators[r], fields[p]))
            assert all(m[2] == 0 and sum(m) == 12 for m in residual)
            residuals[p, r] = residual
    rescaling_checks = 0
    for component, i in enumerate(BASE):
        constant_residual = times(A.add(
            A.mul(beta, A.derivative(delta_gradient[i], i)),
            times(A.mul(A.derivative(beta, i), delta_gradient[i]), -1)), 4)
        for p in range(15 * component, 15 * (component + 1)):
            for r in range(p, 15 * (component + 1)):
                product = A.mul({PARAMETERS[p][1]: ONE}, {PARAMETERS[r][1]: ONE})
                assert residuals[p, r] == times(A.mul(product, constant_residual), 1 if p == r else 2)
                rescaling_checks += 1
    assert rescaling_checks == 600
    correction_labels = [('linear_base_pair', i, j, k) for i, j in combinations(BASE, 2) for k in BASE]
    correction_labels += [('t_mixed', i) for i in BASE]
    mixed = {}
    for p, e in enumerate(denominators):
        ed = [A.derivative(e, i) for i in range(6)]
        for n, label in enumerate(correction_labels):
            if label[0] == 'linear_base_pair':
                _, i, j, k = label
                W_e = A.add(A.mul(delta_gradient[i], ed[j]), times(A.mul(delta_gradient[j], ed[i]), -1))
                W_x = delta_gradient[i] if k == j else times(delta_gradient[j], -1) if k == i else {}
                image = A.add(A.mul(e, W_x), times(A.mul(L.monomial(k), W_e), -1))
            else:
                _, i = label
                image = A.add(A.mul(e, delta_gradient[i]), times(A.mul(delta, ed[i]), -2))
            mixed[p, n] = image
    raw_fields = []
    for i, j in combinations(range(6), 2):
        for m in A.monomials(7 + A.WEIGHTS[i] + A.WEIGHTS[j] - 8):
            field = [{} for _ in range(6)]
            field[i] = A.mul({m: ONE}, gradient[j]); field[j] = times(A.mul({m: ONE}, gradient[i]), -1)
            assert not A.contraction(field, G)
            if 2 not in (i, j):
                k = next(k for k in BASE if m[k])
                n = correction_labels.index(('linear_base_pair', i, j, k)); factor = Q(1, 4)
            elif m[2] == 1:
                other = j if i == 2 else i
                n = correction_labels.index(('t_mixed', other)); factor = Q(-1 if i == 2 else 1, 4)
            else:
                n, factor = None, Q(0)
            for p, e in enumerate(denominators):
                actual = L.even_projection(A.B(e, field), q, h)
                expected = {} if n is None else times(mixed[p, n], factor)
                assert actual == expected, (p, i, j, m)
            raw_fields.append(dict(pair=(i, j), multiplier=m, field=field, compact_index=n, factor=factor))
    assert len(raw_fields) == 230
    assert sum(f['compact_index'] is not None for f in raw_fields) == 55
    quotient_monomials = A.monomials(6)
    assert len(quotient_monomials) == 246
    for m in quotient_monomials:
        assert not L.even_projection(A.mul({m: ONE}, G), q, h)
    # The degree-seven Euler gauge has multiplier weight five.
    euler_checks = 0
    for m in A.monomials(5):
        R = {m: ONE}; normalizer = []
        for i, w in enumerate(A.WEIGHTS):
            n = list(m); n[i] += 1
            normalizer.append({tuple(n): (Q(w, 6), Q(0))})
        assert A.contraction(normalizer, G) == A.mul(R, G)
        for e in denominators:
            assert A.B(e, normalizer) == A.mul(e, R)
            euler_checks += 1
    assert euler_checks == 10575
    injection_rows = [tuple(a + 5 * int(j == i) for j, a in enumerate(m)) for i, m in PARAMETERS]
    assert len(set(injection_rows)) == 75
    injection = [[e.get(m, ZERO)[0] for e in denominators] for m in injection_rows]
    assert [[c.numerator * pow(c.denominator, -1, 5) % 5 for c in row]
            for row in injection] == [[int(i == j) for j in range(75)] for i in range(75)]
    assert A.mod5(F) == {tuple(6 * int(i == j) for j in range(6)): 1 for i in range(6)}
    return dict(F=F, G=G, beta=beta, Q=q, H=h, Delta=delta,
                denominators=denominators, fields=fields, residuals=residuals,
                correction_labels=correction_labels, mixed=mixed, raw_fields=raw_fields,
                quotient_monomials=quotient_monomials, euler_checks=euler_checks,
                rescaling_checks=rescaling_checks,
                injection_rows=injection_rows, injection=injection)


def select_columns(exact, active):
    active = set(active)
    keys = [('a*a', p, r) for p, r in exact['residuals'] if p in active and r in active]
    keys += [('a*c', p, n) for p, n in exact['mixed'] if p in active]
    columns = [exact['residuals'][p, r] if kind == 'a*a' else exact['mixed'][p, r]
               for kind, p, r in keys]
    return keys, columns


def modular_screen(exact, active, prime=1009):
    keys, columns = select_columns(exact, active)
    rows = L.columns_to_rows(columns)
    basis = L.row_basis(rows, prime)
    squares = []
    for p in sorted(active):
        remainder = {keys.index(('a*a', p, p)): 1}
        while remainder:
            j = min(remainder)
            if j not in basis:
                break
            coefficient = remainder[j]
            for k, value in basis[j].items():
                updated = (remainder.get(k, 0) - coefficient * value) % prime
                if updated:
                    remainder[k] = updated
                else:
                    remainder.pop(k, None)
        if not remainder:
            squares.append(p)
    return dict(prime=prime, rows=len(rows), columns=len(columns), rank=len(basis), square_indices=squares)


def prepare(exact):
    keys, columns = select_columns(exact, range(75))
    digest = hashlib.sha256()
    for (kind, p, r), column in zip(keys, columns):
        encoded = [{'powers': list(m), 'coefficient': str(c[0])} for m, c in sorted(column.items())]
        entry = {'label': {'kind': kind, 'indices': [p, r]}, 'polynomial': encoded}
        digest.update((json.dumps(entry, sort_keys=True, separators=(',', ':')) + '\n').encode())
    full = modular_screen(exact, range(75))
    assert full == dict(prime=1009, rows=1799, columns=6975, rank=1759, square_indices=[])
    divisible_parameters = [p for p, (i, m) in enumerate(PARAMETERS) if m[i]]
    assert len(divisible_parameters) == 25
    divisible = modular_screen(exact, divisible_parameters)
    assert divisible['rank'] == 833 and not divisible['square_indices']
    stages = {}
    for component in range(5):
        active = set(range(15 * component, 15 * (component + 1)))
        for stage in range(2):
            keys, columns = select_columns(exact, active)
            rows = L.columns_to_rows(columns)
            rank = len(L.row_basis(rows))
            assert len(keys) == (945 if stage == 0 else 605)
            assert rank == ([489, 493, 493, 495, 491][component] if stage == 0 else 395)
            forced = {p for p in active if (max(PARAMETERS[p][1]) == 2) == (stage == 0)}
            assert len(forced) == (5 if stage == 0 else 10)
            stages[component, stage] = dict(active=sorted(active), keys=keys, columns=columns,
                                           rows=rows, rank=rank, forced=forced)
            active -= forced
        assert not active
    return dict(full_screen=full, divisible_parameters=divisible_parameters,
                divisible_screen=divisible, stages=stages, coefficient_sha256=digest.hexdigest())


def check_screen(actual, expected, active):
    assert actual['prime'] == expected['prime'] == 1009
    assert actual['active_parameters'] == list(active)
    assert actual['active_rows'] == expected['rows']
    assert actual['columns'] == expected['columns']
    assert actual['rank_mod_prime'] == expected['rank']
    assert actual['isolated_square_indices_mod_prime'] == expected['square_indices']


def validate_components(proofs, prepared):
    assert len(proofs) == 5
    pairings = terms = 0
    for component, family in enumerate(proofs):
        assert family['component'] == BASE[component]
        assert family['base_name'] == ['X0', 'X1', 'Y0', 'Y1', 'Y2'][component]
        assert family['remaining_parameters'] == [] and len(family['stages']) == 2
        active = set(range(15 * component, 15 * (component + 1)))
        for stage, packet in enumerate(family['stages']):
            exact = prepared['stages'][component, stage]
            assert sorted(active) == exact['active'] == packet['active_parameters']
            assert packet['active_rows'] == len(exact['rows'])
            assert packet['columns'] == len(exact['columns']) and packet['rank'] == exact['rank']
            assert len(packet['square_duals']) == len(exact['forced'])
            seen = set()
            for identity in packet['square_duals']:
                p = identity['parameter_index']
                assert p in active and p in exact['forced'] and p not in seen
                seen.add(p); dual = decode(identity['dual'])
                assert dual and set(dual) <= set(exact['rows'])
                target = exact['keys'].index(('a*a', p, p))
                assert [L.pairing(dual, column) for column in exact['columns']] == [Q(int(j == target)) for j in range(len(exact['columns']))]
                pairings += len(exact['columns']); terms += len(dual)
            assert seen == exact['forced']
            active -= seen
        assert not active
    return dict(square_duals=75, dual_nonzero_terms=terms, dual_coefficient_pairings=pairings)


def validate(packet, exact, prepared):
    assert packet['schema'] == 'cyclic-fano-quadratic-polars-v1' and packet['status'] == 'PASS'
    assert (packet['instance'], packet['q'], packet['degree']) == ('cyclic-triple-fano', 1, 7)
    assert packet['source_commit'] == 'd96911d725077e66a8f10848908be01a643b1714'
    assert packet['source_instance_sha256'] == A.I.sha(L.C.SOURCE / 'source/instance.rec')
    assert packet['producer_sha256'] == A.I.sha(ROOT / 'experiments/cyclic_fano_quadratic_polars.py')
    assert packet['dependencies'] == {name: A.I.sha(ROOT / 'experiments' / name) for name in
                                      ('cyclic_fano_linear_polars.py', 'cyclic_fano_transfer.py', 'quadric_contact_pilot.py')}
    assert packet['spatial_variables'] == ['X0', 'X1', 'Z', 'Y0', 'Y1', 'Y2']
    assert packet['base_variables'] == ['X0', 'X1', 'Y0', 'Y1', 'Y2']
    assert packet['residual_formula'] == '4*(beta*L(L(Delta))-(L(beta)+beta*div(v))*L(Delta))'
    for name in ('Delta', 'Q', 'H', 'beta'):
        assert decode(packet[name]) == exact[name]
    assert len(packet['parameter_basis']) == 75
    for p, ((i, m), entry) in enumerate(zip(PARAMETERS, packet['parameter_basis'])):
        assert entry['component'] == i and entry['quadratic_powers'] == list(m)
        assert decode(entry['E']) == exact['denominators'][p]
        assert [decode(field) for field in entry['particular']] == exact['fields'][p]
    projection = packet['projection']
    assert projection['raw_field_count'] == 230 and projection['raw_projection_identities'] == 17250
    assert projection['compact_generator_count'] == 55
    expected_compact = []
    for label in exact['correction_labels']:
        if label[0] == 'linear_base_pair':
            _, i, j, k = label
            expected_compact.append(dict(kind='linear_base_pair', pair=[i, j], linear_coordinate=k))
        else:
            expected_compact.append(dict(kind='t_mixed', coordinate=label[1]))
    assert projection['compact_generators'] == expected_compact
    expected_raw = {(f['pair'][0], f['pair'][1], f['multiplier']): f for f in exact['raw_fields']}
    assert len(projection['raw_field_labels']) == 230
    for entry in projection['raw_field_labels']:
        i, j = entry['pair']; m = tuple(entry['multiplier_powers'])
        assert (i, j, m) in expected_raw
        expected = expected_raw.pop((i, j, m))
        assert entry['compact_generator_index'] == expected['compact_index']
        assert Q(entry['compact_scale']) == expected['factor']
    assert not expected_raw
    assert projection['quotient_projection_identities'] == 246
    assert sorted(tuple(m) for m in projection['quotient_monomials']) == sorted(exact['quotient_monomials'])
    full = packet['full_map']
    assert (full['potential_rows'], full['active_rows'], full['columns'], full['pure_quadratic_columns'], full['mixed_columns']) == (1820, 1799, 6975, 2850, 4125)
    assert full['coefficient_sha256'] == prepared['coefficient_sha256']
    check_screen(packet['full_modular_screen'], prepared['full_screen'], range(75))
    check_screen(packet['coordinate_divisible_modular_screen'], prepared['divisible_screen'], prepared['divisible_parameters'])
    proof_stats = validate_components(packet['component_family_exclusions'], prepared)
    assert packet['square_dual_count'] == proof_stats['square_duals'] == 75
    assert packet['square_dual_nonzero_terms'] == proof_stats['dual_nonzero_terms']
    assert packet['single_component_rescaling_checks'] == exact['rescaling_checks'] == 600
    injection = packet['injectivity']
    assert injection['prime'] == 5 and injection['matrix_mod_prime'] == 'identity_75'
    assert injection['coefficient_rows'] == [list(m) for m in exact['injection_rows']]
    assert injection['determinant_mod_prime'] == 1
    regular = packet['regular_sequence_control']
    assert regular['prime'] == 5
    assert {tuple(entry['powers']): entry['coefficient'] for entry in regular['G_mod_prime']} == A.mod5(exact['G'])
    assert [(entry['id'], entry['status']) for entry in packet['attempts']] == [
        ('full75', 'unresolved'), ('coordinate_divisible25', 'unresolved'),
        ('five_single_component_families', 'exactly_excluded')]
    return proof_stats


def main():
    assert __debug__, 'Run without -O'
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUT / 'independent-validation.json')
    args = parser.parse_args()
    exact = derive(); prepared = prepare(exact)
    path = OUT / 'packet.json'; packet = A.I.load(path)
    checked = validate(packet, exact, prepared)
    negatives = []
    bad = copy.deepcopy(packet); bad['parameter_basis'].pop(); negatives.append(bad)
    bad = copy.deepcopy(packet); bad['projection']['raw_field_labels'].pop(); negatives.append(bad)
    bad = copy.deepcopy(packet); bad['projection']['compact_generators'] = bad['projection']['compact_generators'][:50]; negatives.append(bad)
    bad = copy.deepcopy(packet); bad['projection']['quotient_monomials'] = [m for m in bad['projection']['quotient_monomials'] if m[2] < 2]; negatives.append(bad)
    bad = copy.deepcopy(packet); bad['full_map']['coefficient_sha256'] = '0' * 64; negatives.append(bad)
    bad = copy.deepcopy(packet); bad['full_modular_screen']['rank_mod_prime'] -= 1; negatives.append(bad)
    bad = copy.deepcopy(packet); bad['component_family_exclusions'][0]['stages'][0]['square_duals'][0]['dual'][0]['coefficient'] = '0'; negatives.append(bad)
    bad = copy.deepcopy(packet); bad['component_family_exclusions'][0]['stages'][1]['active_parameters'].pop(); negatives.append(bad)
    bad = copy.deepcopy(packet); bad['injectivity']['determinant_mod_prime'] = 0; negatives.append(bad)
    rejected = sum(A.I.rejects(lambda p=p: validate(p, exact, prepared)) for p in negatives)
    assert rejected == len(negatives) == 9
    primary_path = OUT / 'validation.json'; primary = A.I.load(primary_path)
    assert primary['status'] == 'PASS' and primary['packet_sha256'] == A.I.sha(path)
    assert primary['producer_sha256'] == packet['producer_sha256']
    receipt = dict(schema='cyclic-fano-quadratic-polars-independent-v1', status='PASS',
                   checker_lf_sha256=A.I.sha(Path(__file__)), packet_lf_sha256=A.I.sha(path),
                   primary_validation_lf_sha256=A.I.sha(primary_path),
                   source_instance_lf_sha256=A.I.sha(L.C.SOURCE / 'source/instance.rec'),
                   independent_arithmetic_dependencies={Path(p).name: A.I.sha(Path(p)) for p in
                                                        (L.__file__, L.C.__file__, A.__file__, A.I.__file__)},
                   exact_E1_and_upstairs_Piola_lifts=75,
                   Euler_normalization_identities=exact['euler_checks'],
                   component_residual_rescaling_identities=exact['rescaling_checks'],
                   parameter_quadratic_coefficients_reconstructed=2850,
                   compact_mixed_columns_reconstructed=4125,
                   coefficient_sha256=prepared['coefficient_sha256'],
                   complete_raw_Koszul_fields=230, full_Koszul_projection_checks=17250,
                   surviving_correction_types=55, quotient_columns=246,
                   component_family_count=5, component_parameter_dimension=15,
                   negative_controls_rejected=rejected, **checked)
    receipt['exact_component_stages'] = [dict(component=BASE[i], base_name=packet['base_variables'][i],
        stages=[dict(active_parameters=s['active'], rows=len(s['rows']), columns=len(s['columns']),
                     exact_rank=s['rank'], forced_square_indices=sorted(s['forced']))
                for s in (prepared['stages'][i, 0], prepared['stages'][i, 1])]) for i in range(5)]
    receipt['modular_only_unresolved_screens'] = dict(full75=prepared['full_screen'], coordinate_divisible25=prepared['divisible_screen'])
    receipt['modular_limit'] = ('The absence of individual square consequences was checked only modulo1009 '
                                'for the full75 and coordinate-divisible25 screens. No characteristic-zero '
                                'nonmembership or family exclusion follows from those observations.')
    receipt['conclusion'] = ('For each fixed base coordinate i, every nonzero homogeneous quadratic f gives '
                             'an excluded denominator E=f*partial_i(Delta), retaining all55 compatible '
                             'correction types and246 quotient directions. Each complete15-parameter '
                             'family is excluded by two exact square-identity rounds.')
    receipt['limits'] = ('The five family exclusions do not exclude sums of different component directions, '
                         'the full75-dimensional family, the coordinate-divisible25 subfamily, arbitrary '
                         'degree-seven denominators, or unions of separately excluded supports. '
                         'No certificate, Lean acceptance or solution is claimed. Powers of each fixed '
                         'excluded denominator are also excluded by the separately cited q=1 support theorem, '
                         'whose geometric proof is not formalized here.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'status': 'PASS', 'E1_lifts': 75, 'raw_projection_checks': 17250,
                      'quotients': 246, 'excluded_component_families': 5,
                      'exact_square_identities': 75, 'negative_controls': rejected,
                      'receipt_sha256': A.I.sha(args.output)}))


if __name__ == '__main__':
    main()

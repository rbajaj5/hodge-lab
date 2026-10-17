#!/usr/bin/env python3
"""Independent source reconstruction of the degree-six linear polar system.

Only earlier independent arithmetic is reused. The producer is not imported.
"""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import argparse
import copy
import json
import check_cyclic_fano_branch_polars as C

A = C.A
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/cyclic-fano-linear-polars'
BASE = C.BASE
PARAMETERS = tuple((i, j) for i in BASE for j in BASE)
ZERO, ONE = A.ZERO, A.ONE


def decode(terms, length=6):
    result = {}
    for term in terms:
        powers = tuple(term['powers'])
        value = (Q(term['coefficient']), Q(0))
        assert len(powers) == length and all(isinstance(e, int) and e >= 0 for e in powers)
        assert powers not in result and value != ZERO
        result[powers] = value
    return result


def monomial(index):
    return {tuple(int(i == index) for i in range(6)): ONE}


def times(poly, scalar):
    return A.scale(poly, (Q(scalar), Q(0)))


def even_projection(poly, q, h):
    """Reduce all Z powers using its monic equation, then average Z -> -Q-Z."""
    remainder = dict(poly)
    while any(m[2] >= 2 for m in remainder):
        old = remainder
        remainder = {}
        for m, c in old.items():
            if m[2] < 2:
                remainder = A.add(remainder, {m: c})
                continue
            n = list(m); n[2] -= 2
            remainder = A.add(remainder, A.mul({tuple(n): A.cn(c)}, h))
            n[2] += 1
            remainder = A.add(remainder, A.mul({tuple(n): A.cn(c)}, q))
    constant = {m: c for m, c in remainder.items() if m[2] == 0}
    linear = {m[:2] + (0,) + m[3:]: c for m, c in remainder.items() if m[2] == 1}
    return A.add(constant, times(A.mul(q, linear), Q(-1, 2)))


def derive():
    F, alpha, G, beta = A.target()
    q, h, delta = C.split_G(G)
    gradient = [A.derivative(G, i) for i in range(6)]
    denominators, fields, divergences = [], [], []
    for i, j in PARAMETERS:
        x = monomial(j)
        e = A.mul(x, A.derivative(delta, i))
        p = [{} for _ in range(6)]
        p[i] = times(A.mul(beta, x), -4)
        p[2] = times(A.mul(A.mul(beta, x), A.derivative(q, i)), 2)
        assert A.contraction(p, G) == A.mul(beta, e)
        assert A.contraction(A.lift(p), F) == A.mul(alpha, A.pullback(e))
        assert not A.add(times(p[2], 2), A.total(A.mul(A.derivative(q, k), p[k]) for k in BASE))
        d = A.add(A.mul(x, A.derivative(beta, i)), beta if i == j else {})
        assert A.divergence(p) == times(d, -4)
        denominators.append(e); fields.append(p); divergences.append(d)
    residuals = {}
    for p in range(25):
        for r in range(p, 25):
            i, j = PARAMETERS[p]
            first = A.mul(beta, A.mul(monomial(j), A.derivative(denominators[r], i)))
            second = A.mul(divergences[p], denominators[r])
            physical = A.B(denominators[r], fields[p])
            if p != r:
                a, b = PARAMETERS[r]
                first = A.add(first, A.mul(beta, A.mul(monomial(b), A.derivative(denominators[p], a))))
                second = A.add(second, A.mul(divergences[r], denominators[p]))
                physical = A.add(physical, A.B(denominators[p], fields[r]))
            residual = times(A.add(first, times(second, -1)), 4)
            assert residual == physical
            assert all(m[2] == 0 and sum(m) == 10 for m in residual)
            residuals[p, r] = residual
    corrections, labels = [], []
    for i, j in combinations(range(6), 2):
        for m in A.monomials(6 + A.WEIGHTS[i] + A.WEIGHTS[j] - 8):
            field = [{} for _ in range(6)]
            field[i] = A.mul({m: ONE}, gradient[j])
            field[j] = times(A.mul({m: ONE}, gradient[i]), -1)
            assert not A.contraction(field, G)
            corrections.append(field); labels.append((i, j, m))
    assert len(corrections) == 85
    correction_images = {}
    surviving = {}
    for p, e in enumerate(denominators):
        for label, field in zip(labels, corrections):
            i, j, m = label
            raw = A.B(e, field)
            projected = even_projection(raw, q, h)
            expected = {} if 2 in (i, j) else times(A.add(
                A.mul(A.derivative(delta, j), A.derivative(e, i)),
                times(A.mul(A.derivative(delta, i), A.derivative(e, j)), -1)), Q(1, 4))
            assert projected == expected
            correction_images[p, i, j, m] = (raw, projected)
            if 2 not in (i, j):
                assert not any(m)
                surviving[p, i, j] = projected
    assert len(correction_images) == 2125 and len(surviving) == 250
    quotient_images = {}
    for m in A.monomials(4):
        raw = A.mul({m: ONE}, G)
        assert not even_projection(raw, q, h)
        quotient_images[m] = raw
    assert len(quotient_images) == 75
    # Euler normalization: R has weight d-2=4; subtract R times Euler/6.
    euler_count = 0
    for m in A.monomials(4):
        R = {m: ONE}
        normalizer = []
        for i, w in enumerate(A.WEIGHTS):
            n = list(m); n[i] += 1
            normalizer.append({tuple(n): (Q(w, 6), Q(0))})
        assert A.contraction(normalizer, G) == A.mul(R, G)
        for e in denominators:
            assert A.B(e, normalizer) == A.mul(e, R)
            euler_count += 1
    assert euler_count == 1875
    assert A.mod5(F) == {tuple(6 if i == j else 0 for j in range(6)): 1 for i in range(6)}
    return dict(F=F, G=G, beta=beta, Q=q, H=h, Delta=delta,
                denominators=denominators, fields=fields, residuals=residuals,
                correction_labels=labels, correction_images=correction_images,
                surviving_images=surviving, quotient_images=quotient_images,
                Euler_normalization_checks=euler_count)


def pairing(dual, polynomial):
    return sum((coefficient[0] * polynomial.get(m, ZERO)[0]
                for m, coefficient in dual.items()), Q(0))


def columns_to_rows(columns):
    rows = {}
    for j, poly in enumerate(columns):
        for m, (real, imag) in poly.items():
            assert imag == 0
            rows.setdefault(m, {})[j] = real
    return rows


def row_basis(rows, prime=None):
    result = {}
    for m, original in sorted(rows.items(), key=lambda item: (len(item[1]), item[0])):
        row = dict(original) if prime is None else {
            k: c.numerator * pow(c.denominator, -1, prime) % prime
            for k, c in original.items()}
        row = {k: c for k, c in row.items() if c}
        while row:
            j = min(row); coefficient = row[j]
            if j not in result:
                inverse = 1 / coefficient if prime is None else pow(coefficient, -1, prime)
                result[j] = {k: c * inverse if prime is None else c * inverse % prime
                             for k, c in row.items()}
                break
            for k, c in result[j].items():
                value = row.get(k, 0) - coefficient * c
                if prime is not None:
                    value %= prime
                if value:
                    row[k] = value
                else:
                    row.pop(k, None)
    return result


def determinant(matrix):
    work = [row[:] for row in matrix]
    result = Q(1)
    for j in range(len(work)):
        candidates = [i for i in range(j, len(work)) if work[i][j]]
        if not candidates:
            return Q(0)
        k = candidates[-1]
        if j != k:
            work[j], work[k] = work[k], work[j]; result *= -1
        pivot = work[j][j]; result *= pivot
        for i in range(j + 1, len(work)):
            ratio = work[i][j] / pivot
            if ratio:
                work[i] = [x - ratio * y for x, y in zip(work[i], work[j])]
    return result


def map_data(exact):
    pairs = tuple(combinations(BASE, 2))
    pure = list(exact['residuals'])
    mixed = [(p, i, j) for p in range(25) for i, j in pairs]
    columns = [exact['residuals'][key] for key in pure] + [exact['surviving_images'][key] for key in mixed]
    rows = columns_to_rows(columns)
    basis = row_basis(rows)
    modular = row_basis(rows, 1009)
    assert len(rows) == 859 and len(basis) == len(modular) == 414
    diagonal = [0, 6, 12, 18, 24]
    diagonal_pairs = [(p, r) for p in diagonal for r in diagonal if p <= r]
    diagonal_mixed = [(p, i, j) for p in diagonal for i, j in pairs]
    diag_columns = [exact['surviving_images'][key] for key in diagonal_mixed] + [exact['residuals'][key] for key in diagonal_pairs]
    diag_rows = columns_to_rows(diag_columns)
    diag_basis = row_basis(diag_rows)
    assert len(diag_rows) == 219 and len(diag_basis) == 52
    assert sum(k < 50 for k in diag_basis) == 40
    for p in diagonal:
        remainder = {50 + diagonal_pairs.index((p, p)): Q(1)}
        while remainder:
            k = min(remainder)
            if k not in diag_basis:
                break
            coefficient = remainder[k]
            for j, c in diag_basis[k].items():
                value = remainder.get(j, Q(0)) - coefficient * c
                if value:
                    remainder[j] = value
                else:
                    remainder.pop(j, None)
        assert remainder, 'A claimed unsuccessful diagonal-square query actually succeeds'
    # For every matrix basis parameter select x_i^5*x_j. The minor is I mod5.
    inject_rows = [tuple(5 * int(k == i) + int(k == j) for k in range(6))
                   for i, j in PARAMETERS]
    inject_matrix = [[e.get(m, ZERO)[0] for e in exact['denominators']] for m in inject_rows]
    assert [[c.numerator * pow(c.denominator, -1, 5) % 5 for c in row]
            for row in inject_matrix] == [[int(i == j) for j in range(25)] for i in range(25)]
    return dict(pairs=pairs, pure=pure, mixed=mixed, columns=columns, rows=rows,
                diagonal=diagonal, diagonal_pairs=diagonal_pairs,
                diagonal_mixed=diagonal_mixed, diag_columns=diag_columns,
                diag_rows=diag_rows, full_rank=len(basis), diagonal_rank=len(diag_basis),
                inject_rows=inject_rows, inject_matrix=inject_matrix,
                inject_determinant=determinant(inject_matrix))


def validate(packet, exact, maps):
    assert packet['schema'] == 'cyclic-fano-linear-polars-v1' and packet['status'] == 'PASS'
    assert packet['instance'] == 'cyclic-triple-fano' and packet['q'] == 1 and packet['degree'] == 6
    assert packet['source_commit'] == 'd96911d725077e66a8f10848908be01a643b1714'
    assert packet['source_instance_sha256'] == A.I.sha(C.SOURCE / 'source/instance.rec')
    assert packet['producer_sha256'] == A.I.sha(ROOT / 'experiments/cyclic_fano_linear_polars.py')
    assert packet['dependencies'] == {name: A.I.sha(ROOT / 'experiments' / name)
                                      for name in ('cyclic_fano_transfer.py', 'quadric_contact_pilot.py')}
    assert packet['spatial_variables'] == ['X0', 'X1', 'Z', 'Y0', 'Y1', 'Y2']
    assert packet['base_variables'] == ['X0', 'X1', 'Y0', 'Y1', 'Y2']
    assert packet['matrix_parameter_order'] == 'row-major M_ij, v_i=sum_j M_ij*x_j'
    assert packet['residual_formula'] == '4*(beta*L(L(Delta))-(L(beta)+beta*trace(M))*L(Delta))'
    for name in ('Delta', 'Q', 'H', 'beta'):
        assert decode(packet[name]) == exact[name]
    assert len(packet['basis']) == 25
    for p, entry in enumerate(packet['basis']):
        assert entry['matrix_indices'] == [p // 5, p % 5]
        assert decode(entry['E']) == exact['denominators'][p]
        assert [decode(field) for field in entry['particular']] == exact['fields'][p]
    assert len(packet['quadratic_residual_basis']) == 325
    for key, entry in zip(maps['pure'], packet['quadratic_residual_basis']):
        assert entry['matrix_indices'] == list(key)
        assert decode(entry['polynomial']) == exact['residuals'][key]
    assert len(packet['mixed_correction_basis']) == 250
    for key, entry in zip(maps['mixed'], packet['mixed_correction_basis']):
        p, i, j = key
        assert entry['matrix_index'] == p and entry['constant_pair_index'] == maps['pairs'].index((i, j))
        assert decode(entry['polynomial']) == exact['surviving_images'][key]
    assert packet['full_map'] == dict(potential_rows=1001, active_rows=859, columns=575,
                                     quadratic_columns=325, mixed_columns=250, rank=maps['full_rank'])
    projection = packet['projection']
    assert projection['raw_fields_per_denominator'] == 85 and len(projection['raw_fields']) == 85
    assert projection['raw_projection_identities'] == 2125
    assert projection['surviving_constant_base_pairs'] == [list(pair) for pair in maps['pairs']]
    assert projection['mixed_images_nonzero'] == sum(bool(p) for p in exact['surviving_images'].values())
    gradient = [A.derivative(exact['G'], i) for i in range(6)]
    unseen_fields = set(exact['correction_labels'])
    for entry in projection['raw_fields']:
        i, j = entry['pair']; m = tuple(entry['multiplier_powers'])
        assert (i, j, m) in unseen_fields
        unseen_fields.remove((i, j, m))
        assert entry['surviving_constant_pair'] == (None if 2 in (i, j) else maps['pairs'].index((i, j)))
        field = [{} for _ in range(6)]
        field[i] = A.mul({m: ONE}, gradient[j]); field[j] = times(A.mul({m: ONE}, gradient[i]), -1)
        assert [decode(poly) for poly in entry['field']] == field
    assert not unseen_fields
    assert projection['quotient_projection_identities'] == 75
    assert sorted(tuple(m) for m in projection['quotient_multiplier_powers']) == sorted(exact['quotient_images'])
    # Every dual is checked on the complete physical 575-column relaxation.
    assert len(packet['off_diagonal_square_duals']) == 20
    seen = set()
    for entry in packet['off_diagonal_square_duals']:
        p = entry['parameter_index']; assert p in range(25) and p // 5 != p % 5 and p not in seen
        seen.add(p); dual = decode(entry['dual'])
        assert dual and set(dual) <= set(maps['rows'])
        target = maps['pure'].index((p, p))
        assert [pairing(dual, column) for column in maps['columns']] == [Q(int(j == target)) for j in range(575)]
    assert seen == {p for p in range(25) if p // 5 != p % 5}
    diagonal = packet['diagonal_stage']
    assert diagonal['parameter_indices'] == maps['diagonal']
    assert diagonal['active_rows'] == 219 and diagonal['columns'] == 65
    assert diagonal['rank'] == maps['diagonal_rank'] and diagonal['mixed_rank'] == 40
    assert len(diagonal['equations']) == 12
    quadrics = []
    for entry in diagonal['equations']:
        quadric = decode(entry['polynomial'], 5); dual = decode(entry['dual'])
        assert quadric and dual and set(dual) <= set(maps['rows'])
        assert all(sum(m) == 2 for m in quadric)
        expected = [Q(0)] * 50
        for p, r in maps['diagonal_pairs']:
            i, j = maps['diagonal'].index(p), maps['diagonal'].index(r)
            powers = tuple(int(k == i) + int(k == j) for k in range(5))
            expected.append(quadric.get(powers, ZERO)[0])
        assert [pairing(dual, column) for column in maps['diag_columns']] == expected
        quadrics.append(quadric)
    assert len(row_basis(columns_to_rows(quadrics))) == 12
    cubic = packet['cubic_macaulay']
    assert (cubic['degree'], cubic['rows'], cubic['columns'], cubic['rank']) == (3, 35, 60, 35)
    multiples = [A.mul(poly, {tuple(int(j == i) for j in range(5)): ONE})
                 for poly in quadrics for i in range(5)]
    assert len(row_basis(columns_to_rows(multiples))) == 35
    assert len(cubic['identities']) == 5
    seen = set()
    for identity in cubic['identities']:
        p = identity['diagonal_variable']; assert p in range(5) and p not in seen; seen.add(p)
        assert identity['power'] == 3
        target = {tuple(3 * int(j == p) for j in range(5)): ONE}
        assert decode(identity['target'], 5) == target
        result = {}; used = set()
        for term in identity['multipliers']:
            i, j, coefficient = term['equation_index'], term['variable'], Q(term['coefficient'])
            assert i in range(12) and j in range(5) and coefficient and (i, j) not in used
            used.add((i, j)); result = A.add(result, times(multiples[5 * i + j], coefficient))
        assert result == target
    injection = packet['injectivity']
    assert injection['rows'] == [list(m) for m in maps['inject_rows']]
    assert [[Q(c) for c in row] for row in injection['matrix']] == maps['inject_matrix']
    assert Q(injection['determinant']) == maps['inject_determinant'] != 0
    control = packet['regular_sequence_control']
    assert control['prime'] == 5
    actual = {tuple(term['powers']): term['coefficient'] for term in control['G_mod5']}
    expected = {tuple((2 if j == 2 else 6) * int(k == j) for k in range(6)): 1 for j in range(6)}
    assert actual == expected == A.mod5(exact['G'])
    return {'full_map_exact_rank': maps['full_rank'], 'diagonal_exact_rank': maps['diagonal_rank'],
            'diagonal_quadrics_rank': 12, 'cubic_macaulay_exact_rank': 35,
            'dual_coefficient_pairings': 20 * 575 + 12 * 65,
            'injection_determinant': str(maps['inject_determinant'])}


def main():
    assert __debug__, 'Run without -O'
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=OUT / 'independent-validation.json')
    args = parser.parse_args()
    exact = derive(); maps = map_data(exact)
    path = OUT / 'packet.json'; packet = A.I.load(path)
    checked = validate(packet, exact, maps)
    negatives = []
    bad = copy.deepcopy(packet); bad['basis'][0]['particular'][0] = []; negatives.append(bad)
    bad = copy.deepcopy(packet); bad['quadratic_residual_basis'].pop(); negatives.append(bad)
    bad = copy.deepcopy(packet); bad['mixed_correction_basis'][0]['polynomial'][0]['coefficient'] = '0'; negatives.append(bad)
    bad = copy.deepcopy(packet); bad['projection']['raw_fields'].pop(); negatives.append(bad)
    bad = copy.deepcopy(packet); bad['projection']['quotient_multiplier_powers'] = [m for m in bad['projection']['quotient_multiplier_powers'] if not m[2]]; negatives.append(bad)
    bad = copy.deepcopy(packet); bad['off_diagonal_square_duals'][0]['dual'][0]['coefficient'] = '0'; negatives.append(bad)
    bad = copy.deepcopy(packet); bad['diagonal_stage']['equations'][0]['dual'][0]['coefficient'] = '0'; negatives.append(bad)
    bad = copy.deepcopy(packet); bad['diagonal_stage']['equations'][0]['polynomial'][0]['coefficient'] = '0'; negatives.append(bad)
    bad = copy.deepcopy(packet); bad['cubic_macaulay']['identities'][0]['multipliers'][0]['coefficient'] = '0'; negatives.append(bad)
    bad = copy.deepcopy(packet); bad['cubic_macaulay']['rank'] = 34; negatives.append(bad)
    bad = copy.deepcopy(packet); bad['injectivity']['determinant'] = '0'; negatives.append(bad)
    rejected = sum(A.I.rejects(lambda p=p: validate(p, exact, maps)) for p in negatives)
    assert rejected == len(negatives) == 11
    primary_path = OUT / 'validation.json'; primary = A.I.load(primary_path)
    assert primary['status'] == 'PASS' and primary['packet_sha256'] == A.I.sha(path)
    assert primary['producer_sha256'] == packet['producer_sha256']
    receipt = dict(schema='cyclic-fano-linear-polars-independent-v1', status='PASS',
                   checker_lf_sha256=A.I.sha(Path(__file__)), packet_lf_sha256=A.I.sha(path),
                   primary_validation_lf_sha256=A.I.sha(primary_path),
                   source_instance_lf_sha256=A.I.sha(C.SOURCE / 'source/instance.rec'),
                   independent_arithmetic_dependencies={Path(p).name: A.I.sha(Path(p))
                                                        for p in (C.__file__, A.__file__, A.I.__file__)},
                   exact_E1_and_upstairs_Piola_lifts=25,
                   Euler_normalization_basis_identities=exact['Euler_normalization_checks'],
                   parameter_quadratic_coefficients_reconstructed=325,
                   complete_Koszul_fields=85, full_Koszul_projection_checks=2125,
                   surviving_correction_generator_types=10, surviving_mixed_columns=250,
                   quotient_columns=75, off_diagonal_square_identities=20,
                   diagonal_quadrics=12, diagonal_cube_identities=5,
                   failed_diagonal_square_queries_checked_over_Q=5,
                   negative_controls_rejected=rejected, **checked)
    receipt['scope'] = ('Every constant complex 5x5 matrix M is covered, with v=Mx and E=v(Delta). '
                        'Euler normalization and the original cyclic character projection preserve existence. '
                        'All homogeneous Koszul corrections are reconstructed using the regular gradient sequence. '
                        'Reflection removes 75 correction types and retains ten; no shared correction variable is '
                        'specialized. Necessary squares force all off-diagonal M entries to zero, then twelve '
                        'physical coefficient consequences and five cubic identities force every diagonal entry to zero.')
    receipt['limits'] = ('This verifies a degree-six family exclusion, not arbitrary degree-six denominators, '
                         'higher polynomial-direction fields, a complete certificate, Lean acceptance, or a solved instance. '
                         'Applying the repository q=1 prescribed-support theorem additionally excludes powers of each '
                         'member; that geometric theorem is not formalized by this arithmetic checker.')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'status': 'PASS', 'parameter_terms': 325, 'Koszul_projection_checks': 2125,
                      'square_identities': 20, 'cube_identities': 5, 'negative_controls': rejected,
                      'receipt_sha256': A.I.sha(args.output)}))


if __name__ == '__main__':
    main()

"""Independent degree-six reconstruction from SymPy-parsed protected targets.

No project algebra modules are imported. Finite-field elimination uses the
largest exponent tuple as pivot. Exact exported identities are checked with
standard-library Fraction arithmetic; modular observations alone are not
reported as characteristic-zero exclusions.
"""
from __future__ import annotations
import argparse
from fractions import Fraction as Q
import hashlib
import itertools
import json
from pathlib import Path
import time
import sympy as s

P = 1009
NAMES = ('X0', 'X1', 'X2', 'Y0', 'Y1', 'Y2')
SYMS = s.symbols(' '.join(NAMES))


def monos(n, degree):
    if n == 1:
        return [(degree,)]
    return [(a,) + tail for a in range(degree + 1)
            for tail in monos(n - 1, degree - a)]


def addexp(a, b):
    return tuple(x + y for x, y in zip(a, b))


def add(a, b, scale=Q(1)):
    for key, value in b.items():
        new = a.get(key, Q(0)) + scale * value
        if new:
            a[key] = new
        else:
            a.pop(key, None)
    return a


def mul(a, b):
    result = {}
    for m, u in a.items():
        for n, v in b.items():
            key = addexp(m, n)
            result[key] = result.get(key, Q(0)) + u * v
    return {key: value for key, value in result.items() if value}


def shift(poly, mono, scale=Q(1)):
    return {addexp(m, mono): c * scale for m, c in poly.items() if c * scale}


def diff(poly, index):
    result = {}
    for mono, value in poly.items():
        if mono[index]:
            new = list(mono)
            new[index] -= 1
            result[tuple(new)] = value * mono[index]
    return result


def div(field):
    result = {}
    for index, poly in enumerate(field):
        add(result, diff(poly, index))
    return result


def B(denominator, field):
    result = mul(denominator, div(field))
    for index, poly in enumerate(field):
        add(result, mul(poly, diff(denominator, index)), -1)
    return result


def lf_sha(path):
    return hashlib.sha256(path.read_text(encoding='utf-8').encode('utf-8')).hexdigest()


def sympy_coeff(poly):
    return {m: Q(int(v.p), int(v.q)) for m, v in poly.terms() if v}


def target(repo, instance):
    folder = repo / 'sources' / 'sextics' / 'data' / instance
    fields = {}
    for line in (folder / 'instance.rec').read_text(encoding='utf-8').splitlines():
        for key in ('F', 'A', 'q'):
            if line.startswith(key + ': '):
                fields[key] = line[len(key) + 2:]
    assert fields['q'] == '1'
    f = s.Poly(s.sympify(fields['F']), SYMS)
    a = s.Poly(s.sympify(fields['A']), SYMS)
    assert {sum(m) for m, _ in f.terms()} == {6}
    assert {sum(m) for m, _ in a.terms()} == {6}
    bindings = {str(path.relative_to(repo)).replace('\\', '/'): lf_sha(path)
                for path in (folder / 'instance.rec', folder / 'why.md', folder / 'provenance.json')}
    return sympy_coeff(f), sympy_coeff(a), fields, bindings


def mod(poly):
    result = {}
    for key, value in poly.items():
        value = Q(value)
        c = value.numerator * pow(value.denominator, -1, P) % P
        if c:
            result[key] = c
    return result


def madd(a, b, scale=1):
    for key, value in b.items():
        new = (a.get(key, 0) + scale * value) % P
        if new:
            a[key] = new
        else:
            a.pop(key, None)
    return a


def echelon(columns):
    basis = {}
    for column in columns:
        c = mod(column)
        while c:
            pivot = max(c)
            if pivot not in basis:
                inverse = pow(c[pivot], -1, P)
                basis[pivot] = {key: value * inverse % P for key, value in c.items()}
                break
            madd(c, basis[pivot], -c[pivot])
    return basis


def reduce_mod(column, basis):
    c = mod(column)
    for pivot in sorted(basis, reverse=True):
        if pivot in c:
            madd(c, basis[pivot], -c[pivot])
    return c


def rank(columns):
    return len(echelon(columns))


def koszul_fields(gradient):
    fields = []
    for i, j in itertools.combinations(range(6), 2):
        for mono in monos(6, 2):
            field = [{} for _ in range(6)]
            field[i] = shift(gradient[j], mono)
            field[j] = shift(gradient[i], mono, -1)
            fields.append(field)
    return fields


def pair(dual, column):
    if len(dual) > len(column):
        dual, column = column, dual
    return sum((v * column[k] for k, v in dual.items() if k in column), Q(0))


def indexed_dual(raw, row_degree):
    rows = monos(6, row_degree)
    assert len({int(index) for index, _ in raw}) == len(raw)
    assert all(0 <= int(index) < len(rows) for index, _ in raw)
    return {rows[int(index)]: Q(coefficient) for index, coefficient in raw}


def unpack(raw):
    assert len({int(index) for index, _ in raw}) == len(raw)
    return {int(index): Q(coefficient) for index, coefficient in raw}


def check_e1_packet(repo, instance):
    path = repo / 'results' / 'fresh-instance-degree6' / instance / 'degree-6.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    f, a, fields, bindings = target(repo, instance)
    assert data['schema'] == 'fresh-instance-e1-v1'
    assert data['instance'] == instance and data['degree'] == 6 and data['q'] == 1
    assert data['target'] == fields and data['source_sha256'] == bindings
    gradient = [diff(f, i) for i in range(6)]
    jac = [shift(poly, mono) for poly in gradient for mono in monos(6, 7)]
    ad = [shift(a, mono) for mono in monos(6, 6)]
    dc = []
    for item in data['dual_obstructions']:
        dual = indexed_dual(item['functional'], 12)
        assert all(pair(dual, col) == 0 for col in jac)
        values = {i: pair(dual, col) for i, col in enumerate(ad)}
        values = {i: c for i, c in values.items() if c}
        assert values == unpack(item['denominator_constraint'])
        dc.append(values)
    kernel = []
    for item in data['kernel_lifts']:
        den, num = unpack(item['denominator']), unpack(item['numerator'])
        assert all(0 <= i < len(ad) for i in den)
        assert all(0 <= i < len(jac) for i in num)
        residual = {}
        for i, c in den.items():
            add(residual, ad[i], c)
        for i, c in num.items():
            add(residual, jac[i], -c)
        assert not residual
        kernel.append(den)
    assert rank(dc) == len(dc) and rank(kernel) == len(kernel)
    assert len(dc) + len(kernel) == 462
    expected = 36 if instance == 'cycle-three' else 39
    assert len(kernel) == expected
    dimensions = data['dimensions']
    assert dimensions == {'coefficient_rows': 6188, 'denominator_columns': 462,
        'numerator_columns': 4752, 'jacobian_rank': 4437,
        'augmented_rank': 4437 + len(dc), 'denominator_image_rank': len(dc),
        'denominator_kernel_dimension': len(kernel)}
    return {'instance': instance, 'status': 'PASS', 'packet_sha256': lf_sha(path),
            'kernel_lifts_checked': len(kernel), 'dual_constraints_checked': len(dc),
            'exact_jacobian_pairings': len(dc) * len(jac),
            'exact_AD_pairings': len(dc) * len(ad), 'dimensions': dimensions}


def require_failure(call):
    try:
        call()
    except AssertionError:
        return 1
    raise AssertionError('Altered evidence was accepted')


def check_isolating_dual(dual, null_columns, image_columns, expected):
    assert all(pair(dual, column) == 0 for column in null_columns)
    assert [pair(dual, column) for column in image_columns] == expected


def check_hessian_packet(repo):
    folder = repo / 'results' / 'fresh-instance-degree6' / 'cycle-three'
    path = folder / 'degree-6-e2.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    f, a, fields, bindings = target(repo, 'cycle-three')
    assert data['schema'] == 'fresh-instance-degree6-hessian-v1'
    assert data['instance'] == 'cycle-three'
    assert data['target'] == fields and data['source_sha256'] == bindings
    assert data['degree6_E1_sha256'] == lf_sha(folder / 'degree-6.json')
    gradient = [diff(f, i) for i in range(6)]
    jac = [shift(poly, mono) for poly in gradient for mono in monos(6, 7)]
    params = [(i, j) for i in range(6) for j in range(6) if (i, j) != (5, 5)]
    assert data['parameters'] == [[NAMES[i], NAMES[j]] for i, j in params]
    pairs = list(itertools.combinations_with_replacement(range(35), 2))
    assert data['quadratic_column_pairs'] == list(map(list, pairs))
    ahess = [[mul(a, diff(gradient[i], j)) for j in range(6)] for i in range(6)]
    columns = []
    for u, v in pairs:
        i, k = params[u]
        j, ell = params[v]
        mono = tuple(int(t == k) + int(t == ell) for t in range(6))
        columns.append(shift(ahess[i][j], mono, 1 if u == v else 2))
    assert data['steps'][0]['allowed_parameters'] == list(range(35))
    assert data['steps'][0]['active_columns'] == list(range(630))
    witnesses = data['steps'][0]['forced_squares']
    checked, mutations = [], 0
    for item in witnesses:
        u = item['parameter']
        assert 0 <= u < 35 and params[u][0] != params[u][1]
        assert item['square_column'] == pairs.index((u, u))
        expected = [Q(int(col == item['square_column'])) for col in range(630)]
        dual = indexed_dual(item['functional'], 12)
        check_isolating_dual(dual, jac, columns, expected)
        altered = dict(dual)
        add(altered, {next(iter(jac[0])): Q(1)})
        mutations += require_failure(lambda: check_isolating_dual(altered, jac, columns, expected))
        checked.append(u)
    assert sorted(checked) == [u for u, (i, j) in enumerate(params) if i != j]
    remaining = [u for u, (i, j) in enumerate(params) if i == j]
    assert data['remaining_parameters'] == remaining
    assert data['steps'][0]['unresolved_parameters'] == remaining
    assert data['steps'][1]['allowed_parameters'] == remaining
    assert data['steps'][1]['forced_squares'] == []
    assert not data['degree6_excluded']
    return {'instance': 'cycle-three', 'status': 'PASS', 'packet_sha256': lf_sha(path),
            'squares_checked': len(checked), 'exact_J12_pairings': len(checked) * len(jac),
            'exact_hessian_pairings': len(checked) * len(columns),
            'mutations_rejected': mutations, 'remaining_diagonal_parameters': len(remaining)}


def quadratic_poly(raw, pairs, nvars):
    result = {}
    for column, value in unpack(raw).items():
        assert 0 <= column < len(pairs)
        i, j = pairs[column]
        mono = tuple(int(k == i) + int(k == j) for k in range(nvars))
        add(result, {mono: value})
    return result


def check_power_identity(item, equations):
    parameter, power = item['parameter'], item['power']
    assert 0 <= parameter < 5 and power == 4
    total, products = {}, 0
    for row, raw_mono, raw_coefficient in item['multipliers']:
        assert 0 <= row < len(equations)
        mono = tuple(raw_mono)
        assert len(mono) == 5 and all(type(v) is int and v >= 0 for v in mono)
        assert sum(mono) == 2
        coefficient = Q(raw_coefficient)
        assert coefficient
        add(total, shift(equations[row], mono, coefficient))
        products += len(equations[row])
    expected = {tuple(4 if i == parameter else 0 for i in range(5)): Q(1)}
    assert total == expected
    return products


def check_diagonal_packet(repo):
    folder = repo / 'results' / 'fresh-instance-degree6' / 'cycle-three'
    path = folder / 'degree-6-diagonal.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    f, a, fields, bindings = target(repo, 'cycle-three')
    assert data['schema'] == 'fresh-instance-degree6-diagonal-v1'
    assert data['instance'] == 'cycle-three'
    assert data['target'] == fields and data['source_sha256'] == bindings
    assert data['hessian_packet_sha256'] == lf_sha(folder / 'degree-6-e2.json')
    gradient = [diff(f, i) for i in range(6)]
    units = [tuple(int(i == j) for j in range(6)) for i in range(6)]
    ds = [shift(gradient[i], units[i]) for i in range(6)]
    ns = [[shift(a, units[i]) if i == j else {} for j in range(6)] for i in range(6)]
    fields_k = koszul_fields(gradient)
    correction_columns = [shift(f, mono) for mono in monos(6, 6)]
    correction_columns += [B(d, k) for d in ds for k in fields_k]
    pairs = list(itertools.combinations_with_replacement(range(6), 2))
    assert data['quadratic_column_pairs'] == list(map(list, pairs))
    quadratic_columns = []
    for i, j in pairs:
        column = B(ds[i], ns[j])
        if i != j:
            add(column, B(ds[j], ns[i]))
        quadratic_columns.append(column)
    equations6, mutations = [], 0
    for item in data['consequences']:
        dual = indexed_dual(item['functional'], 12)
        coefficients = unpack(item['quadratic_coefficients'])
        expected = [coefficients.get(i, Q(0)) for i in range(21)]
        check_isolating_dual(dual, correction_columns, quadratic_columns, expected)
        equations6.append(quadratic_poly(item['quadratic_coefficients'], pairs, 6))
        altered = dict(dual)
        add(altered, {next(iter(correction_columns[0])): Q(1)})
        mutations += require_failure(lambda: check_isolating_dual(altered, correction_columns, quadratic_columns, expected))
    assert len(equations6) == 7 and rank(equations6) == 7
    pairs5 = list(itertools.combinations_with_replacement(range(5), 2))
    assert data['gauged_column_pairs'] == list(map(list, pairs5))
    gauged = [{m[:5]: c for m, c in equation.items() if m[5] == 0} for equation in equations6]
    assert gauged == [quadratic_poly(raw, pairs5, 5) for raw in data['gauged_equations']]
    search = data['quartic_search']
    assert search['degree'] == 4 and search['coefficient_columns'] == 70
    assert search['multiplier_rows'] == 105 and search['row_rank'] == 70
    macaulay = [shift(equation, mono) for equation in gauged for mono in monos(5, 2)]
    quartic_monomials = set(monos(5, 4))
    assert len(macaulay) == 105 and len(quartic_monomials) == 70
    assert all(set(row) <= quartic_monomials for row in macaulay)
    assert rank(macaulay) == 70  # also proves rational full rowspace, bounded by 70 columns.
    checked, products, multiplier_terms = [], 0, 0
    for item in search['identities']:
        products += check_power_identity(item, gauged)
        checked.append(item['parameter'])
        multiplier_terms += len(item['multipliers'])
        altered = dict(item)
        altered['multipliers'] = [list(row) for row in item['multipliers']]
        altered['multipliers'][0][2] = str(Q(altered['multipliers'][0][2]) + 1)
        mutations += require_failure(lambda: check_power_identity(altered, gauged))
    assert sorted(checked) == list(range(5))
    assert data['degree6_excluded'] is True
    return {'instance': 'cycle-three', 'status': 'PASS', 'packet_sha256': lf_sha(path),
            'full_E2_consequences': len(equations6), 'correction_columns': len(correction_columns),
            'exact_correction_pairings': len(equations6) * len(correction_columns),
            'exact_quadratic_pairings': len(equations6) * len(quadratic_columns),
            'quartic_identities_checked': len(checked), 'quartic_coefficient_products': products,
            'multiplier_monomials': multiplier_terms, 'quartic_rank_mod_p': 70,
            'quartic_multiplier_rows': len(macaulay),
            'quartic_coefficient_columns': len(quartic_monomials),
            'quartic_characteristic_zero_rank_reason': 'The independently reconstructed 105-by-70 rational Macaulay matrix has rank70 modulo1009, matching its70-column upper bound; hence its rank overQ andC is70.',
            'mutations_rejected': mutations,
            'conclusion': 'All five Euler-gauged diagonal coefficients vanish over C. Together with the full E1 kernel and 30 off-diagonal square checks, only inadmissible D proportional to F survives at degree six.'}


def audit_modular(repo, instance):
    start = time.perf_counter()
    f, a, _, bindings = target(repo, instance)
    gradient = [diff(f, i) for i in range(6)]
    jac = [shift(poly, mono) for poly in gradient for mono in monos(6, 7)]
    ad = [shift(a, mono) for mono in monos(6, 6)]
    j6 = [shift(poly, mono) for poly in gradient for mono in monos(6, 1)]
    fields = koszul_fields(gradient)
    flattened = [{(i, m): c for i, poly in enumerate(field) for m, c in poly.items()}
                 for field in fields]
    kernel_rank = rank(flattened)
    assert kernel_rank == 315
    # Each Koszul field is exactly in the numerator kernel; its independence
    # modulo P also establishes independence over Q.
    for field in fields:
        image = {}
        for poly, derivative in zip(field, gradient):
            add(image, mul(poly, derivative))
        assert not image
    nrank, fullrank, j6rank = rank(jac), rank(jac + ad), rank(j6)
    assert nrank == 4437 and j6rank == 36
    projection = len(ad) - fullrank + nrank
    expected = 36 if instance == 'cycle-three' else 39
    assert projection == expected
    result = {'instance': instance, 'prime': P, 'source_sha256': bindings,
              'numerator_columns': len(jac), 'denominator_columns': len(ad),
              'rank_n_mod_p': nrank, 'rank_augmented_mod_p': fullrank,
              'denominator_projection_dimension_mod_p': projection,
              'quadratic_koszul_rank': kernel_rank, 'J6_rank': j6rank,
              'exact_koszul_identities': len(fields),
              'rank_n_characteristic_zero_reason': '315 independent exact Koszul kernel fields give the matching upper bound 4752-315=4437.',
              'projection_characteristic_zero_reason':
                  '36 independent exact gradient denominator lifts and the Koszul fields give the matching augmented upper bound 5214-315-36=4863.'
                  if instance == 'cycle-three' else
                  'Modular observation only here; the three extra characteristic-zero directions require the separate exact packet.'}
    # Necessary Hessian map on the J6 subfamily. For mixed-biweight this is
    # deliberately not used to draw a conclusion about its three extra axes.
    params = [(i, j) for i in range(6) for j in range(6) if (i, j) != (5, 5)]
    pairs = list(itertools.combinations_with_replacement(range(35), 2))
    ahess = [[mul(a, diff(gradient[i], j)) for j in range(6)] for i in range(6)]
    jb = echelon(jac)
    hcols = []
    for u, v in pairs:
        i, k = params[u]
        j, ell = params[v]
        mono = tuple(int(t == k) + int(t == ell) for t in range(6))
        hcols.append(reduce_mod(shift(ahess[i][j], mono, 1 if u == v else 2), jb))
    rows = {}
    for colindex, col in enumerate(hcols):
        for mono, value in col.items():
            rows.setdefault(mono, {})[colindex] = value
    rb = echelon(rows.values())
    squares = [list(params[u]) for col, (u, v) in enumerate(pairs)
               if u == v and not reduce_mod({col: 1}, rb)]
    assert len(rb) == 291 and len(squares) == 30
    result['restricted_hessian_probe'] = {'parameters': params,
        'columns': len(hcols), 'rank_mod_p': len(rb),
        'isolatable_squares_mod_p': squares,
        'scope': 'Complete E1 family only for cycle-three; restricted J6 subfamily for mixed-biweight.'}
    result['seconds'] = time.perf_counter() - start
    return result


def mixed_restricted_failure(repo):
    """Reproduce a failed modular screen; never assert a full-family result."""
    start = time.perf_counter()
    f, a, _, _ = target(repo, 'mixed-biweight')
    gradient = [diff(f, i) for i in range(6)]
    units = [tuple(int(i == j) for j in range(6)) for i in range(6)]
    ds = [shift(gradient[i], units[i]) for i in range(6)]
    ns = [[shift(a, units[i]) if i == j else {} for j in range(6)] for i in range(6)]
    ks = koszul_fields(gradient)
    corrections = [shift(f, mono) for mono in monos(6, 6)]
    corrections += [B(d, k) for d in ds for k in ks]
    cb = echelon(corrections)
    pairs = list(itertools.combinations_with_replacement(range(6), 2))
    columns = []
    for i, j in pairs:
        column = B(ds[i], ns[j])
        if i != j:
            add(column, B(ds[j], ns[i]))
        columns.append(reduce_mod(column, cb))
    rows = {}
    for column_index, col in enumerate(columns):
        for mono, value in col.items():
            rows.setdefault(mono, {})[column_index] = value
    rb = echelon(rows.values())
    assert len(corrections) == 2352 and len(cb) == 1451 and len(rb) == 5
    variables = s.symbols('a0:5') + (s.Integer(0),)
    generators = [sum(c * variables[pairs[j][0]] * variables[pairs[j][1]]
                      for j, c in row.items()) for _, row in sorted(rb.items())]
    gb = s.groebner(generators, *variables[:5], order='grevlex', modulus=P)
    powers_found, attempts = [], []
    for i, variable in enumerate(variables[:5]):
        for power in range(2, 9):
            remainder = gb.reduce(variable ** power)[1]
            attempts.append({'parameter': i, 'power': power,
                             'zero_remainder': bool(remainder == 0)})
            if remainder == 0:
                powers_found.append([i, power])
    assert powers_found == []
    return {'instance': 'mixed-biweight', 'prime': P,
            'status': 'bounded_power_search_unsuccessful',
            'scope': 'Only the diagonal part of the 36-dimensional J6 subfamily after the exploratory off-diagonal screen. The full E1 kernel has three additional directions; they are not tested here.',
            'correction_columns': len(corrections), 'correction_rank_mod_p': len(cb),
            'quadratic_columns': len(columns), 'necessary_quadratic_rank_mod_p': len(rb),
            'quadratic_pairs': list(map(list, pairs)),
            'rowbasis_mod_p': [sorted(row.items()) for _, row in sorted(rb.items())],
            'gauge': 'Set a5=0 after the degree-six Euler/F gauge.',
            'groebner_basis_mod_p': [str(poly.as_expr()) for poly in gb.polys],
            'groebner_order': 'grevlex', 'coordinate_power_checks': attempts,
            'powers_found': powers_found,
            'limits': 'Powers 2 through 8 were tested. No time limit was imposed on this small completed modular Groebner computation. Failure to find powers does not establish existence, nonexistence, or a characteristic-zero conclusion.',
            'seconds': time.perf_counter() - start}


def main():
    if not __debug__:
        raise RuntimeError('Run without -O: this verifier uses assertions.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repo', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    result = {'status': 'PASS', 'method': __doc__,
              'modular_audits': [audit_modular(args.repo, name)
                                 for name in ('cycle-three', 'mixed-biweight')],
              'exact_E1_audits': [check_e1_packet(args.repo, name)
                                 for name in ('cycle-three', 'mixed-biweight')],
              'exact_hessian_audit': check_hessian_packet(args.repo),
              'exact_diagonal_audit': check_diagonal_packet(args.repo),
              'mixed_restricted_failed_probe': mixed_restricted_failure(args.repo)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('w', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items()
                      if k not in ('method', 'modular_audits', 'mixed_restricted_failed_probe')}, indent=2))


if __name__ == '__main__':
    main()

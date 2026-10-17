"""Independent full mixed-biweight degree-six continuation audit.

This reuses only the earlier independent parser/sparse arithmetic, never the
construction implementation. Every saved extra lift is reconstructed and
checked against F,A. Modular exploratory conclusions are labelled separately
from any later exact witness checks.
"""
from __future__ import annotations
import argparse
import itertools
import json
from pathlib import Path
import time
import sympy as s
import check_fresh_instance_degree6_independent as h


def reconstruct(repo):
    f, a, fields, bindings = h.target(repo, 'mixed-biweight')
    gradient = [h.diff(f, i) for i in range(6)]
    units = [tuple(int(i == j) for j in range(6)) for i in range(6)]
    labels = [(i, j) for i in range(6) for j in range(6) if (i, j) != (5, 5)]
    ds = [h.shift(gradient[i], units[j]) for i, j in labels]
    ns = [[h.shift(a, units[j]) if k == i else {} for k in range(6)]
          for i, j in labels]
    path = repo / 'results/fresh-instance-degree6/mixed-biweight/degree-6.json'
    packet = json.loads(path.read_text(encoding='utf-8'))
    assert packet['target'] == fields and packet['source_sha256'] == bindings
    assert packet['non_J6_representative_kernel_indices'] == [17, 29, 30]
    den_monos, num_monos = h.monos(6, 6), h.monos(6, 7)
    for index in (17, 29, 30):
        item = packet['kernel_lifts'][index]
        ds.append({den_monos[j]: c for j, c in h.unpack(item['denominator']).items()})
        n = [{} for _ in range(6)]
        for j, c in h.unpack(item['numerator']).items():
            component, mono = divmod(j, len(num_monos))
            n[component][num_monos[mono]] = c
        ns.append(n)
        labels.append(('extra', index))
    for d, n in zip(ds, ns):
        residual = h.mul(a, d)
        for ni, fi in zip(n, gradient):
            h.add(residual, h.mul(ni, fi), -1)
        assert not residual
    assert h.rank(ds + [f]) == 39
    ks = h.koszul_fields(gradient)
    flattened = [{(i, m): c for i, part in enumerate(k) for m, c in part.items()}
                 for k in ks]
    assert h.rank(flattened) == 315
    jac = [h.shift(fi, mono) for fi in gradient for mono in h.monos(6, 7)]
    assert h.rank(jac) == 4437
    ad = [h.shift(a, mono) for mono in h.monos(6, 6)]
    assert h.rank(jac + ad) == 4860
    # For quadratic monomial t, div(t*(Fj ei-Fi ej)) = (di t)Fj-(dj t)Fi.
    # Hence both components and divergence lie in J, so B_D(K) is in J even
    # for the three extra denominator directions D not in J.
    index = 0
    for i, j in itertools.combinations(range(6), 2):
        for mono in h.monos(6, 2):
            scalar = {mono: h.Q(1)}
            expected = h.mul(h.diff(scalar, i), gradient[j])
            h.add(expected, h.mul(h.diff(scalar, j), gradient[i]), -1)
            assert h.div(ks[index]) == expected
            kernel_identity = {}
            for component, derivative in zip(ks[index], gradient):
                h.add(kernel_identity, h.mul(component, derivative))
            assert not kernel_identity
            index += 1
    return f, a, ds, ns, ks, jac, labels, fields, bindings, path


def check_quotient(repo):
    f, a, ds, ns, ks, jac, labels, fields, bindings, source = reconstruct(repo)
    path = repo / 'results/mixed-degree6-extra/quotient.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    assert data['schema'] == 'mixed-degree6-extra-quotient-v1'
    assert data['instance'] == 'mixed-biweight'
    assert data['target'] == fields and data['source_sha256'] == bindings
    assert data['degree6_E1_sha256'] == h.lf_sha(source)
    assert len(data['parameters']) == 38
    for i, (kind, value) in enumerate(labels):
        meta = data['parameters'][i]
        if kind == 'extra':
            assert meta['kind'] == 'extra-E1' and meta['kernel_lift_index'] == value
        else:
            assert meta['kind'] == 'linear-field' and meta['component'] == kind and meta['variable'] == value
    pairs, cols = full_quadratics(ds, ns)
    assert data['quadratic_column_pairs'] == list(map(list, pairs))
    allowed, stages, mutations, hpairings, jpairings = list(range(38)), [], 0, 0, 0
    for step in data['steps']:
        assert step['allowed_parameters'] == allowed
        active = [i for i, (a, b) in enumerate(pairs) if a in allowed and b in allowed]
        assert step['active_columns'] == active
        eliminated = []
        for item in step['forced_squares']:
            parameter = item['parameter']
            assert parameter in allowed
            column = pairs.index((parameter, parameter))
            assert item['square_column'] == column
            dual = h.indexed_dual(item['functional'], 12)
            expected = [h.Q(int(c == column)) for c in active]
            h.check_isolating_dual(dual, jac, [cols[c] for c in active], expected)
            jpairings += len(jac)
            hpairings += len(active)
            altered = dict(dual)
            h.add(altered, {next(iter(jac[0])): h.Q(1)})
            mutations += h.require_failure(lambda: h.check_isolating_dual(altered, jac, [cols[c] for c in active], expected))
            eliminated.append(parameter)
        assert len(eliminated) == len(set(eliminated))
        allowed = [i for i in allowed if i not in eliminated]
        assert step['unresolved_parameters'] == allowed
        stages.append({'squares_verified': len(eliminated), 'remaining_parameters': allowed})
    assert [stage['squares_verified'] for stage in stages] == [28, 5, 0]
    assert data['remaining_parameters'] == allowed == [0, 7, 14, 21, 28]
    return {'status': 'PASS', 'packet_sha256': h.lf_sha(path),
            'complete_E1_lifts_verified': 38, 'full_E1_dimension': 39,
            'complete_E1_basis_including_F_rank_mod_p': 39,
            'E1_augmented_rank_mod_p': 4860,
            'extra_kernel_lift_indices_included': [17, 29, 30],
            'exact_Koszul_kernel_identities': 315, 'exact_Koszul_divergence_identities': 315,
            'stages': stages, 'exact_J12_pairings': jpairings,
            'exact_quadratic_pairings': hpairings, 'mutations_rejected': mutations}


def qechelon(rows):
    basis = {}
    for row in rows:
        c = dict(row)
        while c:
            pivot = max(c)
            if pivot not in basis:
                scale = c[pivot]
                basis[pivot] = {key: value / scale for key, value in c.items()}
                break
            h.add(c, basis[pivot], -c[pivot])
    return basis


def qreduce(row, basis):
    c = dict(row)
    for pivot in sorted(basis, reverse=True):
        if pivot in c:
            h.add(c, basis[pivot], -c[pivot])
    return c


def poly_power(poly, power):
    n = len(next(iter(poly)))
    result = {(0,) * n: h.Q(1)}
    for _ in range(power):
        result = h.mul(result, poly)
    return result


def linear_poly(raw):
    return {tuple(int(k == i) for k in range(5)): c for i, c in h.unpack(raw).items()}


def difference_identity(item, equations):
    assert item['power'] == 4
    linear = linear_poly(item['linear_form'])
    total, products = {}, 0
    for row, raw_mono, raw_coefficient in item['multipliers']:
        assert 0 <= row < len(equations)
        mono = tuple(raw_mono)
        assert len(mono) == 5 and all(type(n) is int and n >= 0 for n in mono) and sum(mono) == 2
        h.add(total, h.shift(equations[row], mono, h.Q(raw_coefficient)))
        products += len(equations[row])
    assert total == poly_power(linear, 4)
    return products


def check_diagonal(repo):
    f, a, _, _, ks, _, _, fields, bindings, _ = reconstruct(repo)
    path = repo / 'results/mixed-degree6-extra/diagonal.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    assert data['schema'] == 'mixed-degree6-extra-diagonal-v1'
    assert data['instance'] == 'mixed-biweight'
    assert data['target'] == fields and data['source_sha256'] == bindings
    assert data['quotient_sha256'] == h.lf_sha(path.with_name('quotient.json'))
    units = [tuple(int(i == j) for j in range(6)) for i in range(6)]
    ds = [h.shift(h.diff(f, i), units[i]) for i in range(6)]
    ns = [[h.shift(a, units[i]) if i == j else {} for j in range(6)] for i in range(6)]
    corrections = [h.shift(f, mono) for mono in h.monos(6, 6)]
    corrections += [h.B(d, k) for d in ds for k in ks]
    pairs, columns = full_quadratics(ds, ns)
    assert data['quadratic_column_pairs'] == list(map(list, pairs))
    equations6, mutations = [], 0
    for item in data['consequences']:
        dual = h.indexed_dual(item['functional'], 12)
        coefficients = h.unpack(item['quadratic_coefficients'])
        expected = [coefficients.get(i, h.Q(0)) for i in range(21)]
        h.check_isolating_dual(dual, corrections, columns, expected)
        equations6.append(h.quadratic_poly(item['quadratic_coefficients'], pairs, 6))
        altered = dict(dual)
        h.add(altered, {next(iter(corrections[0])): h.Q(1)})
        mutations += h.require_failure(lambda: h.check_isolating_dual(altered, corrections, columns, expected))
    assert len(equations6) == h.rank(equations6) == 5
    pairs5 = list(itertools.combinations_with_replacement(range(5), 2))
    assert data['gauged_column_pairs'] == list(map(list, pairs5))
    equations = [{m[:5]: c for m, c in equation.items() if m[5] == 0} for equation in equations6]
    assert equations == [h.quadratic_poly(row, pairs5, 5) for row in data['gauged_equations']]
    attempts, products, terms = [], 0, 0
    for attempt in data['multiplier_attempts']:
        degree = attempt['degree']
        assert degree in (2, 3, 4)
        multipliers = h.monos(5, degree - 2)
        macaulay = [h.shift(equation, mono) for equation in equations for mono in multipliers]
        qb = qechelon(macaulay)
        assert attempt['coefficient_columns'] == len(h.monos(5, degree))
        assert attempt['multiplier_rows'] == len(macaulay)
        assert attempt['row_rank'] == len(qb)
        unresolved = []
        for i in (0, 1, 3):
            target = linear_poly([[i, '1'], [4, '-1']])
            if qreduce(poly_power(target, degree), qb):
                unresolved.append(i)
        assert attempt['unresolved_difference_parameters'] == unresolved
        attempts.append({'degree': degree, 'exact_rank': len(qb),
                         'multiplier_rows': len(macaulay),
                         'coefficient_columns': len(h.monos(5, degree)),
                         'unresolved_difference_parameters': unresolved})
        checked = []
        for item in attempt['identities']:
            assert degree == 4
            form = h.unpack(item['linear_form'])
            assert len(form) == 2 and form[4] == -1
            i = next(j for j in form if j != 4)
            assert i in (0, 1, 3) and form[i] == 1
            checked.append(i)
            products += difference_identity(item, equations)
            terms += len(item['multipliers'])
            altered = dict(item)
            altered['multipliers'] = [list(row) for row in item['multipliers']]
            altered['multipliers'][0][2] = str(h.Q(altered['multipliers'][0][2]) + 1)
            mutations += h.require_failure(lambda: difference_identity(altered, equations))
        if degree == 4:
            assert sorted(checked) == [0, 1, 3]
    assert [a['degree'] for a in attempts] == [2, 3, 4]
    # After the three exact fourth-power vanishings, substitute a0=a1=a3=a4=s.
    P = {(2, 0): h.Q(5), (1, 1): h.Q(-8), (0, 2): h.Q(8)}
    ratios = data['two_parameter_reduction']['source_equation_multiples']
    assert len(ratios) == len(equations)
    for equation, raw_ratio in zip(equations, ratios):
        substituted = {}
        for mono, c in equation.items():
            h.add(substituted, {(mono[2], sum(mono) - mono[2]): c})
        assert substituted == {m: c * h.Q(raw_ratio) for m, c in P.items()}
    assert any(h.Q(r) for r in ratios)
    return {'status': 'PASS', 'packet_sha256': h.lf_sha(path),
            'exact_full_E2_consequences': len(equations6),
            'exact_correction_pairings': len(equations6) * len(corrections),
            'exact_quadratic_pairings': len(equations6) * len(columns),
            'bounded_multiplier_attempts': attempts, 'fourth_power_identities': 3,
            'multiplier_terms': terms, 'coefficient_products': products,
            'exact_two_parameter_substitutions': len(equations), 'mutations_rejected': mutations,
            'conclusion': 'The complete degree-six E1 family reduces to two normalized conjugate diagonal candidates; their full shared-K equation still needs separate checking.'}


def field_pair(dual, column):
    """Pair using rational polynomial pairs, independently of the field solver.

    Each input consists of its constant and t coefficient dictionaries.
    Reduction uses t^2=(-8+8t)/5 only after the rational dot products.
    """
    a, b = dual
    c, d = column
    bd = h.pair(b, d)
    return (h.pair(a, c) - h.Q(8, 5) * bd,
            h.pair(a, d) + h.pair(b, c) + h.Q(8, 5) * bd)


def validate_field_dual(dual, corrections, target):
    assert all(field_pair(dual, column) == (0, 0) for column in corrections)
    assert field_pair(dual, target) == (1, 0)


def check_field_obstruction(repo):
    path = repo / 'results/mixed-degree6-extra/field-obstruction.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    f, a, _, _, ks, _, _, fields, bindings, _ = reconstruct(repo)
    assert data['schema'] == 'mixed-degree6-quadratic-field-v1'
    assert data['instance'] == 'mixed-biweight' and data['degree'] == 6
    assert data['target'] == fields and data['source_sha256'] == bindings
    assert list(map(h.Q, data['field']['minimal_polynomial_ascending'])) == [8, -8, 5]
    assert data['field']['basis'] == ['1', 't']
    assert [[h.Q(v) for v in pair] for pair in data['diagonal_coordinates']] == [
        [1, 0], [1, 0], [0, 1], [1, 0], [1, 0], [0, 0]]
    units = [tuple(int(i == j) for j in range(6)) for i in range(6)]
    ds = [h.shift(h.diff(f, i), units[i]) for i in range(6)]
    d0, d1 = {}, ds[2]
    for i in (0, 1, 3, 4):
        h.add(d0, ds[i])
    n0 = [h.shift(a, units[i]) if i in (0, 1, 3, 4) else {} for i in range(6)]
    n1 = [h.shift(a, units[i]) if i == 2 else {} for i in range(6)]
    corrections = [(h.shift(f, mono), {}) for mono in h.monos(6, 6)]
    corrections += [(h.B(d0, k), h.B(d1, k)) for k in ks]
    assert len(corrections) == 777
    # Expand B_(D0+tD1)(N0+tN1) over Q before reducing its t^2 term.
    c0 = h.B(d0, n0)
    c1 = h.B(d0, n1)
    h.add(c1, h.B(d1, n0))
    c2 = h.B(d1, n1)
    h.add(c0, c2, -h.Q(8, 5))
    h.add(c1, c2, h.Q(8, 5))
    target = (c0, c1)
    rows = h.monos(6, 12)
    raw = data['functional']
    assert len(raw) == len({int(row[0]) for row in raw}) == 3
    dual = ({rows[int(i)]: h.Q(c) for i, c, _ in raw},
            {rows[int(i)]: h.Q(c) for i, _, c in raw})
    validate_field_dual(dual, corrections, target)
    assert list(map(h.Q, data['target_value'])) == [1, 0]
    mutations = 0
    for index, _, _ in raw:
        mono = rows[int(index)]
        for component in (0, 1):
            altered = (dict(dual[0]), dict(dual[1]))
            altered[component][mono] += 1
            mutations += h.require_failure(lambda: validate_field_dual(altered, corrections, target))
        altered = (dict(dual[0]), dict(dual[1]))
        altered[0].pop(mono)
        altered[1].pop(mono)
        mutations += h.require_failure(lambda: validate_field_dual(altered, corrections, target))
    return {'status': 'PASS', 'packet_sha256': h.lf_sha(path),
            'arithmetic': 'Rational dot products on constant/t coefficient polynomials; no import of the quadratic-field construction code.',
            'correction_columns_checked': len(corrections),
            'exact_zero_field_pairings': len(corrections), 'target_field_pairing': ['1', '0'],
            'functional_support_monomials': [list(rows[int(i)]) for i, _, _ in raw],
            'mutations_rejected': mutations,
            'conclusion': 'The same exact obstruction excludes both embeddings of Q[t]/(5t^2-8t+8) into C, including every shared Koszul correction and unrestricted quotient.'}


def full_quadratics(ds, ns):
    pairs = list(itertools.combinations_with_replacement(range(len(ds)), 2))
    cols = []
    for i, j in pairs:
        col = h.B(ds[i], ns[j])
        if i != j:
            h.add(col, h.B(ds[j], ns[i]))
        cols.append(col)
    return pairs, cols


def modular_probe(repo):
    start = time.perf_counter()
    f, a, ds, ns, ks, jac, labels, fields, bindings, path = reconstruct(repo)
    pairs, cols = full_quadratics(ds, ns)
    jb = h.echelon(jac)
    residuals = [h.reduce_mod(c, jb) for c in cols]
    allowed, steps = list(range(38)), []
    while True:
        active = [i for i, (a, b) in enumerate(pairs) if a in allowed and b in allowed]
        rows = {}
        for c in active:
            for m, v in residuals[c].items():
                rows.setdefault(m, {})[c] = v
        rb = h.echelon(rows.values())
        forced = [i for i in allowed if not h.reduce_mod({pairs.index((i, i)): 1}, rb)]
        steps.append({'allowed_parameters': allowed, 'active_quadratic_columns': len(active),
                      'rank_mod_p': len(rb), 'squares_in_rowspace_mod_p': forced})
        if not forced:
            break
        allowed = [i for i in allowed if i not in forced]
    def text_poly(poly):
        return str(s.factor(sum(s.Rational(c.numerator, c.denominator) * s.prod(x**n for x, n in zip(h.SYMS, m))
                                for m, c in poly.items())))
    return {'instance': 'mixed-biweight', 'status': 'modular_exploration_complete',
            'source_sha256': bindings, 'degree6_E1_sha256': h.lf_sha(path), 'prime': h.P,
            'parameter_labels': [list(label) for label in labels],
            'full_E1_dimension': 39, 'parameters_after_F_gauge': len(ds),
            'Koszul_fields': len(ks), 'Koszul_rank_mod_p': 315, 'J12_rank_mod_p': len(jb),
            'exact_E1_lift_identities': len(ds), 'exact_divergence_identities': len(ks),
            'quadratic_column_pairs': list(map(list, pairs)), 'steps': steps,
            'remaining_parameters': allowed,
            'extra_representatives': [{'kernel_index': index, 'D': text_poly(ds[35+i]),
                                       'N': [text_poly(n) for n in ns[35+i]]}
                                      for i, index in enumerate((17, 29, 30))],
            'scope': 'All three extra E1 directions are included. Modular square consequences are strategy diagnostics until rational physical duals are separately checked.',
            'seconds': time.perf_counter() - start}


def main():
    if not __debug__:
        raise RuntimeError('Run without -O: checks use assertions.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('repo', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    data = modular_probe(args.repo)
    data['exact_quotient_audit'] = check_quotient(args.repo)
    data['exact_diagonal_audit'] = check_diagonal(args.repo)
    data['exact_quadratic_field_audit'] = check_field_obstruction(args.repo)
    data['status'] = 'PASS'
    data['conclusion'] = 'No admissible degree-six denominator for the fixed mixed-biweight target: the complete E1 family is reduced by exact identities to two conjugate candidates, both excluded by the shared-K obstruction.'
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('w', encoding='utf-8', newline='\n') as stream:
        stream.write(json.dumps(data, indent=2) + '\n')
    print(json.dumps({k: v for k, v in data.items() if k not in ('quadratic_column_pairs', 'source_sha256', 'extra_representatives')}, indent=2))


if __name__ == '__main__':
    main()

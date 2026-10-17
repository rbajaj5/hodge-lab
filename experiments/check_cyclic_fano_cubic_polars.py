#!/usr/bin/env python3
"""Independent, source-based audit of degree-eight cubic-direction polars.

Only earlier independent arithmetic is imported. Projection is checked as an
identity of first-order operators on every base polynomial E, not as sampling.
"""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
from array import array
import argparse
import copy
import gzip
import hashlib
import json
import random
import sys
import time

import check_cyclic_fano_linear_polars as L

A = L.A
BASE = L.BASE
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/cyclic-fano-cubic-polars'
ZERO, ONE = A.ZERO, A.ONE
times, decode = L.times, L.decode
CUBICS = tuple(sorted((m for m in A.monomials(3) if not m[2]), reverse=True))
QUADRATICS = tuple(sorted(A.monomials(2), reverse=True))
PARAMETERS = tuple((i, m) for i in BASE for m in CUBICS)


def apply_operator(operator, polynomial):
    assert len(operator) == 6
    return A.add(A.mul(operator[0], polynomial), A.total(
        A.mul(coefficient, A.derivative(polynomial, i))
        for i, coefficient in zip(BASE, operator[1:])))


def degree(polynomial):
    return {sum(w * e for w, e in zip(A.WEIGHTS, m)) for m in polynomial}


def derive():
    assert len(CUBICS) == 35 and len(QUADRATICS) == 15 and len(PARAMETERS) == 175
    F, alpha, G, beta = A.target()
    q, h, delta = L.C.split_G(G)
    gradient = [A.derivative(G, i) for i in range(6)]
    dg = [A.derivative(delta, i) for i in range(6)]
    denominators, fields, divergences = [], [], []
    for i, m in PARAMETERS:
        f = {m: ONE}
        e = A.mul(f, dg[i])
        p = [{} for _ in range(6)]
        p[i] = times(A.mul(beta, f), -4)
        p[2] = times(A.mul(A.mul(beta, f), A.derivative(q, i)), 2)
        assert degree(e) == {8} and all(not powers[2] for powers in e)
        assert A.contraction(p, G) == A.mul(beta, e)
        assert A.contraction(A.lift(p), F) == A.mul(alpha, A.pullback(e))
        assert not A.add(times(p[2], 2), A.total(A.mul(A.derivative(q, k), p[k]) for k in BASE))
        div = times(A.derivative(A.mul(beta, f), i), -4)
        assert A.divergence(p) == div
        denominators.append(e); fields.append(p); divergences.append(div)

    labels, operators = [], []
    for i, j in combinations(BASE, 2):
        for m in QUADRATICS:
            f = {m: ONE}
            operator = [{} for _ in range(6)]
            operator[0] = A.add(A.mul(dg[i], A.derivative(f, j)),
                                times(A.mul(dg[j], A.derivative(f, i)), -1))
            operator[1 + BASE.index(i)] = A.mul(f, dg[j])
            operator[1 + BASE.index(j)] = times(A.mul(f, dg[i]), -1)
            labels.append(dict(kind='quadratic_base_pair', pair=[i, j], multiplier_powers=list(m)))
            operators.append(operator)
    for i in BASE:
        for k in BASE:
            f = L.monomial(k)
            operator = [{} for _ in range(6)]
            operator[0] = A.add(A.mul(f, dg[i]),
                                times(A.mul(delta, A.derivative(f, i)), 2))
            operator[1 + BASE.index(i)] = times(A.mul(f, delta), -2)
            labels.append(dict(kind='linear_t_mixed', coordinate=i, linear_coordinate=k))
            operators.append(operator)
    assert len(operators) == 175

    # On weight-eight E, 25 independent Euler relations express every mixed
    # column through the first150 columns. This is an exact rank upper bound.
    relations = []
    for i in BASE:
        for k in BASE:
            coefficients = []
            for j in BASE:
                if j == i:
                    continue
                m = [0] * 6; m[j] += 1; m[k] += 1
                label = dict(kind='quadratic_base_pair', pair=sorted([i, j]), multiplier_powers=m)
                coefficients.append((labels.index(label), Q(1 if i < j else -1)))
            mixed_index = labels.index(dict(kind='linear_t_mixed', coordinate=i, linear_coordinate=k))
            coefficients.append((mixed_index, Q(3)))
            actual = [A.total(times(operators[n][slot], c) for n, c in coefficients) for slot in range(6)]
            factor = A.mul(L.monomial(k), dg[i])
            expected = [times(factor, 8)] + [times(A.mul(factor, L.monomial(j)), -1) for j in BASE]
            assert actual == expected
            relations.append(dict(coordinate=i, linear_coordinate=k,
                                  coefficients=[[n, str(c)] for n, c in coefficients]))
    assert len(relations) == 25
    assert [row['coefficients'][-1] for row in relations] == [[150 + j, '3'] for j in range(25)]

    raw, raw_operators = [], []
    for i, j in combinations(range(6), 2):
        for m in A.monomials(A.WEIGHTS[i] + A.WEIGHTS[j]):
            f = {m: ONE}
            field = [{} for _ in range(6)]
            field[i] = A.mul(f, gradient[j])
            field[j] = times(A.mul(f, gradient[i]), -1)
            assert not A.contraction(field, G)
            if 2 not in (i, j):
                label = dict(kind='quadratic_base_pair', pair=[i, j], multiplier_powers=list(m))
                n = labels.index(label); factor = Q(1, 4)
            elif m[2]:
                assert m[2] == 1
                k = next(k for k in BASE if m[k])
                assert sum(m) == 2
                other = j if i == 2 else i
                n = labels.index(dict(kind='linear_t_mixed', coordinate=other, linear_coordinate=k))
                factor = Q(-1 if i == 2 else 1, 4)
            else:
                n, factor = None, Q(0)
            # B_E(K)=E div(K)-sum K_i*d_i E, for any base polynomial E.
            actual = [L.even_projection(A.divergence(field), q, h)]
            actual += [times(L.even_projection(field[k], q, h), -1) for k in BASE]
            expected = [{} for _ in range(6)] if n is None else [times(p, factor) for p in operators[n]]
            assert actual == expected, (i, j, m)
            raw.append(dict(pair=[i, j], multiplier_powers=list(m),
                            compact_generator_index=n, compact_scale=str(factor)))
            raw_operators.append(actual)
    assert len(raw) == 525
    assert sum(e['compact_generator_index'] is not None for e in raw) == 175

    quotient = A.monomials(8)
    assert len(quotient) == 636
    for m in quotient:
        assert not L.even_projection(A.mul({m: ONE}, G), q, h)
    euler = A.monomials(6)
    assert len(euler) == 246
    for m in euler:
        R = {m: ONE}; normalizer = []
        for i, w in enumerate(A.WEIGHTS):
            n = list(m); n[i] += 1
            normalizer.append({tuple(n): (Q(w, 6), Q(0))})
        assert A.contraction(normalizer, G) == A.mul(R, G)
        assert A.divergence(normalizer) == times(R, Q(14, 6))
        # Each E has weight8: N(E)=8 R E/6, hence B_E(N)=R E.
    for e in denominators:
        assert A.total(times(A.mul(L.monomial(i), A.derivative(e, i)), w)
                       for i, w in enumerate(A.WEIGHTS)) == times(e, 8)

    injection_rows = [tuple(a + 5 * int(j == i) for j, a in enumerate(m)) for i, m in PARAMETERS]
    assert len(set(injection_rows)) == 175
    for i, m in enumerate(injection_rows):
        assert [A.mod5(e).get(m, 0) for e in denominators] == [int(i == j) for j in range(175)]
    assert A.mod5(F) == {tuple(6 * int(i == j) for j in range(6)): 1 for i in range(6)}
    return dict(F=F, G=G, Q=q, H=h, Delta=delta, beta=beta,
                denominators=denominators, fields=fields, divergences=divergences,
                compact_labels=labels, operators=operators, raw_labels=raw,
                homogeneous_degree8_relations=relations,
                raw_operators=raw_operators,
                quotient_monomials=quotient, euler_monomials=euler, injection_rows=injection_rows)


def check_operator_coverage(exact, labels, operators):
    assert labels == exact['raw_labels'] and len(labels) == 525 and len(operators) == 175
    for label, actual in zip(labels, exact['raw_operators']):
        n, factor = label['compact_generator_index'], Q(label['compact_scale'])
        expected = [{} for _ in range(6)] if n is None else [times(p, factor) for p in operators[n]]
        assert actual == expected


def source_negative_controls(exact):
    cases = []
    bad = copy.deepcopy(exact['operators'])
    n = exact['compact_labels'].index(dict(kind='linear_t_mixed', coordinate=BASE[0], linear_coordinate=BASE[0]))
    bad[n][0] = A.add(bad[n][0], times(exact['Delta'], -2))
    cases.append(lambda: check_operator_coverage(exact, exact['raw_labels'], bad))
    cases.append(lambda: check_operator_coverage(exact, exact['raw_labels'][:-1], exact['operators']))
    field = copy.deepcopy(exact['fields'][0])
    field[BASE[0]] = {}
    def check_e1():
        assert A.contraction(field, exact['G']) == A.mul(exact['beta'], exact['denominators'][0])
    cases.append(check_e1)
    def check_missing_quotient():
        remaining = [m for m in exact['quotient_monomials'] if m[2] < 2]
        assert remaining == A.monomials(8)
    cases.append(check_missing_quotient)
    def check_wrong_degree():
        wrongly_weighted_cubics = A.monomials(3)
        assert len(wrongly_weighted_cubics) == 35 and all(not m[2] for m in wrongly_weighted_cubics)
    cases.append(check_wrong_degree)
    assert all(A.I.rejects(fn) for fn in cases)
    return len(cases)


def physical_system(exact, active):
    active = list(active)
    assert active == sorted(set(active)) and all(p in range(175) for p in active)
    keys, columns = [], []
    for position, p in enumerate(active):
        i, m = PARAMETERS[p]
        f = {m: ONE}
        for r in active[position:]:
            j, n = PARAMETERS[r]
            g = {n: ONE}
            physical = A.B(exact['denominators'][r], exact['fields'][p])
            first = A.mul(exact['beta'], A.mul(f, A.derivative(exact['denominators'][r], i)))
            second = A.mul(A.derivative(A.mul(exact['beta'], f), i), exact['denominators'][r])
            if p != r:
                physical = A.add(physical, A.B(exact['denominators'][p], exact['fields'][r]))
                first = A.add(first, A.mul(exact['beta'], A.mul(g, A.derivative(exact['denominators'][p], j))))
                second = A.add(second, A.mul(A.derivative(A.mul(exact['beta'], g), j), exact['denominators'][p]))
            assert physical == times(A.add(first, times(second, -1)), 4)
            assert all(not powers[2] and sum(powers) == 14 for powers in physical)
            keys.append(('a*a', p, r)); columns.append(physical)
    for p in active:
        for n, operator in enumerate(exact['operators']):
            image = apply_operator(operator, exact['denominators'][p])
            assert all(not powers[2] and sum(powers) == 14 for powers in image)
            keys.append(('a*c', p, n)); columns.append(image)
    return dict(active=active, keys=keys, columns=columns, rows=L.columns_to_rows(columns))


def reduce_row(row, pivots, prime=None):
    row = dict(row)
    while row:
        pivot = min(row)
        if pivot not in pivots:
            return row
        value = row[pivot]
        for j, coefficient in pivots[pivot].items():
            updated = row.get(j, 0) - value * coefficient
            if prime is not None:
                updated %= prime
            if updated:
                row[j] = updated
            else:
                row.pop(j, None)
    return row


def combine_spatial_rows(dual, rows):
    result = {}
    for m, (coefficient, imag) in dual.items():
        assert imag == 0 and m in rows
        for j, value in rows[m].items():
            updated = result.get(j, Q(0)) + coefficient * value
            if updated:
                result[j] = updated
            else:
                result.pop(j, None)
    return result


def audit_component(family, exact):
    assert family['status'] == 'completed'
    component = family['component_index']
    assert component in range(5) and family['component'] == BASE[component]
    active = list(range(35 * component, 35 * (component + 1)))
    checks, duals, pairings, dual_terms = [], 0, 0, 0
    for step, stage in enumerate(family['stages']):
        assert stage['active_raw_parameter_indices'] == active and active
        system = physical_system(exact, active)
        assert stage['rows'] == len(system['rows'])
        assert stage['columns'] == len(system['columns']) == len(active) * (len(active) + 1) // 2 + 175 * len(active)
        pivots = L.row_basis(system['rows'])
        assert stage['rank'] == len(pivots)
        forced = [p for p in active if not reduce_row(
            {system['keys'].index(('a*a', p, p)): Q(1)}, pivots)]
        assert [entry['raw_parameter_index'] for entry in stage['square_duals']] == forced
        for entry in stage['square_duals']:
            p = entry['raw_parameter_index']
            dual = decode(entry['dual'])
            assert dual and all(sum(m) == 14 and not m[2] for m in dual)
            target = system['keys'].index(('a*a', p, p))
            assert combine_spatial_rows(dual, system['rows']) == {target: Q(1)}
            duals += 1; pairings += len(system['columns']); dual_terms += len(dual)
        checks.append(dict(active_raw_parameter_indices=active, rows=len(system['rows']),
                           columns=len(system['columns']), exact_rank=len(pivots),
                           exactly_forced_square_indices=forced))
        active = [p for p in active if p not in forced]
        if not active or not forced:
            assert step == len(family['stages']) - 1
    assert family['remaining_raw_parameter_indices'] == active
    assert family['conclusion'] == ('excluded' if not active else 'unresolved')
    return dict(component=family['component'], status='PASS', stages=checks,
                square_identities=duals, physical_coefficient_pairings=pairings,
                dual_nonzero_terms=dual_terms, remaining_raw_parameter_indices=active,
                conclusion=family['conclusion'])


def pair_equations(packet):
    n = len(packet['active_raw_parameter_indices'])
    equations = []
    for entry in packet['equations']:
        row = {}
        for i, j, coefficient in entry['terms']:
            assert 0 <= i <= j < n and (i, j) not in row and Q(coefficient)
            row[i, j] = Q(coefficient)
        assert row
        equations.append(row)
    return equations


def audit_necessary(packet, exact):
    active = packet['active_raw_parameter_indices']
    system = physical_system(exact, active)
    assert packet['rows'] == len(system['rows']) and packet['columns'] == len(system['columns'])
    pure_count = len(active) * (len(active) + 1) // 2
    physical_basis = L.row_basis(system['rows'])
    full_rank = len(physical_basis)
    squares = [p for p in active if not reduce_row(
        {system['keys'].index(('a*a', p, p)): Q(1)}, physical_basis)]
    correction_rows = {m: {j: c for j, c in row.items() if j >= pure_count}
                       for m, row in system['rows'].items()}
    mixed_rank = len(L.row_basis(correction_rows))
    assert packet['rank'] == full_rank and packet['mixed_rank'] == mixed_rank
    equations = pair_equations(packet)
    assert len(equations) == full_rank - mixed_rank
    dual_terms = 0
    altered_dual_rejected = False
    for entry, equation in zip(packet['equations'], equations):
        dual = decode(entry['dual'])
        assert dual and all(not m[2] and sum(m) == 14 for m in dual)
        expected = {system['keys'].index(('a*a', active[i], active[j])): c
                    for (i, j), c in equation.items()}
        assert combine_spatial_rows(dual, system['rows']) == expected
        if not altered_dual_rejected:
            altered = dict(dual)
            monomial = next(iter(altered))
            coefficient = altered[monomial]
            altered[monomial] = (coefficient[0] + 1, coefficient[1])
            assert combine_spatial_rows(altered, system['rows']) != expected
            altered_dual_rejected = True
        dual_terms += len(dual)
    assert len(L.row_basis(dict(enumerate(equations)))) == len(equations)
    return dict(status='PASS', rows=len(system['rows']), columns=len(system['columns']),
                exact_square_consequences_raw=squares, altered_physical_dual_rejected=altered_dual_rejected,
                rank=full_rank, correction_rank=mixed_rank,
                necessary_quadrics=len(equations), dual_nonzero_terms=dual_terms,
                physical_coefficient_pairings=len(equations) * len(system['columns']))


def audit_reduced_basis(original, reduced):
    assert reduced['active_raw_parameter_indices'] == original['active_raw_parameter_indices']
    old, new = pair_equations(original), pair_equations(reduced)
    assert len(old) == len(new)
    combination_terms = 0
    for entry, expected in zip(reduced['equations'], new):
        result = {}
        combination = entry['combination']
        assert len({i for i, c in combination}) == len(combination)
        for i, coefficient in combination:
            assert i in range(len(old)) and Q(coefficient)
            for pair, value in old[i].items():
                updated = result.get(pair, Q(0)) + Q(coefficient) * value
                if updated:
                    result[pair] = updated
                else:
                    result.pop(pair, None)
        assert result == expected
        combination_terms += len(combination)
    pivots = [min(row) for row in new]
    assert pivots == sorted(set(pivots))
    for p, row in zip(pivots, new):
        assert row[p] == 1 and set(row).intersection(pivots) == {p}
    singleton_squares = [i for i in range(len(original['active_raw_parameter_indices']))
                         if {(i, i): Q(1)} in new]
    bad = copy.deepcopy(reduced)
    q, c = bad['equations'][0]['combination'][0]
    bad['equations'][0]['combination'][0] = [q, str(Q(c) + 1)]
    first = {}
    for q, c in bad['equations'][0]['combination']:
        for pair, v in old[q].items():
            first[pair] = first.get(pair, Q(0)) + Q(c) * v
    assert {k: v for k, v in first.items() if v} != new[0]
    return dict(status='PASS', equivalent_basis_rank=len(new),
                singleton_square_parameters_raw=[original['active_raw_parameter_indices'][i] for i in singleton_squares],
                altered_basis_combination_rejected=True,
                exact_linear_combinations=len(new), combination_terms=combination_terms,
                old_term_count=sum(map(len, old)), new_term_count=sum(map(len, new)))


def verify_cube(identity, equations, dimension):
    target = identity['parameter_index']
    assert target in range(dimension) and identity['power'] == 3
    result = {}
    for entry in identity['multipliers']:
        q, k = entry['equation_index'], entry['linear_variable']
        assert q in range(len(equations)) and k in range(dimension)
        coefficient = Q(entry['coefficient'])
        assert coefficient
        for pair, value in equations[q].items():
            m = tuple(sorted((*pair, k)))
            updated = result.get(m, Q(0)) + coefficient * value
            if updated:
                result[m] = updated
            else:
                result.pop(m, None)
    assert result == {(target,) * 3: Q(1)}


def audit_cubic(proof, reduced):
    active = reduced['active_raw_parameter_indices']
    assert proof['status'] == 'completed' and proof['active_raw_parameter_indices'] == active
    equations = pair_equations(reduced)
    selected = [i for i, q in enumerate(equations) if len(q) <= proof['term_threshold']]
    assert proof['equation_indices'] == selected
    rows = {(q, k): {tuple(sorted((*pair, k))): c for pair, c in equations[q].items()}
            for q in selected for k in range(len(active))}
    assert proof['columns'] == len(rows)
    pivots = L.row_basis(rows)
    assert proof['rank'] == len(pivots)
    found = [i for i in range(len(active)) if not reduce_row({(i,) * 3: Q(1)}, pivots)]
    assert [v['parameter_index'] for v in proof['identities']] == found
    for identity in proof['identities']:
        assert all(m['equation_index'] in selected for m in identity['multipliers'])
        verify_cube(identity, equations, len(active))
    bad = copy.deepcopy(proof['identities'][0])
    bad['multipliers'][0]['coefficient'] = str(Q(bad['multipliers'][0]['coefficient']) + 1)
    assert A.I.rejects(lambda: verify_cube(bad, equations, len(active)))
    return dict(status='PASS', altered_cube_multiplier_rejected=True, selected_quadrics=len(selected), multiplier_generators=len(rows),
                exact_rank=len(pivots), coordinate_cube_identities=len(found),
                multiplier_terms=sum(len(v['multipliers']) for v in proof['identities']),
                forced_raw_parameter_indices=[active[i] for i in found],
                remaining_raw_parameter_indices=[p for i, p in enumerate(active) if i not in found])


def audit_rebuild(previous, current):
    old_active, active = previous['active_raw_parameter_indices'], current['active_raw_parameter_indices']
    positions = {old_active.index(p): i for i, p in enumerate(active)}
    restricted = [{tuple(sorted((positions[i], positions[j]))): c for (i, j), c in q.items()
                   if i in positions and j in positions} for q in pair_equations(previous)]
    fresh = pair_equations(current)
    old_rank = len(L.row_basis(dict(enumerate(restricted))))
    basis = L.row_basis(dict(enumerate(fresh)))
    assert all(not reduce_row(row, basis) for row in restricted)
    return dict(restricted_old_rank=old_rank, rebuilt_rank=len(basis),
                additional_independent_quadrics=len(basis) - old_rank, span_inclusion=True)


def determinant_mod(matrix, prime):
    a = [list(row) for row in matrix]
    n = len(a)
    assert all(len(row) == n for row in a)
    determinant = 1
    for j in range(n):
        pivot = next((r for r in range(j, n) if a[r][j] % prime), None)
        if pivot is None:
            return 0
        if pivot != j:
            a[j], a[pivot] = a[pivot], a[j]
            determinant = -determinant
        value = a[j][j] % prime
        determinant = determinant * value % prime
        inverse = pow(value, -1, prime)
        for r in range(j + 1, n):
            factor = a[r][j] * inverse % prime
            if factor:
                for k in range(j + 1, n):
                    a[r][k] = (a[r][k] - factor * a[j][k]) % prime
            a[r][j] = 0
    return determinant % prime


def fixed_cases():
    rng = random.Random(202610178)
    result = [('monomial-control', {35 * i + i: Q(1)}) for i in range(5)]
    result += [('two-component', {35 * i + i: Q(1),
        35 * ((i + 1) % 5) + 34 - i: Q(-1 if i % 2 else 1)}) for i in range(5)]
    for i in range(6):
        support = rng.sample(range(175), 8 if i < 3 else 175)
        direction = {j: Q(rng.choice([-2, -1, 1, 2])) for j in support}
        result.append(('seeded-eight-term' if i < 3 else 'seeded-dense', direction))
    return result


def audit_gpu_minors(report, exact, check_bindings=True):
    assert report['status'] == 'PASS' and report['prime'] == 65521 and report['seed'] == 202610178
    prime = report['prime']
    assert all(prime % j for j in range(2, 256))
    assert report['correction_types'] == 175
    assert (report['cpu_checked_matrices'], report['constructed_consistent_controls'], report['toy_controls']) == (32, 16, 3)
    if check_bindings:
        for name, digest in report['bindings'].items():
            assert A.I.sha(ROOT / name.replace('\\', '/')) == digest
    assert len(report['cases']) == 16
    polynomials, cases = [], []
    for entry, (kind, direction) in zip(report['cases'], fixed_cases()):
        assert entry['kind'] == kind
        assert entry['direction'] == [[i, str(c)] for i, c in sorted(direction.items())]
        e = A.total(times(exact['denominators'][p], c) for p, c in direction.items())
        field = [A.total(times(exact['fields'][p][i], c) for p, c in direction.items()) for i in range(6)]
        assert e and decode(entry['denominator']) == e and degree(e) == {8}
        assert A.contraction(field, exact['G']) == A.mul(exact['beta'], e)
        columns = [apply_operator(operator, e) for operator in exact['operators']]
        for relation in exact['homogeneous_degree8_relations']:
            assert not A.total(times(columns[n], Q(c)) for n, c in relation['coefficients'])
        rhs = times(A.B(e, field), -1)
        assert all(not m[2] and sum(m) == 14 for p in columns + [rhs] for m in p)
        polynomials.append(columns + [rhs]); cases.append(entry)
    monomials = sorted(set().union(*(set(p) for cols in polynomials for p in cols)))
    assert report['spatial_rows'] == len(monomials)
    residue_cache = {Q(0): 0}
    def mod(c):
        assert c[1] == 0
        c = c[0]
        if c not in residue_cache:
            assert c.denominator % prime
            residue_cache[c] = c.numerator % prime * pow(c.denominator, -1, prime) % prime
        return residue_cache[c]
    checks = []
    for entry, columns in zip(cases, polynomials):
        matrix = array('q', (mod(column.get(m, ZERO)) for m in monomials for column in columns))
        assert matrix.itemsize == 8
        if sys.byteorder != 'little':
            matrix.byteswap()
        digest = hashlib.sha256(matrix.tobytes()).hexdigest()
        assert digest == entry['matrix_sha256']
        selected_rows = [tuple(m) for m in entry['augmented_minor_rows']]
        selected_columns = entry['augmented_minor_columns']
        assert len(selected_rows) == len(set(selected_rows)) == 151
        assert set(selected_rows) <= set(monomials)
        assert selected_columns == list(range(150)) + [175]
        minor = [[mod(columns[j].get(m, ZERO)) for j in selected_columns] for m in selected_rows]
        determinant = determinant_mod(minor, prime)
        assert determinant == entry['augmented_minor_determinant_mod_prime'] and determinant
        assert entry['rank_mod_prime'] == 150 and entry['augmented_rank_mod_prime'] == 151
        assert entry['consistent_control_ranks'] == [150, 150] and entry['modular_inconsistent'] is True
        # Nonzero reduction of this minor proves augmented rank>=151 over Q.
        # The25 exact, independent relations prove coefficient rank<=150.
        checks.append(dict(kind=entry['kind'], matrix_sha256=digest,
                           exact_column_relations=25, rational_rank_upper_bound=150,
                           augmented_minor_size=151, nonzero_determinant_mod_prime=determinant,
                           conclusion='Fixed denominator excluded over Q and C.'))
    return dict(status='PASS', prime=prime, cases=checks,
                matrix_hashes_reconstructed=16, exact_column_relations_replayed=400,
                nonzero_minors_checked=16, GPU_required_for_this_replay=False,
                scope='Five monomial controls and eleven fixed mixed/seeded directions; no mixed-family exclusion.')



def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.suffix == '.gz' else A.I.sha(path)


def load_bound(name, digest):
    assert Path(name).name == name
    path = OUT / name
    assert file_hash(path) == digest
    content = gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes()
    return json.loads(content)


def audit_projection(packet, exact):
    raw = [dict(pair=e['pair'], multiplier_powers=e['multiplier_powers'],
                compact_index=e['compact_generator_index'], compact_scale=e['compact_scale'])
           for e in exact['raw_labels']]
    relations = [dict(coordinate=e['coordinate'], linear_coordinate=e['linear_coordinate'],
                      terms=e['coefficients']) for e in exact['homogeneous_degree8_relations']]
    assert len(packet['raw_field_labels']) == 525
    canonical = lambda entry: (entry['pair'], entry['multiplier_powers'])
    assert sorted(packet['raw_field_labels'], key=canonical) == sorted(raw, key=canonical)
    assert packet['compact_labels'] == exact['compact_labels']
    assert sorted(packet['quotient_monomials']) == sorted(list(m) for m in exact['quotient_monomials'])
    assert packet['universal_correction_relations'] == relations
    assert packet['injectivity_rows_mod5'] == [list(m) for m in exact['injection_rows']]
    for key, expected in [('raw_field_count', 525), ('operator_coefficient_checks', 3150),
                          ('compact_count', 175), ('Euler_gauge_count', 246),
                          ('denominator_homogeneity_checks', 175),
                          ('Euler_identity_count_implied', 43050), ('correction_rank_upper_bound', 150)]:
        assert packet[key] == expected
    assert packet['injectivity_minor_mod5'] == 'identity175'
    return dict(status='PASS', parameters=175, exact_E1_lifts=175, Piola_lifts=175,
                raw_Koszul_fields=525, operator_coefficient_identities=3150,
                retained_correction_types=175, universal_correction_relations=25,
                exact_correction_rank_upper_bound=150, quotient_directions=636,
                Euler_gauges=246, denominator_homogeneity_identities=175,
                implied_Euler_normalization_identities=43050, injection_minor_size=175,
                injection_minor_mod5=1,
                completeness='All weighted homogeneous raw Koszul fields and quotient directions are covered; even projection gives necessary equations.')


def audit_packet_header(packet, exact):
    assert packet['schema'] == 'cyclic-fano-cubic-polars-v1'
    assert packet['status'] == 'five_component_families_excluded_full_family_open'
    assert packet['instance'] == 'cyclic-triple-fano' and packet['q'] == 1 and packet['degree'] == 8
    assert packet['source_commit'] == 'd96911d725077e66a8f10848908be01a643b1714'
    source = ROOT / 'results/cyclic-fano-curve/source/instance.rec'
    assert packet['source_instance_sha256'] == A.I.sha(source) == 'd99d10c84d25dc5def72cd7a9a17e5d022e18f562660c8e33bf106675b4a418c'
    assert packet['producer_sha256'] == A.I.sha(ROOT / 'experiments/cyclic_fano_cubic_polars.py')
    for name, digest in packet['dependencies'].items():
        assert Path(name).name == name and A.I.sha(ROOT / 'experiments' / name) == digest
    assert packet['spatial_variables'] == ['X0', 'X1', 'Z', 'Y0', 'Y1', 'Y2']
    assert packet['base_variables'] == [packet['spatial_variables'][i] for i in BASE]
    for key in ['Delta', 'Q', 'H', 'beta']:
        assert decode(packet[key]) == exact[key]
    assert len(packet['parameter_basis']) == 175
    for k, (entry, (i, m)) in enumerate(zip(packet['parameter_basis'], PARAMETERS)):
        assert entry['component'] == i and entry['cubic_powers'] == list(m)
        assert decode(entry['E']) == exact['denominators'][k]
        assert list(map(decode, entry['particular'])) == exact['fields'][k]
    assert packet['full_family_dimensions'] == dict(parameters=175, potential_rows=3060,
        pure_quadratic_columns=15400, mixed_columns=30625, formal_columns=46025,
        full_map_constructed=False)
    return audit_projection(packet['projection'], exact)


def audit_inventory(packet, components, loaded, exact):
    expected = {'projection-probe.json'}
    for i in range(5):
        expected.update({f'component-{i}-probe.json', f'component-{i}-necessary-summary.json',
                         f'component-{i}-cubic-64.json', f'component-{i}-round-01-necessary-summary.json',
                         f'component-{i}-round-01-cubic-64.json'})
    assert len(packet['attempts']) == len(expected) == 26
    assert {entry['file'] for entry in packet['attempts']} == expected
    records = []
    for entry in packet['attempts']:
        assert entry['status'] == 'completed'
        data = load_bound(entry['file'], entry['sha256'])
        name = entry['file']
        if name == 'projection-probe.json':
            audit_projection(data, exact)
        elif name in loaded:
            assert data == loaded[name]
        else:
            i = int(name.split('-')[1])
            stage = components[i]['stages'][int('round-01' in name)]
            physical = stage['physical']
            if name.endswith('-probe.json'):
                active = list(range(35 * i, 35 * (i + 1)))
                assert data['status'] == 'completed' and data['component_index'] == i
                assert data['component'] == BASE[i] and data['remaining_raw_parameter_indices'] == active
                assert data['conclusion'] == 'unresolved' and len(data['stages']) == 1
                stored = data['stages'][0]
                assert stored['active_raw_parameter_indices'] == active and stored['square_duals'] == []
                assert physical['exact_square_consequences_raw'] == []
                for key in ['rows', 'columns', 'rank']:
                    assert stored[key] == physical[key]
            else:
                assert data['status'] == 'completed' and data['component'] == i
                for key in ['rows', 'columns', 'rank']:
                    assert data[key] == physical[key]
                assert data['mixed_rank'] == physical['correction_rank']
                assert data['quadrics'] == physical['necessary_quadrics']
        records.append(dict(file=name, sha256=entry['sha256'], status='PASS'))
    return dict(status='PASS', checked_records=26, records=records,
                initial_square_searches_without_consequences=5,
                timeouts=0, scope='Initial exact rowspace misses are preserved; subsequent multipliers close only each component family.')


def aggregate(packet, exact):
    started = time.perf_counter()
    projection = audit_packet_header(packet, exact)
    controls = source_negative_controls(exact)
    bad = copy.deepcopy(packet)
    bad['source_instance_sha256'] = '0' * 64
    assert A.I.rejects(lambda: audit_packet_header(bad, exact))
    controls += 1
    bad_projection = copy.deepcopy(packet['projection'])
    bad_projection['universal_correction_relations'][0]['terms'][-1][1] = '4'
    assert A.I.rejects(lambda: audit_projection(bad_projection, exact))
    controls += 1
    assert len(packet['component_families']) == 5
    families, loaded = [], {}
    for i, family in enumerate(packet['component_families']):
        assert family['component_index'] == i and family['component'] == BASE[i]
        assert family['base_name'] == packet['base_variables'][i]
        assert len(family['stages']) == 2
        active = list(range(35 * i, 35 * (i + 1)))
        previous = None
        stages = []
        for step, entry in enumerate(family['stages']):
            assert entry['round'] == step and entry['parameters'] == len(active)
            physical = load_bound(entry['physical_file'], entry['physical_sha256'])
            reduced = load_bound(entry['reduced_file'], entry['reduced_sha256'])
            cubic = load_bound(entry['cubic_file'], entry['cubic_sha256'])
            loaded[entry['cubic_file']] = cubic
            assert physical['active_raw_parameter_indices'] == active
            check = audit_necessary(physical, exact)
            assert (entry['physical_rows'], entry['physical_columns'], entry['rank'],
                    entry['mixed_rank'], entry['necessary_quadrics']) == (
                check['rows'], check['columns'], check['rank'], check['correction_rank'], check['necessary_quadrics'])
            basis_check = audit_reduced_basis(physical, reduced)
            cubic_check = audit_cubic(cubic, reduced)
            assert entry['forced_raw_parameters'] == cubic_check['forced_raw_parameter_indices']
            if step == 0:
                assert len(active) == 35 and check['exact_square_consequences_raw'] == []
                assert cubic_check['coordinate_cube_identities'] == 25
            else:
                assert len(active) == 10
                assert check['exact_square_consequences_raw'] == active
                assert basis_check['singleton_square_parameters_raw'] == active
                assert cubic_check['coordinate_cube_identities'] == cubic_check['multiplier_terms'] == 10
                rebuild = audit_rebuild(previous, physical)
                assert family['rebuild_diagnostic'] == dict(
                    restricted_old_rank=rebuild['restricted_old_rank'], fresh_rebuilt_rank=rebuild['rebuilt_rank'],
                    additional_independent_quadrics=rebuild['additional_independent_quadrics'],
                    span_inclusion=rebuild['span_inclusion'])
                assert rebuild['restricted_old_rank'] == rebuild['rebuilt_rank'] == 45
            controls += 3  # Altered physical dual, equivalent basis combination, and cubic multiplier.
            stages.append(dict(round=step, active_raw_parameter_indices=active,
                physical_file=entry['physical_file'], physical_sha256=entry['physical_sha256'],
                reduced_file=entry['reduced_file'], reduced_sha256=entry['reduced_sha256'],
                cubic_file=entry['cubic_file'], cubic_sha256=entry['cubic_sha256'],
                physical=check, basis=basis_check, cubic=cubic_check))
            active = cubic_check['remaining_raw_parameter_indices']
            previous = physical
            print(f'PASS component {i}, round {step}: {len(stages[-1]["active_raw_parameter_indices"])} parameters; rank {check["rank"]}; {check["necessary_quadrics"]} quadrics; {cubic_check["coordinate_cube_identities"]} cubes', flush=True)
        assert active == family['remaining_raw_parameter_indices'] == []
        assert family['conclusion'] == 'excluded conditionally on the other four vector components being zero'
        families.append(dict(status='PASS', component_index=i, component=BASE[i], base_name=family['base_name'],
                             stages=stages, rebuild_diagnostic=rebuild, remaining_raw_parameter_indices=[],
                             conclusion=family['conclusion']))
    inventory = audit_inventory(packet, families, loaded, exact)
    gpu_path = ROOT / 'results/cyclic-fano-cubic-gpu/report.json'
    gpu = json.loads(gpu_path.read_text(encoding='utf-8'))
    gpu_check = audit_gpu_minors(gpu, exact)
    # The determinant is checked by fresh elimination, not trusted from the GPU.
    for case, checked in zip(gpu['cases'], gpu_check['cases']):
        altered = (case['augmented_minor_determinant_mod_prime'] + 1) % gpu['prime']
        assert altered != checked['nonzero_determinant_mod_prime']
    controls += 16
    totals = dict(
        physical_consequences=sum(s['physical']['necessary_quadrics'] for f in families for s in f['stages']),
        physical_coefficient_pairings=sum(s['physical']['physical_coefficient_pairings'] for f in families for s in f['stages']),
        physical_dual_terms=sum(s['physical']['dual_nonzero_terms'] for f in families for s in f['stages']),
        equivalent_basis_combinations=sum(s['basis']['exact_linear_combinations'] for f in families for s in f['stages']),
        coordinate_cube_identities=sum(s['cubic']['coordinate_cube_identities'] for f in families for s in f['stages']),
        multiplier_terms=sum(s['cubic']['multiplier_terms'] for f in families for s in f['stages']),
        final_singleton_square_rows=sum(len(f['stages'][1]['basis']['singleton_square_parameters_raw']) for f in families))
    assert totals['physical_consequences'] == totals['equivalent_basis_combinations'] == 1269
    assert totals['physical_coefficient_pairings'] == 7458345
    assert totals['coordinate_cube_identities'] == 175 and totals['multiplier_terms'] == 344
    assert totals['final_singleton_square_rows'] == 50
    independent_dependencies = {}
    for module in list(sys.modules.values()):
        file = getattr(module, '__file__', None)
        if file:
            path = Path(file).resolve()
            if path.parent == ROOT / 'experiments' and path.name.startswith('check_') and path != Path(__file__).resolve():
                independent_dependencies[path.relative_to(ROOT).as_posix()] = A.I.sha(path)
    assert independent_dependencies
    return dict(schema='cyclic-fano-cubic-polars-independent-v1', status='PASS',
        source_commit=packet['source_commit'], source_instance_sha256=packet['source_instance_sha256'],
        primary_packet_sha256=A.I.sha(OUT / 'packet.json'), primary_producer_sha256=packet['producer_sha256'],
        primary_dependencies=packet['dependencies'], checker_sha256=A.I.sha(Path(__file__)),
        independent_dependencies=independent_dependencies,
        source_projection=projection, component_families=families, attempts=inventory,
        fixed_direction_minor_audit=gpu_check, gpu_report_lf_sha256=A.I.sha(gpu_path),
        totals=totals, altered_inputs_rejected=controls, elapsed_seconds=round(time.perf_counter()-started,3),
        scope=['Five separate 35-parameter component families are excluded over C, each with the other four components zero.',
               'The five remaining ten-parameter stages already have individual square rows; their one-term cubic witnesses are not minimal-degree claims.',
               'All sixteen fixed degree-eight denominators are excluded by an exact rank upper bound and verified modular nonzero minors. Five are controls, eleven are fixed mixed or seeded tests.',
               'The full mixed 175-parameter cubic-direction family remains open. No existence certificate, support construction, Lean proof or instance solve is claimed.'])


def main():
    assert __debug__, 'Run without -O'
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-only', action='store_true')
    parser.add_argument('--output', type=Path, default=OUT / 'independent-validation.json')
    args = parser.parse_args()
    exact = derive()
    if args.source_only:
        print(json.dumps(dict(status='PASS', parameters=175, raw_Koszul_fields=525,
            exact_projection_operator_coefficients=3150, correction_types=175, quotient_directions=636,
            universal_column_relations=25, exact_rank_upper_bound=150, Euler_gauges=246,
            source_negative_controls_rejected=source_negative_controls(exact))), flush=True)
        return
    packet = json.loads((OUT / 'packet.json').read_text(encoding='utf-8'))
    result = aggregate(packet, exact)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(status=result['status'], totals=result['totals'],
                         altered_inputs_rejected=result['altered_inputs_rejected'],
                         fixed_minors=result['fixed_direction_minor_audit']['nonzero_minors_checked'],
                         elapsed_seconds=result['elapsed_seconds'], output=str(args.output))), flush=True)


if __name__ == '__main__':
    main()

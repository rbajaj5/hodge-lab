#!/usr/bin/env python3
"""Separate reconstruction of the cyclic-triple-fano fixed evaluation fiber.

Uses the quadratic-in-Z recurrence, not the producer's sequential equation
solver. Rebuilds the homogeneous multiplier columns from the protected F.
The finite-field determinant certifies a nonzero characteristic-zero minor;
the exploratory Groebner basis is not an input to this checker.
"""
from __future__ import annotations
import copy
import hashlib
import json
from pathlib import Path
import sys

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / 'results/cyclic-fano-fibers'
SOURCE = ROOT / 'results/cyclic-fano-curve'


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def polynomial(terms, variables):
    seen = set()
    value = 0
    for term in terms:
        powers = tuple(term['powers'])
        assert len(powers) == len(variables) and powers not in seen
        assert all(type(n) is int and n >= 0 for n in powers)
        seen.add(powers)
        real, imag = map(sp.Rational, term['coefficient'])
        value += (real + sp.I*imag)*sp.prod(x**n for x, n in zip(variables, powers))
    return sp.expand(value)


def reconstruct():
    record = (SOURCE / 'source/instance.rec').read_text(encoding='utf-8')
    fields = {}
    active = None
    for line in record.splitlines():
        if line.startswith(('F: ', 'A: ', 'q: ')):
            active, value = line.split(': ', 1)
            fields[active] = value
        elif active and line.startswith('  '):
            fields[active] += ' ' + line.strip()
        else:
            active = None
    manifest = json.loads((SOURCE / 'target.json').read_text(encoding='utf-8'))
    assert fields == manifest['target'] and fields['q'] == '1'
    x0, x1, x2, y0, y1, y2, z, u = sp.symbols('X0 X1 X2 Y0 Y1 Y2 Z u')
    coordinates = (x0, x1, x2, y0, y1, y2)
    F = sp.sympify(fields['F'], locals={str(x): x for x in coordinates})
    poly_x2 = sp.Poly(F, x2)
    assert all(poly_x2.nth(j) == 0 for j in (1, 2, 4, 5))
    G = sp.expand(poly_x2.nth(6)*z*z + poly_x2.nth(3)*z + poly_x2.nth(0))
    assert sp.expand(G.subs(z, x2**3)-F) == 0
    b, c, v, k, ell, m = sp.symbols('b c v k l m')
    slopes = (b, c, v)
    variables = slopes + (k, ell, m)
    substitution = {x0: b*u, x1: 1, y0: sp.I+c*u, y1: 1+u, y2: sp.I+(sp.I+v)*u}
    in_z = sp.Poly(G, z)
    assert in_z.nth(2) == 1
    Q = sp.Poly(sp.expand(in_z.nth(1).subs(substitution)), u)
    P = sp.Poly(sp.expand(in_z.nth(0).subs(substitution)), u)
    delta = Q.nth(0)
    assert delta == 5*sp.I/7 and P.nth(0) == 0
    k_value = sp.expand(-P.nth(1)/delta)
    l_value = sp.expand(-(k_value**2+Q.nth(1)*k_value+P.nth(2))/delta)
    m_value = sp.expand(-(2*k_value*l_value+Q.nth(1)*l_value+Q.nth(2)*k_value+P.nth(3))/delta)
    remaining = [
        sp.expand(l_value**2+2*k_value*m_value+Q.nth(1)*m_value+Q.nth(2)*l_value+Q.nth(3)*k_value+P.nth(4)),
        sp.expand(2*l_value*m_value+Q.nth(2)*m_value+Q.nth(3)*l_value+P.nth(5)),
        sp.expand(m_value**2+Q.nth(3)*m_value+P.nth(6)),
    ]
    raw = sp.Poly(sp.expand((z*z+Q.as_expr()*z+P.as_expr()).subs(z, k*u+ell*u*u+m*u**3)), u)
    equations = [raw.nth(j) for j in range(1, 7)]
    solved = {k: k_value, ell: l_value, m: m_value}
    assert sp.expand(raw.as_expr().subs(solved)-sum(eq*u**j for j, eq in enumerate(remaining, 4))) == 0
    jac = sp.Matrix(remaining).jacobian(slopes).subs(dict.fromkeys(slopes, 0))
    assert sp.simplify(jac.det()) == -180*sp.I/7
    return variables, equations, (k_value, l_value, m_value), remaining, G


def mod_gaussian(value, p, imag):
    real, imaginary = map(sp.Rational, sp.expand(value).as_real_imag())
    return (int(real.p)*pow(int(real.q), -1, p)+imag*int(imaginary.p)*pow(int(imaginary.q), -1, p)) % p


def determinant_mod(rows, prime):
    # Gauss-Jordan, with a separate row permutation sign.
    a = [list(row) for row in rows]
    n = len(a)
    assert all(len(row) == n for row in a)
    det = 1
    for j in range(n):
        pivot = next((i for i in range(j, n) if a[i][j] % prime), None)
        if pivot is None:
            return 0
        if pivot != j:
            a[j], a[pivot] = a[pivot], a[j]
            det = -det
        leading = a[j][j] % prime
        det = det*leading % prime
        a[j] = [(x*pow(leading, -1, prime)) % prime for x in a[j]]
        for i in range(n):
            if i == j:
                continue
            multiplier = a[i][j] % prime
            if multiplier:
                a[i] = [(x-multiplier*y) % prime for x, y in zip(a[i], a[j])]
    return det % prime


def validate(packet, witness, rebuilt):
    variables, equations, solutions, remaining, G = rebuilt
    assert packet['instance'] == 'cyclic-triple-fano'
    assert packet['variables'] == [str(x) for x in variables]
    assert packet['fixed_target_manifest_sha256'] == sha(SOURCE / 'target.json')
    assert packet['curve_packet_sha256'] == sha(SOURCE / 'cyclic-free-curve.json')
    assert sp.expand(sp.sympify(packet['quotient_equation'])-G) == 0
    assert len(packet['coefficient_equations']) == 6
    assert all(sp.expand(polynomial(q, variables)-expected) == 0 for q, expected in zip(packet['coefficient_equations'], equations))
    assert len(packet['triangular_solutions']) == len(packet['remaining_equations']) == 3
    for j, stage in enumerate(packet['triangular_solutions']):
        assert stage['variable'] == str(variables[j+3])
        assert stage['pivot'] == ['0', '5/7']
        assert polynomial(stage['solution'], variables[:3]) == solutions[j]
    assert all(polynomial(q, variables[:3]) == expected for q, expected in zip(packet['remaining_equations'], remaining))
    degrees = [int(sp.Poly(q, *variables[:3]).total_degree()) for q in remaining]
    assert packet['remaining_degrees'] == degrees == [4, 5, 6]
    assert packet['reduced_jacobian_determinant'] == ['0', '-180/7']
    prime, imaginary = witness['prime'], witness['i_image']
    assert (prime, imaginary) == (101, 10) and (imaginary**2+1) % prime == 0
    assert witness['homogeneous_degree'] == 13 and witness['matrix_shape'] == [105, 136]
    rows = [tuple(r) for r in witness['rows']]
    assert len(set(rows)) == len(rows) == 105
    assert set(rows) == {(a, b, 13-a-b) for a in range(14) for b in range(14-a)}
    top = [{powers: mod_gaussian(coefficient, prime, imaginary) for powers, coefficient in sp.Poly(q, *variables[:3]).terms() if sum(powers) == degree} for q, degree in zip(remaining, degrees)]
    expected_metadata = {(i, (a, b, 13-degree-a-b)) for i, degree in enumerate(degrees) for a in range(14-degree) for b in range(14-degree-a)}
    observed_metadata = set()
    columns = []
    for column in witness['columns']:
        i, shift = column['source_equation_index'], tuple(column['multiplier_powers'])
        assert (i, shift) in expected_metadata and (i, shift) not in observed_metadata
        observed_metadata.add((i, shift))
        expected = {tuple(a+b for a, b in zip(power, shift)): value for power, value in top[i].items()}
        dense = [expected.get(row, 0) for row in rows]
        assert column['entries'] == [[j, value] for j, value in enumerate(dense) if value]
        columns.append(dense)
    assert observed_metadata == expected_metadata and len(columns) == 136
    selected = witness['selected_columns']
    assert len(set(selected)) == len(selected) == 105 and all(0 <= j < 136 for j in selected)
    minor = [[columns[j][i] for j in selected] for i in range(105)]
    determinant = determinant_mod(minor, prime)
    assert determinant == witness['selected_minor_determinant_mod_p'] == 47
    return determinant


def main():
    if not __debug__:
        raise RuntimeError('Run without -O.')
    packet = json.loads((INPUT / 'fiber-equations.json').read_text(encoding='utf-8'))
    witness = json.loads((INPUT / 'infinity-witness.json').read_text(encoding='utf-8'))
    assert witness['input_packet_sha256'] == sha(INPUT / 'fiber-equations.json')
    rebuilt = reconstruct()
    determinant = validate(packet, witness, rebuilt)
    mutants = []
    for label, alter in [
        ('equation', lambda p, w: p['coefficient_equations'][0][0]['coefficient'].__setitem__(0, '1')),
        ('triangular solution', lambda p, w: p['triangular_solutions'][0]['solution'][0]['coefficient'].__setitem__(0, '1000')),
        ('remaining equation', lambda p, w: p['remaining_equations'][0][0]['coefficient'].__setitem__(0, '1000')),
        ('Macaulay coefficient', lambda p, w: w['columns'][0]['entries'][0].__setitem__(1, -1)),
        ('minor determinant', lambda p, w: w.__setitem__('selected_minor_determinant_mod_p', 48)),
    ]:
        p, w = copy.deepcopy(packet), copy.deepcopy(witness)
        alter(p, w)
        try:
            validate(p, w, rebuilt)
        except AssertionError:
            mutants.append(label)
        else:
            raise AssertionError('Altered witness accepted: ' + label)
    receipt = {'schema': 'cyclic-fano-fiber-independent-v1', 'status': 'PASS',
               'packet_sha256': sha(INPUT / 'fiber-equations.json'), 'infinity_witness_sha256': sha(INPUT / 'infinity-witness.json'),
               'checker_sha256': sha(Path(__file__)), 'reconstruction': 'quadratic-in-Z Taylor recurrence from raw protected F',
               'three_degrees': [4, 5, 6], 'reduced_jacobian_determinant': '-180*i/7',
               'macaulay_shape': [105, 136], 'selected_minor_mod_101': determinant,
               'all_columns_rebuilt': True, 'no_infinity_over_characteristic_zero': True,
               'complete_intersection_length_with_multiplicity': 120, 'mutations_rejected': mutants,
               'limits': 'Fixed-point fiber of this slice only. Not 120 distinct points, not a degree for the seed component, not a support divisor or certificate.'}
    output = Path(sys.argv[1]) if len(sys.argv) > 1 else INPUT / 'independent-validation.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()

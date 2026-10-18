#!/usr/bin/env python3
"""Independent Case05 polynomial reconstruction; no producer arithmetic imports.

All polynomial operations below use Python's standard-library Fraction. Lean
separately proves the interpretation of its sparse operations and the projected
polynomial obstruction. The seven-row raw check is additional Python evidence.
"""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import argparse
import ast
import copy
import hashlib
import json
import re
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/cyclic-fano-polynomial-bridge'
SOURCE = ROOT / 'results/cyclic-fano-curve/source/instance.rec'
SOURCE_SHA = 'd99d10c84d25dc5def72cd7a9a17e5d022e18f562660c8e33bf106675b4a418c'
CASE05_SHA = '903bd1bc44d32579a4fcc4e44e3a5702f46b1ecc2a6948108599e4c68c84d00c'
BASE = (0, 1, 3, 4, 5)
WEIGHTS = (1, 1, 3, 1, 1, 1)
ZERO = (0,) * 6
NAMES = ('X0', 'X1', 'X2', 'Y0', 'Y1', 'Y2')


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def clean(p):
    return {m: Q(c) for m, c in p.items() if c}


def add(*ps):
    out = {}
    for p in ps:
        for m, c in p.items():
            out[m] = out.get(m, Q(0)) + c
    return clean(out)


def scale(p, c):
    return clean({m: Q(c) * a for m, a in p.items()})


def multiply(p, q):
    out = {}
    for m, a in p.items():
        for n, b in q.items():
            k = tuple(x + y for x, y in zip(m, n))
            out[k] = out.get(k, Q(0)) + a * b
    return clean(out)


def power(p, n):
    assert type(n) is int and n >= 0
    out = {ZERO: Q(1)}
    for _ in range(n):
        out = multiply(out, p)
    return out


def derivative(p, i):
    out = {}
    for m, c in p.items():
        if m[i]:
            n = list(m)
            n[i] -= 1
            out[tuple(n)] = c * m[i]
    return out


def variable(i):
    return {tuple(int(i == j) for j in range(6)): Q(1)}


def divergence(field):
    return add(*(derivative(p, i) for i, p in enumerate(field)))


def contraction(field, p):
    return add(*(multiply(v, derivative(p, i)) for i, v in enumerate(field)))


def B(e, field):
    return add(multiply(e, divergence(field)), scale(contraction(field, e), -1))


def pullback(p):
    return {m[:2] + (3 * m[2],) + m[3:]: c for m, c in p.items()}


def monomials(weight, weights=WEIGHTS):
    def walk(index, remaining, prefix):
        if index == len(weights):
            if remaining == 0:
                yield tuple(prefix)
            return
        for n in range(remaining // weights[index] + 1):
            yield from walk(index + 1, remaining - weights[index] * n, prefix + [n])
    return sorted(walk(0, weight, []), reverse=True)


def parse_polynomial(text):
    def parse(node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return clean({ZERO: Q(node.value)})
        if isinstance(node, ast.Name) and node.id in NAMES:
            return variable(NAMES.index(node.id))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return scale(parse(node.operand), -1)
        if isinstance(node, ast.BinOp):
            if isinstance(node.op, ast.Pow):
                assert isinstance(node.right, ast.Constant)
                return power(parse(node.left), node.right.value)
            p, q = parse(node.left), parse(node.right)
            if isinstance(node.op, ast.Add):
                return add(p, q)
            if isinstance(node.op, ast.Sub):
                return add(p, scale(q, -1))
            if isinstance(node.op, ast.Mult):
                return multiply(p, q)
            if isinstance(node.op, ast.Div):
                assert set(q) == {ZERO} and q[ZERO]
                return scale(p, 1 / q[ZERO])
        raise AssertionError('Unsupported source expression: ' + ast.dump(node))
    return parse(ast.parse('(' + text + ')', mode='eval').body)


def read_target():
    assert sha(SOURCE) == SOURCE_SHA, 'Fixed target bytes changed'
    source = SOURCE.read_text(encoding='utf-8')
    assert re.search(r'^q: 1$', source, re.M)
    f_text = re.search(r'^F: (.*?)\nA:', source, re.S | re.M).group(1)
    a_text = re.search(r'^A: (.*)$', source, re.M).group(1)
    f, alpha = parse_polynomial(f_text), parse_polynomial(a_text)
    g = {}
    for m, c in f.items():
        assert m[2] % 3 == 0
        n = list(m)
        n[2] //= 3
        g[tuple(n)] = c
    q, h = {}, {}
    for m, c in g.items():
        n = list(m)
        n[2] = 0
        if m[2] == 1:
            q[tuple(n)] = c
        elif m[2] == 0:
            h[m] = c
        else:
            assert m == (0, 0, 2, 0, 0, 0) and c == 1
    assert g == add(power(variable(2), 2), multiply(q, variable(2)), h)
    beta = {(1, 0, 0, 3, 0, 0): Q(1, 3)}
    assert alpha == {(1, 0, 2, 3, 0, 0): Q(1)}
    return f, alpha, g, q, h, beta


def projection(p, q, h):
    """Half trace in Q[x,Z]/(Z^2+QZ+H); not substitution before divergence."""
    traces = [{ZERO: Q(1)}, scale(q, -Q(1, 2))]
    degree = max((m[2] for m in p), default=0)
    while len(traces) <= degree:
        traces.append(scale(add(multiply(q, traces[-1]), multiply(h, traces[-2])), -1))
    out = {}
    for m, c in p.items():
        n = list(m)
        n[2] = 0
        out = add(out, multiply({tuple(n): c}, traces[m[2]]))
    return out


def compact_columns(e, delta):
    dg = {i: derivative(delta, i) for i in BASE}
    labels, columns = [], []
    def w(i, j, p):
        return add(multiply(dg[i], derivative(p, j)), scale(multiply(dg[j], derivative(p, i)), -1))
    for i, j in combinations(BASE, 2):
        for m in monomials(2):
            h = {m: Q(1)}
            labels.append(('base', i, j, m))
            columns.append(add(multiply(e, w(i, j, h)), scale(multiply(h, w(i, j, e)), -1)))
    for i in BASE:
        for k in BASE:
            h = variable(k)
            labels.append(('mixed', i, k))
            columns.append(add(multiply(h, add(multiply(e, dg[i]), scale(multiply(delta, derivative(e, i)), -2))),
                               scale(multiply(multiply(delta, e), derivative(h, i)), 2)))
    assert len(columns) == 175
    return labels, columns


def derive():
    f, alpha, g, q, h, beta = read_target()
    delta = add(power(q, 2), scale(h, -4))
    v = [power(variable(0), 3), power(variable(5), 3), {}, {}, {}, {}]
    e = contraction(v, delta)
    field = [scale(multiply(beta, vi), -4) for vi in v]
    field[2] = scale(multiply(beta, contraction(v, q)), 2)
    assert contraction(field, g) == multiply(beta, e)
    jacobian = scale(power(variable(2), 2), 3)
    lifted = [pullback(p) if i == 2 else multiply(jacobian, pullback(p))
              for i, p in enumerate(field)]
    assert contraction(lifted, f) == multiply(alpha, pullback(e))
    assert B(pullback(e), lifted) == multiply(jacobian, pullback(B(e, field)))
    assert all(sum(a * w for a, w in zip(m, WEIGHTS)) == 8 and m[2] == 0 for m in e)
    rhs = scale(B(e, field), -1)
    residual_formula = scale(add(multiply(add(contraction(v, beta), multiply(beta, divergence(v))), e),
                                scale(multiply(beta, contraction(v, e)), -1)), 4)
    assert rhs == residual_formula
    labels, columns = compact_columns(e, delta)
    return dict(F=f, A=alpha, G=g, Q=q, H=h, beta=beta, Delta=delta,
                v=v, E=e, field=field, lifted_field=lifted, rhs=rhs, labels=labels, columns=columns)


def encode(p):
    return [{'powers': list(m), 'coefficient': str(c)} for m, c in sorted(p.items())]


def decode(entries):
    return clean({tuple(entry['powers']): Q(entry['coefficient']) for entry in entries})


def audit_rows(case, data):
    assert case['case_index'] == 5 and case['direction'] == [[0, '1'], [69, '1']]
    assert decode(case['denominator']) == data['E']
    assert case['columns'] == len(data['columns']) == 175
    assert len(case['rows']) == len(case['dual']) == 2
    assert case['dual'] == [756, 1]
    seen = set()
    for row in case['rows']:
        m = tuple(row['powers'])
        assert m not in seen and len(m) == 6 and m[2] == 0 and sum(m) == 14
        seen.add(m)
        scale_factor = Q(row['row_scale'])
        assert scale_factor > 0
        expected = dict(row['entries'])
        assert len(expected) == len(row['entries'])
        assert all(0 <= j < 175 for j in expected)
        for j, column in enumerate(data['columns']):
            assert scale_factor * column.get(m, 0) == expected.get(j, 0)
        assert scale_factor * data['rhs'].get(m, 0) == row['target']
    assert [sum(w * dict(row['entries']).get(j, 0) for w, row in zip(case['dual'], case['rows']))
            for j in range(175)] == [0] * 175
    assert sum(w * row['target'] for w, row in zip(case['dual'], case['rows'])) == case['target_pairing'] == -5
    return dict(status='PASS', physical_coefficients=352, correction_columns=175,
                particular_weighted_E1_identity=True, particular_original_E1_identity=True,
                particular_Piola_E2_identity=True,
                only_nonzero_column=119, exact_unscaled_rows=['2400/49', '-1440/7'],
                exact_unscaled_target=['0', '-200/147'], integer_target_pairing=-5)


def raw_evidence(data):
    m0, m1 = (0, 1, 0, 7, 1, 5), (1, 0, 0, 5, 2, 6)
    functional = {}
    for k in range(5):
        trace = projection(power(variable(2), k), data['Q'], data['H'])
        for target, weight in [(m0, Q(21)), (m1, Q(5))]:
            for m, c in trace.items():
                n = tuple(target[i] - m[i] if i != 2 else k for i in range(6))
                if min(n) >= 0:
                    functional[n] = functional.get(n, Q(0)) + weight * c
    functional = clean(functional)
    def pair(p):
        return sum(c * functional.get(m, 0) for m, c in p.items())
    assert len(functional) == 7 and pair(data['rhs']) == -Q(1000, 147)
    gradient = [derivative(data['G'], i) for i in range(6)]
    count = retained = 0
    for i, j in combinations(range(6), 2):
        for m in monomials(WEIGHTS[i] + WEIGHTS[j]):
            h = {m: Q(1)}
            field = [{} for _ in range(6)]
            field[i] = multiply(h, gradient[j])
            field[j] = scale(multiply(h, gradient[i]), -1)
            assert not contraction(field, data['G'])
            image = B(data['E'], field)
            actual = projection(image, data['Q'], data['H'])
            if 2 not in (i, j):
                index = data['labels'].index(('base', i, j, m))
                expected = scale(data['columns'][index], Q(1, 4))
                retained += 1
            elif m[2]:
                k = next(k for k in BASE if m[k])
                other = j if i == 2 else i
                index = data['labels'].index(('mixed', other, k))
                expected = scale(data['columns'][index], Q(-1 if i == 2 else 1, 4))
                retained += 1
            else:
                expected = {}
            assert actual == expected, (i, j, m)
            assert pair(image) == 0
            count += 1
    quotient = monomials(8)
    for m in quotient:
        image = multiply({m: Q(1)}, data['G'])
        assert not projection(image, data['Q'], data['H'])
        assert pair(image) == 0
    assert count == 525 and retained == 175 and len(quotient) == 636
    return dict(status='PASS', functional=encode(functional), functional_support=7,
                raw_Koszul_columns=525, retained_projection_types=175,
                quotient_columns=636, target_pairing='-1000/147',
                projection='Half trace after reduction modulo G, applied after differentiation',
                scope='Additional independent exact Python check, not part of the Lean theorem. This does not formalize regular-sequence completeness, Euler normalization or Piola transfer.')


def rejects(action):
    try:
        action()
    except (AssertionError, ValueError, KeyError):
        return True
    return False


def negative_controls(case, data):
    names = []
    for name in ('entry', 'target', 'scale', 'monomial', 'dual', 'column_count'):
        bad = copy.deepcopy(case)
        if name == 'entry': bad['rows'][0]['entries'][0][1] += 1
        elif name == 'target': bad['rows'][1]['target'] += 1
        elif name == 'scale': bad['rows'][0]['row_scale'] = '1'
        elif name == 'monomial': bad['rows'][0]['powers'][2] = 1
        elif name == 'dual': bad['dual'][0] += 1
        else: bad['columns'] -= 1
        assert rejects(lambda: audit_rows(bad, data)), name
        names.append(name)
    bad = copy.deepcopy(data)
    bad['columns'][150] = add(bad['columns'][150], scale(multiply(bad['Delta'], bad['E']), -2))
    assert rejects(lambda: raw_evidence(bad))
    names.append('missing_mixed_multiplier_derivative')
    bad = copy.deepcopy(data)
    bad['rhs'] = scale(bad['rhs'], -1)
    assert rejects(lambda: audit_rows(case, bad))
    names.append('residual_sign')
    field = copy.deepcopy(data['field'])
    field[0] = {}
    assert contraction(field, data['G']) != multiply(data['beta'], data['E'])
    names.append('missing_E1_component')
    return names


def lean_definition(source, name):
    """Read one definition body; accepted formulas below are intentionally fixed."""
    pattern = (r'^(?:noncomputable\s+)?def\s+' + re.escape(name) +
               r'\b.*?:=\s*(.*?)(?=\n(?:noncomputable\s+)?def\s|'
               r'\ninductive\s|\nset_option\s|\n(?:@\[[^\n]*\]\s*)?theorem\s|\nend\s|\Z)')
    found = re.findall(pattern, source, re.M | re.S)
    assert len(found) == 1, ('definition missing/ambiguous', name)
    return found[0].strip()


def canonical(text):
    return re.sub(r'\s+', '', text)


def sparse_literal(body):
    pattern = r'\(exp((?:\s+\d+){5}),\s*(\([^()]*\)|-?\d+)\s*\)'
    found = re.findall(pattern, body)
    assert found
    assert re.sub(r'[\s,\[\]]', '', re.sub(pattern, '', body)) == ''
    out = {}
    for powers, coefficient in found:
        five = tuple(map(int, powers.split()))
        m = five[:2] + (0,) + five[2:]
        c = Q(coefficient.strip('()').replace(' ', ''))
        assert m not in out
        out[m] = c
    return clean(out)


def audit_lean_model(source, data):
    assert 'namespace HodgeLab.CyclicFano.Case05Polynomial' in source
    assert not re.search(r'\b(sorry|admit|axiom|native_decide|unsafe)\b', source)
    for name, expected in [('qSparse', data['Q']), ('hSparse', data['H']),
                           ('betaSparse', data['beta']), ('v0', data['v'][0]), ('v1', data['v'][1])]:
        assert sparse_literal(lean_definition(source, name)) == expected, name
    expected_definitions = {
        'exp': '![a,b,c,d,e]',
        'deltaSparse': 'subtract (multiply qSparse qSparse) (scale 4 hSparse)',
        'denominatorSparse': 'multiply v0 (derivative 0 deltaSparse) ++ multiply v1 (derivative 1 deltaSparse)',
        'rhsSparse': '''scale 4 (subtract
          (multiply (derivative 0 (multiply betaSparse v0) ++
                     derivative 1 (multiply betaSparse v1)) denominatorSparse)
          (multiply betaSparse (multiply v0 (derivative 0 denominatorSparse) ++
                               multiply v1 (derivative 1 denominatorSparse))))''',
        'xSparse': '[(fun j => if j = i then 1 else 0, 1)]',
        'columnSparse': '''match correction column with
          | .base i j h =>
            let f : Sparse := [(h, 1)]
            subtract
              (multiply denominatorSparse (subtract
                (multiply (derivative i deltaSparse) (derivative j f))
                (multiply (derivative j deltaSparse) (derivative i f))))
              (multiply f (subtract
                (multiply (derivative i deltaSparse) (derivative j denominatorSparse))
                (multiply (derivative j deltaSparse) (derivative i denominatorSparse))))
          | .mixed i k =>
            multiply (xSparse k) (subtract
              (multiply denominatorSparse (derivative i deltaSparse))
              (scale 2 (multiply deltaSparse (derivative i denominatorSparse)))) ++
            scale 2 (multiply (multiply deltaSparse denominatorSparse) (derivative i (xSparse k)))''',
        'rowExponent': 'if row.val = 0 then exp 0 1 7 1 5 else exp 1 0 5 2 6',
        'rowScale': 'if row.val = 0 then 49 / 2400 else 147 / 40',
        'delta': 'eval deltaSparse', 'denominator': 'eval denominatorSparse',
        'rhs': 'eval rhsSparse', 'column': 'eval (columnSparse j)',
    }
    for name, expected in expected_definitions.items():
        assert canonical(lean_definition(source, name)) == canonical(expected), name
    body = lean_definition(source, 'correction')
    assert body.startswith('match column.val with')
    lines = body.splitlines()[1:]
    assert len(lines) == 176
    actual = []
    for index, line in enumerate(lines[:-1]):
        base = re.fullmatch(r'\s*\| (\d+) => \.base (\d+) (\d+) \(exp((?: \d+){5})\)', line)
        mixed = re.fullmatch(r'\s*\| (\d+) => \.mixed (\d+) (\d+)', line)
        assert base or mixed
        if base:
            n, i, j = map(int, base.group(1, 2, 3))
            five = tuple(map(int, base.group(4).split()))
            label = ('base', BASE[i], BASE[j], five[:2] + (0,) + five[2:])
        else:
            n, i, j = map(int, mixed.groups())
            label = ('mixed', BASE[i], BASE[j])
        assert n == index
        actual.append(label)
    assert canonical(lines[-1]) == '|_=>.base01(exp20000)'
    assert actual == data['labels']
    return dict(status='PASS', literal_polynomials=5, operational_definitions=len(expected_definitions),
                correction_labels=175, base_variable_order=['X0', 'X1', 'Y0', 'Y1', 'Y2'],
                method='Parse literal polynomials and all correction labels; match each computational expression to an independently reconstructed polynomial operation. Lean execution is separate.')


def lean_source_controls(source, data):
    changes = {
        'source_coefficient': ('(exp 3 0 0 0 0, (5 / 7))', '(exp 3 0 0 0 0, (6 / 7))'),
        'source_direction': ('def v1 : Sparse := [(exp 0 0 0 0 3, 1)]', 'def v1 : Sparse := [(exp 0 0 0 3 0, 1)]'),
        'source_row_scale': ('49 / 2400 else 147 / 40', '49 / 2401 else 147 / 40'),
        'source_correction_label': ('| 119 => .base 2 3 (exp 0 0 0 0 2)', '| 119 => .base 2 3 (exp 0 0 0 1 1)'),
        'source_mixed_derivative': ('scale 2 (multiply (multiply deltaSparse denominatorSparse) (derivative i (xSparse k)))',
                                    'scale 0 (multiply (multiply deltaSparse denominatorSparse) (derivative i (xSparse k)))'),
    }
    for name, (before, after) in changes.items():
        assert source.count(before) == 1, name
        assert rejects(lambda: audit_lean_model(source.replace(before, after), data)), name
    return list(changes)


def audit_sparse_implementation(source):
    assert not re.search(r'\b(sorry|admit|axiom|native_decide|unsafe)\b', source)
    assert 'abbrev Exponent := Fin 5 → ℕ' in source
    assert 'abbrev Sparse := List (Exponent × ℚ)' in source
    expected = {
        'exponent': 'Finsupp.equivFunOnFinite.symm m',
        'scale': 'p.map fun term => (term.1, c * term.2)',
        'subtract': 'p ++ scale (-1) q',
        'multiply': 'p.flatMap fun a => q.map fun b => (fun i => a.1 i + b.1 i, a.2 * b.2)',
        'derivative': '''p.flatMap fun term => if term.1 i = 0 then [] else
          [(fun j => term.1 j - if j = i then 1 else 0, term.2 * term.1 i)]''',
    }
    for name, body in expected.items():
        assert canonical(lean_definition(source, name)) == canonical(body), name
    recursive = {
        'eval': '''noncomputable def eval : Sparse → MvPolynomial (Fin 5) ℚ
          | [] => 0
          | (m, c) :: tail => MvPolynomial.monomial (exponent m) c + eval tail''',
        'coefficient': '''def coefficient (m : Exponent) : Sparse → ℚ
          | [] => 0
          | (n, c) :: tail => if n = m then c + coefficient m tail else coefficient m tail''',
    }
    for name, body in recursive.items():
        actual = re.search(r'^(?:noncomputable )?def ' + name + r'\b.*?(?=\n\ndef )', source, re.M | re.S)
        assert actual and canonical(actual.group()) == canonical(body), name
    semantic_lemmas = {
        'coefficient_eval': '''(m : Exponent) (p : Sparse) :
          MvPolynomial.coeff (exponent m) (eval p) = coefficient m p''',
        'eval_append': '(p q : Sparse) : eval (p ++ q) = eval p + eval q',
        'eval_scale': '(c : ℚ) (p : Sparse) : eval (scale c p) = MvPolynomial.C c * eval p',
        'eval_subtract': '(p q : Sparse) : eval (subtract p q) = eval p - eval q',
        'eval_multiply': '(p q : Sparse) : eval (multiply p q) = eval p * eval q',
        'eval_derivative': '''(i : Fin 5) (p : Sparse) :
          eval (derivative i p) = MvPolynomial.pderiv i (eval p)''',
    }
    for name, statement in semantic_lemmas.items():
        assert theorem_statement(source, name) == canonical(statement), name
    return dict(status='PASS', representation='Finite lists interpreted in MvPolynomial (Fin 5) Q',
                checked_computational_operations=list(expected) + list(recursive),
                semantic_lemmas=list(semantic_lemmas),
                scope='Operation definitions and proof statements reviewed; compilation and kernel replay are established only by the separate Lean receipt.')


def audit_case05_literals(source, case):
    assert 'namespace HodgeLab.CyclicFano.Case05' in source
    assert not re.search(r'\b(sorry|admit|axiom|native_decide|unsafe)\b', source)
    matrix = lean_definition(source, 'matrix')
    assert matrix.startswith('match row.val, column.val with')
    lines = matrix.splitlines()[1:]
    assert lines[-1].strip() == '| _, _ => 0'
    actual = {}
    for line in lines[:-1]:
        matched = re.fullmatch(r'\s*\| (\d+), (\d+) => (-?\d+)', line)
        assert matched
        i, j, value = map(int, matched.groups())
        assert (i, j) not in actual
        actual[i, j] = value
    assert actual == {(i, j): c for i, row in enumerate(case['rows']) for j, c in row['entries']}
    for name, expected in [('target', [row['target'] for row in case['rows']]), ('dual', case['dual'])]:
        body = lean_definition(source, name)
        assert body.startswith('match row.val with')
        lines = body.splitlines()[1:]
        assert lines[-1].strip() == '| _ => 0'
        entries = []
        for line in lines[:-1]:
            matched = re.fullmatch(r'\s*\| (\d+) => (-?\d+)', line)
            assert matched
            entries.append(tuple(map(int, matched.groups())))
        assert entries == list(enumerate(expected))
    return dict(status='PASS', encoded_rows=2, encoded_columns=175,
                encoded_dual=[756, 1], encoded_target=[0, -5])


def theorem_statement(source, name):
    found = re.findall(r'^(?:@\[[^\n]*\]\s*)?theorem\s+' + re.escape(name) + r'\b(.*?):=\s*by\b',
                       source, re.M | re.S)
    assert len(found) == 1, ('theorem missing/ambiguous', name)
    return canonical(found[0])


def audit_field_extension(source, rational_source):
    """Check the actual field and scalar-coefficient scope, not just a theorem name."""
    assert not re.search(r'\b(sorry|admit|axiom|native_decide|unsafe)\b', source)
    expected_definitions = {
        'columnOver': 'MvPolynomial.map (Rat.castHom K) (column j)',
        'rhsOver': 'MvPolynomial.map (Rat.castHom K) rhs',
    }
    for name, body in expected_definitions.items():
        assert canonical(lean_definition(source, name)) == canonical(body), name
    expected = {
        'column_coefficients_over': '''(K : Type*) [Field K] [CharZero K]
          (row : Fin 2) (j : Fin 175) :
          (rowScale row : K) * MvPolynomial.coeff (exponent (rowExponent row)) (columnOver K j) =
          (Case05.matrix row j : K)''',
        'target_coefficients_over': '''(K : Type*) [Field K] [CharZero K] (row : Fin 2) :
          (rowScale row : K) * MvPolynomial.coeff (exponent (rowExponent row)) (rhsOver K) =
          (Case05.target row : K)''',
        'polynomial_equation_implies_matrix_over': '''(K : Type*) [Field K] [CharZero K]
          (c : Fin 175 → K)
          (equation : ∑ j, MvPolynomial.C (c j) * columnOver K j = rhsOver K) :
          ∀ row : Fin 2, ∑ j, (Case05.matrix row j : K) * c j = (Case05.target row : K)''',
        'no_polynomial_solution_over': '''(K : Type*) [Field K] [CharZero K] :
          ¬ ∃ c : Fin 175 → K, ∑ j, MvPolynomial.C (c j) * columnOver K j = rhsOver K''',
    }
    for name, statement in expected.items():
        assert theorem_statement(source, name) == canonical(statement), name
    assert theorem_statement(rational_source, 'no_polynomial_solution') == canonical('''
      : ¬ ∃ c : Fin 175 → ℚ, ∑ j, MvPolynomial.C (c j) * column j = rhs''')
    return dict(status='PASS', theorem='HodgeLab.CyclicFano.Case05Polynomial.no_polynomial_solution_over',
                field_scope='Every characteristic-zero field K; coefficients c are scalar elements of K.',
                scalar_extension='MvPolynomial.map (Rat.castHom K) of the explicitly computed rational polynomials.',
                checked_statements=list(expected) + ['no_polynomial_solution'],
                boundary='This is an explicit 175-operator polynomial equation obstruction. General certificate normalization, correction-space completeness, and quotient/Piola transfer remain outside these Lean statements.')


def manifest_bindings(manifest_path, required_sources):
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    assert manifest['schema'] == 'hodge-lab-case05-polynomial-export-v1'
    assert manifest['variable_order'] == ['X0', 'X1', 'Y0', 'Y1', 'Y2']
    assert manifest['direction'] == [[0, '1'], [69, '1']]
    assert manifest['correction_count'] == 175
    assert manifest['selected_rows'] == [[0, 1, 7, 1, 5], [1, 0, 5, 2, 6]]
    assert manifest['row_scales'] == ['49/2400', '147/40']
    assert manifest['coefficient_checks'] == 352
    bindings = manifest['source_lf_sha256']
    required = {p.relative_to(ROOT).as_posix() for p in required_sources}
    assert required <= set(bindings), ('Manifest missing required inputs', sorted(required - set(bindings)))
    for name, digest in bindings.items():
        path = (ROOT / name).resolve()
        assert path.is_relative_to(ROOT), name
        assert sha(path) == digest, ('Changed manifest input', name)
    needed_modules = {'HodgeLab.SparsePolynomial', 'HodgeLab.CyclicFano.Case05Polynomial',
                      'HodgeLab.CyclicFano.Case05PolynomialField'}
    assert needed_modules <= set(manifest['modules'])
    assert 'HodgeLab.CyclicFano.Case05Polynomial.no_polynomial_solution_over' in manifest['theorem_names']
    assert len(manifest['theorem_names']) == len(set(manifest['theorem_names']))
    for control in manifest['negative_controls']:
        assert control['file'] in bindings
        original = (ROOT / control['file']).read_text(encoding='utf-8')
        assert original.count(control['before']) == 1
        assert control['after'] != control['before']
    return manifest, {**bindings, manifest_path.relative_to(ROOT).as_posix(): sha(manifest_path)}


def lean_mutation_expectations(manifest, data):
    """Establish mathematical falsity independently of compiler diagnostic wording."""
    controls = {entry['label']: entry for entry in manifest['negative_controls']}
    assert set(controls) == {'scale', 'density'}
    assert controls['scale']['before'] == 'then 49 / 2400 else'
    assert controls['scale']['after'] == 'then 49 / 2401 else'
    assert controls['density']['before'] == 'def betaSparse : Sparse := [(exp 1 0 3 0 0, (1 / 3))]'
    assert controls['density']['after'] == 'def betaSparse : Sparse := [(exp 1 0 3 0 0, (1 / 4))]'
    changed_beta = scale(data['beta'], Q(3, 4))
    v = data['v']
    changed_rhs = scale(add(multiply(add(contraction(v, changed_beta), multiply(changed_beta, divergence(v))), data['E']),
                           scale(multiply(changed_beta, contraction(v, data['E'])), -1)), 4)
    row0, row1 = (0, 1, 0, 7, 1, 5), (1, 0, 0, 5, 2, 6)
    altered_scale_value = Q(49, 2401) * data['columns'][119][row0]
    altered_density_value = Q(147, 40) * changed_rhs[row1]
    assert altered_scale_value == Q(2400, 2401) != 1
    assert altered_density_value == Q(-15, 4) != -5
    return dict(status='PASS', controls=[
        dict(label='scale', row=0, column=119, changed_left_side=str(altered_scale_value), expected_right_side='1'),
        dict(label='density', row=1, target=True, changed_left_side=str(altered_density_value), expected_right_side='-5')],
        scope='Exact falsity of the two mutated coefficient equalities. Actual Lean rejection and its diagnostic wording belong to the separate compiler receipt.')


def main():
    assert __debug__
    parser = argparse.ArgumentParser()
    parser.add_argument('--arithmetic-only', action='store_true')
    args = parser.parse_args()
    start = time.perf_counter()
    data = derive()
    case_path = ROOT / 'results/cyclic-fano-lean/case-05.json'
    assert sha(case_path) == CASE05_SHA, 'Frozen Case05 certificate changed'
    case = json.loads(case_path.read_text(encoding='utf-8'))
    rows = audit_rows(case, data)
    raw = raw_evidence(data)
    controls = negative_controls(case, data)
    result = dict(schema='cyclic-fano-polynomial-bridge-independent-v1', status='PASS',
                  projected_coefficient_audit=rows, raw_next_step_evidence=raw,
                  altered_inputs_rejected=controls,
                  source_lf_sha256={p.relative_to(ROOT).as_posix(): sha(p) for p in
                                   (Path(__file__).resolve(), SOURCE, case_path)},
                  elapsed_seconds=round(time.perf_counter() - start, 3))
    if args.arithmetic_only:
        print(json.dumps(result, indent=2))
        return
    model_path = ROOT / 'formal/HodgeLab/CyclicFano/Case05Polynomial.lean'
    source = model_path.read_text(encoding='utf-8')
    result['lean_source_audit'] = audit_lean_model(source, data)
    result['altered_inputs_rejected'] += lean_source_controls(source, data)
    sparse_path = ROOT / 'formal/HodgeLab/SparsePolynomial.lean'
    sparse_source = sparse_path.read_text(encoding='utf-8')
    result['sparse_operation_audit'] = audit_sparse_implementation(sparse_source)
    assert sparse_source.count('term.2 * term.1 i') == 1
    assert rejects(lambda: audit_sparse_implementation(sparse_source.replace('term.2 * term.1 i', 'term.2 * (term.1 i + 1)')))
    result['altered_inputs_rejected'].append('source_sparse_derivative')
    assert sparse_source.count('if term.1 i = 0 then [] else') == 1
    assert rejects(lambda: audit_sparse_implementation(sparse_source.replace(
        'if term.1 i = 0 then [] else', 'if term.1 i = 1 then [] else')))
    result['altered_inputs_rejected'].append('source_sparse_derivative_filter')
    coefficient_branch = 'if n = m then c + coefficient m tail else coefficient m tail'
    assert sparse_source.count(coefficient_branch) == 1
    assert rejects(lambda: audit_sparse_implementation(sparse_source.replace(coefficient_branch,
        'if n = m then coefficient m tail else c + coefficient m tail')))
    result['altered_inputs_rejected'].append('source_sparse_coefficient_branch')
    semantic = 'MvPolynomial.coeff (exponent m) (eval p) = coefficient m p'
    assert sparse_source.count(semantic) == 1
    assert rejects(lambda: audit_sparse_implementation(sparse_source.replace(semantic,
        'MvPolynomial.coeff (exponent m) (eval p) = coefficient m p + 1')))
    result['altered_inputs_rejected'].append('source_coefficient_semantic_statement')
    matrix_path = ROOT / 'formal/HodgeLab/CyclicFano/Case05.lean'
    result['finite_matrix_literal_audit'] = audit_case05_literals(matrix_path.read_text(encoding='utf-8'), case)
    field_path = ROOT / 'formal/HodgeLab/CyclicFano/Case05PolynomialField.lean'
    field_source = field_path.read_text(encoding='utf-8')
    result['field_extension_audit'] = audit_field_extension(field_source, source)
    assert rejects(lambda: audit_field_extension(field_source.replace('MvPolynomial.map (Rat.castHom K) rhs',
                                                                      'MvPolynomial.map (Rat.castHom K) (rhs + 1)'), source))
    result['altered_inputs_rejected'].append('source_scalar_extension_target')
    manifest_path = ROOT / 'formal/results/polynomial-bridge-export.json'
    manifest, bindings = manifest_bindings(manifest_path,
        [SOURCE, case_path, sparse_path, model_path, matrix_path, field_path,
         ROOT / 'formal/HodgeLab/RowCertificate.lean'])
    result['lean_negative_control_expectations'] = lean_mutation_expectations(manifest, data)
    result['source_lf_sha256'].update(bindings)
    result['formal_export_manifest_audit'] = dict(status='PASS', modules=manifest['modules'],
        theorem_names=manifest['theorem_names'], source_bindings=len(bindings),
        scope='Hashes and theorem/definition scope checked here. Lean compilation and kernel replay require the separate formal receipt.')
    result['lean_execution_claimed'] = False
    result['elapsed_seconds'] = round(time.perf_counter() - start, 3)
    OUT.mkdir(parents=True, exist_ok=True)
    output_path = OUT / 'independent-validation.json'
    output_path.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(status='PASS', output=output_path.relative_to(ROOT).as_posix(),
                         source_bindings=len(result['source_lf_sha256']),
                         altered_inputs_rejected=len(result['altered_inputs_rejected']),
                         elapsed_seconds=result['elapsed_seconds'])))


if __name__ == '__main__':
    main()

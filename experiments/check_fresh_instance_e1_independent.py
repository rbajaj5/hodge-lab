"""Independent finite-field rank audit; requires SymPy only to parse source F/A.

This implementation uses no project algebra code. Rows are exponent tuples,
and sparse elimination chooses the largest exponent tuple as pivot.
Modular ranks are lower bounds on characteristic-zero ranks, not by themselves
upper bounds. For d<=5, Koszul fields and gradient lifts certify equality.
"""
import hashlib
import itertools
import json
import math
from fractions import Fraction
from pathlib import Path
import sys
import time
import sympy as s

if not __debug__:
    raise RuntimeError('Run without -O: exact checks use assertions.')

REPO = Path(sys.argv[1])
MAXDEG = int(sys.argv[2]) if len(sys.argv) > 2 else 5
OUTPUT = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(__file__).with_suffix('.json')
P = 1009
x = s.symbols('X0 X1 X2 Y0 Y1 Y2')


def monomials(n, d):
    if n == 1:
        return [(d,)]
    return [(a,) + t for a in range(d + 1) for t in monomials(n - 1, d - a)]


def addexp(a, b):
    return tuple(i + j for i, j in zip(a, b))


def canonical_sha(path):
    """Universal-newline UTF-8 hash survives Git CRLF/LF checkout conversion."""
    return hashlib.sha256(path.read_text(encoding='utf-8').encode('utf-8')).hexdigest()


def echelon(columns):
    basis = {}
    for column in columns:
        c = {m: int(v) % P for m, v in column.items() if int(v) % P}
        while c:
            pivot = max(c)
            if pivot not in basis:
                inverse = pow(c[pivot], -1, P)
                basis[pivot] = {j: v * inverse % P for j, v in c.items()}
                break
            scale = c[pivot]
            for j, v in basis[pivot].items():
                value = (c.get(j, 0) - scale * v) % P
                if value:
                    c[j] = value
                else:
                    c.pop(j, None)
    return basis


def rank(columns):
    return len(echelon(columns))


def reduce_mod(column, basis):
    c = {m: int(v) % P for m, v in column.items() if int(v) % P}
    for pivot in sorted(basis, reverse=True):
        if pivot in c:
            scale = c[pivot]
            for j, v in basis[pivot].items():
                value = (c.get(j, 0) - scale * v) % P
                if value:
                    c[j] = value
                else:
                    c.pop(j, None)
    return c


def modcoeff(poly):
    return {m: int(v.p) * pow(int(v.q), -1, P) % P for m, v in poly.terms()}


result = {'prime': P, 'method': __doc__, 'hash_policy': 'SHA256 of UTF-8 text after universal-newline conversion to LF', 'runs': [], 'hessian_degree5': [], 'rational_square_dual_checks': [], 'source_sha256': {}}
for instance in ['cycle-three', 'mixed-biweight']:
    folder = REPO / 'sources' / 'sextics' / 'data' / instance
    text = {}
    for line in (folder / 'instance.rec').read_text(encoding='utf-8').splitlines():
        for key in ['F', 'A', 'q']:
            if line.startswith(key + ': '):
                text[key] = line[len(key) + 2:]
    assert text['q'] == '1'
    for filename in ['instance.rec', 'why.md', 'provenance.json']:
        path = folder / filename
        result['source_sha256'][str(path.relative_to(REPO)).replace('\\', '/')] = canonical_sha(path)
    f = s.Poly(s.sympify(text['F']), x)
    a = s.Poly(s.sympify(text['A']), x)
    assert all(sum(m) == 6 for m, _ in f.terms())
    assert all(sum(m) == 6 for m, _ in a.terms())
    derivatives = [f.diff(y) for y in x]
    gradients = [modcoeff(poly) for poly in derivatives]
    aa = modcoeff(a)
    # Exact identities and a visible diagonal coefficient minor establish
    # independence of the 15 constant Koszul numerator fields at d=4.
    koszul_pairs = list(itertools.combinations(range(6), 2))
    for i, j in koszul_pairs:
        assert (derivatives[j] * derivatives[i] - derivatives[i] * derivatives[j]).is_zero
    pure_coefficients = [[poly.coeff_monomial(y**5) for y in x] for poly in derivatives]
    assert pure_coefficients == [[6 if i == j else 0 for j in range(6)] for i in range(6)]
    linear_koszul = []
    for i, j in koszul_pairs:
        for u in monomials(6, 1):
            field = {(i, addexp(m, u)): v for m, v in gradients[j].items()}
            field.update({(j, addexp(m, u)): -v for m, v in gradients[i].items()})
            linear_koszul.append(field)
    assert rank(linear_koszul) == 90
    assert rank(gradients) == 6
    for degree in range(MAXDEG + 1):
        start = time.perf_counter()
        columns = [{addexp(m, u): v for m, v in gradient.items()}
                   for gradient in gradients for u in monomials(6, degree + 1)]
        n_columns = len(columns)
        rank_n = rank(columns)
        denominator_columns = [{addexp(m, u): v for m, v in aa.items()}
                               for u in monomials(6, degree)]
        rank_full = rank(columns + denominator_columns)
        record = {'instance': instance, 'degree': degree,
                  'numerator_columns': n_columns, 'denominator_columns': len(denominator_columns),
                  'rank_n_mod_p': rank_n, 'rank_augmented_mod_p': rank_full,
                  'denominator_projection_dimension_mod_p': len(denominator_columns) - rank_full + rank_n,
                  'seconds': time.perf_counter() - start}
        if degree <= 3:
            assert rank_n == n_columns
            assert rank_full == n_columns + len(denominator_columns)
            record['char_zero_rank_certificate'] = 'Modular full column rank equals the column-count upper bound.'
        elif degree == 4:
            assert rank_n == n_columns - len(koszul_pairs)
            assert rank_full == n_columns + len(denominator_columns) - len(koszul_pairs)
            record['char_zero_rank_certificate'] = '15 independent rational Koszul kernel vectors give matching rank upper bounds.'
        elif degree == 5:
            assert rank_n == n_columns - 90
            assert rank_full == n_columns + len(denominator_columns) - 90 - 6
            record['char_zero_rank_certificate'] = '90 independent rational linear Koszul fields and 6 independent gradient denominator lifts give matching rank upper bounds.'
        else:
            record['char_zero_rank_certificate'] = None
        result['runs'].append(record)
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(record), flush=True)
    # Necessary E2 for d=5: every D=a.grad(F) and every normalized lift is
    # N=Aa+K with K in the verified Koszul span. Modulo J=(grad F), all
    # B_D(K), D*(a.grad A), and F*quotient vanish. The remaining condition
    # is A*a^T Hess(F)*a=0 in S_10/J_10.
    jacobian10 = [{addexp(m, u): v for m, v in gradient.items()}
                  for gradient in gradients for u in monomials(6, 5)]
    jbasis = echelon(jacobian10)
    symmetric_pairs = list(itertools.combinations_with_replacement(range(6), 2))
    hessian_columns = [modcoeff(a * f.diff(x[i]).diff(x[j]) * (1 if i == j else 2))
                       for i, j in symmetric_pairs]
    residual_columns = [reduce_mod(column, jbasis) for column in hessian_columns]
    quotient_rank = rank(residual_columns)
    augmented_rank = rank(jacobian10 + hessian_columns)
    assert len(jbasis) == 1497 and augmented_rank == 1518 and quotient_rank == 21
    hessian_result = {'instance': instance, 'degree_D': 5,
                      'symmetric_parameter_monomials': [list(p) for p in symmetric_pairs],
                      'jacobian_degree10_rank_mod_p': len(jbasis),
                      'augmented_rank_mod_p': augmented_rank,
                      'quotient_hessian_rank_mod_p': quotient_rank,
                      'char_zero_rank_certificate': 'J10 rank is exactly1497 by the degree4 Koszul upper bound; augmented modularrank1518 and 21 added columns force quotientrank21 overQ andC.',
                      'conclusion': 'Necessary quadratic equations force every a_i*a_j=0 overC, hence every a_i=0; no degree5 legal denominator.'}
    result['hessian_degree5'].append(hessian_result)
    packet = REPO / 'results' / 'fresh-instance-e1' / instance / 'degree-5-e2.json'
    if packet.exists():
        data = json.loads(packet.read_text(encoding='utf-8'))
        rows10 = monomials(6, 10)
        qcoeff = lambda poly: {m: Fraction(int(v.p), int(v.q)) for m, v in poly.terms()}
        rational_jac = [{addexp(m, u): v for m, v in qcoeff(gradient).items()}
                        for gradient in derivatives for u in monomials(6, 5)]
        rational_hess = [qcoeff(a * f.diff(x[i]).diff(x[j]) * (1 if i == j else 2))
                         for i, j in symmetric_pairs]
        checked = []
        for witness in data['square_obstructions']:
            coordinate = [str(y) for y in x].index(witness['coordinate'])
            dual = {rows10[index]: Fraction(coefficient)
                    for index, coefficient in witness['functional']}
            pairing = lambda poly: sum((v * dual.get(m, 0) for m, v in poly.items()), Fraction())
            assert all(pairing(column) == 0 for column in rational_jac)
            assert [pairing(column) for column in rational_hess] == [int(i == j == coordinate) for i, j in symmetric_pairs]
            checked.append(coordinate)
        assert sorted(checked) == list(range(6))
        result['rational_square_dual_checks'].append({
            'instance': instance, 'packet_sha256': canonical_sha(packet),
            'status': 'PASS', 'checked_square_functionals': len(checked),
            'exact_jacobian_pairings': len(checked) * len(rational_jac),
            'exact_hessian_pairings': len(checked) * len(rational_hess),
            'method': 'Source parsed and differentiated independently with SymPy; exported functionals paired using standard-library Fraction.'})
    OUTPUT.write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(hessian_result), flush=True)

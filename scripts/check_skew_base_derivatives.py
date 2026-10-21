"""Independent exact polynomial replay of bounded source-primitive duals.

Does not import the search, use its matrix, or perform Gaussian elimination.
The protected record.json supplies F; the prior residue derivation is reused.
"""
from pathlib import Path
import argparse
import hashlib
import json
import math
import platform
import sys
import time
import sympy as s

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/skew-base-derivatives'
VARS = U, r, w, t = s.symbols('U r w t')
CHECKS = []


def require(name, condition):
    if not condition:
        raise ValueError('FAIL: ' + name)
    CHECKS.append(name)


def zero(name, expression):
    require(name, s.cancel(expression) == 0)


def protected_source():
    pins = json.loads((OUT / 'inputs.json').read_text(encoding='utf-8'))
    for item in pins['local_inputs']:
        require('input hash ' + item['path'], hashlib.sha256((ROOT / item['path']).read_bytes()).hexdigest() == item['sha256'])
    old = json.loads((ROOT / 'results/chi-target-source/inputs.json').read_text(encoding='utf-8'))
    for name in ['record.json', 'provenance.json']:
        relative = 'data/one-reflection-skew/' + name
        item = next(i for i in old['files'] if i['path'] == relative)
        raw = (ROOT / 'results/chi-target-source/inputs' / relative).read_bytes()
        require('source SHA-256 ' + name, hashlib.sha256(raw).hexdigest() == item['sha256'])
        blob = hashlib.sha1(b'blob ' + str(len(raw)).encode('ascii') + b'\0' + raw).hexdigest()
        require('source Git blob ' + name, blob == item['git_blob'])
        current = next(i for i in pins['reused_upstream_files'] if i['upstream_path'] == relative)
        require('unchanged pinned blob ' + name, current['current_blob'] == blob)
    record = json.loads((ROOT / 'results/chi-target-source/inputs/data/one-reflection-skew/record.json').read_text(encoding='utf-8'))
    X = s.symbols('X0 X1 X2 Y0 Y1 Y2')
    x, z = s.symbols('x z')
    def polynomial(field):
        return sum(s.Rational(c) * s.prod(v**e for v, e in zip(X, powers)) for c, powers in record[field]['terms'])
    require('protected target and q', record['id'] == 'one-reflection-skew' and record['q'] == 1)
    substitution = dict(zip(X, (x, r*x, w*x, 1, t, z)))
    zero('protected source on chart', polynomial('A').subs(substitution, simultaneous=True) - x**3)
    transformed = s.Poly(polynomial('F').subs(substitution, simultaneous=True) - z**6, x)
    require('even square quotient', all(e[0] % 2 == 0 for e, _ in transformed.terms()))
    P = sum(c * U**(e[0] // 2) for e, c in transformed.terms())
    return s.Poly(P, *VARS, domain=s.QQ)


def operator(P, vector):
    return sum(5*s.diff(P, v)*f - 6*P*s.diff(f, v) for v, f in zip(VARS, vector))


def formula_checks(mutation):
    # Derive the divergence density directly, with z_j = -P_j/(6 z^5).
    z, p = s.symbols('z p', nonzero=True)
    fj, dfj, pj = s.symbols('f df p_j')
    differentiated = dfj/z**5 + fj*(-5/z**6)*(-pj/(6*z**5))
    zero('ambient differential density', (6*z**11*differentiated).expand().subs(z**6, -p) - (5*pj*fj-6*p*dfj))
    n, dn, den, dden = s.symbols('n dn D dD', nonzero=True)
    zero('quotient derivative clearing', den**2*(5*pj*n/den-6*p*(dn/den-n*dden/den**2)) - (5*den*pj*n-6*p*(den*dn-n*dden)))
    zero('source scale', 6*s.Rational(5, 72)-s.Rational(5, 12))
    zero('integral scaling', 84*s.Rational(5, 12)-35)
    # Manufactured positive controls: base derivatives really can solve the
    # absolute equation even when the corresponding fiber is not exact.
    for j, base in enumerate(VARS[1:], 1):
        toy = U**3 + U + base
        vector = [s.Integer(0)]*4
        vector[j] = U**2/12
        value = operator(toy, vector)
        if mutation == 'drop-base' and j == 1:
            value = operator(toy, [vector[0], 0, 0, 0])
        zero('base-only positive control ' + str(base), value - s.Rational(5, 12)*U**2)
    H = U**3 + U + 1
    toy = r**2*H
    D = 192*r*H
    vector = [0, 5*U**2/D, 0, 0]
    zero('rational denominator positive control', operator(toy, vector) - s.Rational(5, 12)*U**2)
    wrong = 5*s.diff(toy, r)*vector[1]  # incorrectly ignore derivative of 1/D
    zero('omitted denominator term residual', wrong-s.Rational(5, 12)*U**2+s.Rational(5, 32)*U**2)
    value = wrong if mutation == 'drop-denominator-derivative' else operator(toy, vector)
    zero('denominator differentiation required', value-s.Rational(5, 12)*U**2)


def verify_case(P, D, degree, record, mutation):
    expr = P.as_expr()
    zero('saved source ' + record['denominator_label'], s.sympify(record['P'])-expr)
    zero('saved denominator ' + record['denominator_label'], s.sympify(record['denominator'])-D)
    require('fixed denominator metadata', record['denominator_power'] == 1 and record['operator_scale'] == 84)
    require('variable and component conventions', record['variables'] == list(map(str, VARS)) and record['component_order'] == list(map(str, VARS)))
    require('bounded degree and exclusion outcome', record['numerator_total_degree_bound'] == degree and record['outcome'] == 'excluded_in_tested_family')
    require('search file binding', record['search_script_sha256'] == hashlib.sha256((ROOT/'scripts/search_skew_base_derivatives.py').read_bytes()).hexdigest())
    dual = {tuple(item['exponent']): s.Rational(item['coefficient']) for item in record['dual']}
    require('dual exponents valid and unique', len(dual) == len(record['dual']) and all(len(e) == 4 and all(isinstance(k, int) and k >= 0 for k in e) for e in dual))
    if mutation == 'drop-dual-term':
        del dual[next(iter(dual))]
    def pair(poly):
        return sum(c*poly.coeff_monomial(e) for e, c in dual.items())
    rhs = s.Poly(35*U**2*D**2, *VARS, domain=s.QQ)
    require('dual separates full RHS', pair(rhs) == 1)
    # Enumerate through a different API and reconstruct each polynomial column
    # by differentiation and multiplication, not shifted coefficient templates.
    mons = list(s.polys.monomials.itermonomials(VARS, degree))
    require('complete monomial count', len(mons) == math.comb(degree+4, 4))
    DP = s.Poly(D, *VARS, domain=s.QQ)
    union = set(rhs.monoms())
    nonzeros = 0
    for j, v in enumerate(VARS):
        for mon in mons:
            NP = s.Poly(mon, *VARS, domain=s.QQ)
            column = 84*(5*DP*P.diff(v)*NP - 6*P*(DP*NP.diff(v)-NP*DP.diff(v)))
            require('dual annihilates full column', pair(column) == 0)
            union.update(column.monoms() if not column.is_zero else [])
            nonzeros += len(column.terms()) if not column.is_zero else 0
    count = 4*len(mons)
    require('complete matrix dimensions', record['columns'] == count and record['rows'] == len(union))
    return {'denominator': record['denominator_label'], 'degree_bound': degree,
            'rows': len(union), 'columns_checked': count, 'nonzero_entries': nonzeros,
            'dual_terms': len(dual), 'dual_rhs_pairing': '1', 'all_column_pairings_zero': True}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--mutation', choices=['drop-base', 'drop-denominator-derivative', 'drop-dual-term'])
    args = parser.parse_args()
    start = time.perf_counter()
    P = protected_source()
    formula_checks(args.mutation)
    cases, hashes = [], {}
    for label, D in [('1', s.Integer(1)), ('r', r), ('t', t), ('a', s.Poly(P.as_expr(), U).coeff_monomial(U**3))]:
        for degree in [0, 2, 4]:
            path = OUT / f'search-{label}-degree{degree}.json'
            raw = path.read_bytes()
            hashes[path.name] = hashlib.sha256(raw).hexdigest()
            record = json.loads(raw.decode('utf-8'))
            require('case filename agrees', record['denominator_label'] == label)
            cases.append(verify_case(P, D, degree, record, args.mutation))
    if args.mutation:
        raise ValueError('FAIL: mutation was not detected')
    receipt = {'status': 'PASS', 'method': 'QQ polynomial column reconstruction; no matrix or elimination imported from search',
               'python': platform.python_version(), 'sympy': s.__version__, 'seconds': round(time.perf_counter()-start, 6),
               'required_checks': len(CHECKS), 'full_columns_checked': sum(c['columns_checked'] for c in cases),
               'cases': cases, 'certificate_sha256': hashes,
               'checker_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'scope': 'Four fixed denominators, total numerator degree <=0,2,4, all four components. No general rational or physical certificate exclusion.'}
    (OUT/'verification.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'status': 'PASS', 'required_checks': len(CHECKS), 'columns': receipt['full_columns_checked'], 'seconds': receipt['seconds']}))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print(str(error))
        sys.exit(1)

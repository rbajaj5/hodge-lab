#!/usr/bin/env python3
"""Exact bounded Jacobian-ideal necessary-condition scans for fresh instances.

Only Python's standard library is used.  For q=1 a certificate implies
AD in (partial_i F), by coprimality followed by homogeneous Euler normalization.
The exported duals and kernel lifts certify the entire bounded E1 kernel, not
the remaining nonlinear divergence condition.  No certificate is asserted.
"""
from __future__ import annotations

import argparse
import ast
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results' / 'fresh-instance-e1'
NAMES = ('X0', 'X1', 'X2', 'Y0', 'Y1', 'Y2')
ZERO = (0,) * 6


def add(a, b, scale=Q(1)):
    for k, v in b.items():
        n = a.get(k, Q(0)) + scale * v
        if n:
            a[k] = n
        else:
            a.pop(k, None)
    return a


def multiply(a, b):
    c = {}
    for m, u in a.items():
        for n, v in b.items():
            t = tuple(x + y for x, y in zip(m, n))
            c[t] = c.get(t, Q(0)) + u * v
    return {m: v for m, v in c.items() if v}


def parse_poly(source):
    def visit(node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return {ZERO: Q(node.value)} if node.value else {}
        if isinstance(node, ast.Name) and node.id in NAMES:
            return {tuple(int(i == NAMES.index(node.id)) for i in range(6)): Q(1)}
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return {m: -v for m, v in visit(node.operand).items()}
        if isinstance(node, ast.BinOp):
            a = visit(node.left)
            if isinstance(node.op, ast.Pow):
                assert isinstance(node.right, ast.Constant)
                n = node.right.value
                assert type(n) is int and n >= 0
                c = {ZERO: Q(1)}
                for _ in range(n):
                    c = multiply(c, a)
                return c
            b = visit(node.right)
            if isinstance(node.op, ast.Add):
                return add(a, b)
            if isinstance(node.op, ast.Sub):
                return add(a, b, Q(-1))
            if isinstance(node.op, ast.Mult):
                return multiply(a, b)
            if isinstance(node.op, ast.Div):
                assert set(b) == {ZERO} and b[ZERO]
                return {m: v / b[ZERO] for m, v in a.items()}
        raise ValueError(f'Unsupported expression: {ast.dump(node)}')
    return visit(ast.parse(source, mode='eval').body)


def monos(degree, count=6):
    if count == 1:
        return [(degree,)]
    return [(i,) + rest for i in range(degree + 1)
            for rest in monos(degree - i, count - 1)]


def derivative(poly, i):
    out = {}
    for m, c in poly.items():
        if m[i]:
            n = list(m)
            n[i] -= 1
            out[tuple(n)] = c * m[i]
    return out


def sha(path):
    # Sources and packets are UTF-8 text: bind content independently of checkout EOLs.
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def target(instance):
    folder = ROOT / 'sources' / 'sextics' / 'data' / instance
    path = folder / 'instance.rec'
    fields = {}
    for line in path.read_text(encoding='utf-8').splitlines():
        for key in ('F', 'A', 'q'):
            if line.startswith(key + ': '):
                fields[key] = line[len(key) + 2:]
    assert fields['q'] == '1'
    F, A = parse_poly(fields['F']), parse_poly(fields['A'])
    assert {sum(m) for m in F} == {6}
    assert {sum(m) for m in A} == {6}
    bindings = {str(p.relative_to(ROOT)).replace('\\', '/'): sha(p)
                for p in (path, folder / 'why.md', folder / 'provenance.json')}
    return F, A, fields, bindings


def matrices(instance, degree):
    F, A, fields, bindings = target(instance)
    rows, den, num = monos(degree + 6), monos(degree), monos(degree + 1)
    lookup = {m: i for i, m in enumerate(rows)}
    jac = []
    for i in range(6):
        part = derivative(F, i)
        for n in num:
            jac.append({lookup[tuple(a + b for a, b in zip(m, n))]: c
                        for m, c in part.items()})
    ad = [{lookup[tuple(a + b for a, b in zip(m, n))]: c
           for m, c in A.items()} for n in den]
    return rows, den, num, jac, ad, fields, bindings


def obvious_denominators(instance, degree, den):
    """The degree-d part of J(F) is always killed by multiplication by A mod J(F)."""
    if degree < 5:
        return []
    F, _, _, _ = target(instance)
    lookup = {m: i for i, m in enumerate(den)}
    return [{lookup[tuple(x + y for x, y in zip(m, n))]: c
             for m, c in derivative(F, i).items()}
            for i in range(6) for n in monos(degree - 5)]


def reduce_vector(v, basis, combo=None):
    v = dict(v)
    if combo is not None:
        combo = dict(combo)
    for p in sorted(basis):
        c = v.get(p)
        if c:
            b, source = basis[p]
            add(v, b, -c)
            if combo is not None:
                add(combo, source, -c)
    return v, combo


def column_basis(cols, track=True):
    basis = {}
    for i, col in enumerate(cols):
        v, combo = reduce_vector(col, basis, {i: Q(1)} if track else None)
        if v:
            p = min(v)
            scale = v[p]
            basis[p] = ({k: c / scale for k, c in v.items()},
                        {k: c / scale for k, c in combo.items()} if track else {})
    return basis


def dot(a, b):
    if len(a) > len(b):
        a, b = b, a
    return sum((c * b.get(k, Q(0)) for k, c in a.items()), Q(0))


def pack(v):
    return [[k, str(c)] for k, c in sorted(v.items())]


def unpack(v):
    return {int(k): Q(c) for k, c in v}


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding='utf-8', newline='\n') as output:
        output.write(json.dumps(value, indent=2) + '\n')


def compute(instance, degree):
    start = time.perf_counter()
    rows, den, num, jac, ad, fields, bindings = matrices(instance, degree)
    jb = column_basis(jac)
    db, kernel = {}, []
    reduced_ad = []
    for i, col in enumerate(ad):
        v, jc = reduce_vector(col, jb, {})
        reduced_ad.append(dict(v))
        dc = {i: Q(1)}
        for p in sorted(db):
            c = v.get(p)
            if c:
                b, bd, bj = db[p]
                add(v, b, -c)
                add(dc, bd, -c)
                add(jc, bj, -c)
        if v:
            p, scale = min(v), v[min(v)]
            db[p] = ({k: c / scale for k, c in v.items()},
                     {k: c / scale for k, c in dc.items()},
                     {k: c / scale for k, c in jc.items()})
        else:
            kernel.append({'denominator': pack(dc),
                           'numerator': pack({k: -c for k, c in jc.items()})})
    duals = []
    for row in sorted(db):
        dual = {row: Q(1)}
        for p in sorted(jb, reverse=True):
            c = dot(dual, jb[p][0])
            if c:
                add(dual, {p: Q(1)}, -c)
        values = {i: dot(dual, col) for i, col in enumerate(ad)}
        duals.append({'output_row': row, 'functional': pack(dual),
                      'denominator_constraint': pack({k: c for k, c in values.items() if c})})
    result = {
        'schema': 'fresh-instance-e1-v1', 'instance': instance, 'degree': degree,
        'q': 1, 'target': fields, 'source_sha256': bindings,
        'sha256_policy': 'UTF-8 bytes with CRLF normalized to LF',
        'monomial_order': 'ascending lexicographic exponent tuple; X0,X1,X2,Y0,Y1,Y2',
        'numerator_column_order': 'component i, then homogeneous monomial degree d+1',
        'dimensions': {'coefficient_rows': len(rows), 'denominator_columns': len(den),
                       'numerator_columns': len(jac), 'jacobian_rank': len(jb),
                       'augmented_rank': len(jb) + len(db),
                       'denominator_image_rank': len(db), 'denominator_kernel_dimension': len(kernel)},
        'jacobian_denominator_subspace_dimension': len(column_basis(obvious_denominators(instance, degree, den), track=False)),
        'sparsity': {'jacobian_nonzeros': sum(map(len, jac)),
                     'AD_nonzeros': sum(map(len, ad)),
                     'reduced_AD_nonzeros': sum(map(len, reduced_ad))},
        'dual_obstructions': duals, 'kernel_lifts': kernel,
        'matrix_plot': {'residual_entries': [[r, c, str(v)] for c, col in enumerate(reduced_ad)
                                             for r, v in sorted(col.items())]},
        'elapsed_seconds': time.perf_counter() - start,
        'scope': 'Complete degree-d necessary E1 condition only; nonlinear divergence, coprimality, and full certificate not established.'}
    path = OUT / instance / f'degree-{degree}.json'
    write_json(path, result)
    print(json.dumps({'instance': instance, 'degree': degree, 'status': 'complete',
                      'dimensions': result['dimensions'], 'seconds': result['elapsed_seconds']}), flush=True)


def linear_combination(cols, coeffs):
    v = {}
    for i, c in coeffs.items():
        assert 0 <= i < len(cols)
        add(v, cols[i], c)
    return v


def check_dual(item, jac, ad, row_count):
    dual = unpack(item['functional'])
    assert all(0 <= k < row_count for k in dual)
    for col in jac:
        assert dot(dual, col) == 0
    values = {i: dot(dual, col) for i, col in enumerate(ad)}
    values = {i: c for i, c in values.items() if c}
    assert values == unpack(item['denominator_constraint'])
    return values


def check_kernel(item, jac, ad):
    dc, nc = unpack(item['denominator']), unpack(item['numerator'])
    assert dc
    assert linear_combination(ad, dc) == linear_combination(jac, nc)
    return dc


def syzygies_degree_six(instance):
    """All 90 linear multiples of elementary Koszul fields of grad F."""
    F, _, _, _ = target(instance)
    parts = [derivative(F, i) for i in range(6)]
    num = monos(6)
    lookup = {m: j for j, m in enumerate(num)}
    fields = []
    for i in range(6):
        for j in range(i + 1, 6):
            for n in monos(1):
                v = {}
                for component, poly, sign in ((i, parts[j], 1), (j, parts[i], -1)):
                    for m, c in poly.items():
                        shifted = tuple(x + y for x, y in zip(m, n))
                        v[component * len(num) + lookup[shifted]] = sign * c
                fields.append(v)
    return fields


def hessian_columns(instance):
    F, A, _, _ = target(instance)
    rows = monos(10)
    lookup = {m: i for i, m in enumerate(rows)}
    pairs = [(i, j) for i in range(6) for j in range(i, 6)]
    cols = []
    for i, j in pairs:
        p = multiply(A, derivative(derivative(F, i), j))
        scale = 1 if i == j else 2
        cols.append({lookup[m]: scale * c for m, c in p.items()})
    return pairs, cols


def quotient_dual(weights, jac_basis):
    dual = dict(weights)
    for p in sorted(jac_basis, reverse=True):
        c = dot(dual, jac_basis[p][0])
        if c:
            add(dual, {p: Q(1)}, -c)
    return dual


def compute_e2(instance):
    start = time.perf_counter()
    rows, _, _, jac, _, fields, bindings = matrices(instance, 4)
    _, den5, _, jac5, _, _, _ = matrices(instance, 5)
    jb = column_basis(jac, track=False)
    syzygies = syzygies_degree_six(instance)
    for s in syzygies:
        assert linear_combination(jac5, s) == {}
    syzygy_rank = len(column_basis(syzygies, track=False))
    jac5_rank = len(column_basis(jac5, track=False))
    assert syzygy_rank == len(jac5) - jac5_rank == 90
    pairs, hcols = hessian_columns(instance)
    residual = [reduce_vector(c, jb)[0] for c in hcols]
    rowkeys = sorted(set().union(*(set(c) for c in residual)))
    eq = [{j: c[r] for j, c in enumerate(residual) if r in c} for r in rowkeys]
    rb = column_basis(eq)
    witnesses, unresolved = [], []
    for i in range(6):
        diagonal = pairs.index((i, i))
        rem, combo = reduce_vector({diagonal: Q(1)}, rb, {})
        if rem:
            unresolved.append({'coordinate': NAMES[i], 'rowspace_remainder': pack(rem)})
            continue
        raw = {rowkeys[k]: -c for k, c in combo.items()}
        dual = quotient_dual(raw, jb)
        assert all(dot(dual, c) == 0 for c in jac)
        assert [dot(dual, c) for c in hcols] == [Q(int(j == diagonal)) for j in range(21)]
        witnesses.append({'coordinate': NAMES[i], 'quadratic_column': diagonal,
                          'functional': pack(dual)})
    data = {'schema': 'fresh-instance-e2-v1', 'instance': instance, 'degree': 5,
            'target': fields, 'source_sha256': bindings,
            'sha256_policy': 'UTF-8 bytes with CRLF normalized to LF',
            'degree5_e1_sha256': sha(OUT / instance / 'degree-5.json'),
            'quadratic_column_pairs': [[NAMES[i], NAMES[j]] for i, j in pairs],
            'dimensions': {'degree10_coefficient_rows': len(rows), 'jacobian_rank': len(jb),
                           'quadratic_columns': 21, 'quotient_quadratic_rank': len(rb),
                           'degree6_numerator_syzygy_dimension': syzygy_rank,
                           'degree6_koszul_span_dimension': syzygy_rank},
            'square_obstructions': witnesses, 'unresolved_squares': unresolved,
            'degree5_excluded': len(witnesses) == 6,
            'matrix_plot': {'residual_entries': [[r, c, str(v)] for c, col in enumerate(residual)
                                                 for r, v in sorted(col.items())]},
            'elapsed_seconds': time.perf_counter() - start,
            'scope': 'Necessary E2 quotient only. All six square obstructions imply degree-five exclusion; this is not a certificate or higher-degree exclusion.'}
    write_json(OUT / instance / 'degree-5-e2.json', data)
    print(json.dumps({'instance': instance, 'E2': data['dimensions'],
                      'squares': [v['coordinate'] for v in witnesses],
                      'unresolved_squares': unresolved, 'seconds': data['elapsed_seconds']}), flush=True)


def check_square(witness, pairs, jac, hcols):
    i = NAMES.index(witness['coordinate'])
    diagonal = pairs.index((i, i))
    assert witness['quadratic_column'] == diagonal
    dual = unpack(witness['functional'])
    assert all(dot(dual, c) == 0 for c in jac)
    assert [dot(dual, c) for c in hcols] == [Q(int(j == diagonal)) for j in range(21)]
    return NAMES[i]


def verify_e2(path):
    start = time.perf_counter()
    data = json.loads(path.read_text(encoding='utf-8'))
    assert data['schema'] == 'fresh-instance-e2-v1' and data['degree'] == 5
    assert data['sha256_policy'] == 'UTF-8 bytes with CRLF normalized to LF'
    instance = data['instance']
    e1path = OUT / instance / 'degree-5.json'
    e1 = verify_packet(e1path)
    assert data['degree5_e1_sha256'] == sha(e1path)
    assert e1['kernel_equals_jacobian_degree_piece'] and e1['jacobian_denominator_subspace_dimension'] == 6
    rows, _, _, jac, _, fields, bindings = matrices(instance, 4)
    assert data['target'] == fields and data['source_sha256'] == bindings
    _, _, _, jac5, _, _, _ = matrices(instance, 5)
    syzygies = syzygies_degree_six(instance)
    for s in syzygies:
        assert not linear_combination(jac5, s)
    syzygy_rank = len(column_basis(syzygies, track=False))
    assert syzygy_rank == len(jac5) - e1['dimensions']['jacobian_rank'] == 90
    pairs, hcols = hessian_columns(instance)
    assert data['quadratic_column_pairs'] == [[NAMES[i], NAMES[j]] for i, j in pairs]
    jb = column_basis(jac, track=False)
    residual = [reduce_vector(c, jb)[0] for c in hcols]
    qr = len(column_basis(residual, track=False))
    expected = [[r, c, str(v)] for c, col in enumerate(residual) for r, v in sorted(col.items())]
    assert data['matrix_plot']['residual_entries'] == expected
    assert data['dimensions'] == {
        'degree10_coefficient_rows': len(rows), 'jacobian_rank': len(jb),
        'quadratic_columns': 21, 'quotient_quadratic_rank': qr,
        'degree6_numerator_syzygy_dimension': syzygy_rank,
        'degree6_koszul_span_dimension': syzygy_rank}
    names = []
    for witness in data['square_obstructions']:
        names.append(check_square(witness, pairs, jac, hcols))
    assert len(names) == len(set(names))
    assert data['degree5_excluded'] == (len(names) == 6)
    if data['degree5_excluded']:
        assert data['unresolved_squares'] == []
    mutations = 0
    for witness in data['square_obstructions']:
        mutant = dict(witness)
        functional = unpack(mutant['functional'])
        first = min(functional)
        add(functional, {first: Q(1)})
        mutant['functional'] = pack(functional)
        try:
            check_square(mutant, pairs, jac, hcols)
        except AssertionError:
            mutations += 1
        else:
            raise AssertionError('Mutated square functional was accepted')
    return {'instance': instance, 'degree': 5, 'stage': 'E2', 'status': 'PASS',
            'packet_sha256': sha(path), 'square_obstructions': names,
            'degree5_excluded': len(names) == 6, 'koszul_syzygies_checked': len(syzygies),
            'exact_jacobian_annihilation_pairings': len(names) * len(jac),
            'mutations_rejected': mutations,
            'seconds': time.perf_counter() - start}


def verify_packet(path, mutation_test=True):
    start = time.perf_counter()
    data = json.loads(path.read_text(encoding='utf-8'))
    assert data['schema'] == 'fresh-instance-e1-v1' and data['q'] == 1
    assert data['sha256_policy'] == 'UTF-8 bytes with CRLF normalized to LF'
    rows, den, num, jac, ad, fields, bindings = matrices(data['instance'], data['degree'])
    assert data['target'] == fields and data['source_sha256'] == bindings
    dual_constraints, pairings = [], 0
    for item in data['dual_obstructions']:
        values = check_dual(item, jac, ad, len(rows))
        pairings += len(jac)
        dual_constraints.append(values)
    r = len(column_basis(dual_constraints, track=False))
    assert r == len(dual_constraints)
    kernel = []
    for item in data['kernel_lifts']:
        kernel.append(check_kernel(item, jac, ad))
    k = len(column_basis(kernel, track=False))
    assert k == len(kernel) and k + r == len(den)
    jb = column_basis(jac, track=False)
    dims = {'coefficient_rows': len(rows), 'denominator_columns': len(den),
            'numerator_columns': len(jac), 'jacobian_rank': len(jb),
            'augmented_rank': len(jb) + r, 'denominator_image_rank': r,
            'denominator_kernel_dimension': k}
    assert data['dimensions'] == dims
    obvious = obvious_denominators(data['instance'], data['degree'], den)
    obvious_rank = len(column_basis(obvious, track=False))
    assert data['jacobian_denominator_subspace_dimension'] == obvious_rank
    for relation in obvious:
        assert all(dot(constraint, relation) == 0 for constraint in dual_constraints)
    # Plot data is checked against a fresh exact normal form, not trusted.
    expected = [[row, c, str(v)] for c, col in enumerate(ad)
                for row, v in sorted(reduce_vector(col, jb)[0].items())]
    assert data['matrix_plot']['residual_entries'] == expected
    mutations = 0
    if mutation_test:
        if kernel:
            dc = dict(kernel[0])
            first = min(dc)
            add(dc, {first: Q(1)})
            mutant = dict(data['kernel_lifts'][0])
            mutant['denominator'] = pack(dc)
            try:
                check_kernel(mutant, jac, ad)
            except AssertionError:
                mutations += 1
            else:
                raise AssertionError('Mutated kernel lift was accepted')
        if dual_constraints:
            wrong = dict(dual_constraints[0])
            add(wrong, {0: Q(1)})
            mutant = dict(data['dual_obstructions'][0])
            mutant['denominator_constraint'] = pack(wrong)
            try:
                check_dual(mutant, jac, ad, len(rows))
            except AssertionError:
                mutations += 1
            else:
                raise AssertionError('Mutated dual constraint was accepted')
    return {'instance': data['instance'], 'degree': data['degree'], 'status': 'PASS',
            'dimensions': dims, 'exact_jacobian_annihilation_pairings': pairings,
            'jacobian_denominator_subspace_dimension': obvious_rank,
            'kernel_equals_jacobian_degree_piece': obvious_rank == k,
            'kernel_identities': k, 'mutations_rejected': mutations,
            'packet_sha256': sha(path), 'seconds': time.perf_counter() - start}


def run(instances, minimum, maximum, timeout):
    history = OUT / 'attempts.json'
    attempts = json.loads(history.read_text(encoding='utf-8')) if history.exists() else []
    for instance in instances:
        for degree in range(minimum, maximum + 1):
            start = time.perf_counter()
            cmd = [sys.executable, '-S', str(Path(__file__).resolve()), 'worker',
                   '--instances', instance, '--degree', str(degree)]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
                attempt = {'instance': instance, 'degree': degree, 'status': 'complete' if result.returncode == 0 else 'error',
                           'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
            except subprocess.TimeoutExpired as error:
                attempt = {'instance': instance, 'degree': degree, 'status': 'timeout',
                           'stdout': (error.stdout or b'').decode() if isinstance(error.stdout, bytes) else (error.stdout or ''),
                           'stderr': (error.stderr or b'').decode() if isinstance(error.stderr, bytes) else (error.stderr or '')}
            attempt.update({'time_limit_seconds': timeout, 'elapsed_seconds': time.perf_counter() - start})
            attempts.append(attempt)
            write_json(OUT / 'attempts.json', attempts)
            print(json.dumps(attempt), flush=True)


def run_e2(instances, timeout):
    history = OUT / 'e2-attempts.json'
    attempts = json.loads(history.read_text(encoding='utf-8')) if history.exists() else []
    for instance in instances:
        start = time.perf_counter()
        cmd = [sys.executable, '-S', str(Path(__file__).resolve()), 'e2-worker', '--instances', instance]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            attempt = {'instance': instance, 'degree': 5, 'stage': 'E2',
                       'status': 'complete' if result.returncode == 0 else 'error',
                       'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
        except subprocess.TimeoutExpired:
            attempt = {'instance': instance, 'degree': 5, 'stage': 'E2', 'status': 'timeout'}
        attempt.update({'time_limit_seconds': timeout, 'elapsed_seconds': time.perf_counter() - start})
        attempts.append(attempt)
        write_json(history, attempts)
        print(json.dumps(attempt), flush=True)


def main():
    if not __debug__:
        raise RuntimeError('Run without -O: exact checks use assertions')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['run', 'worker', 'e2', 'e2-worker', 'verify'])
    parser.add_argument('--instances', nargs='+', default=['cycle-three', 'mixed-biweight'])
    parser.add_argument('--max-degree', type=int, default=4)
    parser.add_argument('--min-degree', type=int, default=0)
    parser.add_argument('--degree', type=int, default=0)
    parser.add_argument('--timeout', type=float, default=60)
    args = parser.parse_args()
    if args.command == 'worker':
        compute(args.instances[0], args.degree)
    elif args.command == 'run':
        run(args.instances, args.min_degree, args.max_degree, args.timeout)
    elif args.command == 'e2':
        run_e2(args.instances, args.timeout)
    elif args.command == 'e2-worker':
        compute_e2(args.instances[0])
    else:
        checks = [verify_packet(path) for instance in args.instances
                  for path in sorted((OUT / instance).glob('degree-*.json'))
                  if '-e2.' not in path.name]
        assert checks, 'No packets found'
        write_json(OUT / 'validation.json', checks)
        e2checks = [verify_e2(path) for instance in args.instances
                    for path in sorted((OUT / instance).glob('degree-*-e2.json'))]
        if e2checks:
            write_json(OUT / 'e2-validation.json', e2checks)
        print(json.dumps(checks, indent=2))
        print(json.dumps(e2checks, indent=2))


if __name__ == '__main__':
    main()

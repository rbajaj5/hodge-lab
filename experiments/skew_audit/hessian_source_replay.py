"""Replay the small source-to-residual certificate without Gaussian elimination."""
from hessian_source import (OUT, REPO, Q, read_source, require, digest, add, mul,
                            diff, shift, monos, dot, combine)
import copy
import json
import time


def unpack(rows):
    require(len({j for j, _ in rows}) == len(rows), 'Duplicate certificate index')
    return {j: Q(c) for j, c in rows}


def verify(F, A, certificate):
    rows = monos(12)
    idx = {m: j for j, m in enumerate(rows)}
    vector = lambda p: {idx[m]: c for m, c in p.items()}
    units = [tuple(int(i == j) for j in range(6)) for i in range(6)]
    parts = [diff(F, i) for i in range(6)]
    jac = [vector(shift(g, m)) for g in parts for m in monos(7)]
    pairs = [(i, j) for i in range(5) for j in range(i, 5)]
    h = [vector(shift(mul(A, diff(parts[i], j)),
                      tuple(u + v for u, v in zip(units[i], units[j])),
                      Q(1 if i == j else 2))) for i, j in pairs]
    residuals = [unpack(c) for c in certificate['residual_columns']]
    weights = [unpack(c) for c in certificate['jacobian_membership_witnesses']]
    require(len(h) == len(residuals) == len(weights) == 15, 'Column count changed')
    for col, remainder, combination in zip(h, residuals, weights):
        require(col == add(remainder, combine(jac, combination)), 'Hessian membership identity failed')
    rowkeys = sorted(set().union(*(set(c) for c in residuals)))
    require(rowkeys == certificate['row_labels'] and len(rowkeys) == 49, 'Row labels changed')
    equations = [{j: col[r] for j, col in enumerate(residuals) if r in col} for r in rowkeys]
    duals = [unpack(d) for d in certificate['coefficient_duals']]
    require(len(duals) == 49, 'Missing dual functional')
    for dual, equation in zip(duals, equations):
        require(all(dot(dual, c) == 0 for c in jac), 'Dual does not annihilate J12')
        require({j: dot(dual, c) for j, c in enumerate(h) if dot(dual, c)} == equation,
                'Dual coefficient identity failed')
    generators = [unpack(c) for c in certificate['canonical_quadrics']]
    forward = [unpack(c) for c in certificate['canonical_from_source_rows']]
    backward = [unpack(c) for c in certificate['source_rows_from_canonical']]
    require(len(generators) == len(forward) == 4 and len(backward) == 49, 'Incomplete rowspace maps')
    for g, w in zip(generators, forward):
        require(combine(equations, w) == g, 'Canonical generator lacks source expression')
    for equation, w in zip(equations, backward):
        require(combine(generators, w) == equation, 'Source equation lacks canonical expression')


def main():
    start = time.perf_counter()
    manifest = json.loads((OUT / 'inputs.json').read_text(encoding='utf-8'))
    for item in manifest['files']:
        require(digest(REPO / item['path']) == item['lf_sha256'], 'Input checksum mismatch')
    source = REPO / manifest['protected_record']
    F, A = read_source(source)
    certificate = json.loads((OUT / 'reconstruction.json').read_text(encoding='utf-8'))
    verify(F, A, certificate)
    changed = copy.deepcopy(certificate)
    changed['residual_columns'][0][0][1] = str(Q(changed['residual_columns'][0][0][1]) + 1)
    tests = [('changed residual', F, A, changed),
             ('changed protected coupling', add(F, {(1, 1, 0, 3, 1, 0): Q(1, 7)}), A, certificate)]
    failures = []
    for label, f, a, c in tests:
        try:
            verify(f, a, c)
        except ValueError as error:
            failures.append({'control': label, 'rejected_by': str(error)})
        else:
            raise ValueError('Invalid certificate accepted: ' + label)
    output = {'status': 'PASS', 'method': 'Exact certificate replay, no elimination',
              'membership_identities': 15, 'duals': 49, 'full_J_pairings': 49 * 4752,
              'rowspace_maps': '4 canonical generators from49 source rows,49 rows from4 generators',
              'reconstruction_lf_sha256': digest(OUT / 'reconstruction.json'),
              'script_lf_sha256': digest(__import__('pathlib').Path(__file__)),
              'negative_controls': failures, 'elapsed_seconds': time.perf_counter() - start}
    (OUT / 'replay.json').write_text(json.dumps(output, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps(output))


if __name__ == '__main__':
    main()

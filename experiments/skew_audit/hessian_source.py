"""Source -> Jacobian quotient -> diagonal Hessian ideal, over Fraction.

The reconstruction stage reads only the protected record and generic arithmetic.
Saved residuals and canonical generators enter only the comparison stage.
Run with python -B -S; assertions must be enabled.
"""
from check_exclusions import (Q, REPO, NAMES, ZERO, add, mul, shift, diff,
                              parse, monos, dot, chi, pack, B)
from pathlib import Path
import ast
import hashlib
import json
import sys
import time

OUT = REPO / 'results/one-reflection-skew-hessian-source'


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def reduce(v, basis, track=False):
    v, combination = dict(v), {}
    for pivot, (row, provenance) in sorted(basis.items()):
        if pivot in v:
            c = v[pivot]
            v = add(v, row, -c)
            if track:
                combination = add(combination, provenance, -c)
    return v, combination


def echelon(columns, track=False):
    basis = {}
    for j, col in enumerate(columns):
        v, combination = reduce(col, basis, track)
        if v:
            pivot = min(v)
            scale = v[pivot]
            if track:
                combination = add(combination, {j: Q(1)})
            basis[pivot] = ({k: c / scale for k, c in v.items()},
                            {k: c / scale for k, c in combination.items()})
    return basis


def combine(columns, weights):
    result = {}
    for j, c in weights.items():
        result = add(result, columns[j], c)
    return result


def express(v, columns):
    remainder, negative = reduce(v, echelon(columns, True), True)
    require(not remainder, 'Required exact rowspace inclusion failed')
    weights = {j: -c for j, c in negative.items()}
    require(combine(columns, weights) == v, 'Rowspace transformation failed')
    return weights


def pullback(raw, basis):
    dual = dict(raw)
    for pivot, (row, _) in sorted(basis.items(), reverse=True):
        dual = add(dual, {pivot: -dot(dual, row)})
    return dual


def read_source(path):
    fields, key = {}, None
    for line in path.read_text(encoding='utf-8').splitlines():
        if line and not line[0].isspace() and ':' in line:
            key, value = line.split(':', 1)
            fields[key] = value.strip()
        elif key in ('F', 'A') and line.startswith('  '):
            fields[key] += ' ' + line.strip()
    require(fields['q'] == '1', 'This derivation requires q=1')
    return parse(fields['F']), parse(fields['A'])


def reconstruct(F, A):
    """No saved residual packet, expected quadrics or candidate functionals."""
    parts = [diff(F, i) for i in range(6)]
    units = [tuple(int(i == j) for j in range(6)) for i in range(6)]
    require(all(sum(m) == 6 for m in F) and all(sum(m) == 6 for m in A),
            'Expected homogeneous sextic F and degree-six A')
    require(combine([shift(parts[i], units[i]) for i in range(6)],
                    {i: Q(1, 6) for i in range(6)}) == F, 'Euler identity')
    zero = (0, 0, 0, 0)
    require({chi(m) for m in F} == {zero}, 'F must preserve all sign characters')
    source_characters = {chi(m) for m in A}
    require(len(source_characters) == 1, 'A must have one source character')
    source_character = next(iter(source_characters))
    rows = monos(12)
    row_index = {m: j for j, m in enumerate(rows)}
    def vector(p):
        require(all(sum(m) == 12 for m in p), 'Non-degree-12 coefficient')
        return {row_index[m]: c for m, c in p.items()}
    # Enumerate every column first; the exact character check justifies splitting.
    labels = [(i, m) for i in range(6) for m in monos(7)]
    all_jac = [vector(shift(parts[i], m)) for i, m in labels]
    require(len(all_jac) == 4752, 'All six numerator components required')
    characters = []
    for col in all_jac:
        chars = {chi(rows[r]) for r in col}
        require(len(chars) == 1, 'Jacobian column mixes character spaces')
        characters.append(next(iter(chars)))
    indices = [j for j, ch in enumerate(characters) if ch == source_character]
    jac = [all_jac[j] for j in indices]
    basis = echelon(jac, True)
    # Each pivot column has a checked expression in the reconstructed source columns.
    for col, weights in basis.values():
        require(combine(jac, weights) == col, 'Jacobian basis provenance failed')
    require(all(not reduce(c, basis)[0] for c in jac), 'Incomplete quotient basis')
    pairs = [(i, j) for i in range(5) for j in range(i, 5)]
    hessian = [vector(shift(mul(A, diff(parts[i], j)),
                            tuple(x + y for x, y in zip(units[i], units[j])),
                            Q(1 if i == j else 2))) for i, j in pairs]
    require(all(chi(rows[r]) == source_character for c in hessian for r in c),
            'A Hessian column leaves the retained character sector')
    residuals, memberships = [], []
    for col in hessian:
        remainder, negative = reduce(col, basis, True)
        weights = {j: -c for j, c in negative.items()}
        require(add(remainder, combine(jac, weights)) == col,
                'Hessian source = residual + Jacobian combination failed')
        residuals.append(remainder)
        memberships.append({indices[j]: c for j, c in weights.items()})
    rowkeys = sorted(set().union(*(set(c) for c in residuals)))
    equations = [{j: col[r] for j, col in enumerate(residuals) if r in col}
                 for r in rowkeys]
    duals = [pullback({r: Q(1)}, basis) for r in rowkeys]
    for dual, equation in zip(duals, equations):
        require(all(dot(dual, c) == 0 for c in all_jac),
                'A residual functional fails on the full Jacobian space')
        require({j: dot(dual, c) for j, c in enumerate(hessian) if dot(dual, c)}
                == equation, 'A reconstructed coefficient functional fails')
    # Check actual B_D(N), not just the displayed Hessian formula.
    dens = [shift(parts[i], units[i]) for i in range(5)]
    nums = [[shift(A, units[i]) if j == i else {} for j in range(6)]
            for i in range(5)]
    physical = [vector(B(dens[i], nums[j]) if i == j else
                       add(B(dens[i], nums[j]), B(dens[j], nums[i]))) for i, j in pairs]
    for h, p in zip(hessian, physical):
        require(not reduce(add(h, p), basis)[0], 'B/Hessian normalization mismatch')
    return dict(rows=rows, pairs=pairs, labels=labels, indices=indices, jac=all_jac,
                sector_rank=len(basis), sector_rows=sum(chi(m) == source_character for m in rows),
                source_character=source_character, hessian=hessian, physical=physical,
                residuals=residuals, memberships=memberships, rowkeys=rowkeys,
                equations=equations, duals=duals)


def main():
    start = time.perf_counter()
    require(__debug__, 'Assertions in arithmetic helpers require no -O')
    manifest = json.loads((OUT / 'inputs.json').read_text(encoding='utf-8'))
    for item in manifest['files']:
        p = REPO / item['path']
        require(digest(p) == item['lf_sha256'], 'Pinned input changed: ' + item['path'])
    source = REPO / manifest['protected_record']
    raw = source.read_bytes()
    blob = hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
    require(blob == manifest['protected_record_git_blob'], 'Protected raw Git blob changed')
    F, A = read_source(source)
    r = reconstruct(F, A)
    # Reconstruction is now complete. Only here open historical comparison data.
    saved = json.loads((REPO / manifest['residual_packet']).read_text(encoding='utf-8'))
    require(parse(saved['target']['F']) == F and parse(saved['target']['A']) == A
            and saved['target']['q'] == '1', 'Saved target does not match protected record')
    raw_parameters = [(i, j) for i in range(6) for j in range(6) if (i, j) != (5, 5)]
    require(saved['parameters'] == [[NAMES[i], NAMES[j]] for i, j in raw_parameters],
            'Raw matrix parameter order differs')
    remaining = [raw_parameters.index((i, i)) for i in range(5)]
    require(saved['remaining_parameters'] == remaining == [0, 7, 14, 21, 28],
            'Previous square reduction does not leave the diagonal family')
    raw_pairs = [(i, j) for i in range(35) for j in range(i, 35)]
    require(saved['quadratic_column_pairs'] == [list(p) for p in raw_pairs],
            'Saved quadratic-column order differs')
    local_pairs = {raw_pairs.index((remaining[i], remaining[j])): k
                   for k, (i, j) in enumerate(r['pairs'])}
    saved_rows = {}
    for row, column, coefficient in saved['matrix_plot']['residual_entries']:
        if column in local_pairs:
            j = local_pairs[column]
            require(j not in saved_rows.setdefault(row, {}), 'Duplicate saved coefficient')
            saved_rows[row][j] = Q(coefficient)
    require(r['rowkeys'] == sorted(saved_rows), 'Residual row labels disagree')
    previous_rows = [saved_rows[row] for row in r['rowkeys']]
    require(r['equations'] == previous_rows, 'Source and saved residual coefficients differ')
    # Also supply exact rowspace transformations, independent of an equality flag.
    reconstructed_from_saved = [pack(express(q, previous_rows)) for q in r['equations']]
    saved_from_reconstructed = [pack(express(q, r['equations'])) for q in previous_rows]
    canonical_path = REPO / 'experiments/one_reflection_skew_koszul_homology.py'
    tree = ast.parse(canonical_path.read_text(encoding='utf-8'))
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'canonical_quadrics')
    namespace = {'Q': Q}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), str(canonical_path), 'exec'), namespace)
    canonical = namespace['canonical_quadrics']()
    # canonical_quadrics uses exponent vectors, converted below if necessary.
    def convert(p):
        v = {}
        for m, c in p.items():
            pair = tuple(i for i, power in enumerate(m) for _ in range(power)) if len(m) == 5 else tuple(m)
            require(len(pair) == 2 and pair in r['pairs'], 'Not a quadratic in the five parameters')
            v[r['pairs'].index(pair)] = c
        return v
    generators = [convert(p) for p in canonical['P_Hess']]
    old_q3 = convert(canonical['P_full'][2])
    canonical_from_source = [pack(express(q, r['equations'])) for q in generators]
    source_from_canonical = [pack(express(q, generators)) for q in r['equations']]
    old_remainder, _ = reduce(old_q3, echelon(r['equations']))
    require(old_remainder, 'Historical Q3 unexpectedly lies in the source rowspace')
    require(all(sum(q.values()) == 0 for q in r['equations']) and sum(old_q3.values()) == Q(5, 4),
            'Historical Q3 zero-locus counterexample failed')
    # Meaningful perturbation: changing the actual skew-coupling coefficient must
    # invalidate at least one independently rebuilt quotient functional.
    altered = add(F, {(1, 1, 0, 3, 1, 0): Q(1, 7)})
    altered_jac = [shift(diff(altered, i), m) for i, m in r['labels']]
    index = {m: j for j, m in enumerate(r['rows'])}
    altered_jac = [{index[m]: c for m, c in p.items()} for p in altered_jac]
    witness = next(((i, j, dot(d, c)) for i, d in enumerate(r['duals'])
                    for j, c in enumerate(altered_jac) if dot(d, c)), None)
    require(witness is not None, 'Perturbed source escaped the projection control')
    bad_residual = dict(r['residuals'][0])
    bad_residual = add(bad_residual, {r['rowkeys'][0]: Q(1)})
    require(add(bad_residual, combine(r['jac'], r['memberships'][0])) != r['hessian'][0],
            'Corrupted residual escaped exact membership control')
    require(len(r['rowkeys']) == 49 and len(echelon(r['equations'])) == 4,
            'Expected corrected physical size/rank not reproduced')
    old_receipt = json.loads((REPO / manifest['corrected_ideal_receipt']).read_text(encoding='utf-8'))
    for relative, expected in old_receipt['source_lf_sha256'].items():
        require(digest(REPO / relative) == expected, 'Prior corrected-ideal input binding failed')
    require(old_receipt['review_script_lf_sha256'] == digest(REPO / 'experiments/check_one_reflection_skew_hessian.py'),
            'Prior corrected-ideal checker binding failed')
    for g, item in zip(generators, old_receipt['generators']):
        p = {r['pairs'].index(tuple(m)): Q(c) for m, c in item['polynomial']}
        require(p == g, 'Prior height/homology receipt refers to a different ideal')
    require(len(old_receipt['generators']) == 4 and old_receipt['status'] == 'PASS', 'Prior receipt scope')
    # Reused prerequisite receipt: no rerun of E1/square cascade or height/homology.
    prior = json.loads((REPO / manifest['prerequisite_receipt']).read_text(encoding='utf-8'))
    require(prior['status'] == 'PASS' and prior['full_E1_and_Hessian'], 'Missing prerequisite replay')
    for relative, expected in prior['source_lf_sha256'].items():
        require(digest(REPO / relative) == expected, 'Prerequisite packet binding failed')
    require(prior['script_lf_sha256'] == digest(Path(__file__).with_name('check_exclusions.py')),
            'Prerequisite checker binding failed')
    data = {
        'status': 'PASS', 'scope': 'Source-to-pure-Hessian-ideal dependency only; no new family exclusion.',
        'notebook_input_commit': manifest['notebook_input_commit'],
        'upstream_commit': manifest['upstream_commit'], 'coefficient_field': 'Q', 'q': 1,
        'variable_order': list(NAMES), 'source_F': pack(F), 'source_A': pack(A),
        'protected_record_raw_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'script_lf_sha256': digest(Path(__file__)), 'inputs_lf_sha256': digest(OUT / 'inputs.json'),
        'dimensions': {'ambient_degree12': len(r['rows']), 'full_jacobian_columns': len(r['jac']),
                       'source_character_rows': r['sector_rows'], 'source_character_columns': len(r['indices']),
                       'source_character_rank': r['sector_rank'], 'hessian_columns': len(r['pairs']),
                       'nonzero_residual_rows': len(r['rowkeys']), 'quadric_row_rank': len(echelon(r['equations']))},
        'character': list(r['source_character']), 'parameter_raw_indices': remaining,
        'quadratic_pairs': r['pairs'], 'row_labels': r['rowkeys'],
        'residual_columns': [pack(c) for c in r['residuals']],
        'jacobian_membership_witnesses': [pack(c) for c in r['memberships']],
        'coefficient_duals': [pack(d) for d in r['duals']],
        'all_full_jacobian_dual_pairings_zero': len(r['duals']) * len(r['jac']),
        'physical_B_plus_Hessian_identity_columns': len(r['physical']),
        'source_matches_saved_coefficients': True,
        'reconstructed_from_saved_rows': reconstructed_from_saved,
        'saved_from_reconstructed_rows': saved_from_reconstructed,
        'canonical_names': [g['name'] for g in old_receipt['generators']],
        'canonical_quadrics': [pack(c) for c in generators],
        'canonical_from_source_rows': canonical_from_source,
        'source_rows_from_canonical': source_from_canonical,
        'old_Q3_rowspace_remainder': pack(old_remainder),
        'old_Q3_counterexample': {'point': [1] * 5, 'all_rebuilt_rows': '0', 'Q3': '5/4'},
        'negative_controls': {'perturbed_F_term': [1, 1, 0, 3, 1, 0],
                              'coefficient_change': '1/7 -> 2/7',
                              'nonzero_dual_pairing': [witness[0], witness[1], str(witness[2])],
                              'changed_residual_rejected': True},
        'reused_not_rerun': [manifest['prerequisite_receipt'], manifest['corrected_ideal_receipt']],
        'elapsed_seconds': time.perf_counter() - start}
    (OUT / 'reconstruction.json').write_text(json.dumps(data, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'status': 'PASS', 'dimensions': data['dimensions'],
                      'negative_controls': data['negative_controls'], 'elapsed_seconds': data['elapsed_seconds']}))


if __name__ == '__main__':
    main()

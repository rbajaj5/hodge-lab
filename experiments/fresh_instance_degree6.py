#!/usr/bin/env python3
"""Exact degree-six continuation, with output isolated from the previous scan.

The complete necessary E1 map retains and identifies the F gauge.  For
cycle-three the next stages export exact off-diagonal square consequences,
then seven full-E2 diagonal consequences and five fourth-power identities.
The resulting degree-six exclusion is not an existence certificate.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

import fresh_instance_e1 as e1

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results' / 'fresh-instance-degree6'
# Deliberately redirect every reused writer to the new batch directory.
e1.OUT = OUT


def gauge_metadata(instance):
    F, _, _, _ = e1.target(instance)
    den = e1.monos(6)
    lookup = {m: i for i, m in enumerate(den)}
    gauge = {lookup[m]: c for m, c in F.items()}
    obvious = e1.obvious_denominators(instance, 6, den)
    jb = e1.column_basis(obvious, track=True)
    remainder, combo = e1.reduce_vector(gauge, jb, {})
    assert not remainder
    lift = {k: -v for k, v in combo.items()}
    assert e1.linear_combination(obvious, lift) == gauge
    return {'F_gauge_dimension': 1, 'F_denominator_vector': e1.pack(gauge),
            'F_in_J6_coefficients': e1.pack(lift),
            'J6_columns': len(obvious), 'J6_rank': len(jb),
            'J6_mod_F_dimension': len(jb) - 1,
            'interpretation': 'F is retained in the kernel, but is an excluded denominator for the coprime certificate problem.'}


def worker(instance):
    e1.compute(instance, 6)
    path = OUT / instance / 'degree-6.json'
    packet = json.loads(path.read_text(encoding='utf-8'))
    packet['gauge'] = gauge_metadata(instance)
    _, den, _, _, _, _, _ = e1.matrices(instance, 6)
    comparison = e1.column_basis(e1.obvious_denominators(instance, 6, den), track=False)
    extras = []
    for i, item in enumerate(packet['kernel_lifts']):
        vector = e1.unpack(item['denominator'])
        rem, _ = e1.reduce_vector(vector, comparison)
        if rem:
            pivot = min(rem)
            comparison[pivot] = ({j:v/rem[pivot] for j,v in rem.items()}, {})
            extras.append(i)
    packet['non_J6_representative_kernel_indices'] = extras
    packet['experiment_source_sha256'] = {
        'experiments/fresh_instance_e1.py': e1.sha(Path(e1.__file__)),
        'experiments/fresh_instance_degree6.py': e1.sha(Path(__file__))}
    e1.write_json(path, packet)


def run(instances, timeout):
    history = OUT / 'attempts.json'
    attempts = json.loads(history.read_text(encoding='utf-8')) if history.exists() else []
    for instance in instances:
        start = time.perf_counter()
        cmd = [sys.executable, '-S', str(Path(__file__).resolve()), 'worker', '--instances', instance]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            attempt = {'instance': instance, 'stage': 'complete-E1', 'degree': 6,
                       'status': 'complete' if result.returncode == 0 else 'error',
                       'returncode': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr}
        except subprocess.TimeoutExpired as error:
            attempt = {'instance': instance, 'stage': 'complete-E1', 'degree': 6, 'status': 'timeout',
                       'stdout': error.stdout.decode() if isinstance(error.stdout, bytes) else error.stdout or '',
                       'stderr': error.stderr.decode() if isinstance(error.stderr, bytes) else error.stderr or ''}
        attempt.update(time_limit_seconds=timeout, elapsed_seconds=time.perf_counter() - start)
        attempts.append(attempt)
        e1.write_json(history, attempts)
        print(json.dumps(attempt), flush=True)


def verify(instances):
    checks = []
    for instance in instances:
        path = OUT / instance / 'degree-6.json'
        check = e1.verify_packet(path)
        packet = json.loads(path.read_text(encoding='utf-8'))
        assert packet['gauge'] == gauge_metadata(instance)
        for relative, digest in packet['experiment_source_sha256'].items():
            assert e1.sha(ROOT / relative) == digest
        check['F_gauge_dimension'] = 1
        check['denominator_kernel_mod_F_dimension'] = check['dimensions']['denominator_kernel_dimension'] - 1
        check['non_J6_denominator_dimension'] = check['dimensions']['denominator_kernel_dimension'] - check['jacobian_denominator_subspace_dimension']
        _, den, _, _, _, _, _ = e1.matrices(instance, 6)
        obvious = e1.obvious_denominators(instance, 6, den)
        indices = packet['non_J6_representative_kernel_indices']
        assert len(indices) == len(set(indices)) == check['non_J6_denominator_dimension']
        extra = [e1.unpack(packet['kernel_lifts'][i]['denominator']) for i in indices]
        assert len(e1.column_basis(obvious + extra, track=False)) == check['dimensions']['denominator_kernel_dimension']
        checks.append(check)
        print(json.dumps(check), flush=True)
    e1.write_json(OUT / 'validation.json', checks)


def run_e2(timeout):
    history = OUT / 'e2-attempts.json'
    attempts = json.loads(history.read_text(encoding='utf-8')) if history.exists() else []
    for stage in ('e2-worker', 'diagonal-worker'):
        start = time.perf_counter()
        cmd = [sys.executable, '-S', str(Path(__file__).resolve()), stage, '--instances', 'cycle-three']
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            attempt = {'instance':'cycle-three', 'degree':6, 'stage':stage,
                       'status':'complete' if result.returncode==0 else 'error',
                       'returncode':result.returncode, 'stdout':result.stdout, 'stderr':result.stderr}
        except subprocess.TimeoutExpired as error:
            attempt = {'instance':'cycle-three','degree':6,'stage':stage,'status':'timeout',
                       'stdout':error.stdout.decode() if isinstance(error.stdout,bytes) else error.stdout or '',
                       'stderr':error.stderr.decode() if isinstance(error.stderr,bytes) else error.stderr or ''}
        attempt.update(time_limit_seconds=timeout,elapsed_seconds=time.perf_counter()-start)
        attempts.append(attempt)
        e1.write_json(history,attempts)
        print(json.dumps(attempt),flush=True)
        if attempt['status']!='complete':
            break


def quadratic_koszul(instance):
    """All 15*21 degree-seven elementary gradient-syzygy multiples."""
    F, _, _, _ = e1.target(instance)
    parts = [e1.derivative(F, i) for i in range(6)]
    num = e1.monos(7)
    lookup = {m: j for j, m in enumerate(num)}
    syzygies = []
    for i in range(6):
        for j in range(i + 1, 6):
            for n in e1.monos(2):
                v = {}
                for component, poly, sign in ((i, parts[j], 1), (j, parts[i], -1)):
                    for m, c in poly.items():
                        shifted = tuple(x + y for x, y in zip(m, n))
                        v[component * len(num) + lookup[shifted]] = sign * c
                syzygies.append(v)
    return syzygies


def cycle_hessian_columns(instance):
    """Columns of A L^T Hess(F) L, with L=MZ and M55=0."""
    F, A, _, _ = e1.target(instance)
    rows = e1.monos(12)
    lookup = {m: i for i, m in enumerate(rows)}
    parameters = [(i, j) for i in range(6) for j in range(6) if (i, j) != (5, 5)]
    pairs = [(a, b) for a in range(35) for b in range(a, 35)]
    cols = []
    for a, b in pairs:
        i, u = parameters[a]
        j, v = parameters[b]
        poly = e1.multiply(A, e1.derivative(e1.derivative(F, i), j))
        shifted = {}
        scale = 1 if a == b else 2
        for mon, coefficient in poly.items():
            exponent = list(mon)
            exponent[u] += 1
            exponent[v] += 1
            shifted[lookup[tuple(exponent)]] = scale * coefficient
        cols.append(shifted)
    return parameters, pairs, cols


def square_step(allowed, pairs, residual, jb, jac, cols):
    active_columns = [j for j, (a, b) in enumerate(pairs) if a in allowed and b in allowed]
    rowkeys = sorted(set().union(*(set(residual[j]) for j in active_columns)))
    eq = [{j: residual[j][r] for j in active_columns if r in residual[j]} for r in rowkeys]
    rb = e1.column_basis(eq)
    witnesses, unresolved = [], []
    for a in allowed:
        diagonal = pairs.index((a, a))
        rem, combo = e1.reduce_vector({diagonal: e1.Q(1)}, rb, {})
        if rem:
            unresolved.append(a)
            continue
        raw = {rowkeys[k]: -c for k, c in combo.items()}
        dual = e1.quotient_dual(raw, jb)
        assert all(e1.dot(dual, c) == 0 for c in jac)
        assert all(e1.dot(dual, cols[j]) == int(j == diagonal) for j in active_columns)
        witnesses.append({'parameter': a, 'square_column': diagonal, 'functional': e1.pack(dual)})
    return {'allowed_parameters': allowed, 'active_columns': active_columns,
            'quotient_rank': len(rb), 'nonzero_coefficient_rows': len(rowkeys),
            'forced_squares': witnesses, 'unresolved_parameters': unresolved}


def e2_worker(instance):
    assert instance == 'cycle-three', 'This stage currently requires kernel=J6.'
    start = time.perf_counter()
    e1path = OUT / instance / 'degree-6.json'
    packet = json.loads(e1path.read_text(encoding='utf-8'))
    assert packet['dimensions']['denominator_kernel_dimension'] == packet['gauge']['J6_rank'] == 36
    rows, _, _, jac, _, target, bindings = e1.matrices(instance, 6)
    jb = e1.column_basis(jac, track=False)
    syzygies = quadratic_koszul(instance)
    assert all(not e1.linear_combination(jac, s) for s in syzygies)
    syzygy_rank = len(e1.column_basis(syzygies, track=False))
    assert syzygy_rank == len(jac) - len(jb) == 315
    parameters, pairs, cols = cycle_hessian_columns(instance)
    residual = [e1.reduce_vector(c, jb)[0] for c in cols]
    steps, allowed = [], list(range(35))
    while allowed:
        step = square_step(allowed, pairs, residual, jb, jac, cols)
        steps.append(step)
        print(json.dumps({'instance': instance, 'E2_step': len(steps), 'allowed': len(allowed),
                          'rank': step['quotient_rank'], 'forced_squares': [w['parameter'] for w in step['forced_squares']]}), flush=True)
        if not step['forced_squares']:
            break
        allowed = step['unresolved_parameters']
    data = {'schema': 'fresh-instance-degree6-hessian-v1', 'instance': instance,
            'target': target, 'source_sha256': bindings,
            'sha256_policy': 'UTF-8 bytes with CRLF normalized to LF',
            'degree6_E1_sha256': e1.sha(e1path),
            'gauge': 'L=MZ; replace M by M-M55*I, D by D-6*M55*F, N by N-M55*A*Z; then M55=0.',
            'parameters': [[e1.NAMES[i], e1.NAMES[j]] for i, j in parameters],
            'quadratic_column_pairs': pairs,
            'dimensions': {'coefficient_rows': len(rows), 'jacobian_rank': len(jb),
                           'Koszul_fields': len(syzygies), 'Koszul_rank': syzygy_rank,
                           'numerator_kernel_dimension': len(jac)-len(jb),
                           'parameters_after_F_gauge': 35, 'quadratic_columns': len(cols)},
            'steps': steps, 'remaining_parameters': allowed,
            'degree6_excluded': not allowed,
            'matrix_plot': {'residual_entries': [[r, c, str(v)] for c, col in enumerate(residual) for r, v in sorted(col.items())]},
            'elapsed_seconds': time.perf_counter()-start,
            'scope': 'Necessary Hessian quotient after complete E1 and Euler/F gauge. A surviving parameter is not a certificate. No higher-degree conclusion.'}
    e1.write_json(OUT / instance / 'degree-6-e2.json', data)


def check_square(witness, active_columns, pairs, jac, cols):
    a = witness['parameter']
    assert witness['square_column'] == pairs.index((a, a))
    dual = e1.unpack(witness['functional'])
    assert all(e1.dot(dual, c) == 0 for c in jac)
    assert all(e1.dot(dual, cols[j]) == int(j == witness['square_column']) for j in active_columns)


def verify_e2(instance):
    start = time.perf_counter()
    path = OUT / instance / 'degree-6-e2.json'
    data = json.loads(path.read_text(encoding='utf-8'))
    assert data['schema'] == 'fresh-instance-degree6-hessian-v1'
    e1path = OUT / instance / 'degree-6.json'
    e1check = e1.verify_packet(e1path)
    assert e1check['kernel_equals_jacobian_degree_piece']
    assert data['degree6_E1_sha256'] == e1.sha(e1path)
    rows, _, _, jac, _, target, bindings = e1.matrices(instance, 6)
    assert data['target'] == target and data['source_sha256'] == bindings
    jb = e1.column_basis(jac, track=False)
    syzygies = quadratic_koszul(instance)
    assert all(not e1.linear_combination(jac, s) for s in syzygies)
    syzygy_rank = len(e1.column_basis(syzygies, track=False))
    assert syzygy_rank == len(jac) - len(jb) == 315
    parameters, pairs, cols = cycle_hessian_columns(instance)
    assert data['parameters'] == [[e1.NAMES[i], e1.NAMES[j]] for i, j in parameters]
    assert data['quadratic_column_pairs'] == [list(p) for p in pairs]
    residual = [e1.reduce_vector(c, jb)[0] for c in cols]
    expected = [[r, c, str(v)] for c, col in enumerate(residual) for r, v in sorted(col.items())]
    assert data['matrix_plot']['residual_entries'] == expected
    assert data['dimensions'] == {'coefficient_rows': len(rows), 'jacobian_rank': len(jb),
                                  'Koszul_fields': len(syzygies), 'Koszul_rank': syzygy_rank,
                                  'numerator_kernel_dimension': len(jac)-len(jb),
                                  'parameters_after_F_gauge': 35, 'quadratic_columns': len(cols)}
    allowed = list(range(35))
    squares, mutations = 0, 0
    for step in data['steps']:
        assert step['allowed_parameters'] == allowed
        active = [j for j, (a, b) in enumerate(pairs) if a in allowed and b in allowed]
        assert step['active_columns'] == active
        assert step['quotient_rank'] == len(e1.column_basis([residual[j] for j in active], track=False))
        forced = []
        for witness in step['forced_squares']:
            assert witness['parameter'] in allowed and witness['parameter'] not in forced
            check_square(witness, active, pairs, jac, cols)
            forced.append(witness['parameter'])
            altered = dict(witness)
            functional = e1.unpack(altered['functional'])
            e1.add(functional, {min(functional): e1.Q(1)})
            altered['functional'] = e1.pack(functional)
            try:
                check_square(altered, active, pairs, jac, cols)
            except AssertionError:
                mutations += 1
            else:
                raise AssertionError('Altered square functional accepted')
        squares += len(forced)
        allowed = [a for a in allowed if a not in forced]
        assert step['unresolved_parameters'] == allowed
    assert data['remaining_parameters'] == allowed and data['degree6_excluded'] == (not allowed)
    check = {'instance': instance, 'degree': 6, 'stage': 'Hessian-E2', 'status': 'PASS',
             'square_obstructions': squares, 'remaining_parameters': allowed,
             'degree6_excluded': not allowed, 'Koszul_fields_checked': 315,
             'exact_Jacobian_annihilation_pairings': squares*len(jac),
             'mutations_rejected': mutations, 'packet_sha256': e1.sha(path),
             'seconds': time.perf_counter()-start}
    e1.write_json(OUT / instance / 'e2-validation.json', check)
    print(json.dumps(check), flush=True)


def shift(poly, mon, scale=1):
    return {tuple(a+b for a,b in zip(m, mon)): scale*c for m,c in poly.items()}


def B(den, field):
    divergence = {}
    for i, component in enumerate(field):
        e1.add(divergence, e1.derivative(component, i))
    out = e1.multiply(den, divergence)
    for i, component in enumerate(field):
        e1.add(out, e1.multiply(component, e1.derivative(den, i)), -1)
    return out


def diagonal_maps(instance):
    F, A, _, _ = e1.target(instance)
    rows = e1.monos(12)
    lookup = {m: i for i, m in enumerate(rows)}
    def vector(poly):
        return {lookup[m]: c for m,c in poly.items()}
    parts = [e1.derivative(F, i) for i in range(6)]
    units = [tuple(int(i==j) for j in range(6)) for i in range(6)]
    denominators = [shift(parts[i], units[i]) for i in range(6)]
    numerators = [[shift(A, units[i]) if j==i else {} for j in range(6)] for i in range(6)]
    fields = []
    for i in range(6):
        for j in range(i+1, 6):
            for mon in e1.monos(2):
                field = [{} for _ in range(6)]
                field[i], field[j] = shift(parts[j],mon), shift(parts[i],mon,-1)
                fields.append(field)
    corrections = [vector(shift(F, mon)) for mon in e1.monos(6)]
    corrections.extend(vector(B(den, field)) for den in denominators for field in fields)
    pairs = [(i,j) for i in range(6) for j in range(i,6)]
    quadratics = []
    for i,j in pairs:
        col = B(denominators[i], numerators[j])
        if i!=j:
            e1.add(col, B(denominators[j], numerators[i]))
        quadratics.append(vector(col))
    return rows, corrections, pairs, quadratics


def quartic_multipliers(equations, pairs):
    """Bounded degree-four Macaulay rows; no numerical or Groebner oracle."""
    columns = e1.monos(4,5)
    lookup = {m:i for i,m in enumerate(columns)}
    rows, labels = [], []
    for r, eq in enumerate(equations):
        for mon in e1.monos(2,5):
            out = {}
            for c,v in eq.items():
                i,j = pairs[c]
                exponent = list(mon)
                exponent[i] += 1
                exponent[j] += 1
                out[lookup[tuple(exponent)]] = v
            rows.append(out)
            labels.append((r,mon))
    basis = e1.column_basis(rows)
    witnesses, unresolved = [], []
    for a in range(5):
        mon = tuple(4 if i==a else 0 for i in range(5))
        target = {lookup[mon]: e1.Q(1)}
        rem, combo = e1.reduce_vector(target,basis,{})
        if rem:
            unresolved.append(a)
            continue
        combo = {r:-c for r,c in combo.items()}
        assert e1.linear_combination(rows, combo) == target
        witnesses.append({'parameter': a, 'power': 4,
                          'multipliers': [[labels[r][0],list(labels[r][1]),str(c)] for r,c in sorted(combo.items())]})
    return {'degree':4, 'coefficient_columns':len(columns), 'multiplier_rows':len(rows),
            'row_rank':len(basis), 'identities':witnesses, 'unresolved_parameters':unresolved}


def diagonal_worker(instance):
    assert instance == 'cycle-three'
    start = time.perf_counter()
    rows, corrections, pairs, quadratics = diagonal_maps(instance)
    cb = e1.column_basis(corrections,track=False)
    print(json.dumps({'instance':instance,'full_diagonal_correction_rank':len(cb),
                      'seconds':time.perf_counter()-start}),flush=True)
    residual = [e1.reduce_vector(c, cb)[0] for c in quadratics]
    rowkeys = sorted(set().union(*(set(c) for c in residual)))
    eq = [{j: c[r] for j,c in enumerate(residual) if r in c} for r in rowkeys]
    rb = e1.column_basis(eq)
    consequences = []
    for pivot,(coefficients,combo) in sorted(rb.items()):
        raw = {rowkeys[k]:v for k,v in combo.items()}
        dual = e1.quotient_dual(raw,cb)
        assert all(e1.dot(dual,c)==0 for c in corrections)
        assert {j:e1.dot(dual,c) for j,c in enumerate(quadratics) if e1.dot(dual,c)} == coefficients
        consequences.append({'pivot':pivot, 'quadratic_coefficients':e1.pack(coefficients),
                             'functional':e1.pack(dual)})
    active = [j for j,(a,b) in enumerate(pairs) if a<5 and b<5]
    gauged_pairs = [pairs[j] for j in active]
    active_lookup = {j:i for i,j in enumerate(active)}
    gauged_equations = [{active_lookup[j]:v for j,v in e1.unpack(item['quadratic_coefficients']).items() if j in active_lookup}
                       for item in consequences]
    powers = quartic_multipliers(gauged_equations,gauged_pairs)
    _,_,target,bindings = e1.target(instance)
    data = {'schema':'fresh-instance-degree6-diagonal-v1','instance':instance,
            'target':target,'source_sha256':bindings,
            'sha256_policy':'UTF-8 bytes with CRLF normalized to LF',
            'hessian_packet_sha256':e1.sha(OUT/instance/'degree-6-e2.json'),
            'gauge':'a5=0 after D -> D-6*a5*F and N -> N-a5*A*Z; an admissible D cannot become zero.',
            'correction_column_order':'F times degree6 monomials, then i=0..5, Koszul pair j<k, quadratic monomial; products a_i*t_k relaxed independently.',
            'dimensions':{'coefficient_rows':len(rows),'correction_columns':len(corrections),
                          'correction_rank':len(cb),'quadratic_columns':len(quadratics),
                          'necessary_quadratic_rank':len(rb)},
            'quadratic_column_pairs':pairs,'consequences':consequences,
            'gauged_column_pairs':gauged_pairs,'gauged_equations':[e1.pack(eq) for eq in gauged_equations],
            'quartic_search':powers,'degree6_excluded':not powers['unresolved_parameters'],
            'matrix_plot':{'residual_entries':[[r,c,str(v)] for c,col in enumerate(residual) for r,v in sorted(col.items())]},
            'elapsed_seconds':time.perf_counter()-start,
            'scope':'Necessary full E2 consequences with all315 numerator corrections and unrestricted quotient retained before independent-product relaxation. Quartic identities imply degree-six exclusion over C; no higher-degree or existence conclusion.'}
    e1.write_json(OUT/instance/'degree-6-diagonal.json',data)
    print(json.dumps({'instance':instance,'diagonal_dimensions':data['dimensions'],
                      'quartic_search':{k:v for k,v in powers.items() if k!='identities'},
                      'power_identities':len(powers['identities']),'seconds':data['elapsed_seconds']}),flush=True)


def verify_diagonal(instance):
    start=time.perf_counter()
    path=OUT/instance/'degree-6-diagonal.json'
    data=json.loads(path.read_text(encoding='utf-8'))
    assert data['schema']=='fresh-instance-degree6-diagonal-v1'
    assert data['hessian_packet_sha256']==e1.sha(OUT/instance/'degree-6-e2.json')
    hessian=json.loads((OUT/instance/'degree-6-e2.json').read_text(encoding='utf-8'))
    assert hessian['remaining_parameters']==[0,7,14,21,28]
    rows,corrections,pairs,quadratics=diagonal_maps(instance)
    _,_,target,bindings=e1.target(instance)
    assert data['target']==target and data['source_sha256']==bindings
    cb=e1.column_basis(corrections,track=False)
    residual=[e1.reduce_vector(c,cb)[0] for c in quadratics]
    assert data['matrix_plot']['residual_entries']==[[r,c,str(v)]for c,col in enumerate(residual)for r,v in sorted(col.items())]
    rank=len(e1.column_basis(residual,track=False))
    assert data['dimensions']=={'coefficient_rows':len(rows),'correction_columns':len(corrections),
                               'correction_rank':len(cb),'quadratic_columns':len(quadratics),
                               'necessary_quadratic_rank':rank}
    assert data['quadratic_column_pairs']==[list(p) for p in pairs]
    def check_consequence(item):
        dual=e1.unpack(item['functional'])
        assert all(e1.dot(dual,c)==0 for c in corrections)
        assert {j:e1.dot(dual,c)for j,c in enumerate(quadratics)if e1.dot(dual,c)}==e1.unpack(item['quadratic_coefficients'])
    equations=[]
    mutations=0
    for item in data['consequences']:
        check_consequence(item)
        equations.append(e1.unpack(item['quadratic_coefficients']))
        altered=dict(item)
        dual=e1.unpack(altered['functional']);e1.add(dual,{min(dual):e1.Q(1)})
        altered['functional']=e1.pack(dual)
        try:check_consequence(altered)
        except AssertionError:mutations+=1
        else:raise AssertionError('Altered diagonal consequence accepted')
    assert len(e1.column_basis(equations,track=False))==len(equations)==rank
    active=[j for j,(a,b)in enumerate(pairs)if a<5 and b<5]
    active_lookup={j:i for i,j in enumerate(active)}
    gp=[pairs[j]for j in active]
    ge=[{active_lookup[j]:v for j,v in eq.items()if j in active_lookup}for eq in equations]
    assert data['gauged_column_pairs']==[list(p)for p in gp]
    assert data['gauged_equations']==[e1.pack(eq)for eq in ge]
    def check_power(item):
        result={}
        products=0
        for r,mon,coefficient in item['multipliers']:
            assert 0<=r<len(ge) and len(mon)==5 and min(mon)>=0 and sum(mon)==2
            for j,c in ge[r].items():
                exponent=list(mon)
                a,b=gp[j];exponent[a]+=1;exponent[b]+=1
                e1.add(result,{tuple(exponent):c*e1.Q(coefficient)})
                products+=1
        target={tuple(4 if j==item['parameter']else 0 for j in range(5)):e1.Q(1)}
        assert item['power']==4 and result==target
        return products
    products=0
    found=[]
    for item in data['quartic_search']['identities']:
        products+=check_power(item)
        found.append(item['parameter'])
        altered=dict(item);altered['multipliers']=[list(v)for v in item['multipliers']]
        altered['multipliers'][0][2]=str(e1.Q(altered['multipliers'][0][2])+1)
        try:check_power(altered)
        except AssertionError:mutations+=1
        else:raise AssertionError('Altered quartic identity accepted')
    assert sorted(found)==list(range(5)) and data['degree6_excluded']
    assert data['quartic_search']['unresolved_parameters']==[]
    check={'instance':instance,'degree':6,'stage':'full-diagonal-E2','status':'PASS',
           'coefficient_dual_consequences':len(equations),'correction_annihilation_pairings':len(equations)*len(corrections),
           'quadratic_pairings':len(equations)*len(quadratics),'quartic_identities':len(found),
           'quartic_coefficient_products':products,'mutations_rejected':mutations,
           'degree6_excluded':True,'packet_sha256':e1.sha(path),'seconds':time.perf_counter()-start}
    e1.write_json(OUT/instance/'diagonal-validation.json',check)
    print(json.dumps(check),flush=True)


def main():
    if not __debug__:
        raise RuntimeError('Run without -O: checks use assertions.')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=['run', 'worker', 'verify', 'e2', 'e2-worker', 'verify-e2', 'diagonal-worker', 'verify-diagonal', 'verify-all'])
    parser.add_argument('--instances', nargs='+', default=['cycle-three', 'mixed-biweight'])
    parser.add_argument('--timeout', type=float, default=120)
    args = parser.parse_args()
    if args.command == 'worker':
        worker(args.instances[0])
    elif args.command == 'run':
        run(args.instances, args.timeout)
    elif args.command == 'verify':
        verify(args.instances)
    elif args.command == 'e2':
        run_e2(args.timeout)
    elif args.command == 'e2-worker':
        e2_worker(args.instances[0])
    elif args.command == 'verify-e2':
        verify_e2(args.instances[0])
    elif args.command == 'diagonal-worker':
        diagonal_worker(args.instances[0])
    elif args.command == 'verify-diagonal':
        verify_diagonal(args.instances[0])
    else:
        verify(args.instances)
        if 'cycle-three' in args.instances:
            verify_e2('cycle-three')
            verify_diagonal('cycle-three')


if __name__ == '__main__':
    main()

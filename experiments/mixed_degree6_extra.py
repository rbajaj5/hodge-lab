#!/usr/bin/env python3
"""Complete mixed-biweight degree-six continuation, retaining all E1 directions.

The basis has 35 linear-field parameters after the F gauge, followed by the
three independently certified extra E1 directions.  All315 Koszul numerator
corrections are retained.  No previous packet or experiment is modified.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

import fresh_instance_degree6 as previous

e1 = previous.e1
ROOT = previous.ROOT
OUT = ROOT / 'results' / 'mixed-degree6-extra'
INSTANCE = 'mixed-biweight'
E1_PATH = previous.OUT / INSTANCE / 'degree-6.json'


def field_from_vector(vector, degree=7):
    monomials = e1.monos(degree)
    field = [{} for _ in range(6)]
    for column, coefficient in vector.items():
        component, index = divmod(column, len(monomials))
        field[component][monomials[index]] = coefficient
    return field


def data_basis():
    F, A, target, bindings = e1.target(INSTANCE)
    packet = json.loads(E1_PATH.read_text(encoding='utf-8'))
    assert packet['target'] == target and packet['source_sha256'] == bindings
    assert packet['dimensions']['denominator_kernel_dimension'] == 39
    extras = packet['non_J6_representative_kernel_indices']
    assert len(extras) == 3
    variables = [tuple(int(i == j) for j in range(6)) for i in range(6)]
    gradient = [e1.derivative(F, i) for i in range(6)]
    denominators, numerators, names = [], [], []
    for i in range(6):
        for j in range(6):
            if (i, j) == (5, 5):
                continue
            denominators.append(previous.shift(gradient[i], variables[j]))
            numerators.append([previous.shift(A, variables[j]) if k == i else {} for k in range(6)])
            names.append({'kind':'linear-field', 'component':i, 'variable':j,
                          'label':'M_%s_%s' % (e1.NAMES[i], e1.NAMES[j])})
    monomials = e1.monos(6)
    for i in extras:
        item = packet['kernel_lifts'][i]
        denominators.append({monomials[k]:v for k,v in e1.unpack(item['denominator']).items()})
        numerators.append(field_from_vector(e1.unpack(item['numerator'])))
        names.append({'kind':'extra-E1', 'kernel_lift_index':i, 'label':'extra_%s' % i})
    fields = []
    for i in range(6):
        for j in range(i + 1, 6):
            for mon in e1.monos(2):
                field = [{} for _ in range(6)]
                field[i] = previous.shift(gradient[j], mon)
                field[j] = previous.shift(gradient[i], mon, -1)
                fields.append(field)
    assert len(names) == 38 and len(fields) == 315
    return F, A, target, bindings, denominators, numerators, names, fields


def quotient_columns():
    _, _, target, bindings, ds, ns, names, fields = data_basis()
    rows, _, _, jac, _, _, _ = e1.matrices(INSTANCE, 6)
    lookup = {m:i for i,m in enumerate(rows)}
    pairs = [(i,j) for i in range(38) for j in range(i,38)]
    columns = []
    for i,j in pairs:
        col = previous.B(ds[i], ns[j])
        if i != j:
            e1.add(col, previous.B(ds[j], ns[i]))
        columns.append({lookup[m]:v for m,v in col.items()})
    return rows, jac, pairs, columns, names, target, bindings


def square_step(allowed, pairs, residual, jac_basis, jac, columns):
    active = [j for j,(a,b) in enumerate(pairs) if a in allowed and b in allowed]
    rowkeys = sorted(set().union(*(set(residual[j]) for j in active)))
    equations = [{j:residual[j][r] for j in active if r in residual[j]} for r in rowkeys]
    basis = e1.column_basis(equations)
    witnesses, unresolved = [], []
    for a in allowed:
        diagonal = pairs.index((a,a))
        rem, combo = e1.reduce_vector({diagonal:e1.Q(1)},basis,{})
        if rem:
            unresolved.append(a)
            continue
        raw = {rowkeys[k]:-v for k,v in combo.items()}
        dual = e1.quotient_dual(raw,jac_basis)
        assert all(e1.dot(dual,c)==0 for c in jac)
        assert all(e1.dot(dual,columns[j])==int(j==diagonal) for j in active)
        witnesses.append({'parameter':a,'square_column':diagonal,'functional':e1.pack(dual)})
    return {'allowed_parameters':allowed,'active_columns':active,'quotient_rank':len(basis),
            'nonzero_coefficient_rows':len(rowkeys),'forced_squares':witnesses,
            'unresolved_parameters':unresolved}


def quotient_worker():
    start = time.perf_counter()
    rows,jac,pairs,columns,names,target,bindings = quotient_columns()
    jb = e1.column_basis(jac,track=False)
    residual = [e1.reduce_vector(c,jb)[0] for c in columns]
    allowed, steps = list(range(38)), []
    while allowed:
        step = square_step(allowed,pairs,residual,jb,jac,columns)
        steps.append(step)
        print(json.dumps({'stage':'quotient','step':len(steps),'allowed':len(allowed),
                          'rank':step['quotient_rank'],'forced':[w['parameter'] for w in step['forced_squares']]}),flush=True)
        if not step['forced_squares']:
            break
        allowed = step['unresolved_parameters']
    result = {'schema':'mixed-degree6-extra-quotient-v1','instance':INSTANCE,
              'target':target,'source_sha256':bindings,
              'degree6_E1_sha256':e1.sha(E1_PATH),
              'sha256_policy':'UTF-8 bytes with CRLF normalized to LF',
              'gauge':'Remove M55 by D->D-6*M55*F, N->N-M55*A*Z; all3 extra E1 parameters retained.',
              'parameters':names,'quadratic_column_pairs':pairs,
              'dimensions':{'coefficient_rows':len(rows),'jacobian_rank':len(jb),
                            'E1_kernel_dimension':39,'parameters_after_F_gauge':38,
                            'quadratic_columns':len(columns),'numerator_kernel_dimension':len(jac)-len(jb)},
              'steps':steps,'remaining_parameters':allowed,'degree6_excluded':not allowed,
              'matrix_plot':{'residual_entries':[[r,c,str(v)]for c,col in enumerate(residual)for r,v in sorted(col.items())]},
              'elapsed_seconds':time.perf_counter()-start,
              'scope':'Actual B_D(N0) modulo J12 on the complete E1 kernel. Necessary only; surviving parameters are not certificates.'}
    e1.write_json(OUT/'quotient.json',result)


def check_square(item,active,pairs,jac,columns):
    assert item['square_column']==pairs.index((item['parameter'],item['parameter']))
    dual=e1.unpack(item['functional'])
    assert all(0<=i<6188 for i in dual)
    assert all(e1.dot(dual,c)==0 for c in jac)
    assert all(e1.dot(dual,columns[j])==int(j==item['square_column'])for j in active)


def verify_quotient():
    start=time.perf_counter()
    path=OUT/'quotient.json'
    packet=json.loads(path.read_text(encoding='utf-8'))
    assert packet['schema']=='mixed-degree6-extra-quotient-v1'
    assert packet['degree6_E1_sha256']==e1.sha(E1_PATH)
    e1_check=e1.verify_packet(E1_PATH)
    assert e1_check['dimensions']['denominator_kernel_dimension']==39
    rows,jac,pairs,columns,names,target,bindings=quotient_columns()
    assert packet['parameters']==names and packet['target']==target and packet['source_sha256']==bindings
    assert packet['quadratic_column_pairs']==[list(p)for p in pairs]
    _,A,_,_,ds,ns,_,fields=data_basis()
    F,_,_,_=e1.target(INSTANCE)
    denominator_monomials=e1.monos(6)
    denominator_lookup={m:i for i,m in enumerate(denominator_monomials)}
    complete_basis=[{denominator_lookup[m]:c for m,c in den.items()}for den in [F]+ds]
    basis_rank=len(e1.column_basis(complete_basis,track=False))
    assert basis_rank==39==e1_check['dimensions']['denominator_kernel_dimension']
    for den,num in zip(ds,ns):
        image={}
        for i,p in enumerate(num):e1.add(image,e1.multiply(p,e1.derivative(F,i)))
        assert image==e1.multiply(A,den)
    syzygies=previous.quadratic_koszul(INSTANCE)
    assert all(not e1.linear_combination(jac,s)for s in syzygies)
    sr=len(e1.column_basis(syzygies,track=False))
    jb=e1.column_basis(jac,track=False)
    assert sr==len(jac)-len(jb)==315
    residual=[e1.reduce_vector(c,jb)[0]for c in columns]
    assert packet['matrix_plot']['residual_entries']==[[r,c,str(v)]for c,col in enumerate(residual)for r,v in sorted(col.items())]
    assert packet['dimensions']=={'coefficient_rows':len(rows),'jacobian_rank':len(jb),'E1_kernel_dimension':39,
                                   'parameters_after_F_gauge':38,'quadratic_columns':len(columns),
                                   'numerator_kernel_dimension':315}
    allowed=list(range(38));squares=mutations=0
    for step in packet['steps']:
        assert step['allowed_parameters']==allowed
        active=[j for j,(a,b)in enumerate(pairs)if a in allowed and b in allowed]
        assert step['active_columns']==active
        assert step['quotient_rank']==len(e1.column_basis([residual[j]for j in active],track=False))
        forced=[]
        for item in step['forced_squares']:
            assert item['parameter']in allowed and item['parameter']not in forced
            check_square(item,active,pairs,jac,columns)
            forced.append(item['parameter'])
            altered=dict(item);dual=e1.unpack(altered['functional'])
            e1.add(dual,{min(dual):e1.Q(1)});altered['functional']=e1.pack(dual)
            try:check_square(altered,active,pairs,jac,columns)
            except AssertionError:mutations+=1
            else:raise AssertionError('Altered quotient square accepted')
        squares+=len(forced)
        allowed=[a for a in allowed if a not in forced]
        assert step['unresolved_parameters']==allowed
    assert packet['remaining_parameters']==allowed and packet['degree6_excluded']==(not allowed)
    result={'instance':INSTANCE,'stage':'quotient','status':'PASS','square_obstructions':squares,
            'remaining_parameters':allowed,'degree6_excluded':not allowed,'numerator_lifts_checked':38,
            'complete_E1_basis_including_F_rank':basis_rank,
            'Koszul_fields_checked':315,'Jacobian_annihilation_pairings':squares*len(jac),
            'mutations_rejected':mutations,'packet_sha256':e1.sha(path),'seconds':time.perf_counter()-start}
    e1.write_json(OUT/'quotient-validation.json',result)
    print(json.dumps(result),flush=True)


def diagonal_consequences():
    rows,corrections,pairs,quadratics=previous.diagonal_maps(INSTANCE)
    cb=e1.column_basis(corrections,track=False)
    residual=[e1.reduce_vector(c,cb)[0]for c in quadratics]
    rowkeys=sorted(set().union(*(set(c)for c in residual)))
    eq=[{j:c[r]for j,c in enumerate(residual)if r in c}for r in rowkeys]
    rb=e1.column_basis(eq)
    consequences=[]
    for pivot,(coefficients,combo)in sorted(rb.items()):
        raw={rowkeys[k]:v for k,v in combo.items()}
        dual=e1.quotient_dual(raw,cb)
        assert all(e1.dot(dual,c)==0 for c in corrections)
        assert {j:e1.dot(dual,c)for j,c in enumerate(quadratics)if e1.dot(dual,c)}==coefficients
        consequences.append({'pivot':pivot,'quadratic_coefficients':e1.pack(coefficients),'functional':e1.pack(dual)})
    return rows,corrections,pairs,quadratics,cb,residual,consequences


def homogeneous_power(linear,degree,n=5):
    factor={tuple(int(i==j)for j in range(n)):c for i,c in linear.items()}
    out={(0,)*n:e1.Q(1)}
    for _ in range(degree):out=e1.multiply(out,factor)
    return out


def multiplier_search(equations,pairs,degree):
    monomials=e1.monos(degree,5);lookup={m:i for i,m in enumerate(monomials)}
    rows,labels=[],[]
    for r,eq in enumerate(equations):
        for mon in e1.monos(degree-2,5):
            row={}
            for j,c in eq.items():
                a,b=pairs[j];m=list(mon);m[a]+=1;m[b]+=1
                row[lookup[tuple(m)]]=c
            rows.append(row);labels.append((r,mon))
    basis=e1.column_basis(rows)
    witnesses,unresolved=[],[]
    for a in (0,1,3):
        linear={a:e1.Q(1),4:e1.Q(-1)}
        polynomial=homogeneous_power(linear,degree)
        target={lookup[m]:c for m,c in polynomial.items()}
        rem,combo=e1.reduce_vector(target,basis,{})
        if rem:
            unresolved.append(a)
            continue
        combo={r:-c for r,c in combo.items()}
        assert e1.linear_combination(rows,combo)==target
        witnesses.append({'linear_form':e1.pack(linear),'power':degree,
                          'multipliers':[[labels[r][0],list(labels[r][1]),str(c)]for r,c in sorted(combo.items())]})
    return {'degree':degree,'coefficient_columns':len(monomials),'multiplier_rows':len(rows),
            'row_rank':len(basis),'identities':witnesses,'unresolved_difference_parameters':unresolved}


def diagonal_worker():
    start=time.perf_counter()
    rows,corrections,pairs,quadratics,cb,residual,consequences=diagonal_consequences()
    active=[j for j,(a,b)in enumerate(pairs)if a<5 and b<5]
    active_lookup={j:i for i,j in enumerate(active)}
    gp=[pairs[j]for j in active]
    ge=[{active_lookup[j]:v for j,v in e1.unpack(item['quadratic_coefficients']).items()if j in active_lookup}for item in consequences]
    attempts=[]
    for degree in (2,3,4,5,6):
        result=multiplier_search(ge,gp,degree)
        attempts.append(result)
        print(json.dumps({'stage':'diagonal','degree':degree,'rank':result['row_rank'],
                          'columns':result['coefficient_columns'],'identities':len(result['identities'])}),flush=True)
        if not result['unresolved_difference_parameters']:break
    # If all three differences vanish, reduce all five source quadrics in two
    # parameters t=a2 and s=a4, before the nonzero-s normalization.
    reduced=[]
    image={0:1,1:1,2:0,3:1,4:1}
    for equation in ge:
        out={}
        for j,c in equation.items():
            a,b=gp[j];m=[0,0];m[image[a]]+=1;m[image[b]]+=1
            e1.add(out,{tuple(m):c})
        reduced.append(out)
    P={(2,0):e1.Q(5),(1,1):e1.Q(-8),(0,2):e1.Q(8)}
    ratios=[]
    for equation in reduced:
        ratio=equation.get((2,0),e1.Q(0))/5
        assert equation=={m:c*ratio for m,c in P.items()if c*ratio}
        ratios.append(str(ratio))
    _,_,target,bindings=e1.target(INSTANCE)
    result={'schema':'mixed-degree6-extra-diagonal-v1','instance':INSTANCE,
            'target':target,'source_sha256':bindings,'quotient_sha256':e1.sha(OUT/'quotient.json'),
            'sha256_policy':'UTF-8 bytes with CRLF normalized to LF',
            'correction_column_order':'462 F*S6 columns, then all6 diagonal D_i and315 quadratic Koszul fields; a_i*k_j relaxed independently.',
            'dimensions':{'coefficient_rows':len(rows),'correction_columns':len(corrections),'correction_rank':len(cb),
                          'quadratic_columns':len(quadratics),'necessary_quadratic_rank':len(consequences)},
            'quadratic_column_pairs':pairs,'consequences':consequences,
            'gauged_column_pairs':gp,'gauged_equations':[e1.pack(q)for q in ge],
            'multiplier_attempts':attempts,
            'two_parameter_reduction':{'substitution':'a0=a1=a3=a4=s; a2=t; a5=0',
                                       'equation':'5*t^2-8*t*s+8*s^2=0',
                                       'source_equation_multiples':ratios,
                                       'normalization':'s=0 forces t=0, hence D=0; admissibility forces s nonzero, so divide all coefficients by s.'},
            'matrix_plot':{'residual_entries':[[r,c,str(v)]for c,col in enumerate(residual)for r,v in sorted(col.items())]},
            'degree6_excluded':False,
            'elapsed_seconds':time.perf_counter()-start,
            'scope':'Complete E1 kernel reduced to the two conjugate normalized diagonal candidates (1,1,t,1,1,0), 5*t^2-8*t+8=0. Their true shared-K equation still requires testing.'}
    e1.write_json(OUT/'diagonal.json',result)


def verify_diagonal():
    start=time.perf_counter();path=OUT/'diagonal.json'
    packet=json.loads(path.read_text(encoding='utf-8'))
    assert packet['schema']=='mixed-degree6-extra-diagonal-v1'
    assert packet['quotient_sha256']==e1.sha(OUT/'quotient.json')
    quotient=json.loads((OUT/'quotient.json').read_text(encoding='utf-8'))
    assert quotient['remaining_parameters']==[0,7,14,21,28]
    rows,corrections,pairs,quadratics,cb,residual,consequences=diagonal_consequences()
    _,_,target,bindings=e1.target(INSTANCE)
    assert packet['target']==target and packet['source_sha256']==bindings
    assert packet['consequences']==consequences
    assert packet['quadratic_column_pairs']==[list(p)for p in pairs]
    assert packet['matrix_plot']['residual_entries']==[[r,c,str(v)]for c,col in enumerate(residual)for r,v in sorted(col.items())]
    assert packet['dimensions']=={'coefficient_rows':len(rows),'correction_columns':len(corrections),'correction_rank':len(cb),
                                  'quadratic_columns':len(quadratics),'necessary_quadratic_rank':len(consequences)}
    def check_consequence(item):
        dual=e1.unpack(item['functional'])
        assert all(0<=i<len(rows)for i in dual)
        assert all(e1.dot(dual,c)==0 for c in corrections)
        assert {j:e1.dot(dual,c)for j,c in enumerate(quadratics)if e1.dot(dual,c)}==e1.unpack(item['quadratic_coefficients'])
    mutations=0
    for item in packet['consequences']:
        check_consequence(item)
        altered=dict(item);dual=e1.unpack(altered['functional']);e1.add(dual,{min(dual):e1.Q(1)})
        altered['functional']=e1.pack(dual)
        try:check_consequence(altered)
        except AssertionError:mutations+=1
        else:raise AssertionError('Altered diagonal consequence accepted')
    active=[j for j,(a,b)in enumerate(pairs)if a<5 and b<5];al={j:i for i,j in enumerate(active)}
    gp=[pairs[j]for j in active]
    ge=[{al[j]:v for j,v in e1.unpack(item['quadratic_coefficients']).items()if j in al}for item in consequences]
    assert packet['gauged_column_pairs']==[list(p)for p in gp]and packet['gauged_equations']==[e1.pack(q)for q in ge]
    def check_power(item):
        result={};products=0
        for r,mon,coefficient in item['multipliers']:
            assert 0<=r<len(ge)and len(mon)==5 and min(mon)>=0 and sum(mon)==item['power']-2
            for j,c in ge[r].items():
                a,b=gp[j];m=list(mon);m[a]+=1;m[b]+=1
                e1.add(result,{tuple(m):c*e1.Q(coefficient)});products+=1
        assert result==homogeneous_power(e1.unpack(item['linear_form']),item['power'])
        return products
    identities=products=0;forced=set()
    for attempt in packet['multiplier_attempts']:
        computed=multiplier_search(ge,gp,attempt['degree'])
        assert attempt==computed
        for item in attempt['identities']:
            products+=check_power(item);identities+=1
            linear=e1.unpack(item['linear_form'])
            a=next(j for j in linear if j!=4)
            assert linear=={a:e1.Q(1),4:e1.Q(-1)}and a in(0,1,3)
            forced.add(a)
            altered=dict(item);altered['multipliers']=[list(x)for x in item['multipliers']]
            altered['multipliers'][0][2]=str(e1.Q(altered['multipliers'][0][2])+1)
            try:check_power(altered)
            except AssertionError:mutations+=1
            else:raise AssertionError('Altered difference-power identity accepted')
    assert forced=={0,1,3}
    image={0:1,1:1,2:0,3:1,4:1};ratios=[]
    P={(2,0):e1.Q(5),(1,1):e1.Q(-8),(0,2):e1.Q(8)}
    for equation in ge:
        reduced={}
        for j,c in equation.items():
            a,b=gp[j];m=[0,0];m[image[a]]+=1;m[image[b]]+=1
            e1.add(reduced,{tuple(m):c})
        ratio=reduced.get((2,0),e1.Q(0))/5
        assert reduced=={m:c*ratio for m,c in P.items()if c*ratio}
        ratios.append(str(ratio))
    assert packet['two_parameter_reduction']['source_equation_multiples']==ratios
    assert any(e1.Q(c)for c in ratios)and not packet['degree6_excluded']
    result={'instance':INSTANCE,'stage':'diagonal','status':'PASS','physical_dual_consequences':len(consequences),
            'correction_annihilation_pairings':len(consequences)*len(corrections),
            'quadratic_pairings':len(consequences)*len(quadratics),
            'difference_power_identities':identities,'multiplier_coefficient_products':products,
            'forced_linear_differences':sorted(forced),'mutations_rejected':mutations,
            'degree6_excluded':False,'packet_sha256':e1.sha(path),'seconds':time.perf_counter()-start}
    e1.write_json(OUT/'diagonal-validation.json',result);print(json.dumps(result),flush=True)


def run(timeout,stage='quotient'):
    path=OUT/'attempts.json'
    attempts=json.loads(path.read_text(encoding='utf-8'))if path.exists()else[]
    start=time.perf_counter()
    command=[sys.executable,'-S',str(Path(__file__).resolve()),stage+'-worker']
    try:
        process=subprocess.run(command,capture_output=True,text=True,timeout=timeout)
        result={'stage':stage,'status':'complete'if process.returncode==0 else'error',
                'returncode':process.returncode,'stdout':process.stdout,'stderr':process.stderr}
    except subprocess.TimeoutExpired as error:
        result={'stage':stage,'status':'timeout',
                'stdout':error.stdout.decode()if isinstance(error.stdout,bytes)else error.stdout or'',
                'stderr':error.stderr.decode()if isinstance(error.stderr,bytes)else error.stderr or''}
    result.update(time_limit_seconds=timeout,elapsed_seconds=time.perf_counter()-start)
    attempts.append(result);e1.write_json(path,attempts)
    print(json.dumps(result),flush=True)


def main():
    if not __debug__:raise RuntimeError('Run without -O: exact checks use assertions.')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['run','quotient-worker','verify','diagonal','diagonal-worker','verify-diagonal','verify-all'])
    parser.add_argument('--timeout',type=float,default=120)
    args=parser.parse_args()
    if args.command=='run':run(args.timeout)
    elif args.command=='quotient-worker':quotient_worker()
    elif args.command=='verify':verify_quotient()
    elif args.command=='diagonal':run(args.timeout,'diagonal')
    elif args.command=='diagonal-worker':diagonal_worker()
    elif args.command=='verify-diagonal':verify_diagonal()
    else:
        verify_quotient();verify_diagonal()


if __name__=='__main__':main()

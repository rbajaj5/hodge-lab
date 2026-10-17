#!/usr/bin/env python3
"""Bounded polynomial-multiplier tests for coordinate-divisible quadratic polars."""
from pathlib import Path
from fractions import Fraction as Q
import argparse
import copy
import json
import math
import subprocess
import sys
import time
import cyclic_fano_quadratic_polars as source

base=source.base;poly=source.poly;arithmetic=source.arithmetic
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/cyclic-fano-divisible-multipliers'
encode=source.encode


def necessary_equations(active=None,data=None):
    data=source.system()if data is None else data
    if active is None:active=[i for i,b in enumerate(data['basis'])if b['quadratic_powers'][b['component']]]
    restricted,kept=source.restricted_rows(data,set(active))
    pure=[j for j in sorted(kept)if data['labels'][j]['kind']=='a*a']
    mixed=[j for j in sorted(kept)if data['labels'][j]['kind']=='a*c']
    order=mixed+pure;lookup={j:k for k,j in enumerate(order)}
    rows={m:{lookup[j]:c for j,c in row.items()}for m,row in restricted.items()}
    pivots=arithmetic.exact_row_basis(rows);equations=[]
    for j,(row,track)in sorted(pivots.items()):
        if j<len(mixed):continue
        assert base.total(poly.scale(rows[m],c)for m,c in track.items())==row
        polynomial={}
        for k,c in row.items():
            inds=data['labels'][order[k]]['indices']
            power=tuple(sum(i==a for i in inds)for a in active)
            polynomial[power]=c
        equations.append({'polynomial':encode(polynomial),'dual':encode(track)})
    return {'active_raw_parameter_indices':active,'rows':len(rows),'columns':len(order),
            'pure_columns':len(pure),'mixed_columns':len(mixed),'rank':len(pivots),
            'mixed_rank':sum(j<len(mixed)for j in pivots),'equations':equations}


def macaulay_probe(packet,degree,p=1009):
    qs=[arithmetic.decode(x['polynomial'])for x in packet['equations']]
    multipliers=base.monomials(degree-2,(1,)*25)
    generators=[]
    for i,q in enumerate(qs):
        for m in multipliers:
            v={tuple(a+b for a,b in zip(k,m)):arithmetic.modq(c,p)for k,c in q.items()}
            generators.append((i,m,v))
    pivots={}
    for i,m,row in sorted(generators,key=lambda x:len(x[2])):
        v=arithmetic.mod_reduce(row,pivots,p)
        if v:
            j=min(v);scale=pow(v[j],-1,p);pivots[j]={k:c*scale%p for k,c in v.items()}
    forced=[]
    for i in range(25):
        m=tuple(degree*int(j==i)for j in range(25))
        if not arithmetic.mod_reduce({m:1},pivots,p):forced.append(i)
    return {'degree':degree,'prime':p,'rows':len(base.monomials(degree,(1,)*25)),
            'columns':len(generators),'rank_mod_prime':len(pivots),'coordinate_powers_in_rowspace_mod_prime':forced}


def exact_cubic(packet):
    n=len(packet['active_raw_parameter_indices'])
    qs=[arithmetic.decode(x['polynomial'])for x in packet['equations']];rows={}
    for i,q in enumerate(qs):
        for k in range(n):
            m=tuple(int(j==k)for j in range(n))
            rows[(i,k)]=poly.mul(q,{m:Q(1)})
    pivots=arithmetic.exact_row_basis(rows);identities=[];unresolved=[]
    for k in range(n):
        m=tuple(3*int(j==k)for j in range(n));target={m:Q(1)}
        rem,track=arithmetic.exact_reduce(target,pivots)
        if rem:unresolved.append(k);continue
        track=poly.scale(track,-1)
        assert base.total(poly.scale(rows[j],c)for j,c in track.items())==target
        identities.append({'parameter_index':k,'power':3,'multipliers':[{'equation_index':i,'linear_variable':j,'coefficient':str(c)}for(i,j),c in sorted(track.items())]})
    assert unresolved==([2,7,12,17,22]if n==25 else [])
    return {'degree':3,'rows':math.comb(n+2,3),'columns':len(rows),'rank':len(pivots),'identities':identities,'remaining_parameter_indices':unresolved}


def untracked_rank(rows):
    pivots={}
    for v in sorted(rows,key=len):
        v=v.copy()
        while v:
            j=min(v)
            if j not in pivots:
                pivots[j]=poly.scale(v,1/v[j]);break
            v=poly.add(v,pivots[j],-v[j])
    return len(pivots)


def verify_cubic(stage,proof):
    n=len(stage['active_raw_parameter_indices']);qs=[arithmetic.decode(x['polynomial'])for x in stage['equations']]
    assert proof['degree']==3 and proof['rows']==math.comb(n+2,3)and proof['columns']==len(qs)*n
    rows=[]
    for q in qs:
        for j in range(n):rows.append(poly.mul(q,{tuple(int(i==j)for i in range(n)):Q(1)}))
    assert untracked_rank(rows)==proof['rank']
    indices=[]
    for identity in proof['identities']:
        k=identity['parameter_index'];assert identity['power']==3 and 0<=k<n
        indices.append(k);out={}
        for term in identity['multipliers']:
            i=term['equation_index'];j=term['linear_variable'];assert 0<=i<len(qs)and 0<=j<n
            m=tuple(int(l==j)for l in range(n))
            out=poly.add(out,poly.mul(qs[i],{m:Q(term['coefficient'])}))
        assert out=={tuple(3*int(i==k)for i in range(n)):Q(1)}
    remaining=proof['remaining_parameter_indices']
    assert sorted(indices+remaining)==list(range(n))and len(set(indices+remaining))==n
    assert remaining==([2,7,12,17,22]if n==25 else [])


def calculate(existing_cubic=None):
    data=source.system();initial=necessary_equations(data=data)
    cubic=exact_cubic(initial)if existing_cubic is None else existing_cubic
    if existing_cubic is not None:verify_cubic(initial,cubic)
    remaining=[initial['active_raw_parameter_indices'][i]for i in cubic['remaining_parameter_indices']]
    rebuild=necessary_equations(remaining,data);final=exact_cubic(rebuild)
    assert len(initial['equations'])==155 and len(rebuild['equations'])==12
    assert not final['remaining_parameter_indices']
    keep=cubic['remaining_parameter_indices'];restricted=[]
    for equation in initial['equations']:
        reduced={}
        for m,c in arithmetic.decode(equation['polynomial']).items():
            if any(m[i]for i in range(25)if i not in keep):continue
            power=tuple(m[i]for i in keep);reduced[power]=reduced.get(power,Q(0))+c
        restricted.append({m:c for m,c in reduced.items()if c})
    new_quadrics=[arithmetic.decode(e['polynomial'])for e in rebuild['equations']]
    restricted_rank=untracked_rank(restricted);rebuilt_rank=untracked_rank(new_quadrics)
    new_basis=arithmetic.exact_row_basis(dict(enumerate(new_quadrics)))
    assert all(not arithmetic.exact_reduce(q,new_basis)[0]for q in restricted)
    assert restricted_rank==9 and rebuilt_rank==12
    prior=source.OUT/'packet.json';prior_receipt=source.OUT/'validation.json'
    previous=json.loads(prior.read_text());receipt=json.loads(prior_receipt.read_text())
    assert previous['producer_sha256']==poly.sha(Path(source.__file__))and receipt['packet_sha256']==poly.sha(prior)
    assert previous['projection']['compact_generators']==data['correction_labels']
    assert previous['source_instance_sha256']==poly.sha(base.SOURCE/'source/instance.rec')
    labels=[]
    for i in initial['active_raw_parameter_indices']:
        b=data['basis'][i];component=b['component'];m=b['quadratic_powers'][:];m[component]-=1
        j=next(k for k in source.BASE if m[k])
        labels.append({'raw_parameter_index':i,'matrix_row':source.BASE.index(component),'matrix_column':source.BASE.index(j),'quadratic_powers':b['quadratic_powers']})
    assert [(x['matrix_row'],x['matrix_column'])for x in labels]==[(i,j)for i in range(5)for j in range(5)]
    return {'schema':'cyclic-fano-divisible-multipliers-v1','status':'PASS',
            'instance':'cyclic-triple-fano','q':1,'degree':7,
            'source_commit':'d96911d725077e66a8f10848908be01a643b1714',
            'source_instance_sha256':poly.sha(base.SOURCE/'source/instance.rec'),
            'producer_sha256':poly.sha(Path(__file__)),
            'dependencies':{Path(m.__file__).name:poly.sha(Path(m.__file__))for m in (source,arithmetic,base,poly)},
            'prior_projection_proof':{'packet':str(prior.relative_to(ROOT)).replace('\\','/'),'packet_sha256':poly.sha(prior),
                                      'primary_receipt_sha256':poly.sha(prior_receipt),
                                      'independent_receipt_sha256':poly.sha(source.OUT/'independent-validation.json'),
                                      'raw_Koszul_fields':230,'compact_correction_types':55,'quotient_directions':246,
                                      'scope':'Prior source-bound proof supplies the full projection and regular-sequence coverage. This batch reconstructs and checks both restricted physical coefficient systems.'},
            'parameter_order':labels,'base_variables':list(source.NAMES),
            'family':'v_i=x_i*sum_j M_ij*x_j, with25 constant complex coefficients M_ij',
            'initial_stage':initial,'cubic_stage':cubic,'rebuild_stage':rebuild,'final_cubic_stage':final,
            'rebuild_diagnostic':{'initial_quadrics_after_restriction_rank':restricted_rank,
                                   'fresh_rebuilt_quadrics_rank':rebuilt_rank,'additional_independent_quadrics':3,
                                   'restricted_initial_span_contained_in_rebuilt_span':True},
            'conclusion':'Every nonzero coordinate-divisible homogeneous quadratic direction v_i=x_i*l_i gives an excluded degree-seven denominator E=v(Delta).',
            'attempts':[{'stage':'degree2','status':'no_individual_square','evidence':'Prior full physical degree2 screen modulo1009 isolated none; this batch extracts155 exact necessary quadrics.'},
                        {'stage':'degree3_modular','status':'partial_discovery','prime':1009,'rows':2925,'columns':3875,'rank_mod_prime':2892,'bound_seconds':120},
                        {'stage':'degree3_rational','status':'20_coordinate_cubes_verified','bound_seconds':120},
                        {'stage':'five_variable_rebuild','status':'five_final_cubes_verified','bound_seconds':120},
                        {'stage':'degree4','status':'not_run','reason':'The degree3 identities plus exact rebuild already exclude the family.'}],
            'limits':'The full75-parameter quadratic-direction family remains unresolved. No arbitrary degree-seven exclusion, geometric support, Lean proof or solution is claimed.'}


def verify_packet(actual):
    expected=calculate(actual['cubic_stage']);assert actual==expected
    mutations=[]
    for stage in ('initial_stage','rebuild_stage'):
        bad=copy.deepcopy(actual);bad[stage]['equations']=bad[stage]['equations'][1:];mutations.append(bad)
    for stage in ('cubic_stage','final_cubic_stage'):
        bad=copy.deepcopy(actual);bad[stage]['identities'][0]['multipliers'][0]['coefficient']='0';mutations.append(bad)
    bad=copy.deepcopy(actual);bad['prior_projection_proof']['compact_correction_types']=50;mutations.append(bad)
    bad=copy.deepcopy(actual);bad['rebuild_stage']['active_raw_parameter_indices']=[];mutations.append(bad)
    bad=copy.deepcopy(actual);bad['parameter_order']=bad['parameter_order'][1:];mutations.append(bad)
    bad=copy.deepcopy(actual);bad['source_instance_sha256']='0'*64;mutations.append(bad)
    for bad in mutations:
        try:assert bad==expected
        except AssertionError:pass
        else:raise AssertionError('Mutation accepted')
    save('validation.json',{'schema':'cyclic-fano-divisible-multipliers-validation-v1','status':'PASS',
                           'producer_sha256':poly.sha(Path(__file__)),'packet_sha256':poly.sha(OUT/'packet.json'),
                           'initial_physical_duals':155,'initial_cube_identities':20,'rebuild_physical_duals':12,
                           'final_cube_identities':5,'compact_corrections_retained':55,'negative_controls_rejected':len(mutations),
                           'scope':'Reconstructs both physical maps and replays every multiplier; recomputes exact Macaulay rank without rediscovering tracked multipliers.'})


def save(name,data):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')


def main():
    assert __debug__,'Run without -O'
    parser=argparse.ArgumentParser();parser.add_argument('command',choices=['probe','_probe','cubic','_cubic','quartic','_quartic','exact-cubic','_exact-cubic','run','_run','verify','_verify']);args=parser.parse_args()
    if args.command in ('probe','cubic','quartic','exact-cubic','run','verify'):
        bound=300 if args.command in ('run','verify') else 120
        try:r=subprocess.run([sys.executable,'-S',str(Path(__file__)),'_'+args.command],timeout=bound)
        except subprocess.TimeoutExpired:
            save(args.command+'-timeout.json',{'status':'timeout','bound_seconds':bound});raise SystemExit(2)
        raise SystemExit(r.returncode)
    started=time.perf_counter()
    if args.command=='_run':
        result=calculate();save('packet.json',result)
        print(json.dumps({'status':'PASS','command':'run','seconds':time.perf_counter()-started,'packet_sha256':poly.sha(OUT/'packet.json')}));return
    if args.command=='_verify':
        actual=json.loads((OUT/'packet.json').read_text());verify_packet(actual)
        print(json.dumps({'status':'PASS','command':'verify','seconds':time.perf_counter()-started,'packet_sha256':poly.sha(OUT/'packet.json')}));return
    if args.command=='_exact-cubic':
        packet=json.loads((OUT/'necessary-probe.json').read_text());result=exact_cubic(packet)
        save('exact-cubic-probe.json',result);print(json.dumps({'seconds':time.perf_counter()-started,'rank':result['rank'],'identities':len(result['identities'])}));return
    if args.command in ('_cubic','_quartic'):
        packet=json.loads((OUT/'necessary-probe.json').read_text());result=macaulay_probe(packet,3 if args.command=='_cubic' else 4)
        result['seconds']=time.perf_counter()-started;save(args.command[1:]+'-probe.json',result);print(json.dumps(result));return
    result=necessary_equations();save('necessary-probe.json',result)
    print(json.dumps({'seconds':time.perf_counter()-started,**{k:v for k,v in result.items()if k!='equations'},'necessary_quadrics':len(result['equations'])}))


if __name__=='__main__':main()

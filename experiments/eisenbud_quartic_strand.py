"""Degree-four continuation on five reduced holdout families.

Exact Macaulay maps and the distinction between prolonged linear syzygies,
Koszul boundaries of the necessary quadratics, and remaining relations.
"""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import argparse, copy, gzip, hashlib, json, time
from math import comb
import eisenbud_linear_strand as e

ROOT=e.ROOT
OUT=ROOT/'results/eisenbud-quartic-strand'
NUMBERS=[6,8,10,149,152]
PRIME=1000003


def source():
    with gzip.open(e.OUT/'certificates.json.gz','rt',encoding='utf-8') as f:p=json.load(f)
    return {f['number']:f for f in p['families'] if f['number'] in NUMBERS}


def source_sha():return hashlib.sha256((e.OUT/'certificates.json.gz').read_bytes()).hexdigest()


def save(path,obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    with gzip.open(path,'wt',encoding='utf-8') as f:json.dump(obj,f,separators=(',',':'))


def load(path):
    with gzip.open(path,'rt',encoding='utf-8') as f:return json.load(f)


def ordered_strand(equations,ids):
    labels,rows=e.mac_map(equations,ids,4)
    order=sorted(range(len(rows)),key=lambda i:(len(rows[i]),i))
    span=e.t.base.Elimination();dependencies=[]
    for count,k in enumerate(order,1):
        rel=span.insert(dict(rows[k]),{k:Q(1)})
        if rel is not None:dependencies.append([[i,str(c)] for i,c in sorted(rel.items())])
        if count%1000==0:print('sparse order',count,'/',len(rows),'rank',len(span.basis),flush=True)
    found=[]
    for i in ids:
        residual={(i,)*4:Q(1)};weights={}
        while residual:
            pivot=min(residual)
            if pivot not in span.basis:break
            c=residual[pivot];row,rep=span.basis[pivot]
            residual=e.t.base.padd(residual,row,-c);weights=e.t.base.padd(weights,rep,c)
        if not residual:
            found.append({'coordinate':i,'power':4,'products':[[labels[k][0],list(labels[k][1]),str(c)]
                                                               for k,c in sorted(weights.items())]})
    rank=len(span.basis)
    return {'degree':4,'domain':len(rows),'codomain':comb(len(ids)+3,4),'rank':rank,
            'kernel':len(rows)-rank,'quotient_dimension':comb(len(ids)+3,4)-rank,
            'dependencies':dependencies,'vanishings':found,'tested_coordinates':ids,'column_order':order}


def check_quartic(equations,ids,record):
    """Exact kernel upper bound + modular minor lower bound, then power tests."""
    labels,rows=e.mac_map(equations,ids,4);span=e.t.base.Elimination(prime=PRIME)
    for row in rows:
        span.insert({m:c.numerator*pow(c.denominator,-1,PRIME)%PRIME for m,c in row.items()})
    assert record['degree']==4 and record['domain']==len(rows)
    assert record['codomain']==comb(len(ids)+3,4)
    assert len(span.basis)==record['rank']
    assert record['kernel']==len(rows)-record['rank']==len(record['dependencies'])
    assert record['quotient_dimension']==record['codomain']-record['rank']
    order=record.get('column_order',list(range(len(rows))))
    assert sorted(order)==list(range(len(rows)))
    position={k:i for i,k in enumerate(order)};previous=-1
    for rel in record['dependencies']:
        weights=e.decode_weights(rel)
        assert weights and all(k in position for k in weights)
        pivot=max(weights,key=position.get)
        assert position[pivot]>previous and weights[pivot]==1
        previous=position[pivot]
        products=[[labels[k][0],labels[k][1],c] for k,c in weights.items()]
        assert not e.expand_products(equations,products)
    # These independent rational nullvectors plus the modular rank lower bound
    # prove the exact rational rank, without another large rational elimination.
    found={p['coordinate'] for p in record['vanishings']}
    assert len(found)==len(record['vanishings']) and record['tested_coordinates']==ids
    for proof in record['vanishings']:
        i=proof['coordinate'];assert i in ids and proof['power']==4
        assert all(0<=j<len(equations) and len(m)==2 and all(k in ids for k in m)
                   for j,m,c in proof['products'])
        assert e.expand_products(equations,proof['products'])=={(i,)*4:Q(1)}
    for i in set(ids)-found:
        v={(i,)*4:1}
        while v:
            pivot=min(v)
            if pivot not in span.basis:break
            c=v[pivot];row,_=span.basis[pivot]
            for m,b in row.items():
                value=(v.get(m,0)-c*b)%PRIME
                if value:v[m]=value
                elif m in v:del v[m]
        # Since the base rank has no drop, augmented rank r+1 modulo p proves
        # nonmembership over Q (and hence C) for this rational coefficient vector.
        assert v


def syzygy_layers(equations,ids,cubic,quartic,prime=None):
    labels3,_=e.mac_map(equations,ids,3)
    labels4,_=e.mac_map(equations,ids,4)
    lookup={label:i for i,label in enumerate(labels4)}
    span=e.t.base.Elimination(prime=prime)
    def insert(v):
        if prime:v={i:c.numerator*pow(c.denominator,-1,prime)%prime for i,c in v.items() if c}
        return span.insert(v)
    linear_generators=[]
    for j,rel in enumerate(cubic['dependencies']):
        for variable in ids:
            v={}
            for k,c in rel:
                equation,mon=labels3[k];key=lookup[(equation,tuple(sorted(mon+(variable,))))]
                v[key]=v.get(key,Q(0))+Q(c)
            if insert(v) is None:linear_generators.append([j,variable])
    linear_rank=len(span.basis)
    # These are Koszul boundaries for P_j, not the original gradient fields.
    boundaries=[]
    for i,j in combinations(range(len(equations)),2):
        v={lookup[(i,m)]:c for m,c in equations[j].items()}
        for m,c in equations[i].items():v[lookup[(j,m)]]=-c
        if insert(v) is None:boundaries.append([i,j])
    known_rank=len(span.basis)
    new=[]
    for k,rel in enumerate(quartic['dependencies']):
        if insert(e.decode_weights(rel)) is None:new.append(k)
    assert len(span.basis)==quartic['kernel']
    return {'linear_multiple_generators':len(cubic['dependencies'])*len(ids),
            'linear_multiple_rank':linear_rank,'linear_independent_generators':linear_generators,
            'koszul_boundary_dimension':len(equations)*(len(equations)-1)//2,
            'additional_koszul_boundaries':boundaries,'linear_plus_koszul_rank':known_rank,
            'quadratic_minimal_generators':quartic['kernel']-linear_rank,
            'new_beyond_linear_and_koszul':len(new),'new_representatives':new,
            'koszul_H1_degree4':quartic['kernel']-len(equations)*(len(equations)-1)//2}


def run_family(number,reuse=None,sparse_order=False):
    start=time.perf_counter();initial=source()[number];stage=initial['stages'][-1]
    ids=stage['active'];assert ids==initial['remaining'] and not stage['removed']
    eq=[e.t.cert.decode(r['polynomial']) for r in stage['necessary']]
    print('family',number,'degree four',len(ids),'variables',len(eq),'quadratics',flush=True)
    quartic=load(Path(reuse)) if reuse else ordered_strand(eq,ids) if sparse_order else e.strand(eq,ids,4)
    if reuse:
        assert quartic['degree']==4 and quartic['tested_coordinates']==ids
        # The complete checker replays every supplied relation and rank.
    print('family',number,'quartic rank',quartic['rank'],'zeros',
          [p['coordinate'] for p in quartic['vanishings']],flush=True)
    layers=syzygy_layers(eq,ids,stage['strands'][1],quartic)
    print('family',number,'layers',layers['linear_multiple_rank'],layers['linear_plus_koszul_rank'],
          'new',layers['new_beyond_linear_and_koszul'],flush=True)
    row={'number':number,'source_sha256':source_sha(),'active':ids,'quartic':quartic,
         'layers':layers,'seconds':time.perf_counter()-start}
    save(OUT/f'family-{number}.json.gz',row)


def check_family(number,independent=False):
    start=time.perf_counter();initial=source()[number];record=load(OUT/f'family-{number}.json.gz')
    assert record['source_sha256']==source_sha() and record['number']==number
    stage=initial['stages'][-1];ids=stage['active'];assert record['active']==ids
    eq=[e.t.cert.decode(r['polynomial']) for r in stage['necessary']]
    if independent:
        from check_degree7_triples import IndependentModel
        model=IndependentModel()
    else:model=e.t.Model()
    original=next(f for f in e.original() if f['number']==number)
    counts=e.t.verify_family(model,original)
    active=initial['initial_active'];assert active==original['remaining']
    for s in initial['stages']:
        assert s['active']==active
        counts.update(e.check_physical(model,s))
        equations=[e.t.cert.decode(r['polynomial']) for r in s['necessary']]
        for strand in s['strands']:e.check_strand(equations,active,strand)
        active=[i for i in active if i not in s['removed']]
    assert active==ids
    check_quartic(eq,ids,record['quartic'])
    exact=syzygy_layers(eq,ids,stage['strands'][1],record['quartic'])
    assert exact==record['layers']
    mod=syzygy_layers(eq,ids,stage['strands'][1],record['quartic'],prime=PRIME)
    for key in ['linear_multiple_rank','linear_plus_koszul_rank','new_beyond_linear_and_koszul']:
        assert mod[key]==exact[key]
    removed={p['coordinate'] for p in record['quartic']['vanishings']}
    remaining=[i for i in ids if i not in removed]
    chars=sorted({model.dc[i] for i in remaining})
    # Mutation check on one of the actual newly found identities.
    broken=copy.deepcopy(record['quartic']['vanishings'][0]) if removed else None
    if broken:
        broken['products'][0][2]=str(Q(broken['products'][0][2])+1)
        assert e.expand_products(eq,broken['products'])!={(broken['coordinate'],)*4:Q(1)}
    result={'number':number,'status':'PASS','independent_physical_polynomials':independent,
            'physical_checks':dict(counts),'variables':len(ids),'quadratics':len(eq),
            'quartic':{k:record['quartic'][k] for k in ['domain','codomain','rank','kernel','quotient_dimension']},
            'layers':{k:v for k,v in exact.items() if k not in ['linear_independent_generators','additional_koszul_boundaries','new_representatives']},
            'forced_zero':sorted(removed),'remaining':remaining,'remaining_characters':chars,
            'corrupted_identity_rejected':bool(broken),'seconds':time.perf_counter()-start,
            'source_sha256':source_sha()}
    name=f'family-{number}-'+('independent-' if independent else '')+'validation.json'
    (OUT/name).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--family',type=int,choices=NUMBERS,required=True)
    p.add_argument('--reuse',help='Optional archived pilot to replay; discovery only.')
    p.add_argument('--sparse-order',action='store_true',help='Insert shorter Macaulay columns first.')
    p.add_argument('--check',action='store_true');p.add_argument('--independent',action='store_true')
    a=p.parse_args()
    if a.independent and not a.check:p.error('--independent requires --check')
    check_family(a.family,a.independent) if a.check else run_family(a.family,a.reuse,a.sparse_order)

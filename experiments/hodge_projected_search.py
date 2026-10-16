"""Degree-seven, three-character search through the complete correction map.

The Hodge analogy is the finite complex 0 -> R^840 --M_D--> R^rows -> 0.
Its cokernel component is an obstruction, not an existence certificate.
Discovery uses numerical projections; selected directions have rational duals.
Run --check for a standard-library-only exact replay of selected directions.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import product
import argparse, copy, gzip, hashlib, json, random, sys, time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'algebra'))
import degree6_e1 as p
import degree7_e1 as e1
from degree6_e2_model import modF
from degree6_quadratic_structure import B
from fixed_denominator_search import solve

OUT=ROOT/'results/hodge-projected-search'
SEED=202610164800
WEIGHTS=[Q(-4),Q(-2),Q(-1),Q(-1,2),Q(-1,4),Q(1,4),Q(1,2),Q(1),Q(2),Q(4)]

def jacobian_remainders(data,pairs):
    span=p.Elimination()
    for df in p.DF:
        for m in p.mons(2):span.insert(p.pmul(df,{m:Q(1)}))
    def remainder(D):
        result={};v=dict(D)
        while v:
            pivot=min(v);c=v[pivot]
            if pivot in span.basis:v=p.padd(v,span.basis[pivot][0],-c)
            else:result[pivot]=v.pop(pivot)
        return result
    return {i:remainder(pairs[i][0]) for i in data['retained_basis_indices']}

def recipes(data,pairs):
    remainders=jacobian_remainders(data,pairs)
    eligible=[i for i,r in remainders.items() if r]
    rng=random.Random(SEED);triples=[]
    while len(triples)<6:
        ids=sorted(rng.sample(eligible,3))
        if len({e1.character(next(iter(pairs[i][0]))) for i in ids})<3:continue
        if ids not in triples:triples.append(ids)
    specs=[]
    for family,ids in enumerate(triples):
        heights=[sum(abs(c) for c in pairs[i][0].values()) for i in ids]
        for a,b in product(WEIGHTS,repeat=2):
            coords=[[i,str(w/h)] for i,w,h in zip(ids,[Q(1),a,b],heights)]
            specs.append({'family':family,'coordinates':coords,'twists':[str(a),str(b)]})
    return specs,eligible

def build(spec,pairs):
    D={};N=[{} for _ in range(6)]
    for i,c in spec['coordinates']:
        c=Q(c);D=p.padd(D,pairs[i][0],c)
        for j in range(6):N[j]=p.padd(N[j],pairs[i][1][j],c)
    assert D and e1.directional(N)==p.pmul(p.A,D)
    assert len({e1.character(m) for m in modF(D)})==3
    return D,N

def fixed_system(spec,pairs,fields):
    D,N=build(spec,pairs)
    return modF(B(D,N)),[modF(B(D,K)) for K in fields]

def verify(case,pairs,fields):
    b,columns=fixed_system(case['spec'],pairs,fields)
    if case['status']=='rejected':
        dual={tuple(m):Q(c) for m,c in case['dual_functional']}
        assert sum(c*dual.get(m,0) for m,c in b.items())==1
        assert all(sum(c*dual.get(m,0) for m,c in col.items())==0 for col in columns)
    else:
        assert case['status']=='solvable'
        for i,c in case['corrections']:b=p.padd(b,columns[i],Q(c))
        assert not b

def replay():
    data,pairs=e1.load();fields,_=e1.koszul_fields()
    with gzip.open(OUT/'certificates.json.gz','rt') as f:packet=json.load(f)
    assert packet['target']=={'F':p.poly_json(p.F),'A':p.poly_json(p.A),'q':1}
    specs,eligible=recipes(data,pairs)
    assert packet['specs']==specs and packet['eligible_outside_J']==eligible
    assert packet['basis_sha256']==hashlib.sha256(e1.BASIS.read_bytes()).hexdigest()
    assert len(fields)==840
    report=json.loads((OUT/'report.json').read_text())
    assert len(report['records'])==len(specs)==600
    for i,record in enumerate(report['records']):
        assert record['candidate_id']==i and record['spec']==specs[i]
    for fam in report['families']:
        subset=report['records'][fam['family']*100:(fam['family']+1)*100]
        assert fam['basis_indices']==[i for i,c in subset[0]['spec']['coordinates']]
        for metric in ['coefficient','bombieri']:
            ordered=sorted((r for r in subset if r['metrics'][metric]['valid']),key=lambda r:r['metrics'][metric]['residual'])
            assert fam['selections'][metric]==[r['candidate_id'] for r in ordered[:2]]
        assert fam['selections']['random']==random.Random(SEED+fam['family']+1).sample([r['candidate_id'] for r in subset],2)
    selected=sorted(set(i for fam in report['families'] for ids in fam['selections'].values() for i in ids))
    assert selected==[case['candidate_id'] for case in packet['cases']]
    for case in packet['cases']:
        assert case['spec']==specs[case['candidate_id']];verify(case,pairs,fields)
    assert report['rejected']==sum(c['status']=='rejected' for c in packet['cases'])
    assert report['exact_candidates']==len(packet['cases'])
    damaged=copy.deepcopy(next(c for c in packet['cases'] if c['status']=='rejected'))
    damaged['dual_functional']=[[m,str(2*Q(c))] for m,c in damaged['dual_functional']]
    try:verify(damaged,pairs,fields)
    except AssertionError:pass
    else:raise AssertionError('Corrupted dual accepted')
    print(json.dumps({'exact_directions_replayed':len(packet['cases']),'full_Koszul_dimension':840,
        'outside_J_recipes_checked':len(specs),'damaged_dual_rejected':True}),flush=True)

def run():
    import math
    import numpy as np
    from scipy import sparse
    from scipy.sparse.linalg import lsmr
    start=time.perf_counter();data,pairs=e1.load();fields,_=e1.koszul_fields()
    specs,eligible=recipes(data,pairs);records=[];families=[];selected=set()
    OUT.mkdir(parents=True,exist_ok=True)
    for family in range(6):
        choices=[(i,s) for i,s in enumerate(specs) if s['family']==family]
        ids=[i for i,c in choices[0][1]['coordinates']]
        # Precompute all bilinear physical polynomials, retaining shared K coordinates.
        bb=[[modF(B(pairs[i][0],pairs[j][1])) for j in ids] for i in ids]
        mm=[[modF(B(pairs[i][0],K)) for K in fields] for i in ids]
        physical=sorted(set().union(*(set(q) for row in bb+mm for q in row)))
        lookup={m:k for k,m in enumerate(physical)}
        def vector(poly):
            v=np.zeros(len(physical))
            for m,c in poly.items():v[lookup[m]]=float(c)
            return v
        rhs=np.array([[vector(q) for q in row] for row in bb])
        matrices=[]
        for row in mm:
            entries=[(lookup[m],j,float(c)) for j,col in enumerate(row) for m,c in col.items()]
            rr,cc,vv=zip(*entries)
            matrices.append(sparse.coo_matrix((vv,(rr,cc)),shape=(len(physical),840)).tocsr())
        # Bombieri weights on the chosen remainder representative, not a canonical quotient metric.
        bombieri=np.array([math.prod(math.factorial(x) for x in m)/math.factorial(14) for m in physical])
        bombieri/=np.exp(np.mean(np.log(bombieri)))
        for candidate_id,spec in choices:
            a=np.array([float(Q(c)) for i,c in spec['coordinates']])
            b=np.einsum('i,j,ijr->r',a,a,rhs)
            M=sum(c*A for c,A in zip(a,matrices)).tocsr();M.eliminate_zeros()
            D,_=build(spec,pairs);dscale=sum(float(c)**2 for c in modF(D).values())
            row={'candidate_id':candidate_id,'spec':spec,'metrics':{}}
            for metric,w in [('coefficient',np.ones(len(b))),('bombieri',bombieri)]:
                bw=np.sqrt(w)*b;Mw=M.multiply(np.sqrt(w)[:,None]).tocsr()
                scale=np.sqrt(np.asarray(Mw.power(2).sum(axis=0)).ravel());active=scale>0
                T=Mw[:,active].multiply(1/scale[active]).tocsr()
                fit=lsmr(T,-bw,atol=1e-12,btol=1e-12,conlim=1e14,maxiter=4000)
                residual=bw+T@fit[0]
                normal=float(np.linalg.norm(T.T@residual)/max(np.linalg.norm(bw),1e-30))
                valid=fit[1]!=7 and normal<1e-8
                row['metrics'][metric]={'residual':float(np.linalg.norm(residual)/dscale),
                    'fraction_of_initial_energy':float(residual@residual/(bw@bw)),
                    'normal_equation_residual':normal,'iterations':int(fit[2]),'stop':int(fit[1]),'valid':valid}
            records.append(row)
        subset=records[-100:];selections={}
        for metric in ['coefficient','bombieri']:
            good=[r for r in subset if r['metrics'][metric]['valid']]
            selections[metric]=[r['candidate_id'] for r in sorted(good,key=lambda r:r['metrics'][metric]['residual'])[:2]]
        selections['random']=random.Random(SEED+family+1).sample([i for i,s in choices],2)
        selected.update(i for ids in selections.values() for i in ids)
        families.append({'family':family,'basis_indices':ids,'physical_rows':len(physical),'selections':selections})
        print('Numerical family',family,'complete; selected',selections,flush=True)
    cases=[]
    for i in sorted(selected):
        b,columns=fixed_system(specs[i],pairs,fields);case=solve(b,columns)
        case.update(candidate_id=i,spec=specs[i]);verify(case,pairs,fields);cases.append(case)
        print('EXACT',i,case['status'],flush=True)
    report={'seed':SEED,'target_commit':'b8c4edeb80a82395ec07164caf445cfa43bbbd56',
        'numerical_candidates':len(records),'exact_candidates':len(cases),
        'rejected':sum(c['status']=='rejected' for c in cases),'solvable':sum(c['status']=='solvable' for c in cases),
        'families':families,'records':records,'seconds':time.perf_counter()-start,
        'scope':'Six seeded three-character spans outside the Jacobian ideal; 100 rational coefficient choices per span. No continuous-family or complex-coefficient search. Full 840-dimensional numerator fibre and unrestricted quotient in exact checks. Metrics are heuristics, not intrinsic geometry or certificates.',
        'compute':'CPU sparse floating-point projection; standard-library rational certificate discovery/replay.'}
    packet={'target':{'F':p.poly_json(p.F),'A':p.poly_json(p.A),'q':1},'specs':specs,
        'eligible_outside_J':eligible,'basis_sha256':hashlib.sha256(e1.BASIS.read_bytes()).hexdigest(),'cases':cases}
    with gzip.open(OUT/'certificates.json.gz','wt',encoding='utf-8') as f:json.dump(packet,f,separators=(',',':'))
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    replay()

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions are required; do not use -O.')
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true')
    if parser.parse_args().check:replay()
    else:run()

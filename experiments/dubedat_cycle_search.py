"""A determinant/cofactor search inspired by Dubedat's dimer operators.

This is a chosen polynomial matrix on a six-cycle, not a discrete CR operator
or a theorem transferring dimer/GFF results to the holdout. Exact E1 lifts are
built in. Every fixed-D E2 test retains all 840 Koszul correction directions.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations, permutations
from concurrent.futures import ProcessPoolExecutor
import argparse, copy, gzip, hashlib, json, sys, time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'algebra'))
import degree6_e1 as p
import degree7_e1 as e1
from degree6_e2_model import modF
from degree6_quadratic_structure import B
from fixed_denominator_search import solve

OUT=ROOT/'results/dubedat-cycle'
X=[{tuple(int(i==j) for j in range(6)):Q(1)} for i in range(6)]

def scale(a,c):return {m:v*c for m,v in a.items() if v*c}

def determinant(matrix):
    result={}
    for perm in permutations(range(3)):
        term={(0,)*6:Q(1)}
        for i,j in enumerate(perm):term=p.pmul(term,matrix[i][j])
        inversions=sum(perm[i]>perm[j] for i in range(3) for j in range(i+1,3))
        result=p.padd(result,term,(-1)**inversions)
    return result

def build(spec):
    i,j=spec['gradient_pair'];tau=Q(spec['twist'])
    if spec['edges']=='monomial':L=[X[0],X[2],X[3],X[4]]
    else:
        assert spec['edges']=='mixed'
        L=[p.padd(X[0],X[3]),p.padd(X[2],X[5]),
           p.padd(X[0],X[4]),p.padd(X[1],X[4])]
    matrix=[[p.DF[i],scale(p.DF[j],tau),{}],
            [{},L[0],L[1]],[L[2],{},L[3]]]
    h=[{} for _ in range(6)]
    h[i]=p.pmul(L[0],L[3]);h[j]=scale(p.pmul(L[1],L[2]),tau)
    D=p.padd(p.pmul(p.DF[i],h[i]),p.pmul(p.DF[j],h[j]))
    assert D==determinant(matrix) and D and all(sum(m)==7 for m in D)
    N=[p.pmul(p.A,v) for v in h]
    directional={}
    for derivative,n in zip(p.DF,N):directional=p.padd(directional,p.pmul(derivative,n))
    assert directional==p.pmul(p.A,D)
    # Reciprocal edge rescaling preserves the two matching products exactly.
    # It is a negative control, not another candidate or a search improvement.
    matrix[1][1]=scale(L[0],Q(2));matrix[2][2]=scale(L[3],Q(1,2))
    assert determinant(matrix)==D
    assert p.pmul(matrix[1][1],matrix[2][2])==h[i]
    canonical=modF(D);assert canonical
    leading=canonical[min(canonical)]
    canonical=scale(canonical,1/leading)
    return D,N,canonical

def specs():
    return [{'gradient_pair':list(pair),'edges':kind,'twist':str(tau)}
            for kind,tau in [('monomial',1),('mixed',1),('mixed',-1)]
            for pair in combinations(range(6),2)]

def model(D,N,fields):
    return modF(B(D,N)),[modF(B(D,K)) for K in fields]

def check_case(case,fields):
    D,N,canonical=build(case['spec']);rhs,columns=model(D,N,fields)
    assert case['D']==p.poly_json(D)
    assert case['canonical_D']==p.poly_json(canonical)
    assert case['characters_mod_gauge']==[list(c) for c in sorted({e1.character(m) for m in canonical})]
    if case['status']=='rejected':
        dual={tuple(m):Q(c) for m,c in case['dual_functional']}
        assert sum(c*dual.get(m,0) for m,c in rhs.items())==1
        assert all(sum(c*dual.get(m,0) for m,c in col.items())==0 for col in columns)
    else:
        assert case['status']=='solvable'
        actual=rhs
        for i,c in case['corrections']:actual=p.padd(actual,columns[i],Q(c))
        assert not actual

def compute(spec):
    started=time.perf_counter();D,N,canonical=build(spec)
    fields,_=e1.koszul_fields();rhs,columns=model(D,N,fields)
    result=solve(rhs,columns)
    result.update(spec=spec,D=p.poly_json(D),canonical_D=p.poly_json(canonical),
        characters_mod_gauge=[list(c) for c in sorted({e1.character(m) for m in canonical})],
        seconds=time.perf_counter()-started)
    check_case(result,fields)
    return result

def replay():
    with gzip.open(OUT/'certificates.json.gz','rt') as f:packet=json.load(f)
    assert packet['specs']==specs() and len(packet['cases'])==len(specs())
    assert packet['target']=={'F':p.poly_json(p.F),'A':p.poly_json(p.A),'q':1}
    fields,_=e1.koszul_fields();assert len(fields)==840
    for spec,case in zip(specs(),packet['cases']):
        assert case['spec']==spec;check_case(case,fields)
    damaged=copy.deepcopy(next(case for case in packet['cases'] if case['status']=='rejected'))
    damaged['dual_functional']=[[m,str(2*Q(c))] for m,c in damaged['dual_functional']]
    try:check_case(damaged,fields)
    except AssertionError:pass
    else:raise AssertionError('Damaged dual was accepted')
    report=json.loads((OUT/'report.json').read_text())
    assert report['cases']==len(packet['cases'])
    assert report['rejected']==sum(c['status']=='rejected' for c in packet['cases'])
    assert report['certificate_sha256']==hashlib.sha256((OUT/'certificates.json.gz').read_bytes()).hexdigest()
    print(json.dumps({'exact_cases_replayed':len(packet['cases']),
        'Koszul_corrections_per_case':840,'determinants_and_E1_checked':True,
        'reciprocal_edge_controls_checked':len(packet['cases']),
        'corrupted_dual_rejected':True}),flush=True)

def run(workers):
    started=time.perf_counter();cases=[]
    with ProcessPoolExecutor(max_workers=workers) as pool:
        for case in pool.map(compute,specs()):
            cases.append(case)
            print('CASE',len(cases),case['spec'],case['status'],flush=True)
    OUT.mkdir(parents=True,exist_ok=True)
    packet={'specs':specs(),'target':{'F':p.poly_json(p.F),'A':p.poly_json(p.A),'q':1},'cases':cases}
    with gzip.open(OUT/'certificates.json.gz','wt',encoding='utf-8') as f:json.dump(packet,f,separators=(',',':'))
    groups=[]
    for kind,tau in [('monomial','1'),('mixed','1'),('mixed','-1')]:
        selected=[c for c in cases if c['spec']['edges']==kind and c['spec']['twist']==tau]
        groups.append({'edges':kind,'twist':tau,'cases':len(selected),
            'rejected':sum(c['status']=='rejected' for c in selected),
            'character_counts_mod_gauge':sorted({len(c['characters_mod_gauge']) for c in selected})})
    unique={json.dumps(c['canonical_D'],sort_keys=True) for c in cases}
    report={'cases':len(cases),'distinct_D_directions_mod_gauge':len(unique),
        'rejected':sum(c['status']=='rejected' for c in cases),
        'solvable_E2':sum(c['status']=='solvable' for c in cases),'groups':groups,
        'Koszul_corrections_per_case':840,'reciprocal_edge_controls':len(cases),
        'certificate_sha256':hashlib.sha256((OUT/'certificates.json.gz').read_bytes()).hexdigest(),
        'seconds':time.perf_counter()-started,
        'scope':'Finite fixed-denominator search over Q with exact obstructions valid over C. '
                'No exclusion of all cycle matrices, continuous twists, mixed-character families, or degree seven. '
                'No certificate of existence or Lean theorem. CPU rational arithmetic; no GPU claim.'}
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Do not use -O; assertions verify identities.')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true');parser.add_argument('--workers',type=int,default=2)
    args=parser.parse_args()
    if args.check:replay()
    else:run(args.workers)

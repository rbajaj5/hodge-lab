"""Independent polynomial assembly of every shortlisted E1/E2 dual check."""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations
import gzip, json, sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'algebra'))
from degree7_verify_polynomials import poly, decode, remainder, B

def run():
    target=poly.load_target(ROOT/'sources/sextics/data/holdout');F,A=target['F'],target['A']
    assert target['q']==1
    data=json.loads((ROOT/'algebra/degree7_e1_basis.json').read_text())
    pairs=[(decode(p['D']),[decode(n) for n in p['N']]) for p in data['basis']]
    DF=[poly.derivative(F,i) for i in range(6)];fields=[]
    # Generate the complete homogeneous cubic monomials without the producer's iterator.
    monomials=[(a,b,c,d,e,3-a-b-c-d-e) for a in range(3,-1,-1) for b in range(3-a,-1,-1)
               for c in range(3-a-b,-1,-1) for d in range(3-a-b-c,-1,-1) for e in range(3-a-b-c-d,-1,-1)]
    for i,j in combinations(range(6),2):
        for m in monomials:
            K=[{} for _ in range(6)];K[i]=poly.mul({m:Q(1)},DF[j]);K[j]=poly.scale(poly.mul({m:Q(1)},DF[i]),-1)
            fields.append(K)
    assert len(fields)==840
    out=ROOT/'results/hodge-projected-search'
    with gzip.open(out/'certificates.json.gz','rt') as f:packet=json.load(f)
    assert packet['target']['q']==1 and decode(packet['target']['F'])==F and decode(packet['target']['A'])==A
    columns=0
    for case in packet['cases']:
        D={};N=[{} for _ in range(6)]
        for i,c in case['spec']['coordinates']:
            D=poly.add(D,poly.scale(pairs[i][0],Q(c)))
            N=[poly.add(n,poly.scale(p,Q(c))) for n,p in zip(N,pairs[i][1])]
        directional={}
        for n,df in zip(N,DF):directional=poly.add(directional,poly.mul(n,df))
        assert directional==poly.mul(A,D)
        dual={tuple(m):Q(c) for m,c in case['dual_functional']}
        apply=lambda q:sum(c*dual.get(m,0) for m,c in remainder(q,F).items())
        assert case['status']=='rejected' and apply(B(D,N))==1
        for K in fields:assert apply(B(D,K))==0;columns+=1
    print(json.dumps({'independent_exact_directions':len(packet['cases']),'correction_columns_checked':columns,
        'opposite_division_order':True,'full_target_read_from_pinned_instance':True}))

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Do not disable assertions')
    run()

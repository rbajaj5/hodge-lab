"""Rebuild every degree-seven character equation using a second polynomial API.

The generating B/modF routines are not imported. Division eliminates physical
monomials in the opposite order. All stored E1 lifts and gauge vectors are
checked against the pinned target, then every E2 coefficient is reconstructed.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations_with_replacement, product
import gzip, json, sys

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'experiments'))
import gpu_identity_screen as poly


def decode(terms):return {tuple(m):Q(c) for c,m in terms}


def remainder(P,F):
    result=dict(P);lead=(6,0,0,0,0,0);assert F[lead]==1
    while any(m[0]>=6 for m in result):
        m=min(m for m in result if m[0]>=6);c=result.pop(m)
        shift=(m[0]-6,)+m[1:]
        for n,d in F.items():
            if n==lead:continue
            k=tuple(a+b for a,b in zip(shift,n));result[k]=result.get(k,0)-c*d
            if not result[k]:del result[k]
    return result


def B(D,N):
    divergence={};directional={}
    for i,component in enumerate(N):
        divergence=poly.add(divergence,poly.derivative(component,i))
        directional=poly.add(directional,poly.mul(component,poly.derivative(D,i)))
    return poly.add(poly.mul(D,divergence),poly.scale(directional,-1))


def run():
    target=poly.load_target(ROOT/'sources/sextics/data/holdout');F,A=target['F'],target['A']
    assert target['q']==1
    data=json.loads((ROOT/'algebra/degree7_e1_basis.json').read_text())
    assert decode(data['F'])==F and decode(data['A'])==A
    pairs=[(decode(p['D']),[decode(n) for n in p['N']]) for p in data['basis']]
    DF=[poly.derivative(F,i) for i in range(6)]
    for D,N in pairs:
        actual={}
        for p,d in zip(N,DF):actual=poly.add(actual,poly.mul(p,d))
        assert actual==poly.mul(A,D)
    for gauge in data['gauge_vectors']:
        actual={}
        for i,c in gauge['basis_coordinates']:actual=poly.add(actual,poly.scale(pairs[i][0],Q(c)))
        unit=tuple(int(i==gauge['coordinate']) for i in range(6))
        assert actual==poly.mul(F,{unit:Q(1)})
    W=data['character_generators']
    char=lambda m:tuple(sum(x*y for x,y in zip(w,m))%6 for w in W)
    group={tuple(sum(h[j]*W[j][i] for j in range(3))%6 for i in range(6)) for h in product(range(6),repeat=3)}
    assert len(group)==216 and {char(m) for m in F}=={(0,0,0)}
    fields=[];field_chars=[]
    for i,j,m in data['koszul_labels']:
        K=[{} for _ in range(6)];K[i]=poly.mul({tuple(m):Q(1)},DF[j]);K[j]=poly.scale(poly.mul({tuple(m):Q(1)},DF[i]),-1)
        weights={tuple((x-w[component])%6 for x,w in zip(char(n),W)) for component,p in enumerate(K) for n in p}
        assert len(weights)==1;fields.append(K);field_chars.append(weights.pop())
    with gzip.open(ROOT/'results/degree7-characters/certificates.json.gz','rt') as handle:packet=json.load(handle)
    columns=coefficients=gauge_checks=0
    for family in packet['families']:
        ids=family['denominator_basis_indices'];delta=tuple(family['character'])
        assert all({char(m) for m in pairs[i][0]}=={delta} for i in ids)
        needed=tuple((a+d)%6 for a,d in zip(char(next(iter(A))),delta))
        selected=[i for i,c in enumerate(field_chars) if c==needed]
        assert selected==family['Koszul_indices']
        expected={tuple(m):{tuple(k):Q(c) for k,c in eq} for m,eq in zip(family['physical_monomials'],family['equations'])}
        actual={}
        def add_column(p,parameters):
            nonlocal columns,coefficients
            p=remainder(p,F);columns+=1;coefficients+=len(p)
            for m,c in p.items():actual.setdefault(m,{})[parameters]=c
        for i,j in combinations_with_replacement(range(len(ids)),2):
            D,N=pairs[ids[i]];E,P=pairs[ids[j]];p=B(D,P)
            if i!=j:p=poly.add(p,B(E,N))
            add_column(p,(i,j))
        for i,index in enumerate(ids):
            for j,k in enumerate(selected):add_column(B(pairs[index][0],fields[k]),(i,len(ids)+j))
        assert actual==expected
    # Generalized gauge has an extra -F*N(h) term when h is linear.
    for D,N in pairs:
        div={}
        for i,p in enumerate(N):div=poly.add(div,poly.derivative(p,i))
        for coordinate in range(6):
            h={tuple(int(i==coordinate) for i in range(6)):Q(1)}
            E=[poly.scale(poly.mul(poly.mul(A,h),{tuple(int(j==i) for j in range(6)):Q(1)}),Q(1,6)) for i in range(6)]
            lhs=poly.add(B(poly.add(D,poly.mul(F,h)),[poly.add(n,e) for n,e in zip(N,E)]),poly.scale(B(D,N),-1))
            rhs=poly.mul(F,poly.add(poly.add(poly.mul(h,div),poly.scale(N[coordinate],-1)),poly.mul(A,poly.mul(h,h))))
            assert lhs==rhs;gauge_checks+=1
    result={'all_E1_lifts_verified':len(pairs),'diagonal_group_order':len(group),
        'all_degree7_linear_gauge_identities_verified':gauge_checks,
        'families_reconstructed':len(packet['families']),'E2_columns_reconstructed':columns,
        'nonzero_coefficients_checked':coefficients,'opposite_physical_monomial_reduction':True,
        'scope':'Independent polynomial construction check; character-branch proof replay is a separate command.'}
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    run()

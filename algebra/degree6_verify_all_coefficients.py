"""Reconstruct EVERY E2 coefficient directly, using an independent assembly.

No parameter sampling: all 5,886 aa and 34,020 az columns are checked.
The division loop and derivative assembly are independent of the exporter.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import combinations
import gzip
import hashlib
import json
import time

if not __debug__:
    raise RuntimeError('Exact verification requires assertions; do not use -O.')
HERE=Path(__file__).resolve().parent


def add(p,q,c=Q(1)):
    out=dict(p)
    for m,v in q.items():
        out[m]=out.get(m,Q(0))+c*v
        if not out[m]:del out[m]
    return out


def multiply(p,q):
    out={}
    for m,c in p.items():
        for n,d in q.items():
            key=tuple(x+y for x,y in zip(m,n))
            out[key]=out.get(key,Q(0))+c*d
    return {m:c for m,c in out.items() if c}


def derivative(p,i):
    out={}
    for m,c in p.items():
        if m[i]:
            n=list(m);n[i]-=1;out[tuple(n)]=c*m[i]
    return out


def decode(terms):
    return {tuple(m):Q(c) for c,m in terms}


def main():
    started=time.perf_counter()
    source=HERE/'degree6_full_e2_model.json.gz'
    with gzip.open(source,'rt') as f:model=json.load(f)
    basis_path=HERE/'degree6_e1_basis.json'
    assert model['source_basis_sha256']==hashlib.sha256(basis_path.read_bytes()).hexdigest()
    basis=json.loads(basis_path.read_text())
    pure=[tuple(6 if i==j else 0 for i in range(6)) for j in range(6)]
    F={m:Q(1) for m in pure}
    F[(3,1,0,1,1,0)]=Q(1);F[(0,3,1,0,1,1)]=Q(1)
    A={(3,0,0,3,0,0):Q(1)}
    dF=[derivative(F,i) for i in range(6)]
    pairs=[(decode(p['D']),[decode(n) for n in p['N']]) for p in basis['basis']]
    for D,N in pairs:
        actual={}
        for i in range(6):actual=add(actual,multiply(N[i],dF[i]))
        assert actual==multiply(A,D)
    assert len(pairs)==109
    pairs=pairs[:108]
    derivatives=[[derivative(D,i) for i in range(6)] for D,N in pairs]
    nums=[N for D,N in pairs]
    for i,j,mon in model['koszul_labels']:
        assert 0<=i<j<6 and sum(mon)==2
        K=[{} for _ in range(6)]
        K[i]=multiply({tuple(mon):Q(1)},dF[j])
        K[j]=multiply({tuple(mon):Q(-1)},dF[i])
        nums.append(K)
    assert len(nums)==423
    divergences=[]
    for N in nums:
        divergence={}
        for i in range(6):divergence=add(divergence,derivative(N[i],i))
        divergences.append(divergence)

    def B(i,j):
        value=multiply(pairs[i][0],divergences[j])
        for k in range(6):value=add(value,multiply(nums[j][k],derivatives[i][k]),Q(-1))
        return value

    def remainder(poly):
        work=dict(poly);out={}
        while work:
            mon=max(work);coefficient=work.pop(mon)
            if mon[0]<6:
                out[mon]=out.get(mon,Q(0))+coefficient
            else:
                shift=(mon[0]-6,)+mon[1:]
                for term,c in F.items():
                    if term==pure[0]:continue
                    key=tuple(x+y for x,y in zip(shift,term))
                    work[key]=work.get(key,Q(0))-coefficient*c
                    if not work[key]:del work[key]
        return {m:c for m,c in out.items() if c}

    count=len(model['aa_columns'])+108*315
    serialized=[{} for _ in range(count)]
    for row,col,num,den in model['entries']:
        mon=tuple(model['row_monomials'][row]);assert mon not in serialized[col]
        serialized[col][mon]=Q(num,den)
    for col,(i,j) in enumerate(model['aa_columns']):
        value=B(i,j)
        if i!=j:value=add(value,B(j,i))
        assert remainder(value)==serialized[col],('aa',i,j)
    offset=model['az_column_offset']
    for i in range(108):
        for k in range(315):
            assert remainder(B(i,108+k))==serialized[offset+i*315+k],('az',i,k)
    result={'verified':True,'all109_first_equation_lifts_checked':True,
            'aa_columns_checked':len(model['aa_columns']),'az_columns_checked':108*315,
            'nonzero_rational_coefficients_checked':len(model['entries']),
            'source_tensor_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
            'method':'Independent direct divergence/derivative assembly and lexicographic polynomial division; all columns, no random sampling.',
            'seconds':time.perf_counter()-started}
    (HERE/'degree6_all_coefficients_validation.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()

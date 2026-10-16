"""Solve the complete degree-six numerator-correction problem for fixed D.

All arithmetic is rational. Failed candidates export a dual functional L with
L(M)=0 and L(b)=1, so M*z+b=0 has no solution over C for that fixed denominator.
The full coefficient tensor is independently checked by
degree6_verify_all_coefficients.py. No assertion about all denominators follows.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse, copy, gzip, hashlib, json, random, time
import degree6_e1 as e1

HERE=Path(__file__).resolve().parent
PACKET=HERE/'fixed-denominator-report.json'


def load_model():
    with gzip.open(HERE/'degree6_full_e2_model.json.gz','rt') as f:model=json.load(f)
    return model


def specialize(model,a):
    b={};columns=[{} for _ in range(315)];off=model['az_column_offset']
    for row,col,num,den in model['entries']:
        if col<off:
            i,j=model['aa_columns'][col];weight=a.get(i,0)*a.get(j,0);out=b
        else:
            i,k=divmod(col-off,315);weight=a.get(i,0);out=columns[k]
        if weight:out[row]=out.get(row,Q(0))+weight*Q(num,den)
    return {r:c for r,c in b.items() if c},[{r:c for r,c in col.items() if c} for col in columns]


def solve(b,columns):
    span=e1.Elimination()
    for j,col in enumerate(columns):span.insert(dict(col),{j:Q(1)})
    remainder=dict(b);solution={}
    for pivot,(row,comb) in sorted(span.basis.items()):
        scale=remainder.get(pivot,0)
        if scale:
            remainder=e1.padd(remainder,row,-scale)
            solution=e1.padd(solution,comb,-scale)
    if not remainder:
        actual=dict(b)
        for j,c in solution.items():actual=e1.padd(actual,columns[j],c)
        assert not actual
        return {'status':'solvable','corrections':[[j,str(c)] for j,c in sorted(solution.items())]}
    free=min(remainder);dual={free:Q(1)}
    for pivot,(row,_) in sorted(span.basis.items(),reverse=True):
        value=-sum(c*dual.get(i,0) for i,c in row.items() if i!=pivot)
        if value:dual[pivot]=value
    value=sum(c*dual.get(r,0) for r,c in b.items())
    assert value==remainder[free] and value
    dual={r:c/value for r,c in dual.items()}
    assert all(sum(c*dual.get(r,0) for r,c in col.items())==0 for col in columns)
    assert sum(c*dual.get(r,0) for r,c in b.items())==1
    return {'status':'rejected','correction_matrix_rank':len(span.basis),
            'dual_functional':[[r,str(c)] for r,c in sorted(dual.items())]}


def check(model,row):
    a={int(i):Q(c) for i,c in row['denominator_coordinates']}
    assert a and all(0<=i<108 for i in a)
    b,columns=specialize(model,a)
    if row['status']=='rejected':
        dual={r:Q(c) for r,c in row['dual_functional']}
        assert all(sum(c*dual.get(r,0) for r,c in col.items())==0 for col in columns)
        assert sum(c*dual.get(r,0) for r,c in b.items())==1
    else:
        assert row['status']=='solvable'
        actual=dict(b)
        for j,c in row['corrections']:actual=e1.padd(actual,columns[j],Q(c))
        assert not actual


def replay():
    model=load_model();report=json.loads(PACKET.read_text())
    assert report['model_sha256']==hashlib.sha256((HERE/'degree6_full_e2_model.json.gz').read_bytes()).hexdigest()
    for row in report['cases']:check(model,row)
    altered=copy.deepcopy(next(r for r in report['cases'] if r['status']=='rejected'))
    altered['dual_functional'][0][1]=str(2*Q(altered['dual_functional'][0][1]))
    try:check(model,altered)
    except AssertionError:pass
    else:raise AssertionError('Altered dual certificate was accepted.')
    print(json.dumps({'replayed':len(report['cases']),'corrupted_dual_rejected':True}))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true')
    if parser.parse_args().check:replay();return
    start=time.perf_counter();model=load_model();rng=random.Random(202610162155)
    candidates=[{i:Q(1)} for i in range(108)]
    # Five retained directions appearing in F's basis coordinates.
    for _ in range(12):
        candidates.append({i:Q(rng.choice([-3,-2,-1,1,2,3])) for i in [0,36,82,96,105]})
    cases=[]
    for index,a in enumerate(candidates):
        b,columns=specialize(model,a);result=solve(b,columns)
        result['denominator_coordinates']=[[i,str(c)] for i,c in sorted(a.items())]
        check(model,result);cases.append(result)
        if (index+1)%20==0:print('Checked',index+1,'fixed denominators',flush=True)
    report={'seed':202610162155,'model_sha256':hashlib.sha256((HERE/'degree6_full_e2_model.json.gz').read_bytes()).hexdigest(),
        'candidates':len(cases),'rejected':sum(r['status']=='rejected' for r in cases),
        'solvable':sum(r['status']=='solvable' for r in cases),'cases':cases,
        'seconds':time.perf_counter()-start,
        'scope':'All 315 degree-six Koszul corrections are allowed for each chosen denominator. Exact rational dual certificates exclude only these fixed denominator directions and nonzero scalar multiples; no global degree-six exclusion or Hodge solve. Individual-direction scans were already reported by fqlx; no novelty claimed.'}
    PACKET.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='cases'},indent=2))
    replay()


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O; exact verification requires assertions.')
    main()

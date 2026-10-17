#!/usr/bin/env python3
"""Seven bounded exact first-polar denominator tests for the fixed cyclic target."""
from pathlib import Path
from fractions import Fraction as Q
import argparse
import json
import subprocess
import sys
import time
import cyclic_fano_branch_products as engine

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/cyclic-fano-branch-polars'
old=engine.old; base=engine.base; poly=engine.poly; GQ=engine.GQ
W=base.WEIGHTS; BASE=(0,1,3,4,5)
NAMES=('X0','X1','Y0','Y1','Y2')
DEPS=('cyclic_fano_branch_products.py',)+engine.DEPS
SPECS=[('polar_'+name,tuple(int(i==j)for i in range(5)))for j,name in enumerate(NAMES)]
SPECS += [('polar_X0_plus_Y0',(1,0,1,0,0)),('polar_X1_plus_Y1',(0,1,0,1,0))]


def save(name,value):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')


def bindings():
    return {'producer_sha256':poly.sha(Path(__file__)),
            'dependencies':{name:poly.sha(ROOT/'experiments'/name)for name in DEPS},
            'source_instance_sha256':poly.sha(base.SOURCE/'source/instance.rec'),
            'source_commit':'d96911d725077e66a8f10848908be01a643b1714'}


def derivative(p,v):
    return base.total(poly.scale(poly.derivative(p,j),v[i])for i,j in enumerate(BASE))


def construct(v):
    F,A,G,beta=base.target()
    q={m[:2]+(0,)+m[3:]:c for m,c in G.items()if m[2]==1}
    h={m:c for m,c in G.items()if not m[2]}
    delta=poly.add(poly.mul(q,q),h,-4);J=poly.derivative(G,2)
    E=derivative(delta,v);qv=derivative(q,v)
    assert E and all(sum(m)==5 and not m[2]for m in E)
    assert E==poly.add(poly.scale(poly.mul(J,qv),2),derivative(G,v),-4)
    particular=[{}for _ in W]
    for i,j in enumerate(BASE):particular[j]=poly.scale(beta,-4*v[i])
    particular[2]=poly.scale(poly.mul(beta,qv),2)
    assert base.contraction(particular,G)==poly.mul(beta,E)
    residual=poly.scale(poly.add(poly.mul(beta,derivative(E,v)),poly.mul(derivative(beta,v),E),-1),4)
    assert base.B(E,particular)==residual
    # Replay the physical original-target identities, not only weighted ones.
    N=base.lift(particular);D=base.pullback(E)
    jac={(0,0,2,0,0,0):Q(3)}
    assert base.contraction(N,F)==poly.mul(A,D)
    assert base.B(D,N)==poly.mul(jac,base.pullback(residual))
    return G,beta,delta,E,particular,residual


def quotient(dividend,G):
    """Exact monic Z division; return quotient and remainder."""
    rest=dividend.copy();answer={};lead=(0,0,2,0,0,0)
    assert G[lead]==1
    while any(m[2]>=2 for m in rest):
        m=max((m for m in rest if m[2]>=2),key=lambda m:(m[2],m))
        c=rest[m];n=list(m);n[2]-=2;n=tuple(n)
        answer=poly.add(answer,{n:c});rest=poly.add(rest,poly.mul({n:c},G),-1)
    assert dividend==poly.add(poly.mul(answer,G),rest)
    return answer,rest


def calculate(name,v):
    started=time.perf_counter();G,beta,delta,E,P,residual=construct(v)
    reduce=engine.reducer(G);rhs=reduce(poly.scale(residual,-1))
    columns=list(engine.koszul_columns(5,E,G,reduce))
    equations,labels=engine.linear_system(iter(columns),rhs)
    dual,solution,rank,processed=engine.eliminate(equations,rhs,len(columns))
    assert len(columns)==25 and len(base.monomials(2))==15
    corrected=None;quot=None
    if dual is not None:
        assert engine.check_dual(dual,iter(columns),rhs)==25
    else:
        corrected=[p.copy()for p in P];grad=[poly.derivative(G,j)for j in range(6)]
        for coefficient,label in zip(solution,labels):
            i,j=label['coordinates'];h={tuple(label['powers']):coefficient}
            corrected[i]=poly.add(corrected[i],poly.mul(h,grad[j]))
            corrected[j]=poly.add(corrected[j],poly.mul(h,grad[i]),-1)
        assert base.contraction(corrected,G)==poly.mul(beta,E)
        quot,rem=quotient(base.B(E,corrected),G);assert not rem
        assert all(sum(w*x for w,x in zip(W,m))==2 for m in quot)
    return {'schema':'cyclic-fano-branch-polars-v1','id':name,**bindings(),
            'direction':list(v),'direction_variables':list(NAMES),'weighted_variables':['X0','X1','Z','Y0','Y1','Y2'],
            'degree':5,'Delta':old.encode(delta),'denominator':old.encode(E),
            'particular':[old.encode(p)for p in P],'residual':old.encode(residual),'rhs':old.encode(rhs),
            'status':'excluded'if dual is not None else 'exact_polynomial_witness',
            'dual':old.encode(dual)if dual is not None else None,
            'corrected_field':[old.encode(p)for p in corrected]if corrected else None,
            'quotient':old.encode(quot)if quot is not None else None,
            'correction_coefficients':[c.pair()for c in solution]if solution is not None else None,
            'columns':[{'label':label,'polynomial':old.encode(p)}for label,p in columns],
            'active_rows':len(equations),'ambient_remainder_rows':sum(m[2]<2 for m in base.monomials(8)),
            'complete_Koszul_directions':25,'quotient_dimension_eliminated':15,
            'full_projected_numerator_dimension':sum(len(base.monomials(5+w-2))for w in W),
            'rank_lower_bound':rank,'rows_processed':processed,'seconds':time.perf_counter()-started,
            'scope':'Only this fixed direction. Seven tested polars do not exclude the full five-parameter polar family.',
            'attribution':'Dolgachev, Classical Algebraic Geometry: a modern view, supplied excerpt §1.1.2, first polars; applied here to Delta=Q^2-4H.'}


def verify():
    checks=[];unresolved=[];mutations=0
    for name,v in SPECS:
        attempt=json.loads((OUT/('attempt-'+name+'.json')).read_text(encoding='utf-8'))
        assert attempt['bindings']==bindings()and attempt['direction']==list(v)
        if attempt['status']!='completed':
            assert attempt['status']in ('timeout','error');unresolved.append({'id':name,'status':attempt['status']});continue
        path=OUT/(name+'.json');packet=json.loads(path.read_text(encoding='utf-8'))
        assert all(packet[k]==value for k,value in bindings().items())
        G,beta,delta,E,P,residual=construct(v);reduce=engine.reducer(G)
        assert packet['direction']==list(v)and packet['denominator']==old.encode(E)
        assert packet['Delta']==old.encode(delta)and packet['particular']==[old.encode(p)for p in P]
        assert packet['residual']==old.encode(residual)
        rhs=reduce(poly.scale(residual,-1));assert packet['rhs']==old.encode(rhs)
        columns=list(engine.koszul_columns(5,E,G,reduce))
        assert packet['columns']==[{'label':label,'polynomial':old.encode(p)}for label,p in columns]
        if packet['status']=='excluded':
            dual=old.decode(packet['dual']);assert engine.check_dual(dual,iter(columns),rhs)==25
            assert sum((c*rhs.get(m,0)for m,c in poly.scale(dual,2).items()),GQ())!=1;mutations+=1
            assert sum((c*poly.scale(rhs,2).get(m,0)for m,c in dual.items()),GQ())!=1;mutations+=1
        else:
            assert packet['status']=='exact_polynomial_witness'
            field=[old.decode(p)for p in packet['corrected_field']]
            assert base.contraction(field,G)==poly.mul(beta,E)
            assert base.B(E,field)==poly.mul(old.decode(packet['quotient']),G)
        checks.append({'id':name,'status':packet['status'],'packet_sha256':poly.sha(path),'columns_checked':25})
    receipt={'schema':'cyclic-fano-branch-polars-validation-v1','status':'PASS',**bindings(),
             'checks':checks,'unresolved':unresolved,'negative_controls_rejected':mutations}
    save('validation.json',receipt);print(json.dumps(receipt))


def main():
    assert __debug__,'Run without -O'
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('list','run','worker','verify'))
    parser.add_argument('--candidate');parser.add_argument('--seconds',type=int,default=60);args=parser.parse_args()
    if args.command=='list':print(json.dumps(SPECS));return
    if args.command=='verify':verify();return
    name,v=next(item for item in SPECS if item[0]==args.candidate)
    if args.command=='worker':
        item=calculate(name,v);save(name+'.json',item)
        print(json.dumps({'id':name,'status':item['status'],'dual_terms':len(item['dual']or []),'seconds':item['seconds']}));return
    started=time.perf_counter()
    try:
        child=subprocess.run([sys.executable,'-S',str(Path(__file__)),'worker','--candidate',name],capture_output=True,text=True,timeout=args.seconds)
        result={'status':'completed'if child.returncode==0 else 'error','returncode':child.returncode,'stdout':child.stdout,'stderr':child.stderr}
    except subprocess.TimeoutExpired:
        result={'status':'timeout','stop_reason':'Worker wall-clock bound; no mathematical conclusion from this attempt.'}
    result.update(id=name,direction=list(v),bindings=bindings(),time_limit_seconds=args.seconds,elapsed_seconds=time.perf_counter()-started)
    save('attempt-'+name+'.json',result);print(json.dumps(result))


if __name__=='__main__':main()

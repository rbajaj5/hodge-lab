#!/usr/bin/env python3
"""Bounded exact tests of powers/products, preserving full quotient freedom."""
from pathlib import Path
from functools import lru_cache
from fractions import Fraction as Q
import argparse
import json
import subprocess
import sys
import time
import cyclic_fano_guided_denominators as old
import cyclic_fano_branch_compact as compact

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/cyclic-fano-branch-products'
INPUT=ROOT/'results/cyclic-fano-higher-unfolding/candidates.json'
base=old.base;poly=base.poly;GQ=old.GQ
W=base.WEIGHTS;ZERO=(0,)*6
DEPS=('cyclic_fano_guided_denominators.py','cyclic_fano_transfer.py','quadric_contact_pilot.py','cyclic_fano_branch_compact.py')
SPECS=[('T2',(2,0,0,0,0)),('T4',(4,0,0,0,0)),('T8',(8,0,0,0,0)),
       ('C2',(0,2,0,0,0)),('C3',(0,3,0,0,0)),('S2',(0,0,2,0,0)),
       ('TC',(1,1,0,0,0)),('TS',(1,0,1,0,0)),('CS',(0,1,1,0,0)),
       ('RC',(0,1,0,1,0)),('RS',(0,0,1,1,0)),('R4',(0,0,0,4,0)),
       ('J2',(0,0,0,0,2)),('J3',(0,0,0,0,3)),('J4',(0,0,0,0,4)),
       ('JT2',(2,0,0,0,1)),('JTC',(1,1,0,0,1)),('JC2',(0,2,0,0,1)),
       ('JS',(0,0,1,0,1)),('JR2',(0,0,0,2,1)),('JTS',(1,0,1,0,1)),
       ('J2T2',(2,0,0,0,2)),('J2C2',(0,2,0,0,2)),
       ('J2R',(0,0,0,1,2)),('J3T',(1,0,0,0,3)),('J2S',(0,0,1,0,2))]


def save(name,value):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')


def power(p,n):
    out={ZERO:GQ(1)}
    for _ in range(n):out=poly.mul(out,p)
    return out


def candidates():
    data=json.loads(INPUT.read_text(encoding='utf-8'));_,_,G,_=base.target()
    factors=[old.decode(x['quotient_denominator'])for x in data['candidates']]
    factors += [{(0,2,0,0,0,0):GQ(1),(0,0,0,0,0,2):GQ(1)},poly.derivative(G,2)]
    for name,exponents in SPECS:
        E={ZERO:GQ(1)};K={ZERO:GQ(1)}
        for i,(factor,n)in enumerate(zip(factors,exponents)):
            E=poly.mul(E,power(factor,n))
            K=poly.mul(K,power(factor,n-(1 if i==4 and n else 0)))
        d=sum(n*w for n,w in zip(exponents,(1,3,6,2,3)))
        yield {'id':name,'factor_order':['T','C','S','R','J'],'exponents':list(exponents),
               'degree':d,'denominator':old.encode(E),'jacobian_cofactor':old.encode(K)if exponents[4]else None}


def reducer(G):
    z2=(0,0,2,0,0,0);assert G[z2]==1
    tail={m:-c for m,c in G.items()if m!=z2}
    assert all(m[2]<2 for m in tail)
    @lru_cache(maxsize=None)
    def monomial(m):
        if m[2]<2:return {m:Q(1)}
        out={};n=list(m);n[2]-=2
        for a,c in tail.items():
            out=poly.add(out,monomial(tuple(x+y for x,y in zip(a,n))),c)
        return out
    def reduce(p):
        out={}
        for m,c in p.items():out=poly.add(out,monomial(m),c)
        return out
    return reduce


def normal_columns(d,G):
    grad=[poly.derivative(G,i)for i in range(6)]
    for i,w in enumerate(W):
        for m in base.monomials(d+w-2):
            yield {'coordinate':i,'powers':list(m)},poly.mul({m:Q(1)},grad[i])


def koszul_columns(d,E,G,reduce):
    grad=[poly.derivative(G,i)for i in range(6)];ed=[poly.derivative(E,i)for i in range(6)]
    for i in range(6):
        for j in range(i+1,6):
            c=poly.add(poly.mul(grad[i],ed[j]),poly.mul(grad[j],ed[i]),-1)
            ei=poly.mul(E,grad[j]);ej=poly.mul(E,grad[i])
            for m in base.monomials(d+W[i]+W[j]-8):
                h={m:Q(1)}
                raw=poly.add(poly.mul(h,c),poly.mul(poly.derivative(h,i),ei))
                raw=poly.add(raw,poly.mul(poly.derivative(h,j),ej),-1)
                yield {'coordinates':[i,j],'powers':list(m)},reduce(raw)


def linear_system(iterator,rhs):
    equations={m:{}for m in rhs};labels=[]
    for col,(label,values)in enumerate(iterator):
        labels.append(label)
        for m,c in values.items():equations.setdefault(m,{})[col]=GQ.cast(c)
    return equations,labels


def eliminate(equations,rhs,ncols):
    rows=sorted(equations,key=lambda m:(len(equations[m]),not bool(rhs.get(m)),m))
    pivots={}
    for processed,m in enumerate(rows,1):
        vector=equations[m].copy();value=GQ.cast(rhs.get(m,0));track={m:GQ(1)}
        while vector:
            pivot=min(vector)
            if pivot not in pivots:
                c=vector[pivot];pivots[pivot]=(poly.scale(vector,1/c),value/c,poly.scale(track,1/c));break
            previous,previous_value,previous_track=pivots[pivot];c=vector[pivot]
            vector=poly.add(vector,previous,-c);value=value-c*previous_value;track=poly.add(track,previous_track,-c)
        if not vector and value:return poly.scale(track,1/value),None,len(pivots),processed
    solution=[GQ()for _ in range(ncols)]
    for pivot in sorted(pivots,reverse=True):
        vector,value,_=pivots[pivot]
        solution[pivot]=value-sum((c*solution[j]for j,c in vector.items()if j!=pivot),GQ())
    return None,solution,len(pivots),len(rows)


def check_dual(dual,columns,rhs):
    assert sum((c*rhs.get(m,0)for m,c in dual.items()),GQ())==1
    count=0
    for _,column in columns:
        assert not sum((c*column.get(m,0)for m,c in dual.items()),GQ());count+=1
    return count


def calculate(candidate,raw=False):
    started=time.perf_counter();_,_,G,beta=base.target();reduce=reducer(G)
    E=old.decode(candidate['denominator']);d=candidate['degree']
    assert E and all(sum(w*x for w,x in zip(W,m))==d for m in E)
    if candidate['exponents'][4] and not raw:
        columns,rhs,metadata=compact.system(candidate)
        equations,labels=linear_system(columns,rhs)
        prior=OUT/'J3.json'
        if candidate['id']=='J4'and prior.exists():
            previous=json.loads(prior.read_text(encoding='utf-8'))
            if previous['producer_sha256']==poly.sha(Path(__file__))and previous['status']=='excluded':
                dual=old.decode(previous['dual'])
                assert check_dual(dual,compact.system(candidate)[0],rhs)==len(labels)
                stages=[{'stage':'E2_reflection_compact','rows':len(equations),'columns':len(labels),'rows_processed':0,'rank_lower_bound':0}]
                item=packet(candidate,'E2_reflection_compact',dual,None,stages,started)
                item['compact_metadata']=metadata;item['reused_dual_packet']={'id':'J3','sha256':poly.sha(prior)}
                return item
        dual,solution,rank,processed=eliminate(equations,rhs,len(labels))
        stages=[{'stage':'E2_reflection_compact','rows':len(equations),'columns':len(labels),'rows_processed':processed,'rank_lower_bound':rank}]
        if dual is None:
            # Preserve a successful compact solve for full physical reconstruction.
            # Do not label this a certificate before that reconstruction is done.
            item=packet(candidate,'E2_reflection_compact',None,None,stages,started)
            item['status']='compact_solution_requires_lift';item['compact_solution']=[c.pair()for c in solution]
        else:
            assert check_dual(dual,compact.system(candidate)[0],rhs)==len(labels)
            item=packet(candidate,'E2_reflection_compact',dual,None,stages,started)
        item['compact_metadata']=metadata
        return item
    particular=[{}for _ in W];stages=[]
    if candidate['jacobian_cofactor'] is not None:
        K=old.decode(candidate['jacobian_cofactor']);particular[2]=poly.mul(beta,K)
        assert base.contraction(particular,G)==poly.mul(beta,E)
    else:
        rhs=poly.mul(beta,E);equations,labels=linear_system(normal_columns(d,G),rhs)
        dual,solution,rank,processed=eliminate(equations,rhs,len(labels))
        stages.append({'stage':'E1','rows':len(equations),'columns':len(labels),'rows_processed':processed,'rank_lower_bound':rank})
        if dual is not None:
            assert check_dual(dual,normal_columns(d,G),rhs)==len(labels)
            return packet(candidate,'E1',dual,None,stages,started)
        for c,label in zip(solution,labels):
            if c:particular[label['coordinate']][tuple(label['powers'])]=c
        assert base.contraction(particular,G)==rhs
        save('checkpoint-'+candidate['id']+'.json',{'status':'E1_satisfied_only','candidate':candidate,
             'particular':[old.encode(p)for p in particular],'scope':'E2 has not yet been established.'})
    rhs=reduce(poly.scale(base.B(E,particular),-1))
    if candidate['jacobian_cofactor'] is not None:assert rhs==reduce(poly.scale(poly.mul(beta,poly.mul(K,K)),2))
    equations,labels=linear_system(koszul_columns(d,E,G,reduce),rhs)
    dual,solution,rank,processed=eliminate(equations,rhs,len(labels))
    stages.append({'stage':'E2_mod_G','rows':len(equations),'columns':len(labels),'rows_processed':processed,'rank_lower_bound':rank})
    if dual is not None:
        assert check_dual(dual,koszul_columns(d,E,G,reduce),rhs)==len(labels)
        return packet(candidate,'E2_mod_G',dual,particular,stages,started)
    grad=[poly.derivative(G,i)for i in range(6)]
    for c,label in zip(solution,labels):
        if not c:continue
        i,j=label['coordinates'];h={tuple(label['powers']):c}
        particular[i]=poly.add(particular[i],poly.mul(h,grad[j]))
        particular[j]=poly.add(particular[j],poly.mul(h,grad[i]),-1)
    assert base.contraction(particular,G)==poly.mul(beta,E)and not reduce(base.B(E,particular))
    return packet(candidate,'E2_mod_G',None,particular,stages,started)


def packet(candidate,stage,dual,particular,stages,started):
    return {'schema':'cyclic-fano-branch-products-v1','instance':'cyclic-triple-fano','candidate':candidate,
            'producer_sha256':poly.sha(Path(__file__)),'dependencies':{s:poly.sha(ROOT/'experiments'/s)for s in DEPS},
            'candidate_input_sha256':poly.sha(INPUT),'source_instance_sha256':poly.sha(base.SOURCE/'source/instance.rec'),
            'status':'excluded'if dual is not None else 'exact_polynomial_witness','obstruction_stage':stage,
            'dual':old.encode(dual)if dual is not None else None,'particular':[old.encode(p)for p in particular]if particular is not None else None,
            'stages':stages,'full_numerator_dimension':sum(len(base.monomials(candidate['degree']+w-2))for w in W),
            'complete_Koszul_directions':sum(len(base.monomials(candidate['degree']+W[i]+W[j]-8))for i in range(6)for j in range(i+1,6)),
            'quotient_dimension_eliminated':len(base.monomials(2*candidate['degree']-8)),
            'exact_rank_claim':False,'seconds':time.perf_counter()-started,
            'scope':'Only the displayed fixed product. A timeout is unresolved; arbitrary powers, linear combinations and general supports remain outside this batch.'}


def verify():
    _,_,G,beta=base.target();checks=[];unresolved=[]
    specs=[(c,c['id'])for c in candidates()]
    specs += [(c,'raw-'+c['id'])for c in candidates()if (OUT/('attempt-raw-'+c['id']+'.json')).exists()]
    for candidate,name in specs:
        attempt=json.loads((OUT/('attempt-'+name+'.json')).read_text(encoding='utf-8'))
        assert attempt['candidate']==candidate and attempt['producer_sha256']==poly.sha(Path(__file__))
        if attempt['status']!='completed':
            assert attempt['status']in ('timeout','error');unresolved.append({'id':name,'status':attempt['status']});continue
        p=OUT/(name+'.json');item=json.loads(p.read_text(encoding='utf-8'))
        assert item['candidate']==candidate and item['producer_sha256']==poly.sha(Path(__file__))
        assert item['source_instance_sha256']==poly.sha(base.SOURCE/'source/instance.rec')and item['candidate_input_sha256']==poly.sha(INPUT)
        assert item['dependencies']=={s:poly.sha(ROOT/'experiments'/s)for s in DEPS}
        E=old.decode(candidate['denominator']);d=candidate['degree'];reduce=reducer(G)
        if item['obstruction_stage']=='E2_reflection_compact':
            _,rhs,metadata=compact.system(candidate);assert item['compact_metadata']==metadata
            columns=lambda:compact.system(candidate)[0]
        elif item['obstruction_stage']=='E1':
            rhs=poly.mul(beta,E);columns=lambda:normal_columns(d,G)
        else:
            field=[old.decode(p)for p in item['particular']];assert base.contraction(field,G)==poly.mul(beta,E)
            rhs=reduce(poly.scale(base.B(E,field),-1));columns=lambda:koszul_columns(d,E,G,reduce)
        if item['status']=='excluded':
            dual=old.decode(item['dual']);n=check_dual(dual,columns(),rhs)
            assert n==item['stages'][-1]['columns']
            bad=poly.scale(dual,2)
            assert sum((c*rhs.get(m,0)for m,c in bad.items()),GQ())!=1
        elif item['status']=='compact_solution_requires_lift':
            total={};cols=list(columns());assert len(cols)==len(item['compact_solution'])
            for c,(_,col)in zip(item['compact_solution'],cols):total=poly.add(total,col,GQ(*c))
            assert total==rhs;n=len(cols)
        else:
            assert item['status']=='exact_polynomial_witness'and not rhs;n=0
        checks.append({'id':name,'status':item['status'],'stage':item['obstruction_stage'],'packet_sha256':poly.sha(p),'columns_checked':n})
    receipt={'status':'PASS','checks':checks,'unresolved':unresolved,'source_instance_sha256':poly.sha(base.SOURCE/'source/instance.rec'),
             'producer_sha256':poly.sha(Path(__file__)),'certificate_found':any(c['status']=='exact_polynomial_witness'for c in checks)}
    save('validation.json',receipt);print(json.dumps(receipt))


def main():
    assert __debug__,'Run without -O'
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=('list','run','worker','verify'))
    parser.add_argument('--candidate');parser.add_argument('--seconds',type=int,default=120);parser.add_argument('--raw',action='store_true');args=parser.parse_args()
    if args.command=='list':print(json.dumps([{'id':c['id'],'degree':c['degree'],'exponents':c['exponents']}for c in candidates()]));return
    if args.command=='verify':verify();return
    candidate=next(c for c in candidates()if c['id']==args.candidate)
    name=('raw-'if args.raw else '')+candidate['id']
    if args.command=='worker':
        item=calculate(candidate,args.raw);save(name+'.json',item)
        print(json.dumps({'status':item['status'],'stage':item['obstruction_stage'],'dual_terms':len(item['dual']or []),'seconds':item['seconds']}));return
    started=time.perf_counter()
    try:
        command=[sys.executable,'-S',str(Path(__file__)),'worker','--candidate',candidate['id']]+(['--raw']if args.raw else [])
        run=subprocess.run(command,capture_output=True,text=True,timeout=args.seconds)
        receipt={'status':'completed'if run.returncode==0 else 'error','returncode':run.returncode,'stdout':run.stdout,'stderr':run.stderr}
    except subprocess.TimeoutExpired as e:
        receipt={'status':'timeout','stop_reason':'Worker wall-clock limit; no exclusion inferred.','stdout':(e.stdout or b'').decode()if isinstance(e.stdout,bytes)else e.stdout}
    receipt.update(candidate=candidate,time_limit_seconds=args.seconds,elapsed_seconds=time.perf_counter()-started,producer_sha256=poly.sha(Path(__file__)))
    save('attempt-'+name+'.json',receipt);print(json.dumps({k:v for k,v in receipt.items()if k!='candidate'},ensure_ascii=True))


if __name__=='__main__':main()

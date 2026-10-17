#!/usr/bin/env python3
"""Complete fixed-denominator tests guided by actual higher local jets.

Discovery and portable replay use exact Gaussian rational arithmetic. A local
branch approximation is only a heuristic global denominator, not a support.
Each candidate is run in a separate subprocess with a 120-second bound.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse
import copy
import json
import subprocess
import sys
import time
import cyclic_fano_transfer as base

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'results/cyclic-fano-higher-unfolding/candidates.json'
OUT=ROOT/'results/cyclic-fano-guided-denominators'
WEIGHTS=base.WEIGHTS


class GQ:
    __slots__=('re','im')
    def __init__(self,re=0,im=0):self.re,self.im=Q(re),Q(im)
    @staticmethod
    def cast(x):return x if isinstance(x,GQ)else GQ(x)
    def __add__(self,x):
        x=self.cast(x);return GQ(self.re+x.re,self.im+x.im)
    __radd__=__add__
    def __neg__(self):return GQ(-self.re,-self.im)
    def __sub__(self,x):return self+-self.cast(x)
    def __rsub__(self,x):return self.cast(x)+-self
    def __mul__(self,x):
        x=self.cast(x);return GQ(self.re*x.re-self.im*x.im,self.re*x.im+self.im*x.re)
    __rmul__=__mul__
    def __truediv__(self,x):
        x=self.cast(x);norm=x.re*x.re+x.im*x.im;assert norm
        return self*GQ(x.re/norm,-x.im/norm)
    def __rtruediv__(self,x):return self.cast(x)/self
    def __bool__(self):return bool(self.re or self.im)
    def __eq__(self,x):
        x=self.cast(x);return self.re==x.re and self.im==x.im
    def pair(self):return [str(self.re),str(self.im)]


def encode(a):return [{'powers':list(m),'coefficient':GQ.cast(c).pair()}for m,c in sorted(a.items(),reverse=True)]
def decode(a):return {tuple(t['powers']):GQ(*t['coefficient'])for t in a}
def save(name,value):
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/name).write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')


def candidates():
    packet=json.loads(INPUT.read_text(encoding='utf-8'))
    ans=list(packet['candidates'])
    # Rational norm of the full-target tangent covector Y2-iX1.
    norm={(0,2,0,0,0,0):GQ(1),(0,0,0,0,0,2):GQ(1)}
    power={(0,)*6:GQ(1)}
    for k in (1,2,3):
        power=base.poly.mul(power,norm)
        ans.append({'id':f'tangent_norm_power_{k}','degree':2*k,'quotient_denominator':encode(power),
                    'rationale':'Power of rational conjugate product of the actual full-target branch tangent Y2-iX1.',
                    'scope':'Fixed candidate only; local tangent data do not prove global support.'})
    _,_,G,_=base.target();Gz=base.poly.derivative(G,2)
    for name,factor in [('jacobian_tangent',ans[0]),('jacobian_center_cubic',ans[1]),('jacobian_tangent_norm',ans[3])]:
        product=base.poly.mul(Gz,decode(factor['quotient_denominator']))
        ans.append({'id':name,'degree':factor['degree']+3,'quotient_denominator':encode(product),
                    'parameterization':'complete_Koszul','jacobian_factor':factor['quotient_denominator'],
                    'rationale':'Multiply a branch-inspired factor by G_Z to satisfy E1 with P_Z=beta*factor; test all weighted Koszul corrections and quotients.',
                    'scope':'One fixed denominator only; the Jacobian multiplication is a candidate repair, not a global support theorem.'})
    assert len({a['id']for a in ans})==len(ans)
    return ans


def physical(candidate):
    F,A,G,beta=base.target();E=decode(candidate['quotient_denominator']);d=candidate['degree']
    assert E and 1<=d<=6 and all(sum(a*w for a,w in zip(m,WEIGHTS))==d for m in E)
    # F is smooth and geometrically irreducible. At degree6, its x2^6 term
    # rules out a scalar multiple of these denominators (Z degree at most1).
    assert d<6 or all(m[2]<2 for m in E)
    columns=[];labels=[]
    if candidate.get('parameterization')=='complete_Koszul':
        factor=decode(candidate['jacobian_factor']);particular=[{}for _ in WEIGHTS]
        particular[2]=base.poly.mul(beta,factor)
        assert base.contraction(particular,G)==base.poly.mul(beta,E)
        gradient=[base.poly.derivative(G,i)for i in range(6)]
        for i in range(6):
            for j in range(i+1,6):
                for mon in base.monomials(d+WEIGHTS[i]+WEIGHTS[j]-8):
                    field=[{}for _ in WEIGHTS]
                    field[i]=base.poly.mul({mon:Q(1)},gradient[j]);field[j]=base.poly.scale(base.poly.mul({mon:Q(1)},gradient[i]),-1)
                    assert not base.contraction(field,G)
                    columns.append({('E2',)+m:GQ.cast(c)for m,c in base.B(E,field).items()})
                    labels.append({'kind':'Koszul','coordinates':[i,j],'powers':list(mon)})
        rhs={('E2',)+m:GQ.cast(-c)for m,c in base.B(E,particular).items()}
    else:
        for i,w in enumerate(WEIGHTS):
            for mon in base.monomials(d+w-2):
                field=[{}for _ in WEIGHTS];field[i]={mon:GQ(1)}
                e1=base.contraction(field,G);e2=base.B(E,field)
                columns.append({**{('E1',)+m:GQ.cast(c)for m,c in e1.items()},
                                **{('E2',)+m:GQ.cast(c)for m,c in e2.items()}})
                labels.append({'kind':'numerator','coordinate':i,'powers':list(mon)})
        rhs={('E1',)+m:GQ.cast(c)for m,c in base.poly.mul(beta,E).items()}
    numerator_count=len(columns)
    # Full E2 quotient freedom, weight 2d-8; never force it to zero if allowed.
    for mon in base.monomials(2*d-8):
        columns.append({('E2',)+m:GQ.cast(-c)for m,c in base.poly.mul(G,{mon:Q(1)}).items()})
        labels.append({'kind':'G_quotient','powers':list(mon)})
    support=set(rhs).union(*(set(c)for c in columns))
    # Deterministic physical row order. Stop at the first exact contradiction;
    # no full matrix rank is claimed from this early stopping rule.
    rows=sorted(support)
    return E,rows,columns,labels,rhs,numerator_count


def first_dual(rows,columns,rhs):
    pivots={}
    for row,mon in enumerate(rows):
        vector={j:col[mon]for j,col in enumerate(columns)if mon in col}
        value=rhs.get(mon,GQ());tracking={row:GQ(1)}
        while vector:
            pivot=min(vector)
            if pivot not in pivots:
                coefficient=vector[pivot]
                vector=base.poly.scale(vector,1/coefficient);tracking=base.poly.scale(tracking,1/coefficient);value=value/coefficient
                pivots[pivot]=(vector,value,tracking);break
            old,oldvalue,oldtracking=pivots[pivot];coefficient=vector[pivot]
            vector=base.poly.add(vector,old,-coefficient);tracking=base.poly.add(tracking,oldtracking,-coefficient);value=value-coefficient*oldvalue
        if not vector and value:return base.poly.scale(tracking,1/value),len(pivots),row+1,None
    solution=[GQ()for _ in columns]
    for pivot in sorted(pivots,reverse=True):
        vector,value,_=pivots[pivot]
        solution[pivot]=value-sum((c*solution[j]for j,c in vector.items()if j!=pivot),GQ())
    return None,len(pivots),len(rows),solution


def check_dual(item,rows,columns,rhs):
    dual={rows[i]:GQ(*c)for i,c in item['obstruction_functional']}
    assert sum((c*rhs.get(m,GQ())for m,c in dual.items()),GQ())==1
    for column in columns:assert not sum((c*column.get(m,GQ())for m,c in dual.items()),GQ())


def calculate(candidate):
    start=time.perf_counter();E,rows,columns,labels,rhs,n=physical(candidate)
    dual,rank_lower_bound,processed,solution=first_dual(rows,columns,rhs)
    item={'schema':'cyclic-fano-guided-denominator-v1','candidate':candidate,
          'producer_sha256':base.poly.sha(Path(__file__)),'candidate_input_sha256':base.poly.sha(INPUT),
          'arithmetic_dependencies':{name:base.poly.sha(ROOT/'experiments'/name)for name in ('cyclic_fano_transfer.py','quadric_contact_pilot.py')},
          'source_instance_sha256':base.poly.sha(base.SOURCE/'source/instance.rec'),
          'matrix_shape':[len(rows),len(columns)],'numerator_parameterization':candidate.get('parameterization','full_coefficient_basis'),
          'numerator_parameters':n,'full_numerator_coefficients':sum(len(base.monomials(candidate['degree']+w-2))for w in WEIGHTS),
          'quotient_coefficients':len(columns)-n,
          'coefficient_rows':[list(r)for r in rows],'column_labels':labels,
          'obstruction_functional':[[i,GQ.cast(c).pair()]for i,c in sorted(dual.items())]if dual else None,
          'rows_processed':processed,'coefficient_rank_lower_bound':rank_lower_bound,
          'exact_rank_computed':dual is None,'status':'excluded'if dual else 'exact_polynomial_witness',
          'solution_coefficients':[c.pair()for c in solution]if solution is not None else None,
          'scope':'This fixed homogeneous invariant denominator only, with complete weighted numerator and allowed quotient freedom. No global support or arbitrary-degree exclusion.',
          'seconds':time.perf_counter()-start}
    if dual:check_dual(item,rows,columns,rhs)
    else:
        total={}
        for c,column in zip(solution,columns):total=base.poly.add(total,column,c)
        assert total==rhs
    return item


def verify():
    rejected=[];checks=[]
    for candidate in candidates():
        path=OUT/(candidate['id']+'.json')
        assert path.exists(),f'Missing candidate packet: {path.name}'
        item=json.loads(path.read_text(encoding='utf-8'));assert item['candidate']==candidate
        assert item['producer_sha256']==base.poly.sha(Path(__file__))and item['candidate_input_sha256']==base.poly.sha(INPUT)
        assert item['source_instance_sha256']==base.poly.sha(base.SOURCE/'source/instance.rec')
        for name,digest in item['arithmetic_dependencies'].items():assert digest==base.poly.sha(ROOT/'experiments'/name)
        E,rows,columns,labels,rhs,n=physical(candidate)
        assert item['coefficient_rows']==[list(r)for r in rows]and item['column_labels']==labels
        assert item['matrix_shape']==[len(rows),len(columns)]and item['numerator_parameters']==n
        assert item['numerator_parameterization']==candidate.get('parameterization','full_coefficient_basis')
        assert item['full_numerator_coefficients']==sum(len(base.monomials(candidate['degree']+w-2))for w in WEIGHTS)
        assert item['quotient_coefficients']==len(columns)-n
        if item['status']=='excluded':
            check_dual(item,rows,columns,rhs)
            bad=copy.deepcopy(item);bad['obstruction_functional'][0][1]=(GQ(*bad['obstruction_functional'][0][1])+1).pair()
            try:check_dual(bad,rows,columns,rhs)
            except AssertionError:rejected.append(candidate['id'])
            else:raise AssertionError('Changed dual accepted')
        else:
            assert item['status']=='exact_polynomial_witness'
            total={}
            for c,column in zip(item['solution_coefficients'],columns):total=base.poly.add(total,column,GQ(*c))
            assert len(item['solution_coefficients'])==len(columns)and total==rhs
        checks.append({'id':candidate['id'],'status':item['status'],'packet_sha256':base.poly.sha(path),
                       'shape':item['matrix_shape'],'quotient_coefficients':item['quotient_coefficients'],
                       'dual_terms':len(item['obstruction_functional']or [])})
    result={'status':'PASS','candidate_input_sha256':base.poly.sha(INPUT),'checks':checks,'mutations_rejected':rejected,
            'certificate_found':any(c['status']=='exact_polynomial_witness'for c in checks),'note':'Reconstruction and witness replay; stopped discovery does not claim exact full matrix ranks.'}
    save('validation.json',result);print(json.dumps(result))


def main():
    assert __debug__,'Run without -O'
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=['list','run','worker','verify']);parser.add_argument('--candidate');args=parser.parse_args()
    if args.command=='list':print(json.dumps([{'id':a['id'],'degree':a['degree']}for a in candidates()]));return
    if args.command=='verify':verify();return
    candidate=next(c for c in candidates()if c['id']==args.candidate)
    if args.command=='worker':
        packet=calculate(candidate);save(candidate['id']+'.json',packet)
        print(json.dumps({'status':packet['status'],'shape':packet['matrix_shape'],'dual_terms':len(packet['obstruction_functional']or[]),'seconds':packet['seconds']}));return
    start=time.perf_counter()
    try:
        run=subprocess.run([sys.executable,'-S',str(Path(__file__)),'worker','--candidate',candidate['id']],capture_output=True,text=True,timeout=120)
        result={'status':'completed'if run.returncode==0 else 'error','returncode':run.returncode,'stdout':run.stdout,'stderr':run.stderr}
    except subprocess.TimeoutExpired:result={'status':'timeout','stop_reason':'120-second wall-clock limit; no exclusion inferred'}
    result.update(candidate=candidate['id'],time_limit_seconds=120,elapsed_seconds=time.perf_counter()-start)
    save('attempt-'+candidate['id']+'.json',result);print(json.dumps(result))


if __name__=='__main__':main()

"""Bounded exact search of four-component fields N/D on the skew quotient."""
from pathlib import Path
import argparse
import hashlib
import itertools
import json
import re
import time
import sympy as s
from flint import fmpq
from check_chi_target_source import arithmetic

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/skew-base-derivatives'
VARS=s.symbols('U r w t')


def source():
    pins=json.loads((OUT/'inputs.json').read_text(encoding='utf-8'))
    for item in pins['local_inputs']:
        if hashlib.sha256((ROOT/item['path']).read_bytes()).hexdigest()!=item['sha256']:
            raise ValueError('Reused input hash mismatch: '+item['path'])
    raw=(ROOT/'results/chi-target-source/inputs/data/one-reflection-skew/instance.rec').read_text(encoding='utf-8')
    def field(label):
        match=re.search(r'^'+label+r': (.*(?:\n  [^\n]+)*)',raw,re.M)
        if match is None:raise ValueError('Missing source '+label)
        return ' '.join(match.group(1).splitlines())
    X=s.symbols('X0 X1 X2 Y0 Y1 Y2');x,z=s.symbols('x z')
    U,r,w,t=VARS
    F=arithmetic(field('F'),dict(zip(map(str,X),X)))
    A=arithmetic(field('A'),dict(zip(map(str,X),X)))
    mapping=dict(zip(X,(x,r*x,w*x,1,t,z)))
    if int(field('q'))!=1 or s.expand(A.subs(mapping,simultaneous=True)-x**3)!=0:
        raise ValueError('Protected source changed')
    terms=s.Poly(s.expand(F.subs(mapping,simultaneous=True)-z**6),x).terms()
    if any(e[0]%2 for e,_ in terms):raise ValueError('Square quotient unavailable')
    return s.Poly(sum(co*U**(e[0]//2) for e,co in terms),*VARS)


def denominator(label,P):
    U,r,w,t=VARS
    return {'1':s.Integer(1),'r':r,'t':t,'a':s.Poly(P.as_expr(),U).coeff_monomial(U**3)}[label]


def monomials(bound):
    return sorted((m for m in itertools.product(range(bound+1),repeat=4) if sum(m)<=bound),key=lambda m:(sum(m),m))


def integer_terms(expr):
    poly=s.Poly(expr,*VARS)
    if any(not c.is_Integer for c in poly.coeffs()):raise ValueError('Expected integral operator')
    return {tuple(e):int(c) for e,c in poly.terms()}


def build(P,D,bound):
    # Scale the rational equation by 84: 7 clears P, 12 clears source 5/12.
    p7=7*P.as_expr()
    T=[integer_terms(12*(5*D*s.diff(p7,v)+6*p7*s.diff(D,v))) for v in VARS]
    S=integer_terms(-72*p7*D)
    rhs=integer_terms(35*VARS[0]**2*D**2)
    columns=[];labels=[]
    for j in range(4):
        for m in monomials(bound):
            col={}
            for e,c in T[j].items():
                k=tuple(e[i]+m[i] for i in range(4));col[k]=col.get(k,0)+c
            if m[j]:
                for e,c in S.items():
                    k=tuple(e[i]+m[i]-(i==j) for i in range(4));col[k]=col.get(k,0)+c*m[j]
            columns.append({k:v for k,v in col.items() if v})
            labels.append((j,m))
    return columns,rhs,labels


def eliminate(columns,rhs,deadline):
    exponents=sorted(set(rhs).union(*(set(c) for c in columns)))
    rows={e:{} for e in exponents};n=len(columns)
    for j,col in enumerate(columns):
        for e,c in col.items():rows[e][j]=fmpq(c)
    ordering=sorted(exponents,key=lambda e:(len(rows[e]),sum(e),e))
    basis={}
    def subtract(target,other,factor):
        for key,val in other.items():
            new=target.get(key,fmpq(0))-factor*val
            if new:target[key]=new
            elif key in target:del target[key]
    for e in ordering:
        if time.monotonic()>deadline:raise TimeoutError('Per-worker 90-second computation budget exceeded')
        row=dict(rows[e]);row[n]=fmpq(rhs.get(e,0))
        if not row[n]:del row[n]
        witness={e:fmpq(1)}
        while row:
            pivot=min(row)
            if pivot==n:
                scale=row[n]
                dual={k:v/scale for k,v in witness.items() if v}
                if any(sum(dual.get(k,fmpq(0))*v for k,v in col.items()) for col in columns):
                    raise ValueError('Constructed dual does not annihilate full matrix')
                if sum(dual.get(k,fmpq(0))*v for k,v in rhs.items())!=1:
                    raise ValueError('Constructed dual does not separate RHS')
                return {'outcome':'excluded_in_tested_family','rows':len(exponents),'columns':n,
                        'pivots_before_contradiction_not_total_rank':len(basis),
                        'dual':[{'exponent':list(k),'coefficient':str(v)} for k,v in sorted(dual.items())]}
            if pivot not in basis:
                scale=row[pivot]
                basis[pivot]=({k:v/scale for k,v in row.items()},{k:v/scale for k,v in witness.items()})
                break
            factor=row[pivot]
            subtract(row,basis[pivot][0],factor)
            subtract(witness,basis[pivot][1],factor)
    answer={}
    for pivot,(row,_) in sorted(basis.items(),reverse=True):
        answer[pivot]=row.get(n,fmpq(0))-sum(v*answer.get(k,fmpq(0)) for k,v in row.items() if k!=n and k!=pivot)
    if any(sum(answer.get(j,fmpq(0))*col.get(e,0) for j,col in enumerate(columns))!=rhs.get(e,0) for e in exponents):
        raise ValueError('Candidate does not solve full system')
    return {'outcome':'candidate_found','rows':len(exponents),'columns':n,'coefficients':{str(j):str(v) for j,v in answer.items() if v}}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--denominator',choices=['1','r','t','a'],required=True)
    args=parser.parse_args();started=time.monotonic();deadline=started+90
    P=source();D=denominator(args.denominator,P)
    for bound in [0,2,4]:
        t0=time.monotonic();columns,rhs,labels=build(P,D,bound)
        result=eliminate(columns,rhs,deadline)
        result.update({'denominator_label':args.denominator,'denominator':str(D),'denominator_power':1,
            'numerator_total_degree_bound':bound,'variables':list(map(str,VARS)),
            'component_order':['U','r','w','t'],'monomial_order':'total degree, then lexicographic exponent tuple',
            'P':str(P.as_expr()),'operator_scale':84,'scaled_rhs':'35*U^2*D^2',
            'scope':'All four numerator components and every monomial of total degree at most the bound; fixed D only',
            'seconds':round(time.monotonic()-t0,6),'search_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})
        path=OUT/f'search-{args.denominator}-degree{bound}.json'
        path.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
        print(json.dumps({k:result[k] for k in ['denominator_label','numerator_total_degree_bound','outcome','rows','columns','seconds']}),flush=True)


if __name__=='__main__':main()

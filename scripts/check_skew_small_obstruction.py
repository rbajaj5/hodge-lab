#!/usr/bin/env python3
"""Independent exact sparse transpose audit; no imported search/operator code.

Each dictionary is a polynomial in U,r,w,t.  For the first-order operator,
coefficient extraction transposes finite supports exactly; this both checks
all degree-four columns and exhibits the first degree where this dual fails.
"""
from fractions import Fraction as Q
from itertools import product
from pathlib import Path
import json
import platform
import time

START = time.perf_counter()
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results' / 'skew-small-obstruction'
OUT.mkdir(parents=True, exist_ok=True)
VARS = ('U','r','w','t')
ZERO = (0,0,0,0)

def add(*ps):
    out = {}
    for p in ps:
        for k,v in p.items():
            out[k] = out.get(k,0)+v
    return {k:v for k,v in out.items() if v}

def scale(p,c):
    return {k:c*v for k,v in p.items() if c*v}

def mul(p,q):
    out={}
    for a,c in p.items():
        for b,d in q.items():
            k=tuple(x+y for x,y in zip(a,b))
            out[k]=out.get(k,0)+c*d
    return {k:v for k,v in out.items() if v}

def diff(p,j):
    out={}
    for a,c in p.items():
        if a[j]:
            b=list(a);b[j]-=1
            out[tuple(b)]=a[j]*c
    return out

def shift(p,e):
    return {tuple(a+b for a,b in zip(k,e)):v for k,v in p.items()}

# P7 is reconstructed directly from the protected sextic chart formula.
a={ZERO:1,(0,6,0,0):1,(0,0,6,0):1}
P7={
    (3,0,0,0):7,(3,6,0,0):7,(3,0,6,0):7,
    (2,1,0,1):7,(2,3,1,1):7,
    (1,1,0,1):1,(1,1,0,3):-1,
    ZERO:7,(0,0,0,6):7,
}
B=scale(mul(P7,a),-72)
A=[add(scale(mul(a,diff(P7,j)),60),scale(mul(P7,diff(a,j)),72)) for j in range(4)]
targets=((0,1,0,3),(2,0,12,0),(2,0,12,2))
weights=(Q(3,5),Q(1,35),Q(-1,35))

def transpose(target,j):
    out={}
    for k,v in A[j].items():
        e=tuple(x-y for x,y in zip(target,k))
        if min(e)>=0: out[e]=out.get(e,0)+v
    for k,v in B.items():
        e=list(x-y for x,y in zip(target,k));e[j]+=1;e=tuple(e)
        if min(e)>=0 and e[j]>0: out[e]=out.get(e,0)+v*e[j]
    return {e:v for e,v in out.items() if v}

transposes=[[transpose(T,j) for j in range(4)] for T in targets]
duals=[add(*(scale(transposes[k][j],weights[k]) for k in range(3))) for j in range(4)]
requirements=[]
def require(label,value):
    if not value: raise RuntimeError(label)
    requirements.append(label)

expected=[
    [{ZERO:-60,(0,0,0,2):60},{},{},{}],
    [{ZERO:1260},{},{},{}],
    [{(0,0,0,2):1260},{},{},{}],
]
for k,T in enumerate(targets):
    for j in range(4):
        require(f'transpose_formula_{k}_{j}',{e:v for e,v in transposes[k][j].items() if sum(e)<=4}==expected[k][j])

# Independently apply the forward operator to all 280 monomial columns,
# rather than relying solely on its sparse transpose.
monomials=[e for e in product(range(5),repeat=4) if sum(e)<=4]
column_count=0
for j in range(4):
    for e in monomials:
        out=shift(A[j],e)
        if e[j]:
            em=list(e);em[j]-=1
            out=add(out,scale(shift(B,tuple(em)),e[j]))
        pairing=sum(c*out.get(T,0) for c,T in zip(weights,targets))
        require(f'column_{j}_{e}',pairing==0)
        column_count+=1
require('280_columns',column_count==280)
rhs=scale(shift(mul(a,a),(2,0,0,0)),35)
require('rhs_coefficients',[rhs.get(T,0) for T in targets]==[0,35,0])
require('rhs_pairing',sum(c*rhs.get(T,0) for c,T in zip(weights,targets))==1)

nonzero=[(sum(e),j,e,v) for j,p in enumerate(duals) for e,v in p.items()]
min_degree=min(k[0] for k in nonzero)
require('first_failure_degree_5',min_degree==5)
first=sorted(k for k in nonzero if k[0]==min_degree)

# A degree-five field satisfies these three selected equations, but fails
# the full equation. This demonstrates the limitation constructively.
sample_N=[{ZERO:Q(1,36)},{(0,2,0,3):Q(-5,3024)},{},{}]
sample_out={}
for j,n in enumerate(sample_N):
    sample_out=add(sample_out,mul(A[j],n),mul(B,diff(n,j)))
require('degree5_selected_rows_satisfiable',all(sample_out.get(T,0)==rhs.get(T,0) for T in targets))
sample_residual=add(sample_out,scale(rhs,-1))
require('degree5_sample_not_primitive',sample_residual.get((0,1,0,1),0)==Q(5,3))

# Deliberate-error control: remove the denominator derivative.  This dual
# happens still to annihilate degree-four columns, so explicitly report that
# this particular tiny certificate cannot by itself test that implementation
# error.  The original broader checkpoint provides that separate control.
A_no_denom=[scale(mul(a,diff(P7,j)),60) for j in range(4)]
mutant_pairings=[]
for j in range(4):
    for e in monomials:
        out=shift(A_no_denom[j],e)
        if e[j]:
            em=list(e);em[j]-=1
            out=add(out,scale(shift(B,tuple(em)),e[j]))
        pairing=sum(c*out.get(T,0) for c,T in zip(weights,targets))
        if pairing: mutant_pairings.append((j,e,str(pairing)))

# An actually sensitive control: omit the first dual term, which must fail
# already on constant N_U.
bad=sum(c*A[0].get(T,0) for c,T in zip((Q(0),Q(1,35),Q(-1,35)),targets))
require('missing_dual_term_detected',bad==36)

def rows(p):
    return [{'exponents':list(e),'coefficient':str(v),'degree':sum(e)} for e,v in sorted(p.items(),key=lambda k:(sum(k[0]),k[0]))]

report={
 'purpose':'Independent three-coefficient dual and its exact degree frontier',
 'coordinate_order':list(VARS),
 'operator':'60*a*grad(P7).N -72*P7*a*div(N)+72*P7*N.grad(a)',
 'columns_checked':column_count,
 'requirements_passed':len(requirements),
 'selected_targets':[list(t) for t in targets],
 'dual_weights':[str(c) for c in weights],
 'rhs_selected_coefficients':[rhs.get(T,0) for T in targets],
 'rhs_pairing':'1',
 'full_selected_coefficient_maps':[[rows(p) for p in row] for row in transposes],
 'full_dual_support':[{'component':VARS[j],'coefficients':rows(p)} for j,p in enumerate(duals)],
 'earliest_failure_degree':min_degree,
 'earliest_failure_columns':[{'component':VARS[j],'exponents':list(e),'pairing':str(v)} for d,j,e,v in first],
 'degree5_selected_only_solution':[rows(n) for n in sample_N],
 'degree5_selected_only_residual_rt':'5/3',
 'mutation_omit_first_dual_term_on_constant_NU':str(bad),
 'mutation_omit_denominator_derivative_nonzero_pairings':mutant_pairings,
 'limits':['No source/residue or covariant-jet replay','No claim of solvability at degree five','No full degree-five matrix elimination','No identification with companion ansatz'],
 'python':platform.python_version(),
 'elapsed_seconds':time.perf_counter()-START,
}
path=OUT/'three-coefficient-replay.json'
path.write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
print(json.dumps({k:report[k] for k in ['columns_checked','requirements_passed','rhs_pairing','earliest_failure_degree','earliest_failure_columns','mutation_omit_first_dual_term_on_constant_NU','mutation_omit_denominator_derivative_nonzero_pairings','elapsed_seconds']},indent=2))

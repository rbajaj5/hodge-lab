#!/usr/bin/env python3
"""Finite modular screen of polynomial coefficients in the rank-2 PDE.

This is a bounded screen only.  When augmented rank exceeds the number of
unknowns, its nonzero modular minor is also a characteristic-zero obstruction
to that exact ansatz.  No result here is an unrestricted obstruction.
"""
import argparse, hashlib, json, math, time
from pathlib import Path
import sympy as S
from flint import nmod_mat

parser=argparse.ArgumentParser()
parser.add_argument('--degree',type=int,default=4)
parser.add_argument('--prime',type=int,default=1000003)
parser.add_argument('--denominator',choices=['1','a','Delta'],default='1')
parser.add_argument('--chart',choices=['Y1','Y0'],default='Y1')
args=parser.parse_args()
ROOT=Path(__file__).resolve().parent
data=json.loads((ROOT/'rank2_primitive_system.json').read_text())
a,b,c,d,r,w,alpha=S.symbols('a b c d r w alpha')
loc={str(x):x for x in [a,b,c,d,r,w,alpha]}
Delta=S.sympify(data['Delta'],locals=loc)
physical={S.sympify(k,locals=loc):S.sympify(v,locals=loc) for k,v in data['physical_coefficients'].items()}
M={S.sympify(k,locals=loc):S.Matrix([[S.sympify(q,locals=loc) for q in row] for row in mat]) for k,mat in data['connection'].items()}
g=S.Matrix([[S.sympify(q,locals=loc) for q in row] for row in data['physical_source']])
if args.chart == 'Y0':
    physical[c] = r*alpha*(1-alpha**2)/7
    target_c=S.Matrix([[S.sympify(q,locals=loc) for q in row] for row in data['target_reduction_c']])
    g=S.Rational(5,72)*target_c
variables=[r,w,alpha]
L=504*a*Delta
Lphysical=S.Poly(S.expand(L.subs(physical)),*variables,domain=S.QQ)
N=[]
for t in variables:
    mt=sum((S.diff(physical[p],t)*M[p] for p in [a,b,c,d]),S.zeros(2))
    N.append((L*mt).applyfunc(S.cancel).subs(physical).applyfunc(S.expand))
G=(L*g).applyfunc(S.cancel).subs(physical).applyfunc(S.expand)

# For f=H/B, multiply the system by B^2: L B partial H +
# (B N - L partial B)H = B^2 G.  B=1 is the polynomial screen.
B={'1':S.Integer(1),'a':physical[a],'Delta':Delta.subs(physical)}[args.denominator]
Lnew=S.expand(Lphysical.as_expr()*B)
Nnew=[S.expand(B)*nt-S.eye(2)*S.expand(Lphysical.as_expr()*S.diff(B,t)) for t,nt in zip(variables,N)]
Gnew=(B*B*G).applyfunc(S.expand)
polys=[S.Poly(Lnew,*variables,domain=S.QQ)]
polys += [S.Poly(S.expand(mt[i,j]),*variables,domain=S.QQ) for mt in Nnew for i in range(2) for j in range(2)]
polys += [S.Poly(Gnew[i],*variables,domain=S.QQ) for i in range(2)]
scale=S.ilcm(*[q.q for p in polys for q in p.coeffs()])
dicts=[{mon:int(coef*scale) for mon,coef in p.terms()} for p in polys]
ld=dicts[0]
nd=[[[dicts[1+4*t+2*i+j] for j in range(2)] for i in range(2)] for t in range(3)]
gd=dicts[-2:]

monomials=[(i,j,k) for total in range(args.degree+1) for i in range(total+1) for j in range(total-i+1) for k in [total-i-j]]
column_labels=[];columns=[]
for direction in range(3):
    for component in range(2):
        for mon in monomials:
            col={}
            for out_component in range(2):
                for q,coef in nd[direction][out_component][component].items():
                    label=(out_component,)+tuple(q[k]+mon[k] for k in range(3))
                    col[label]=col.get(label,0)+coef
            if mon[direction]:
                shifted=tuple(mon[k]-(k==direction) for k in range(3))
                for q,coef in ld.items():
                    label=(component,)+tuple(q[k]+shifted[k] for k in range(3))
                    col[label]=col.get(label,0)+mon[direction]*coef
            columns.append({k:v for k,v in col.items() if v})
            column_labels.append((str(variables[direction]),component,mon))
rhs={(i,)+mon:coef for i in range(2) for mon,coef in gd[i].items() if coef}
row_labels=sorted(set(rhs).union(*(set(col) for col in columns)))
row_index={label:i for i,label in enumerate(row_labels)}
nr,nc=len(row_labels),len(columns)
entries=[0]*(nr*(nc+1))
for j,col in enumerate(columns):
    for label,coef in col.items():entries[row_index[label]*(nc+1)+j]=coef%args.prime
for label,coef in rhs.items():entries[row_index[label]*(nc+1)+nc]=coef%args.prime
started=time.monotonic()
mat=nmod_mat(nr,nc+1,entries,args.prime)
rref,rank=mat.rref()
inconsistent=any(all(not rref[i,j] for j in range(nc)) and rref[i,nc] for i in range(rank))
result={
    'chart':args.chart,'degree':args.degree,'denominator':args.denominator,'prime':args.prime,
    'rows':nr,'unknowns':nc,'augmented_rank':rank,
    'coefficient_rank':rank-int(inconsistent),'consistent_mod_prime':not inconsistent,
    'exact_bounded_characteristic_zero_obstruction':rank>nc,
    'seconds_for_rref':round(time.monotonic()-started,6),
    'integer_common_scale':str(scale),
    'status':('exact bounded ansatz obstruction from augmented modular rank > unknown count; no unrestricted claim'
              if rank>nc else 'modular bounded screen only; no unrestricted claim'),
    'connection_data_sha256':hashlib.sha256((ROOT/'rank2_primitive_system.json').read_bytes()).hexdigest(),
}
if not inconsistent:
    pivotcols=[]
    for i in range(rank):
        pivot=next(j for j in range(nc) if rref[i,j])
        pivotcols.append(pivot)
    solution=[0]*nc
    for i,j in enumerate(pivotcols):solution[j]=int(rref[i,nc])
    result['one_modular_solution']=[{'label':column_labels[j],'coefficient':v} for j,v in enumerate(solution) if v]
outfile=ROOT/f'rank2_screen_{args.chart}_deg{args.degree}_{args.denominator}_p{args.prime}.json'
outfile.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))

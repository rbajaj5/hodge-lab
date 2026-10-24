#!/usr/bin/env python3
"""Search the exact physical rank-two compact equation with flux P/a.

This extends the published degree-six numerator screen. It retains both
rows and all three physical derivatives, with the simultaneous-sign
character forced by the invariant source. A modular failure is only a
search result unless full coefficient-column rank is certified.
"""
import json, random, time
from pathlib import Path
import sympy as sp
from flint import nmod_mat

HERE=Path(__file__).resolve().parent
SRC=HERE/'inputs/source-rank2-connection.json'
raw=json.loads(SRC.read_text())
aa,bb,cc,dd=sp.symbols('a b c d')
r,w,t=sp.symbols('r w t')
vars_=(r,w,t)
local={'a':aa,'b':bb,'c':cc,'d':dd}
Delta=27*aa**2*dd**2-18*aa*bb*cc*dd+4*aa*cc**3+4*bb**3*dd-bb**2*cc**2
M={v:sp.Matrix([[sp.sympify(q,locals=local) for q in row]
               for row in raw['connection'][str(v)]]) for v in (aa,bb,cc,dd)}
phys={aa:1+r**6+w**6,bb:t*(r+r**3*w),cc:r*t*(1-t**2)/7,dd:1+t**6}
pd=sp.Poly(sp.expand(Delta.subs(phys)),*vars_,domain=sp.QQ)
ad=sp.Poly(sp.expand(phys[aa]*pd.as_expr()),*vars_,domain=sp.QQ)
base_matrices={v:(aa*Delta*M[v]).applyfunc(sp.cancel) for v in (aa,bb,cc,dd)}
Bs=[]
for x in vars_:
    b=sum((base_matrices[v].subs(phys)*sp.diff(phys[v],x)
           for v in (aa,bb,cc,dd)),sp.zeros(2))-sp.eye(2)*sp.diff(phys[aa],x)*pd.as_expr()
    Bs.append([[sp.Poly(sp.expand(b[i,j]),*vars_,domain=sp.QQ) for j in range(2)] for i in range(2)])
rhs=[sp.Poly(sp.expand(sp.cancel(aa**2*Delta*M[bb][i,0]/12).subs(phys)),*vars_,domain=sp.QQ) for i in range(2)]

def modular_poly(poly,prime):
    return [(mon,int(c.p)%prime*pow(int(c.q),-1,prime)%prime) for mon,c in poly.terms()]

def evaluate(poly,powers,prime):
    return sum(c*powers[0][mon[0]]*powers[1][mon[1]]*powers[2][mon[2]] for mon,c in poly)%prime

def monomials(degree):
    for n in range(degree+1):
        for i in range(n+1):
            for j in range(n-i+1):
                yield (i,j,n-i-j)

def run(degree,prime=32003,seed=7149):
    # Flux r,t must be odd under (r,t)->(-r,-t); flux w even.
    basis=[(v,j,m) for v in range(3) for j in range(2) for m in monomials(degree)
           if (m[0]+m[2])%2==(v!=1)]
    n=len(basis);points=(n+1)//2+25
    max_power=max([degree]+[sum(mon) for p in [ad,pd,*rhs] for mon,_ in p.terms()]
                  +[sum(mon) for b in Bs for row in b for p in row for mon,_ in p.terms()])
    adp=modular_poly(ad,prime)
    bp=[[[modular_poly(p,prime) for p in row] for row in b] for b in Bs]
    rp=[modular_poly(p,prime) for p in rhs]
    rng=random.Random(seed);rows=[]
    for _ in range(points):
        point=[rng.randrange(1,prime) for _ in range(3)]
        powers=[]
        for x in point:
            powers.append([pow(x,k,prime) for k in range(max_power+1)])
        av=evaluate(adp,powers,prime)
        bv=[[[evaluate(p,powers,prime) for p in row] for row in b] for b in bp]
        rv=[evaluate(p,powers,prime) for p in rp]
        rr=[[],[]]
        for v,j,m in basis:
            mon=powers[0][m[0]]*powers[1][m[1]]*powers[2][m[2]]%prime
            derivative=(m[v]*mon*pow(point[v],-1,prime))%prime
            for i in range(2):
                rr[i].append((bv[v][i][j]*mon+(av*derivative if i==j else 0))%prime)
        for i in range(2):rows.append(rr[i]+[rv[i]])
    start=time.time()
    coeff=nmod_mat([q[:-1] for q in rows],prime)
    aug=nmod_mat(rows,prime)
    rank=coeff.rank();arank=aug.rank()
    result={'degree':degree,'prime':prime,'columns':n,'sample_rows':len(rows),
            'rank':rank,'augmented_rank':arank,'rank_seconds':time.time()-start,
            'full_column_rank':rank==n,
            'interpretation':'complete bounded characteristic-zero exclusion' if rank==n and arank>rank else 'modular search only'}
    if rank<n:
        ns,nullity=coeff.nullspace()
        result['nullity']=nullity
        result['nullspace']=[[
            {'flux':vars_[v].name,'row':j,'exponent':list(m),'coefficient_mod_p':int(ns[k,h])}
            for k,(v,j,m) in enumerate(basis) if ns[k,h]] for h in range(nullity)]
        print('Nullspace support sizes:',[len(q) for q in result['nullspace']],flush=True)
    print(json.dumps(result),flush=True)
    return result

if __name__=='__main__':
    import sys
    degree=int(sys.argv[1]) if len(sys.argv)>1 else 9
    out=run(degree)
    (HERE/('a_denominator_degree'+str(degree)+'.json')).write_text(json.dumps(out,indent=2)+'\n')

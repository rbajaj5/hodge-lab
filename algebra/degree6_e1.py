"""Independent complete degree-six E1 reproduction for sextics/holdout.

Reference: https://github.com/hodge-computer/sextics/discussions/44,
fqlx's exact degree-six calculation, retrieved 2026-10-16. Its published
109-dimensional denominator space is prior work, not a new result here.
This runner independently assembles every monomial column over two finite
fields and Q, verifies every rational lift and every quadratic Koszul
generator, exports the complete denominator/lift basis, and locates F in it.
E1 solutions alone are not certificates. Denominators proportional to F
are inadmissible. No parity or denominator ansatz is imposed.

Run: python algebra/degree6_e1.py
Only Python standard-library modules are required.
"""
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import hashlib
import json
import time

OUT=Path(__file__).resolve().parent
VARS=['X0','X1','X2','Y0','Y1','Y2']
F={(6,0,0,0,0,0):1,(3,1,0,1,1,0):1,(0,6,0,0,0,0):1,
   (0,3,1,0,1,1):1,(0,0,6,0,0,0):1,(0,0,0,6,0,0):1,
   (0,0,0,0,6,0):1,(0,0,0,0,0,6):1}
A={(3,0,0,3,0,0):1}

def mons(d,n=6):
    if n==1:yield (d,)
    else:
        for a in range(d,-1,-1):
            for tail in mons(d-a,n-1):yield(a,)+tail
def expadd(a,b):return tuple(x+y for x,y in zip(a,b))
def diff(p,i):return {u[:i]+(u[i]-1,)+u[i+1:]:c*u[i] for u,c in p.items() if u[i]}
def padd(a,b,scale=1):
    o=dict(a)
    for k,v in b.items():
        z=o.get(k,0)+scale*v
        if z:o[k]=z
        elif k in o:del o[k]
    return o
def pmul(a,b):
    o={}
    for u,c in a.items():
        for v,d in b.items():
            w=expadd(u,v);o[w]=o.get(w,0)+c*d
    return {k:v for k,v in o.items() if v}
DF=[diff(F,i) for i in range(6)]

class Elimination:
    def __init__(self,prime=None):self.p=prime;self.basis={};self.operations=0
    def insert(self,v,comb=None):
        p=self.p
        while v:
            k=min(v);c=v[k]
            if k not in self.basis:
                inv=pow(c,-1,p) if p else Fraction(1,c)
                normal={i:e*inv%p if p else e*inv for i,e in v.items()}
                track=None if comb is None else {i:e*inv%p if p else e*inv for i,e in comb.items()}
                self.basis[k]=(normal,track)
                return None
            other,track=self.basis[k]
            for i,e in other.items():
                z=v.get(i,0)-c*e
                if p:z%=p
                if z:v[i]=z
                elif i in v:del v[i]
            if comb is not None:
                for i,e in track.items():
                    z=comb.get(i,0)-c*e
                    if p:z%=p
                    if z:comb[i]=z
                    elif i in comb:del comb[i]
            self.operations+=1
        return {} if comb is None else comb

def poly_json(poly):return [[str(c),list(u)] for u,c in sorted(poly.items(),reverse=True)]
def rational_run(prime=None):
    started=time.perf_counter();rows={m:i for i,m in enumerate(mons(12))};m7=list(mons(7));m6=list(mons(6))
    e=Elimination(prime);labels=[];nullN=0
    for i in range(6):
        for u in m7:
            col={rows[expadd(u,v)]:c for v,c in DF[i].items()};idx=len(labels);labels.append(('N',i,u))
            null=e.insert(col,{idx:1})
            if null is not None:nullN+=1
    rankN=len(e.basis);pairs=[];jacobian_basis=e.basis.copy()
    for u in m6:
        col={rows[expadd(u,v)]:c for v,c in A.items()};idx=len(labels);labels.append(('D',u))
        null=e.insert(col,{idx:1})
        if null is not None:
            D={};N=[{} for _ in range(6)]
            for j,c in null.items():
                label=labels[j]
                if label[0]=='D':D[label[1]]=c
                else:N[label[1]][label[2]]=(-c)%prime if prime else -c
            pairs.append((D,N))
    checks=[]
    for D,N in pairs:
        directional={}
        for i in range(6):directional=padd(directional,pmul(N[i],DF[i]))
        residual=padd(directional,pmul(A,D),-1)
        if prime:residual={k:v%prime for k,v in residual.items() if v%prime}
        checks.append(not residual)
    assert all(checks)
    # Independent verification of the entire numerator kernel, rather than
    # assuming smoothness/regularity for the dimension assertion.
    kspan=Elimination(prime);idx7={u:i for i,u in enumerate(m7)}
    for i,j in combinations(range(6),2):
        for u in mons(2):
            K=[{} for _ in range(6)];K[i]=pmul({u:1},DF[j]);K[j]={v:-c for v,c in pmul({u:1},DF[i]).items()}
            assert not padd(pmul(K[i],DF[i]),pmul(K[j],DF[j]))
            col={component*len(m7)+idx7[v]:(c%prime if prime else c) for component in (i,j) for v,c in K[component].items()}
            kspan.insert(col)
    assert len(kspan.basis)==nullN
    # Express the forbidden F direction in the full denominator space.
    dspan=Elimination(prime);rows6={u:i for i,u in enumerate(m6)}
    for j,(D,N) in enumerate(pairs):assert dspan.insert({rows6[u]:c for u,c in D.items()},{j:1}) is None
    null=dspan.insert({rows6[u]:c for u,c in F.items()},{len(pairs):1})
    assert null is not None and null[len(pairs)]==1
    fcoordinates={j:((-c)%prime if prime else -c) for j,c in null.items() if j<len(pairs)}
    report={'field':f'GF({prime})' if prime else 'Q','prime':prime,'N_columns':6*len(m7),'D_columns':len(m6),'rows':len(rows),
            'rank_N':rankN,'rank_N_AD':len(e.basis),'N_kernel_dimension':nullN,'D_projection_dimension':len(pairs),
            'independent_Koszul_generators':len(kspan.basis),'all_E1_lifts_verified':all(checks),
            'F_basis_coordinates':{str(j):str(c) for j,c in fcoordinates.items()},
            'legality':'D proportional to F is inadmissible; preserve its coordinate in general D',
            'column_elimination_steps':e.operations,'seconds':time.perf_counter()-started}
    print(json.dumps(report),flush=True)
    return report,pairs,jacobian_basis

def main():
    OUT.mkdir(exist_ok=True,parents=True)
    reports=[]
    for prime in (1000003,1000033,None):
        report,pairs,jacobian=rational_run(prime);reports.append(report)
        if prime is None:
            bundle={'instance':'holdout','q':1,'degree_D':6,'degree_N':7,'variables':VARS,'F':poly_json(F),'A':poly_json(A),
                    'basis':[{'D':poly_json(D),'N':[poly_json(n) for n in N]} for D,N in pairs],
                    'F_basis_coordinates':report['F_basis_coordinates'],
                    'reference':'https://github.com/hodge-computer/sextics/discussions/44',
                    'scope':'Complete first equation only, not a certificate; no parity or ansatz restriction'}
            path=OUT/'degree6_e1_basis.json';path.write_text(json.dumps(bundle,separators=(',',':')),encoding='utf-8')
            report['basis_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
    assert all(r['rank_N']==4437 and r['rank_N_AD']==4790 and r['D_projection_dimension']==109 for r in reports)
    (OUT/'degree6_e1_report.json').write_text(json.dumps({'runs':reports,'claim':'Independent reproduction of prior degree-six E1 result; not new mathematics or a full E2 solution'},indent=2),encoding='utf-8')

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    main()

#!/usr/bin/env python3
"""Test the NEW one-row residual in the r direction with a complete pole bound.

This is not a reuse of the obstruction for the original source.  First
subtract an explicit ordinary rational primitive of the residual.  Its
critical-point poles cancel against the vanishing r-connection.  The
remaining twisted equation has a complete Laurent ansatz of powers -16..2.
"""
import json,hashlib
from pathlib import Path
import sympy as s
from flint import nmod_mat

HERE=Path(__file__).resolve().parent
SRC=HERE/'inputs/source-rank2-connection.json'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()=='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
raw=json.loads(SRC.read_text())
a,b,c,d,r,v,t=s.symbols('a b c d r v t')
loc={str(z):z for z in (a,b,c,d)}
M={z:s.Matrix([[s.sympify(q,locals=loc) for q in row]
              for row in raw['connection'][str(z)]]) for z in (a,b,c,d)}
Delta=27*a*a*d*d-18*a*b*c*d+4*a*c**3+4*b**3*d-b*b*c*c
A=r**3+r**-3+(v*r-1)**6/r**15
Ar=s.diff(A,r);Av=s.diff(A,v)
psi=r**-3;psir=s.diff(psi,r)
Dv=lambda q:s.diff(q,v)-Av/Ar*s.diff(q,r)
psivv=s.cancel(Dv(Dv(psi)))
K=90*sum(s.binomial(4,k)*v**k*(-1)**(4-k)*r**(k-16)/s.Integer(k-16) for k in range(5))
H=s.cancel(psir*Av**2/Ar+K)
L=s.cancel(psir*Av**2+Ar*K)
assert s.cancel(s.diff(K,r)+psir*s.diff(A,v,2))==0
assert s.cancel(s.diff(H,r)-Ar*psivv)==0
assert s.cancel(Ar*H-L)==0
print('PASS exact ordinary primitive H and critical-pole cancellation',flush=True)

vp,tp=s.Integer(2),s.Integer(3)
Ap=A.subs(v,vp);Arp=s.diff(Ap,r)
ph={a:Ap,b:tp*vp,c:tp*(1-tp**2)/7,d:1+tp**6}
Ma=M[a].subs(ph).applyfunc(s.cancel)
N=(Arp*Ma).applyfunc(s.cancel)
# Seeking h_total = H e1/(36t^2) + h.  Then the exact remaining source is -N H e1/(36t^2).
g=(-L.subs(v,vp)*Ma[:,1]/(36*tp**2)).applyfunc(s.cancel)
G=s.Poly(s.cancel(r**15*Ap),r)
DeltaNum=s.Poly(s.cancel(r**30*Delta.subs(ph)),r)
assert G.degree()==18 and DeltaNum.degree()==36
assert s.gcd(G,G.diff()).degree()==0
assert s.gcd(DeltaNum,DeltaNum.diff()).degree()==0
assert s.gcd(G,DeltaNum).degree()==0
assert G.eval(0)!=0 and DeltaNum.eval(0)!=0
# These universal identities prove all finite singular residue eigenvalues.
DeltaMa=(Delta*M[a]).applyfunc(s.cancel)
assert s.cancel(s.trace(DeltaMa)+Delta/(3*a)+s.diff(Delta,a)/3)==0
assert s.cancel(DeltaMa.det()-Delta*(216*a*d*d-36*b*c*d+7*c**3)/(36*a))==0
assert M[a].applyfunc(lambda z:s.cancel(a*z).subs(a,0)).applyfunc(s.cancel)==s.Matrix([[0,-c/(6*b)],[0,-s.Rational(1,3)]])
R0=N.applyfunc(lambda z:s.limit(r*z,r,0))
Rinf=N.applyfunc(lambda z:s.limit(r*z,r,s.oo))
assert set(R0.eigenvals())=={s.Integer(5),s.Integer(10)}
assert set(Rinf.eigenvals())=={s.Integer(-1),s.Integer(-2)}
assert all(s.limit(z*r**17,r,0).is_finite for z in g)
assert any(s.limit(z*r**17,r,0)!=0 for z in g)
assert all(s.limit(z*r**12,r,s.oo)==0 for z in g)

basis=[(j,k) for j in range(2) for k in range(-16,3)]
columns=[]
for j,k in basis:
    q=s.zeros(2,1);q[j]=r**k
    columns.append((q.diff(r)+N*q).applyfunc(s.cancel))
den=s.lcm([s.denom(z) for col in columns for z in col]+[s.denom(z) for z in g])
polys=[[s.Poly(s.cancel(den*z),r) for z in col] for col in columns]
rhs=[s.Poly(s.cancel(den*z),r) for z in g]
maxdeg=max(p.degree() for col in polys for p in col)
maxdeg=max(maxdeg,*[p.degree() for p in rhs])
rows=[]
for j in range(2):
    for k in range(maxdeg+1):
        row=[col[j].nth(k) for col in polys]+[rhs[j].nth(k)]
        if any(row):rows.append(row)
prime=32003
def modq(q):return int(q.p)%prime*pow(int(q.q),-1,prime)%prime
modrows=[[modq(z) for z in row] for row in rows]
cm=nmod_mat([row[:-1] for row in modrows],prime)
am=nmod_mat(modrows,prime)
rank,arank=cm.rank(),am.rank()
report={'specialization':{'v':2,'t':3},
        'ordinary_primitive':'H=psi_r*A_v^2/A_r+K',
        'K':str(K),'L':str(s.factor(L)),
        'exact_identity':'dH/dr=A_r*psi_vv; A_r*H=L',
        'initial_residual':'A_r*psi_vv*e1/(36*t^2)',
        'subtracted_primitive':'H*e1/(36*t^2)',
        'remaining_twisted_source':'-L*M_a*e1/(36*t^2)',
        'basis':[{'row':j,'power':k} for j,k in basis],
        'source_order_zero':-17,'source_order_infinity_at_most':-13,
        'matrix_shape':[len(rows),len(basis)],'prime':prime,
        'coefficient_rank_mod_p':rank,'augmented_rank_mod_p':arank,
        'claim':'No rational r-direction primitive for the NEW residual; two/three-direction problem still open.' if rank==len(basis) and arank==rank+1 else 'Further investigation required.'}
(HERE/'residual-vertical-r-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2),flush=True)
assert rank==len(basis) and arank==rank+1

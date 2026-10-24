#!/usr/bin/env python3
"""Complete rational r-only test at a good (v,t) specialization.

The connection and source are the exact transformed physical system.
At generic finite roots of A Delta its residue eigenvalues are 0,-1/3;
the source has at most simple poles.  Thus a rational primitive has no
finite poles except r=0.  At zero the connection residue eigenvalues
are 5,10; at infinity its r-normalized limit has eigenvalues -1,-2.
Consequently any rational primitive is Laurent with exponents -10..2.
This script checks a good specialization exactly, with a finite-field
matrix witness and full column rank.  A good specialization with full
column rank implies the same generic inconsistency over Q(v,t).
"""
import hashlib,json
from pathlib import Path
import sympy as s
from flint import nmod_mat

HERE=Path(__file__).resolve().parent
SRC=HERE/'inputs/source-rank2-connection.json'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()=='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
raw=json.loads(SRC.read_text())
a,b,c,d,r=s.symbols('a b c d r')
loc={str(z):z for z in (a,b,c,d)}
M={z:s.Matrix([[s.sympify(q,locals=loc) for q in row]
              for row in raw['connection'][str(z)]]) for z in (a,b,c,d)}
Delta=27*a*a*d*d-18*a*b*c*d+4*a*c**3+4*b**3*d-b*b*c*c
# Exact universal residue proof, not a numerical residue example.
DeltaMa=(Delta*M[a]).applyfunc(s.cancel)
assert s.cancel(s.trace(DeltaMa)+Delta/(3*a)+s.diff(Delta,a)/3)==0
assert s.cancel(DeltaMa.det()-Delta*(216*a*d*d-36*b*c*d+7*c**3)/(36*a))==0
Ra=M[a].applyfunc(lambda z:s.cancel(a*z).subs(a,0)).applyfunc(s.cancel)
assert Ra==s.Matrix([[0,-c/(6*b)],[0,-s.Rational(1,3)]])
vp,tp=s.Integer(2),s.Integer(3)
A=r**3+r**-3+(vp*r-1)**6/r**15
B=tp*vp;C=tp*(1-tp**2)/7;D=1+tp**6
ph={a:A,b:B,c:C,d:D}
N=(s.diff(A,r)*M[a].subs(ph)).applyfunc(s.cancel)
g=(r**-4*M[b].subs(ph)[:,0]/12).applyfunc(s.cancel)
G=s.Poly(s.cancel(r**15*A),r)
H=s.Poly(s.cancel(r**30*Delta.subs(ph)),r)
assert G.degree()==18 and H.degree()==36
assert s.gcd(G,G.diff()).degree()==0
assert s.gcd(H,H.diff()).degree()==0
assert s.gcd(G,H).degree()==0
assert G.eval(0)!=0 and H.eval(0)!=0
R0=N.applyfunc(lambda z:s.limit(r*z,r,0))
Rinf=N.applyfunc(lambda z:s.limit(r*z,r,s.oo))
assert set(R0.eigenvals())=={s.Integer(5),s.Integer(10)}
assert set(Rinf.eigenvals())=={s.Integer(-1),s.Integer(-2)}
assert all(s.limit(z/r**10,r,0)==0 for z in g)
assert all(s.limit(z*r**6,r,s.oo)==0 for z in g)

basis=[(j,k) for j in range(2) for k in range(-10,3)]
columns=[]
for j,k in basis:
    v=s.zeros(2,1);v[j]=r**k
    columns.append((v.diff(r)+N*v).applyfunc(s.cancel))
# Exact rational polynomial identity matrix after clearing one denominator.
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
assert rank==26 and arank==27
report={'specialization':{'v':2,'t':3},'basis':[{'row':j,'power':k} for j,k in basis],
        'finite_residue_proof':{
          'a_zero':'res(a Ma)=[[0,-c/(6b)],[0,-1/3]]',
          'Delta_zero_trace':'trace(Delta Ma)=-Delta/(3a)-Delta_a/3',
          'Delta_zero_determinant':'det(Delta Ma)=Delta*(216ad^2-36bcd+7c^3)/(36a)',
          'conclusion':'At every simple Delta root, residue=(Delta Ma)/Delta_a has trace -1/3 and determinant0.'},
        'good_finite_poles':True,'G_degree':18,'Delta_numerator_degree':36,
        'residue_zero':[[str(z) for z in row] for row in R0.tolist()],
        'r_times_connection_at_infinity':[[str(z) for z in row] for row in Rinf.tolist()],
        'source_order_zero_at_least':11,'source_order_infinity_at_most':-7,
        'matrix_shape':[len(rows),26],'coefficient_rank_mod_p':rank,
        'augmented_rank_mod_p':arank,'prime':prime,
        'claim':'No rational primitive in the r direction over Q(v,t); full three-direction system remains open.'}
(HERE/'vertical-r-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))

#!/usr/bin/env python3
"""Exact source binding and small degree-18 cover for one-reflection-skew.

All identities are in rational function fields over Q.  No physical
coefficient direction is omitted.  This is a coordinate/current reduction,
not a primitive or a HasCertificate claim.
"""
import hashlib
import json
from pathlib import Path
from itertools import combinations
import sympy as S

HERE=Path(__file__).resolve().parent
SRC=HERE/'inputs/source-rank2-connection.json'
assert hashlib.sha256(SRC.read_bytes()).hexdigest()=='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
raw=json.loads(SRC.read_text())
a,b,c,d,r,w,t,v,alpha=S.symbols('a b c d r w t v alpha')
coeff=(a,b,c,d)
loc={str(z):z for z in coeff}
M={z:S.Matrix([[S.sympify(q,locals=loc) for q in row]
              for row in raw['connection'][str(z)]]) for z in coeff}
e0=S.Matrix([1,0]);e1=S.Matrix([0,1]);checks=[]

def check(name,x):
    vals=list(x) if isinstance(x,S.MatrixBase) else [x]
    assert all(S.cancel(z)==0 for z in vals),name
    checks.append(name)
    print('PASS',name,flush=True)

def gauge_check(name,sub,T,parameter):
    old={z:M[z].subs(sub,simultaneous=True) for z in coeff}
    for x in (*coeff,parameter):
        Mold=sum((old[z]*S.diff(sub[z],x) for z in coeff),S.zeros(2))
        Mnew=M[x] if x in coeff else S.zeros(2)
        check(name+' connection '+str(x),T.diff(x)+Mnew*T-T*Mold)
    return old

# The old JSON chart is Y1=1, Y0=alpha.  The actual canonical chart
# is Y0=1, t=1/alpha.  Uold=alpha^2 Unew and nuold=alpha nunew.
sub_chart={a:a,b:alpha**2*b,c:alpha**4*c,d:alpha**6*d}
Tc=S.diag(alpha**-3,alpha**-1)
Mc=gauge_check('projective chart',sub_chart,Tc,alpha)
check('old source and d-alpha transform to canonical source',
      (-alpha**3)*Tc*Mc[b]*e0*(-alpha**2)-M[b]*e0)
old_c=alpha*r*(alpha**2-1)/7
check('physical c sign after chart inversion',
      (old_c/alpha**4).subs(alpha,1/t)-r*t*(1-t**2)/7)

# V=r U and v=1/r+r w.  The new universal coefficients are a,b,c,d;
# old coefficients are r^3 a,r^2 b,r c,d.
sub_scale={a:r**3*a,b:r**2*b,c:r*c,d:d}
Tr=S.diag(r**-1,r**-2)
Mr=gauge_check('fibre rescaling',sub_scale,Tr,r)
check('source under fibre rescaling',Tr*Mr[b]*e0-r**-3*M[b]*e0)

winv=(v*r-1)/r**2
A=r**3+r**-3+(v*r-1)**6/r**15
f=r**18+r**12+(v*r-1)**6-a*r**15
check('new cubic leading coefficient',(1+r**6+w**6).subs(w,winv)/r**3-A)
check('new cubic quadratic coefficient',(t*(r+r**3*w)).subs(w,winv)/r**2-t*v)
check('new cubic linear coefficient',(r*t*(1-t**2)/7)/r-t*(1-t**2)/7)
check('degree-18 polynomial identity',f-r**15*(A-a))
check('physical base volume',S.diff(winv,v)-1/r)
check('f-r on the cover',S.diff(f,r).subs(a,A)-r**15*S.diff(A,r))
phi=r**11/S.diff(f,r)
check('complete transformed source density',
      (r**-4/S.diff(A,r)-phi).subs(a,A))

# Derivatives on the degree-18 cover.  t has no covering correction.
ra=r**15/S.diff(f,r)
rv=-6*r*(v*r-1)**5/S.diff(f,r)
check('implicit a derivative',S.diff(f,a)+S.diff(f,r)*ra)
check('implicit v derivative',S.diff(f,v)+S.diff(f,r)*rv)
check('implicit t derivative',S.diff(f,t))
check('source is algebraic a derivative before rank-2 twist',
      -S.diff(r**-3,r)*ra/3-phi)
for i in range(18):
    if i!=14:
        check('codifferent a integration slot '+str(i),
              S.diff(r**(i-14)/S.Integer(i-14),r)*ra-r**i/S.diff(f,r))
check('exceptional slot is d-log r',ra/r-r**14/S.diff(f,r))

# A small exact one-form identity in the universal rank-two connection.
beta={a:S.Matrix([-c/(3*a),-2*b/(3*a)]),
      b:e1,c:e0,d:S.Matrix([-2*c/(3*d),-b/(3*d)])}
theta={a:0,b:0,c:0,d:1/(6*d)}
for x,y in combinations(coeff,2):
    lhs=beta[y].diff(x)-beta[x].diff(y)+M[x]*beta[y]-M[y]*beta[x]
    check('twisted closed beta '+str(x)+str(y),
          lhs-theta[x]*beta[y]+theta[y]*beta[x])

# Exact two-stage current after passing to (a,v,t).  Abstract commuting
# derivatives of psi suffice, since the rational cover is etale generically.
psia,psiv,psiav,psivv=S.symbols('psi_a psi_v psi_av psi_vv')
Xa=psiv*e0/(36*t)
Xv=-psia*e0/(36*t)-psiv*e1/(36*t**2)
div=(psiav*e0/(36*t)-psiav*e0/(36*t)-psivv*e1/(36*t**2)
     +M[a]*Xa+t*M[b]*Xv)
B=-psia*M[b]*e0/36
check('companion-column identity',M[a]*e0-M[b]*e1)
check('two-stage current and full remaining one-row source',
      div-B+psivv*e1/(36*t**2))

# Kernel of the degree-nine P/a scan, hence exact column-rank upper bound.
ph={a:1+r**6+w**6,b:t*(r+r**3*w),c:r*t*(1-t**2)/7,d:1+t**6}
ar=ph[a]
Ps=[S.Matrix([-S.Rational(2,7)*r*w**5*(1-t**2),r**3*ar-4*r*w**5*(1+r**2*w)]),
    S.Matrix([-S.Rational(1,7)*(1-t**2)*(1+w**6-r**6),-ar*(1+3*r**2*w)+4*r**6*(1+r**2*w)]),
    S.zeros(2,1)]
# Verify using the universal closed-one-form identity, avoiding huge
# physical expansions: alpha=beta+(4c,2b) dlog(d)/6, and d=d(t).
alph={a:S.Matrix([-c/(3*a),-2*b/(3*a)]),b:e1,c:e0,d:S.zeros(2,1)}
pull={x:sum((alph[z].subs(ph)*S.diff(ph[z],x) for z in coeff),S.zeros(2,1))
      for x in (r,w,t)}
check('degree-nine kernel flux r',Ps[0]/ar-pull[w]/t)
check('degree-nine kernel flux w',Ps[1]/ar+pull[r]/t)
for x,y in combinations((a,b,c),2):
    check('alpha is closed with fixed d '+str(x)+str(y),
          alph[y].diff(x)-alph[x].diff(y)+M[x]*alph[y]-M[y]*alph[x])

N={a:M[a],v:t*M[b],
   t:v*M[b]+(1-3*t**2)*M[c]/7+6*t**5*M[d]}
report={
 'checks':checks,'checks_passed':len(checks),
 'claim':'Exact source and connection equivalence; not a rational primitive.',
 'coordinate_maps':{'canonical':'Y0=1, X0=x, X1=r*x, X2=w*x, Y1=t; U=x^2',
                    'simple_base':'v=1/r+r*w; V=r*U',
                    'inverse':'w=(v*r-1)/r^2',
                    'coefficient_map':{'a':str(A),'b':'t*v','c':'t*(1-t**2)/7','d':'1+t**6'}},
 'cover':str(f),'cover_degree':18,'cover_t_derivative':0,
 'source_density':'r^11/f_r * M_b*e0/12 in da wedge dv wedge dt',
 'cover_derivatives':{'r_a':str(ra),'r_v':str(rv),'r_t':'0'},
 'rank_two_connection_before_substitution':{
    str(x):[[str(S.cancel(N[x][i,j])) for j in range(2)] for i in range(2)] for x in N},
 'connection_substitution':{'b':'t*v','c':'t*(1-t**2)/7','d':'1+t**6'},
 'codifferent_integrals':'r^i/f_r = partial_a[r^(i-14)/(i-14)] for i!=14',
 'codifferent_exception':'slot14 is partial_a(log r); residue1 on the rational r-line',
 'beta':'(dc-c/3*dlog(a)-2c/3*dlog(d), db-2b/3*dlog(a)-b/3*dlog(d))^T',
 'beta_identity':'D_M beta = dlog(d)/6 wedge beta',
 'two_stage_current':{'psi':'r^(-3)',
    'Xa':'psi_v e0/(36t)',
    'Xv':'-psi_a e0/(36t)-psi_v e1/(36t^2)',
    'Xt':'0',
    'identity':'Div_D X = r11/fr M_b e0/12 - psi_vv e1/(36t^2)',
    'scope':'Exact rational current subtraction; remaining one-row source is not discarded.'},
 'exact_degree9_kernel':[list(map(str,z)) for z in Ps],
 'degree9_bound_note':'The nonzero exact kernel proves coefficient rank<=659; combine with rank659/augmented660 mod32003.'}
out=HERE/'simple-cover-report.json'
out.write_text(json.dumps(report,indent=2)+'\n')
print('ALL',len(checks),'CHECKS PASSED',flush=True)

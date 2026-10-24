#!/usr/bin/env python3
"""Independent audit of the protected source and degree-nine exclusion.

This file uses a direct fibre-reduction identity and a fully cleared
physical polynomial kernel, not the geometric derivation of the kernel.
The standard projective-volume sign is recorded separately from the
pinned packet convention.  No solve is claimed.
"""
import contextlib,io,json,sys
from pathlib import Path
import sympy as S

HERE=Path(__file__).resolve().parent
SRC=HERE/'inputs/source-rank2-connection.json'
raw=json.loads(SRC.read_text())
record=json.loads((HERE/'inputs/record.json').read_text())
a,b,c,d,U,x,r,w,t,y,v=S.symbols('a b c d U x r w t y v')
parameters=(a,b,c,d)
local={str(z):z for z in (*parameters,U)}
M={z:S.Matrix([[S.sympify(q,locals=local) for q in row] for row in raw['connection'][str(z)]]) for z in parameters}
Rs={z:[S.sympify(q,locals=local) for q in raw['exact_corrections_R'][str(z)]] for z in parameters}
P=a*U**3+b*U**2+c*U+d
checks=[]


def check(name,expr):
    entries=list(expr) if isinstance(expr,S.MatrixBase) else [expr]
    assert all(S.cancel(z)==0 for z in entries),name
    checks.append(name)


# Reconstruct the protected polynomial without importing any reduced model.
X=S.symbols('X0 X1 X2 Y0 Y1 Y2')
poly=S.sympify(record['F']['expression'],locals={str(z):z for z in X})
source=S.sympify(record['A']['expression'],locals={str(z):z for z in X})
chart={X[0]:x,X[1]:r*x,X[2]:w*x,X[3]:1,X[4]:t,X[5]:y}
physical={a:1+r**6+w**6,b:t*(r+r**3*w),c:r*t*(1-t**2)/7,d:1+t**6}
check('protected F on Y0=1 chart',poly.subs(chart)-(P.subs(physical).subs(U,x*x)+y**6))
check('protected A on Y0=1 chart',source.subs(chart)-x**3)

# Eight exact fibre identities independently bind all connection columns.
# v^6=-P, hence d(R/v^5)=(-P R_U+5 P_U R/6) dU/v^11.
for z in parameters:
    for k in range(2):
        rhs=-P*(M[z][0,k]+M[z][1,k]*U)-P*S.diff(Rs[z][k],U)+S.Rational(5,6)*S.diff(P,U)*Rs[z][k]
        check('fibre connection '+str(z)+' column '+str(k),
              S.Rational(5,6)*U**k*S.diff(P,z)-rhs)

# Standard projective Ω on Y0=1 has chart sign (-1)^3.
# Reordering dx,dr,dw,dt,dy to dr,dw,dt,dx,dy adds (-1)^3.
jac=S.Matrix([x,r*x,w*x,t,y]).jacobian([x,r,w,t,y]).det()
Q=S.cancel((-1)**3*source.subs(chart)*jac*(-1)**3/(2*x))
check('standard Omega numerator in dU,dy',Q-x**4/2)
normal_coefficient=-5*S.Rational(1,2)*U**2/(36*y**11)
check('normal-last double-pole source sign',
      normal_coefficient+S.Rational(1,12)*S.Rational(5,6)*U**2/y**11)

# Full cleared physical kernel, checked as a polynomial identity.
sys.path.insert(0,str(HERE))
import a_denominator_search as scan
ar=physical[a]
Ps=[S.Matrix([-S.Rational(2,7)*r*w**5*(1-t**2),
               r**3*ar-4*r*w**5*(1+r**2*w)]),
    S.Matrix([-S.Rational(1,7)*(1-t**2)*(1+w**6-r**6),
               -ar*(1+3*r**2*w)+4*r**6*(1+r**2*w)]),
    S.zeros(2,1)]
for i in range(2):
    total=S.Poly(0,r,w,t,domain=S.QQ)
    for j,z in enumerate((r,w,t)):
        total+=scan.ad*S.Poly(S.diff(Ps[j][i],z),r,w,t,domain=S.QQ)
        for k in range(2):
            total+=scan.Bs[j][i][k]*S.Poly(Ps[j][k],r,w,t,domain=S.QQ)
    assert total.is_zero,'cleared physical kernel row '+str(i)
    checks.append('cleared physical kernel row '+str(i))
assert any(z!=0 for flux in Ps for z in flux)
for j,flux in enumerate(Ps):
    for component in flux:
        assert S.Poly(component,r,w,t).total_degree()<=9
        check('kernel character '+str(j)+' '+str(component),
              component.subs({r:-r,t:-t},simultaneous=True)-(-1 if j!=1 else 1)*component)

# The modular ranks are exact finite computations.  Combined with the
# exact nonzero kernel above, they give a characteristic-zero exclusion.
with contextlib.redirect_stdout(io.StringIO()):
    rank=scan.run(9,prime=32003,seed=7149)
assert rank['columns']==660 and rank['rank']==659 and rank['augmented_rank']==660
checks.append('degree-nine rank659 and augmented660 replay')

# The physical source is also an ordinary derivative before twisting.
f=r**18+r**12+(v*r-1)**6-a*r**15
fr=S.diff(f,r);ra=r**15/fr;rv=-6*r*(v*r-1)**5/fr
F0=-r**-3/3
phi=r**11/fr
check('ordinary a primitive',S.diff(F0,r)*ra-phi)
check('ordinary v derivative',S.diff(F0,r)*rv+6*r**-3*(v*r-1)**5/fr)
check('ab connection flatness',M[b].diff(a)-M[a].diff(b)+M[a]*M[b]-M[b]*M[a])
check('adjacent compact columns',M[a]*S.Matrix([1,0])-M[b]*S.Matrix([0,1]))

result={
    'checks_passed':len(checks),'checks':checks,
    'source_orientation':{
        'standard_projective_Omega':'sum_i (-1)^i X_i dX_omit_i, variables (X0,X1,X2,Y0,Y1,Y2)',
        'standard_normal_last_residue':'-M_b e0/12 on Y0=1',
        'pinned_packet_convention':'+M_b e0/12 on Y0=1',
        'difference':'One global minus sign. Existence of a primitive and all coefficient ranks are unchanged.'},
    'rank_result':{k:rank[k] for k in ('degree','prime','columns','sample_rows','rank','augmented_rank')},
    'rank_logic':'The exact nonzero polynomial kernel bounds characteristic-zero coefficient rank by659. The modular matrix bounds coefficient rank below by659 and augmented rank below by660. Therefore the degree<=9 flux P/a ansatz is inconsistent in characteristic zero.',
    'scope':'All six flux entries of degree<=9, denominator a, and the forced simultaneous-sign parity. Averaging recovers this parity for any solution in the unrestricted bounded ansatz. No restriction or exclusion of other poles/degrees is asserted.',
    'twisted_IBP':{
        'F0':'-r^(-3)/3',
        'current_a':'F0*M_b*e0/12',
        'current_v':'-F0*M_a*e0/(12*t)',
        'current_t':'0',
        'source':'(r^11/f_r)*M_b*e0/12',
        'remaining_residual':'-r^(-3)*(v*r-1)^5*M_a*e0/(2*t*f_r)',
        'identity':'source = Div_nabla(current) + remaining_residual',
        'status':'Exact integration by parts; residual remains unsolved.'}}
(HERE/'independent-peer-audit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='checks'},indent=2))

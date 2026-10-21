"""Independent exact audit of displayed transport identities, not a packet replay or certificate."""
from pathlib import Path
import hashlib,json,sys,time
import sympy as s
if not __debug__: raise RuntimeError("Do not run with -O")
started=time.time()
here=Path(__file__).resolve().parents[2]/"results/one-reflection-skew-audit-20261021"
record_path=here/"inputs/live/upstream/data/one-reflection-skew/record.json"
record=json.loads(record_path.read_text(encoding="utf-8"))
checks=[]
def check(name,expr):
    value=s.cancel(s.expand(expr))
    if value!=0: raise AssertionError((name,value))
    checks.append(name)
X=s.symbols("X0 X1 X2 Y0 Y1 Y2")
def poly(key):
    return s.Add(*(s.Rational(c)*s.prod(x**e for x,e in zip(X,exps)) for c,exps in record[key]["terms"]))
F,A=poly("F"),poly("A")
assert record["q"]==1
perturbation=F-sum(q**6 for q in X)
perturbation_bounds=[sum(abs(co) for co in s.Poly(s.diff(perturbation,q),*X).coeffs()) for q in X]
assert max(perturbation_bounds)==s.Rational(30,7) and max(perturbation_bounds)<6
checks.append("all perturbing derivative coefficient sums < 6 (max 30/7)")
check("F invariant under Y2 reflection",F.subs(X[5],-X[5])-F)
check("A even under Y2 reflection",A.subs(X[5],-X[5])-A)
assert A!=0
checks.append("nonzero even A cannot equal odd Y2*B(x,Y2^2) in characteristic zero")
r,w,t,x,z,U=s.symbols("r w t x z U")
a,b,c,d,beta=s.symbols("a b c d beta")
pa=1+r**6+w**6; pb=t*(r+r**3*w); pc=r*t*(1-t**2)/7; pd=1+t**6
actual=F.subs(dict(zip(X,(x,r*x,w*x,1,t,z))),simultaneous=True)
check("protected F maps to z^6+P(x^2)",actual-(z**6+pa*x**6+pb*x**4+pc*x**2+pd))
check("protected A maps to x^3",A.subs(dict(zip(X,(x,r*x,w*x,1,t,z))),simultaneous=True)-x**3)
jac=s.Matrix([x,r*x,w*x]).jacobian((x,r,w)).det()
check("physical chart Jacobian is x^2",jac-x**2)
# Omega at Y0=1 is minus dX0^dX1^dX2^dt^dz. U=x^2:
check("physical source density is -U^2/2",(-x**3*jac)/(2*x)+x**4/2)
# d(U^2/(12 z^5) dU^nu /G) subtracts the double pole.
check("double-pole residue coefficient 5/72",(-s.diff(U**2/(12*z**5),z))/(6*z**5)-5*U**2/(72*z**11))
P=a*U**3+b*U**2+c*U+d
delta=s.discriminant(P,U)
R=3*a*a*beta**4-4*a*b*beta**3+6*a*c*beta**2-12*a*d*beta+4*b*d-c*c
M=b-3*a*beta
N=(c-3*a*beta**2)/2
k=N-M*beta
L=beta+3*k/M
check("quartic decomposition identity",R-4*(M*(d-a*beta**3)-N*N))
check("quartic derivative identity",M*s.diff(R,beta)+12*a*k*k+3*a*R)
check("cubic decomposition modulo quartic",M*(P-a*(U+beta)**3)-(M*U+N)**2-R/4)
H0=12*b*b*d-b*c*c-27*a*c*d
H1=6*a*(c*c-3*b*d)
Q=6*d*(b*c-9*a*d)+6*(b*c*c-2*b*b*d-3*a*c*d)*U+12*a*(c*c-3*b*d)*U*U
check("Hermite exact source reduction",-6*P*(H0+H1*U+s.diff(Q,U))+5*Q*s.diff(P,U)-30*delta*U*U)
check("differential pullback factor -1/6",M*((U+beta)*s.diff(P,U)-3*P+(M*U+N)*(U+L))+3*R/4)
field=s.QQ.frac_field(a,b,c,d)
def rem(poly):
    return s.rem(poly,R,beta,domain=field)
check("pushed coefficient two displayed formulas",
      rem(a*M*(beta*H1-H0)*k**3-delta*M*M*(3*a*beta**2*k-2*N*N)))
# Lagrange identity sum f(beta)/R'(beta) = leading degree-3 coefficient of rem(f,R)/(3a^2).
traces=[]
for j in range(3):
    numerator=rem(-12*a*beta**j*k)
    traces.append(s.cancel(s.Poly(numerator,beta).coeff_monomial(beta**3)/(3*a*a)))
for j,expected in enumerate((0,-6,-4*b/a)):
    check("quartic raw trace beta^%d M/k"%j,traces[j]-expected)
trace_beta=4*b/(3*a)
Ttrace=s.Matrix([[traces[1]+12,-traces[2]-3*trace_beta],[traces[0],-traces[1]]])
for i in range(2):
    for j in range(2): check("summed serving operator entry %d%d"%(i,j),Ttrace[i,j]-(6 if i==j else 0))
# Cubic field trace via rational partial fractions / Lagrange coefficients:
zz,xi,vv,mm,kk=s.symbols("zz xi vv mm kk")
h=vv*zz**3-mm*xi*zz**2-kk
check("inverse cubic zh' identity",zz*s.diff(h,zz)-(mm*xi*zz**2+3*kk)-3*h)
# The identities sum1/(z h')=1/k and sum z/h'=0 give the displayed pushforward factors.
assert s.Poly(zz,zz).degree()<s.Poly(h,zz).degree()-1
checks.append("cubic trace prerequisites h(0)=-k and degree(z)<2")
check("cubic trace constant",h.subs(zz,0)+kk)
# Covariant elliptic differential in independent variables a,M,xi with v^2=-M(1+a xi^3):
v,mu=s.symbols("v mu")
coords=(a,mu,xi)
dv=(-mu*xi**3/(2*v),v/(2*mu),-3*mu*a*xi**2/(2*v))
omega=(xi/(6*a*v),0,1/(2*v))
gamma=(1/(3*a),1/(2*mu),0)
def dd(f,j): return s.diff(f,coords[j])+s.diff(f,v)*dv[j]
for i in range(3):
    for j in range(i+1,3):
        f=s.cancel(dd(omega[j],i)-dd(omega[i],j)+gamma[i]*omega[j]-gamma[j]*omega[i])
        num=s.fraction(f)[0]
        check("domega=-gamma wedge omega coefficient %d%d"%(i,j),
              s.rem(num,v*v+mu*(1+a*xi**3),v))
physical={a:pa,b:pb,c:pc,d:pd}
point={r:1,w:1,t:2}
delta_point=s.factor(delta.subs(physical).subs(point))
q_point=s.factor((3*a*c-b*b).subs(physical).subs(point))
check("physical discriminant sample",delta_point+s.Rational(361978181,343))
check("physical nondegeneracy sample",q_point+s.Rational(166,7))
# Quartet separability and no M or k poles at this ordinary physical point:
Rpoint=s.Poly(R.subs(physical).subs(point),beta)
Mpoint=s.Poly(M.subs(physical).subs(point),beta)
kpoint=s.Poly(k.subs(physical).subs(point),beta)
assert s.gcd(Rpoint,Rpoint.diff()).degree()==0
assert s.gcd(Rpoint,Mpoint).degree()==0
assert s.gcd(Rpoint,kpoint).degree()==0
checks.append("sample quartic squarefree and coprime to M,k")
print(json.dumps({
 "scope":"Independent exact checks of displayed formulas only; no certificate or large-packet replay",
 "python":sys.version,"sympy":s.__version__,
 "record_sha256":hashlib.sha256(record_path.read_bytes()).hexdigest(),
 "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 "checks":checks,"count":len(checks),"result":"PASS",
 "delta_at_1_1_2":str(delta_point),"3ac_minus_b2_at_1_1_2":str(q_point),
 "quartic_discriminant_at_1_1_2":str(s.discriminant(Rpoint)),
 "perturbing_derivative_absolute_coefficient_sums":list(map(str,perturbation_bounds)),
 "seconds":time.time()-started},indent=2))

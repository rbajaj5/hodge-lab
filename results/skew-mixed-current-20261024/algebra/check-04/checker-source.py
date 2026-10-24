import argparse
import hashlib
import json
import pathlib
import sys
import time
import sympy as s

START = time.monotonic()
parser=argparse.ArgumentParser()
parser.add_argument('output',type=pathlib.Path)
parser.add_argument('--connection',required=True,type=pathlib.Path)
args=parser.parse_args()
PACKET=args.connection
OUT=args.output
if OUT.exists():
    raise SystemExit('refusing to overwrite output')
data = json.loads(PACKET.read_text(encoding='utf-8'))
a,b,c,d,r,v,t,V,z = s.symbols('a b c d r v t V z')
symbols = {str(x):x for x in [a,b,c,d,r,v,t,V,z]}
M = {name:s.Matrix([[s.sympify(x, locals=symbols) for x in row] for row in rows])
     for name, rows in data['connection'].items()}
f = r**18+r**12+(v*r-1)**6-a*r**15
fr = s.diff(f,r)
ra = r**15/fr
rv = -s.diff(f,v)/fr
checks = []
def zero(name,x):
    numer,denom = s.fraction(s.cancel(x))
    if numer != 0:
        raise ArithmeticError(name+': '+str(numer))
    checks.append({'name':name,'result':'pass'})

# A formal sheet R satisfies f(R)=0. No root approximation or scalar trace replay.
Uj = V/r
wj = (v*r-1)/r**2
P = a*V**3+t*v*V**2+t*(1-t**2)*V/7+1+t**6
physical = (1+r**6+wj**6)*Uj**3+r*t*(1+r**2*wj)*Uj**2+r*t*(1-t**2)*Uj/7+1+t**6
zero('sheet curve compatibility: pullback p minus compact P = V^3 f/r^15', physical-P-V**3*f/r**15)
def Da(h): return s.diff(h,a)+s.diff(h,r)*ra
def Dv(h): return s.diff(h,v)+s.diff(h,r)*rv
J = s.Matrix([[s.diff(h,V),Da(h),Dv(h),s.diff(h,t)] for h in [Uj,r,wj,t]])
zero('sheet four-form Jacobian',J.det()-r**13/fr)
zero('full normalized sheet coefficient, fibre first',s.Rational(5,72)*Uj**2*J.det()/z**11-s.Rational(5,72)*r**11/fr*V**2/z**11)

# New two-direction continuation of the packet's reused one-row residual.
sub = {b:t*v,c:t*(1-t**2)/7,d:1+t**6}
Mb = M['b'].subs(sub)
Nt = (v*M['b']+(1-3*t**2)/7*M['c']+6*t**5*M['d']).subs(sub)
e0=s.Matrix([1,0]); e1=s.Matrix([0,1])
g,k = s.symbols('g k')
# Here psi=r^-3, g=psi_vv and k=v psi_v-psi, so k_v=v*g.
# Flux Y_t=-g e1/(36t), Y_v=-k e0/(108at).
# g_t=k_t=0; N_v=t M_b. These exact two-row residuals are new.
R0=g*e1/(36*t**2)
div_Yt=g*e1/(36*t**2)-g*Nt*e1/(36*t)
div_Yv=-v*g*e0/(108*a*t)-k*Mb*e0/(108*a)
R2=g*(Nt*e1+v*e0/(3*a))/(36*t)+k*Mb*e0/(108*a)
for row in range(2):
    zero('new two-direction current identity row '+str(row),(R0-div_Yt-div_Yv-R2)[row])
    zero('regularized Nt column vanishes at t=0 row '+str(row),(Nt*e1+v*e0/(3*a))[row].subs(t,0))
    rr=s.cancel(R2[row])
    num,den=s.fraction(rr)
    if s.expand(den.subs(t,0)) == 0:
        raise ArithmeticError('remaining t=0 pole row '+str(row))
    checks.append({'name':'new residual has no t=0 pole, row '+str(row),'result':'pass'})

psi=r**-3
psiv=Dv(psi)
psivv=Dv(psiv)
kk=v*psiv-psi
zero('cover derivative k_v = v g',Dv(kk)-v*psivv)
point={a:s.Integer(3),v:s.Integer(2),r:s.Integer(1)}
g0=s.cancel(psivv).subs(point)
k0=s.cancel(kk).subs(point)
witness={str(x):str(y) for x,y in [('f',f.subs(point)),('f_r',fr.subs(point)),('g',g0),('k',k0)]}
actualR = [s.cancel(q.subs({g:g0,k:k0,a:3,v:2,t:1})) for q in R2]
if actualR == [0,0]: raise ArithmeticError('residual unexpectedly zero')
witness['R2_t1']=[str(q) for q in actualR]
witness['R2_t0']=[str(s.cancel(q).subs({g:g0,k:k0,a:3,v:2,t:0})) for q in R2]
checks.append({'name':'regularized residual is nonzero at an allowed exact point','result':'pass'})

# Newly needed projection of the CURRENT scalars, not a replay of the old
# weight-11 source trace. Newton sums of inverse roots use f's low terms.
coeff=[s.Poly(f,r).coeff_monomial(r**i) for i in range(4)]
inverse_sums={0:s.Integer(18)}
for n in range(1,4):
    inverse_sums[n]=s.expand(-sum(coeff[i]*inverse_sums[n-i] for i in range(1,n))-n*coeff[n])
zero('negative-third-power trace needed for current projection',inverse_sums[3]-6*v**3)
chi=psi-v**3/3
chiv=psiv-v**2
gt=psivv-2*v
kt=kk-s.Rational(2,3)*v**3
zero('trace-free current preserves original source derivative',Da(chi)-Da(psi))
zero('trace-free current preserves k_v=v g',Dv(kt)-v*gt)
zero('trace-free psi normalization',inverse_sums[3]-18*v**3/3)
g_t0=gt.subs(point); k_t0=kt.subs(point)
witness['trace_free_g']=str(g_t0)
witness['trace_free_k']=str(k_t0)
witness['trace_free_R2_t1']=[str(s.cancel(q.subs({g:g_t0,k:k_t0,a:3,v:2,t:1}))) for q in R2]
witness['trace_free_R2_t0']=[str(s.cancel(q).subs({g:g_t0,k:k_t0,a:3,v:2,t:0})) for q in R2]

# Gauge-improved current has no actual t=0 pole. Check it directly against
# the original source, using only psi_a=-3 phi and k=v psi_v-psi.
pp,pa,pv = s.symbols('psi psi_a psi_v')
Ma=M['a'].subs(sub)
ka=v*pv-pp
Qa=-pp*Mb*e0/36
Qv=(pp*Ma*e0-pv*Nt*e1-ka*e0/(3*a))/(36*t)
Qt=pv*Mb*e1/36
c1,d1=s.symbols('c1 d1')
# Verify the direct current before physical substitution, where the rational
# numerators are much smaller. D_v b=t; D_t(b,c,d)=(v,c1,d1).
ma,mb,mc,md=[M[q] for q in ['a','b','c','d']]
nt=v*mb+c1*mc+d1*md
qa=-pp*mb*e0/36
qv=(pp*ma*e0-pv*nt*e1-ka*e0/(3*a))/(36*t)
qt=pv*mb*e1/36
universal_R2=g*(nt*e1+v*e0/(3*a))/(36*t)+ka*mb*e0/(108*a)
divQa=qa.diff(a)+qa.diff(pp)*pa+ma*qa
divQv=qv.diff(v)+t*qv.diff(b)+qv.diff(pp)*pv+qv.diff(pv)*g+t*mb*qv
divQt=v*qt.diff(b)+c1*qt.diff(c)+d1*qt.diff(d)+nt*qt
improved_error=-pa*mb*e0/36-divQa-divQv-divQt-universal_R2
for row in range(2):
    # Check each scalar coefficient independently to avoid a large expansion.
    for scalar in [pp,pa,pv,g]:
        zero('regular-current direct identity row '+str(row)+' coefficient '+str(scalar),s.diff(improved_error[row],scalar))
    zero('regular-current constant term row '+str(row),improved_error[row].subs({pp:0,pa:0,pv:0,g:0}))
    zero('regular-current Qv numerator vanishes at t=0 row '+str(row),(pp*Ma*e0-pv*Nt*e1-ka*e0/(3*a))[row].subs(t,0))
    if s.fraction(s.cancel(Qv[row]))[1].subs(t,0)==0:
        raise ArithmeticError('Qv retains a t=0 pole')
    checks.append({'name':'regular-current Qv has no t=0 pole row '+str(row),'result':'pass'})

# Deliberate failures guard the new cancellations; these are not old scalar checks.
bad_t_div = g*e1/(36*t**2)+g*Nt*e1/(36*t)
bad_v_div = v*g*e0/(108*a*t)-k*Mb*e0/(108*a)
mutations=[]
for name,expr in [('wrong t-connection sign',R0-bad_t_div-div_Yv-R2),('wrong v derivative sign',R0-div_Yt-bad_v_div-R2),('drop compact row 1',s.Matrix([0,R2[1]]))]:
    vals=[s.cancel(q.subs({g:g0,k:k0,a:3,v:2,t:1})) for q in expr]
    if vals == [0,0]: raise ArithmeticError('mutation not detected '+name)
    mutations.append({'name':name,'nonzero_exact_witness':[str(q) for q in vals]})

res={
 'status':'pass', 'scope':'sheet-map compatibility and new regularization of the reused packet one-row residual; no scalar trace or CI replay',
 'source':str(PACKET),'source_sha256':hashlib.sha256(PACKET.read_bytes()).hexdigest(),
 'python':sys.version,'sympy':s.__version__,'seconds':time.monotonic()-START,
 'checks':checks,'mutations':mutations,'witness':witness,
 'residual_rows':[str(s.factor(s.cancel(q))) for q in R2],
 't0_residual':[str(s.factor(s.cancel(q).subs(t,0))) for q in R2]
}
OUT.write_text(json.dumps(res,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':'pass','checks':len(checks),'mutations':len(mutations),'seconds':res['seconds'],'witness':witness},indent=2))

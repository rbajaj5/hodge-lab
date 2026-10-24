import hashlib
import json
import pathlib
import sys
import time
import sympy as s

START = time.monotonic()
ROOT = pathlib.Path(r'C:\Users\anaxe\Documents\Codex\hl-source-20261023')
PACKET = ROOT / 'results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'
OUT = pathlib.Path(sys.argv[1])
if OUT.exists():
    raise SystemExit('refusing to overwrite output')
data = json.loads(PACKET.read_text())
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
OUT.write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps({'status':'pass','checks':len(checks),'mutations':len(mutations),'seconds':res['seconds'],'witness':witness},indent=2))

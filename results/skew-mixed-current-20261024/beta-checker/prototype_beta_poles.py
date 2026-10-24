#!/usr/bin/env python3
"""Exact generic pole-order proof for canonical beta h-star, locally at A_r=0.

Uses symbolic jets of A to avoid a broad coefficient search or giant expansion.
The source is centered R0 and the current is J=h-star*W*e1.
"""
from pathlib import Path
import hashlib,json,subprocess,sys,time,threading,os
HERE=Path(__file__).resolve().parent
if '--run' in sys.argv:
    st=time.monotonic()
    try:
        run=subprocess.run([sys.executable,str(Path(__file__).resolve())],capture_output=True,text=True,encoding='utf-8',timeout=60)
    except subprocess.TimeoutExpired as ex:
        def txt(x):return x.decode('utf-8',errors='replace') if isinstance(x,bytes) else (x or '')
        (HERE/'beta-poles-timeout.log').write_text(txt(ex.stdout)+txt(ex.stderr),encoding='utf-8');raise
    (HERE/'beta-poles.log').write_text(run.stdout+run.stderr,encoding='utf-8')
    print(run.stdout,end='');print(run.stderr,end='',file=sys.stderr)
    print('Child wall seconds:',round(time.monotonic()-st,3));sys.exit(run.returncode)
import sympy as S
watchdog=threading.Timer(58,lambda:os._exit(124));watchdog.daemon=True;watchdog.start()
r,v,t,a=S.symbols('r v t a')
ar,av,arr,arv,avv=S.symbols('A_r A_v A_rr A_rv A_vv')
P=t**8-3*t**6-3*t**2+1;Q=t**8-5*t**6-5*t**2+1;D=1+t**6
Wa=t*P/(7*D);Wv=t*v*Q/(21*a*D);Wt=t*t*(1-t*t)/(21*a)
q=t*(1-3*t*t+2*t**6-4*t**8)/(21*a*D)
E=Wa-av*Wv
def dr(x):return S.diff(x,r)+ar*S.diff(x,a)+arr*S.diff(x,ar)+arv*S.diff(x,av)
def dv(x):return S.diff(x,v)+av*S.diff(x,a)+arv*S.diff(x,ar)+avv*S.diff(x,av)
def da(x):return dr(x)/ar
def Dv(x):return dv(x)-av*dr(x)/ar
chiv=3*av/(r**4*ar)-v**2
g=Dv(chiv)
C=-av/(36*t*t*E)
h=C*chiv
L=lambda x:E*dr(x)/ar+Wv*dv(x)+Wt*S.diff(x,t)+q*x
R0=g/(36*t*t)
checks=[]
def check(name,x):
    z=S.cancel(x);assert z==0,(name,z)
    checks.append(name);print('PASS:',name,flush=True)
# Radial derivative cancellation removes all second derivatives of chi_v.
R_struct=Wa*dv(chiv)/(36*t*t*E)-chiv*L(C)
check('structural exact remainder',R0-L(h)-R_struct)
R=S.cancel(R_struct)
num,den=S.fraction(R)
denorder=S.Poly(den,ar).terms()[0][0][0] if len(S.Poly(den,ar).terms())==1 else None
assert denorder==1,(denorder,den)
assert S.cancel((ar*R).subs(ar,0))!=0
checks.append('generic jet remainder has exactly a simple A_r denominator')
print('PASS: exact generic jet remainder has only A_r^-1; A_r^-3 and A_r^-2 cancel',flush=True)
check('remainder contains no A_rr',S.diff(R,arr))

H=3*a*P-v*av*Q
J=[S.cancel(h*w) for w in (Wa,Wv,Wt)]
expected=[-a*P*av*chiv/(12*t*t*H),-v*Q*av*chiv/(36*t*t*H),-D*(1-t*t)*av*chiv/(36*t*H)]
for i in range(3):check('flux factored '+str(i),J[i]-expected[i])
leadJ=[S.cancel((t**k*Jj).subs(t,0)) for k,Jj in zip((2,2,1),J)]
assert all(x!=0 for x in leadJ)
leadR=S.cancel((t*t*R).subs(t,0));assert leadR!=0
checks.append('generic t orders of J are (-2,-2,-1) and remainder has order -2')
print('PASS: t poles are reintroduced in J and remainder',flush=True)

# Substitute the actual cover at two ordinary exact points to corroborate formula.
A=r**3+r**-3+(v*r-1)**6/r**15
jets={a:A,ar:S.diff(A,r),av:S.diff(A,v),arr:S.diff(A,r,2),arv:S.diff(A,r,v),avv:S.diff(A,v,2)}
point={r:S.Integer(1),v:S.Integer(2),t:S.Integer(1)}
jetpoint={x:S.cancel(y.subs(point)) for x,y in jets.items()};jetpoint.update(point)
check('exact residual ordinary point',R.subs(jetpoint)-S.Rational(1,18))
leadpoint=S.cancel(leadR.subs(jetpoint))
assert leadpoint!=0

# Check actual A_r-divisor residue nonvanishing by an exact complex chart point.
# At r=1,v=0: A_r=-15, so use polynomial remainder instead of selecting a root.
# v=2,t=1 specialization yields a univariate rational expression in r.
special={v:S.Integer(2),t:S.Integer(1)}
actualResidue=S.cancel((ar*R).subs(jets,simultaneous=True).subs(special))
ar_poly=S.fraction(S.cancel(S.diff(A,r).subs(v,2)))[0]
res_num,res_den=S.fraction(actualResidue)
gcd_num=S.gcd(S.Poly(ar_poly,r),S.Poly(res_num,r))
gcd_den=S.gcd(S.Poly(ar_poly,r),S.Poly(res_den,r))
assert gcd_den.degree()==0
assert gcd_num.degree()<S.degree(ar_poly,r)
checks.append('actual cover A_r simple pole survives at v=2,t=1 by polynomial gcd')
print('PASS: actual cover simple A_r pole survives; residue gcd degree',gcd_num.degree(),flush=True)

report={
 'status':'PASS: beta h-star cancels A_r^-3 and A_r^-2 but leaves simple ramification poles and trades denominator support',
 'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'checks':checks,
 'definitions':{'P':str(P),'Q':str(Q),'H':str(H),'E':str(E),'chi_v':str(chiv)},
 'exact_jet_remainder':str(R),'jet_remainder_denominator':str(S.factor(den)),
 'A_r_residue':str(S.cancel((ar*R).subs(ar,0))),
 'J_factored':[str(x) for x in expected],
 'J_t_orders':[-2,-2,-1],'J_t_leading_coefficients':[str(x) for x in leadJ],
 'remainder_t_order':-2,'remainder_t_leading_coefficient':str(leadR),'remainder_t_leading_value_at_r1_v2':str(leadpoint),
 'actual_cover_specialization':{'v':'2','t':'1','A_r_numerator_degree':S.degree(ar_poly,r),'residue_numerator_gcd_degree':gcd_num.degree(),'residue_denominator_gcd_degree':gcd_den.degree()},
 'denominator_trade':'Besides existing chart factors r,a,t, current introduces H=3aP-vA_vQ. J has H^-1; remainder generally H^-2. Generic t=0 poles are present. This is not simultaneous regularity of the earlier Q and ramification improvement.',
 'scope':'Exact algebraic identity in formal A jets, then an actual-cover gcd witness. Only this new beta candidate is checked. Nonzero survivor means no full primitive.',
 'provenance':'Independent derivation from the canonical scalar operator verified separately against the pinned connection.'
}
(HERE/'beta-poles.json').write_text(json.dumps(report,indent=2,default=str)+'\n',encoding='utf-8')
print('PASS:',len(checks),'pole and identity checks',flush=True)
watchdog.cancel()

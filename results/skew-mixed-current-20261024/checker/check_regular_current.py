#!/usr/bin/env python3
"""Independent direct check of regular representative Q and centered remainder.

Run --connection /path/to/source-rank2-connection.json --run.
The symbolic child has a 58-second watchdog and a 60-second parent timeout.
Only connection JSON is input; no proposer script or earlier check is imported.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time

HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser()
p.add_argument('--connection', type=Path, default=Path(r'C:/Users/anaxe/Documents/Codex/hl-source-20261023/results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'))
p.add_argument('--run', action='store_true')
args=p.parse_args()
if args.run:
    start=time.monotonic()
    try:
        run=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--connection',str(args.connection)],
                           capture_output=True,text=True,encoding='utf-8',timeout=60)
    except subprocess.TimeoutExpired as exc:
        def txt(x): return x.decode('utf-8',errors='replace') if isinstance(x,bytes) else (x or '')
        (HERE/'check-regular-current-timeout.log').write_text(txt(exc.stdout)+txt(exc.stderr),encoding='utf-8')
        raise
    (HERE/'check-regular-current.log').write_text(run.stdout+run.stderr,encoding='utf-8')
    print(run.stdout,end='');print(run.stderr,end='',file=sys.stderr)
    print('Child wall seconds:',round(time.monotonic()-start,3))
    sys.exit(run.returncode)

import sympy as S
watchdog=threading.Timer(58,lambda:os._exit(124));watchdog.daemon=True;watchdog.start()
a,b,c,d,v,t,r,z=S.symbols('a b c d v t r z')
ps,pa,pv,gv=S.symbols('chi chi_a chi_v chi_vv')
e0=S.Matrix([1,0]);e1=S.Matrix([0,1])
data=args.connection.read_bytes()
sha=hashlib.sha256(data).hexdigest()
assert sha=='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
raw=json.loads(data);loc={str(x):x for x in (a,b,c,d)}
M={x:S.Matrix([[S.sympify(y,locals=loc) for y in row] for row in raw['connection'][str(x)]]) for x in (a,b,c,d)}
sub={b:t*v,c:t*(1-t*t)/7,d:1+t**6}
Ma,Mb,Mc,Md=[M[x].subs(sub,simultaneous=True) for x in (a,b,c,d)]
Nv=t*Mb;Nt=v*Mb+(1-3*t*t)*Mc/7+6*t**5*Md
checks=[];controls=[]
def check(name,expr):
    xs=list(expr) if isinstance(expr,S.MatrixBase) else [expr]
    got=[S.cancel(x) for x in xs]
    assert all(x==0 for x in got),(name,got)
    checks.append(name);print('PASS:',name,flush=True)
def cv(x):return x.applyfunc(S.cancel)

Qa=-ps*Mb*e0/36
Qt=pv*Mb*e1/36
Qv=(ps*Ma*e0-pv*Nt*e1-(v*pv-ps)*e0/(3*a))/(36*t)
dQa=-pa*Mb*e0/36-ps*Mb.diff(a)*e0/36
dQt=pv*Mb.diff(t)*e1/36
dQv=(pv*Ma*e0+ps*Ma.diff(v)*e0-gv*Nt*e1-pv*Nt.diff(v)*e1-v*gv*e0/(3*a))/(36*t)
divQ=dQa+dQv+dQt+Ma*Qa+Nv*Qv+Nt*Qt
B=-pa*Mb*e0/36
R2=gv*(Nt*e1+v*e0/(3*a))/(36*t)+(v*pv-ps)*Mb*e0/(108*a)
defect=divQ+R2-B
for scalar in (ps,pa,pv,gv):
    check('direct Q identity coefficient '+str(scalar),defect.diff(scalar))
check('direct Q identity constant coefficient',defect.subs({ps:0,pa:0,pv:0,gv:0}))

Q={name:cv(vec) for name,vec in [('a',Qa),('v',Qv),('t',Qt)]}
den0={name:[S.factor(S.denom(x).subs(t,0)) for x in vec] for name,vec in Q.items()}
assert all(x!=0 for vec in den0.values() for x in vec)
checks.append('all six current components regular at generic t=0')
print('PASS: all six Q denominators nonzero at generic t=0',flush=True)
q0={name:S.simplify(vec.subs(t,0)) for name,vec in Q.items()}
check('Q_a(0)',q0['a'])
check('Q_t(0)',q0['t']+pv*e0/(108*a))
check('Q_v(0)',q0['v']-S.Matrix([-pv/(10584*a),(ps-3*v*pv)/(4536*a)]))

# New centering audit from the reciprocal polynomial, without old trace code.
f=r**18+r**12+(v*r-1)**6-a*r**15
reciprocal=S.Poly(S.expand(z**18*f.subs(r,1/z)),z)
coef=reciprocal.all_coeffs()
assert coef[0]==1
sums=[S.Integer(18)]
for j in range(1,4):
    sums.append(S.expand(-sum(coef[i]*sums[j-i] for i in range(1,j))-j*coef[j]))
check('Newton reciprocal trace r^-3',sums[3]-6*v**3)
check('centered chi has zero trace',sums[3]-18*v**3/3)
check('centered chi_v has zero trace',S.diff(sums[3],v)-18*v**2)
check('centered g has zero trace',S.diff(sums[3],v,2)-18*2*v)
check('centered k has zero trace',v*S.diff(sums[3],v)-sums[3]-18*2*v**3/3)

# Fixed-a derivatives at a nonsingular rational physical point, derived afresh.
A=r**3+r**-3+(v*r-1)**6/r**15
point_rv={r:S.Integer(1),v:S.Integer(2)}
Ar=S.diff(A,r);Av=S.diff(A,v)
ar=S.cancel(Ar.subs(point_rv));av=S.cancel(Av.subs(point_rv));rv=-av/ar
rrv=-(S.diff(A,v,2).subs(point_rv)+2*S.diff(A,r,v).subs(point_rv)*rv+S.diff(A,r,2).subs(point_rv)*rv**2)/ar
psi_a=-3/ar;psi_v=-3*rv;psi_vv=12*rv**2-3*rrv
pt={a:S.cancel(A.subs(point_rv)),v:S.Integer(2),t:S.Integer(1),ps:1-S.Rational(8,3),pa:psi_a,pv:psi_v-4,gv:psi_vv-4}
assert (pt[a],ar,pt[ps],pt[pa],pt[pv],pt[gv])==(3,-3,-S.Rational(5,3),1,-10,38)
delta=S.sympify(raw['Delta'],locals=loc).subs(sub,simultaneous=True)
assert S.cancel(delta.subs(pt))==1036
res=cv(R2).subs(pt).applyfunc(S.cancel)
assert all(x!=0 for x in res)
check('centered exact ordinary-point current equation',divQ.subs(pt)+res-B.subs(pt))
res0=cv(R2).subs(t,0).subs(pt).applyfunc(S.cancel)
check('centered t=0 residual',res0-S.Matrix([S.Rational(19,15876),S.Rational(19,1134)]))
for label,bad in [('flip Q_t sign',divQ-2*(dQt+Nt*Qt)+R2-B),
                  ('flip Q_v sign',divQ-2*(dQv+Nv*Qv)+R2-B),
                  ('flip residual sign',divQ-R2-B)]:
    val=bad.subs(pt).applyfunc(S.cancel)
    assert any(x!=0 for x in val),(label,val)
    controls.append({'name':label,'defect':[str(x) for x in val]})
    print('REJECTED CONTROL:',label,list(val),flush=True)

report={
 'status':'PASS: direct current Q and centered residual, not a full solution',
 'connection_sha256':sha,'source_path':str(args.connection),
 'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'python':sys.version,'sympy':S.__version__,
 'checks':checks,'sign_controls':controls,
 'current':{name:[str(x) for x in vec] for name,vec in Q.items()},
 'current_denominators_at_t_zero':{name:[str(x) for x in vec] for name,vec in den0.items()},
 'current_at_t_zero':{name:[str(x) for x in vec] for name,vec in q0.items()},
 'centered_definitions':'chi=r^-3-v^3/3; chi_a=psi_a; chi_v=psi_v-v^2; ghat=psi_vv-2v; khat=v*psi_v-psi-2v^3/3',
 'reciprocal_newton_sums':[str(x) for x in sums],
 'trace_reason':'Finite separable trace commutes with base derivations. Q and R2 are linear over the base field in chi and its derivatives, so their components have trace zero. This new audit concerns the new centering only.',
 'ordinary_point':{str(x):str(y) for x,y in pt.items()},
 'ordinary_point_delta':'1036','ordinary_point_A_r':str(ar),
 'ordinary_point_centered_residual':[str(x) for x in res],
 't_zero_centered_residual':[str(x) for x in res0],
 'domain':'Generic chart r!=0, a!=0, A_r!=0, Delta!=0. Reduced Q and R2 extend regularly to t=0 on that open. At t=0 Delta=27a^2; no claim at a=0 or cover ramification or discriminant.',
 'scope':'Q gives B=Div_D(Q)+R2 with a nonzero trace-free remainder. This remains a constructive reduction, not an all-sheet rational primitive or homogeneous certificate.',
 'provenance':'Independent Codex parallel checker directly loads pinned public fqlx connection JSON from benediamond packet. No proposer checker or old source/chart/rank/trace routine is imported.'
}
(HERE/'check-regular-current.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('PASS:',len(checks),'checks;',len(controls),'sign controls rejected',flush=True)
watchdog.cancel()

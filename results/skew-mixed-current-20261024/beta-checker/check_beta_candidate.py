#!/usr/bin/env python3
"""Independent canonical beta-current operator and h-star candidate check.

No imported proposer checker. --run imposes a 60-second child bound.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,time,threading,os
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--run',action='store_true')
p.add_argument('--connection',type=Path,default=Path(r'C:/Users/anaxe/Documents/Codex/hl-source-20261023/results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'))
args=p.parse_args()
if args.run:
    start=time.monotonic()
    try:
        run=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--connection',str(args.connection)],capture_output=True,text=True,encoding='utf-8',timeout=60)
    except subprocess.TimeoutExpired as ex:
        def txt(x):return x.decode('utf-8',errors='replace') if isinstance(x,bytes) else (x or '')
        (HERE/'beta-timeout.log').write_text(txt(ex.stdout)+txt(ex.stderr),encoding='utf-8');raise
    (HERE/'beta-check.log').write_text(run.stdout+run.stderr,encoding='utf-8')
    print(run.stdout,end='');print(run.stderr,end='',file=sys.stderr)
    print('Child wall seconds:',round(time.monotonic()-start,3));sys.exit(run.returncode)
import sympy as S
watchdog=threading.Timer(58,lambda:os._exit(124));watchdog.daemon=True;watchdog.start()
a,b,c,d,r,v,t=S.symbols('a b c d r v t')
rawbytes=args.connection.read_bytes();sha=hashlib.sha256(rawbytes).hexdigest()
assert sha=='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
raw=json.loads(rawbytes);loc={str(x):x for x in (a,b,c,d)}
M={x:S.Matrix([[S.sympify(y,locals=loc) for y in row] for row in raw['connection'][str(x)]]) for x in (a,b,c,d)}
C=t*(1-t*t)/7;D=1+t**6
sub={b:t*v,c:C,d:D}
Ma,Mb,Mc,Md=[M[x].subs(sub,simultaneous=True) for x in (a,b,c,d)]
N=[Ma,t*Mb,v*Mb+S.diff(C,t)*Mc+S.diff(D,t)*Md]
wa=-C/(3*a);wt=S.diff(C,t)-2*C*S.diff(D,t)/(3*D)
za=-2*t*v/(3*a);zt=v-t*v*S.diff(D,t)/(3*D)
W=S.Matrix([t*wt,zt*wa-za*wt,-t*wa]).applyfunc(S.factor)
q=S.factor(sum(S.diff(W[i],x)+N[i][1,1]*W[i] for i,x in enumerate((a,v,t))))
checks=[]
def check(name,x):
    ys=list(x) if isinstance(x,S.MatrixBase) else [x]
    z=[S.cancel(y) for y in ys];assert all(y==0 for y in z),(name,z)
    checks.append(name);print('PASS:',name,flush=True)
check('canonical beta current first connection row vanishes',sum(N[i][0,1]*W[i] for i in range(3)))
q_expected=t*(1-3*t**2+2*t**6-4*t**8)/(21*a*D)
check('second row zero-order coefficient',q-q_expected)
check('scalar operator exterior-form derivation',q-(S.diff(D,t)*W[2]/(6*D)-t*S.diff(wa,t)))

# Pull back only the NEW scalar candidate, retaining all physical derivatives.
A=r**3+r**-3+(v*r-1)**6/r**15
Ar=S.diff(A,r);Av=S.diff(A,v)
chi=r**-3-v**3/3
rv=-Av/Ar
chiv=S.diff(chi,v)+rv*S.diff(chi,r)
ghat=S.diff(chiv,v)+rv*S.diff(chiv,r)
Wphys=W.subs(a,A)
qphys=q_expected.subs(a,A)
E=Wphys[0]-Av*Wphys[1]
h=-Av*chiv/(36*t**2*E)
point={r:S.Integer(1),v:S.Integer(2),t:S.Integer(1)}
val=lambda x:S.cancel(x.subs(point))
hpoint=val(h)
hder=[val(S.diff(h,x)) for x in (r,v,t)]
Lpoint=val(E/Ar)*hder[0]+val(Wphys[1])*hder[1]+val(Wphys[2])*hder[2]+val(qphys)*hpoint
targetpoint=val(ghat/(36*t**2))
remainderpoint=S.cancel(targetpoint-Lpoint)
check('h-star point value',hpoint-S.Rational(7,2))
check('canonical scalar operator point value',Lpoint-1)
check('centered target point value',targetpoint-S.Rational(19,18))
check('candidate remainder point value',remainderpoint-S.Rational(1,18))
assert remainderpoint!=0
delta=S.sympify(raw['Delta'],locals=loc).subs(sub,simultaneous=True).subs(a,A)
assert (val(Ar),val(Av),val(delta),val(E))==(-3,6,1036,S.Rational(10,21))
wrong_sign=S.cancel(targetpoint+Lpoint-remainderpoint)
assert wrong_sign!=0

report={
 'status':'PASS for canonical beta-current operator and exact h-star point; candidate does not solve source',
 'source_sha256':sha,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'checks':checks,'W':[str(x) for x in W],'q':str(q_expected),
 'operator_in_base':'Lh=W_a*h_a+W_v*h_v+W_t*h_t+q*h',
 'operator_on_cover':'Lh=(W_a-A_v*W_v)*h_r/A_r+W_v*h_v_at_fixed_r+W_t*h_t+q*h',
 'h_star':'-A_v*chi_v/(36*t^2*(W_a-A_v*W_v)); chi_v is at fixed a',
 'point':{'r':'1','v':'2','t':'1','a':'3','A_r':'-3','A_v':'6','Delta':'1036','E':str(val(E)),'W':[str(val(x)) for x in Wphys],'q':str(val(qphys)),
          'chi_v':str(val(chiv)),'ghat':str(val(ghat)),'h':str(hpoint),'h_r_h_v_h_t':[str(x) for x in hder],
          'Lh':str(Lpoint),'R0_scalar':str(targetpoint),'remainder':str(remainderpoint)},
 'negative_control':{'flip_h_sign_defect':str(wrong_sign)},
 'domain':'Generic chart a*r*A_r*Delta*t*(1+t^6)*(W_a-A_v*W_v)!=0. The candidate introduces the E=W_a-A_v*W_v divisor; point check does not prove global pole cancellation.',
 'scope':'New beta current only. Raw h-star scalar current is matched to centered R0=chi_vv e1/(36t^2). It may be added to the known first current. Relation to regular Q/R2 uses their known current equivalence, not a new Q replay.',
 'provenance':'Independent checker derives the canonical beta wedge flux and uses the pinned connection directly; no proposer script is imported.'
}
(HERE/'beta-check.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('PASS:',len(checks),'new checks; nonzero remainder',remainderpoint,flush=True)
watchdog.cancel()

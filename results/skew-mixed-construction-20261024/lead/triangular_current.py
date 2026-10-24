"""New fixed-a triangular current: exact base-field coefficients and full residual.

Use a rational-function field for bounded coefficient calculations. Physical
root derivatives are represented by independent chi, chi_v, chi_vv jets; their
coefficients are checked exactly, not suppressed or numerically fitted.
"""
from pathlib import Path
import datetime, hashlib, json, sys, time
import sympy as s
from sympy.polys.fields import field
from sympy.polys.domains import QQ
start=time.monotonic(); out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
root=Path(__file__).resolve().parents[3]
source=root/'results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'
expected='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
if hashlib.sha256(source.read_bytes()).hexdigest()!=expected:raise RuntimeError('Pinned connection changed')
data=json.loads(source.read_text(encoding='utf-8'))
aa,bb,cc,dd,vv,tt=s.symbols('a b c d v t'); loc={str(x):x for x in [aa,bb,cc,dd,vv,tt]}
F,a,v,t=field('a,v,t',QQ)
C=t*(1-t*t)/7;D=1+t**6;Cp=C.diff(t);Dp=D.diff(t)
subs={bb:tt*vv,cc:tt*(1-tt**2)/7,dd:1+tt**6}
M={name:[[F.from_expr(s.sympify(x,locals=loc).subs(subs)) for x in row] for row in mat] for name,mat in data['connection'].items()}
def add(x,y):return [u+z for u,z in zip(x,y)]
def scale(c,x):return [c*z for z in x]
def mul(M,x):return [sum((z*y for z,y in zip(row,x)),F.zero) for row in M]
def mdiff(M,q):return [[z.diff(q) for z in row] for row in M]
def mscale(c,M):return [[c*z for z in row] for row in M]
def madd(*Ms):return [[sum((m[i][j] for m in Ms),F.zero) for j in range(2)] for i in range(2)]
Nt=madd(mscale(v,M['b']),mscale(Cp,M['c']),mscale(Dp,M['d']))
Nv=mscale(t,M['b'])
K=C*C-3*t*v*D;w=C*Cp-2*t*v*Dp;q=3*D*Cp-2*C*Dp
Gv=-t*v*w+3*a*q+2*v*K;Gt=-2*t*K
Gamma=[[3*t*w/2,-t*q],[F.zero,t*w/2]]
contracted=madd(mscale(Gv,Nv),mscale(Gt,Nt))
checks={}
def zero(label,x):
    values=[z for row in x for z in row] if x and isinstance(x[0],list) else x
    if any(z!=0 for z in values):raise RuntimeError(label+' failed')
    checks[label]='exact zero';print(label+' PASS',flush=True)
zero('contracted_triangular_connection',madd(contracted,mscale(-1,Gamma)))
div=Gv.diff(v)+Gt.diff(t)
kappa=[[Gamma[i][j]+(div if i==j else 0) for j in range(2)] for i in range(2)]
def DG(x):return [Gv*z.diff(v)+Gt*z.diff(t) for z in x]
def Op(x):return add(DG(x),mul(kappa,x))
alpha=[(Nt[i][1]+(v/(3*a) if i==0 else 0))/(36*t) for i in range(2)]
beta=[M['b'][i][0]/(108*a) for i in range(2)]
S=scale(1/Gv,alpha)
print('S constructed',flush=True)
T=scale(1/Gv,add(scale(v,beta),scale(-1,Op(S))))
print('T constructed',flush=True)
Cv=scale(-1,add(beta,Op(T)))
print('Cvec constructed',flush=True)
zero('chi_vv_coefficient',add(alpha,scale(-Gv,S)))
zero('chi_v_coefficient',add(scale(v,beta),scale(-1,add(Op(S),scale(Gv,T)))))
zero('chi_coefficient',add(scale(-1,beta),scale(-1,add(Op(T),Cv))))
def expr(x):return s.factor(x.as_expr())
def ev(x,point):return s.cancel(x.as_expr().subs(point,simultaneous=True))
point={aa:s.Integer(3),vv:s.Integer(2),tt:s.Integer(1)}
chi=-s.Rational(5,3);chiv=-10;chivv=38
R=[ev(z,point) for z in add(scale(chivv,alpha),scale(2*chiv-chi,beta))]
res=[chi*ev(z,point) for z in Cv]
if all(x==0 for x in res): raise RuntimeError('Selected point did not discriminate; candidate remains unresolved here')
result={'status':'EXACT_CANDIDATE_REJECTED','executor':'Pro root constructive lead','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-start,'python':sys.version,'sympy':s.__version__,'source_sha256':expected,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'checks':checks,'point':{str(x):str(y) for x,y in point.items()},'physical_r':'1','chi':'-5/3','chi_v':'-10','chi_vv':'38','Gv':str(ev(Gv,point)),'Gt':str(ev(Gt,point)),'R2':list(map(str,R)),'full_two_row_residual':list(map(str,res)),'S_at_point':[str(ev(x,point)) for x in S],'T_at_point':[str(ev(x,point)) for x in T],'scope':'Both rows and all derivative jets retained; specific rational current rejected. No arbitrary-current exclusion; no physical primitive, certificate, or solve.'}
(out/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2),flush=True)
# Exact expressions are saved for independent downstream use.
expressions={'Gv':Gv,'Gt':Gt,'alpha0':alpha[0],'alpha1':alpha[1],'beta0':beta[0],'beta1':beta[1],'S0':S[0],'S1':S[1],'T0':T[0],'T1':T[1],'C0':Cv[0],'C1':Cv[1]}
for name,value in expressions.items():
    (out/(name+'.txt')).write_text(str(value.as_expr())+'\n',encoding='utf-8')
print('saved exact expressions',flush=True)

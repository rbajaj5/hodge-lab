"""Independent full two-row checker for the fixed-a translation/gauge current.
Uses exact truncated Taylor arithmetic for coefficient derivatives, separately
from the proposed rational current's derivation. All v,t flux derivatives and
physical cover motion of chi are retained. No Lean or old checker replay.
"""
from pathlib import Path
from fractions import Fraction as Q
import datetime, hashlib, json, sys, time
import sympy as S
start=time.monotonic();root=Path(__file__).resolve().parents[3]
packet=root/'results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'
expected='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
if hashlib.sha256(packet.read_bytes()).hexdigest()!=expected:raise RuntimeError('Pinned connection changed')
data=json.loads(packet.read_text(encoding='utf-8'))
a,b,c,d,r,v,t=S.symbols('a b c d r v t');loc={str(x):x for x in [a,b,c,d,r,v,t]}
M={x:S.Matrix([[S.sympify(z,locals=loc) for z in row] for row in data['connection'][str(x)]]) for x in [a,b,c,d]}
C=t*(1-t*t)/7;D=1+t**6;Cp=S.diff(C,t);Dp=S.diff(D,t)
K=C*C-3*t*v*D;w=C*Cp-2*t*v*Dp;q0=3*D*Cp-2*C*Dp
Gv=-t*v*w+3*a*q0-2*v*K;Gt=2*t*K
sub={b:t*v,c:C,d:D};Nv=t*M[b].subs(sub);Nt=(v*M[b]+Cp*M[c]+Dp*M[d]).subs(sub)
Gamma=S.Matrix([[3*t*w/2,-t*q0],[0,t*w/2]])
checks={}
def check(name,x):
 y=x.applyfunc(S.cancel) if isinstance(x,S.MatrixBase) else S.cancel(x)
 if y!=(S.zeros(*y.shape) if isinstance(y,S.MatrixBase) else 0):raise RuntimeError(name+': '+str(y))
 checks[name]='zero';print(name+' PASS',flush=True)
check('gauge_connection_full_matrix',Gv*Nv+Gt*Nt-Gamma)
# Independent coefficient-jet expansion of the proposed two-row residual.
gv,gt,dv,dt,k00,k01,k10,k11=S.symbols('gv gt dv dt k00 k01 k10 k11')
s0,s1,sv0,sv1,st0,st1,T0,T1,Tv0,Tv1,Tt0,Tt1=S.symbols('s0 s1 sv0 sv1 st0 st1 T0 T1 Tv0 Tv1 Tt0 Tt1')
al0,al1,be0,be1,ch,cv,cvv=S.symbols('al0 al1 be0 be1 ch cv cvv')
kap=S.Matrix([[k00,k01],[k10,k11]])
ss=S.Matrix([s0,s1]);ssv=S.Matrix([sv0,sv1]);sst=S.Matrix([st0,st1]);tt=S.Matrix([T0,T1]);ttv=S.Matrix([Tv0,Tv1]);ttt=S.Matrix([Tt0,Tt1]);al=S.Matrix([al0,al1]);be=S.Matrix([be0,be1])
raw=al*cvv+be*(v*cv-ch)-(gv*(ss*cvv+(ssv+tt)*cv+ttv*ch)+gt*(sst*cv+ttt*ch)+kap*(ss*cv+tt*ch))
pred=(al-gv*ss)*cvv+(v*be-gv*ssv-gt*sst-gv*tt-kap*ss)*cv+(-be-gv*ttv-gt*ttt-kap*tt)*ch
check('all_jet_slots_full_two_rows',raw-pred)

class J:
 """Bivariate Q Taylor series through total degree two, coefficients / factorial."""
 def __init__(self,x=0):self.c=dict(x) if isinstance(x,dict) else {(0,0):Q(x)}
 @staticmethod
 def cast(x):return x if isinstance(x,J) else J(x)
 def __add__(self,other):
  q=J.cast(other);z=self.c.copy()
  for e,x in q.c.items():z[e]=z.get(e,Q(0))+x
  return J({e:x for e,x in z.items() if x})
 __radd__=__add__
 def __neg__(self):return J({e:-x for e,x in self.c.items()})
 def __sub__(self,q):return self+-J.cast(q)
 def __rsub__(self,q):return J.cast(q)+-self
 def __mul__(self,other):
  q=J.cast(other);z={}
  for e,x in self.c.items():
   for f,y in q.c.items():
    g=(e[0]+f[0],e[1]+f[1])
    if sum(g)<=2:z[g]=z.get(g,Q(0))+x*y
  return J({e:x for e,x in z.items() if x})
 __rmul__=__mul__
 def __pow__(self,n):
  n=int(n)
  if n<0:
   z=self.val()
   if not z:raise ZeroDivisionError('Zero jet denominator')
   u=(self-z)*(1/z);inv=(1-u+u*u)*(1/z)
   return inv**(-n)
  out=J(1);base=self
  while n:
   if n&1:out=out*base
   base=base*base;n//=2
  return out
 def __truediv__(self,q):return self*(J.cast(q)**-1)
 def __rtruediv__(self,q):return J.cast(q)*(self**-1)
 def diff(self,i):
  z={}
  for e,x in self.c.items():
   if e[i]:g=list(e);g[i]-=1;z[tuple(g)]=x*e[i]
  return J(z)
 def val(self):return self.c.get((0,0),Q(0))
def ev(expr,env):
 if expr in env:return env[expr]
 if expr.is_Rational:return J(Q(int(expr.p),int(expr.q)))
 if expr.is_Add:return sum((ev(x,env) for x in expr.args),J())
 if expr.is_Mul:
  out=J(1)
  for x in expr.args:out*=ev(x,env)
  return out
 if expr.is_Pow and expr.exp.is_Integer:return ev(expr.base,env)**int(expr.exp)
 raise RuntimeError('Unsupported expression '+str(expr))
def mvec(m,x):return [sum((m[i][j]*x[j] for j in range(2)),J()) for i in range(2)]
def plus(x,y):return [x[i]+y[i] for i in range(2)]
def vals(x):return [str(y.val()) for y in x]
A=r**3+r**-3+(v*r-1)**6/r**15;Ar=S.diff(A,r);Av=S.diff(A,v)
chi=r**-3-v**3/3;cvexpr=S.diff(chi,v)-Av*S.diff(chi,r)/Ar
cvvexpr=S.diff(cvexpr,v)-Av*S.diff(cvexpr,r)/Ar
points=[]
for rp,vp,tp in [(1,2,1),(1,2,2)]:
 point={r:S.Rational(rp),v:S.Rational(vp),t:S.Rational(tp)}
 aa=S.cancel(A.xreplace(point));p=S.cancel(Ar.xreplace(point));q=S.cancel(Av.xreplace(point))
 gvj=J({(0,0):Q(vp),(1,0):Q(1)});gtj=J({(0,0):Q(tp),(0,1):Q(1)})
 env={a:J(Q(str(aa))),v:gvj,t:gtj}
 nv=[[ev(Nv[i,j],env) for j in range(2)] for i in range(2)];nt=[[ev(Nt[i,j],env) for j in range(2)] for i in range(2)]
 mb=[[ev(M[b][i,j].subs(sub),env) for j in range(2)] for i in range(2)]
 Fv=ev(Gv,env);Ft=ev(Gt,env)
 gam=[[Fv*nv[i][j]+Ft*nt[i][j] for j in range(2)] for i in range(2)]
 divergence=Fv.diff(0)+Ft.diff(1);kk=[[gam[i][j]+(divergence if i==j else 0) for j in range(2)] for i in range(2)]
 alpha=[(nt[i][1]+(gvj/(3*Q(str(aa))) if i==0 else 0))/(36*gtj) for i in range(2)]
 beta=[mb[i][0]/(108*Q(str(aa))) for i in range(2)]
 scalarS=[x/Fv for x in alpha]
 dgS=[Fv*x.diff(0)+Ft*x.diff(1) for x in scalarS]
 kapS=mvec(kk,scalarS)
 scalarT=[(gvj*beta[i]-dgS[i]-kapS[i])/Fv for i in range(2)]
 dgT=[Fv*x.diff(0)+Ft*x.diff(1) for x in scalarT];kapT=mvec(kk,scalarT)
 coeff=[-beta[i]-dgT[i]-kapT[i] for i in range(2)]
 chval=S.cancel(chi.xreplace(point));cvval=S.cancel(cvexpr.xreplace(point));cvvval=S.cancel(cvvexpr.xreplace(point))
 chiJ=J({(0,0):Q(str(chval)),(1,0):Q(str(cvval)),(2,0):Q(str(cvvval))/2})
 def div_with(chj):
  hj=[scalarS[i]*chj.diff(0)+scalarT[i]*chj for i in range(2)]
  jv=[Fv*x for x in hj];jt=[Ft*x for x in hj]
  result=plus([x.diff(0) for x in jv],[x.diff(1) for x in jt]);result=plus(result,mvec(nv,jv));result=plus(result,mvec(nt,jt))
  return result,jv,jt
 full,jv,jt=div_with(chiJ)
 target=[alpha[i]*Q(str(cvvval))+beta[i]*(Q(vp)*Q(str(cvval))-Q(str(chval))) for i in range(2)]
 residual=[target[i]-full[i] for i in range(2)]
 if any(residual[i].val()!=chval*coeff[i].val() for i in range(2)):raise RuntimeError('Full residual versus survivor disagreement')
 wrongchi=J({(0,0):Q(str(chval)),(1,0):Q(-vp*vp),(2,0):Q(-vp)})
 wrongdiv,_,_=div_with(wrongchi)
 controls={
  'omit_cover_motion':[wrongdiv[i].val()-full[i].val() for i in range(2)],
  'drop_t_derivative':[jt[i].diff(1).val() for i in range(2)],
  'drop_t_connection':[x.val() for x in mvec(nt,jt)],
  'transpose_connection':[sum(nv[j][i].val()*jv[j].val()+nt[j][i].val()*jt[j].val() for j in range(2))-mvec(nv,jv)[i].val()-mvec(nt,jt)[i].val() for i in range(2)]}
 if any(not any(x) for x in controls.values()):raise RuntimeError('Mutation not detected')
 denominator={'r':rp,'t':tp,'a':str(aa),'Ar':str(p),'Gv':str(Fv.val()),'Delta':str(ev(S.sympify(data['Delta'],locals=loc).subs(sub),env).val())}
 if any(S.sympify(x)==0 for x in denominator.values()):raise RuntimeError('Invalid domain point')
 points.append({'point':{'r':rp,'v':vp,'t':tp,'a':str(aa)},'nonzero_denominators':denominator,'chi':str(chval),'chi_v':str(cvval),'chi_vv':str(cvvval),'Gv':str(Fv.val()),'Gt':str(Ft.val()),'S':vals(scalarS),'T':vals(scalarT),'coefficient_survivor':vals(coeff),'full_source_R2':vals(target),'full_divergence':vals(full),'residual':vals(residual),'flux_v':vals(jv),'flux_t':vals(jt),'mutations':{name:[str(x) for x in value] for name,value in controls.items()}})
if not any(any(S.sympify(x)!=0 for x in p['residual']) for p in points):raise RuntimeError('No rejection witness found')
out=Path(sys.argv[1])
if out.exists():raise RuntimeError('Fresh output required')
out.parent.mkdir(parents=True,exist_ok=False)
result={'status':'PASS_FULL_RESIDUAL_IDENTITY_AND_REJECTED_CANDIDATE','executor':'mixed_checker AI worker','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-start,'python':sys.version,'sympy':S.__version__,'packet_sha256':expected,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'checks':checks,'Gv':str(S.factor(Gv)),'Gt':str(S.factor(Gt)),'Gamma':[[str(x) for x in Gamma.row(i)] for i in range(2)],'candidate':'J_a=0, J_v=Gv*(S*chi_v+T*chi), J_t=Gt*(S*chi_v+T*chi), S=alpha/Gv, T=(v*beta-DG(S)-kappa*S)/Gv','residual_identity':'R2-Div_N J=chi*(-beta-DG(T)-kappa*T)','exact_points':points,'scope':'Specific new mixed two-row rational current rejected at exact physical points. Generic jet residual identity checked without treating either source row as scalar trace. No nonexistence for other currents. Finite coefficient jets preserve all needed derivatives; no generic survivor expansion is claimed.'}
out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))

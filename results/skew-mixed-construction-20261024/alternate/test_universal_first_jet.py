#!/usr/bin/env python3
"""Test a NEW mixed (v,t), two-row current linear in chi and chi_v.

No Lean; no old checks replayed. The literal connection is reused input.
K is permitted simple discriminant poles, not restricted to a polynomial.
This test specializes only base coefficients a=3,v=2, not moving-root jets.
"""
from pathlib import Path
import datetime, hashlib, json, sys, time
import sympy as S
START=time.monotonic()
ROOT=Path(__file__).resolve().parents[3]
SRC=ROOT/'results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'
# The exact packet pin, kept explicit to fail closed.
SHA='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
if hashlib.sha256(SRC.read_bytes()).hexdigest()!=SHA: raise RuntimeError('source pin mismatch')
a,b,c,d,t=S.symbols('a b c d t'); loc={str(x):x for x in [a,b,c,d,t]}
data=json.loads(SRC.read_text(encoding='utf-8'))
M={k:S.Matrix([[S.sympify(e,locals=loc) for e in row] for row in value]) for k,value in data['connection'].items()}
e0=S.Matrix([1,0]); e1=S.Matrix([0,1]); C=t*(1-t*t)/7; D=1+t**6
sub={a:S.Integer(3),b:2*t,c:C,d:D}
Nt=(2*M['b']+S.diff(C,t)*M['c']+S.diff(D,t)*M['d']).subs(sub).applyfunc(S.cancel)
Delta=S.sympify(data['Delta'],locals=loc).subs(sub)
Delta=S.Poly(Delta,t).monic().as_expr()
T=((M['a'].diff(b)+M['b']*M['a'])*e0/36).subs(sub).applyfunc(S.cancel)
N=(Delta*Nt).applyfunc(S.cancel); rhs=(Delta**2*T).applyfunc(S.cancel)
for e in list(N)+list(rhs): S.Poly(e,t)
if S.gcd(S.Poly(Delta,t),S.Poly(S.diff(Delta,t),t)).degree()!=0: raise RuntimeError('Delta not squarefree')
print('source specialized; Delta degree',S.degree(Delta,t),flush=True)
columns=[]; labels=[]
for row,degree in [(0,15),(1,13)]:
 for k in range(degree+1):
  p=S.zeros(2,1);p[row]=t**k
  col=Delta*p.diff(t)+(N-S.diff(Delta,t)*S.eye(2))*p
  columns.append(col.applyfunc(S.expand)); labels.append([row,k])
degree=max(S.degree(e,t) for col in columns for e in col if e!=0)
degree=max(degree,max(S.degree(e,t) for e in rhs if e!=0))
def flatten(col):
 return [S.Poly(col[j],t).nth(k) for j in range(2) for k in range(int(degree)+1)]
A=S.Matrix.hstack(*[S.Matrix(flatten(col)) for col in columns]); y=S.Matrix(flatten(rhs))
print('matrix',A.shape,'assembled',flush=True)
from sympy.polys.matrices import DomainMatrix
aug=DomainMatrix.from_Matrix(A.row_join(y)).convert_to(S.QQ)
rr,pivots=aug.rref(method='FF')
rankA=sum(p<A.cols for p in pivots);rankAug=len(pivots)
print('ranks',rankA,rankAug,flush=True)
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
record={'status':'UNIVERSAL_FIRST_JET_FAMILY_REJECTED' if rankAug>rankA else 'FAMILY_NOT_REJECTED',
 'executor':'Pro mixed_constructive AI worker','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'elapsed_seconds':time.monotonic()-START,'sympy_version':S.__version__,'python_version':sys.version,
 'source_sha256':SHA,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'base_specialization':{'a':'3','v':'2'},'Delta':str(Delta),'N_times_Delta':[[str(e) for e in row] for row in N.tolist()],
 'target_T':[str(e) for e in T],'rhs_Delta_squared_T':[str(e) for e in rhs],
 'candidate':'J_a=0; J_v=chi_v*e1/(36*t^2)-chi*M_a*e0/(36*t); J_t=chi*K',
 'full_residual':'Div_N J - R0 = chi*(D_t K + N_t*K - (partial_b M_a+M_b*M_a)*e0/36)',
 'K_family':'K=(P0,P1)/Delta, deg(P0)<=15, deg(P1)<=13',
 'matrix_shape':list(A.shape),'rank_coefficient':rankA,'rank_augmented':rankAug,'pivots':list(pivots),
 'limits':'A rejection is scoped to this universal first-jet family at this base specialization. No claim against arbitrary mixed actual-cover currents, no primitive, no trace computation.'}
system={'columns':labels,'coefficient_matrix':[[str(e) for e in row] for row in A.tolist()],'rhs':[str(e) for e in y]}
(out/'system.json').write_text(json.dumps(system,indent=2)+'\n',encoding='utf-8')
(out/'validation.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
print(json.dumps(record,indent=2),flush=True)

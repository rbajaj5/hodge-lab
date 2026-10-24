"""Independent coefficient-recurrence verification of the new first-jet system.
Reconstructs source from pinned literal connection and checks an exact left-null
inconsistency certificate. No claim that this covers arbitrary mixed currents.
"""
from pathlib import Path
from functools import reduce
import datetime, hashlib, json, math, sys, time
import sympy as S
from sympy.polys.matrices import DomainMatrix
start=time.monotonic();root=Path(__file__).resolve().parents[3]
packet=root/'results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'
expected='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
if hashlib.sha256(packet.read_bytes()).hexdigest()!=expected:raise RuntimeError('Source changed')
record=json.loads(packet.read_text(encoding='utf-8'))
a,b,c,d,t=S.symbols('a b c d t');loc={str(x):x for x in [a,b,c,d,t]}
M={str(x):S.Matrix([[S.sympify(e,locals=loc) for e in row] for row in record['connection'][str(x)]]) for x in [a,b,c,d]}
C=t*(1-t*t)/7;D=1+t**6
sub={a:S.Integer(3),b:2*t,c:C,d:D}
Delta=S.Poly(S.sympify(record['Delta'],locals=loc).subs(sub),t,domain=S.QQ).monic()
Nt=(2*M['b']+S.diff(C,t)*M['c']+S.diff(D,t)*M['d']).subs(sub)
Ns=[[S.Poly(S.cancel(Delta.as_expr()*Nt[i,j]),t,domain=S.QQ) for j in range(2)] for i in range(2)]
# Independent product-rule source: each entry differentiates the first column
# of Ma, then adds both compact intermediate rows of Mb*Ma.
T=[S.diff(M['a'][i,0],b)+sum(M['b'][i,j]*M['a'][j,0] for j in range(2)) for i in range(2)]
rhs=[S.Poly(S.cancel(Delta.as_expr()**2*T[i].subs(sub)/36),t,domain=S.QQ) for i in range(2)]
labels=[(0,k) for k in range(16)]+[(1,k) for k in range(14)]
def coeff(poly,k):return poly.nth(k) if k>=0 else S.Integer(0)
# Coefficient of t^n in Delta P' +(N−Delta'I)P for input e_j t^k.
A=S.Matrix([[coeff(Ns[i][j],n-k)+(2*k-n-1)*coeff(Delta,n-k+1)*int(i==j) for j,k in labels] for i in range(2) for n in range(26)])
y=S.Matrix([coeff(rhs[i],n) for i in range(2) for n in range(26)])
author=root/'results/skew-mixed-construction-20261024/alternate/first-jet-result-01/system.json'
auth=json.loads(author.read_text(encoding='utf-8'))
Am=S.Matrix([[S.Rational(x) for x in row] for row in auth['coefficient_matrix']]);ym=S.Matrix([S.Rational(x) for x in auth['rhs']])
if A!=Am or y!=ym or [list(x) for x in labels]!=auth['columns']:raise RuntimeError('Independent coefficient recurrence disagrees')
print('independent 52x30 coefficient recurrence agrees',flush=True)
# Left-kernel rows from exact rational domain arithmetic, independently checked.
W=DomainMatrix.from_Matrix(A.T).convert_to(S.QQ).nullspace().to_Matrix()
chosen=None
for row in W.tolist():
 v=S.Matrix([row]);product=(v*y)[0]
 if product:
  denom=S.ilcm(*[x.q for x in row]);ints=[int(x*denom) for x in row];g=reduce(math.gcd,ints)
  ints=[x//g for x in ints]
  if next(x for x in ints if x)<0:ints=[-x for x in ints]
  chosen=S.Matrix([ints]);break
if chosen is None:raise RuntimeError('No inconsistency certificate')
if chosen*A!=S.zeros(1,A.cols):raise RuntimeError('Left-kernel witness failed')
value=(chosen*y)[0]
if not value:raise RuntimeError('Witness does not reject target')
# Separate polynomial operator sanity check with both input components.
P=S.Matrix([1-2*t+t**3,2+t**2]);raw=Delta.as_expr()*P.diff(t)+(S.Matrix([[z.as_expr() for z in row] for row in Ns])-Delta.diff().as_expr()*S.eye(2))*P
coeffvec=S.Matrix([S.Poly(raw[i],t).nth(n) for i in range(2) for n in range(26)])
inputvec=S.Matrix([S.Poly(P[j],t).nth(k) for j,k in labels])
if coeffvec!=A*inputvec:raise RuntimeError('Polynomial operator check failed')
# Operator mutations must not satisfy the same certificate equation.
mutations={}
for name,mut in {
 'omit_denominator_derivative':S.Matrix([[coeff(Ns[i][j],n-k)+k*coeff(Delta,n-k+1)*int(i==j) for j,k in labels] for i in range(2) for n in range(26)]),
 'transpose_compact_connection':S.Matrix([[coeff(Ns[j][i],n-k)+(2*k-n-1)*coeff(Delta,n-k+1)*int(i==j) for j,k in labels] for i in range(2) for n in range(26)])}.items():
 row=chosen*mut
 if row==S.zeros(1,A.cols):raise RuntimeError('Mutation not detected: '+name)
 j=next(j for j,x in enumerate(row) if x)
 mutations[name]={'column':j,'value':str(row[j])}
rankA=A.cols-(DomainMatrix.from_Matrix(A).convert_to(S.QQ).nullspace().shape[0])
if rankA!=30:raise RuntimeError('Unexpected coefficient rank')
out=Path(sys.argv[1])
if out.exists():raise RuntimeError('Fresh output required')
out.parent.mkdir(parents=True,exist_ok=False)
certificate={'row_labels':[[i,n] for i in range(2) for n in range(26)],'witness':[str(x) for x in list(chosen)],'witness_times_A':'zero','witness_times_rhs':str(value)}
(out.parent/'left-null-certificate.json').write_text(json.dumps(certificate,indent=2)+'\n',encoding='utf-8')
result={'status':'PASS_INDEPENDENT_FIRST_JET_SYSTEM_OBSTRUCTION','executor':'mixed_checker AI worker','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-start,'python':sys.version,'sympy':S.__version__,'packet_sha256':expected,'author_system_sha256':hashlib.sha256(author.read_bytes()).hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'matrix_shape':list(A.shape),'coefficient_rank':rankA,'augmented_rank':rankA+1,'independent_recurrence':'A[(i,n),(j,k)] = coeff(Nij,n-k)+(2k-n-1)*coeff(Delta,n-k+1)*deltaij','witness_times_rhs':str(value),'certificate_sha256':hashlib.sha256((out.parent/'left-null-certificate.json').read_bytes()).hexdigest(),'mutations':mutations,'scope':'The supplied K=(P0,P1)/Delta family with degrees15/13 is inconsistent at a=3,v=2. The full mixed-current identity and completeness of a larger rational family require their own argument; not inferred from ranks or specialization. No claim excluding arbitrary physical-cover currents.'}
out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))

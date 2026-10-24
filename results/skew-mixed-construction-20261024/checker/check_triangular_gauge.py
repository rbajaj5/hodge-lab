"""Independent coefficient-field check of a new two-row triangular gauge family.
No source cancellation or rational solvability claim is made.
"""
from pathlib import Path
import datetime, hashlib, json, sys, time
import sympy as S
start=time.monotonic()
root=Path(__file__).resolve().parents[3]
packet=root/'results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'
expected='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
if hashlib.sha256(packet.read_bytes()).hexdigest()!=expected:raise RuntimeError('Source hash mismatch')
data=json.loads(packet.read_text(encoding='utf-8'))
a,b,c,d,v,t=S.symbols('a b c d v t'); loc={str(x):x for x in [a,b,c,d,v,t]}
M={x:S.Matrix([[S.sympify(z,locals=loc) for z in row] for row in data['connection'][str(x)]]) for x in [a,b,c,d]}
zero=S.zeros(2);checks={}
def check(name, expr):
    value=expr.applyfunc(S.cancel) if isinstance(expr,S.MatrixBase) else S.cancel(expr)
    if value!=(S.zeros(*value.shape) if isinstance(value,S.MatrixBase) else 0):raise RuntimeError(name+': '+str(value))
    checks[name]='zero'
    print(name+' PASS',flush=True)
check('coefficient_scaling',a*M[a]+b*M[b]+c*M[c]+d*M[d]+S.Rational(5,6)*S.eye(2))
check('fibre_scaling',3*a*M[a]+2*b*M[b]+c*M[c]+S.diag(1,2))
check('fibre_translation',3*a*M[b]+2*b*M[c]+c*M[d]-S.Matrix([[0,-1],[0,0]]))
C=t*(1-t*t)/7;D=1+t**6;Cp=S.diff(C,t);Dp=S.diff(D,t)
w=Cp*C-2*t*v*Dp;s=C*Dp
F=[3*a*w,S.cancel((2*t*v*w+3*a*s-v*C*C)/t),C*C]
sub={b:t*v,c:C,d:D}
N=[M[a].subs(sub),t*M[b].subs(sub),(v*M[b]+Cp*M[c]+Dp*M[d]).subs(sub)]
expected_matrix=S.Matrix([[-w,-s],[0,-2*w]])
check('physical_tangent_connection',sum((x*n for x,n in zip(F,N)),zero)-expected_matrix)
check('c_parameter_tangency',w*C+2*s*t*v-Cp*F[2])
check('d_parameter_tangency',s*C-Dp*F[2])
divF=sum(S.diff(x,q) for x,q in zip(F,[a,v,t]))
mu0=S.factor(S.cancel(divF-w));mu1=S.factor(S.cancel(divF-2*w))
# Independent scalar jets expose both rows without assuming a source identity.
h0,h1,h0a,h0v,h0t,h1a,h1v,h1t=S.symbols('h0 h1 h0a h0v h0t h1a h1v h1t')
row0=sum(x*j for x,j in zip(F,[h0a,h0v,h0t]))+mu0*h0-s*h1
row1=sum(x*j for x,j in zip(F,[h1a,h1v,h1t]))+mu1*h1
point={a:S.Integer(3),v:S.Integer(2),t:S.Integer(2)}
controls={'omit_translation_coupling':S.cancel((-s).subs(point)),'wrong_fibre_scaling_sign':S.cancel((2*w).subs(point))}
if any(x==0 for x in controls.values()):raise RuntimeError('Mutation not detected')
out=Path(sys.argv[1])
if out.exists():raise RuntimeError('Fresh output required')
out.parent.mkdir(parents=True,exist_ok=False)
result={'status':'PASS_TRIANGULAR_FAMILY_ONLY','executor':'mixed_checker AI worker','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-start,'python':sys.version,'sympy':S.__version__,'packet_sha256':expected,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'checks':checks,'w':str(S.factor(w)),'s':str(S.factor(s)),'F':[str(S.factor(x)) for x in F],'connection_matrix':[list(map(str,expected_matrix.row(i))) for i in range(2)],'mu0':str(mu0),'mu1':str(mu1),'full_row0':str(row0),'full_row1':str(row1),'mutation_witnesses':{k:str(x) for k,x in controls.items()},'scope':'A new mixed-direction triangular two-row current family. h0,h1 remain unknown rational functions. All derivative slots retained. This does not cancel R2, prove trace freedom, or give a primitive.'}
out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))

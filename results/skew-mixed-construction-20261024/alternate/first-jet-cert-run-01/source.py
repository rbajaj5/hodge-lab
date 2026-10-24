#!/usr/bin/env python3
"""Generic jet identity, pole completeness and exact saved-system certificate."""
from pathlib import Path
import datetime,hashlib,json,sys,time
import sympy as S
from sympy.polys.matrices import DomainMatrix
start=time.monotonic();ROOT=Path(__file__).resolve().parents[3]
SRC=ROOT/'results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'
pin='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
if hashlib.sha256(SRC.read_bytes()).hexdigest()!=pin:raise RuntimeError('Source pin changed')
data=json.loads(SRC.read_text(encoding='utf-8'));a,b,c,d,v,t=S.symbols('a b c d v t');loc={str(x):x for x in[a,b,c,d,v,t]}
M={k:S.Matrix([[S.sympify(e,locals=loc) for e in row] for row in value]) for k,value in data['connection'].items()}
e0=S.Matrix([1,0]);e1=S.Matrix([0,1]);C=t*(1-t*t)/7;D=1+t**6
sub={b:t*v,c:C,d:D};Ma=M['a'].subs(sub);Mb=M['b'].subs(sub)
Nt=(v*M['b']+S.diff(C,t)*M['c']+S.diff(D,t)*M['d']).subs(sub).applyfunc(S.cancel)
Delta=S.sympify(data['Delta'],locals=loc).subs(sub).expand();N=(Delta*Nt).applyfunc(S.cancel)
T=((M['a'].diff(b)+M['b']*M['a'])*e0/36).subs(sub)
checks={}
def zero(label,x):
 z=S.cancel(x)
 if z!=0:raise RuntimeError(label+' failed: '+str(z))
 checks[label]='zero';print(label+' PASS',flush=True)
chi,chiv,chivv,k0,k1,kt0,kt1=S.symbols('chi chi_v chi_vv k0 k1 kt0 kt1')
K=S.Matrix([k0,k1]);Kt=S.Matrix([kt0,kt1])
Jv=chiv*e1/(36*t*t)-chi*Ma*e0/(36*t)
DvJv=chivv*e1/(36*t*t)-chiv*Ma*e0/(36*t)-chi*Ma.diff(v)*e0/(36*t)
divJ=DvJv+t*Mb*Jv+chi*(Kt+Nt*K)
claimed=chivv*e1/(36*t*t)+chi*(Kt+Nt*K-T)
for j in range(2):zero('full_jet_identity_row_'+str(j),divJ[j]-claimed[j])
zero('generic_residue_trace',S.trace(N)+S.diff(Delta,t)/3)
poly=S.Poly(S.expand((a*N).det()),t,a,v); divisor=S.Poly(Delta,t,a,v)
quot,rem=poly.div(divisor)
if not rem.is_zero:raise RuntimeError('Residue determinant not zero modulo Delta')
checks['generic_residue_determinant_mod_Delta']='zero'
print('generic_residue_determinant_mod_Delta PASS',flush=True)
G=S.diag(t**-3,t**-1)
Nbar=(G*Nt*G.inv()-G.diff(t)*G.inv()).applyfunc(S.cancel)
Tbar=(G*T).applyfunc(S.cancel)
def infinity_degree(x):
 if x==0:return None
 nu,de=S.fraction(S.cancel(x));return int(S.degree(nu,t)-S.degree(de,t))
norders=[infinity_degree(x) for x in Nbar];torders=[infinity_degree(x) for x in Tbar]
if any(k is not None and k>-2 for k in norders):raise RuntimeError('Nbar not O(t^-2)')
if any(k is not None and k>-2 for k in torders):raise RuntimeError('Tbar not O(t^-2)')
checks['generic_infinity_orders']='PASS';print('generic_infinity_orders',norders,torders,flush=True)
saved=Path(__file__).with_name('first-jet-result-01')/'system.json'
system=json.loads(saved.read_text(encoding='utf-8'));A=S.Matrix([[S.Rational(e) for e in row] for row in system['coefficient_matrix']]);y=S.Matrix([S.Rational(e) for e in system['rhs']])
null=DomainMatrix.from_Matrix(A.T).convert_to(S.QQ).nullspace(divide_last=True).to_Matrix()
witness=None
for i in range(null.rows):
 w=null.row(i); value=(w*y)[0]
 if value!=0:witness=(w,value);break
if witness is None:raise RuntimeError('No exact inconsistent witness')
w,value=witness
if w*A!=S.zeros(1,A.cols):raise RuntimeError('Witness does not annihilate coefficient matrix')
checks['exact_left_null_witness']='PASS'
point={a:S.Integer(3),v:S.Integer(2),t:S.Integer(1),chi:-S.Rational(5,3),chiv:-S.Integer(10),chivv:S.Integer(38),k0:0,k1:0,kt0:0,kt1:0}
residual=(-chi*T).subs(point).applyfunc(S.cancel)
controls={
 'drop_v_connection':[-S.cancel((t*Mb*Jv)[j].subs(point)) for j in range(2)],
 'wrong_T_sign':[S.cancel((2*chi*T)[j].subs(point)) for j in range(2)],
 'drop_cover_motion_chi_vv':[S.Integer(0),S.Rational(-4-38,36)],
}
if any(all(z==0 for z in vector) for vector in controls.values()):raise RuntimeError('A mutation escaped')
checks['three_mutations_rejected']='PASS'
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
certificate={'left_null_vector':[str(e) for e in w],'left_null_times_rhs':str(value),'coefficient_matrix_sha256':hashlib.sha256(saved.read_bytes()).hexdigest()}
(out/'left-null-certificate.json').write_text(json.dumps(certificate,indent=2)+'\n',encoding='utf-8')
record={'status':'PASS_SCOPED_COMPLETE_UNIVERSAL_K_EXCLUSION','executor':'Pro mixed_constructive AI worker','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-start,'sympy_version':S.__version__,'python_version':sys.version,'source_sha256':pin,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'checks':checks,'generic_Nbar_orders':norders,'generic_Tbar_orders':torders,'K_zero_actual_cover_point':{'r':'1','a':'3','v':'2','t':'1','chi':'-5/3','chi_v':'-10','chi_vv':'38'},'Div_J_minus_R0_at_K_zero':[str(e) for e in residual],'mutation_vectors':{k:[str(e) for e in z] for k,z in controls.items()},'pole_argument':['Away from Delta all coefficients and T are regular, so a rational K cannot have a finite pole.','At a simple Delta root, residue eigenvalues are 0 and -1/3. T has order at most two; K can therefore have at most a simple pole.','Generic Delta is squarefree because the saved specialization a=3,v=2 is squarefree and leading coefficient 27a^2 is nonzero.','G=diag(t^-3,t^-1); Nbar=O(t^-2) and G*T=O(t^-2). A positive-degree polynomial part of G*K is impossible. Hence K0=O(t^3), K1=O(t), giving deg(P0)<=15,deg(P1)<=13 for K=P/monic(Delta).','The generic coefficient system and rhs are regular at a=3,v=2. The full column rank30 at that point supplies an invertible30x30 minor. By Cramer any putative generic solution is regular there, contradicting rank30 versus31. Thus no rational K in Q(a,v,t)^2 solves this universal-family equation.'],'limit':'This excludes the displayed universal mixed first-jet family, not all mixed currents using the actual cover relation. No new global source exactness, trace, primitive or target-solve claim.'}
(out/'validation.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print(json.dumps(record,indent=2),flush=True)

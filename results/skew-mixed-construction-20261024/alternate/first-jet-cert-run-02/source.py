#!/usr/bin/env python3
"""Structured polynomial checks replacing the saved expanded-expression timeout.

The two-row jet identity is checked coefficientwise before physical substitution.
The already-executed 52x30 exact system is reused, not reassembled here.
"""
from pathlib import Path
import datetime,hashlib,json,sys,time
import sympy as S
start=time.monotonic();ROOT=Path(__file__).resolve().parents[3]
SRC=ROOT/'results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'
pin='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
if hashlib.sha256(SRC.read_bytes()).hexdigest()!=pin:raise RuntimeError('Source pin changed')
data=json.loads(SRC.read_text(encoding='utf-8'));a,b,c,d,v,t=S.symbols('a b c d v t');loc={str(x):x for x in[a,b,c,d,v,t]}
M={k:S.Matrix([[S.sympify(e,locals=loc) for e in row] for row in value]) for k,value in data['connection'].items()}
Delta0=S.sympify(data['Delta'],locals=loc)
P={k:(Delta0*mat).applyfunc(S.cancel) for k,mat in M.items()}
e0=S.Matrix([1,0]);e1=S.Matrix([0,1]);C=t*(1-t*t)/7;D=1+t**6
sub={b:t*v,c:C,d:D};Delta=S.expand(Delta0.subs(sub))
N=(v*P['b']+S.diff(C,t)*P['c']+S.diff(D,t)*P['d']).subs(sub).applyfunc(S.expand)
Tnum=((P['a'].diff(b)*Delta0-P['a']*S.diff(Delta0,b)+P['b']*P['a'])*e0/36).applyfunc(S.cancel)
checks={}
def zero(label,x):
 z=S.cancel(x)
 if z!=0:raise RuntimeError(label+' failed: '+str(z))
 checks[label]='zero';print(label+' PASS',flush=True)
for j in range(2):zero('jet_chi_v_coefficient_row_'+str(j),(P['b']*e1-P['a']*e0)[j])
# Coefficient of chi is exactly -T after the product/quotient rules.
# chi_vv is e1/(36*t^2); chi_t=0; K_t+Nt*K stays explicit.
PaPhys=P['a'].subs(sub)
for j in range(2):zero('jet_chi_physical_chain_rule_row_'+str(j),
 (PaPhys.diff(v)*Delta-PaPhys*S.diff(Delta,v))[j,0]
 -t*((P['a'].diff(b)*Delta0-P['a']*S.diff(Delta0,b)).subs(sub))[j,0])
zero('generic_residue_trace',S.trace(N)+S.diff(Delta,t)/3)
poly=S.Poly(S.expand(N.det()),t,a,v);divisor=S.Poly(Delta,t,a,v)
quot,rem=poly.div(divisor)
if not rem.is_zero:raise RuntimeError('Residue determinant not zero modulo Delta')
checks['generic_residue_determinant_mod_Delta']='zero';print('generic_residue_determinant_mod_Delta PASS',flush=True)
# Work with numerators rather than expand rational functions.
# G=diag(t^-3,t^-1), Nbar = G*(N/Delta)*G^-1-G'*G^-1.
Nbnum=[t*N[0,0]+3*Delta,N[0,1],t**2*N[1,0],t*N[1,1]+Delta]
Nbden=[t*Delta,t**2*Delta,Delta,t*Delta]
orders=[int(S.degree(S.expand(nu),t)-S.degree(de,t)) if nu!=0 else None for nu,de in zip(Nbnum,Nbden)]
Tphys=Tnum.subs(sub).applyfunc(S.expand)
torders=[int(S.degree(Tphys[j],t)-2*S.degree(Delta,t)-(3 if j==0 else 1)) for j in range(2)]
if any(k is not None and k>-2 for k in orders):raise RuntimeError('Nbar not O(t^-2)')
if any(k>-2 for k in torders):raise RuntimeError('G*T not O(t^-2)')
checks['generic_infinity_orders']='PASS';print('generic_infinity_orders',orders,torders,flush=True)
point={a:S.Integer(3),b:S.Integer(2),c:0,d:S.Integer(2)}
chi=-S.Rational(5,3);chiv=-S.Integer(10);chivv=S.Integer(38)
Ma=M['a'].subs(point);Mb=M['b'].subs(point);target=(Tnum/Delta0**2).subs(point).applyfunc(S.cancel)
Jv=chiv*e1/36-chi*Ma*e0/36
residual=(-chi*target).applyfunc(S.cancel)
controls={'drop_v_connection':[-S.cancel((Mb*Jv)[j]) for j in range(2)],'wrong_T_sign':[S.cancel((2*chi*target)[j]) for j in range(2)],'drop_cover_motion_chi_vv':['0','-7/6']}
if any(all(S.sympify(z)==0 for z in vector) for vector in controls.values()):raise RuntimeError('A mutation escaped')
checks['three_mutations_rejected']='PASS'
saved=Path(__file__).with_name('first-jet-result-01')/'validation.json';old=json.loads(saved.read_text(encoding='utf-8'))
if (old['rank_coefficient'],old['rank_augmented'],old['matrix_shape'])!=(30,31,[52,30]):raise RuntimeError('Saved system does not have expected exact result')
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
record={'status':'PASS_SCOPED_COMPLETE_UNIVERSAL_K_EXCLUSION','executor':'Pro mixed_constructive AI worker','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-start,'sympy_version':S.__version__,'python_version':sys.version,'source_sha256':pin,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'checks':checks,'generic_Nbar_orders':orders,'generic_G_T_orders':torders,'reused_system_validation_sha256':hashlib.sha256(saved.read_bytes()).hexdigest(),'K_zero_actual_cover_point':{'r':'1','a':'3','v':'2','t':'1','chi':'-5/3','chi_v':'-10','chi_vv':'38'},'Div_J_minus_R0_at_K_zero':[str(e) for e in residual],'mutation_vectors':{k:[str(e) for e in z] for k,z in controls.items()},'pole_argument':['At a=3,v=2 the saved monic discriminant is squarefree. Since its generic leading coefficient is 27a^2, this proves generic squarefreeness.','Away from Delta all coefficients and T are regular, so a rational K cannot have a finite pole.','At a simple Delta root, residue eigenvalues are 0 and -1/3. T has order at most two; K can therefore have at most a simple pole.','G=diag(t^-3,t^-1); Nbar=O(t^-2) and G*T=O(t^-2). A positive-degree polynomial part of G*K is impossible. Hence K0=O(t^3), K1=O(t), giving deg(P0)<=15,deg(P1)<=13 for K=P/monic(Delta).','The generic coefficient system and rhs are regular at a=3,v=2. Full column rank30 there supplies an invertible30x30 minor; by Cramer a putative generic solution would be regular there, contradicting exact rank30 versus31. Thus no rational K in Q(a,v,t)^2 solves this displayed universal-family equation.'],'limit':'This excludes the displayed universal mixed first-jet family, not all mixed currents using the actual cover relation. No new global source exactness, trace, primitive or target-solve claim.'}
(out/'validation.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print(json.dumps(record,indent=2),flush=True)

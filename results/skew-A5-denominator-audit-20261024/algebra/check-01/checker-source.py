"""Minimal new order-five identities; prior support/module proof reused.
No numerical search, old determinant replay or lower-sector restriction.
"""
import argparse,datetime,hashlib,json,pathlib,sys,time
import sympy as s
p=argparse.ArgumentParser()
p.add_argument('--repo',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parents[3])
p.add_argument('--output',required=True,type=pathlib.Path)
args=p.parse_args()
if args.output.exists():raise SystemExit('fresh output required')
args.output.mkdir(parents=True)
started=time.monotonic();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=args.repo/'results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'
pin='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
if sha(source)!=pin:raise ValueError('literal source changed')
base=args.repo/'results/skew-A-denominator-audit-20261024/algebra/check-02/result'
validation_path=base/'validation.json';injection_path=base/'tangent-injection.json'
if sha(validation_path)!='1d45f2e5e254c7b6c8aa24e3aeee106a5756c5a0f9407cbb9d426ef2f289367c':raise ValueError('support theorem validation changed')
if sha(injection_path)!='047d04f6d9ee1c70000146506fa2ada26c456fd1dd9de5b2d70e4be811ce828b':raise ValueError('tangent injection changed')
prior4_path=args.repo/'results/skew-A4-denominator-audit-20261024/algebra/check-01/result/validation.json'
prior4=json.loads(prior4_path.read_text(encoding='utf-8'))
if prior4['source_sha256']!=pin or prior4['script_sha256']!='7ca72b6082aeb6cd75a75062b24068a1520345e08c46ebe179284e79acd11364':raise ValueError('A4 dependency changed')
pv=json.loads(validation_path.read_text(encoding='utf-8'))
a,b,c,d,r,v,t=s.symbols('a b c d r v t');loc={str(q):q for q in (a,b,c,d,r,v,t)}
R=s.Matrix([[s.cancel(s.sympify(q,locals=loc)) for q in row] for row in pv['a_residue']])
Tr,Tv,ell=[s.sympify(pv[key],locals=loc) for key in ('T_r','T_v','ell')]
checks=[]
def zero(name,expr):
    items=list(expr) if isinstance(expr,s.MatrixBase) else [expr]
    if any(s.cancel(q)!=0 for q in items):raise ArithmeticError(name)
    checks.append(name);print('PASS '+name,flush=True)
determinant=s.factor((R-5*s.eye(2)).det())
tau=s.expand(s.diff(Tr,r)+s.diff(Tv,v)-5*ell)
zero('new order-six residue determinant',determinant-s.Rational(80,3))
zero('new tau5 derived from divergence',tau-(-5*r**7+18*r))
z=s.symbols('z');AA=s.Function('A')(z);PP=s.Function('P')(z)
zero('power-five quotient derivative',s.diff(PP/AA**5,z)-(s.diff(PP,z)/AA**5-5*PP*s.diff(AA,z)/AA**6))
U=s.symbols('U');DP=s.symbols('DP0:6');Q=s.symbols('Q0:6');W5=s.symbols('W5')
raw=U**5*(DP[0]+sum(DP[j]/U**j-j*Q[j]/U**(j+1) for j in range(1,6)))
scaled=U**5*DP[0]+U**4*DP[1]-U**3*Q[1]+U**3*DP[2]-2*U**2*Q[2]+U**2*DP[3]-3*U*Q[3]+U*DP[4]-4*Q[4]+DP[5]-5*Q[5]/U
zero('complete six-sector scaled equation',raw-scaled)
reduced=U**5*DP[0]+U**4*DP[1]-U**3*Q[1]+U**3*DP[2]-2*U**2*Q[2]+U**2*DP[3]-3*U*Q[3]+U*DP[4]-4*Q[4]+W5
zero('replace only highest tangent sector',raw.subs(DP[5],W5+5*Q[5]/U)-reduced)
w0,w1=s.symbols('w0 w1');W=s.Matrix([w0,w1])
normal=s.Matrix([w0/4-c*w1/(104*b),s.Rational(3,13)*w1])
zero('coupled next-pole inverse',(R-4*s.eye(2))*normal+W)

# All lower sectors are kept, byte-reusing the accepted tangent module.
old=json.loads(injection_path.read_text(encoding='utf-8'));basis=old['original_basis'];nb=len(basis)
columns=[]
for sector in range(5):
    for j,key in enumerate(basis):columns.append({'sector':sector,'kind':'unrestricted','basis':key,'entries':[[sector*nb+j,1]]})
for col in old['columns']:
    columns.append({'sector':5,'kind':col['kind'],'row':col['row'],'monomial':col['monomial'],
        'entries':[[5*nb+i,q] for i,q in col['entries']]})
if nb!=702 or len(columns)!=3804 or any(sum(c['sector']==j for c in columns)!=702 for j in range(5)):
    raise ArithmeticError('lower-sector count or dimension')
checks.append('all 3510 lower coefficients retained')
joint={'shape':[4212,3804],'original_order':'P0 through P5; then original_basis. Sector j means Pj/A^j.',
    'original_basis':basis,'columns':columns,'imported_top_injection_sha256':sha(injection_path),
    'scope':'Only P5 tangent. P0 through P4 unrestricted. No operator-kernel or solution claim.'}
map_path=args.output/'highest-pole-injection.json'
map_path.write_text(json.dumps(joint,indent=2)+'\n',encoding='utf-8')
controls=[]
wrong_tau=s.expand(s.diff(Tr,r)+s.diff(Tv,v)-4*ell-tau)
if wrong_tau==0:raise ArithmeticError('wrong power mutation survived')
controls.append({'name':'quotient factor4 instead of5','difference':str(wrong_tau)})
bad=(normal[0]-w0/4).subs({b:1,c:1,w1:1})
if bad==0:raise ArithmeticError('row-coupling omission survived')
controls.append({'name':'omit off-diagonal coupling','witness':str(bad)})
wrong_lower=reduced+Q[4]
bad=(wrong_lower-reduced).subs(Q[4],1)
if bad==0:raise ArithmeticError('lower P4 order mutation survived')
controls.append({'name':'lower P4 quotient factor3 instead of4','difference_at_Q4_1':str(bad)})
report={'status':'PASS_NEW_A5_HIGHEST_POLE_AND_FULL_SCALED_EQUATION',
    'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':time.monotonic()-started,
    'python':sys.version,'sympy':s.__version__,'source_sha256':pin,'script_sha256':sha(pathlib.Path(__file__)),
    'prior_validation_sha256':sha(validation_path),'prior_injection_sha256':sha(injection_path),'prior_A4_validation_sha256':sha(prior4_path),
    'checks':checks,'mutations':controls,'det_R_minus_5I':str(determinant),'tau5':str(tau),'ell':str(ell),
    'top_operator':'W5=[T_r*partial_r+T_v*partial_v+(-5*r^7+18*r)*I+ell*A*M_a+t*T_v*M_b]*h+(partial_t+N_t)*k',
    'full_scaled_equation':'A^5*Div_N(P0)+A^4*Div_N(P1)-A^3*Q1+A^3*Div_N(P2)-2*A^2*Q2+A^2*Div_N(P3)-3*A*Q3+A*Div_N(P4)-4*Q4+W5=A^5*S',
    'normal_definition':'Qj=A_r*Pjr+A_v*Pjv','next_pole_condition':'(R_a-4I)*Q4+W5|A=0=0',
    'next_pole_normal_target':['W5_0/4-c*W5_1/(104*b)','3*W5_1/13'],
    'dimensions':{'scalar_B':117,'sector':702,'top_h':60,'top_k':234,'top_necessary':294,'joint_original':4212,'unrestricted_lower':3510,'joint_necessary':3804},
    'injection_sha256':sha(map_path),
    'why_old_exclusion_is_not_imposed':'The lower current now solves S-Div_N(P5/A^5), not S. Prior exclusion applies if P5=0; it does not eliminate possible cancellation between levels.',
    'domain':'Characteristic zero; physical open r*A*Delta!=0. Pole comparison uses generic prime smooth A=0 away from b*Delta=0. Completed divisor and source-regularity arguments imported, not rerun.',
    'scope':'No numerical search, lower-pole refinement, exact kernel, rank upper bound, full-source cancellation or primitive claim.'}
(args.output/'validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'checks':len(checks),'controls':len(controls),'seconds':report['seconds']},indent=2),flush=True)

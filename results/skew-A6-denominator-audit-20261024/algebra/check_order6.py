"""New A^-6 structural identities only; accepted support/module proof reused.
No old determinant replay, matrix search or lower-sector restriction.
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
vp=base/'validation.json';ip=base/'tangent-injection.json'
if sha(vp)!='1d45f2e5e254c7b6c8aa24e3aeee106a5756c5a0f9407cbb9d426ef2f289367c':raise ValueError('support proof receipt changed')
if sha(ip)!='047d04f6d9ee1c70000146506fa2ada26c456fd1dd9de5b2d70e4be811ce828b':raise ValueError('top injection changed')
p5=args.repo/'results/skew-A5-denominator-audit-20261024/algebra/check-01/result/validation.json'
old5=json.loads(p5.read_text(encoding='utf-8'))
if old5['source_sha256']!=pin or old5['script_sha256']!='bad3f26c1f1f07c944024b6acdfa91f0c4953951a3c8f434ebd66b24850e8d8c':raise ValueError('A5 dependency changed')
prior=json.loads(vp.read_text(encoding='utf-8'))
a,b,c,d,r,v,t=s.symbols('a b c d r v t');loc={str(q):q for q in (a,b,c,d,r,v,t)}
R=s.Matrix([[s.cancel(s.sympify(q,locals=loc)) for q in row] for row in prior['a_residue']])
Tr,Tv,ell=[s.sympify(prior[key],locals=loc) for key in ('T_r','T_v','ell')]
checks=[]
def zero(name,expr):
    items=list(expr) if isinstance(expr,s.MatrixBase) else [expr]
    if any(s.cancel(q)!=0 for q in items):raise ArithmeticError(name)
    checks.append(name);print('PASS '+name,flush=True)
determinant=s.factor((R-6*s.eye(2)).det())
tau=s.expand(s.diff(Tr,r)+s.diff(Tv,v)-6*ell)
zero('new order-seven residue determinant',determinant-38)
zero('new tau6 from divergence',tau-(-8*r**7+21*r))
z=s.symbols('z');AA=s.Function('A')(z);PP=s.Function('P')(z)
zero('power-six quotient derivative',s.diff(PP/AA**6,z)-(s.diff(PP,z)/AA**6-6*PP*s.diff(AA,z)/AA**7))
U=s.symbols('U');DP=s.symbols('DP0:7');Q=s.symbols('Q0:7');W6=s.symbols('W6')
raw=U**6*(DP[0]+sum(DP[j]/U**j-j*Q[j]/U**(j+1) for j in range(1,7)))
explicit=U**6*DP[0]+U**5*DP[1]-U**4*Q[1]+U**4*DP[2]-2*U**3*Q[2]+U**3*DP[3]-3*U**2*Q[3]+U**2*DP[4]-4*U*Q[4]+U*DP[5]-5*Q[5]+DP[6]-6*Q[6]/U
zero('complete seven-sector scaled equation',raw-explicit)
reduced=U**6*DP[0]+U**5*DP[1]-U**4*Q[1]+U**4*DP[2]-2*U**3*Q[2]+U**3*DP[3]-3*U**2*Q[3]+U**2*DP[4]-4*U*Q[4]+U*DP[5]-5*Q[5]+W6
zero('replace only P6 tangent sector',raw.subs(DP[6],W6+6*Q[6]/U)-reduced)
w0,w1=s.symbols('w0 w1');W=s.Matrix([w0,w1])
normal=s.Matrix([w0/5-c*w1/(160*b),s.Rational(3,16)*w1])
zero('coupled next-pole inverse',(R-5*s.eye(2))*normal+W)

old=json.loads(ip.read_text(encoding='utf-8'));basis=old['original_basis'];nb=len(basis);columns=[]
for sector in range(6):
    for j,key in enumerate(basis):columns.append({'sector':sector,'kind':'unrestricted','basis':key,'entries':[[sector*nb+j,1]]})
for col in old['columns']:
    columns.append({'sector':6,'kind':col['kind'],'row':col['row'],'monomial':col['monomial'],
        'entries':[[6*nb+i,q] for i,q in col['entries']]})
if nb!=702 or len(columns)!=4506 or any(sum(c['sector']==j for c in columns)!=702 for j in range(6)):
    raise ArithmeticError('lower-sector preservation or dimension')
checks.append('all 4212 lower coefficients retained')
joint={'shape':[4914,4506],'original_order':'P0 through P6; then original_basis. Sector j represents Pj/A^j.',
    'original_basis':basis,'columns':columns,'imported_top_injection_sha256':sha(ip),
    'scope':'Only P6 tangent. P0 through P5 unrestricted. No solution or operator-kernel claim.'}
mp=args.output/'highest-pole-injection.json'
mp.write_text(json.dumps(joint,indent=2)+'\n',encoding='utf-8')
controls=[]
wrong_tau=s.expand(s.diff(Tr,r)+s.diff(Tv,v)-5*ell-tau)
if wrong_tau==0:raise ArithmeticError('wrong pole-order control survived')
controls.append({'name':'quotient factor5 instead of6','difference':str(wrong_tau)})
bad=(normal[0]-w0/5).subs({b:1,c:1,w1:1})
if bad==0:raise ArithmeticError('missing row coupling survived')
controls.append({'name':'omit off-diagonal next-pole term','witness':str(bad)})
bad=((reduced+Q[5])-reduced).subs(Q[5],1)
if bad==0:raise ArithmeticError('lower pole derivative mutation survived')
controls.append({'name':'lower P5 quotient factor4 instead of5','difference_at_Q5_1':str(bad)})
report={'status':'PASS_NEW_A6_HIGHEST_POLE_AND_FULL_SCALED_EQUATION',
    'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':time.monotonic()-started,
    'python':sys.version,'sympy':s.__version__,'source_sha256':pin,'script_sha256':sha(pathlib.Path(__file__)),
    'prior_validation_sha256':sha(vp),'prior_injection_sha256':sha(ip),'prior_A5_validation_sha256':sha(p5),
    'checks':checks,'mutations':controls,'det_R_minus_6I':str(determinant),'tau6':str(tau),'ell':str(ell),
    'top_operator':'W6=[T_r*partial_r+T_v*partial_v+(-8*r^7+21*r)*I+ell*A*M_a+t*T_v*M_b]*h+(partial_t+N_t)*k',
    'full_scaled_equation':'A^6*Div_N(P0)+A^5*Div_N(P1)-A^4*Q1+A^4*Div_N(P2)-2*A^3*Q2+A^3*Div_N(P3)-3*A^2*Q3+A^2*Div_N(P4)-4*A*Q4+A*Div_N(P5)-5*Q5+W6=A^6*S',
    'normal_definition':'Qj=A_r*Pjr+A_v*Pjv','next_pole_condition':'(R_a-5I)*Q5+W6|A=0=0',
    'next_pole_normal_target':['W6_0/5-c*W6_1/(160*b)','3*W6_1/16'],
    'dimensions':{'scalar_B':117,'sector':702,'top_h':60,'top_k':234,'top_necessary':294,'joint_original':4914,'unrestricted_lower':4212,'joint_necessary':4506},
    'injection_sha256':sha(mp),
    'why_old_exclusion_is_not_imposed':'The lower current must solve S-Div_N(P6/A^6), not S. The prior exclusion applies when P6=0 only. No separate lower tangency or secondary projection is justified by it.',
    'domain':'Characteristic zero; physical open r*A*Delta!=0. Pole comparison at generic prime smooth A=0 away from b*Delta=0. Earlier divisor, source-regularity and bounded-module proofs reused without replay.',
    'handoff_use':'Pending receiver confirmation at original freeze; add a separate provenance addendum if use is reported.',
    'scope':'No numerical search, lower-order refinement, exact kernel, rank upper bound, full-source cancellation or primitive claim.'}
(args.output/'validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'checks':len(checks),'controls':len(controls),'seconds':report['seconds']},indent=2),flush=True)

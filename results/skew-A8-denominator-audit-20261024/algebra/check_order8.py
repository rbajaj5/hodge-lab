"""Only new A^-8 identities; completed divisor/module/support results reused.
No old mathematical replay, matrix search, or lower-sector restriction.
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
if sha(source)!=pin:raise ValueError('source bytes changed')
base=args.repo/'results/skew-A-denominator-audit-20261024/algebra/check-02/result'
vp=base/'validation.json';ip=base/'tangent-injection.json'
if sha(vp)!='1d45f2e5e254c7b6c8aa24e3aeee106a5756c5a0f9407cbb9d426ef2f289367c':raise ValueError('support receipt changed')
if sha(ip)!='047d04f6d9ee1c70000146506fa2ada26c456fd1dd9de5b2d70e4be811ce828b':raise ValueError('tangent injection changed')
p7=args.repo/'results/skew-A7-denominator-audit-20261024/algebra/check-01/result/validation.json'
prior7=json.loads(p7.read_text(encoding='utf-8'))
if prior7['source_sha256']!=pin or prior7['script_sha256']!='aca70673f8a5273e56bbe4f60066102678c3a7157199c8fde29415455c7a1cab':raise ValueError('A7 binding changed')
prior=json.loads(vp.read_text(encoding='utf-8'))
a,b,c,d,r,v,t=s.symbols('a b c d r v t');loc={str(q):q for q in (a,b,c,d,r,v,t)}
R=s.Matrix([[s.cancel(s.sympify(q,locals=loc)) for q in row] for row in prior['a_residue']])
Tr,Tv,ell=[s.sympify(prior[key],locals=loc) for key in ('T_r','T_v','ell')]
checks=[]
def zero(name,expr):
    items=list(expr) if isinstance(expr,s.MatrixBase) else [expr]
    if any(s.cancel(q)!=0 for q in items):raise ArithmeticError(name)
    checks.append(name);print('PASS '+name,flush=True)
determinant=s.factor((R-8*s.eye(2)).det())
tau=s.expand(s.diff(Tr,r)+s.diff(Tv,v)-8*ell)
zero('new order-nine residue determinant',determinant-s.Rational(200,3))
zero('new tau8 from divergence',tau-(-14*r**7+27*r))
z=s.symbols('z');AA=s.Function('A')(z);PP=s.Function('P')(z)
zero('power-eight quotient derivative',s.diff(PP/AA**8,z)-(s.diff(PP,z)/AA**8-8*PP*s.diff(AA,z)/AA**9))
U=s.symbols('U');DP=s.symbols('DP0:9');Q=s.symbols('Q0:9');W8=s.symbols('W8')
raw=U**8*(DP[0]+sum(DP[j]/U**j-j*Q[j]/U**(j+1) for j in range(1,9)))
explicit=U**8*DP[0]+U**7*DP[1]-U**6*Q[1]+U**6*DP[2]-2*U**5*Q[2]+U**5*DP[3]-3*U**4*Q[3]+U**4*DP[4]-4*U**3*Q[4]+U**3*DP[5]-5*U**2*Q[5]+U**2*DP[6]-6*U*Q[6]+U*DP[7]-7*Q[7]+DP[8]-8*Q[8]/U
zero('complete nine-sector scaled equation',raw-explicit)
reduced=U**8*DP[0]+U**7*DP[1]-U**6*Q[1]+U**6*DP[2]-2*U**5*Q[2]+U**5*DP[3]-3*U**4*Q[3]+U**4*DP[4]-4*U**3*Q[4]+U**3*DP[5]-5*U**2*Q[5]+U**2*DP[6]-6*U*Q[6]+U*DP[7]-7*Q[7]+W8
zero('substitute only P8 tangent sector',raw.subs(DP[8],W8+8*Q[8]/U)-reduced)
w0,w1=s.symbols('w0 w1');W=s.Matrix([w0,w1])
normal=-(R-7*s.eye(2)).inv()*W
zero('coupled inverse retains both rows',normal-s.Matrix([w0/7-c*w1/(308*b),s.Rational(3,22)*w1]))

old=json.loads(ip.read_text(encoding='utf-8'));basis=old['original_basis'];nb=len(basis);columns=[]
for sector in range(8):
    for j,key in enumerate(basis):columns.append({'sector':sector,'kind':'unrestricted','basis':key,'entries':[[sector*nb+j,1]]})
for col in old['columns']:
    columns.append({'sector':8,'kind':col['kind'],'row':col['row'],'monomial':col['monomial'],
        'entries':[[8*nb+i,q] for i,q in col['entries']]})
if nb!=702 or len(columns)!=5910 or any(sum(col['sector']==j for col in columns)!=702 for j in range(8)):
    raise ArithmeticError('lower-sector preservation or dimension')
checks.append('all 5616 lower coefficients remain unrestricted')
joint={'shape':[6318,5910],'original_order':'P0 through P8; then original_basis. Sector j represents Pj/A^j.',
    'original_basis':basis,'columns':columns,'imported_top_injection_sha256':sha(ip),
    'scope':'Only P8 tangent; P0 through P7 remain free. No operator kernel or solution claim.'}
mp=args.output/'highest-pole-injection.json'
mp.write_text(json.dumps(joint,indent=2)+'\n',encoding='utf-8')
controls=[]
bad=s.expand(s.diff(Tr,r)+s.diff(Tv,v)-7*ell-tau)
if bad==0:raise ArithmeticError('wrong pole order survived')
controls.append({'name':'quotient factor7 instead of8','difference':str(bad)})
bad=s.cancel((normal[0]-w0/7).subs({b:1,c:1,w1:1}))
if bad==0:raise ArithmeticError('off-diagonal omission survived')
controls.append({'name':'omit next-pole off-diagonal term','witness':str(bad)})
bad=((reduced+Q[7])-reduced).subs(Q[7],1)
if bad==0:raise ArithmeticError('wrong lower quotient factor survived')
controls.append({'name':'lower P7 quotient factor6 instead of7','difference_at_Q7_1':str(bad)})
report={'status':'PASS_NEW_A8_HIGHEST_POLE_AND_FULL_SCALED_EQUATION',
    'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':time.monotonic()-started,
    'python':sys.version,'sympy':s.__version__,'source_sha256':pin,'script_sha256':sha(pathlib.Path(__file__)),
    'prior_validation_sha256':sha(vp),'prior_injection_sha256':sha(ip),'prior_A7_validation_sha256':sha(p7),
    'checks':checks,'mutations':controls,'det_R_minus_8I':str(determinant),'tau8':str(tau),'ell':str(ell),
    'top_operator':'W8=[T_r*partial_r+T_v*partial_v+(-14*r^7+27*r)*I+ell*A*M_a+t*T_v*M_b]*h+(partial_t+N_t)*k',
    'full_scaled_equation':'A^8*Div_N(P0)+A^7*Div_N(P1)-A^6*Q1+A^6*Div_N(P2)-2*A^5*Q2+A^5*Div_N(P3)-3*A^4*Q3+A^4*Div_N(P4)-4*A^3*Q4+A^3*Div_N(P5)-5*A^2*Q5+A^2*Div_N(P6)-6*A*Q6+A*Div_N(P7)-7*Q7+W8=A^8*S',
    'normal_definition':'Qj=A_r*Pjr+A_v*Pjv','next_pole_condition':'(R_a-7I)*Q7+W8|A=0=0',
    'next_pole_normal_target':['W8_0/7-c*W8_1/(308*b)','3*W8_1/22'],
    'dimensions':{'scalar_B':117,'sector':702,'top_h':60,'top_k':234,'top_necessary':294,'joint_original':6318,'unrestricted_lower':5616,'joint_necessary':5910},
    'injection_sha256':sha(mp),
    'why_old_exclusion_is_not_imposed':'The lower current now solves S-Div_N(P8/A^8), not S. Prior exclusion applies only when P8=0; it neither imposes lower tangency nor forbids cross-level cancellation.',
    'domain':'Characteristic zero, physical open r*A*Delta!=0. Pole comparison at generic prime smooth A=0 away from b*Delta=0, using unchanged divisor/module/support proofs without replay.',
    'scope':'No numerical search, lower refinement, exact kernel, rank upper bound, full-source cancellation or primitive claim.'}
(args.output/'validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'checks':len(checks),'controls':len(controls),'seconds':report['seconds']},indent=2),flush=True)

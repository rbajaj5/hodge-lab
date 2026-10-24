"""New A^-4 identities only; no search or lower-sector restriction.

The completed A-divisor/tangent/support theorem is imported by byte hashes.
This extends the author's A^3 structural checker to the new pole order.
"""
import argparse,datetime,hashlib,json,pathlib,sys,time
import sympy as s
p=argparse.ArgumentParser()
p.add_argument('--repo',type=pathlib.Path,default=pathlib.Path(__file__).resolve().parents[3])
p.add_argument('--output',required=True,type=pathlib.Path)
args=p.parse_args()
if args.output.exists():raise SystemExit('fresh output directory required')
args.output.mkdir(parents=True)
started=time.monotonic();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
source=args.repo/'results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'
pin='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
if sha(source)!=pin:raise ValueError('source connection pin changed')
prior=args.repo/'results/skew-A-denominator-audit-20261024/algebra/check-02/result'
validation_path=prior/'validation.json';injection_path=prior/'tangent-injection.json'
if sha(validation_path)!='1d45f2e5e254c7b6c8aa24e3aeee106a5756c5a0f9407cbb9d426ef2f289367c':raise ValueError('prior validation changed')
if sha(injection_path)!='047d04f6d9ee1c70000146506fa2ada26c456fd1dd9de5b2d70e4be811ce828b':raise ValueError('prior injection changed')
prior_validation=json.loads(validation_path.read_text(encoding='utf-8'))
if prior_validation['source_sha256']!=pin:raise ValueError('prior/source dependency mismatch')
a,b,c,d,r,v,t=s.symbols('a b c d r v t');loc={str(q):q for q in (a,b,c,d,r,v,t)}
R=s.Matrix([[s.cancel(s.sympify(q,locals=loc)) for q in row] for row in prior_validation['a_residue']])
Tr,Tv,ell=[s.sympify(prior_validation[key],locals=loc) for key in ('T_r','T_v','ell')]
checks=[]
def zero(name,expr):
    items=list(expr) if isinstance(expr,s.MatrixBase) else [expr]
    if any(s.cancel(q)!=0 for q in items):raise ArithmeticError(name)
    checks.append(name);print('PASS '+name,flush=True)
zero('new order-five residue determinant',(R-4*s.eye(2)).det()-s.Rational(52,3))
tau4=-2*r**7+15*r
zero('new tau4 zeroth-order coefficient',s.diff(Tr,r)+s.diff(Tv,v)-4*ell-tau4)
z=s.symbols('z');AA=s.Function('A')(z);PP=s.Function('P')(z)
zero('power-four quotient derivative',s.diff(PP/AA**4,z)-(s.diff(PP,z)/AA**4-4*PP*s.diff(AA,z)/AA**5))
U=s.symbols('U');dp=s.symbols('dp0:5');Q=s.symbols('Q0:5');W4=s.symbols('W4')
raw=U**4*(dp[0]+sum(dp[j]/U**j-j*Q[j]/U**(j+1) for j in range(1,5)))
expected=U**4*dp[0]+U**3*dp[1]-U**2*Q[1]+U**2*dp[2]-2*U*Q[2]+U*dp[3]-3*Q[3]+dp[4]-4*Q[4]/U
zero('complete five-sector scaled product rule',raw-expected)
top_reduced=U**4*dp[0]+U**3*dp[1]-U**2*Q[1]+U**2*dp[2]-2*U*Q[2]+U*dp[3]-3*Q[3]+W4
zero('substitute only top tangent sector',raw.subs(dp[4],W4+4*Q[4]/U)-top_reduced)
w0,w1=s.symbols('w0 w1');W=s.Matrix([w0,w1])
normal_target=s.Matrix([w0/3-c*w1/(60*b),s.Rational(3,10)*w1])
zero('coupled next-pole inverse preserves both rows',(R-3*s.eye(2))*normal_target+W)

# The only change to the imported tangent map is its pole-sector index.
# All four lower sectors are identities; no old secondary projection.
old=json.loads(injection_path.read_text(encoding='utf-8'));basis=old['original_basis'];nb=len(basis)
columns=[]
for sector in range(4):
    for j,key in enumerate(basis):
        columns.append({'sector':sector,'kind':'unrestricted','basis':key,'entries':[[sector*nb+j,1]]})
for col in old['columns']:
    columns.append({'sector':4,'kind':col['kind'],'row':col['row'],'monomial':col['monomial'],
        'entries':[[4*nb+i,q] for i,q in col['entries']]})
if nb!=702 or len(columns)!=3102 or any(sum(q['sector']==j for q in columns)!=702 for j in range(4)):
    raise ArithmeticError('lower-sector preservation or dimension failed')
checks.append('all 2808 lower coefficients preserved in necessary injection')
joint={'shape':[3510,3102],'original_order':'P0,P1,P2,P3,P4; within each sector use original_basis; sector j means Pj/A^j',
    'original_basis':basis,'columns':columns,'imported_top_injection_sha256':sha(injection_path),
    'scope':'Only P4 highest-pole tangency. P0/P1/P2/P3 unrestricted. No matrix search or operator-kernel claim.'}
map_path=args.output/'highest-pole-injection.json'
map_path.write_text(json.dumps(joint,indent=2)+'\n',encoding='utf-8')
mutations=[]
bad=s.expand(s.diff(Tr,r)+s.diff(Tv,v)-3*ell-tau4)
if bad==0:raise ArithmeticError('incorrect quotient power not detected')
mutations.append({'name':'use quotient factor3 instead of4','nonzero_tau_difference':str(bad)})
bad=(normal_target[0]-w0/3).subs({b:1,c:1,w1:1})
if bad==0:raise ArithmeticError('missing row coupling not detected')
mutations.append({'name':'omit off-diagonal next-pole coupling','witness':str(bad)})
bad=(2*U*Q[2]-U*Q[2]).subs({U:2,Q[2]:1})
if bad==0:raise ArithmeticError('wrong lower P2 quotient coefficient not detected')
mutations.append({'name':'use lower P2 quotient factor1 instead of2','nonzero_difference_at_A2_Q2_1':str(bad)})
report={'status':'PASS_NEW_A4_HIGHEST_POLE_AND_FULL_SCALED_EQUATION',
    'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':time.monotonic()-started,
    'python':sys.version,'sympy':s.__version__,'source_sha256':pin,'script_sha256':sha(pathlib.Path(__file__)),
    'prior_validation_sha256':sha(validation_path),'prior_injection_sha256':sha(injection_path),
    'checks':checks,'mutations':mutations,'det_R_minus_4I':'52/3','tau4':str(tau4),'ell':str(ell),
    'top_operator':'W4=[T_r*partial_r+T_v*partial_v+(-2*r^7+15*r)*I+ell*A*M_a+t*T_v*M_b]*h+(partial_t+N_t)*k',
    'full_scaled_equation':'A^4*Div_N(P0)+A^3*Div_N(P1)-A^2*Q1+A^2*Div_N(P2)-2*A*Q2+A*Div_N(P3)-3*Q3+W4=A^4*S',
    'normal_definition':'Qj=A_r*Pjr+A_v*Pjv','next_pole_condition':'(R_a-3I)*Q3+W4|A=0=0',
    'next_pole_normal_target':['W4_0/3-c*W4_1/(60*b)','3*W4_1/10'],
    'dimensions':{'scalar_B':117,'six_component_sector':702,'top_h':60,'top_k':234,'top_necessary':294,
        'joint_original':3510,'unrestricted_lower':2808,'joint_necessary':3102},
    'injection_sha256':sha(map_path),
    'why_lower_exclusion_does_not_transfer':'With nonzero P4 the lower current is required to solve S-Div_N(P4/A^4), not the old source S. The old exclusion applies to P4=0 only; it cannot force lower tangency or rule out cross-level cancellation.',
    'domain':'Characteristic zero; physical open r*A*Delta!=0. Leading-pole comparison at generic prime smooth A=0 away from b*Delta=0. Completed divisor, source-regularity and support arguments are imported, not rerun.',
    'scope':'No numerical matrix search, primitive, full-source cancellation, exact operator kernel or characteristic-zero rank upper bound. No lower-pole constraints imposed.'}
(args.output/'validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'checks':len(checks),'mutations':len(mutations),'seconds':report['seconds']},indent=2),flush=True)

"""Minimal new A^-3 identities; completed lower-power proofs are reused.
No numerical search and no extra lower-pole restriction are performed.
"""
import argparse,datetime,hashlib,json,pathlib,sys,time
import sympy as s
p=argparse.ArgumentParser()
p.add_argument('--connection',required=True,type=pathlib.Path)
p.add_argument('--prior',required=True,type=pathlib.Path)
p.add_argument('--output',required=True,type=pathlib.Path)
args=p.parse_args()
if args.output.exists():raise SystemExit('fresh output required')
args.output.mkdir(parents=True)
started=time.monotonic();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pin='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
if sha(args.connection)!=pin:raise ValueError('source connection pin changed')
prior_validation=args.prior/'check-02/result/validation.json'
prior_injection=args.prior/'check-02/result/tangent-injection.json'
pv=json.loads(prior_validation.read_text(encoding='utf-8'))
if pv['source_sha256']!=pin or pv['script_sha256']!='473e333ef1b3d21fdde74372aec2ae01c50a8e3b32af1087177448e0798f4395':
    raise ValueError('imported theorem binding changed')
if sha(prior_injection)!='047d04f6d9ee1c70000146506fa2ada26c456fd1dd9de5b2d70e4be811ce828b':
    raise ValueError('imported tangent injection changed')
a,b,c,d,r,v,t=s.symbols('a b c d r v t');loc={str(q):q for q in (a,b,c,d,r,v,t)}
R=s.Matrix([[s.cancel(s.sympify(q,locals=loc)) for q in row] for row in pv['a_residue']])
Tr,Tv,ell=[s.sympify(pv[key],locals=loc) for key in ('T_r','T_v','ell')]
checks=[]
def zero(name,expr):
    items=list(expr) if isinstance(expr,s.MatrixBase) else [expr]
    if any(s.cancel(q)!=0 for q in items):raise ArithmeticError(name)
    checks.append(name);print('PASS '+name,flush=True)
zero('new highest-pole shifted residue determinant',(R-3*s.eye(2)).det()-10)
tau3=r**7+12*r
zero('new tau3 coefficient',s.diff(Tr,r)+s.diff(Tv,v)-3*ell-tau3)

# The new quotient power is checked as an exact one-variable product rule.
z=s.symbols('z');AA=s.Function('A')(z);PP=s.Function('P')(z)
zero('power-three quotient rule',s.diff(PP/AA**3,z)-(s.diff(PP,z)/AA**3-3*PP*s.diff(AA,z)/AA**4))
dp0,dp1,dp2,dp3,Q1,Q2,Q3,U,W3=s.symbols('dp0 dp1 dp2 dp3 Q1 Q2 Q3 U W3')
raw=U**3*(dp0+dp1/U-Q1/U**2+dp2/U**2-2*Q2/U**3+dp3/U**3-3*Q3/U**4)
zero('complete scaled four-sector product rule',raw-(U**3*dp0+U**2*dp1-U*Q1+U*dp2-2*Q2+dp3-3*Q3/U))
zero('replace only the top tangent operator',raw.subs(dp3,W3+3*Q3/U)-(U**3*dp0+U**2*dp1-U*Q1+U*dp2-2*Q2+W3))
w0,w1=s.symbols('w0 w1')
W=s.Matrix([w0,w1]);normal_target=s.Matrix([w0/2-c*w1/(28*b),s.Rational(3,7)*w1])
zero('coupled next-pole normal target',(R-2*s.eye(2))*normal_target+W)

# Original sectors have 702 columns each. Retain all three lower sectors;
# append the imported 294-column top tangent injection without filtering.
old=json.loads(prior_injection.read_text(encoding='utf-8'))
basis=old['original_basis'];nb=len(basis);columns=[]
for sector in range(3):
    for j,key in enumerate(basis):
        columns.append({'sector':sector,'kind':'unrestricted','basis':key,'entries':[[sector*nb+j,1]]})
for col in old['columns']:
    columns.append({'sector':3,'kind':col['kind'],'row':col['row'],'monomial':col['monomial'],
        'entries':[[3*nb+i,q] for i,q in col['entries']]})
if nb!=702 or len(columns)!=2400 or any(sum(c['sector']==sector for c in columns)!=702 for sector in range(3)):
    raise ArithmeticError('unrestricted lower-sector count')
checks.append('highest-pole injection preserves all 2106 lower coefficients')
joint={'shape':[2808,2400],'original_order':'P0,P1,P2,P3 sectors; then original_basis. Sector j represents Pj/A^j.',
    'original_basis':basis,'columns':columns,'imported_top_injection_sha256':sha(prior_injection),
    'scope':'Only highest-pole tangency imposed. No lower-sector tangency, no A^-2 secondary projection, no kernel claim.'}
map_path=args.output/'highest-pole-injection.json'
map_path.write_text(json.dumps(joint,indent=2)+'\n',encoding='utf-8')
mutations=[]
bad=s.expand(s.diff(Tr,r)+s.diff(Tv,v)-2*ell-tau3)
if bad==0:raise ArithmeticError('power-two correction mutation survived')
mutations.append({'name':'wrong quotient factor2 instead of3','nonzero_tau_difference':str(bad)})
bad=s.simplify((w0/2-c*w1/(28*b)-w0/2).subs({b:1,c:1,w1:1}))
if bad==0:raise ArithmeticError('missing off-diagonal coupling mutation survived')
mutations.append({'name':'omit next-pole off-diagonal row coupling','witness':str(bad)})
report={'status':'PASS_MINIMAL_A3_HIGHEST_POLE_AND_FULL_SCALED_FORMULA',
    'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':time.monotonic()-started,
    'python':sys.version,'sympy':s.__version__,'source_sha256':pin,'script_sha256':sha(pathlib.Path(__file__)),
    'prior_validation_sha256':sha(prior_validation),'prior_injection_sha256':sha(prior_injection),
    'checks':checks,'mutations':mutations,'det_R_minus_3I':'10','tau3':str(tau3),'ell':str(ell),
    'top_operator':'W3=[T_r*partial_r+T_v*partial_v+(r^7+12r)*I+ell*A*M_a+t*T_v*M_b]*h+(partial_t+N_t)*k',
    'full_scaled_equation':'A^3*Div_N(P0)+A^2*Div_N(P1)-A*Q1+A*Div_N(P2)-2*Q2+W3=A^3*S',
    'normal_definition':'Qj=A_r*Pjr+A_v*Pjv',
    'next_pole_condition':'(R_a-2I)*Q2+W3|A=0=0',
    'next_pole_normal_target':['W3_0/2-c*W3_1/(28*b)','3*W3_1/7'],
    'dimensions':{'pure_original':702,'pure_necessary':294,'joint_original':2808,'joint_necessary':2400,'unrestricted_lower':2106},
    'injection_sha256':sha(map_path),
    'domain':'Characteristic zero, physical open r*A*Delta!=0. Pole comparisons use the generic prime smooth A=0 boundary away from b*Delta=0; completed proof and regularity of full source are imported, not rerun.',
    'scope':'Highest-pole only. All lower P0/P1/P2 remain unrestricted. No completed A^-2 secondary restriction is applied to P2 or P3. No search, solution, exact kernel or characteristic-zero rank upper bound.'}
(args.output/'validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'checks':len(checks),'mutations':len(mutations),'seconds':report['seconds']},indent=2),flush=True)

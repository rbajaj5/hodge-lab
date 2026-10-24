"""New A^-2 coupled-pole diagnostic; no numerical matrix search.

The completed A^-1 tangency theorem and sparse injection are imported by
hash, not recomputed. This script verifies the new pole order, boundary
coupling and lower compact row compatibility projection.
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
started=time.monotonic()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pin='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
if sha(args.connection)!=pin:raise ValueError('connection pin changed')
prior_validation=args.prior/'check-02/result/validation.json'
prior_injection=args.prior/'check-02/result/tangent-injection.json'
if sha(prior_injection)!='047d04f6d9ee1c70000146506fa2ada26c456fd1dd9de5b2d70e4be811ce828b':
    raise ValueError('prior injection changed')
previous=json.loads(prior_validation.read_text(encoding='utf-8'))
if previous['source_sha256']!=pin or previous['script_sha256']!='473e333ef1b3d21fdde74372aec2ae01c50a8e3b32af1087177448e0798f4395':
    raise ValueError('prior theorem source binding changed')
a,b,c,d,r,v,t,x=s.symbols('a b c d r v t x')
loc={str(y):y for y in (a,b,c,d)}
raw=json.loads(args.connection.read_text(encoding='utf-8'))
M={name:s.Matrix([[s.sympify(q,locals=loc) for q in row] for row in rows]) for name,rows in raw['connection'].items()}
R=s.Matrix([[s.sympify(q,locals=loc) for q in row] for row in previous['a_residue']])
checks=[]
def zero(name,expr):
    items=list(expr) if isinstance(expr,s.MatrixBase) else [expr]
    if any(s.cancel(y)!=0 for y in items):raise ArithmeticError(name)
    checks.append(name);print('PASS '+name,flush=True)
zero('new order-three shifted residue determinant',(R-2*s.eye(2)).det()-s.Rational(14,3))
Tr=r**2*(r**6+1);Tv=r*(2*r**6+1)*v-(3*r**6+2)
ell=3*r*(r**6-1);tau2=r*(4*r**6+9)
zero('new order-two tangent zeroth term',s.diff(Tr,r)+s.diff(Tv,v)-2*ell-tau2)

# These boundary matrix values are new input to the coupled-pole problem.
# The old residue/tangency theorem itself is not rerun.
boundary={name:M[name].applyfunc(lambda q:s.cancel(q).subs(a,0)) for name in ('b','c','d')}
D0=4*b*d-c*c
expected={
 'b':s.Matrix([[-(12*b*d-c*c)/(6*b*D0),c*(6*b*d-c*c)/(3*b*b*D0)],[0,-1/(2*b)]]),
 'c':s.Matrix([[2*c/(3*D0),-(12*b*d-c*c)/(6*b*D0)],[0,0]]),
 'd':s.Matrix([[-4*b/(3*D0),2*c/(3*D0)],[0,0]])}
for name in boundary:zero('boundary M_'+name+' from pinned JSON',boundary[name]-expected[name])
Cphys=t*(1-t*t)/7;Dphys=1+t**6
sub={b:t*v,c:Cphys,d:Dphys}
Mb0,Mc0,Md0=[boundary[n].subs(sub) for n in ('b','c','d')]
Nt0=v*Mb0+s.diff(Cphys,t)*Mc0+s.diff(Dphys,t)*Md0
R0=R.subs(sub)
h0,h1,hr0,hr1,hv0,hv1,k0,k1,kt0,kt1,q10,q11=s.symbols('h0 h1 hr0 hr1 hv0 hv1 k0 k1 kt0 kt1 q10 q11')
h=s.Matrix([h0,h1]);hr=s.Matrix([hr0,hr1]);hv=s.Matrix([hv0,hv1])
k=s.Matrix([k0,k1]);kt=s.Matrix([kt0,kt1]);Q1=s.Matrix([q10,q11])
W=Tr*hr+Tv*hv+(tau2*s.eye(2)+ell*R0+t*Tv*Mb0)*h+kt+Nt0*k
bottom=(Tr*hr1+Tv*hv1+(2*r**7+s.Rational(19,2)*r+(3*r**6+2)/(2*v))*h1+kt1-k1/(2*t))
zero('new lower compact row boundary operator',W[1]-bottom)
desired=s.Matrix([W[0]-Cphys*W[1]/(8*t*v),s.Rational(3,4)*W[1]])
zero('coupled order-two normal target',(R0-s.eye(2))*desired+W)

# Normal image support {0,1,2,5} is imported from the completed theorem.
# Only the NEW lower-row projection and its consequence are checked here.
Ccover=r**18+r**12;H=x**6+Ccover
inv_v=-r*(x**5-x**4+x**3-x**2+x-1)/(Ccover+1)
zero('new boundary inverse-v representative',s.rem((x+1)*inv_v/r-1,H,x))
H0,H1,H0r,H1r,K0,K1,K2,K0t,K1t,K2t=s.symbols('H0 H1 H0r H1r K0 K1 K2 K0t K1t K2t')
bottom_model=bottom.subs({h1:H0+v*H1,hr1:H0r+v*H1r,hv1:H1,k1:K0+K1*v+K2*v*v,kt1:K0t+K1t*v+K2t*v*v},simultaneous=True)
pole=(3*r**6+2)*H0/(2*v)
polynomial=s.cancel(bottom_model-pole)
if s.Poly(polynomial,v).degree()>2:raise ArithmeticError('lower row polynomial part exceeds v degree two')
checks.append('new lower row has only one nonpolynomial-v term')
representative=s.expand(polynomial.subs(v,(x+1)/r)+(3*r**6+2)*H0*inv_v/2)
mu=r*(3*r**6+2)/(2*(Ccover+1))
zero('lower row x^3 projection',representative.coeff(x,3)+mu*H0)
zero('lower row x^4 projection',representative.coeff(x,4)-mu*H0)
zero('v-divisibility removes both forbidden lower projections',representative.subs(H0,0).coeff(x,3)+representative.subs(H0,0).coeff(x,4))
if s.cancel(mu)==0:raise ArithmeticError('zero projection coefficient')
checks.append('projection coefficient is a nonzero characteristic-zero rational function')

# Reuse the exact old tangent injection and filter precisely the fifteen
# prohibited top h row1/v^0 columns; lower P1 remains unrestricted.
oldmap=json.loads(prior_injection.read_text(encoding='utf-8'))
base=oldmap['original_basis'];nbase=len(base)
columns=[]
for sector in (0,1):
    for j,key in enumerate(base):
        columns.append({'sector':sector,'kind':'unrestricted','basis':key,'entries':[[sector*nbase+j,1]]})
removed=[]
for col in oldmap['columns']:
    if col['kind']=='h' and col['row']==1 and col['monomial'][1]==0:
        removed.append(col);continue
    columns.append({'sector':2,'kind':col['kind'],'row':col['row'],'monomial':col['monomial'],
        'entries':[[2*nbase+i,q] for i,q in col['entries']]})
if len(removed)!=15 or len(columns)!=1683:raise ArithmeticError('necessary joint injection dimension')
checks.append('new 1683-parameter injection keeps all 702 intermediate-pole coefficients')
joint={'shape':[2106,1683],'original_order':'sector0,sector1,sector2, then original_basis; sector j means Pj/A^j',
    'original_basis':base,'columns':columns,
    'removed_top_columns':removed,
    'scope':'Necessary only. Does not impose every coupled order-two condition. P1 is unrestricted. No operator kernel claim.',
    'imported_tangent_injection_sha256':sha(prior_injection)}
joint_path=args.output/'necessary-injection.json'
joint_path.write_text(json.dumps(joint,indent=2)+'\n',encoding='utf-8')

mutations=[]
wrong_tau=s.diff(Tr,r)+s.diff(Tv,v)-ell-tau2
if s.cancel(wrong_tau)==0:raise ArithmeticError('wrong quotient power survived')
mutations.append({'name':'use power-one quotient correction at power two','difference':str(s.expand(wrong_tau))})
bad=(s.Rational(3,4)*mu).subs(r,1)
if bad==0:raise ArithmeticError('missed forbidden v-constant top multiplier')
mutations.append({'name':'permit h2 row1 v-constant term','nonzero_forbidden_Q1_x4_coefficient_at_r1':str(bad)})
bad=(Cphys/(8*t*v)).subs({t:2,v:1})
if bad==0:raise ArithmeticError('lost row coupling not detected')
mutations.append({'name':'drop off-diagonal residue coupling','coefficient_at_t2_v1':str(bad)})

report={'status':'PASS_NEW_COUPLED_POLE_CONSTRAINT_AND_TOP_ROW1_V_DIVISIBILITY',
 'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':time.monotonic()-started,
 'python':sys.version,'sympy':s.__version__,'source_sha256':pin,'script_sha256':sha(pathlib.Path(__file__)),
 'prior_validation_sha256':sha(prior_validation),'prior_injection_sha256':sha(prior_injection),
 'checks':checks,'mutations':mutations,
 'det_R_minus_2I':'14/3','tau2':str(tau2),'ell':str(ell),
 'boundary_matrices':{n:[[str(s.factor(q)) for q in row] for row in boundary[n].tolist()] for n in boundary},
 'coupled_boundary_operator_W':list(map(str,W)),
 'coupled_order_two':'(R_a-I)*(A_r*P1r+A_v*P1v)+W2=0 mod A',
 'normal_target':['W2_0-c*W2_1/(8*b)','3*W2_1/4'],
 'normal_image_imported_support_x':[0,1,2,5],
 'inverse_v_representative':str(inv_v),'projection_mu':str(mu),
 'new_lower_projection':['-mu*H0','mu*H0'],
 'new_constraint':'Top tangent multiplier h2_1 is divisible by v. Its v-constant coefficient H0(r,t) vanishes. This does not imply that P1 is tangent.',
 'dimensions':{'original_three_sectors':2106,'top_tangency_only':1698,'new_additional_removed':15,'necessary_after_new_projection':1683},
 'injection_sha256':sha(joint_path),
 'domain':'Characteristic zero. Physical identities on r*A*Delta!=0. Pole comparison is at the generic prime A=0 boundary away from b*Delta=0; imported smoothness/primality theorem reused. In the quotient field Q(r,t)[x]/(x^6+r^18+r^12), C+1 is nonzero and thus invertible.',
 'limits':'No sample matrix search or cancellation. General upper-row and polynomial bounded-lift order-two constraints remain. No exact kernel or characteristic-zero rank upper bound supplied. Previous A^-1 exclusion is not applied to P1 separately.'}
(args.output/'validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'checks':len(checks),'mutations':len(mutations),'seconds':report['seconds'],'dimension':1683},indent=2),flush=True)

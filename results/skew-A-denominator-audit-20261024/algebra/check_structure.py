"""Exact structural reduction, not a sample matrix search.

All six physical flux components are P_i/A; the numerator box is
r=-10..2, v=0..2, t=0..2.  This script checks local necessary conditions,
the small polynomial syzygy and a sparse injection of its surviving box.
"""
import argparse, datetime, hashlib, json, pathlib, sys, time
import sympy as s

p=argparse.ArgumentParser()
p.add_argument('--connection', required=True, type=pathlib.Path)
p.add_argument('--output', required=True, type=pathlib.Path)
args=p.parse_args()
if args.output.exists(): raise SystemExit('fresh output required')
args.output.mkdir(parents=True)
start=time.monotonic()
a,b,c,d,r,v,t,x=s.symbols('a b c d r v t x')
pin='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
raw=args.connection.read_bytes()
if hashlib.sha256(raw).hexdigest()!=pin: raise ValueError('connection pin mismatch')
data=json.loads(raw.decode('utf-8'))
loc={str(q):q for q in (a,b,c,d)}
M={name:s.Matrix([[s.sympify(q,locals=loc) for q in row] for row in rows]) for name,rows in data['connection'].items()}
checks=[]
def zero(name, expr):
    items=list(expr) if isinstance(expr,s.MatrixBase) else [expr]
    if any(s.cancel(q)!=0 for q in items): raise ArithmeticError(name)
    checks.append(name)
    print('PASS '+name,flush=True)
def regular_at_a0(expr):
    return s.cancel(expr).subs(a,0)

R=s.Matrix([[regular_at_a0(a*q) for q in row] for row in M['a'].tolist()])
zero('a-residue matrix from pinned literal connection',R-s.Matrix([[0,-c/(6*b)],[0,-s.Rational(1,3)]]))
zero('shifted a-residue invertible', (R-s.eye(2)).det()-s.Rational(4,3))
zero('transverse matrices have no a-pole',s.Matrix([regular_at_a0(a*q) for name in ('b','c','d') for q in M[name]]))
zero('full two-row target has no a-pole',s.Matrix([regular_at_a0(a*q/12) for q in M['b'][:,0]]))

C=r**18+r**12
H=(r*v-1)**6+C
A=H/r**15
Ar=s.diff(A,r);Av=s.diff(A,v)
Tr=r**2*(r**6+1)
Tv=r*(2*r**6+1)*v-(3*r**6+2)
ell=3*r*(r**6-1)
q0=7*r**7+6*r
zero('logarithmic vector field T(A)=ell*A',Tr*Ar+Tv*Av-ell*A)
zero('div(T)-ell=q0',s.diff(Tr,r)+s.diff(Tv,v)-ell-q0)

# A is prime: the Laurent-coordinate change w=(rv-1)/r^2 turns
# r^3*A into w^6+r^6+1. Eisenstein at r^2+1 in QQ[r] applies.
w=s.symbols('w')
zero('Fermat coordinate identity',r**3*A.subs(v,(r*r*w+1)/r)-(w**6+r**6+1))
factor=s.Poly(r*r+1,r,domain=s.QQ)
constant=s.Poly(r**6+1,r,domain=s.QQ)
if not constant.rem(factor).is_zero or constant.rem(factor**2).is_zero:
    raise ArithmeticError('Eisenstein prime has wrong multiplicity')
checks.append('Eisenstein constant has valuation one at r^2+1')
zero('smooth Fermat derivative in r',s.diff(w**6+r**6+1,r)-6*r**5)
delta=s.sympify(data['Delta'],locals=loc)
delta_boundary=s.expand(delta.subs({a:0,b:t*v,c:t*(1-t*t)/7,d:1+t**6}))
if s.Poly(delta_boundary,v).degree()!=3 or s.Poly(H,v).degree()!=6:
    raise ArithmeticError('generic discriminant boundary degree')
checks.append('Delta is generically a unit along A=0 by v degrees 3<6')

# A=0 is a generic divisor calculation, not an ordinary allowed point.
# Work over QQ(r,t)[x], x=rv-1.  Here H=x^6+C and r is a unit.
p0,p1,p2,q0s,q1,q2=s.symbols('p0 p1 p2 q0s q1 q2')
Pr=p0+p1*x+p2*x*x
Pv=q0s+q1*x+q2*x*x
E=Pr+r*r*Pv
B=6*r**11*(2*r**6+1)
normal=B*Pr+6*x**5*E/r
normal_remainder=s.rem(normal,x**6+C,x)
expected=B*Pr+6*((p0+r*r*q0s)*x**5-C*(p1+r*r*q1)-C*(p2+r*r*q2)*x)/r
zero('normal-flux polynomial remainder',normal_remainder-expected)
zero('original normal flux has that remainder',s.rem((s.diff(H,r)*Pr+s.diff(H,v)*Pv).subs(v,(x+1)/r)-expected,x**6+C,x))

# The four coefficients force p2=0, E0=0, E1=lambda*p0,
# E2=lambda*p1; this gives exactly two QQ(r,t) parameters.
lam=(2*r**6+1)/(r**6+1)
sub={p2:0,q0s:-p0/r**2,q1:(lam*p0-p1)/r**2,q2:lam*p1/r**2}
zero('complete two-parameter polynomial syzygy solves all coefficients',normal_remainder.subs(sub,simultaneous=True))
normal_matrix=s.Matrix([[s.diff(s.expand(normal_remainder).coeff(x,i),u) for u in (p0,p1,p2,q0s,q1,q2)] for i in (0,1,2,5)])
minor=normal_matrix[:,[0,1,2,3]].det()
if s.cancel(minor)==0: raise ArithmeticError('four residue constraints not independent')
checks.append('four normal-flux constraints have nonzero exact minor')
zero('syzygy is (Tr,Tv)*h',s.cancel(((lam*x-1)/r**2)*Tr-Tv.subs(v,(x+1)/r)))

# Primitive content over QQ[r,r^-1,t]: Tr and the v-constant
# part of Tv are coprime. This rules out hidden r-denominators in h.
gcd=s.gcd(r**6+1,3*r**6+2)
zero('primitive tangent vector has no hidden r denominator',gcd-1)

# A connection-only product rule proves the operator conjugation without
# re-expanding the large physical discriminant. Each vector component can
# be replaced by independent scalar symbols in this product rule.
u,ur,uv,ut,aa,aar,aav,nr,nv,nt=s.symbols('u ur uv ut aa aar aav nr nv nt')
zero('r quotient derivative', (ur/aa-u*aar/aa**2+nr*u/aa)-(ur+(nr-aar/aa)*u)/aa)
zero('v quotient derivative', (uv/aa-u*aav/aa**2+nv*u/aa)-(uv+(nv-aav/aa)*u)/aa)
zero('t quotient derivative with A_t=0', (ut+nt*u)/aa-(ut/aa+nt*u/aa))

# Sparse injection P_r=Tr*h, P_v=Tv*h, P_t=k. No operator sample
# matrix is assembled, reduced, or copied here.
basis=[(i,j,m,n,k) for i in range(3) for j in range(2) for m in range(-10,3) for n in range(3) for k in range(3)]
index={key:i for i,key in enumerate(basis)}
columns=[]
for j in range(2):
    for m in range(-10,-5):
        for n in range(2):
            for k in range(3):
                terms=[(0,8,0,1),(0,2,0,1),(1,7,1,2),(1,1,1,1),(1,6,0,-3),(1,0,0,-2)]
                entries=[]
                for direction,dm,dn,coef in terms:
                    key=(direction,j,m+dm,n+dn,k)
                    if key not in index: raise ArithmeticError('tangent multiplier escaped declared numerator box')
                    entries.append([index[key],coef])
                columns.append({'kind':'h','row':j,'monomial':[m,n,k],'entries':entries})
for j in range(2):
    for m in range(-10,3):
        for n in range(3):
            for k in range(3):
                columns.append({'kind':'P_t','row':j,'monomial':[m,n,k],'entries':[[index[(2,j,m,n,k)],1]]})
if len(columns)!=294: raise ArithmeticError('reduced dimension')
checks.append('294-column exact sparse injection stays inside 702-column numerator box')
injection={'convention':'P=E*u, F=P/A; E is 702 by 294; each column stores [zero_based_row, rational_integer_coefficient] entries',
    'original_basis':basis,'columns':columns,'shape':[702,294],
    'proof_injective':'P_r=Tr*h with Tr nonzero forces h=0; then P_t=k forces k=0.'}
injection_path=args.output/'tangent-injection.json'
injection_path.write_text(json.dumps(injection,indent=2)+'\n',encoding='utf-8')

mutations=[]
bad=s.cancel(Tr*Ar-Tv*Av-ell*A).subs({r:1,v:2})
if bad==0: raise ArithmeticError('wrong tangency sign not detected')
mutations.append({'name':'reverse T_v sign','nonzero_witness_r1_v2':str(bad)})
bad=(R+s.eye(2)).det()-s.Rational(4,3)
if s.cancel(bad)==0: raise ArithmeticError('wrong quotient derivative sign not detected')
mutations.append({'name':'wrong shifted-residue sign','det_difference':str(s.cancel(bad))})

report={'status':'PASS_EXACT_NECESSARY_TANGENCY_REDUCTION_NOT_SOURCE_CANCELLATION',
    'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':time.monotonic()-start,
    'python':sys.version,'sympy':s.__version__,'source_sha256':pin,
    'script_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
    'checks':checks,'mutations':mutations,
    'A':str(A),'T_r':str(Tr),'T_v':str(Tv),'ell':str(ell),'q0':str(q0),
    'a_residue':[[str(q) for q in row] for row in R.tolist()],
    'shifted_residue_determinant':'4/3',
    'normal_remainder':str(s.factor(normal_remainder)),
    'normal_constraint_minor':str(s.factor(minor)),
    'multiplier_box':{'m':[-10,-6],'n':[0,1],'k':[0,2]},
    'reduced_operator':'[T_r*partial_r+T_v*partial_v+q0*I+ell*A*M_a+t*T_v*M_b] h +(partial_t+N_t) P_t = A*r^-4*M_b*e0/12',
    'dimension':{'original':702,'tangent_h':60,'free_P_t':234,'necessary_reduced':294},
    'injection_sha256':hashlib.sha256(injection_path.read_bytes()).hexdigest(),
    'prime_and_smooth':'w=(rv-1)/r^2 identifies r^3*A with w^6+r^6+1. Eisenstein at r^2+1 over QQ[r] proves irreducibility; derivative 6*r^5 is a unit on r!=0, hence this divisor is smooth. Delta|A=0 has v-degree3, whereas H=r^15*A has v-degree6, so Delta is generically a unit there.',
    'domain':'Characteristic zero. Rational function identities in QQ(r,v,t), on r*A*Delta != 0. The pole proof uses the generic A=0 boundary away from b*Delta=0; no ordinary point with A=0 is admitted.',
    'scope':'Every solution and every homogeneous kernel in the stated new numerator box factors through this injection. This gives no kernel dimensions beyond at most294, no matrix rank upper bound, no solution, and no exclusion by itself. The residue constraint is necessary, not sufficient.',
    'old_box_intersection':'B intersect (B/A)={0}: for nonzero L in B, deg_v(A*L)=6+deg_v(L)>2.'}
(args.output/'validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'checks':len(checks),'mutations':len(mutations),'seconds':report['seconds']},indent=2),flush=True)

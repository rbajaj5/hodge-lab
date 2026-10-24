import argparse,datetime,hashlib,json,pathlib,sys,time
import sympy as s
p=argparse.ArgumentParser();p.add_argument('--connection',required=True,type=pathlib.Path);p.add_argument('--prior-residue',required=True,type=pathlib.Path);p.add_argument('--output',required=True,type=pathlib.Path);args=p.parse_args()
if args.output.exists():raise SystemExit('fresh output required')
start=time.monotonic();raw=args.connection.read_bytes();pin='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
if hashlib.sha256(raw).hexdigest()!=pin:raise ValueError('source mismatch')
data=json.loads(raw.decode('utf-8'));prior=json.loads(args.prior_residue.read_text(encoding='utf-8'))
a,b,c,d,v,t,g,k=s.symbols('a b c d v t gamma kappa');loc={str(x):x for x in (a,b,c,d)}
M={name:s.Matrix([[s.sympify(x,locals=loc) for x in row] for row in rows]) for name,rows in data['connection'].items()}
delta=s.sympify(data['Delta'],locals=loc);db=s.diff(delta,b)
B=(delta*M['b']).applyfunc(s.cancel);e0=s.Matrix([1,0]);e1=s.Matrix([0,1]);adj=B.adjugate()
checks=[];quotients={}
def zero(name,x):
 xs=list(x) if isinstance(x,s.MatrixBase) else [x]
 if any(s.cancel(q)!=0 for q in xs):raise ArithmeticError(name)
 checks.append(name);print('PASS '+name,flush=True)
def divisible(name,x):
 xs=list(x) if isinstance(x,s.MatrixBase) else [x];qs=[]
 for q in xs:
  quotient=s.cancel(q/delta)
  s.Poly(quotient,a,b,c,d,domain=s.QQ)
  qs.append(str(quotient))
 quotients[name]=qs;checks.append(name);print('PASS '+name,flush=True)
zero('generic residue trace',s.trace(B)+db/3)
divisible('generic determinant vanishes on Delta',B.det())
for name,vec in [('b-column0',delta*M['b']*e0),('b-column1',delta*M['b']*e1),('c-column1',delta*M['c']*e1),('d-column1',delta*M['d']*e1)]:
 divisible('generic image certificate '+name,adj*vec)

# Full source and connection residues at the same boundary point.
C=t*(1-t*t)/7;D=1+t**6;sub={b:t*v,c:C,d:D}
Nv=t*M['b'];Nt=v*M['b']+s.diff(C,t)*M['c']+s.diff(D,t)*M['d']
dphys=delta.subs(sub);dv=s.diff(dphys,v)
point={a:s.Integer(4),v:s.Integer(-6),t:s.Integer(1)}
rv=(delta*Nv).applyfunc(s.cancel).subs(sub).subs(point)/dv.subs(point)
rt=(delta*Nt*e1).applyfunc(s.cancel).subs(sub).subs(point)/dv.subs(point)
rb=(delta*M['b']*e0).applyfunc(s.cancel).subs(sub).subs(point)/dv.subs(point)
source_res=g*rt/(36*point[t])+k*rb/(108*point[a])
scalar=g/s.Integer(756)-k/s.Integer(2592)
expected=-s.ones(2)/6
zero('full two-row Nv residue matrix',rv-expected)
zero('full two-row R2 residue vector',source_res-scalar*s.ones(2,1))
left=s.Matrix([[1,-1]])
zero('point left-null vector',left*rv)
zero('point full source projection is zero',left*source_res)
zero('point compatible leading regular value',rv*(-3*source_res)-source_res)
zero('point eigenvalue polynomial',rv.charpoly().as_expr()-rv.charpoly().gen*(rv.charpoly().gen+s.Rational(1,3)))
zero('point residue-image projector',rv*rv+rv/3)

# Generic normalizing factor Nv/Delta_v = B/Delta_b, since b=t v.
zero('physical v derivative of discriminant',dv-t*db.subs(sub))
divisible('generic residue-image projector numerator',B*B+db*B/3)

mutations=[]
bad_source=s.Matrix([scalar,0])
if s.cancel((left*bad_source)[0])==0:raise ArithmeticError('dropped row mutation undetected')
mutations.append({'name':'drop residue row1','nonzero_projection':str((left*bad_source)[0])})
if rv*(-source_res/3)==source_res:raise ArithmeticError('wrong reciprocal normalization undetected')
mutations.append({'name':'wrong leading coefficient -1/3 instead of -3','defect':[str(s.factor(q)) for q in rv*(-source_res/3)-source_res]})

report={'status':'PASS: generic Delta image compatibility; no v-only local residue obstruction found',
 'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':time.monotonic()-start,'python':sys.version,'sympy':s.__version__,
 'source_sha256':hashlib.sha256(raw).hexdigest(),'script_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
 'prior_residue_sha256':hashlib.sha256(args.prior_residue.read_bytes()).hexdigest(),
 'checks':checks,'mutations':mutations,'generic_polynomial_quotients':quotients,
 'generic_conditions':'Characteristic zero; Delta=0, Delta_v=t Delta_b !=0, a!=0, physical cover unramified f_r!=0, r!=0; source scalars gamma,kappa regular along this divisor.',
 'generic_residue_matrix':'C=(Delta M_b)/Delta_b on Delta=0',
 'generic_eigenvalues':['0','-1/3'],'generic_image_condition':'adj(Delta M_b) S=0 modulo Delta; all displayed quotient identities are exact polynomial divisibility, not a specialization inference',
 'generic_leading_solution':'Z0=-3 S + u, with u in ker C and S=Res(R2 dv). This is divisor data, not a global rational flux.',
 'pole_argument':'If a rational v-only correction had pole order m>=1, leading (C-m I)Z_-m=0. Eigenvalues 0,-1/3 exclude all positive integer m, so it must be regular and must obey C Z0=S. Compatibility holds; at n>=1, n I+C is invertible, so the regular local formal recursion has no further resonant obstruction.',
 'point':{'a':4,'v':-6,'t':1,'residue_Nv':[[str(q) for q in row] for row in rv.tolist()],
 'residue_R2':[str(q) for q in source_res],'left_null':['1','-1'],'projection':'0','leading_Z0':[str(s.factor(q)) for q in -3*source_res]},
 'reused_nonzero_scalar_certificate':{'source':str(args.prior_residue),'not_recomputed':True,'boundary_witness':prior['boundary_witness']},
 'scope':'The fixed-L scalar residue obstruction is removed by two-row v-connection coupling. This proves generic local compatibility on the stated Delta open, not existence of a global rational v-only primitive and not any conclusion about other divisors or infinity. No old gcd or source reduction replay.'}
args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'checks':len(checks),'mutations':len(mutations),'seconds':report['seconds'],'projection':'0'},indent=2),flush=True)

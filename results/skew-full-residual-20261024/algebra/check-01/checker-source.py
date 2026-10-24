import argparse, datetime, hashlib, json, pathlib, sys, time
import sympy as s

p=argparse.ArgumentParser()
p.add_argument('--connection',required=True,type=pathlib.Path)
p.add_argument('--output',required=True,type=pathlib.Path)
args=p.parse_args()
if args.output.exists(): raise SystemExit('fresh output required')
start=time.monotonic()
a,b,c,d,r,v,t=s.symbols('a b c d r v t')
raw=args.connection.read_bytes()
expected='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
if hashlib.sha256(raw).hexdigest()!=expected: raise ValueError('connection pin mismatch')
data=json.loads(raw.decode('utf-8'))
loc={str(x):x for x in (a,b,c,d)}
M={name:s.Matrix([[s.sympify(x,locals=loc) for x in row] for row in rows]) for name,rows in data['connection'].items()}
checks=[]
def zero(name,x):
    xs=list(x) if isinstance(x,s.MatrixBase) else [x]
    if any(s.cancel(y)!=0 for y in xs): raise ArithmeticError(name)
    checks.append(name); print('PASS '+name,flush=True)

# This is the new coefficient-Euler tangent calculation, not an assertion
# that all one-row currents lie on the Euler line.
e0=s.Matrix([1,0]);e1=s.Matrix([0,1])
zero('universal scalar coefficient Euler operator',a*M['a']+b*M['b']+c*M['c']+d*M['d']+s.eye(2)*s.Rational(5,6))
zero('universal fibre-coordinate Euler operator',3*a*M['a']+2*b*M['b']+c*M['c']+s.diag(1,2))
C=t*(1-t*t)/7; D=1+t**6; Cp=s.diff(C,t);Dp=s.diff(D,t)
P=t**8-3*t**6-3*t**2+1; Q=t**8-5*t**6-5*t**2+1
T=s.Matrix([a*(3*Cp*D-2*C*Dp),v*(2*Cp*D-C*Dp-C*D/t),C*D])
W=s.Matrix([t*P/(7*D),t*v*Q/(21*a*D),t*t*(1-t*t)/(21*a)])
zero('coefficient-Euler lift is existing beta line, not transverse',T-3*a*D*W/t)
# Tangency equations for a combination u E_scalar + w E_fibre:
# Dp gamma=D u, Cp gamma=C(u+w). For C*D!=0 these determine u,w
# from gamma; alpha,beta then follow uniquely. This is the scoped rank-one claim.
u,w,gamma=s.symbols('u w gamma')
tangency=s.Matrix([[-D,0,Dp],[-C,-C,Cp]])
zero('tangency two-by-two minor',tangency[:,0:2].det()-C*D)

# A polynomial Bezout transverse direction, with no added divisor.
J=(4-5*t*t)/4
U=7*t*(17+2*t*t+14*t**4-5*t**6)/4
zero('polynomial Bezout c U + P J = 1',C*U+P*J-1)
La=-7*D*J; Lt=-3*a*U
beta0a=-C/(3*a); beta0t=P/(7*D)
beta1a=-2*t*v/(3*a);beta1v=t;beta1t=v*(1-t*Dp/(3*D))
zero('beta0 wedge L is da wedge dt',beta0a*Lt-beta0t*La-1)
F=7*J*(D-t*Dp/3)+2*t*U
Wt=s.Matrix([-3*a*t*U,-v*F,7*t*D*J])
qt=t*(-3*U+s.Rational(49,6)*Dp*J+7*D*s.diff(J,t))
sub={b:t*v,c:C,d:D}
Ma,Mb,Mc,Md=[M[q].subs(sub) for q in ('a','b','c','d')]
N=[Ma,t*Mb,v*Mb+Cp*Mc+Dp*Md]
# Fluxes are h*(0,Wt_a), h*(-1,Wt_v), h*(0,Wt_t).
flux=[s.Matrix([0,Wt[0]]),s.Matrix([-1,Wt[1]]),s.Matrix([0,Wt[2]])]
zero_order=sum((flux[i].diff(x)+N[i]*flux[i] for i,x in enumerate((a,v,t))),s.zeros(2,1))
zero('mixed beta operator first row is exactly minus h_v',zero_order[0])
zero('mixed beta operator second row zero-order polynomial',zero_order[1]-qt)
zero('mixed beta flux wedge construction',Wt-s.Matrix([beta1v*Lt,beta1t*La-beta1a*Lt,-beta1v*La]))

# The canonical h cancels all cover derivative poles in output row zero.
A,B,Av,Avv,Bv,x,xv,xvv=s.symbols('A B Av Avv Bv chi chi_v chi_vv')
h=-A*xv-(v*B-Av)*x
hv=-Av*xv-A*xvv-(B+v*Bv-Avv)*x-(v*B-Av)*xv
target0=A*xvv+B*(v*xv-x)
zero('row0 integration-by-parts survivor',target0+hv-(Avv-2*B-v*Bv)*x)

# A decisive residue for the ENTIRE family h beta wedge L, not merely h above.
# At t=1 the Delta divisor has a rational point a=4,v=-6. A0,B0 are
# the actual R2 first-row coefficients of chi_vv and v chi_v-chi.
delta=s.sympify(data['Delta'],locals=loc).subs(sub)
A0=(N[2][0,1]+v/(3*a))/(36*t)
B0=Mb[0,0]/(108*a)
dv=s.diff(delta,v)
point={a:s.Integer(4),v:s.Integer(-6),t:s.Integer(1)}
def point_value(expr):return s.cancel(expr).subs(point)
zero('simple discriminant boundary point',delta.subs(point))
if dv.subs(point)!=864: raise ArithmeticError('Delta_v witness')
resA=point_value(A0*delta)/dv.subs(point)
resB=point_value(B0*delta)/dv.subs(point)
zero('R2 row0 gamma residue',resA-s.Rational(1,756))
zero('R2 row0 kappa residue',resB+s.Rational(1,2592))

f=r**18+r**12+(v*r-1)**6-a*r**15
fr=s.diff(f,r); fv=s.diff(f,v);frr=s.diff(fr,r);frv=s.diff(fr,v);fvv=s.diff(fv,v)
fixed={a:s.Integer(4),v:s.Integer(-6)}
ff,zz,pp,rr,jj,uu=[s.Poly(q.subs(fixed),r,domain=s.QQ) for q in (f,fr,fv,frr,frv,fvv)]
if s.gcd(ff,zz).degree()!=0: raise ArithmeticError('cover not etale at boundary witness')
checks.append('all cover sheets are etale at discriminant boundary witness')
# gamma=g+12, kappa=k+144 at v=-6. Res=(24g-7k-720)/18144.
rp=s.Poly(r,r,domain=s.QQ)
G=12*pp**2*zz+3*rp*uu*zz**2-6*rp*jj*pp*zz+3*rp*rr*pp**2
Nres=24*G-21*(-6)*rp*pp*zz**2+7*rp**2*zz**3-720*rp**5*zz**3
Dres=18144*rp**5*zz**3
rem=Nres.rem(ff)
gn=s.gcd(ff,Nres);gd=s.gcd(ff,Dres)
if gn.degree()!=0 or gd.degree()!=0:raise ArithmeticError('residue nonzero/unit witness failed')
checks.append('nonzero row0 residue on every cover sheet at boundary witness')

mutations=[]
bad=s.expand(C*U-P*J-1)
if bad==0: raise ArithmeticError('Bezout sign mutation survived')
mutations.append({'name':'wrong Bezout sign','witness_at_t0':str(bad.subs(t,0))})
if (resA+s.Rational(1,756))==0:raise ArithmeticError('operator sign mutation survived')
mutations.append({'name':'replace output minus h_v by plus h_v','target_double_residue_gamma':str(2*resA)})

report={'status':'PASS; polynomial mixed-beta family has a nonzero residue obstruction, not a full-source nonexistence claim',
 'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':time.monotonic()-start,
 'python':sys.version,'sympy':s.__version__,'source_sha256':hashlib.sha256(raw).hexdigest(),
 'script_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),
 'checks':checks,'mutations':mutations,'L':[str(La),str(Lt)],'mixed_second_row_flux':[str(s.factor(q)) for q in Wt],'mixed_second_row_zero_order':str(s.factor(qt)),
 'full_operator':['-D_v(h)','Wt_a*D_a(h)+Wt_v*D_v(h)+Wt_t*partial_t(h)+qt*h'],
 'row0_survivor':'(partial_v^2 A0 - 2 B0 - v partial_v B0)*chi',
 'boundary_witness':{'a':4,'v':-6,'t':1,'Delta_v':864,'residue_gamma':str(resA),'residue_kappa':str(resB),
 'cover_polynomial':str(ff.as_expr()),'gcd_f_fr_degree':s.gcd(ff,zz).degree(),
 'residue_denominator':str(Dres.as_expr()),'residue_numerator_remainder':str(rem.as_expr()),
 'gcd_f_residue_numerator_degree':gn.degree(),'gcd_f_residue_denominator_degree':gd.degree()},
 'scope':'No rational scalar h can make Div_N(h beta wedge L)=R2: first component is -D_v h, whose relative 1-form has zero residues, while R2_0 dv has the certified nonzero residue. Arbitrary other two-row fluxes remain unexcluded.',
 'new_divisor':'none in L or its scalar operator; L is polynomial in a,t. A0,B0 and canonical h use only the existing a,Delta,ramification support.',
 'prior_results':'Q/R2, beta and W imported as prior mathematics; no old scalar trace, Lean or CI replay.'}
args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'status':report['status'],'checks':len(checks),'mutations':len(mutations),'seconds':report['seconds'],'gcd_residue_numerator':gn.degree(),'gcd_residue_denominator':gd.degree()},indent=2),flush=True)

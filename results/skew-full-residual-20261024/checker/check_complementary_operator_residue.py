#!/usr/bin/env python3
"""Independent new fixed-L full operator and discriminant residue obstruction.

Checks the full two-row differential operator directly against the pinned
connection. The residue computation uses exact finite-field quotient arithmetic
as a characteristic-zero nonvanishing certificate at a good reduction prime.
"""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,threading,time
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--run',action='store_true')
p.add_argument('--connection',type=Path,default=Path(r'C:/Users/anaxe/Documents/Codex/hl-source-20261023/results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'))
args=p.parse_args()
if args.run:
    began=time.monotonic()
    try:out=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--connection',str(args.connection)],capture_output=True,text=True,encoding='utf-8',timeout=60)
    except subprocess.TimeoutExpired as ex:
        txt=lambda x:x.decode('utf-8',errors='replace') if isinstance(x,bytes) else (x or '')
        (HERE/'complementary-operator-residue-timeout.log').write_text(txt(ex.stdout)+txt(ex.stderr),encoding='utf-8');raise
    log=out.stdout+out.stderr;(HERE/'complementary-operator-residue.log').write_text(log,encoding='utf-8')
    print(out.stdout,end='');print(out.stderr,end='',file=sys.stderr)
    receipt={'exit_code':out.returncode,'wall_seconds':time.monotonic()-began,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'log_sha256':hashlib.sha256(log.encode('utf-8')).hexdigest(),'child_limit_seconds':60}
    rp=HERE/'complementary-operator-residue.json'
    if rp.exists():receipt['report_sha256']=hashlib.sha256(rp.read_bytes()).hexdigest()
    (HERE/'complementary-operator-residue-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt));sys.exit(out.returncode)
import sympy as S
watch=threading.Timer(58,lambda:os._exit(124));watch.daemon=True;watch.start()
a,b,c,d,v,t,r=S.symbols('a b c d v t r')
source=args.connection.read_bytes();source_sha=hashlib.sha256(source).hexdigest()
assert source_sha=='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
raw=json.loads(source);loc={str(x):x for x in (a,b,c,d)}
M={x:S.Matrix([[S.sympify(y,locals=loc) for y in row] for row in raw['connection'][str(x)]]) for x in (a,b,c,d)}
C=t*(1-t*t)/7;D=1+t**6;P=t**8-3*t**6-3*t*t+1
J=(4-5*t*t)/4;U=7*t*(17+2*t*t+14*t**4-5*t**6)/4
La=-7*D*J;Lt=-3*a*U
wa=-C/(3*a);wt=S.diff(C,t)-2*C*S.diff(D,t)/(3*D)
za=-2*t*v/(3*a);zt=v-t*v*S.diff(D,t)/(3*D)
sub={b:t*v,c:C,d:D}
Ma,Mb,Mc,Md=[M[x].subs(sub,simultaneous=True) for x in (a,b,c,d)]
N=[Ma,t*Mb,v*Mb+S.diff(C,t)*Mc+S.diff(D,t)*Md]
W=S.Matrix([t*Lt,zt*La-za*Lt,-t*La])
q=t*(-3*U+S.Rational(49,6)*S.diff(D,t)*J+7*D*S.diff(J,t))
checks=[]
def check(name,x):
    zs=list(x) if isinstance(x,S.MatrixBase) else [x]
    got=[S.cancel(z) for z in zs];assert all(z==0 for z in got),(name,got)
    checks.append(name);print('PASS:',name,flush=True)
check('polynomial Bezout identity cU+PJ=1',C*U+P*J-1)
check('beta0 wedge L equals da wedge dt',wa*Lt-wt*La-1)
check('explicit three second-row flux coefficients',W-S.Matrix([-3*a*t*U,-v*(7*J*(D-t*S.diff(D,t)/3)+2*t*U),7*t*D*J]))
# The first-row flux is exactly (0,-h,0). Check both zero-order rows;
# coefficients of h_a,h_v,h_t then give the full differential operator.
check('full operator row0 is minus D_v h',-N[1][0,0]+sum(N[i][0,1]*W[i] for i in range(3)))
qdirect=sum(S.diff(W[i],x)+N[i][1,1]*W[i] for i,x in enumerate((a,v,t)))-N[1][1,0]
check('full operator second-row zero-order coefficient',qdirect-q)
check('second-row exterior-form derivation',q-(S.diff(D,t)*W[2]/(6*D)+t*(S.diff(Lt,a)-S.diff(La,t))))

# Residue of the NEW target row0, obtained from pinned entries before going
# to the singular divisor. No singular matrix value is evaluated.
alpha1=S.cancel(((N[2][0,1]+v/(3*a))/(36*t)).subs(t,1))
beta1=S.cancel((Mb[0,0]/(108*a)).subs(t,1))
delta1=S.cancel(S.sympify(raw['Delta'],locals=loc).subs({b:v,c:0,d:2,a:4}))
check('simple discriminant divisor',delta1-8*(v**3+216))
assert S.diff(delta1,v).subs(v,-6)==864
ares=S.cancel((v+6)*alpha1.subs(a,4)).subs(v,-6)
bres=S.cancel((v+6)*beta1.subs(a,4)).subs(v,-6)
check('source alpha residue',ares-S.Rational(1,756))
check('source beta residue',bres+S.Rational(1,2592))

# Compute all cover motion in the residue algebra, rather than freezing r.
# Good modular reduction gives an exact characteristic-zero witness:
# monic f, f_r invertible, r invertible, 756*2592 invertible modulo prime.
prime=32003
domain=S.GF(prime)
f=r**18+r**12+(v*r-1)**6-a*r**15
spec={a:S.Integer(4),v:S.Integer(-6)}
fp=S.Poly(f.subs(spec),r,domain=domain)
conv=lambda x:S.Poly(x.subs(spec),r,domain=domain)
one=S.Poly(1,r,domain=domain)
red=lambda x:x.rem(fp)
fr=conv(S.diff(f,r));fv=conv(S.diff(f,v))
frv=conv(S.diff(f,r,v));frr=conv(S.diff(f,r,2));fvv=conv(S.diff(f,v,2))
assert S.gcd(fp,fr).degree()==0
fri=S.invert(fr,fp);ri=S.invert(S.Poly(r,r,domain=domain),fp)
rv=red(-fv*fri)
rvv=red(-(fvv+2*frv*rv+frr*red(rv*rv))*fri)
psiv=red(-3*red(ri**4)*rv)
gamma=red(12*red(ri**5)*red(rv*rv)-3*red(ri**4)*rvv+12*one)
chi=red(ri**3+72*one)
chiv=red(psiv-36*one)
kappa=red(-6*chiv-chi)
residue=red(pow(756,-1,prime)*gamma-pow(2592,-1,prime)*kappa)
assert not residue.is_zero
checks.append('moving-root residue nonzero at good modular reduction')
print('PASS: moving-root residue nonzero; degree',residue.degree(),'mod',prime,flush=True)
wrong=red(pow(756,-1,prime)*gamma+pow(2592,-1,prime)*kappa)
defect=red(wrong-residue);assert not defect.is_zero
print('REJECTED CONTROL: flip kappa residue sign; degree',defect.degree(),flush=True)
# Deliberately freezing r is also wrong; this is separate from sign control.
frozen_gamma=12*one;frozen_kappa=red(-6*(-36*one)-chi)
frozen=red(pow(756,-1,prime)*frozen_gamma-pow(2592,-1,prime)*frozen_kappa)
assert not red(residue-frozen).is_zero
checks.append('freezing the cover root changes the residue')

report={
 'status':'PASS: full fixed-L operator verified; nonzero relative residue excludes that entire rational-h family for centered R2',
 'source_sha256':source_sha,'source_path':str(args.connection),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'checks':checks,'L_a':str(La),'L_t':str(Lt),'Wtilde':[str(S.factor(x)) for x in W],'qtilde':str(S.factor(q)),
 'full_operator':['-D_v(h)','Wtilde_a D_a(h)+Wtilde_v D_v(h)+Wtilde_t partial_t(h)+qtilde h'],
 'cover_derivatives':'D_a=partial_a+r^15/f_r partial_r; D_v=partial_v-f_v/f_r partial_r; r_t=0. In (r,v,t), D_a=partial_r/A_r and D_v=partial_v|r-A_v partial_r/A_r.',
 'source_binding':'Target is centered R2 from the pinned compact source/current relation, with row0=alpha chi_vv+beta(v chi_v-chi); chi=r^-3-v^3/3.',
 'residue_divisor_point':{'a':'4','t':'1','v':'-6','Delta_v':'864','alpha_residue':str(ares),'beta_residue':str(bres)},
 'residue_expression':'gamma/756-kappa/2592; gamma=chi_vv and kappa=v chi_v-chi, with full moving-root derivatives',
 'exact_modular_witness':{'prime':prime,'f_coefficients':[int(x)%prime for x in fp.all_coeffs()],'gcd_f_fr_degree':0,'residue_coefficients_descending':[int(x)%prime for x in residue.all_coeffs()],'residue_degree':residue.degree(),'nonzero':True,'flipped_kappa_sign_defect_coefficients_descending':[int(x)%prime for x in defect.all_coeffs()]},
 'characteristic_zero_reason':'A nonzero good reduction of this rational residue element implies the characteristic-zero element is nonzero. All inverted factors (f_r, r, 756,2592) are explicitly invertible in the modular quotient; monicity avoids a leading-coefficient degeneration. gcd(f,f_r)=1 modulo the prime implies the characteristic-zero specialization is etale.',
 'generic_divisor_reason':'On f_r*Delta_v!=0, R2 row0 has at most a simple Delta pole, so the coefficient of dv/(v-v0) is a rational residue on the relative discriminant divisor over Q(a,t). The permitted evaluation above proves that residue is not identically zero on at least one component. This does not specialize a hypothetical h. A rational D_v derivative has zero residue in the local parameter v-v0 on each etale branch, so no rational h can give -D_v h=R2 row0 globally.',
 'scope':'Excludes Z=h beta wedge L for this fixed explicit L, with h any rational function in the full physical field, as a correction solving centered R2. It does not exclude general two-row mixed currents, different L, or the target problem. No new Q/beta replay and no trace-free assertion for a general root-dependent h.',
 'python':sys.version,'sympy':S.__version__
}
(HERE/'complementary-operator-residue.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('PASS:',len(checks),'new scoped checks and one sign control',flush=True)
watch.cancel()

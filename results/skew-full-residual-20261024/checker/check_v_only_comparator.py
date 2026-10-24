#!/usr/bin/env python3
"""V-only two-row comparator: formal identity and exact point jets.

All coefficient derivatives precede point evaluation, including t derivatives.
Independent truncated rational arithmetic is cross-checked against direct
symbolic alpha derivatives. This does not replay an earlier current identity.
"""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,threading,time
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--run',action='store_true')
p.add_argument('--connection',type=Path,default=Path(r'C:/Users/anaxe/Documents/Codex/hl-source-20261023/results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'))
args=p.parse_args()
if args.run:
    start=time.monotonic()
    try:out=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--connection',str(args.connection)],capture_output=True,text=True,encoding='utf-8',timeout=60)
    except subprocess.TimeoutExpired as ex:
        txt=lambda x:x.decode('utf-8',errors='replace') if isinstance(x,bytes) else (x or '')
        (HERE/'v-only-comparator-timeout.log').write_text(txt(ex.stdout)+txt(ex.stderr),encoding='utf-8');raise
    log=out.stdout+out.stderr;(HERE/'v-only-comparator.log').write_text(log,encoding='utf-8')
    print(out.stdout,end='');print(out.stderr,end='',file=sys.stderr)
    receipt={'exit_code':out.returncode,'wall_seconds':time.monotonic()-start,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'log_sha256':hashlib.sha256(log.encode('utf-8')).hexdigest(),'child_limit_seconds':60}
    rp=HERE/'v-only-comparator.json'
    if rp.exists():receipt['report_sha256']=hashlib.sha256(rp.read_bytes()).hexdigest()
    (HERE/'v-only-comparator-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt));sys.exit(out.returncode)
import sympy as S
from functools import lru_cache
watch=threading.Timer(58,lambda:os._exit(124));watch.daemon=True;watch.start()
a,b,c,d,v,t,r=S.symbols('a b c d v t r')
src=args.connection.read_bytes();source_sha=hashlib.sha256(src).hexdigest()
assert source_sha=='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
raw=json.loads(src);loc={str(x):x for x in (a,b,c,d)}
M={x:S.Matrix([[S.sympify(y,locals=loc) for y in row] for row in raw['connection'][str(x)]]) for x in (a,b,c,d)}
C=t*(1-t*t)/7;D=1+t**6;K0=C*C-3*t*v*D
w=C*S.diff(C,t)-2*t*v*S.diff(D,t)
q=3*D*S.diff(C,t)-2*C*S.diff(D,t)
Gv=-t*v*w+3*a*q-2*v*K0;Gt=2*t*K0
sub={b:t*v,c:C,d:D}
Mb,Mc,Md=[M[x].subs(sub,simultaneous=True) for x in (b,c,d)]
Nv=t*Mb;Nt=v*Mb+S.diff(C,t)*Mc+S.diff(D,t)*Md
Gamma=Gv*Nv+Gt*Nt
claimed=S.Matrix([[3*t*w/2,-t*q],[0,t*w/2]])
checks=[]
def check(name,x):
    vals=list(x) if isinstance(x,S.MatrixBase) else [x]
    got=[S.cancel(y) for y in vals];assert all(y==0 for y in got),(name,got)
    checks.append(name);print('PASS:',name,flush=True)
# The unrelated triangular draft failed its contraction test and is preserved
# separately. This script executes only the unaffected v-only comparator.

# Formal full-vector identity, with coefficient derivatives left independent.
phi,pv,gv,gg=S.symbols('chi chi_v chi_vv G_v')
AA=S.Matrix(S.symbols('A0:2'));BB=S.Matrix(S.symbols('B0:2'))
SS=AA/gg;DS=S.Matrix(S.symbols('DS0:2'));DT=S.Matrix(S.symbols('DT0:2'))
MM=S.Matrix(2,2,S.symbols('m0:4'))
TT=(v*BB-DS-MM*SS)/gg
formal_div=gg*SS*gv+(DS+gg*TT+MM*SS)*pv+(DT+MM*TT)*phi
formal_target=AA*gv+BB*(v*pv-phi)
check('formal two-row IBP identity',formal_target-formal_div-phi*(-BB-DT-MM*TT))

# Exact order-two jets around (a,v,t)=(3,2,1), with a held fixed.
mons=[(0,0),(1,0),(0,1),(2,0),(1,1),(0,2)];index={m:i for i,m in enumerate(mons)}
class Jet:
    def __init__(self,x=0):
        self.c=x.c[:] if isinstance(x,Jet) else ([S.Rational(z) for z in x] if isinstance(x,list) else [S.Rational(x),0,0,0,0,0])
    def __add__(self,x):
        x=Jet(x);return Jet([a+b for a,b in zip(self.c,x.c)])
    __radd__=__add__
    def __neg__(self):return Jet([-x for x in self.c])
    def __sub__(self,x):return self+-Jet(x)
    def __rsub__(self,x):return Jet(x)+-self
    def __mul__(self,x):
        x=Jet(x);out=[S.Integer(0)]*6
        for i,(u,w) in enumerate(mons):
            for j,(u2,w2) in enumerate(mons):
                m=(u+u2,w+w2)
                if m in index:out[index[m]]+=self.c[i]*x.c[j]
        return Jet(out)
    __rmul__=__mul__
    def inv(self):
        assert self.c[0]!=0
        n=self*(1/self.c[0])-1
        return (1-n+n*n)*(1/self.c[0])
    def __truediv__(self,x):return self*Jet(x).inv()
    def __rtruediv__(self,x):return Jet(x)*self.inv()
    def __pow__(self,n):
        n=int(n)
        if n<0:return self.inv()**(-n)
        z=Jet(1);x=self
        while n:
            if n&1:z=z*x
            x=x*x;n//=2
        return z
    def diff(self,k):
        out=[S.Integer(0)]*6
        for i,m in enumerate(mons):
            if m[k]:
                nxt=list(m);nxt[k]-=1;out[index[tuple(nxt)]]+=m[k]*self.c[i]
        return Jet(out)
    def at(self):return self.c[0]
vj=Jet([2,1,0,0,0,0]);tj=Jet([1,0,1,0,0,0]);aj=Jet(3)
env={a:aj,b:tj*vj,c:tj*(1-tj*tj)/7,d:1+tj**6,v:vj,t:tj}
@lru_cache(None)
def ev(x):
    if x in env:return env[x]
    if x.is_Rational:return Jet(x)
    if x.is_Add:return sum((ev(y) for y in x.args),Jet(0))
    if x.is_Mul:
        z=Jet(1)
        for y in x.args:z=z*ev(y)
        return z
    if x.is_Pow and x.exp.is_Integer:return ev(x.base)**int(x.exp)
    raise TypeError(x)
def mv(mat,vec):return [sum((mat[i][j]*vec[j] for j in range(2)),Jet(0)) for i in range(2)]
def jmatrix(mat):return [[ev(mat[i,j]) for j in range(2)] for i in range(2)]
nv=jmatrix(Nv);nt=jmatrix(Nt);mb=jmatrix(Mb)
alpha=[(nt[0][1]+vj/(3*aj))/(36*tj),nt[1][1]/(36*tj)]
beta=[mb[0][0]/(108*aj),mb[1][0]/(108*aj)]
point={a:S.Integer(3),v:S.Integer(2),t:S.Integer(1)}
alpha_expr=(Nt*S.Matrix([0,1])+v*S.Matrix([1,0])/(3*a))/(36*t)
for i in range(2):
    for j,x in enumerate((v,t)):
        check('independent alpha jet derivative '+str(i)+str(x),alpha[i].diff(j).at()-S.diff(alpha_expr[i],x).subs(point))
    check('independent alpha second-v jet '+str(i),alpha[i].diff(0).diff(0).at()-S.diff(alpha_expr[i],v,2).subs(point))

# Physical cover derivatives are computed afresh at the point, not frozen.
A=r**3+r**-3+(v*r-1)**6/r**15
rp={r:S.Integer(1),v:S.Integer(2)}
Ar=S.diff(A,r).subs(rp);Av=S.diff(A,v).subs(rp);rv=-Av/Ar
rvv=-(S.diff(A,v,2).subs(rp)+2*S.diff(A,r,v).subs(rp)*rv+S.diff(A,r,2).subs(rp)*rv**2)/Ar
ch=S.Rational(-5,3);chv=-3*rv-4;chvv=12*rv**2-3*rvv-4
assert (Ar,Av,chv,chvv)==(-3,6,-10,38)
target=S.Matrix([x.at()*chvv+y.at()*(2*chv-ch) for x,y in zip(alpha,beta)])

def run_current(label,g_v,g_t,gamma):
    assert g_v.at()!=0
    divg=g_v.diff(0)+g_t.diff(1)
    mm=[[gamma[i][j]+(divg if i==j else 0) for j in range(2)] for i in range(2)]
    ss=[x/g_v for x in alpha]
    ds=[g_v*x.diff(0)+g_t*x.diff(1) for x in ss]
    ms=mv(mm,ss)
    tt=[(vj*beta[i]-ds[i]-ms[i])/g_v for i in range(2)]
    mt=mv(mm,tt)
    coeff=S.Matrix([-beta[i].at()-g_v.at()*tt[i].diff(0).at()-g_t.at()*tt[i].diff(1).at()-mt[i].at() for i in range(2)])
    F=S.Matrix([ss[i].at()*chv+tt[i].at()*ch for i in range(2)])
    Fv=S.Matrix([ss[i].diff(0).at()*chv+ss[i].at()*chvv+tt[i].diff(0).at()*ch+tt[i].at()*chv for i in range(2)])
    Ft=S.Matrix([ss[i].diff(1).at()*chv+tt[i].diff(1).at()*ch for i in range(2)])
    gam0=S.Matrix([[gamma[i][j].at() for j in range(2)] for i in range(2)])
    div=g_v.at()*Fv+g_t.at()*Ft+divg.at()*F+gam0*F
    remainder=target-div
    check(label+' direct full point divergence',remainder-ch*coeff)
    assert any(x!=0 for x in remainder)
    # Deliberately change the sign of the connection contribution.
    mutation=target-(g_v.at()*Fv+g_t.at()*Ft+divg.at()*F-gam0*F)-ch*coeff
    assert any(x!=0 for x in mutation)
    print('REJECTED CONTROL:',label,'connection sign mutation',list(mutation),flush=True)
    print('RESULT:',label,'full remainder',list(remainder),flush=True)
    return {'Gv':str(g_v.at()),'Gt':str(g_t.at()),'Gamma':[[str(x) for x in row] for row in gam0.tolist()],
            'S':[str(x.at()) for x in ss],'T':[str(x.at()) for x in tt],
            'residual_coefficient':[str(x) for x in coeff],'full_residual':[str(x) for x in remainder],
            'sign_mutation_defect':[str(x) for x in mutation]}

simple=run_current('v-only comparator',Jet(1),Jet(0),nv)
report={
 'status':'V-only full two-row identity verified; displayed comparator has nonzero ordinary-point residual',
 'source_sha256':source_sha,'source_path':str(args.connection),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'checks':checks,
 'generic_identity':'S=alpha/Gv; T=(v beta-calD(S)-Mcal S)/Gv; R2-Div_N J=chi[-beta-calD(T)-Mcal T], with J_v=Gv(S chi_v+T chi), J_t=Gt(S chi_v+T chi).',
 'point':{'r':'1','a':'3','v':'2','t':'1','A_r':str(Ar),'A_v':str(Av),'chi':str(ch),'chi_v':str(chv),'chi_vv':str(chvv),'target_R2':[str(x) for x in target]},
 'v_only_point':simple,
 'comparator_generic_identity':'T0=v beta-partial_v(alpha)-N_v alpha; J_v=alpha chi_v+T0 chi; R2-Div_N J=chi[-beta-partial_v(T0)-N_v T0]. J_a=J_t=0.',
 'coefficient_derivative_method':'Exact order-two rational jets in v,t at fixed a; no t specialization before derivatives. Direct symbolic first alpha derivatives and second-v derivatives independently cross-check the jet engine.',
 'pole_scope':'The v-only comparator adds no Gv divisor. Its final residual has root dependence only through chi; its coefficient lies in Q(a,v,t), so no f_r denominator remains there. Current may still contain chi_v and its f_r denominator. This is not claimed as a newly discharged bottleneck; earlier source integrations already yield no-f_r representatives.',
 'trace_scope':'Coefficients lie in the base field. Thus centering of chi and chi_v transfers to this current and residual.',
 'limits':'Nonzero point values disprove full cancellation for this specific comparator. No general mixed-current exclusion, novel coverage, solution, or certificate is claimed. Existing Q/beta identities and simpler baselines were not replayed.',
 'python':sys.version,'sympy':S.__version__
}
(HERE/'v-only-comparator.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('PASS:',len(checks),'scoped checks and one connection-sign control',flush=True)
watch.cancel()

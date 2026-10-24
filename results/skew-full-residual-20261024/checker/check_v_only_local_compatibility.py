#!/usr/bin/env python3
"""Independent point-local full two-row residue compatibility test.

No replay of the cover gcd/residue nonvanishing calculation. Gamma and kappa
are placeholders for the full moving-root scalar values already defined.
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
        (HERE/'v-only-local-compatibility-timeout.log').write_text(txt(ex.stdout)+txt(ex.stderr),encoding='utf-8');raise
    log=out.stdout+out.stderr;(HERE/'v-only-local-compatibility.log').write_text(log,encoding='utf-8')
    print(out.stdout,end='');print(out.stderr,end='',file=sys.stderr)
    receipt={'exit_code':out.returncode,'wall_seconds':time.monotonic()-start,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'log_sha256':hashlib.sha256(log.encode('utf-8')).hexdigest(),'child_limit_seconds':60}
    rp=HERE/'v-only-local-compatibility.json'
    if rp.exists():receipt['report_sha256']=hashlib.sha256(rp.read_bytes()).hexdigest()
    (HERE/'v-only-local-compatibility-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt));sys.exit(out.returncode)
import sympy as S
watch=threading.Timer(58,lambda:os._exit(124));watch.daemon=True;watch.start()
a,b,c,d,v,t,lam,gamma,kappa=S.symbols('a b c d v t lambda gamma kappa')
src=args.connection.read_bytes();sha=hashlib.sha256(src).hexdigest()
assert sha=='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
raw=json.loads(src);loc={str(x):x for x in (a,b,c,d)}
M={x:S.Matrix([[S.sympify(y,locals=loc) for y in row] for row in raw['connection'][str(x)]]) for x in (a,b,c,d)}
C=t*(1-t*t)/7;D=1+t**6;sub={b:t*v,c:C,d:D}
Mb,Mc,Md=[M[x].subs(sub,simultaneous=True) for x in (b,c,d)]
Nv=t*Mb;Nt=v*Mb+S.diff(C,t)*Mc+S.diff(D,t)*Md
e0=S.Matrix([1,0]);e1=S.Matrix([0,1])
alpha=(Nt*e1+v*e0/(3*a))/(36*t);beta=Mb*e0/(108*a)
at={a:S.Integer(4),t:S.Integer(1)}
def residue(x):return S.cancel((v+6)*x.subs(at)).subs(v,-6)
R=Nv.applyfunc(residue);ar=alpha.applyfunc(residue);br=beta.applyfunc(residue)
checks=[]
def check(name,x):
    vals=list(x) if isinstance(x,S.MatrixBase) else [x]
    got=[S.cancel(y) for y in vals];assert all(y==0 for y in got),(name,got)
    checks.append(name);print('PASS:',name,flush=True)
check('full connection residue matrix',R+S.ones(2)/6)
check('residue characteristic polynomial',R.charpoly(lam).as_expr()-lam*(lam+S.Rational(1,3)))
check('both target alpha residue rows',ar-S.ones(2,1)/756)
check('both target beta residue rows',br+S.ones(2,1)/2592)
left=S.Matrix([[1,-1]])
check('left kernel',left*R)
s=gamma/756-kappa/2592
rhs=ar*gamma+br*kappa
check('full target residue vector',rhs-s*S.ones(2,1))
check('local compatibility projection',left*rhs)
leading=-3*s*S.ones(2,1)
check('regular leading current matches source pole',R*leading-rhs)
mutation=-R*leading-rhs
assert any(S.expand(x)!=0 for x in mutation)
print('REJECTED CONTROL: reverse leading current sign',list(mutation),flush=True)
prior=HERE/'complementary-operator-residue.json'
report={
 'status':'PASS: point-local coupled v-only residue compatibility; no general v-only exclusion follows',
 'source_path':str(args.connection),'source_sha256':sha,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'checks':checks,
 'point':{'a':'4','t':'1','v':'-6'},'connection_residue':[[str(x) for x in row] for row in R.tolist()],
 'characteristic_polynomial':str(R.charpoly(lam).as_expr()),'eigenvalues':['0','-1/3'],
 'target_residue':[str(x) for x in rhs],'left_kernel':['1','-1'],'left_kernel_projection':'0',
 'regular_leading_current':[str(x) for x in leading],'sign_mutation_defect':[str(x) for x in mutation],
 'scalar_placeholders':'gamma=chi_vv, kappa=v chi_v-chi, with full moving-root derivatives. Their residue-algebra nonvanishing and etaleness are reused, not rerun here.',
 'reused_residue_report_sha256':hashlib.sha256(prior.read_bytes()).hexdigest() if prior.exists() else None,
 'scope':'At this specified good discriminant point, the full target residue lies in the image of the coupled connection residue. This invalidates extending the fixed-L scalar-derivative obstruction to arbitrary two-row v-only currents. No generic-discriminant identity, rational v-only primitive, mixed-current solution, or certificate is claimed.',
 'pole_logic':'The local matrix has no positive-integer eigenvalues, so a rational solution to a simple-pole target cannot have a pole on these etale branches: its leading pole would require (R-kI)u=0 for k>=1. A regular leading coefficient can satisfy R Z0=Res R2, as explicitly shown. This is a necessary local compatibility check, not global rational solvability.',
 'python':sys.version,'sympy':S.__version__
}
(HERE/'v-only-local-compatibility.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('PASS:',len(checks),'point-local checks and one sign control',flush=True)
watch.cancel()

#!/usr/bin/env python3
"""Independent universal polynomial certificate of generic v-residue image.

Only the pinned connection JSON is algebra input. No point or cover-gcd test
is repeated. Polynomial remainders prove the generic discriminant statement.
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
        (HERE/'generic-v-residue-timeout.log').write_text(txt(ex.stdout)+txt(ex.stderr),encoding='utf-8');raise
    log=out.stdout+out.stderr;(HERE/'generic-v-residue.log').write_text(log,encoding='utf-8')
    print(out.stdout,end='');print(out.stderr,end='',file=sys.stderr)
    receipt={'exit_code':out.returncode,'wall_seconds':time.monotonic()-start,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'log_sha256':hashlib.sha256(log.encode('utf-8')).hexdigest(),'child_limit_seconds':60}
    rp=HERE/'generic-v-residue.json'
    if rp.exists():receipt['report_sha256']=hashlib.sha256(rp.read_bytes()).hexdigest()
    (HERE/'generic-v-residue-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt));sys.exit(out.returncode)
import sympy as S
watch=threading.Timer(58,lambda:os._exit(124));watch.daemon=True;watch.start()
a,b,c,d,t,v=S.symbols('a b c d t v');variables=(a,b,c,d)
data=args.connection.read_bytes();sha=hashlib.sha256(data).hexdigest()
assert sha=='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
raw=json.loads(data);loc={str(x):x for x in variables}
M={x:S.Matrix([[S.sympify(y,locals=loc) for y in row] for row in raw['connection'][str(x)]]) for x in variables}
Delta=S.sympify(raw['Delta'],locals=loc);Db=S.diff(Delta,b)
B=(Delta*M[b]).applyfunc(S.cancel);adj=B.adjugate();I=S.eye(2)
e0=S.Matrix([1,0]);e1=S.Matrix([0,1]);checks=[];quotients={}
def poly(x):return S.Poly(S.cancel(x),*variables,domain=S.QQ)
DP=poly(Delta)
def check(name,x):
    vals=list(x) if isinstance(x,S.MatrixBase) else [x]
    got=[S.cancel(y) for y in vals];assert all(y==0 for y in got),(name,got)
    checks.append(name);print('PASS:',name,flush=True)
def divisible(name,x):
    vals=list(x) if isinstance(x,S.MatrixBase) else [x];qs=[]
    for y in vals:
        qq,rr=poly(y).div(DP);assert rr.is_zero,(name,rr.as_expr());qs.append(str(qq.as_expr()))
    quotients[name]=qs;checks.append(name);print('PASS:',name,flush=True)
check('universal exact trace',S.trace(B)+Db/3)
divisible('determinant divisible by Delta',B.det())
H=b*d-c*c/12
check('determinant quotient',S.cancel(B.det())-Delta*H)
check('exact quadratic matrix identity',B*B+(Db/3)*B+Delta*H*I)
cols={
 'b-column0':B*e0,
 'b-column1':B*e1,
 'c-column1':(Delta*M[c]*e1).applyfunc(S.cancel),
 'd-column1':(Delta*M[d]*e1).applyfunc(S.cancel)
}
for name,col in cols.items():
    divisible('adjugate image '+name,adj*col)
    divisible('image eigenvalue '+name,(B+(Db/3)*I)*col)
physical={b:t*v,c:t*(1-t*t)/7,d:1+t**6}
check('physical v-transversality factor',S.diff(Delta.subs(physical,simultaneous=True),v)-t*Db.subs(physical,simultaneous=True))
# Differentiate no cover variables here: all columns are universal; regular
# scalar residue densities may live on the etale physical cover.
bad=(3*B-Db*I)*cols['b-column0']
bad_remainders=[poly(x).rem(DP).as_expr() for x in bad]
assert any(x!=0 for x in bad_remainders)
print('REJECTED CONTROL: leading +3 instead of -3 has nonzero Delta remainder',flush=True)
report={
 'status':'PASS: generic discriminant residue lies in coupled v-connection image; positive local compatibility, no global primitive',
 'source_path':str(args.connection),'source_sha256':sha,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'checks':checks,
 'B':[[str(x) for x in row] for row in B.tolist()],'Delta':str(Delta),'Delta_b':str(Db),
 'polynomial_quotients':quotients,'quadratic_identity':'B^2+(Delta_b/3)B=-Delta*(bd-c^2/12)*I',
 'negative_control':{'leading_factor':'+3 instead of -3','nonzero_remainders':[str(x) for x in bad_remainders]},
 'generic_residue_matrix':'C=B/Delta_b on Delta=0; rank1, trace -1/3, determinant0, C^2=-C/3',
 'source_binding':'rho=Res(R2 dv) is a scalar linear combination of columns (Delta M_b)e1,(Delta M_c)e1,(Delta M_d)e1,(Delta M_b)e0, divided by Delta_v=t Delta_b. The regular added v e0/(3a) term has no residue. gamma=chi_vv and kappa=v chi_v-chi are regular on the stated etale open.',
 'generic_consequence':'adj(B)rho=0 and rank(B)=1 imply rho in image(C); the checked eigenvalue identities directly give C rho=-rho/3. Thus Z0=-3rho+u, u in ker(C), is compatible leading divisor data.',
 'domain':'Characteristic zero; Delta=0, Delta_v=t Delta_b!=0, a!=0, r!=0, f_r!=0. Compact coefficient field K=Q(a,v,t)[r]/(f), equivalently Q(r,v,t) with a=A(r,v). No claim at tangency, cover ramification, or other excluded loci.',
 'local_pole_scope':'No positive-integer residue eigenvalue permits a pole in a rational v-only current against a simple-pole target. Compatible leading data exist. Subsequent formal recurrence uses nI+C with eigenvalues n,n-1/3 for n>=1, hence no further local resonance. This is local formal compatibility, not global rational solvability.',
 'limits':'No point calculation or cover gcd was repeated. No rational primitive, stronger mixed-current exclusion, global current, or certificate is supplied. This explains why the fixed-L scalar residue obstruction does not extend to coupled v-only currents.',
 'python':sys.version,'sympy':S.__version__
}
(HERE/'generic-v-residue.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('PASS:',len(checks),'generic polynomial checks and one sign control',flush=True)
watch.cancel()

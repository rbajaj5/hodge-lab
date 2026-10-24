#!/usr/bin/env python3
"""New complementary-beta candidate: exact row-0 integration coefficient test.

This does not check the pending full second-row/current formula.
"""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,threading,time
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--run',action='store_true')
p.add_argument('--connection',type=Path,default=Path(r'C:/Users/anaxe/Documents/Codex/hl-source-20261023/results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'))
args=p.parse_args()
if args.run:
    began=time.monotonic()
    try:
        out=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--connection',str(args.connection)],capture_output=True,text=True,encoding='utf-8',timeout=60)
    except subprocess.TimeoutExpired as exc:
        txt=lambda x:x.decode('utf-8',errors='replace') if isinstance(x,bytes) else (x or '')
        (HERE/'complementary-row0-timeout.log').write_text(txt(exc.stdout)+txt(exc.stderr),encoding='utf-8');raise
    log=out.stdout+out.stderr
    (HERE/'complementary-row0.log').write_text(log,encoding='utf-8')
    print(out.stdout,end='');print(out.stderr,end='',file=sys.stderr)
    receipt={'exit_code':out.returncode,'wall_seconds':time.monotonic()-began,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'log_sha256':hashlib.sha256(log.encode('utf-8')).hexdigest(),'child_limit_seconds':60}
    report=HERE/'complementary-row0.json'
    if report.exists():receipt['report_sha256']=hashlib.sha256(report.read_bytes()).hexdigest()
    (HERE/'complementary-row0-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(receipt));sys.exit(out.returncode)
import sympy as S
watch=threading.Timer(58,lambda:os._exit(124));watch.daemon=True;watch.start()
a,b,c,d,v,t=S.symbols('a b c d v t')
chi,chiv,g=S.symbols('chi chi_v chi_vv')
source=args.connection.read_bytes();source_sha=hashlib.sha256(source).hexdigest()
assert source_sha=='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
raw=json.loads(source);loc={str(x):x for x in (a,b,c,d)}
M={x:S.Matrix([[S.sympify(y,locals=loc) for y in row] for row in raw['connection'][str(x)]]) for x in (a,b,c,d)}
sub={b:t*v,c:t*(1-t*t)/7,d:1+t**6}
Mb,Mc,Md=[M[x].subs(sub,simultaneous=True) for x in (b,c,d)]
Nt=v*Mb+(1-3*t*t)*Mc/7+6*t**5*Md
alpha=S.cancel((Nt[0,1]+v/(3*a))/(36*t))
beta=S.cancel(Mb[0,0]/(108*a))
h=-alpha*chiv-(v*beta-S.diff(alpha,v))*chi
hv=S.diff(h,v)+chiv*S.diff(h,chi)+g*S.diff(h,chiv)
target=alpha*g+beta*(v*chiv-chi)
coefficient=S.cancel(S.diff(alpha,v,2)-2*beta-v*S.diff(beta,v))
assert S.cancel(target+hv-coefficient*chi)==0
print('PASS: proposed h leaves exactly (alpha_vv-2beta-v beta_v)*chi in row0',flush=True)
point={a:S.Integer(3),v:S.Integer(2),t:S.Integer(1),chi:-S.Rational(5,3),chiv:S.Integer(-10),g:S.Integer(38)}
cp=S.cancel(coefficient.subs(point))
remaining=S.cancel((target+hv).subs(point))
targetp=S.cancel(target.subs(point))
producedp=S.cancel((-hv).subs(point))
wrong=S.cancel((target-hv-coefficient*chi).subs(point))
assert wrong!=0 and not wrong.has(S.nan,S.zoo,S.oo)
print('REJECTED CONTROL: reverse current sign; exact row0 defect',wrong,flush=True)
if coefficient==0:
    print('RESULT: generic coefficient is ZERO; proposed current cancels row0 exactly',flush=True)
else:
    assert cp!=0
    print('RESULT: generic coefficient is NONZERO; point coefficient',cp,'and row0 remainder',remaining,flush=True)
assert targetp-producedp==remaining
report={
 'status':'row0 cancels exactly' if coefficient==0 else 'row0 does NOT cancel exactly',
 'source_path':str(args.connection),'source_sha256':source_sha,
 'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'alpha':str(alpha),'beta':str(beta),'h':str(h),
 'remaining_scalar_coefficient':str(S.factor(coefficient)),
 'generic_coefficient_zero':coefficient==0,
 'point':{str(x):str(y) for x,y in point.items()},
 'point_coefficient':str(cp),'point_target_row0':str(targetp),'point_produced_row0':str(producedp),'point_row0_remainder':str(remaining),
 'negative_control':{'reverse_current_sign_defect':str(wrong)},
 'assumptions':'L=L_a da+L_t dt depends only on a,t and beta0 wedge L=da wedge dt. Then Div_N(h beta wedge L)_0=-h_v. h_v is at fixed a,t; its formal chi derivatives include cover motion.',
 'scope':'Only the new proposed row0 integration formula is tested; no full second-row equation, full cancellation, rational primitive, or certificate is claimed.',
 'provenance':'Independent parallel Codex checker directly parses pinned public connection JSON; no author checker and no old Q/beta replay is imported.',
 'python':sys.version,'sympy':S.__version__
}
(HERE/'complementary-row0.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
watch.cancel()

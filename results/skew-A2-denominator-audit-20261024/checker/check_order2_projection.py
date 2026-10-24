#!/usr/bin/env python3
"""Independent new mixed-next-pole projection; no matrix search."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,threading,time
HERE=Path(__file__).resolve().parent
PIN='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
PRIOR='7493c4076b993709f51b15e612b2b102855887aba76d7907563addabfabf7af7'
p=argparse.ArgumentParser();p.add_argument('--child',action='store_true')
p.add_argument('--connection',type=Path,required=True);p.add_argument('--prior-structure',type=Path,required=True)
args=p.parse_args()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,obj):path.write_bytes((json.dumps(obj,indent=2,ensure_ascii=False)+'\n').encode('utf-8'))
if not args.child:
    start=time.monotonic();outer_timeout=False
    try:
        out=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--child','--connection',str(args.connection),'--prior-structure',str(args.prior_structure)],capture_output=True,env=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8'),timeout=60)
        stdout,stderr,code=out.stdout,out.stderr,out.returncode
    except subprocess.TimeoutExpired as ex:
        stdout,stderr,code=ex.stdout or b'',ex.stderr or b'',124;outer_timeout=True
    for stream,data in [('stdout',stdout),('stderr',stderr)]:
        (HERE/('order2-projection.'+stream+'.log')).write_bytes(data)
    receipt={'exit_code':code,'outer_timeout':outer_timeout,'child_watchdog_exit':code==124,
      'wall_seconds':time.monotonic()-start,'child_limit_seconds':60,'internal_watchdog_seconds':58,
      'stream_encoding':'UTF-8 raw bytes; no newline translation','script_sha256':sha(Path(__file__)),
      'connection_sha256':sha(args.connection),'prior_structure_sha256':sha(args.prior_structure),
      'stdout_sha256':sha(HERE/'order2-projection.stdout.log'),'stderr_sha256':sha(HERE/'order2-projection.stderr.log')}
    if (HERE/'order2-projection.json').exists():receipt['report_sha256']=sha(HERE/'order2-projection.json')
    save(HERE/'order2-projection-receipt.json',receipt)
    sys.stdout.buffer.write(stdout);sys.stderr.buffer.write(stderr);print(json.dumps(receipt));sys.exit(code)

import sympy as S
watch=threading.Timer(58,lambda:os._exit(124));watch.daemon=True;watch.start()
assert sha(args.connection)==PIN and sha(args.prior_structure)==PRIOR
assert sha(HERE/'order2-controls.json')=='4b6906e9e5423c4907ab1dd46f5fd919ad2d946455d3e0b0eeea7db77509d41f'
raw=json.loads(args.connection.read_bytes().decode('utf-8'))
prior=json.loads(args.prior_structure.read_bytes().decode('utf-8'))
a,b,c,d,r,v,t,x=S.symbols('a b c d r v t x')
loc={str(z):z for z in (a,b,c,d,r,v,t,x)}
M={key:S.Matrix([[S.sympify(z,locals=loc) for z in row] for row in entries]) for key,entries in raw['connection'].items()}
R=S.Matrix([[S.sympify(z,locals=loc) for z in row] for row in prior['residue_matrix']])
subst={a:0,b:t*v,c:t*(1-t**2)/7,d:1+t**6}
M0={key:M[key].applyfunc(lambda z:S.cancel(z.subs(subst))) for key in ('b','c','d')}
Tr=r**2*(r**6+1);Tv=r*(2*r**6+1)*v-(3*r**6+2)
q=3*r*(r**6-1);tau2=4*r**7+9*r
R0=R.subs({b:t*v,c:t*(1-t**2)/7})
K=(tau2*S.eye(2)+q*R0+t*Tv*M0['b']).applyfunc(S.cancel)
Nt0=(v*M0['b']+(1-3*t**2)*M0['c']/7+6*t**5*M0['d']).applyfunc(S.cancel)
expected=2*r**7+S.Rational(19,2)*r+(3*r**6+2)/(2*v)
assert K[1,0]==0 and Nt0[1,0]==0
assert S.cancel(K[1,1]-expected)==0 and S.cancel(Nt0[1,1]+1/(2*t))==0
print('PASS: source-derived second-row coefficients and zero lower-left couplings',flush=True)

H0,H1,H0r,H1r,K0,K1,K2,K0t,K1t,K2t=S.symbols('H0 H1 H0r H1r K0 K1 K2 K0t K1t K2t')
h=H0+v*H1;k=K0+v*K1+v**2*K2
W=Tr*(H0r+v*H1r)+Tv*H1+K[1,1]*h+(K0t+v*K1t+v**2*K2t)+Nt0[1,1]*k
pole=(3*r**6+2)*H0/(2*v)
poly=S.cancel(W-pole)
assert S.Poly(poly,v,domain='EX').degree()<=2
C=r**18+r**12;F=x**6+C
vinv=-r*(x**5-x**4+x**3-x**2+x-1)/(C+1)
def remainder(expr):
    return S.Poly(S.expand(expr),x,domain='EX').rem(S.Poly(F,x,domain='EX')).as_expr()
assert S.cancel(remainder((x+1)*vinv/r-1))==0
wrong=S.cancel(remainder((x+1)*(-vinv)/r-1))
assert wrong==-2
reduced=S.expand(poly.subs(v,(x+1)/r)+(3*r**6+2)*H0*vinv/2)
mu=r*(3*r**6+2)/(2*(C+1))
assert S.cancel(reduced.coeff(x,3)+mu*H0)==0
assert S.cancel(reduced.coeff(x,4)-mu*H0)==0
print('PASS: x^3,x^4 projections are -mu*H0,+mu*H0; wrong inverse sign rejected',flush=True)

# Reuse the prior exact normal-map remainder, extracting its new projections.
normal=S.sympify(prior['remainder_formula'],locals=loc)
assert S.expand(normal).coeff(x,3)==0 and S.expand(normal).coeff(x,4)==0
assert R[1,0]==0 and R[1,1]-1==-S.Rational(4,3)
print('PASS: mixed order2 equation forces H0=0 without forcing P1 tangent',flush=True)

report={
 'status':'PASS: necessary divisibility of second fibre component h2_1 by v; no full solve/exclusion',
 'script_sha256':sha(Path(__file__)),'connection_sha256':PIN,'prior_structure_sha256':PRIOR,
 'order2_controls_sha256':sha(HERE/'order2-controls.json'),
 'row_index_convention':'zero-based row1 is the second compact fibre component',
 'second_row_h_coefficient':str(expected),'second_row_Pt_coefficient':'-1/(2*t)',
 'lower_left_entries':'Both K[1,0] and Nt0[1,0] vanish exactly at a=0',
 'normal_map_prior_reuse':'The prior normal remainder is for F_r P_r+F_v P_v. The A normal map differs modulo F only by the unit r^-15, so its x3 and x4 projections also vanish.',
 'inverse_v_mod_F':str(vinv),'mu':str(mu),
 'projection_x3':'-mu*H0','projection_x4':'+mu*H0',
 'negative_control':{'mutation':'reverse sign of inverse_v','remainder_of_v_times_mutant_minus1':'-2'},
 'necessity':'The mixed next-pole equation is W2_1-(4/3)Q1_1=0. Q1_1 has zero x3,x4 projections; mu is a nonzero rational function of r. Thus H0=0 and h2_1=v*H1. No separate tangency condition on the A^-1 numerator is imposed.',
 'support_after_constraint':'h2 row0 retains30 terms; h2 row1 retains15 terms with v exponent1; P2_t retains234 terms total.',
 'safe_parameter_counts':{'pure_V_over_A2_necessary':279,'joint_V_plus_V_over_A_plus_V_over_A2_necessary':1683},
 'domain':'Generic r,t with r*t*(C+1)!=0 and the generic A=0,Delta!=0 locus. These denominators are nonzero rational functions; polynomial coefficient identities extend from this dense locus. No specialization to their zero sets is used.',
 'scope':'Only this necessary mixed next-pole consequence. Other next-pole equations may impose additional constraints. No matrix search, modular rank claim, all-current exclusion or primitive.',
 'python':sys.version,'sympy':S.__version__}
save(HERE/'order2-projection.json',report)
watch.cancel()

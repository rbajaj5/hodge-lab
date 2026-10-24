#!/usr/bin/env python3
"""Independent A-pole, tangent-module, and reciprocal-derivative checks.

No finite-field matrix search or full-residual solvability conclusion.
"""
from pathlib import Path
import argparse, hashlib, json, os, subprocess, sys, threading, time
HERE=Path(__file__).resolve().parent
PIN='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
p=argparse.ArgumentParser()
p.add_argument('--child',action='store_true')
p.add_argument('--connection',type=Path,default=Path('C:/Users/anaxe/Documents/Codex/hl-source-20261023/results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'))
args=p.parse_args()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,obj):path.write_bytes((json.dumps(obj,indent=2,ensure_ascii=False)+'\n').encode('utf-8'))
if not args.child:
    start=time.monotonic();outer_timeout=False
    env=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8')
    try:
        out=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--child','--connection',str(args.connection)],capture_output=True,env=env,timeout=60)
        stdout,stderr,code=out.stdout,out.stderr,out.returncode
    except subprocess.TimeoutExpired as ex:
        stdout,stderr,code=ex.stdout or b'',ex.stderr or b'',124;outer_timeout=True
    for stream,content in [('stdout',stdout),('stderr',stderr)]:
        (HERE/('structure-independent.'+stream+'.log')).write_bytes(content)
    receipt={'exit_code':code,'outer_timeout':outer_timeout,'child_watchdog_exit':code==124,
      'wall_seconds':time.monotonic()-start,'child_limit_seconds':60,'internal_watchdog_seconds':58,
      'stream_encoding':'UTF-8; raw bytes preserved without newline conversion',
      'script_sha256':sha(Path(__file__)),'connection_sha256':sha(args.connection),
      'stdout_sha256':sha(HERE/'structure-independent.stdout.log'),
      'stderr_sha256':sha(HERE/'structure-independent.stderr.log')}
    if (HERE/'structure-independent.json').exists():receipt['report_sha256']=sha(HERE/'structure-independent.json')
    save(HERE/'structure-independent-receipt.json',receipt)
    sys.stdout.buffer.write(stdout);sys.stderr.buffer.write(stderr);print(json.dumps(receipt));sys.exit(code)

import sympy as S
watch=threading.Timer(58,lambda:os._exit(124));watch.daemon=True;watch.start()
assert sha(args.connection)==PIN
raw=json.loads(args.connection.read_bytes().decode('utf-8'))
a,b,c,d,r,v,t,x,w=S.symbols('a b c d r v t x w')
loc={str(z):z for z in (a,b,c,d)}
M={key:S.Matrix([[S.sympify(z,locals=loc) for z in row] for row in rows]) for key,rows in raw['connection'].items()}
R=(a*M['a']).applyfunc(S.cancel).subs(a,0).applyfunc(S.cancel)
expectedR=S.Matrix([[0,-c/(6*b)],[0,-S.Rational(1,3)]])
assert (R-expectedR).applyfunc(S.cancel)==S.zeros(2)
assert S.cancel((R-S.eye(2)).det())==S.Rational(4,3)
for key in ('b','c','d'):
    for entry in M[key]:
        assert S.denom(S.cancel(entry)).subs(a,0)!=0
print('PASS: A-pole residue matrix, invertible R-I, and other directions/source regular in a',flush=True)

F=r**18+r**12+(r*v-1)**6
A_original=r**3+r**-3+(r*v-1)**6/r**15
A=F/r**15
assert S.cancel(A_original-A)==0
reciprocal=[]
for z in (r,v,t):
    lhs=S.diff(r**15/F,z)
    rhs=-S.diff(A_original,z)/A_original**2
    assert S.cancel(lhs-rhs)==0
    reciprocal.append(str(z))
assert S.diff(A_original,t)==0
point={r:S.Integer(1),v:S.Integer(2),t:S.Integer(1)}
mutations=[]
for z in (r,v):
    value=S.cancel(S.diff(r**15/F,z)).subs(point)
    assert value!=0
    mutations.append({'omitted_term':'-A_'+str(z)+'/A^2','correct_derivative':str(value),'mutated_derivative':'0'})
assert [row['correct_derivative'] for row in mutations]==['1/3','-2/3']
print('PASS: three reciprocal derivative identities; two omitted-quotient-term controls rejected',flush=True)

p0,p1,p2,q0,q1,q2=S.symbols('p0 p1 p2 q0 q1 q2')
P=p0+p1*x+p2*x**2;Q=q0+q1*x+q2*x**2
C=r**12*(r**6+1);H=x**6+C
F_r=S.diff(F,r).subs(v,(x+1)/r)
F_v=S.diff(F,v).subs(v,(x+1)/r)
actual=S.Poly(S.expand(F_r*P+F_v*Q),x,domain='EX').rem(S.Poly(H,x,domain='EX')).as_expr()
B=6*r**11*(2*r**6+1)
E0=p0+r**2*q0;E1=p1+r**2*q1;E2=p2+r**2*q2
predicted=6*E0*x**5/r+B*p2*x**2+(B*p1-6*C*E2/r)*x+B*p0-6*C*E1/r
assert S.expand(actual-predicted)==0
lam=(2*r**6+1)/(r**6+1)
substitution={p2:0,q0:-p0/r**2,q1:(lam*p0-p1)/r**2,q2:lam*p1/r**2}
assert S.cancel(actual.subs(substitution))==0
assert S.cancel(Q.subs(substitution)-((lam*x-1)/r**2)*(p0+p1*x))==0
print('PASS: complete degree-two tangency remainder equations and their parametrization',flush=True)

Tr=r**2*(r**6+1)
Tv=r*(2*r**6+1)*v-(3*r**6+2)
assert S.expand(Tr*S.diff(F,r)+Tv*S.diff(F,v)-6*r*(3*r**6+2)*F)==0
assert S.gcd(S.Poly(Tr,r,v),S.Poly(Tv,r,v)).as_expr()==1
assert S.cancel((6*r*(3*r**6+2)-15*Tr/r)-3*r*(r**6-1))==0
assert S.degree(Tr,r)==8 and S.Poly(Tr,r).coeff_monomial(r**2)==1
assert S.Poly(Tv,r).coeff_monomial(1)==-2
assert S.degree(Tv,v)==1
assert S.degree(S.Poly(Tv,v).coeff_monomial(v),r)==7
print('PASS: exact tangent vector, coprimality, and supporting extremal coefficients',flush=True)

# The Laurent coordinate change identifies A=0 with an irreducible smooth
# Fermat curve. Eisenstein at r^2+1 establishes irreducibility over Q(r).
assert S.cancel(A.subs(v,(r**2*w+1)/r)-r**-3*(r**6+w**6+1))==0
assert S.rem(r**6+1,r**2+1,r)==0
assert S.rem(r**6+1,(r**2+1)**2,r)!=0
delta=S.sympify(raw['Delta'],locals=loc)
delta0=S.expand(delta.subs({a:0,b:t*v,c:t*(1-t**2)/7,d:1+t**6}))
assert S.degree(delta0,v)==3
assert delta0!=0
print('PASS: Fermat coordinate identity, Eisenstein multiplicity, and generic Delta complement',flush=True)

report={
 'status':'PASS: necessary reduction of V/A family to 294 parameters; not a solvability or exclusion certificate',
 'script_sha256':sha(Path(__file__)),'connection_sha256':PIN,
 'repository_pin_observed_before_execution':'aa5a30dff2fd70994c48c484845981c141e77ef9',
 'residue_matrix':[[str(R[i,j]) for j in range(2)] for i in range(2)],
 'det_R_minus_I':'4/3','reciprocal_identities':reciprocal,'negative_controls':mutations,
 'tangent_vector':[str(Tr),str(Tv)],'tangent_identity':'T(A)=3*r*(r^6-1)*A',
 'remainder_formula':str(predicted),
 'necessity':'The A^-2 coefficient is (R-I)*(A_r P_r+A_v P_v); source and M_b,M_c,M_d have no a-pole on Delta!=0, so each fibre component is tangent modulo A.',
 'degree_solution':'p2=0; q0=-p0/r^2; q1=(lambda*p0-p1)/r^2; q2=lambda*p1/r^2; lambda=(2*r^6+1)/(r^6+1)',
 'support_reason':'Coprime Tr,Tv imply h lies in Q[r,r^-1,v,t]. The top r exponent of Tr is8, so max_r(h)<=-6. The unique trailing r term of Tv is-2, so min_r(h)>=-10. Its v-degree1 implies deg_v(h)<=1; Tr preserves the t-degree range0..2.',
 'reduced_family':'J_r=T_r*h/A, J_v=T_v*h/A, J_t=P_t/A; h has -10<=m<=-6,0<=n<=1,0<=k<=2; P_t is in the original117-monomial V. h and P_t are independent two-component vectors.',
 'counts':{'h_scalar':30,'P_t_scalar':117,'total_six_component_parameters':294,'optional_V_plus_V_over_A_necessary_parameters':996},
 'generic_locus':'r!=0 and the generic point of A=0 with Delta!=0. A=0 is irreducible (Eisenstein after Fermat coordinate change) and smooth on r!=0. The physical Delta at A=0 has v-degree3 and does not vanish identically on the v-degree6 divisor.',
 'scope':'Only an exact necessary parameter reduction. No matrix search, rank computation or full residual cancellation has been performed. The optional V+V/A statement preserves an independent regular V summand; it is a different family.',
 'source_binding':'r^-4 M_b e0/12, positive packet orientation; reused finished source conventions, not re-proved here',
 'python':sys.version,'sympy':S.__version__}
save(HERE/'structure-independent.json',report)
watch.cancel()

#!/usr/bin/env python3
"""Minimal new A^-2 identities; prior tangency and source evidence is reused."""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,threading,time
HERE=Path(__file__).resolve().parent
SOURCE_PIN='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
PRIOR_PIN='7493c4076b993709f51b15e612b2b102855887aba76d7907563addabfabf7af7'
p=argparse.ArgumentParser()
p.add_argument('--child',action='store_true')
p.add_argument('--connection',type=Path,required=True)
p.add_argument('--prior-structure',type=Path,required=True)
args=p.parse_args()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,obj):path.write_bytes((json.dumps(obj,indent=2,ensure_ascii=False)+'\n').encode('utf-8'))
if not args.child:
    start=time.monotonic();outer_timeout=False
    env=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8')
    try:
        out=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--child','--connection',str(args.connection),'--prior-structure',str(args.prior_structure)],capture_output=True,env=env,timeout=60)
        stdout,stderr,code=out.stdout,out.stderr,out.returncode
    except subprocess.TimeoutExpired as ex:
        stdout,stderr,code=ex.stdout or b'',ex.stderr or b'',124;outer_timeout=True
    for stream,content in [('stdout',stdout),('stderr',stderr)]:
        (HERE/('order2-controls.'+stream+'.log')).write_bytes(content)
    receipt={'exit_code':code,'outer_timeout':outer_timeout,'child_watchdog_exit':code==124,
      'wall_seconds':time.monotonic()-start,'child_limit_seconds':60,'internal_watchdog_seconds':58,
      'stream_encoding':'UTF-8; raw subprocess bytes without newline translation',
      'script_sha256':sha(Path(__file__)),'connection_sha256':sha(args.connection),
      'prior_structure_sha256':sha(args.prior_structure),
      'stdout_sha256':sha(HERE/'order2-controls.stdout.log'),'stderr_sha256':sha(HERE/'order2-controls.stderr.log')}
    if (HERE/'order2-controls.json').exists():receipt['report_sha256']=sha(HERE/'order2-controls.json')
    save(HERE/'order2-controls-receipt.json',receipt)
    sys.stdout.buffer.write(stdout);sys.stderr.buffer.write(stderr);print(json.dumps(receipt));sys.exit(code)

import sympy as S
watch=threading.Timer(58,lambda:os._exit(124));watch.daemon=True;watch.start()
assert sha(args.connection)==SOURCE_PIN
assert sha(args.prior_structure)==PRIOR_PIN
prior=json.loads(args.prior_structure.read_bytes().decode('utf-8'))
assert prior['connection_sha256']==SOURCE_PIN
r,v,t,b,c=S.symbols('r v t b c')
loc={str(z):z for z in (r,v,t,b,c)}
R=S.Matrix([[S.sympify(entry,locals=loc) for entry in row] for row in prior['residue_matrix']])
Tr,Tv=[S.sympify(entry,locals=loc) for entry in prior['tangent_vector']]
assert S.cancel((R-2*S.eye(2)).det())==S.Rational(14,3)
print('PASS: det(Res_a M_a-2I)=14/3 using pinned prior residue evidence',flush=True)

A=r**3+r**-3+(v*r-1)**6/r**15
F=r**18+r**12+(v*r-1)**6
for z in (r,v,t):
    assert S.cancel(S.diff(r**30/F**2,z)+2*S.diff(A,z)/A**3)==0
assert S.diff(A,t)==0
point={r:S.Integer(1),v:S.Integer(2),t:S.Integer(1)}
controls=[]
for z in (r,v):
    correct=S.diff(r**30/F**2,z).subs(point)
    wrong=(-S.diff(A,z)/A**3).subs(point)
    assert correct!=wrong
    controls.append({'coordinate':str(z),'correct_derivative':str(correct),
      'mutant_derivative':str(wrong),'mutation':'use pole-order1 derivative coefficient instead of2'})
assert [z['correct_derivative'] for z in controls]==['2/9','-4/9']
print('PASS: three second-order reciprocal identities; two coefficient-of2 controls rejected',flush=True)

q=3*r*(r**6-1)
tau2=S.expand(S.diff(Tr,r)+S.diff(Tv,v)-2*q)
assert S.expand(tau2-r*(4*r**6+9))==0
print('PASS: reduced scalar correction div(T)-2q=r*(4r^6+9)',flush=True)

# Formal local coefficient example: a nonzero lower-order transverse numerator
# can cancel a second-order contribution. This is not a global/current example.
H2=S.Matrix([1,0]);W1=S.Matrix([1,0])
assert (R-S.eye(2))*W1+H2==S.zeros(2,1)
assert W1!=S.zeros(2,1)
print('PASS: next-pole equation is coupled; vanishing does not separately force W1=0',flush=True)

report={
 'status':'PASS: minimal new order2 controls only; no new finite-family exclusion or primitive',
 'script_sha256':sha(Path(__file__)),'source_sha256':SOURCE_PIN,'prior_structure_sha256':PRIOR_PIN,
 'repository_pin_observed_before_execution':'fc4f38a338b47addf62d1bf699783302285378fe',
 'reciprocal_identities':3,'negative_controls':controls,
 'det_R_minus_2I':'14/3','tau2':str(tau2),
 'highest_pole':'For J=P2/A^2, the A^-3 coefficient is (R-2I)*(A_r P2_r+A_v P2_v). Its vanishing forces only P2 to be tangent modulo A.',
 'reused_support':'The prior exact low-v-degree tangent-module/support proof gives P2_r=T_r h2, P2_v=T_v h2; h2 has -10<=m<=-6,0<=n<=1,0<=k<=2 and P2_t is in V.',
 'reduced_order2_operator':'A^-2*[T_r h2_r+T_v h2_v+r(4r^6+9)h2+q A M_a h2+t T_v M_b h2+(partial_t+N_t)P2_t], q=3r(r^6-1)',
 'next_pole':'For the sum, A^-2 coefficient is H2+(R-I)*W1 on A=0, where W1=(A_r P1_r+A_v P1_v)|A=0 and H2 is the order2 reduced bracket restricted to A=0 (A M_a restricts to R). It is invalid to force W1=0 unless H2=0 has separately been established.',
 'formal_coupling_control':'H2=(1,0),W1=(1,0) satisfy H2+(R-I)W1=0 with W1 nonzero. This is a local coefficient demonstration, not a current in the declared global family.',
 'safe_parameter_counts':{'pure_V_over_A2_top_only':294,'joint_original_generators':2106,'joint_top_only_necessary_generators':1698},
 'joint_count_reason':'Regular V702 and A^-1 V702 remain unrestricted at the top-pole stage; only A^-2 V702 reduces to294.',
 'reused_domain':'Generic point of irreducible smooth A=0 on r!=0,Delta!=0, as established in the pinned prior structural report. No repeated chart/source/trace/tangency proof.',
 'source':'r^-4 M_b e0/12 in positive packet orientation; all physical directions and both fibre rows retained',
 'scope':'No exploratory matrix, rank calculation, kernel conclusion, full residual check or solvability claim. Wait for a concrete author artifact before the decisive audit.',
 'python':sys.version,'sympy':S.__version__}
save(HERE/'order2-controls.json',report)
watch.cancel()

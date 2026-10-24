#!/usr/bin/env python3
"""New order3 controls only; reuse pinned earlier source/tangency proof."""
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
        (HERE/('order3-controls.'+stream+'.log')).write_bytes(data)
    receipt={'exit_code':code,'outer_timeout':outer_timeout,'child_watchdog_exit':code==124,
      'wall_seconds':time.monotonic()-start,'child_limit_seconds':60,'internal_watchdog_seconds':58,
      'stream_encoding':'UTF-8 raw subprocess bytes without newline conversion',
      'script_sha256':sha(Path(__file__)),'connection_sha256':sha(args.connection),'prior_structure_sha256':sha(args.prior_structure),
      'stdout_sha256':sha(HERE/'order3-controls.stdout.log'),'stderr_sha256':sha(HERE/'order3-controls.stderr.log')}
    if (HERE/'order3-controls.json').exists():receipt['report_sha256']=sha(HERE/'order3-controls.json')
    save(HERE/'order3-controls-receipt.json',receipt)
    sys.stdout.buffer.write(stdout);sys.stderr.buffer.write(stderr);print(json.dumps(receipt));sys.exit(code)

import sympy as S
watch=threading.Timer(58,lambda:os._exit(124));watch.daemon=True;watch.start()
assert sha(args.connection)==PIN and sha(args.prior_structure)==PRIOR
prior=json.loads(args.prior_structure.read_bytes().decode('utf-8'))
assert prior['connection_sha256']==PIN
r,v,t,b,c=S.symbols('r v t b c');loc={str(z):z for z in (r,v,t,b,c)}
R=S.Matrix([[S.sympify(z,locals=loc) for z in row] for row in prior['residue_matrix']])
Tr,Tv=[S.sympify(z,locals=loc) for z in prior['tangent_vector']]
assert S.cancel((R-3*S.eye(2)).det())==10
print('PASS: det(R-3I)=10 using pinned prior residue evidence',flush=True)
A=r**3+r**-3+(v*r-1)**6/r**15
F=r**18+r**12+(v*r-1)**6
for z in (r,v,t):
    assert S.cancel(S.diff(r**45/F**3,z)+3*S.diff(A,z)/A**4)==0
assert S.diff(A,t)==0
point={r:S.Integer(1),v:S.Integer(2),t:S.Integer(1)}
controls=[]
for z in (r,v):
    correct=S.diff(r**45/F**3,z).subs(point)
    wrong=(-2*S.diff(A,z)/A**4).subs(point)
    assert correct!=wrong
    controls.append({'coordinate':str(z),'correct':str(correct),'mutant':str(wrong),'mutation':'use pole coefficient2 instead of3'})
assert [row['correct'] for row in controls]==['1/9','-2/9']
print('PASS: three A^-3 reciprocal identities; both wrong-pole-coefficient controls rejected',flush=True)
q=3*r*(r**6-1)
tau3=S.expand(S.diff(Tr,r)+S.diff(Tv,v)-3*q)
assert tau3==r**7+12*r
print('PASS: tau3=div(T)-3q=r^7+12r',flush=True)
H3=S.Matrix([2,0]);W2=S.Matrix([1,0])
assert H3+(R-2*S.eye(2))*W2==S.zeros(2,1) and W2!=S.zeros(2,1)
print('PASS: formal next-pole coupling does not force lower P2 tangent',flush=True)
report={
 'status':'PASS: minimal order3 identities only; no matrix/exclusion/primitive claim',
 'script_sha256':sha(Path(__file__)),'connection_sha256':PIN,'prior_structure_sha256':PRIOR,
 'repository_pin_observed_before_execution':'2dff6afddab993a216ba3f262197ae69aeb9143a',
 'reciprocal_identities':3,'negative_controls':controls,'det_R_minus_3I':'10','tau3':str(tau3),
 'highest_pole':'The A^-4 coefficient is (R-3I)*(A_r P3_r+A_v P3_v), forcing only the highest-pole numerator P3 tangent modulo A.',
 'reduced_operator':'A^-3*[T_r h3_r+T_v h3_v+(r^7+12r)h3+q A M_a h3+t T_v M_b h3+(partial_t+N_t)k3], q=3r(r^6-1)',
 'mixed_next_pole':'H3+(R-2I)W2=0 on A=0; W2 is the normal flux of the unrestricted lower P2 numerator. The prior A^2 restrictions do not transfer to P2 in this larger family.',
 'formal_coupling_control':'H3=(2,0),W2=(1,0) satisfy the next-pole equation with W2 nonzero. Formal local coefficient demonstration only, not a global bounded current.',
 'necessary_counts':{'pure_V_over_A3':294,'joint_original':2808,'joint_top_only':2400},
 'basis_scope':'V has -10<=m<=2 and0<=n,k<=2. Highest h3 has -10<=m<=-6,0<=n<=1,0<=k<=2 in both fibre components; k3 has full V. All three lower sectors P2,P1,P0 retain702 entries each.',
 'source':'r^-4 M_b e0/12 with connection(A_r M_a,A_v M_a+t M_b,N_t), all physical directions and both rows retained',
 'reused_evidence':'Pinned source/divisor/tangent-module/support theorem is reused, not rerun. Generic A=0,r!=0,Delta!=0 locus remains the same.',
 'scope':'No exploratory matrix, rank assumption, kernel claim, finite-family exclusion, target solve, or Lean result. Wait for a fixed author specification.',
 'python':sys.version,'sympy':S.__version__}
save(HERE/'order3-controls.json',report)
watch.cancel()

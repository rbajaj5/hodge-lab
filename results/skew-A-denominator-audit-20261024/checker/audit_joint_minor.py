#!/usr/bin/env python3
"""Independent reconstruction of the decisive joint-family augmented minor.

Uses rational-polynomial evaluation, symbolic physical Jacobians, the separately
checked reduced tangent operator, and normalized Gaussian elimination. Does not
execute the Pro lead or checker scripts and performs no exploratory search.
"""
from pathlib import Path
import argparse, hashlib, json, os, subprocess, sys, threading, time
HERE=Path(__file__).resolve().parent
PIN='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
p=argparse.ArgumentParser()
p.add_argument('--child',action='store_true')
p.add_argument('--packet',type=Path,required=True)
p.add_argument('--connection',type=Path,required=True)
args=p.parse_args()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,obj):path.write_bytes((json.dumps(obj,indent=2,ensure_ascii=False)+'\n').encode('utf-8'))
if not args.child:
    start=time.monotonic();outer_timeout=False
    env=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8')
    try:
        out=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--child','--packet',str(args.packet),'--connection',str(args.connection)],capture_output=True,env=env,timeout=60)
        stdout,stderr,code=out.stdout,out.stderr,out.returncode
    except subprocess.TimeoutExpired as ex:
        stdout,stderr,code=ex.stdout or b'',ex.stderr or b'',124;outer_timeout=True
    for stream,content in [('stdout',stdout),('stderr',stderr)]:
        (HERE/('joint-minor.'+stream+'.log')).write_bytes(content)
    receipt={'exit_code':code,'outer_timeout':outer_timeout,'child_watchdog_exit':code==124,
      'wall_seconds':time.monotonic()-start,'child_limit_seconds':60,'internal_watchdog_seconds':58,
      'stream_encoding':'UTF-8, raw subprocess bytes without newline conversion',
      'script_sha256':sha(Path(__file__)),'connection_sha256':sha(args.connection),
      'stdout_sha256':sha(HERE/'joint-minor.stdout.log'),'stderr_sha256':sha(HERE/'joint-minor.stderr.log')}
    if (HERE/'joint-minor.json').exists():receipt['report_sha256']=sha(HERE/'joint-minor.json')
    save(HERE/'joint-minor-receipt.json',receipt)
    sys.stdout.buffer.write(stdout);sys.stderr.buffer.write(stderr);print(json.dumps(receipt));sys.exit(code)

import numpy as np
import sympy as S
watch=threading.Timer(58,lambda:os._exit(124));watch.daemon=True;watch.start()
assert sha(args.connection)==PIN
lead=args.packet/'lead/sum-01/result'
inputs_path=lead/'inputs.json';matrix_path=lead/'augmented-matrix.csv'
order_path=args.packet/'checker/reduced-sum-01/result/minor-row-order.json'
assert sha(inputs_path)=='1ba4cb45c4bfe2b750ae15eebc23e5ea3c8beb9376638172164d845a9eeebcb2'
assert sha(matrix_path)=='dfd559995c74bf09fab0b74345a65672d80e0e19538e0b5db6c6393e5016babc'
assert sha(HERE/'structure-independent.json')=='7493c4076b993709f51b15e612b2b102855887aba76d7907563addabfabf7af7'
meta=json.loads(inputs_path.read_bytes().decode('utf-8'))
order=json.loads(order_path.read_bytes().decode('utf-8'))
prime=meta['prime'];assert prime==32003 and S.isprime(prime)
assert order['minor_row_set']==list(range(997))
assert order['determinant_of_first_997_rows_mod_32003']==26947
saved_full=np.loadtxt(matrix_path,delimiter=',',dtype=np.int64)
assert saved_full.shape==(1056,997) and meta['matrix_shape']==[1056,997]
assert np.all((saved_full>=0)&(saved_full<prime))
saved=saved_full[:997,:]
assert len(meta['samples'])==528
raw=json.loads(args.connection.read_bytes().decode('utf-8'))
a,b,c,d,r,v,t=S.symbols('a b c d r v t')
universals=(a,b,c,d);coords=(r,v,t);loc={str(z):z for z in universals}

# Independent rational-polynomial evaluator; no Pro AST evaluator is imported.
denominator_evaluations=0
def compiler(expr,symbols):
    num,den=S.fraction(S.cancel(expr))
    def terms(poly):
        answer=[]
        for ex,co in S.Poly(poly,*symbols,domain=S.QQ).terms():
            pp,qq=co.as_numer_denom();assert int(qq)%prime
            answer.append((ex,int(pp)*pow(int(qq),-1,prime)%prime))
        return answer
    ns,ds=terms(num),terms(den)
    def evaluate(values):
        global denominator_evaluations
        def calc(ts):
            total=0
            for ex,co in ts:
                z=co
                for value,power in zip(values,ex):z=z*pow(int(value),int(power),prime)%prime
                total=(total+z)%prime
            return total
        nn,dd=calc(ns),calc(ds)
        if not dd:raise ZeroDivisionError('Bad reduction at an evaluation denominator')
        denominator_evaluations+=1
        return nn*pow(dd,-1,prime)%prime
    return evaluate

M={str(z):[[compiler(S.sympify(entry,locals=loc),universals) for entry in row] for row in raw['connection'][str(z)]] for z in universals}
delta_expr=S.sympify(raw['Delta'],locals=loc)
assert S.expand(delta_expr.subs(a,0)-b**2*(4*b*d-c**2))==0
delta=compiler(delta_expr,universals)
A=r**3+r**-3+(v*r-1)**6/r**15
coefficient_expr=(A,t*v,t*(1-t**2)/7,1+t**6)
base=[compiler(expr,coords) for expr in coefficient_expr]
jac=[[compiler(S.diff(expr,z),coords) for expr in coefficient_expr] for z in coords]
Tr=r**2*(r**6+1);Tv=r*(2*r**6+1)*v-(3*r**6+2)
q=3*r*(r**6-1)
tau=S.expand(S.diff(Tr,r)+S.diff(Tv,v)-q)
assert tau==7*r**7+6*r
tangent=[compiler(expr,coords) for expr in (Tr,Tv,q,tau)]
exponents=[(m,n,k) for m in range(-10,3) for n in range(3) for k in range(3)]
hexponents=[(m,n,k) for m in range(-10,-5) for n in range(2) for k in range(3)]
hindices=np.array([exponents.index(ex) for ex in hexponents],dtype=np.int64)
mons=[r**m*v**n*t**k for m,n,k in exponents]
mon_eval=[compiler(expr,coords) for expr in mons]
derivative_eval=[[compiler(S.diff(expr,z),coords) for expr in mons] for z in coords]
basis=([['h',-1,j,*ex] for j in range(2) for ex in hexponents]
       +[['Pt',2,j,*ex] for j in range(2) for ex in exponents]
       +[['Laurent',i,j,*ex] for i in range(3) for j in range(2) for ex in exponents])
assert len(basis)==996 and basis==meta['basis'] and len({tuple(z) for z in basis})==996

rebuilt=np.zeros((997,997),dtype=np.int64)
mutation=None
for ip,sample in enumerate(meta['samples'][:499]):
    pt=sample['point'];assert len(pt)==3 and all(0<=int(z)<prime for z in pt)
    assert int(pt[0])!=0
    values=[fn(pt) for fn in base];avalue=values[0]
    deltavalue=delta(values)
    assert avalue!=0 and deltavalue!=0
    matrices=[[[fn(values) for fn in row] for row in M[str(z)]] for z in universals]
    jvalues=[[fn(pt) for fn in row] for row in jac]
    assert sample['domain']=={'a':avalue,'Ar':jvalues[0][0],'Av':jvalues[1][0],'Delta':deltavalue}
    connection=[[[sum(jvalues[direction][s]*matrices[s][i][j] for s in range(4))%prime for j in range(2)] for i in range(2)] for direction in range(3)]
    tr,tv,qv,tauv=[fn(pt) for fn in tangent]
    gamma=[[(qv*avalue*matrices[0][i][j]+int(pt[2])*tv*matrices[1][i][j])%prime for j in range(2)] for i in range(2)]
    mon=np.array([fn(pt) for fn in mon_eval],dtype=np.int64)
    deriv=[np.array([fn(pt) for fn in row],dtype=np.int64) for row in derivative_eval]
    hmon=mon[hindices]
    tangent_derivative=(tr*deriv[0][hindices]+tv*deriv[1][hindices]+tauv*hmon)%prime
    for i in range(2):
        row=2*ip+i
        if row>=997:continue
        for j in range(2):
            # Equation multiplied by A: the tangent and Pt columns have no1/A.
            rebuilt[row,j*30:(j+1)*30]=(gamma[i][j]*hmon+(tangent_derivative if i==j else 0))%prime
            start=60+j*117
            rebuilt[row,start:start+117]=(connection[2][i][j]*mon+(deriv[2] if i==j else 0))%prime
        for direction in range(3):
            for j in range(2):
                start=294+(2*direction+j)*117
                unscaled=(connection[direction][i][j]*mon+(deriv[direction] if i==j else 0))%prime
                rebuilt[row,start:start+117]=avalue*unscaled%prime
        rebuilt[row,-1]=avalue*pow(int(pt[0]),-4,prime)*pow(12,-1,prime)*matrices[1][i][0]%prime
    # Removing the quotient correction -q*h changes tau to div(T).
    if mutation is None and qv:
        row=2*ip;column=0;difference=qv*int(hmon[0])%prime
        assert difference!=0
        correct=int(rebuilt[row,column]);wrong=(correct+difference)%prime
        assert wrong!=int(saved[row,column])
        mutation={'omitted_term':'-q*h in A-scaled tangent operator (the denominator derivative)',
          'point_index':ip,'point':pt,'row':row,'column':column,
          'correct_entry':correct,'mutant_entry':wrong,'nonzero_difference':difference}

assert mutation is not None
if not np.array_equal(rebuilt,saved):
    where=np.argwhere(rebuilt!=saved)[0];pos=tuple(where)
    raise AssertionError(('matrix mismatch',where.tolist(),int(rebuilt[pos]),int(saved[pos])))
print('PASS: all994009 decisive-minor entries independently reconstructed at499 points',flush=True)
print('REJECTED CONTROL:',json.dumps(mutation),flush=True)
assert 2*(prime-1)**2<2**63
H=rebuilt.copy();det=1;swaps=0
for k in range(997):
    nz=np.flatnonzero(H[k:,k])
    if not len(nz):raise AssertionError(('singular augmented minor',k))
    pivotrow=k+int(nz[0])
    if pivotrow!=k:H[[k,pivotrow]]=H[[pivotrow,k]];det=-det;swaps+=1
    pivot=int(H[k,k]);det=det*pivot%prime
    H[k,k:]=H[k,k:]*pow(pivot,-1,prime)%prime
    if k<996:H[k+1:,k:]=(H[k+1:,k:]-H[k+1:,k,None]*H[k,k:])%prime
det%=prime
assert det==26947
print('PASS: independently computed augmented determinant26947 modulo32003',flush=True)
report={
 'status':'PASS: exact characteristic-zero exclusion of declared joint V+V/A family, using independently checked necessary reduction',
 'script_sha256':sha(Path(__file__)),'connection_sha256':PIN,
 'inputs_sha256':sha(inputs_path),'source_matrix_csv_sha256':sha(matrix_path),
 'author_validation_sha256':sha(lead/'validation.json'),'minor_order_sha256':sha(order_path),
 'structural_report_sha256':sha(HERE/'structure-independent.json'),
 'canonical_rebuilt_minor_bytes_sha256':hashlib.sha256(rebuilt.astype('<i8',copy=False).tobytes()).hexdigest(),
 'prime':prime,'prime_verified':True,'minor_shape':[997,997],'entries_checked':994009,
 'sample_points_checked':499,'denominator_evaluations':denominator_evaluations,
 'coefficient_columns':996,'basis_counts':{'h':60,'Pt':234,'Laurent':702},
 'determinant':det,'gaussian_row_swaps':swaps,'negative_control':mutation,
 'normalization':'Entire equation multiplied by A. Old Laurent columns scaled A; reduced tangent columns and Pt columns have no1/A; source A*r^-4 M_b e0/12.',
 'operator':'Coefficient Jacobians derive physical connection. Tangent column uses T_r*h_r+T_v*h_v+(divT-q)*h+q*A*M_a*h+t*T_v*M_b*h, q=3r(r^6-1). Pt uses partial_t+N_t.',
 'method':'Independently authored rational-polynomial evaluation and symbolic monomial derivatives; normalized-pivot Gaussian elimination. No Pro script execution, no new random points, no exploratory matrix search.',
 'Delta_at_a_zero':'b^2*(4*b*d-c^2), directly confirmed against pinned JSON. Opposite-sign prose in earlier external handoff is corrected here; historical receipts are unchanged.',
 'characteristic_zero_reason':'The integer lifts of these499 finite-field points have all rational input denominators prime to32003. Thus the rational997-square augmented determinant reduces to26947 and is nonzero. Its997 columns are independent, while coefficient count is996. This directly closes the kernel/rank upper-bound issue, without assuming unknown solution coefficients have denominators prime to32003.',
 'family_conclusion':'No full six-component current with every scalar component in V+V/A can solve the pinned equation; in particular none in V/A. V has -10<=m<=2,0<=n,k<=2. The original1404-generator sum is covered by the independently checked necessary996 family.',
 'limits':'Does not exclude larger supports, higher A-poles, extra denominators, arbitrary rational compact currents or fibre-dependent sextic functions. No target solve or homogeneous certificate. Only first997 rows reconstructed, not the remaining59 rows of the1056-row Pro matrix. Separate Pro replay/checker runs are not ours.',
 'python':sys.version,'numpy':np.__version__,'sympy':S.__version__}
save(HERE/'joint-minor.json',report)
watch.cancel()

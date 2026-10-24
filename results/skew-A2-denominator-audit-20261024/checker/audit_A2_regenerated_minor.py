#!/usr/bin/env python3
"""Independent fixed-specification A^2 minor regeneration, no Pro-code replay.

The deterministic specification was supplied explicitly while archive transfer
was pending. A separate later comparison is required for delivered-CSV binding.
"""
from pathlib import Path
import argparse,hashlib,json,os,random,subprocess,sys,threading,time
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
        (HERE/('A2-minor.'+stream+'.log')).write_bytes(data)
    receipt={'exit_code':code,'outer_timeout':outer_timeout,'child_watchdog_exit':code==124,
      'wall_seconds':time.monotonic()-start,'child_limit_seconds':60,'internal_watchdog_seconds':58,
      'stream_encoding':'UTF-8, raw subprocess bytes without newline translation','script_sha256':sha(Path(__file__)),
      'connection_sha256':sha(args.connection),'prior_structure_sha256':sha(args.prior_structure),
      'stdout_sha256':sha(HERE/'A2-minor.stdout.log'),'stderr_sha256':sha(HERE/'A2-minor.stderr.log')}
    for name in ('A2-minor.json','regenerated-inputs.json','regenerated-minor.npy'):
        if (HERE/name).exists():receipt[name+'_sha256']=sha(HERE/name)
    save(HERE/'A2-minor-receipt.json',receipt)
    sys.stdout.buffer.write(stdout);sys.stderr.buffer.write(stderr);print(json.dumps(receipt));sys.exit(code)

import numpy as np
import sympy as S
watch=threading.Timer(58,lambda:os._exit(124));watch.daemon=True;watch.start()
assert sha(args.connection)==PIN and sha(args.prior_structure)==PRIOR
assert sha(HERE/'order2-controls.json')=='4b6906e9e5423c4907ab1dd46f5fd919ad2d946455d3e0b0eeea7db77509d41f'
prime=32003;assert S.isprime(prime)
seed=2026102432;size=1699
raw=json.loads(args.connection.read_bytes().decode('utf-8'))
a,b,c,d,r,v,t=S.symbols('a b c d r v t')
universals=(a,b,c,d);coords=(r,v,t);loc={str(z):z for z in universals}
denominator_evaluations=0
def compiler(expr,symbols):
    num,den=S.fraction(S.cancel(expr))
    def terms(poly):
        out=[]
        for ex,co in S.Poly(poly,*symbols,domain=S.QQ).terms():
            pp,qq=co.as_numer_denom();assert int(qq)%prime
            out.append((ex,int(pp)*pow(int(qq),-1,prime)%prime))
        return out
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
        if not dd:raise ZeroDivisionError('Bad evaluation denominator')
        denominator_evaluations+=1
        return nn*pow(dd,-1,prime)%prime
    return evaluate

M={str(z):[[compiler(S.sympify(entry,locals=loc),universals) for entry in row] for row in raw['connection'][str(z)]] for z in universals}
delta=compiler(S.sympify(raw['Delta'],locals=loc),universals)
A=r**3+r**-3+(v*r-1)**6/r**15
coefficient_expr=(A,t*v,t*(1-t**2)/7,1+t**6)
base=[compiler(expr,coords) for expr in coefficient_expr]
jac=[[compiler(S.diff(expr,z),coords) for expr in coefficient_expr] for z in coords]
Tr=r**2*(r**6+1);Tv=r*(2*r**6+1)*v-(3*r**6+2);q=3*r*(r**6-1)
tau2=S.expand(S.diff(Tr,r)+S.diff(Tv,v)-2*q)
assert tau2==4*r**7+9*r
tangent=[compiler(expr,coords) for expr in (Tr,Tv,q,tau2)]
exponents=[(m,n,k) for m in range(-10,3) for n in range(3) for k in range(3)]
hexponents=[(m,n,k) for m in range(-10,-5) for n in range(2) for k in range(3)]
hindices=np.array([exponents.index(ex) for ex in hexponents],dtype=np.int64)
mons=[r**m*v**n*t**k for m,n,k in exponents]
mon_eval=[compiler(expr,coords) for expr in mons]
derivative_eval=[[compiler(S.diff(expr,z),coords) for expr in mons] for z in coords]
basis=([['h2',-1,j,*ex] for j in range(2) for ex in hexponents]
       +[['k2',2,j,*ex] for j in range(2) for ex in exponents]
       +[[sector,i,j,*ex] for sector in ('P1','P0') for i in range(3) for j in range(2) for ex in exponents])
assert len(basis)==1698 and len({tuple(z) for z in basis})==1698
assert sum(entry[0]=='h2' and entry[2]==1 and entry[4]==0 for entry in basis)==15

rng=random.Random(seed);samples=[];excluded=[]
rebuilt=np.zeros((size,size),dtype=np.int64);controls={}
while len(samples)<850:
    pt=[rng.randrange(1,prime) for _ in range(3)]
    values=[fn(pt) for fn in base];avalue=values[0];deltavalue=delta(values)
    if avalue==0 or deltavalue==0:
        excluded.append({'point':pt,'a':avalue,'Delta':deltavalue});continue
    ip=len(samples)
    matrices=[[[fn(values) for fn in row] for row in M[str(z)]] for z in universals]
    jvalues=[[fn(pt) for fn in row] for row in jac]
    samples.append({'point':pt,'domain':{'a':avalue,'Ar':jvalues[0][0],'Av':jvalues[1][0],'Delta':deltavalue}})
    connection=[[[sum(jvalues[direction][s]*matrices[s][i][j] for s in range(4))%prime for j in range(2)] for i in range(2)] for direction in range(3)]
    tr,tv,qv,tauv=[fn(pt) for fn in tangent]
    gamma=[[(qv*avalue*matrices[0][i][j]+pt[2]*tv*matrices[1][i][j])%prime for j in range(2)] for i in range(2)]
    mon=np.array([fn(pt) for fn in mon_eval],dtype=np.int64)
    deriv=[np.array([fn(pt) for fn in row],dtype=np.int64) for row in derivative_eval]
    hmon=mon[hindices]
    tangent_derivative=(tr*deriv[0][hindices]+tv*deriv[1][hindices]+tauv*hmon)%prime
    asquare=avalue*avalue%prime
    for i in range(2):
        row=2*ip+i
        if row>=size:continue
        for j in range(2):
            rebuilt[row,j*30:(j+1)*30]=(gamma[i][j]*hmon+(tangent_derivative if i==j else 0))%prime
            start=60+j*117
            rebuilt[row,start:start+117]=(connection[2][i][j]*mon+(deriv[2] if i==j else 0))%prime
        for direction in range(3):
            for j in range(2):
                block=(2*direction+j)*117
                ordinary=(connection[direction][i][j]*mon+(deriv[direction] if i==j else 0))%prime
                rebuilt[row,294+block:294+block+117]=(avalue*ordinary-(jvalues[direction][0]*mon if i==j else 0))%prime
                rebuilt[row,996+block:996+block+117]=asquare*ordinary%prime
        rebuilt[row,-1]=asquare*pow(pt[0],-4,prime)*pow(12,-1,prime)*matrices[1][i][0]%prime
    if 'order2_wrong_pole_coefficient' not in controls and qv:
        correct=int(rebuilt[2*ip,0]);difference=qv*int(hmon[0])%prime
        assert difference
        controls['order2_wrong_pole_coefficient']={'point_index':ip,'row':2*ip,'column':0,'correct':correct,'mutant':(correct+difference)%prime,'difference':difference,'mutation':'use divT-q instead of divT-2q'}
    if 'lower_order_omitted_denominator_derivative' not in controls and jvalues[0][0]:
        correct=int(rebuilt[2*ip,294]);difference=jvalues[0][0]*int(mon[0])%prime
        assert difference
        controls['lower_order_omitted_denominator_derivative']={'point_index':ip,'row':2*ip,'column':294,'correct':correct,'mutant':(correct+difference)%prime,'difference':difference,'mutation':'omit -A_r*u from A-scaled lower-pole column'}

assert len(controls)==2 and np.all((rebuilt>=0)&(rebuilt<prime))
metadata={'prime':prime,'seed':seed,'basis':basis,'samples':samples,'excluded_points':excluded,
 'matrix_shape':[size,size],'convention':'sample0-row0,sample0-row1,...; first1699 rows; last column source',
 'specification_origin':'Explicit coordinator fallback handoff; independent deterministic regeneration, not yet compared with delivered CSV',
 'selection':'random.Random(2026102432); each coordinate rng.randrange(1,32003); discard only A==0 or literal JSON Delta==0; first850 accepted points',
 'source_sha256':PIN,'projection1683_used':False}
save(HERE/'regenerated-inputs.json',metadata)
np.save(HERE/'regenerated-minor.npy',rebuilt.astype('<u2'),allow_pickle=False)
print('PASS: fixed specification independently regenerated2886601 entries at850 good points',flush=True)
print('REJECTED CONTROLS:',json.dumps(controls),flush=True)
H=rebuilt.copy();det=1;swaps=0
assert 2*(prime-1)**2<2**63
for k in range(size):
    nz=np.flatnonzero(H[k:,k])
    if not len(nz):raise AssertionError(('singular augmented minor',k))
    pivotrow=k+int(nz[0])
    if pivotrow!=k:H[[k,pivotrow]]=H[[pivotrow,k]];det=-det;swaps+=1
    pivot=int(H[k,k]);det=det*pivot%prime
    H[k,k:]=H[k,k:]*pow(pivot,-1,prime)%prime
    if k<size-1:H[k+1:,k:]=(H[k+1:,k:]-H[k+1:,k,None]*H[k,k:])%prime
det%=prime
assert det==14098
print('PASS: independent normalized Gaussian determinant14098 modulo32003',flush=True)
report={
 'status':'PASS: independently regenerated exact characteristic-zero exclusion for declared V+V/A+V/A^2 family',
 'script_sha256':sha(Path(__file__)),'connection_sha256':PIN,'prior_structure_sha256':PRIOR,
 'order2_controls_sha256':sha(HERE/'order2-controls.json'),
 'regenerated_inputs_sha256':sha(HERE/'regenerated-inputs.json'),'saved_minor_sha256':sha(HERE/'regenerated-minor.npy'),
 'canonical_minor_int64_bytes_sha256':hashlib.sha256(rebuilt.astype('<i8',copy=False).tobytes()).hexdigest(),
 'prime':prime,'prime_verified':True,'seed':seed,'minor_shape':[size,size],'entries_regenerated':size*size,
 'sample_points':850,'excluded_points':len(excluded),'denominator_evaluations':denominator_evaluations,
 'coefficient_columns':1698,'basis_counts':{'h2':60,'k2':234,'P1':702,'P0':702},
 'projection1683_used':False,'determinant':det,'gaussian_row_swaps':swaps,'negative_controls':controls,
 'normalization':'Whole equation multiplied by A^2; h2 tangent columns use tau2, k2 uses partial_t+Nt, P1 uses A(partial_i+Ni)-Ai, P0 uses A^2(partial_i+Ni), source A^2*r^-4 Mb e0/12',
 'provenance':'Independently authored rational-polynomial evaluator and symbolic physical Jacobian/monomial derivatives, reduced tangent operator, normalized Gaussian elimination. No Pro script run; no exploratory search. Fixed explicit seed/basis/row specification supplied by coordinator.',
 'delivered_csv_comparison':'Not performed in this execution; preserve this report and add a separate binding receipt after download.',
 'characteristic_zero_reason':'All input denominators are units modulo32003 at the integer lifts of the850 sample points. The rational1699-square augmented determinant therefore reduces to14098 and is nonzero. There are only1698 coefficient columns, so no rational constant coefficient vector solves the necessary evaluations. Unknown coefficient denominators need not be prime to32003. The rank obstruction persists after any characteristic-zero constant-field extension.',
 'structural_dependency':'The prior low-degree tangent/support theorem plus new invertibility of R-2I restrict only the highest-pole numerator, leaving all702 P1 coefficients. This necessary1698 family contains every possible solution in the declared original2106-generator sum. The additional1683 projection is unused.',
 'scope':'Excludes only full six-component V+V/A+V/A^2 and its subfamily V/A^2 with the stated monomial box. Does not exclude larger supports, A^-3 or other denominators, arbitrary rational compact currents, fibre-dependent sextic functions, or solve the full target.',
 'python':sys.version,'numpy':np.__version__,'sympy':S.__version__}
save(HERE/'A2-minor.json',report)
watch.cancel()

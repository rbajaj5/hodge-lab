#!/usr/bin/env python3
"""Independent reconstruction of the predeclared A^4 augmented minor.

Reuses this checker's rational-polynomial evaluator, not Pro's implementation.
Only the fixed first 3103 rows are built; no point/minor search is performed.
"""
from pathlib import Path
import argparse,hashlib,json,os,random,subprocess,sys,threading,time
HERE=Path(__file__).resolve().parent
PIN='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
PRIOR='7493c4076b993709f51b15e612b2b102855887aba76d7907563addabfabf7af7'
p=argparse.ArgumentParser();p.add_argument('--child',action='store_true')
p.add_argument('--connection',type=Path,required=True);p.add_argument('--prior-structure',type=Path,required=True)
p.add_argument('--prior-A3-report',dest='prior_A3_report',type=Path,required=True)
p.add_argument('--prime',type=int,default=32003);p.add_argument('--seed',type=int,required=True)
p.add_argument('--author-points',type=int,required=True)
args=p.parse_args()
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def save(path,obj):path.write_bytes((json.dumps(obj,indent=2,ensure_ascii=False)+'\n').encode('utf-8'))
if not args.child:
    start=time.monotonic();outer_timeout=False
    command=[sys.executable,str(Path(__file__).resolve()),'--child','--connection',str(args.connection),'--prior-structure',str(args.prior_structure),'--prior-A3-report',str(args.prior_A3_report),'--prime',str(args.prime),'--seed',str(args.seed),'--author-points',str(args.author_points)]
    try:
        out=subprocess.run(command,capture_output=True,env=dict(os.environ,PYTHONUTF8='1',PYTHONIOENCODING='utf-8'),timeout=60)
        stdout,stderr,code=out.stdout,out.stderr,out.returncode
    except subprocess.TimeoutExpired as ex:
        stdout,stderr,code=ex.stdout or b'',ex.stderr or b'',124;outer_timeout=True
    for stream,data in [('stdout',stdout),('stderr',stderr)]:
        (HERE/('A4-minor.'+stream+'.log')).write_bytes(data)
    receipt={'exit_code':code,'outer_timeout':outer_timeout,'child_watchdog_exit':code==124 and not outer_timeout,
      'wall_seconds':time.monotonic()-start,'child_limit_seconds':60,'internal_watchdog_seconds':58,
      'command':command,'stream_encoding':'UTF-8, raw subprocess bytes without newline translation',
      'script_sha256':sha(Path(__file__)),'connection_sha256':sha(args.connection),'prior_structure_sha256':sha(args.prior_structure),
      'stdout_sha256':sha(HERE/'A4-minor.stdout.log'),'stderr_sha256':sha(HERE/'A4-minor.stderr.log')}
    for name in ('A4-minor.json','regenerated-inputs.json','regenerated-minor.npy'):
        if (HERE/name).exists():receipt[name+'_sha256']=sha(HERE/name)
    save(HERE/'A4-minor-receipt.json',receipt)
    sys.stdout.buffer.write(stdout);sys.stderr.buffer.write(stderr);print(json.dumps(receipt));sys.exit(code)

watch=threading.Timer(58,lambda:os._exit(124));watch.daemon=True;watch.start()
math_start=time.monotonic()
import numpy as np
import sympy as S
import flint
assert sha(args.connection)==PIN and sha(args.prior_structure)==PRIOR
assert sha(args.prior_A3_report)=='6c2ed5fc2d425e6c3121ffd481d21b742e335fad9c29754f7bb36f497fa57cfc'
prime=args.prime;assert S.isprime(prime) and prime<65536
seed=args.seed;size=3103;point_count=(size+1)//2
assert args.author_points>=point_count
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
tau4=S.expand(S.diff(Tr,r)+S.diff(Tv,v)-4*q)
assert tau4==-2*r**7+15*r
prior=json.loads(args.prior_structure.read_bytes().decode('utf-8'))
R=S.Matrix([[S.sympify(entry,locals=loc) for entry in row] for row in prior['residue_matrix']])
assert S.cancel((R-4*S.eye(2)).det())==S.Rational(52,3)
reciprocal_symbol=S.Symbol('u')
assert S.diff(reciprocal_symbol**-4,reciprocal_symbol)+4*reciprocal_symbol**-5==0
tangent=[compiler(expr,coords) for expr in (Tr,Tv,q,tau4)]
exponents=[(m,n,k) for m in range(-10,3) for n in range(3) for k in range(3)]
hexponents=[(m,n,k) for m in range(-10,-5) for n in range(2) for k in range(3)]
hindices=np.array([exponents.index(ex) for ex in hexponents],dtype=np.int64)
mons=[r**m*v**n*t**k for m,n,k in exponents]
mon_eval=[compiler(expr,coords) for expr in mons]
derivative_eval=[[compiler(S.diff(expr,z),coords) for expr in mons] for z in coords]
basis=([['h4',-1,j,*ex] for j in range(2) for ex in hexponents]
       +[['k4',2,j,*ex] for j in range(2) for ex in exponents]
       +[[sector,i,j,*ex] for sector in ('P3','P2','P1','P0') for i in range(3) for j in range(2) for ex in exponents])
assert len(basis)==3102 and len({tuple(z) for z in basis})==3102
assert {sector:sum(entry[0]==sector for entry in basis) for sector in ('h4','k4','P3','P2','P1','P0')}=={'h4':60,'k4':234,'P3':702,'P2':702,'P1':702,'P0':702}
assert sum(entry[0]=='h4' and entry[2]==1 and entry[4]==0 for entry in basis)==15

rng=random.Random(seed);samples=[];excluded=[]
rebuilt=np.zeros((size,size),dtype=np.int64);controls={}
while len(samples)<point_count:
    pt=[rng.randrange(1,prime) for _ in range(3)]
    values=[fn(pt) for fn in base];avalue=values[0];deltavalue=delta(values)
    if avalue==0 or deltavalue==0:
        excluded.append({'point':pt,'a':avalue,'Delta':deltavalue,'reason':'A or Delta zero'});continue
    try:
        matrices=[[[fn(values) for fn in row] for row in M[str(z)]] for z in universals]
    except ZeroDivisionError:
        excluded.append({'point':pt,'a':avalue,'Delta':deltavalue,'reason':'literal connection denominator zero'});continue
    ip=len(samples)
    jvalues=[[fn(pt) for fn in row] for row in jac]
    samples.append({'point':pt,'domain':{'a':avalue,'Ar':jvalues[0][0],'Av':jvalues[1][0],'Delta':deltavalue}})
    connection=[[[sum(jvalues[direction][s]*matrices[s][i][j] for s in range(4))%prime for j in range(2)] for i in range(2)] for direction in range(3)]
    tr,tv,qv,tauv=[fn(pt) for fn in tangent]
    gamma=[[(qv*avalue*matrices[0][i][j]+pt[2]*tv*matrices[1][i][j])%prime for j in range(2)] for i in range(2)]
    mon=np.array([fn(pt) for fn in mon_eval],dtype=np.int64)
    deriv=[np.array([fn(pt) for fn in row],dtype=np.int64) for row in derivative_eval]
    hmon=mon[hindices]
    tangent_derivative=(tr*deriv[0][hindices]+tv*deriv[1][hindices]+tauv*hmon)%prime
    asquare=avalue*avalue%prime;acube=asquare*avalue%prime;afour=acube*avalue%prime
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
                normal=jvalues[direction][0]*mon if i==j else 0
                rebuilt[row,294+block:294+block+117]=(avalue*ordinary-3*normal)%prime
                rebuilt[row,996+block:996+block+117]=(asquare*ordinary-2*avalue*normal)%prime
                rebuilt[row,1698+block:1698+block+117]=(acube*ordinary-asquare*normal)%prime
                rebuilt[row,2400+block:2400+block+117]=afour*ordinary%prime
        rebuilt[row,-1]=afour*pow(pt[0],-4,prime)*pow(12,-1,prime)*matrices[1][i][0]%prime
    if 'top_wrong_order3_tau' not in controls and qv:
        correct=int(rebuilt[2*ip,0]);difference=qv*int(hmon[0])%prime
        assert difference
        controls['top_wrong_order3_tau']={'point_index':ip,'row':2*ip,'column':0,'correct':correct,'mutant':(correct+difference)%prime,'difference':difference,'mutation':'use divT-3q instead of divT-4q'}
    if 'P3_wrong_pole_coefficient' not in controls and jvalues[0][0]:
        correct=int(rebuilt[2*ip,294]);difference=jvalues[0][0]*int(mon[0])%prime
        assert difference
        controls['P3_wrong_pole_coefficient']={'point_index':ip,'row':2*ip,'column':294,'correct':correct,'mutant':(correct+difference)%prime,'difference':difference,'mutation':'use -2*A_r*u instead of -3*A_r*u in A-scaled P3 column'}
    if 'P1_omitted_quotient_derivative' not in controls and jvalues[0][0]:
        correct=int(rebuilt[2*ip,1698]);difference=asquare*jvalues[0][0]*int(mon[0])%prime
        assert difference
        controls['P1_omitted_quotient_derivative']={'point_index':ip,'row':2*ip,'column':1698,'correct':correct,'mutant':(correct+difference)%prime,'difference':difference,'mutation':'omit -A^2*A_r*u from A^3-scaled P1 column'}
assert len(controls)==3 and np.all((rebuilt>=0)&(rebuilt<prime))
metadata={'prime':prime,'seed':seed,'basis':basis,'samples':samples,'excluded_points':excluded,
 'matrix_shape':[size,size],'convention':'sample0-row0,sample0-row1,...; first3103 rows; last column positive source',
 'specification_origin':'Coordinator fixed explicit handoff; independent deterministic reconstruction, not yet compared with delivered CSV',
 'selection':f'random.Random({seed}); each coordinate rng.randrange(1,{prime}); discard A==0, literal JSON Delta==0, or any literal connection denominator zero; first{point_count} accepted points',
 'full_author_specification':f'{args.author_points} accepted triples, row0 then row1; only first3103 rows reconstructed here',
 'source_sha256':PIN,'all_lower_coefficients_preserved':True,'lower_A2_projection_used':False}
save(HERE/'regenerated-inputs.json',metadata)
np.save(HERE/'regenerated-minor.npy',rebuilt.astype('<u2'),allow_pickle=False)
reconstruction_seconds=time.monotonic()-math_start
print('PASS: independently reconstructed 9628609 entries at 1552 good points',flush=True)
print('REJECTED CONTROLS:',json.dumps(controls),flush=True)
det_start=time.monotonic()
matrix=flint.nmod_mat(size,size,rebuilt.ravel().tolist(),prime)
det=int(matrix.det())
determinant_seconds=time.monotonic()-det_start
print('EXACT DETERMINANT:',det,'modulo',prime,'using python-flint',flint.__version__,flush=True)
report={
 'status':'PASS: declared finite family excluded' if det else 'ZERO: this fixed minor gives no exclusion',
 'script_sha256':sha(Path(__file__)),'connection_sha256':PIN,'prior_structure_sha256':PRIOR,
 'reused_A3_report_sha256':sha(args.prior_A3_report),
 'new_order4_controls':{'det_R_minus_4I':'52/3','tau4':str(tau4),'abstract_reciprocal_rule':'d(u^-4)/du=-4u^-5'},
 'regenerated_inputs_sha256':sha(HERE/'regenerated-inputs.json'),'saved_minor_sha256':sha(HERE/'regenerated-minor.npy'),
 'canonical_minor_int64_bytes_sha256':hashlib.sha256(rebuilt.astype('<i8',copy=False).tobytes()).hexdigest(),
 'prime':prime,'prime_verified':True,'seed':seed,'minor_shape':[size,size],'entries_regenerated':size*size,
 'sample_points':point_count,'excluded_points':len(excluded),'denominator_evaluations':denominator_evaluations,
 'coefficient_columns':3102,'basis_counts':{'h4':60,'k4':234,'P3':702,'P2':702,'P1':702,'P0':702},
 'all_lower_coefficients_preserved':True,'lower_A2_projection_used':False,'determinant':det,'negative_controls':controls,
 'reconstruction_seconds':reconstruction_seconds,'determinant_seconds':determinant_seconds,
 'normalization':'Whole equation multiplied by A^4; h4 tangent columns use tau4, k4 uses partial_t+Nt, P3 uses A(partial_i+Ni)-3Ai, P2 uses A^2(partial_i+Ni)-2A*Ai, P1 uses A^3(partial_i+Ni)-A^2*Ai, P0 uses A^4(partial_i+Ni), source A^4*r^-4 Mb e0/12',
 'provenance':'Independently authored rational-polynomial evaluator, symbolic physical Jacobian and monomial derivatives, and reduced tangent operator. Exact determinant by FLINT through python-flint nmod_mat.det, not an independently authored elimination algorithm. No Pro script replay or exploratory search.',
 'delivered_csv_comparison':'Not performed in this execution; preserve this report and add a separate binding receipt after download.',
 'characteristic_zero_reason':'If determinant is nonzero: all input denominators are units modulo the recorded prime at the integer lifts of the1552 sample points. The rational3103-square augmented determinant reduces to the reported nonzero residue, hence is nonzero overQ. There are only3102 coefficient columns, so no rational constant coefficient vector solves these necessary evaluations. Unknown coefficient denominators need not be prime to the recorded prime. This does not infer characteristic-zero rank from a deficient modular rank.',
 'structural_dependency':'Prior low-degree tangent/support theorem and new invertibility of R-4I restrict only P4. All2808 coefficients in lower P3,P2,P1,P0 are retained. This necessary3102 family contains every possible solution in the declared original3510-generator sum. No lower A^2 or A^3 projection is used.',
 'scope':'If determinant is nonzero, excludes full six-component B+B/A+B/A^2+B/A^3+B/A^4 and its B/A^4 subfamily for -10<=r exponent<=2 and v,t exponents0..2. Does not exclude larger supports, A^-5 or other denominators, arbitrary rational compact currents, fibre-dependent sextic functions; no homogeneous certificate, Lean proof, or full-target solution.',
 'python':sys.version,'numpy':np.__version__,'sympy':S.__version__,'python_flint':flint.__version__,'determinant_backend':'flint.nmod_mat.det'}
save(HERE/'A4-minor.json',report)
watch.cancel()

#!/usr/bin/env python3
"""Independent polynomial-evaluation reconstruction and Gaussian determinant.

Reconstructs only the decisive first703-row minor, from captured sample points
and pinned JSON. Symbolic coefficient Jacobians and monomial derivatives replace
the Pro evaluator/differentiation code. Gaussian normalization replaces Bareiss.
"""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,threading,time
HERE=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--child',action='store_true')
p.add_argument('--connection',type=Path,default=Path(r'C:/Users/anaxe/Documents/Codex/hl-source-20261023/results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'))
args=p.parse_args()
if not args.child:
    start=time.monotonic()
    try:out=subprocess.run([sys.executable,str(Path(__file__).resolve()),'--child','--connection',str(args.connection)],capture_output=True,text=True,encoding='utf-8',timeout=60)
    except subprocess.TimeoutExpired as ex:
        txt=lambda x:x.decode('utf-8',errors='replace') if isinstance(x,bytes) else (x or '')
        (HERE/'independent-audit-timeout.log').write_text(txt(ex.stdout)+txt(ex.stderr),encoding='utf-8');raise
    log=out.stdout+out.stderr;(HERE/'independent-audit.log').write_text(log,encoding='utf-8')
    receipt={'kind':'Independently authored decisive-minor reconstruction and normalized Gaussian elimination','exit_code':out.returncode,'wall_seconds':time.monotonic()-start,'child_limit_seconds':60,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(args.connection.read_bytes()).hexdigest(),'log_sha256':hashlib.sha256(log.encode('utf-8')).hexdigest()}
    if (HERE/'independent-audit.json').exists():receipt['report_sha256']=hashlib.sha256((HERE/'independent-audit.json').read_bytes()).hexdigest()
    (HERE/'independent-audit-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print(out.stdout,end='');print(out.stderr,end='',file=sys.stderr);print(json.dumps(receipt));sys.exit(out.returncode)
import numpy as np
import sympy as S
watch=threading.Timer(58,lambda:os._exit(124));watch.daemon=True;watch.start()
prime=32003;assert S.isprime(prime)
source=args.connection.read_bytes();sha=hashlib.sha256(source).hexdigest()
assert sha=='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
meta=json.loads((HERE/'capture.json').read_text(encoding='utf-8'))
saved=np.load(HERE/'augmented-minor.npy',allow_pickle=False)
assert saved.shape==(703,703) and saved.dtype==np.int64
assert np.all((saved>=0)&(saved<prime))
raw=json.loads(source);a,b,c,d,r,v,t=S.symbols('a b c d r v t')
universals=(a,b,c,d);coords=(r,v,t);loc={str(x):x for x in universals}

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
        def calc(ts):
            total=0
            for ex,co in ts:
                z=co
                for value,power in zip(values,ex):z=z*pow(int(value),int(power),prime)%prime
                total=(total+z)%prime
            return total
        nn,dd=calc(ns),calc(ds)
        if not dd:raise ZeroDivisionError('Invalid evaluation denominator')
        return nn*pow(dd,-1,prime)%prime
    return evaluate

M={str(x):[[compiler(S.sympify(z,locals=loc),universals) for z in row] for row in raw['connection'][str(x)]] for x in universals}
delta=compiler(S.sympify(raw['Delta'],locals=loc),universals)
A=r**3+r**-3+(v*r-1)**6/r**15
coefficient_expr=[A,t*v,t*(1-t*t)/7,1+t**6]
base=[compiler(x,coords) for x in coefficient_expr]
# Derive the full connection pullback by Jacobian, rather than copying formulas.
jac=[[compiler(S.diff(x,z),coords) for x in coefficient_expr] for z in coords]
exponents=[(m,n,k) for m in range(-10,3) for n in range(3) for k in range(3)]
mons=[r**m*v**n*t**k for m,n,k in exponents]
mon_eval=[compiler(x,coords) for x in mons]
derivative_eval=[[compiler(S.diff(x,z),coords) for x in mons] for z in coords]
basis=[[i,j,m,n,k] for i in range(3) for j in range(2) for m,n,k in exponents]
assert len(basis)==702 and basis==meta['basis']
assert len(meta['points'])==352
rebuilt=np.zeros((703,703),dtype=np.int64)
mutation=None
for ip,pt in enumerate(meta['points']):
    assert len(pt)==3 and all(0<int(x)<prime for x in pt)
    values=[fn(pt) for fn in base]
    assert values[0]!=0 and delta(values)!=0
    matrices=[[[fn(values) for fn in row] for row in M[str(x)]] for x in universals]
    jvalues=[[fn(pt) for fn in row] for row in jac]
    connection=[[[sum(jvalues[direction][s]*matrices[s][i][j] for s in range(4))%prime for j in range(2)] for i in range(2)] for direction in range(3)]
    mon=np.array([fn(pt) for fn in mon_eval],dtype=np.int64)
    deriv=[np.array([fn(pt) for fn in row],dtype=np.int64) for row in derivative_eval]
    for i in range(2):
        row=2*ip+i
        if row>=703:continue
        for direction in range(3):
            for j in range(2):
                start=(2*direction+j)*117
                rebuilt[row,start:start+117]=(connection[direction][i][j]*mon+(deriv[direction] if i==j else 0))%prime
        rebuilt[row,-1]=pow(int(pt[0]),-4,prime)*pow(12,-1,prime)*matrices[1][i][0]%prime
    # A direct negative control for the essential moving-a contribution to Nv.
    if mutation is None:
        mid=exponents.index((0,0,0))
        for i in range(2):
            for j in range(2):
                wrong=int(pt[2])*matrices[1][i][j]%prime
                correct=connection[1][i][j]
                if correct!=wrong:
                    mutation={'omitted_term':'A_v M_a','point_index':ip,'row':2*ip+i,'column':(2+j)*117+mid,'correct_entry':correct,'mutant_entry':wrong}
                    break
            if mutation is not None:break
assert mutation is not None
if not np.array_equal(rebuilt,saved):
    where=np.argwhere(rebuilt!=saved)[0]
    raise AssertionError(('matrix mismatch',where.tolist(),int(rebuilt[tuple(where)]),int(saved[tuple(where)])))
print('PASS: all 494209 decisive-minor entries independently reconstructed',flush=True)
print('REJECTED CONTROL: omitted A_v M_a changes entry',mutation,flush=True)

# Standard Gaussian elimination with normalized pivots and determinant product,
# structurally different from the supplied fraction-free Bareiss recurrence.
H=rebuilt.copy();det=1;swaps=0
assert 2*(prime-1)**2<2**63
for k in range(703):
    nz=np.flatnonzero(H[k:,k])
    if not len(nz):raise AssertionError(('singular independent minor',k))
    pivotrow=k+int(nz[0])
    if pivotrow!=k:H[[k,pivotrow]]=H[[pivotrow,k]];det=-det;swaps+=1
    pivot=int(H[k,k]);det=det*pivot%prime
    H[k,k:]=H[k,k:]*pow(pivot,-1,prime)%prime
    if k<702:H[k+1:,k:]=(H[k+1:,k:]-H[k+1:,k,None]*H[k,k:])%prime
det%=prime
assert det==13884
print('PASS: independent normalized Gaussian determinant',det,flush=True)
report={
 'status':'PASS: complete independent reconstruction of decisive minor and distinct Gaussian determinant algorithm',
 'source_sha256':sha,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'captured_pro_script_sha256':meta['pro_verifier_sha256'],'capture_sha256':hashlib.sha256((HERE/'capture.json').read_bytes()).hexdigest(),'captured_matrix_npy_sha256':hashlib.sha256((HERE/'augmented-minor.npy').read_bytes()).hexdigest(),
 'canonical_rebuilt_matrix_bytes_sha256':hashlib.sha256(rebuilt.astype('<i8',copy=False).tobytes()).hexdigest(),
 'prime':prime,'prime_verified':True,'shape':[703,703],'entries_checked':703*703,'coefficient_columns':702,'determinant':det,'row_swaps':swaps,
 'basis':'Six physical components, each span_Q{r^m v^n t^k: -10<=m<=2,0<=n,k<=2};117 independent monomials per component.',
 'operator_binding':'Connection obtained by symbolic Jacobian of (A(r,v),tv,t(1-t^2)/7,1+t^6), contracted with literal universal M entries. Every monomial derivative obtained by symbolic differentiation in r,v,t. Source r^-4 M_b e0/12 uses packet positive orientation.',
 'methods':'Independent rational-polynomial numerator/denominator evaluator; full entry equality against passively captured Pro minor; normalized-pivot Gaussian elimination with pivot-product determinant. Does not use Pro AST evaluator or Bareiss recurrence.',
 'negative_control':mutation,
 'characteristic_zero_reason':'Each selected finite-field point has integer lifts. All rational input denominators are prime units by explicit evaluation checks, so the rational augmented determinant reduces to13884 and is nonzero in Q. Its703 columns are independent while the coefficient matrix has only702 columns. Thus no rational coefficient vector can solve these necessary evaluations, regardless of denominators in hypothetical solution coefficients. The same rank obstruction persists after any characteristic-zero extension of the constant field.',
 'scope':'Excludes exactly the declared bounded six-component physical Laurent family. It does not exclude additional current denominators, larger exponents, general rational compact currents, fibre-dependent sextic functions, or the target problem. Only the decisive first703 rows are reconstructed; the larger762-row search matrix and the separate first-jet obstruction are not replayed.',
 'python':sys.version,'numpy':np.__version__,'sympy':S.__version__
}
(HERE/'independent-audit.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
watch.cancel()

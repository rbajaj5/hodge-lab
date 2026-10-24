"""New A-denominator SUM family after the externally checked necessary tangency.

F = Laurent + (T_r*h,T_v*h,P_t)/A. Laurent and P_t use the original
box m=-10..2,n,k=0..2; h uses m=-10..-6,n=0..1,k=0..2.
Direct quotient derivatives are used and the whole equation multiplied by A.
Full physical connection and target are evaluated
exactly modulo a prime. Full augmented column rank would exclude this
declared QQ family; deficient modular rank is ONLY a modular search result.
"""
from pathlib import Path
import datetime,hashlib,json,random,sys,time
import numpy as np
import sympy as S
start=time.monotonic();out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
root=Path(__file__).resolve().parents[3]
src=root/'results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'
pin='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
if hashlib.sha256(src.read_bytes()).hexdigest()!=pin:raise RuntimeError('Source pin changed')
raw=json.loads(src.read_text(encoding='utf-8'));a,b,c,d=S.symbols('a b c d');xs=[a,b,c,d];loc={str(x):x for x in xs}
prime=32003;seed=2026102416;rng=random.Random(seed)
def coeff(q):q=S.Rational(q);return int(q.p)%prime*pow(int(q.q),-1,prime)%prime
def poly(expr):return [(m,coeff(q)) for m,q in S.Poly(expr,*xs,domain=S.QQ).terms()]
def rational(expr):
    nu,de=S.fraction(S.cancel(expr));return poly(nu),poly(de)
M={name:[[rational(S.sympify(z,locals=loc)) for z in row] for row in mat] for name,mat in raw['connection'].items()}
def peval(p,x):return sum(q*pow(x[0],m[0],prime)*pow(x[1],m[1],prime)*pow(x[2],m[2],prime)*pow(x[3],m[3],prime) for m,q in p)%prime
def reval(f,x):return peval(f[0],x)*pow(peval(f[1],x),-1,prime)%prime
def evaluate(point):
    r,v,t=point;ri=pow(r,-1,prime);vr=v*r-1
    av=(pow(r,3,prime)+pow(ri,3,prime)+pow(vr,6,prime)*pow(ri,15,prime))%prime
    ar=(3*r*r-3*pow(ri,4,prime)+6*v*pow(vr,5,prime)*pow(ri,15,prime)-15*pow(vr,6,prime)*pow(ri,16,prime))%prime
    va=6*pow(vr,5,prime)*pow(ri,14,prime)%prime
    cv=t*(1-t*t)*pow(7,-1,prime)%prime;dv=(1+pow(t,6,prime))%prime
    inputs=[av,t*v%prime,cv,dv]
    mm={name:np.array([[reval(z,inputs) for z in row] for row in mat],dtype=np.int64) for name,mat in M.items()}
    nr=ar*mm['a']%prime
    nv=(va*mm['a']+t*mm['b'])%prime
    nt=(v*mm['b']+(1-3*t*t)*pow(7,-1,prime)*mm['c']+6*pow(t,5,prime)*mm['d'])%prime
    target=pow(ri,4,prime)*pow(12,-1,prime)*mm['b'][:,0]%prime
    # Make the open explicit in saved samples; Ar is not inverted in this physical search.
    delta=(27*av*av*dv*dv-18*av*inputs[1]*cv*dv+4*av*cv**3+4*inputs[1]**3*dv-inputs[1]**2*cv*cv)%prime
    if not av or not delta:raise ZeroDivisionError('Excluded open')
    return [nr,nv,nt],target,{'a':int(av),'Ar':int(ar),'Av':int(va),'Delta':int(delta)}
monomials=[(m,n,k) for m in range(-10,3) for n in range(3) for k in range(3)]
basis=[('h',-1,j,m,n,k) for j in range(2) for m in range(-10,-5) for n in range(2) for k in range(3)]
basis += [('Pt',2,j,*exponent) for j in range(2) for exponent in monomials]
basis += [('Laurent',direction,j,*exponent) for direction in range(3) for j in range(2) for exponent in monomials]
columns=len(basis);samples=[];rows=[];excluded=[]
while len(samples)<columns//2+30:
    point=[rng.randrange(1,prime) for _ in range(3)]
    try:N,y,domain=evaluate(point)
    except (ValueError,ZeroDivisionError):excluded.append(point);continue
    invs=[pow(x,-1,prime) for x in point]
    powers=[{e:pow(x,e,prime) for e in range(-10,4)} for x in point]
    mon=[powers[0][m]*powers[1][n]*powers[2][k]%prime for m,n,k in monomials]
    rr=[[],[]]
    r,v,t=point
    Tr=(pow(r,8,prime)+r*r)%prime
    Tv=(r*(2*pow(r,6,prime)+1)*v-(3*pow(r,6,prime)+2))%prime
    dTr=(8*pow(r,7,prime)+2*r)%prime
    dTv=r*(2*pow(r,6,prime)+1)%prime
    ainv=pow(domain['a'],-1,prime)
    for sector,direction,j,m,n,k in basis:
        value=powers[0][m]*powers[1][n]*powers[2][k]%prime
        if sector=='h':
            derivative=(dTr+dTv+Tr*m*invs[0]+Tv*n*invs[1]-(Tr*domain['Ar']+Tv*domain['Av'])*ainv)%prime
            for i in range(2):
                rr[i].append(int((Tr*int(N[0][i,j])+Tv*int(N[1][i,j])+(derivative if i==j else 0))*value%prime))
        else:
            derivative=([m,n,k][direction]*invs[direction])%prime
            multiplier=domain['a'] if sector=='Laurent' else 1
            for i in range(2):rr[i].append(int((int(N[direction][i,j])+(derivative if i==j else 0))*value*multiplier%prime))
    samples.append({'point':point,'domain':domain})
    for i in range(2):rows.append(rr[i]+[int(y[i])*domain['a']%prime])
matrix=np.array(rows,dtype=np.int64)
np.savetxt(out/'augmented-matrix.csv',matrix,fmt='%d',delimiter=',')
(out/'inputs.json').write_text(json.dumps({'prime':prime,'seed':seed,'basis':basis,'samples':samples,'excluded_points':excluded,'matrix_shape':list(matrix.shape),'convention':'rows are sample0-row0,sample0-row1,...; final column is source'},indent=2)+'\n',encoding='utf-8')
print('assembled',matrix.shape,'seconds',time.monotonic()-start,flush=True)
# Deterministic finite-field elimination, retaining source row origins for a minor.
B=matrix.copy();rank=0;pivots=[];origins=list(range(len(B)));pivot_rows=[];pivot_values=[]
for j in range(B.shape[1]):
    indices=np.flatnonzero(B[rank:,j])
    if not len(indices):continue
    k=rank+int(indices[0]);B[[rank,k]]=B[[k,rank]];origins[rank],origins[k]=origins[k],origins[rank]
    pivot=int(B[rank,j]);pivot_values.append(pivot);pivot_rows.append(origins[rank]);pivots.append(j)
    B[rank,j:]=B[rank,j:]*pow(pivot,-1,prime)%prime
    if rank+1<len(B):
        B[rank+1:,j:]=(B[rank+1:,j:]-B[rank+1:,j,None]*B[rank,j:])%prime
    rank+=1
    if rank==len(B):break
crank=sum(x<columns for x in pivots);aug=rank
if aug==columns+1:status='EXACT_QQ_FINITE_FAMILY_EXCLUDED_BY_MODULAR_MINOR'
elif aug>crank:status='MODULAR_INCONSISTENCY_ONLY_WITH_RANK_DEFECT'
else:status='MODULAR_CANDIDATES_REQUIRE_LIFT_AND_EXACT_CHECK'
receipt={'status':status,'executor':'Pro root constructive lead','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-start,'python':sys.version,'numpy':np.__version__,'sympy':S.__version__,'source_sha256':pin,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'prime':prime,'seed':seed,'matrix_shape':list(matrix.shape),'rank_denominator_tangent_block':sum(x<294 for x in pivots),'rank_coefficient':crank,'rank_augmented':aug,'pivots':pivots,'pivot_source_rows':pivot_rows,'pivot_values':pivot_values,'family':'Necessary tangent subfamily of full six-component B plus B/A; original1404 parameters, necessary996','parameter_sectors':{'h':60,'Pt':234,'Laurent':702},'structural_dependency':'Externally checked necessary P_r=T_r h,P_v=T_v h and support bound; coordinator source proof is imported evidence, not a root rerun','quotient_rule':'direct -Ar/A^2 and -Av/A^2 retained; At=0; equation multiplied by A','full_operator':'A*sum_i(partial_i+Nphysical_i)F_i, Nphysical=(Ar Ma,Av Ma+t Mb,Nt)','target':'A*r^-4 Mb e0/12','matrix_sha256':hashlib.sha256((out/'augmented-matrix.csv').read_bytes()).hexdigest(),'inputs_sha256':hashlib.sha256((out/'inputs.json').read_bytes()).hexdigest(),'limits':'No completeness beyond declared family and imported necessary-condition theorem; deficient modular rank cannot prove QQ inconsistency without an exact rank upper bound. No primitive or solve claimed.'}
(out/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:val for k,val in receipt.items() if not k.startswith('pivot')},indent=2),flush=True)

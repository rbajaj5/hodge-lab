"""NEW A-cubed SUM family after imported necessary TOP tangency only.

F = P0 + P1/A + P2/A**2 + (T_r*h3,T_v*h3,k3)/A**3. P0, P1, P2 and k3
use the original box m=-10..2,n,k=0..2; h3 uses m=-10..-6,n=0..1,k=0..2.
P2, P1, P0 stay unrestricted. Direct quotient derivatives, including factor3,
are used; the equation is multiplied by A**3.
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
prime=32003;seed=2026102458;rng=random.Random(seed)
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
basis=[('h3',-1,j,m,n,k) for j in range(2) for m in range(-10,-5) for n in range(2) for k in range(3)]
basis += [('k3',2,j,*exponent) for j in range(2) for exponent in monomials]
basis += [('P2',direction,j,*exponent) for direction in range(3) for j in range(2) for exponent in monomials]
basis += [('P1',direction,j,*exponent) for direction in range(3) for j in range(2) for exponent in monomials]
basis += [('P0',direction,j,*exponent) for direction in range(3) for j in range(2) for exponent in monomials]
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
        if sector=='h3':
            derivative=(dTr+dTv+Tr*m*invs[0]+Tv*n*invs[1]-3*(Tr*domain['Ar']+Tv*domain['Av'])*ainv)%prime
            for i in range(2):
                rr[i].append(int((Tr*int(N[0][i,j])+Tv*int(N[1][i,j])+(derivative if i==j else 0))*value%prime))
        else:
            derivative=([m,n,k][direction]*invs[direction])%prime
            if sector in ['P2','P1']:
                power=2 if sector=='P2' else 1
                derivative=(derivative-power*[domain['Ar'],domain['Av'],0][direction]*ainv)%prime
                multiplier=pow(domain['a'],3-power,prime)
            elif sector=='P0':multiplier=pow(domain['a'],3,prime)
            elif sector=='k3':multiplier=1
            else:raise RuntimeError('Unknown sector')
            for i in range(2):rr[i].append(int((int(N[direction][i,j])+(derivative if i==j else 0))*value*multiplier%prime))
    samples.append({'point':point,'domain':domain})
    for i in range(2):rows.append(rr[i]+[int(y[i])*domain['a']**3%prime])
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
receipt={'status':status,'executor':'Pro root constructive lead','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-start,'python':sys.version,'numpy':np.__version__,'sympy':S.__version__,'source_sha256':pin,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'prime':prime,'seed':seed,'matrix_shape':list(matrix.shape),'rank_top_tangent_block':sum(x<294 for x in pivots),'rank_coefficient':crank,'rank_augmented':aug,'pivots':pivots,'pivot_source_rows':pivot_rows,'pivot_values':pivot_values,'family':'Necessary TOP-tangent subfamily of full six-component B plus B/A plus B/A² plus B/A³; original2808 parameters, necessary2400; P2,P1,P0 unrestricted','parameter_sectors':{'h3':60,'k3':234,'P2':702,'P1':702,'P0':702},'structural_dependency':'Imported coordinator highest-pole det(Ra-3I)=10 reasoning plus reused bounded tangent parametrization; only P3 constrained. Not rerun here. No lower tangency or A2 projection imposed.','quotient_rule':'direct top -3Ar/A^4 and -3Av/A^4 plus lower -jAi/A^(j+1) retained; At=0; equation multiplied by A³','full_operator':'A³*sum_i(partial_i+Nphysical_i)F_i, Nphysical=(Ar Ma,Av Ma+t Mb,Nt)','target':'A³*r^-4 Mb e0/12','matrix_sha256':hashlib.sha256((out/'augmented-matrix.csv').read_bytes()).hexdigest(),'inputs_sha256':hashlib.sha256((out/'inputs.json').read_bytes()).hexdigest(),'limits':'No completeness beyond declared family and imported necessary-condition theorem; deficient modular rank cannot prove QQ inconsistency without an exact rank upper bound. No primitive or solve claimed.'}
(out/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:val for k,val in receipt.items() if not k.startswith('pivot')},indent=2),flush=True)

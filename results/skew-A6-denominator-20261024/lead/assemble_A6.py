"""NEW A-sixth SUM family after imported necessary TOP tangency only.

F = P0 + P1/A + P2/A**2 + P3/A**3 + P4/A**4 + P5/A**5 + (T_r*h6,T_v*h6,k6)/A**6. P0,P1,P2,P3,P4,P5,k6
use the original box m=-10..2,n,k=0..2; h6 uses m=-10..-6,n=0..1,k=0..2.
P5,P4,P3,P2,P1,P0 stay unrestricted. Direct quotient derivatives, including factor6,
are used; the equation is multiplied by A**6.
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
prime=65521;seed=2026102486;rng=random.Random(seed)
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
    # Reduce the rational c' coefficient before NumPy int64 multiplication.
    cp=(1-3*t*t)*pow(7,-1,prime)%prime
    nt=(v*mm['b']+cp*mm['c']+6*pow(t,5,prime)*mm['d'])%prime
    target=pow(ri,4,prime)*pow(12,-1,prime)*mm['b'][:,0]%prime
    # Make the open explicit in saved samples; Ar is not inverted in this physical search.
    delta=(27*av*av*dv*dv-18*av*inputs[1]*cv*dv+4*av*cv**3+4*inputs[1]**3*dv-inputs[1]**2*cv*cv)%prime
    if not av or not delta:raise ZeroDivisionError('Excluded open')
    return [nr,nv,nt],target,{'a':int(av),'Ar':int(ar),'Av':int(va),'Delta':int(delta)}
monomials=[(m,n,k) for m in range(-10,3) for n in range(3) for k in range(3)]
basis=[('h6',-1,j,m,n,k) for j in range(2) for m in range(-10,-5) for n in range(2) for k in range(3)]
basis += [('k6',2,j,*exponent) for j in range(2) for exponent in monomials]
basis += [('P5',direction,j,*exponent) for direction in range(3) for j in range(2) for exponent in monomials]
basis += [('P4',direction,j,*exponent) for direction in range(3) for j in range(2) for exponent in monomials]
basis += [('P3',direction,j,*exponent) for direction in range(3) for j in range(2) for exponent in monomials]
basis += [('P2',direction,j,*exponent) for direction in range(3) for j in range(2) for exponent in monomials]
basis += [('P1',direction,j,*exponent) for direction in range(3) for j in range(2) for exponent in monomials]
basis += [('P0',direction,j,*exponent) for direction in range(3) for j in range(2) for exponent in monomials]
columns=len(basis);samples=[];rows=[];excluded=[]
if columns!=4506:raise RuntimeError('Incorrect parameter count')
if any(prime%d==0 for d in range(2,int(prime**.5)+1)):raise RuntimeError('Nonprime modulus')
while len(samples)<2280:
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
        if sector=='h6':
            derivative=(dTr+dTv+Tr*m*invs[0]+Tv*n*invs[1]-6*(Tr*domain['Ar']+Tv*domain['Av'])*ainv)%prime
            for i in range(2):
                rr[i].append(int((Tr*int(N[0][i,j])+Tv*int(N[1][i,j])+(derivative if i==j else 0))*value%prime))
        else:
            derivative=([m,n,k][direction]*invs[direction])%prime
            if sector in ['P5','P4','P3','P2','P1']:
                power=int(sector[1:])
                derivative=(derivative-power*[domain['Ar'],domain['Av'],0][direction]*ainv)%prime
                multiplier=pow(domain['a'],6-power,prime)
            elif sector=='P0':multiplier=pow(domain['a'],6,prime)
            elif sector=='k6':multiplier=1
            else:raise RuntimeError('Unknown sector')
            for i in range(2):rr[i].append(int((int(N[direction][i,j])+(derivative if i==j else 0))*value*multiplier%prime))
    samples.append({'point':point,'domain':domain})
    for i in range(2):rows.append(rr[i]+[int(y[i])*domain['a']**6%prime])
matrix=np.array(rows,dtype=np.int64)
matrix.astype('<u2').tofile(out/'augmented-matrix.u16.bin')
(out/'inputs.json').write_text(json.dumps({'prime':prime,'seed':seed,'basis':basis,'samples':samples,'excluded_points':excluded,'matrix_shape':list(matrix.shape),'binary_format':'row-major little-endian uint16; no header','convention':'rows are sample0-row0,sample0-row1,...; final column is source'},indent=2)+'\n',encoding='utf-8')
print('assembled',matrix.shape,'seconds',time.monotonic()-start,flush=True)

receipt={'status':'ASSEMBLED_DIRECT_QUOTIENT_A6_MATRIX_NO_RANK_CLAIM','executor':'Pro root constructive lead','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-start,'python':sys.version,'numpy':np.__version__,'sympy':S.__version__,'source_sha256':pin,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'prime':prime,'seed':seed,'matrix_shape':list(matrix.shape),'matrix_entries':int(matrix.size),'matrix_dtype':'<u2','matrix_order':'C','matrix_sha256':hashlib.sha256((out/'augmented-matrix.u16.bin').read_bytes()).hexdigest(),'inputs_sha256':hashlib.sha256((out/'inputs.json').read_bytes()).hexdigest(),'parameter_sectors':{'h6':60,'k6':234,'P5':702,'P4':702,'P3':702,'P2':702,'P1':702,'P0':702},'structural_dependency':'Imported highest-pole det(Ra-6I)=38 plus reused bounded tangent/support theorem; only P6 constrained. All lower sectors free.','quotient_rule':'Direct top -6Ar/A^7 and -6Av/A^7; lower -jAi/A^(j+1), At=0; equation multiplied by A^6','target':'A^6*r^-4*Mb e0/12','limits':'Assembly only; exclusion requires nonzero augmented rational minor. No rational primitive claimed.'}
(out/'validation.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt,indent=2),flush=True)

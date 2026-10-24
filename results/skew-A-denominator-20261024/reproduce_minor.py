"""Standalone plaintext fallback for the NEW reduced joint A-denominator minor.
Requires NumPy and the pinned parent connection JSON; no saved matrix required.
Run: timeout 60s python -O reproduce_minor.py CONNECTION_JSON
The original-family conclusion additionally uses the credited structural theorem.
"""
import ast,hashlib,json,random,sys
from pathlib import Path
import numpy as np
p=32003;path=Path(sys.argv[1])
pin='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
if hashlib.sha256(path.read_bytes()).hexdigest()!=pin:raise RuntimeError('Source pin mismatch')
data=json.loads(path.read_text(encoding='utf-8'))
def integer(n):
    if isinstance(n,ast.Constant) and type(n.value) is int:return n.value
    if isinstance(n,ast.UnaryOp) and isinstance(n.op,ast.USub):return -integer(n.operand)
    raise RuntimeError('Nonliteral exponent')
def ev(n,e):
    if isinstance(n,ast.Constant) and type(n.value) is int:return n.value%p
    if isinstance(n,ast.Name):return e[n.id]%p
    if isinstance(n,ast.UnaryOp) and isinstance(n.op,ast.USub):return -ev(n.operand,e)%p
    if not isinstance(n,ast.BinOp):raise RuntimeError('Unsupported syntax')
    x=ev(n.left,e)
    if isinstance(n.op,ast.Pow):return pow(x,integer(n.right),p)
    y=ev(n.right,e)
    if isinstance(n.op,ast.Add):return (x+y)%p
    if isinstance(n.op,ast.Sub):return (x-y)%p
    if isinstance(n.op,ast.Mult):return x*y%p
    if isinstance(n.op,ast.Div):return x*pow(y,-1,p)%p
    raise RuntimeError('Unsupported operator')
tree={q:[[ast.parse(z,mode='eval').body for z in row] for row in mat] for q,mat in data['connection'].items()}
dtree=ast.parse(data['Delta'],mode='eval').body
basis=[('h',-1,j,m,n,k) for j in range(2) for m in range(-10,-5) for n in range(2) for k in range(3)]
basis += [('Pt',2,j,m,n,k) for j in range(2) for m in range(-10,3) for n in range(3) for k in range(3)]
basis += [('L',q,j,m,n,k) for q in range(3) for j in range(2) for m in range(-10,3) for n in range(3) for k in range(3)]
rng=random.Random(2026102416);rows=[]
while len(rows)<998:
    r,v,t=[rng.randrange(1,p) for _ in range(3)];x=v*r-1
    A=(r**3+pow(r,-3,p)+pow(x,6,p)*pow(r,-15,p))%p
    Ar=(3*r*r-3*pow(r,-4,p)+6*v*pow(x,5,p)*pow(r,-15,p)-15*pow(x,6,p)*pow(r,-16,p))%p
    Av=6*pow(x,5,p)*pow(r,-14,p)%p
    e=dict(a=A,b=t*v%p,c=t*(1-t*t)*pow(7,-1,p)%p,d=(1+pow(t,6,p))%p)
    if not A or not ev(dtree,e):continue
    M={q:[[ev(z,e) for z in row] for row in mat] for q,mat in tree.items()}
    N=[[[Ar*M['a'][i][j]%p for j in range(2)] for i in range(2)],
       [[(Av*M['a'][i][j]+t*M['b'][i][j])%p for j in range(2)] for i in range(2)],
       [[(v*M['b'][i][j]+((1-3*t*t)*pow(7,-1,p)%p)*M['c'][i][j]+6*pow(t,5,p)*M['d'][i][j])%p for j in range(2)] for i in range(2)]]
    Tr=r*r*(pow(r,6,p)+1)%p
    Tv=(r*(2*pow(r,6,p)+1)*v-(3*pow(r,6,p)+2))%p
    lam=3*r*(pow(r,6,p)-1)%p;z0=(7*pow(r,7,p)+6*r)%p
    if (Tr*Ar+Tv*Av-lam*A)%p:raise RuntimeError('Tangency mismatch')
    H=[[ (lam*A*M['a'][i][j]+t*Tv*M['b'][i][j]+(z0 if i==j else 0))%p for j in range(2)] for i in range(2)]
    rr=[[],[]]
    for sector,q,j,m,n,k in basis:
        mon=pow(r,m,p)*pow(v,n,p)*pow(t,k,p)%p
        if sector=='h':
            der=(Tr*m*pow(r,-1,p)+Tv*n*pow(v,-1,p))%p
            for i in range(2):rr[i].append(mon*(H[i][j]+(der if i==j else 0))%p)
        else:
            der=[m,n,k][q]*pow([r,v,t][q],-1,p)%p
            scale=A if sector=='L' else 1
            for i in range(2):rr[i].append(scale*mon*(N[q][i][j]+(der if i==j else 0))%p)
    for i in range(2):rows.append(rr[i]+[A*pow(r,-4,p)*pow(12,-1,p)*M['b'][i][0]%p])
Q=np.array(rows[:997],dtype=np.int64);previous=1;sign=1
if 2*(p-1)**3>=2**63:raise RuntimeError('Overflow bound failed')
for k in range(996):
    nz=np.flatnonzero(Q[k:,k])
    if not len(nz):raise RuntimeError('Singular minor')
    j=k+int(nz[0])
    if j!=k:Q[[k,j]]=Q[[j,k]];sign=-sign
    pivot=int(Q[k,k])
    Q[k+1:,k+1:]=((pivot*Q[k+1:,k+1:]-Q[k+1:,k,None]*Q[k,k+1:])*pow(previous,-1,p))%p
    Q[k+1:,k]=0;previous=pivot
det=sign*int(Q[-1,-1])%p
if det!=26947:raise RuntimeError('Wrong determinant')
print(json.dumps(dict(prime=p,columns=len(basis),minor=997,determinant=det,
    scope='Reduced joint family excluded; full1404 family uses necessary tangency theorem')))

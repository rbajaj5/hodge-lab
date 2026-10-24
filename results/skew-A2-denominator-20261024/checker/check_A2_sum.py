"""Independent A^-2 sum-family matrix and certificate checker.

The input family is P0+P1/A+(Tr*h2,Tv*h2,k2)/A^2.  Only the highest
pole is tangent; P1 is unrestricted.  The structural top tangency and
support theorem is imported coordinator evidence, not rerun here.

The author uses direct quotient derivatives.  This checker independently
evaluates the literal JSON with a restricted AST and uses the reduced top
operator.  A modular Bareiss determinant is distinct from author's Gaussian
rank search.  No rank-defective modular gap is promoted to a QQ exclusion.
"""
from pathlib import Path
import ast,datetime,hashlib,json,sys,time
import numpy as np

start=time.monotonic()
out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
root=Path(__file__).resolve().parents[3]
author=Path(sys.argv[2]).resolve()
packet=root/'results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'
pin='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
if hashlib.sha256(packet.read_bytes()).hexdigest()!=pin:raise RuntimeError('Pinned connection changed')
data=json.loads(packet.read_text(encoding='utf-8'))
inputs=json.loads((author/'inputs.json').read_text(encoding='utf-8'))
receipt=json.loads((author/'validation.json').read_text(encoding='utf-8'))
p=inputs['prime']
if p!=32003 or any(p%k==0 for k in range(2,int(p**.5)+1)):raise RuntimeError('Prime gate failed')

def integer(node):
    if isinstance(node,ast.Constant) and type(node.value) is int:return node.value
    if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.USub):return -integer(node.operand)
    raise RuntimeError('Nonliteral exponent')

def ev(node,env):
    if isinstance(node,ast.Constant) and type(node.value) is int:return node.value%p
    if isinstance(node,ast.Name):return env[node.id]%p
    if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.USub):return -ev(node.operand,env)%p
    if not isinstance(node,ast.BinOp):raise RuntimeError('Unsupported source syntax')
    x=ev(node.left,env)
    if isinstance(node.op,ast.Pow):return pow(x,integer(node.right),p)
    y=ev(node.right,env)
    if isinstance(node.op,ast.Add):return (x+y)%p
    if isinstance(node.op,ast.Sub):return (x-y)%p
    if isinstance(node.op,ast.Mult):return x*y%p
    if isinstance(node.op,ast.Div):return x*pow(y,-1,p)%p
    raise RuntimeError('Unsupported source operator')

parsed={name:[[ast.parse(x,mode='eval').body for x in row] for row in mat] for name,mat in data['connection'].items()}
deltatree=ast.parse(data['Delta'],mode='eval').body
basis=[['h2',-1,j,m,n,k] for j in range(2) for m in range(-10,-5) for n in range(2) for k in range(3)]
basis += [['k2',2,j,m,n,k] for j in range(2) for m in range(-10,3) for n in range(3) for k in range(3)]
for sector in ['P1','P0']:
    basis += [[sector,direction,j,m,n,k] for direction in range(3) for j in range(2) for m in range(-10,3) for n in range(3) for k in range(3)]
if len(basis)!=1698 or inputs['basis']!=basis:raise RuntimeError('Unexpected declared A2 sum basis')

rebuilt=[];controls=None;domains=0
for sample in inputs['samples']:
    r,v,t=sample['point']
    if not all(0<x<p for x in [r,v,t]):raise RuntimeError('Invalid sample')
    q=v*r-1
    A=(pow(r,3,p)+pow(r,-3,p)+pow(q,6,p)*pow(r,-15,p))%p
    Ar=(3*r*r-3*pow(r,-4,p)+6*v*pow(q,5,p)*pow(r,-15,p)-15*pow(q,6,p)*pow(r,-16,p))%p
    Av=6*pow(q,5,p)*pow(r,-14,p)%p
    C=t*(1-t*t)*pow(7,-1,p)%p;D=(1+pow(t,6,p))%p
    env={'a':A,'b':t*v%p,'c':C,'d':D};delta=ev(deltatree,env)
    if not A or not delta:raise RuntimeError('Excluded denominator locus')
    if {'a':A,'Ar':Ar,'Av':Av,'Delta':delta}!=sample['domain']:raise RuntimeError('Physical source binding mismatch')
    domains+=1;Ai=[Ar,Av,0];invA=pow(A,-1,p)
    M={name:[[ev(x,env) for x in row] for row in mat] for name,mat in parsed.items()}
    N=[[[Ar*M['a'][i][j]%p for j in range(2)] for i in range(2)],
       [[(Av*M['a'][i][j]+t*M['b'][i][j])%p for j in range(2)] for i in range(2)],
       [[(v*M['b'][i][j]+((1-3*t*t)*pow(7,-1,p)%p)*M['c'][i][j]+6*pow(t,5,p)*M['d'][i][j])%p for j in range(2)] for i in range(2)]]
    Tr=r*r*(pow(r,6,p)+1)%p
    Tv=(r*(2*pow(r,6,p)+1)*v-(3*pow(r,6,p)+2))%p
    ell=3*r*(pow(r,6,p)-1)%p
    zeroth=(4*pow(r,7,p)+9*r)%p
    if (Tr*Ar+Tv*Av-ell*A)%p:raise RuntimeError('Tangency binding failed at sample')
    direct_zero=(10*pow(r,7,p)+3*r-2*(Tr*Ar+Tv*Av)*invA)%p
    if direct_zero!=zeroth:raise RuntimeError('A2 quotient zero-order mismatch')
    Hmat=[[(ell*A*M['a'][i][j]+t*Tv*M['b'][i][j]+(zeroth if i==j else 0))%p for j in range(2)] for i in range(2)]
    for i in range(2):
        for j in range(2):
            if (Tr*N[0][i][j]+Tv*N[1][i][j]+(direct_zero if i==j else 0)-Hmat[i][j])%p:raise RuntimeError('Reduced top connection mismatch')
    rr=[[],[]]
    for sector,direction,j,m,n,k in basis:
        exp=[m,n,k]
        mon=pow(r,m,p)*pow(v,n,p)*pow(t,k,p)%p
        if sector=='h2':
            derivative=(Tr*m*pow(r,m-1,p)*pow(v,n,p)*pow(t,k,p)+Tv*n*pow(r,m,p)*pow(v,n-1,p)*pow(t,k,p))%p
            for i in range(2):rr[i].append((Hmat[i][j]*mon+(derivative if i==j else 0))%p)
        else:
            lower=exp.copy();lower[direction]-=1
            derivative=exp[direction]*pow(r,lower[0],p)*pow(v,lower[1],p)*pow(t,lower[2],p)%p
            scale=A*A if sector=='P0' else A if sector=='P1' else 1
            for i in range(2):
                value=N[direction][i][j]*mon+(derivative if i==j else 0)
                if sector=='P1' and i==j:value-=Ai[direction]*invA*mon
                rr[i].append(scale*value%p)
    target=[A*A*pow(r,-4,p)*pow(12,-1,p)*M['b'][i][0]%p for i in range(2)]
    for i in range(2):rebuilt.append(rr[i]+[target[i]])
    if controls is None:
        unit=pow(r,-10,p)
        differences={
          'replace_top_factor_2_by_1':unit*ell%p,
          'omit_top_r_quotient_term':2*unit*Tr*Ar*invA%p,
          'omit_top_v_quotient_term':2*unit*Tv*Av*invA%p,
          'reverse_top_quotient_sign':4*unit*ell%p,
          'omit_P1_r_quotient_term':unit*Ar%p,
          'omit_P1_v_quotient_term':unit*Av%p,
          'omit_Av_connection_chain':unit*Tv*Av*M['a'][0][0]%p,
          'omit_source_1_over_12':11*target[0]%p,
          'reverse_source_sign':2*target[0]%p,
          'omit_k2_t_derivative':unit}
        if all(differences.values()):controls={'point':sample['point'],'nonzero_differences':differences}
if controls is None:raise RuntimeError('Mutation controls did not discriminate')
B=np.array(rebuilt,dtype=np.int64)
saved=np.loadtxt(author/'augmented-matrix.csv',delimiter=',',dtype=np.int64)
if B.shape[1]!=1699 or not np.array_equal(B,saved):raise RuntimeError('Augmented A2 sum matrix mismatch')
print('all A2 joint matrix entries independently reconstructed',B.shape,flush=True)
rank=receipt['rank_coefficient'];aug=receipt['rank_augmented'];det=None;selected=[]
if rank==1698 and aug==1699:
    selected=receipt['pivot_source_rows']
    if len(selected)!=1699 or len(set(selected))!=1699 or min(selected)<0 or max(selected)>=len(B):raise RuntimeError('Invalid minor rows')
    H=B[selected,:].copy();previous=1;sign=1
    if 2*(p-1)**3>=2**63:raise RuntimeError('Integer overflow guard failed')
    for k in range(1698):
        nz=np.flatnonzero(H[k:,k])
        if not len(nz):raise RuntimeError('Claimed minor singular')
        j=k+int(nz[0])
        if j!=k:H[[k,j]]=H[[j,k]];sign=-sign
        pivot=int(H[k,k])
        H[k+1:,k+1:]=((pivot*H[k+1:,k+1:]-H[k+1:,k,None]*H[k,k+1:])*pow(previous,-1,p))%p
        H[k+1:,k]=0;previous=pivot
    det=sign*int(H[-1,-1])%p
    if not det:raise RuntimeError('Zero augmented determinant')
    status='PASS_EXACT_QQ_A2_SUM_FINITE_FAMILY_EXCLUSION'
else:
    status='PASS_MATRIX_ONLY_EXACT_KERNEL_OR_RANK_CERTIFICATE_REQUIRED'
result={'status':status,'executor':'a2_denominator_checker AI worker','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':time.monotonic()-start,'python':sys.version,'numpy':np.__version__,'packet_sha256':pin,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'author_validation_sha256':hashlib.sha256((author/'validation.json').read_bytes()).hexdigest(),'inputs_sha256':hashlib.sha256((author/'inputs.json').read_bytes()).hexdigest(),'matrix_sha256':hashlib.sha256((author/'augmented-matrix.csv').read_bytes()).hexdigest(),'matrix_shape':list(B.shape),'entries_reconstructed':int(B.size),'domain_points_checked':domains,'author_modular_rank_coefficient':rank,'author_modular_rank_augmented':aug,'independent_augmented_minor_det_mod_prime':det,'prime':p,'mutations':controls,'scope':'Necessary1698-parameter current family: h2=60,k2=234,P1=702,P0=702. Full1699 augmented minor proves exclusion over QQ; exclusion of original2106-dimensional sum additionally uses imported top tangency/support theorem. No P1 tangency is imposed. Structural theorem not rerun here. No general rational-current exclusion or primitive.'}
(out/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
(out/'minor-row-order.json').write_text(json.dumps({'selected_rows':selected,'are_first_rows_as_set':set(selected)==set(range(len(selected))) if selected else None,'permutation_inversions':sum(selected[i]>selected[j] for i in range(len(selected)) for j in range(i+1,len(selected))) if selected else None},indent=2)+'\n',encoding='utf-8')
print(json.dumps(result,indent=2))

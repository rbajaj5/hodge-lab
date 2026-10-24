"""Independent reduced joint Laurent + A^-1 reconstruction.

Literal-AST evaluation, exponent-lowered derivative, and modular Bareiss differ
from the author's evaluator/elimination. The necessary294 denominator reduction
is an imported coordinator result, not replayed here. Independent matrix entries
use its reduced operator; the author's entries use direct quotient derivatives.
"""
from pathlib import Path
import ast,datetime,hashlib,json,sys,time
import numpy as np
start=time.monotonic();out=Path(sys.argv[1]);out.mkdir(parents=True,exist_ok=False)
root=Path(__file__).resolve().parents[3];author=Path(sys.argv[2]).resolve()
packet=root/'results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'
pin='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
if hashlib.sha256(packet.read_bytes()).hexdigest()!=pin:raise RuntimeError('Pinned connection changed')
data=json.loads(packet.read_text(encoding='utf-8'));inputs=json.loads((author/'inputs.json').read_text(encoding='utf-8'));receipt=json.loads((author/'validation.json').read_text(encoding='utf-8'))
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
basis=[['h',-1,j,m,n,k] for j in range(2) for m in range(-10,-5) for n in range(2) for k in range(3)]
basis += [['Pt',2,j,m,n,k] for j in range(2) for m in range(-10,3) for n in range(3) for k in range(3)]
basis += [['Laurent',direction,j,m,n,k] for direction in range(3) for j in range(2) for m in range(-10,3) for n in range(3) for k in range(3)]
if inputs['basis']!=basis:raise RuntimeError('Unexpected declared joint basis')
rebuilt=[];controls=None;domains=0
for sample in inputs['samples']:
    r,v,t=sample['point']
    if not all(0<x<p for x in [r,v,t]):raise RuntimeError('Invalid sample')
    h=v*r-1
    A=(pow(r,3,p)+pow(r,-3,p)+pow(h,6,p)*pow(r,-15,p))%p
    Ar=(3*r*r-3*pow(r,-4,p)+6*v*pow(h,5,p)*pow(r,-15,p)-15*pow(h,6,p)*pow(r,-16,p))%p
    Av=6*pow(h,5,p)*pow(r,-14,p)%p
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
    lam=3*r*(pow(r,6,p)-1)%p
    zeroth=(7*pow(r,7,p)+6*r)%p
    if (Tr*Ar+Tv*Av-lam*A)%p:raise RuntimeError('Tangency source binding failed at sample')
    direct_zero=(10*pow(r,7,p)+3*r-(Tr*Ar+Tv*Av)*invA)%p
    if direct_zero!=zeroth:raise RuntimeError('Quotient zero-order mismatch')
    Hmat=[[(lam*A*M['a'][i][j]+t*Tv*M['b'][i][j]+(zeroth if i==j else 0))%p for j in range(2)] for i in range(2)]
    for i in range(2):
        for j in range(2):
            if (Tr*N[0][i][j]+Tv*N[1][i][j]+(direct_zero if i==j else 0)-Hmat[i][j])%p:raise RuntimeError('Reduced connection matrix mismatch')
    rr=[[],[]]
    for sector,direction,j,m,n,k in basis:
        exp=[m,n,k];mon=pow(r,m,p)*pow(v,n,p)*pow(t,k,p)%p
        if sector=='h':
            derivative=(Tr*m*pow(r,m-1,p)*pow(v,n,p)*pow(t,k,p)+Tv*n*pow(r,m,p)*pow(v,n-1,p)*pow(t,k,p))%p
            for i in range(2):rr[i].append((Hmat[i][j]*mon+(derivative if i==j else 0))%p)
        else:
            lower=exp.copy();lower[direction]-=1
            derivative=exp[direction]*pow(r,lower[0],p)*pow(v,lower[1],p)*pow(t,lower[2],p)%p
            scale=A if sector=='Laurent' else 1
            for i in range(2):rr[i].append(scale*(N[direction][i][j]*mon+(derivative if i==j else 0))%p)
    target=[A*pow(r,-4,p)*pow(12,-1,p)*M['b'][i][0]%p for i in range(2)]
    for i in range(2):rebuilt.append(rr[i]+[target[i]])
    if controls is None:
        unit=pow(r,-10,p)
        differences={'omit_r_quotient_term':unit*Tr*Ar*invA%p,'omit_v_quotient_term':unit*Tv*Av*invA%p,'reverse_quotient_sign':2*unit*lam%p,'omit_Av_connection_chain':unit*Tv*Av*M['a'][0][0]%p,'omit_source_1_over_12':11*target[0]%p,'reverse_source_sign':2*target[0]%p,'omit_Pt_derivative':unit}
        if all(differences.values()):controls={'point':sample['point'],'nonzero_differences':differences}
if controls is None:raise RuntimeError('Mutation controls did not discriminate')
B=np.array(rebuilt,dtype=np.int64);saved=np.loadtxt(author/'augmented-matrix.csv',delimiter=',',dtype=np.int64)
if B.shape[1]!=997 or not np.array_equal(B,saved):raise RuntimeError('Joint augmented matrix mismatch')
print('all joint matrix entries independently reconstructed',B.shape,flush=True)
rank=receipt['rank_coefficient'];aug=receipt['rank_augmented'];det=None
if rank==996 and aug==997:
    selected=receipt['pivot_source_rows']
    if len(selected)!=997 or len(set(selected))!=997:raise RuntimeError('Invalid minor rows')
    H=B[selected,:].copy();previous=1;sign=1
    if 2*(p-1)**3>=2**63:raise RuntimeError('Integer overflow guard failed')
    for k in range(996):
        nz=np.flatnonzero(H[k:,k])
        if not len(nz):raise RuntimeError('Claimed minor singular')
        j=k+int(nz[0])
        if j!=k:H[[k,j]]=H[[j,k]];sign=-sign
        pivot=int(H[k,k]);H[k+1:,k+1:]=((pivot*H[k+1:,k+1:]-H[k+1:,k,None]*H[k,k+1:])*pow(previous,-1,p))%p
        H[k+1:,k]=0;previous=pivot
    det=sign*int(H[-1,-1])%p
    if not det:raise RuntimeError('Zero augmented determinant')
    status='PASS_EXACT_QQ_JOINT_FINITE_FAMILY_EXCLUSION'
else:
    status='PASS_MATRIX_ONLY_EXACT_KERNEL_OR_RANK_CERTIFICATE_REQUIRED'
result={'status':status,'executor':'a_denominator_checker AI worker','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'seconds':time.monotonic()-start,'python':sys.version,'numpy':np.__version__,'packet_sha256':pin,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'author_validation_sha256':hashlib.sha256((author/'validation.json').read_bytes()).hexdigest(),'inputs_sha256':hashlib.sha256((author/'inputs.json').read_bytes()).hexdigest(),'matrix_sha256':hashlib.sha256((author/'augmented-matrix.csv').read_bytes()).hexdigest(),'matrix_shape':list(B.shape),'entries_reconstructed':int(B.size),'domain_points_checked':domains,'author_modular_rank_coefficient':rank,'author_modular_rank_augmented':aug,'independent_augmented_minor_det_mod_prime':det,'prime':p,'mutations':controls,'scope':'Reduced996-parameter current family: h60,Pt234,Laurent702. Exact exclusion follows from the997augmented minor. Exclusion of original1404parameter B/A+B additionally uses the imported necessary tangency/support theorem; that structural theorem was not rerun by this checker. No general current exclusion or solve.'}
(out/'validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))

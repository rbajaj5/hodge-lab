"""Independent literal-AST reconstruction and Bareiss minor certificate.
No SymPy polynomial evaluator, author elimination, or floating point is used.
The prime-field computation certifies a nonzero rational augmented minor;
it excludes precisely the declared finite six-component Laurent family.
"""
from pathlib import Path
import ast, datetime, hashlib, json, sys, time
import numpy as np
start=time.monotonic();root=Path(__file__).resolve().parents[3]
packet=root/'results/skew-physical-source-20261023/inputs/benediamond/packet/one-reflection-skew-followup/inputs/source-rank2-connection.json'
expected='a86c01f7fed725aac86e958a10f484b9b340765714c5b228513890977a59ce5d'
if hashlib.sha256(packet.read_bytes()).hexdigest()!=expected:raise RuntimeError('Connection pin changed')
data=json.loads(packet.read_text(encoding='utf-8'))
author=root/'results/skew-mixed-construction-20261024/lead/physical-laurent-01/result'
inputs=json.loads((author/'inputs.json').read_text(encoding='utf-8'));receipt=json.loads((author/'validation.json').read_text(encoding='utf-8'))
p=inputs['prime']
if p!=32003 or any(p%k==0 for k in range(2,int(p**0.5)+1)):raise RuntimeError('Prime gate failed')
def number(node):
 if isinstance(node,ast.Constant) and isinstance(node.value,int):return node.value
 if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.USub):return -number(node.operand)
 raise RuntimeError('Nonliteral exponent')
def evaluate(node,env):
 if isinstance(node,ast.Constant) and isinstance(node.value,int):return node.value%p
 if isinstance(node,ast.Name):return env[node.id]%p
 if isinstance(node,ast.UnaryOp) and isinstance(node.op,ast.USub):return -evaluate(node.operand,env)%p
 if isinstance(node,ast.BinOp):
  left=evaluate(node.left,env)
  if isinstance(node.op,ast.Pow):return pow(left,number(node.right),p)
  right=evaluate(node.right,env)
  if isinstance(node.op,ast.Add):return (left+right)%p
  if isinstance(node.op,ast.Sub):return (left-right)%p
  if isinstance(node.op,ast.Mult):return left*right%p
  if isinstance(node.op,ast.Div):return left*pow(right,-1,p)%p
 raise RuntimeError('Unsupported literal AST node')
parsed={name:[[ast.parse(expr,mode='eval').body for expr in row] for row in mat] for name,mat in data['connection'].items()}
delta_ast=ast.parse(data['Delta'],mode='eval').body
expected_basis=[[i,j,m,n,k] for i in range(3) for j in range(2) for m in range(-10,3) for n in range(3) for k in range(3)]
if inputs['basis']!=expected_basis:raise RuntimeError('Ansatz changed')
rebuilt=[];domain_checks=0;control=None
for sample in inputs['samples']:
 r,v,t=sample['point']
 if not all(0<x<p for x in [r,v,t]):raise RuntimeError('Invalid nonzero point')
 powers=lambda x,e:pow(x,e,p)
 A=(r**3+powers(r,-3)+powers(v*r-1,6)*powers(r,-15))%p
 # Explicit derivative of the actual rational chart; includes both product terms.
 Ar=(3*r*r-3*powers(r,-4)+6*v*powers(v*r-1,5)*powers(r,-15)-15*powers(v*r-1,6)*powers(r,-16))%p
 Av=6*powers(v*r-1,5)*powers(r,-14)%p
 C=t*(1-t*t)*pow(7,-1,p)%p;D=(1+powers(t,6))%p
 env={'a':A,'b':t*v%p,'c':C,'d':D}
 delta=evaluate(delta_ast,env)
 if A==0 or delta==0:raise RuntimeError('Excluded physical denominator')
 observed={'a':A,'Ar':Ar,'Av':Av,'Delta':delta}
 if observed!=sample['domain']:raise RuntimeError('Chart binding mismatch')
 domain_checks+=1
 M={name:[[evaluate(node,env) for node in row] for row in mat] for name,mat in parsed.items()}
 N=[[[Ar*M['a'][i][j]%p for j in range(2)] for i in range(2)],
    [[(Av*M['a'][i][j]+t*M['b'][i][j])%p for j in range(2)] for i in range(2)],
    [[(v*M['b'][i][j]+((1-3*t*t)*pow(7,-1,p)%p)*M['c'][i][j]+6*powers(t,5)*M['d'][i][j])%p for j in range(2)] for i in range(2)]]
 rows=[[],[]]
 for direction,j,m,n,k in expected_basis:
  mon=powers(r,m)*powers(v,n)*powers(t,k)%p
  exponent=[m,n,k];point=[r,v,t]
  # Derivative is evaluated from the exponent-lowered monomial, independently
  # of the author's value*(m/r) construction.
  shifted=exponent.copy();shifted[direction]-=1
  derivative=exponent[direction]*powers(r,shifted[0])*powers(v,shifted[1])*powers(t,shifted[2])%p
  for i in range(2):rows[i].append((mon*N[direction][i][j]+(derivative if i==j else 0))%p)
 target=[powers(r,-4)*pow(12,-1,p)*M['b'][i][0]%p for i in range(2)]
 for i in range(2):rebuilt.append(rows[i]+[target[i]])
 if control is None:
  controls={'omit_Av_chain_term':Av*M['a'][0][0]%p,
            'drop_source_1_over_12':powers(r,-4)*M['b'][0][0]*(1-pow(12,-1,p))%p,
            'reverse_source_sign':2*target[0]%p,
            'wrong_laurent_derivative_sign':20*powers(r,-11)%p}
  if all(controls.values()):control={'sample':sample['point'],'nonzero_differences':controls}
if control is None:raise RuntimeError('Could not distinguish required mutations')
B=np.array(rebuilt,dtype=np.int64)
saved=np.loadtxt(author/'augmented-matrix.csv',dtype=np.int64,delimiter=',')
if B.shape!=(762,703) or not np.array_equal(B,saved):raise RuntimeError('Full physical augmented matrix mismatch')
print('all 535686 matrix entries independently reconstructed',flush=True)
# Verify the exact saved minor by a different elimination algorithm.
minor_rows=receipt['pivot_source_rows']
if len(minor_rows)!=703 or len(set(minor_rows))!=703:raise RuntimeError('Invalid claimed square minor')
H=B[minor_rows,:].copy();previous=1;sign=1;swaps=0
for k in range(H.shape[0]-1):
 nonzero=np.flatnonzero(H[k:,k])
 if not len(nonzero):raise RuntimeError('Claimed minor singular')
 pivotrow=k+int(nonzero[0])
 if pivotrow!=k:H[[k,pivotrow]]=H[[pivotrow,k]];sign=-sign;swaps+=1
 pivot=int(H[k,k])
 # Every value is reduced modulo p; the largest pre-reduction product is
 # bounded by 2*(p−1)^3 < 2^63, so signed NumPy int64 cannot overflow.
 H[k+1:,k+1:]=((pivot*H[k+1:,k+1:]-H[k+1:,k,None]*H[k,k+1:])*pow(previous,-1,p))%p
 H[k+1:,k]=0;previous=pivot
minor_det=int(H[-1,-1])*sign%p
if minor_det==0:raise RuntimeError('Zero augmented determinant')
if 2*(p-1)**3>=2**63:raise RuntimeError('Integer overflow guard failed')
out=Path(sys.argv[1])
if out.exists():raise RuntimeError('Fresh output required')
out.parent.mkdir(parents=True,exist_ok=False)
result={'status':'PASS_INDEPENDENT_QQ_FINITE_FAMILY_EXCLUSION','executor':'mixed_checker AI worker','created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'elapsed_seconds':time.monotonic()-start,'python':sys.version,'numpy':np.__version__,'packet_sha256':expected,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'inputs_sha256':hashlib.sha256((author/'inputs.json').read_bytes()).hexdigest(),'matrix_sha256':hashlib.sha256((author/'augmented-matrix.csv').read_bytes()).hexdigest(),'author_validation_sha256':hashlib.sha256((author/'validation.json').read_bytes()).hexdigest(),'prime':p,'matrix_shape':list(B.shape),'independently_reconstructed_entries':int(B.size),'domain_points_checked':domain_checks,'square_minor_size':703,'minor_rows':minor_rows,'minor_determinant_mod_prime':minor_det,'bareiss_row_swaps':swaps,'int64_absolute_intermediate_bound':2*(p-1)**3,'mutations':control,'rational_conclusion':'The 703-column augmented rational sample matrix has a minor nonzero modulo32003, hence nonzero overQ. With702 coefficient columns, the declared finite family is inconsistent overQ. This does not rely on reducing an unknown solution denominator modulo p.','scope':'All six physical flux components independently span r^m v^n t^k, m=-10..2,n=0..2,k=0..2. Exact bounded-family exclusion only; no exclusion of arbitrary rational mixed currents, no primitive or target solve.'}
out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:x for k,x in result.items() if k!='minor_rows'},indent=2))

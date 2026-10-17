"""CUDA coefficient-rank screening of a bounded degree-eight polar selection.

Finite-field inconsistencies are screening observations, not rational proofs.
The matrices use every one of the 175 projected correction types. CPU ranks
and constructed consistent controls check the CUDA elimination separately.
"""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import random
import time

import cyclic_fano_cubic_polars as model
from gpu_identity_screen import load_cupy

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/cyclic-fano-cubic-gpu'
PRIME = 65521
SEED = 202610178

CUDA = r'''
extern "C" __global__ void select_pivot(
  const int rows, const int cols, const int col, const long long p,
  long long* a, int* used, int* pivots, int* ranks, int* prefix) {
 int b=blockIdx.x;
 if(threadIdx.x)return;
 int r=-1;
 for(int i=0;i<rows;i++)
   if(!used[b*rows+i] && a[(b*rows+i)*cols+col]){r=i;break;}
 pivots[b]=r;
 if(r>=0){
   used[b*rows+r]=1;ranks[b]++;
   long long x=a[(b*rows+r)*cols+col],inv=1,e=p-2;
   while(e){if(e&1)inv=(inv*x)%p;x=(x*x)%p;e>>=1;}
   for(int j=col;j<cols;j++)a[(b*rows+r)*cols+j]=(a[(b*rows+r)*cols+j]*inv)%p;
 }
 if(col==cols-2)prefix[b]=ranks[b];
}
extern "C" __global__ void eliminate(
 const int rows, const int cols, const int col, const long long p,
 long long* a, const int* used, const int* pivots) {
 int b=blockIdx.x,r=blockIdx.y;
 if(used[b*rows+r] || pivots[b]<0)return;
 // Each row's factor is read before any thread overwrites its column.
 __shared__ long long factor;
 if(threadIdx.x==0)factor=a[(b*rows+r)*cols+col];
 __syncthreads();
 if(!factor)return;
 for(int j=col+threadIdx.x;j<cols;j+=blockDim.x){
   long long z=(factor*a[(b*rows+pivots[b])*cols+j])%p;
   a[(b*rows+r)*cols+j]=(a[(b*rows+r)*cols+j]+p-z)%p;
 }
}
'''


def sha(path):
    return hashlib.sha256(path.read_bytes().replace(b'\r\n', b'\n')).hexdigest()


def selection(data):
    rng = random.Random(SEED)
    choices = []
    # Five monomial controls, one in each component; then mixed-component
    # directions which cannot be covered by a one-component family test.
    for i in range(5):
        choices.append(('monomial-control', {35*i+i: Fraction(1)}))
    for i in range(5):
        choices.append(('two-component', {35*i+i: Fraction(1),
                         35*((i+1)%5)+34-i: Fraction(-1 if i%2 else 1)}))
    for i in range(6):
        support = rng.sample(range(175), 8 if i<3 else 175)
        choices.append(('seeded-eight-term' if i<3 else 'seeded-dense',
                        {j: Fraction(rng.choice([-2,-1,1,2])) for j in support}))
    return choices


def mod(c):
    c = Fraction(c)
    assert c.denominator % PRIME
    return c.numerator % PRIME * pow(c.denominator, -1, PRIME) % PRIME


def cpu_rank(matrix):
    """Independent NumPy echelon implementation, with ordinary row swaps."""
    import numpy as np
    a=matrix.copy();rank=0;prefix=None
    for j in range(a.shape[1]):
        candidates=np.flatnonzero(a[rank:,j])
        if len(candidates):
            r=rank+int(candidates[0]);a[[rank,r]]=a[[r,rank]]
            a[rank,j:]=a[rank,j:]*pow(int(a[rank,j]),-1,PRIME)%PRIME
            f=a[rank+1:,j].copy()
            a[rank+1:,j:]=(a[rank+1:,j:]-f[:,None]*a[rank,j:])%PRIME
            rank+=1
        if j==a.shape[1]-2:prefix=rank
    return [prefix,rank]


def modular_minor(matrix):
    """Choose independent rows, then certify their square minor modulo p."""
    import numpy as np
    a=matrix.copy();origins=list(range(len(a)));chosen=[]
    for j in range(a.shape[1]):
        candidates=np.flatnonzero(a[j:,j])
        assert len(candidates), 'Expected full column rank in the reduced augmented map'
        r=j+int(candidates[0]);a[[j,r]]=a[[r,j]]
        origins[j],origins[r]=origins[r],origins[j]
        chosen.append(origins[j])
        a[j,j:]=a[j,j:]*pow(int(a[j,j]),-1,PRIME)%PRIME
        f=a[j+1:,j].copy()
        a[j+1:,j:]=(a[j+1:,j:]-f[:,None]*a[j,j:])%PRIME
    a=matrix[chosen].copy();det=1
    for j in range(a.shape[1]):
        r=j+int(np.flatnonzero(a[j:,j])[0])
        if r!=j:a[[j,r]]=a[[r,j]];det=-det
        value=int(a[j,j]);det=det*value%PRIME
        a[j,j:]=a[j,j:]*pow(value,-1,PRIME)%PRIME
        f=a[j+1:,j].copy()
        a[j+1:,j:]=(a[j+1:,j:]-f[:,None]*a[j,j:])%PRIME
    assert det
    return chosen,int(det)


def main():
    import numpy as np
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--deps',type=Path)
    parser.add_argument('--output',type=Path,default=OUT)
    args=parser.parse_args()
    started=time.perf_counter();data=model.prepare();cases=[];polys=[]
    for kind,direction in selection(data):
        columns,rhs,metadata=model.fixed_columns(direction,data)
        cases.append(dict(kind=kind,**metadata));polys.append(columns+[rhs])
    monomials=sorted(set().union(*(set(p)for cols in polys for p in cols)))
    row_of={m:i for i,m in enumerate(monomials)}
    arrays=np.zeros((len(cases),len(monomials),176),dtype=np.int64)
    for b,cols in enumerate(polys):
        for j,p in enumerate(cols):
            for m,c in p.items():arrays[b,row_of[m],j]=mod(c)
    # A consistent control for each same correction matrix: rhs=M*z.
    z=np.array([(i%7)-3 for i in range(175)],dtype=np.int64)
    controls=arrays.copy()
    controls[:,:,-1]=np.einsum('brc,c->br',arrays[:,:,:175],z)%PRIME
    batch=np.concatenate([arrays,controls])
    construction_seconds=time.perf_counter()-started
    print(json.dumps({'stage':'matrices','shape':list(batch.shape),
                      'construction_seconds':construction_seconds}),flush=True)
    cp,handles=load_cupy(args.deps)
    pivot=cp.RawKernel(CUDA,'select_pivot');elim=cp.RawKernel(CUDA,'eliminate')
    def gpu_rank(a):
        n,rows,cols=a.shape
        used=cp.zeros((n,rows),dtype=cp.int32);pivots=cp.empty(n,dtype=cp.int32)
        ranks=cp.zeros(n,dtype=cp.int32);prefix=cp.zeros(n,dtype=cp.int32)
        for j in range(cols):
            pivot((n,),(1,),(np.int32(rows),np.int32(cols),np.int32(j),np.int64(PRIME),a,used,pivots,ranks,prefix))
            elim((n,rows),(128,),(np.int32(rows),np.int32(cols),np.int32(j),np.int64(PRIME),a,used,pivots))
        return cp.stack([prefix,ranks],axis=1)
    # Small deliberate edge cases compile kernels and test zero/identity rank.
    toy=np.zeros((3,4,4),dtype=np.int64)
    toy[1,:,:]=np.eye(4,dtype=np.int64)
    toy[2,:,:3]=np.eye(4,3,dtype=np.int64);toy[2,:,3]=toy[2,:,0]
    assert cp.asnumpy(gpu_rank(cp.asarray(toy))).tolist()==[[0,0],[3,4],[3,3]]
    a=cp.asarray(batch);cp.cuda.Device().synchronize()
    t=time.perf_counter();gpu=cp.asnumpy(gpu_rank(a));cp.cuda.Device().synchronize()
    gpu_seconds=time.perf_counter()-t
    print(json.dumps({'stage':'GPU','seconds':gpu_seconds,'ranks':gpu.tolist()}),flush=True)
    t=time.perf_counter();cpu=np.array([cpu_rank(a) for a in batch])
    cpu_seconds=time.perf_counter()-t
    assert np.array_equal(gpu,cpu),'CPU/CUDA rank mismatch'
    assert np.all(gpu[len(cases):,0]==gpu[len(cases):,1])
    for i,case in enumerate(cases):
        case['rank_mod_prime'],case['augmented_rank_mod_prime']=map(int,gpu[i])
        case['consistent_control_ranks']=list(map(int,gpu[len(cases)+i]))
        case['modular_inconsistent']=bool(gpu[i,1]>gpu[i,0])
        case['matrix_sha256']=hashlib.sha256(arrays[i].astype('<i8').tobytes()).hexdigest()
        minor_rows,det=modular_minor(arrays[i][:,list(range(150))+[175]])
        case['augmented_minor_columns']=list(range(150))+[175]
        case['augmented_minor_rows']=[list(monomials[r]) for r in minor_rows]
        case['augmented_minor_determinant_mod_prime']=det
    device=cp.cuda.runtime.getDeviceProperties(cp.cuda.Device().id)
    name=device['name'];name=name.decode()if isinstance(name,bytes)else name
    bindings={p.relative_to(ROOT).as_posix():sha(p)for p in
              (Path(__file__),ROOT/'experiments/cyclic_fano_cubic_polars.py',
               ROOT/'experiments/gpu_identity_screen.py',
               ROOT/'results/cyclic-fano-curve/source/instance.rec')}
    report=dict(status='PASS',prime=PRIME,seed=SEED,device=name,cupy=cp.__version__,
                bindings=bindings,correction_types=175,spatial_rows=len(monomials),
                cases=cases,cpu_checked_matrices=len(batch),constructed_consistent_controls=len(cases),
                toy_controls=3,construction_seconds=construction_seconds,
                gpu_rank_seconds=gpu_seconds,cpu_rank_seconds=cpu_seconds,
                limits='A finite coefficient-rank screen in one finite field with exported nonzero151x151 minors. Modular inconsistency alone does not prove inconsistency over Q or C. A separate independent checker verifies the exact universal rank upper bound150 and these minors, which together can certify the16 fixed rejections over Q/C. Timings cover these implementations on this batch, exclude CUDA compilation, GPU upload and minor extraction, and are not a general speedup claim.')
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:v for k,v in report.items()if k not in ('bindings','cases')}),flush=True)


if __name__=='__main__':main()

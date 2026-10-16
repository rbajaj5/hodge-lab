"""Weighted graph GFF, harmonic reference field and phase-response experiment.

Finite genus-48 combinatorial mesh; regularized illustrations, not SLE.
The exact finite-Gaussian characteristic-function formula predicts the
relative-phase coherence. Smooth crossovers cannot be thermodynamic singularities.
"""
from pathlib import Path
import argparse, hashlib, json, time
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import splu
from scipy.optimize import minimize_scalar, brentq
from high_genus_complex import build_incidence, GPUComplex
from gpu_identity_screen import load_cupy

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/high-genus-flow'
SEED=202610164801
CHI=.62
ANISOTROPY=[-1.6,0.,1.6]
STIFFNESS=np.logspace(-3,2,101)

CUDA=r'''
extern "C" __global__ void weighted_lap(int n,int b,const int* ptr,const int* edge,
 const int* endpoints,const double* weight,const double* x,double* y){
 int id=blockIdx.x*blockDim.x+threadIdx.x;if(id>=n*b)return;
 int i=id/b,k=id%b;if(i==0){y[id]=x[id];return;}double value=0;
 for(int p=ptr[i];p<ptr[i+1];p++){
  int e=edge[p],j=endpoints[2*e]+endpoints[2*e+1]-i;
  value+=weight[e]*(x[id]-(j==0?0:x[j*b+k]));
 }y[id]=value;
}
'''

class WeightedGraph(GPUComplex):
    def __init__(self,cp,topo,c):
        super().__init__(cp,topo);self.c=cp.asarray(c)
        self.kernel=cp.RawKernel(CUDA,'weighted_lap')
        self.degree=cp.bincount(self.a['edges'].ravel(),weights=cp.repeat(self.c,2),minlength=topo['nv'])
        self.degree[0]=1
    def lap(self,x,kind):
        assert kind=='vertex'
        n,b=x.shape;out=self.cp.empty_like(x)
        self.kernel(((n*b+255)//256,),(256,),
            (np.int32(n),np.int32(b),self.a['d0t_ptr'],self.a['d0t_edges'],self.a['edges'],self.c,x,out))
        return out
    def solve(self,rhs,kind='vertex',tol=2e-11,maxiter=6000):
        cp=self.cp;rhs=rhs.copy();rhs[0]=0
        x=cp.zeros_like(rhs);r=rhs.copy();norm=cp.sqrt(cp.sum(r*r,axis=0))
        z=r/self.degree[:,None];p=z.copy();rz=cp.sum(r*z,axis=0)
        start=time.perf_counter()
        for it in range(1,maxiter+1):
            ap=self.lap(p,kind);alpha=rz/cp.sum(p*ap,axis=0)
            x+=p*alpha;r-=ap*alpha
            if it%20==0 and float(cp.max(cp.sqrt(cp.sum(r*r,axis=0))/norm).get())<tol:
                true=rhs-self.lap(x,kind)
                residual=float(cp.max(cp.sqrt(cp.sum(true*true,axis=0))/norm).get())
                if residual<5*tol:break
                r=true;z=r/self.degree[:,None];p=z.copy();rz=cp.sum(r*z,axis=0);continue
            z=r/self.degree[:,None];new=cp.sum(r*z,axis=0);p=z+p*(new/rz);rz=new
        else:raise ArithmeticError('Weighted PCG did not converge')
        assert np.isfinite(residual)
        x-=cp.mean(x,axis=0,keepdims=True)
        return x,{'iterations':it,'max_grounded_residual':residual,'seconds':time.perf_counter()-start}

def conductances(v,edges,a):
    delta=v[edges[:,1]]-v[edges[:,0]]
    direction=delta[:,0]**2/np.sum(delta*delta,axis=1)
    return np.exp(2*a*(direction-direction.mean()))

def smooth(gpu,x,steps=64):
    # Positive Markov smoothing, with a strict bound from max vertex degree.
    dt=.4/np.diff(gpu.t['vertex_ptr']).max();x=x.copy()
    for _ in range(steps):x-=dt*gpu.d0t(gpu.d0(x))
    return x

def phase_prediction(covariance,stiffness=STIFFNESS):
    var=np.diag(covariance)[:,None]+np.diag(covariance)[None,:]-2*covariance
    if var.min() < -1e-8:raise ArithmeticError('Negative Gaussian increment variance')
    var=np.maximum(var,0)/(2*CHI**2)
    x=var[None,:,:]/np.asarray(stiffness)[:,None,None]
    return np.exp(-x).mean(axis=(1,2)),(x*np.exp(-x)).mean(axis=(1,2))

def phase_statistics(cov):
    def response(logk):return phase_prediction(cov,[np.exp(logk)])[1][0]
    opt=minimize_scalar(lambda x:-response(x),bounds=(-12,12),method='bounded')
    peak=np.exp(opt.x);height=-opt.fun
    lo=brentq(lambda x:response(x)-height/2,-25,opt.x)
    hi=brentq(lambda x:response(x)-height/2,opt.x,25)
    return {'response_peak_stiffness':float(peak),'response_peak_height':float(height),
            'half_max_stiffness_interval':[float(np.exp(lo)),float(np.exp(hi))],
            'half_max_width_decades':float((hi-lo)/np.log(10))}

def covariance_product(cp,left,right):
    # Reductions work in the project's small CUDA runtime without cuBLAS.
    return cp.asnumpy(cp.stack([cp.sum(left*right[:,j,None],axis=0) for j in range(right.shape[1])],axis=1))

def run(args):
    start=time.perf_counter();cp,handles=load_cupy(args.deps)
    mesh=np.load(OUT/'surface.npz');v=mesh['vertices'].astype(float);f=mesh['faces'].astype(np.int32)
    topo=build_incidence(v,f);nv,ne,nf=topo['nv'],topo['ne'],topo['nf']
    assert nv-ne+nf==-94
    unit=GPUComplex(cp,topo);rng=np.random.default_rng(SEED)
    noise=cp.asarray(rng.standard_normal((ne,args.samples)))
    anchors=np.sort(rng.choice(nv,96,replace=False));indicator=np.zeros((nv,len(anchors)))
    indicator[anchors,np.arange(len(anchors))]=1;indicator-=1/nv
    probe=smooth(unit,cp.asarray(indicator))
    reports=[];display=[];covariances=[];predicted=[];mcmeans=[];mcses=[];anchor_samples=[];smoothing_controls=[]
    edges=topo['edges'];d0=sparse.coo_matrix((np.tile([-1.,1.],ne),(np.repeat(np.arange(ne),2),edges.ravel())),shape=(ne,nv)).tocsr()
    for a in ANISOTROPY:
        c=conductances(v,edges,a);graph=WeightedGraph(cp,topo,c)
        rhs=graph.d0t(cp.sqrt(graph.c)[:,None]*noise)
        phi,diag=graph.solve(rhs)
        full_error=float(cp.max(cp.sqrt(cp.sum((graph.d0t(graph.c[:,None]*graph.d0(phi))-rhs)**2,axis=0))/cp.sqrt(cp.sum(rhs*rhs,axis=0))).get())
        assert full_error<1e-8
        h=smooth(unit,phi);display.append(cp.asnumpy(h[:,0]))
        inverse,solve=graph.solve(probe);cov=covariance_product(cp,probe,inverse);cov=(cov+cov.T)/2
        assert np.linalg.eigvalsh(cov).min()>0
        covariances.append(cov);mean,response=phase_prediction(cov);predicted.append(mean)
        values=cp.asnumpy(h[anchors]);anchor_samples.append(values);emp=[];se=[]
        for k in STIFFNESS:
            m2=abs(np.exp(1j*values/(CHI*np.sqrt(k))).mean(axis=0))**2
            emp.append(float(m2.mean()));se.append(float(m2.std(ddof=1)/np.sqrt(args.samples)))
        mcmeans.append(emp);mcses.append(se)
        # Independent SciPy factorization checks one adjoint covariance column and one sample.
        L=(d0.T@sparse.diags(c)@d0).tocsc();lu=splu(L[1:,1:])
        target=cp.asnumpy(cp.column_stack([probe[:,0],rhs[:,0]]));check=np.zeros_like(target)
        check[1:]=lu.solve(target[1:]);check-=check.mean(axis=0)
        gpu=cp.asnumpy(cp.column_stack([inverse[:,0],phi[:,0]]))
        error=float(np.linalg.norm(check-gpu)/np.linalg.norm(check));assert error<1e-8
        energy=cp.asnumpy(cp.sum(graph.c[:,None]*graph.d0(phi)**2,axis=0))
        reports.append({'anisotropy':a,'conductance_range':[float(c.min()),float(c.max())],
            'sample_solve':diag,'covariance_solve':solve,'max_full_relative_residual':full_error,
            'scipy_independent_relative_error':error,'mean_edge_energy':float(energy.mean()),
            'edge_energy_standard_error':float(energy.std(ddof=1)/np.sqrt(args.samples)),
            'expected_edge_energy':nv-1,'phase_response':phase_statistics(cov)})
        if a==0:
            for steps in [0,16,128]:
                u=smooth(unit,cp.asarray(indicator),steps);answer,_=graph.solve(u)
                C=covariance_product(cp,u,answer);C=(C+C.T)/2
                smoothing_controls.append({'smoothing_steps':steps,**phase_statistics(C)})
        print('Genus48 anisotropy',a,'complete',reports[-1]['phase_response'],flush=True)
    # A genuine cochain Hodge projection supplies a reference direction for the drawing.
    z=cp.asarray(np.random.default_rng(SEED+1).standard_normal((ne,1)))
    exact,_=unit.solve(unit.d0t(z),'vertex');coexact,_=unit.solve(unit.d1(z),'dual')
    harmonic=z-unit.d0(exact)-unit.d1t(coexact);harmonic/=cp.linalg.norm(harmonic)
    closed=float(cp.linalg.norm(unit.d1(harmonic)).get());coclosed=float(cp.linalg.norm(unit.d0t(harmonic)).get())
    assert max(closed,coclosed)<1e-7
    np.savez_compressed(OUT/'fields.npz',fields=np.array(display),covariances=np.array(covariances),
        anchors=anchors,anisotropy=ANISOTROPY,stiffness=STIFFNESS,prediction=predicted,
        mc_mean=mcmeans,mc_se=mcses,anchor_samples=anchor_samples,harmonic=cp.asnumpy(harmonic[:,0]))
    report={'seed':SEED,'samples_per_weight':args.samples,'fixed_anchor_vertices':len(anchors),
        'device':cp.cuda.runtime.getDeviceProperties(0)['name'].decode(),'vertices':nv,'edges':ne,'faces':nf,
        'genus':48,'harmonic_dimension_from_topology':96,'chi_display':CHI,
        'smoothing_steps':64,'smoothing_dt':float(.4/np.diff(topo['vertex_ptr']).max()),
        'mesh_sha256':hashlib.sha256((OUT/'surface.npz').read_bytes()).hexdigest(),
        'experiments':reports,'smoothing_controls':smoothing_controls,
        'harmonic_closed_residual':closed,'harmonic_coclosed_residual':coclosed,
        'seconds':time.perf_counter()-start,
        'interpretation':'Analytic finite-Gaussian phase-decoherence crossover, not a detected thermodynamic phase transition. Scalar relative-phase coherence uses 96 fixed vertices, not parallel-transported tangent alignment. No mesh/volume limit, dimer model, compact winding sectors, SLE theorem or algebraic certificate.',
        'compute':'Seeded CPU noise; CUDA sampling, smoothing, covariance and Hodge projections. Independent SciPy sparse solves. CPU analytic response formulas.'}
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--deps',type=Path);parser.add_argument('--samples',type=int,default=256)
    run(parser.parse_args())

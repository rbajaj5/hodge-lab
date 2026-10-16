"""A convex planar anisotropic-flow probe derived from the holdout sextic.

Implements a finite-difference support-function flow with Euclidean mobility,
followed by a small area projection. This is a discretization of the smooth
convex case of Kim--Kwon (2405.08296), not their general flat-flow scheme.
"""
from pathlib import Path
import argparse, hashlib, json, math
import numpy as np
import gpu_identity_screen as algebra

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'results/anisotropic-flow'
SEED = 202610162137


def second(h):
    dx = 2 * math.pi / h.shape[-1]
    return (np.roll(h, 1, axis=-1) - 2*h + np.roll(h, -1, axis=-1)) / dx**2


def area(h):
    return math.pi / h.shape[-1] * np.sum(h * (h + second(h)), axis=-1)


def setup(n=128, batch=8):
    theta = np.arange(n) * (2*math.pi/n)
    target = algebra.load_target(ROOT / 'sources/sextics/data/holdout')
    rng = np.random.default_rng(SEED)
    plane, _ = np.linalg.qr(rng.normal(size=(6, 2)))
    z = plane @ np.array([np.cos(theta), np.sin(theta)])
    angular = np.zeros(n)
    for exponents, coefficient in target['F'].items():
        angular += float(coefficient) * np.prod(z**np.array(exponents)[:, None], axis=0)
    assert angular.min() > 0
    centered = angular - angular.mean()
    modes = np.fft.fftfreq(n, 1/n)
    g = centered / np.max(np.abs(centered))
    coefficients = np.fft.fft(g)/n
    g2 = np.fft.ifft(-modes**2 * np.fft.fft(g)).real
    # Triangle inequality bounds the stiffness perturbation at EVERY angle,
    # rather than just at the sampled angles.
    stiffness_bound = np.sum(np.abs((1-modes**2)*coefficients))
    epsilon = .35 / stiffness_bound
    phi = 1 + epsilon*g
    stiffness_exact = 1 + epsilon*(g + g2)
    assert stiffness_exact.min() >= .65 - 1e-12
    assert np.max(np.abs(phi - np.roll(phi, n//2))) < 1e-12
    # The discrete stiffness makes h = r*phi an exact discrete equilibrium.
    stiffness = phi + second(phi)
    phases = rng.uniform(0, 2*math.pi, size=(batch, 3))
    h = np.ones((batch, n))
    for j, (k, amplitude) in enumerate([(3, .012), (5, .005), (7, .003)]):
        h += amplitude * np.cos(k*theta + phases[:, j, None])
    assert np.min(h + second(h)) > .5
    return theta, plane, angular, phi, stiffness, h, epsilon, stiffness_exact


def evolve_cpu(h, phi, dt, steps, stride):
    h = h.copy(); target = area(h); frames = [h.copy()]; max_projection = 0.
    a = phi + second(phi)
    for k in range(steps):
        rho = h + second(h)
        if rho.min() <= 0:raise ValueError('Convexity lost; reduce time step.')
        lam = a.sum() / rho.sum(axis=-1)
        v = lam[:, None] - a / rho
        u = h + dt*v
        current = area(u)
        max_projection = max(max_projection, float(np.max(np.abs(current/target-1))))
        if np.any(current <= 0):raise ValueError('Nonpositive discrete area.')
        h = u*np.sqrt(target/current)[:, None]
        if (k+1) % stride == 0:frames.append(h.copy())
    return np.array(frames), max_projection


KERNEL = r'''
extern "C" __global__ void flow(const double* initial,const double* phi,
 double* frames,double* diagnostics,const int n,const int steps,const int stride,const double dt){
 const int i=threadIdx.x, b=blockIdx.x;
 extern __shared__ double memory[];
 double *h=memory, *u=h+n, *rho=u+n, *a=rho+n;
 __shared__ double target,lambda,scale,maxdrift;
 __shared__ int failed;
 const double dx=6.2831853071795864769/n;
 const int lo=(i+n-1)%n, hi=(i+1)%n;
 h[i]=initial[b*n+i];
 a[i]=phi[i]+(phi[lo]-2*phi[i]+phi[hi])/(dx*dx);
 frames[b*n+i]=h[i];
 if(i==0){maxdrift=0;failed=0;}
 __syncthreads();
 rho[i]=h[i]+(h[lo]-2*h[i]+h[hi])/(dx*dx);
 __syncthreads();
 if(i==0){target=0;for(int j=0;j<n;j++)target+=h[j]*rho[j];target*=dx/2;}
 __syncthreads();
 for(int k=0;k<steps;k++){
   rho[i]=h[i]+(h[lo]-2*h[i]+h[hi])/(dx*dx);
   __syncthreads();
   if(i==0){double sumr=0,suma=0;for(int j=0;j<n;j++){
     if(rho[j]<=0)failed=1;sumr+=rho[j];suma+=a[j];}lambda=suma/sumr;}
   __syncthreads();
   if(failed){if(i==0)diagnostics[b]=-1;return;}
   u[i]=h[i]+dt*(lambda-a[i]/rho[i]);
   __syncthreads();
   rho[i]=u[i]+(u[lo]-2*u[i]+u[hi])/(dx*dx);
   __syncthreads();
   if(i==0){double current=0;for(int j=0;j<n;j++)current+=u[j]*rho[j];current*=dx/2;
     if(current<=0)failed=1;scale=sqrt(target/current);
     maxdrift=fmax(maxdrift,fabs(current/target-1));}
   __syncthreads();
   if(failed){if(i==0)diagnostics[b]=-1;return;}
   h[i]=u[i]*scale;
   if((k+1)%stride==0)frames[((k+1)/stride*gridDim.x+b)*n+i]=h[i];
   __syncthreads();
 }
 if(i==0)diagnostics[b]=maxdrift;
}
'''


def evolve_gpu(cp, h, phi, dt, steps, stride):
    batch, n = h.shape
    assert steps % stride == 0
    frames = cp.empty((steps//stride+1, batch, n), dtype=cp.float64)
    diagnostics = cp.empty(batch, dtype=cp.float64)
    kernel = cp.RawKernel(KERNEL, 'flow')
    kernel((batch,), (n,), (cp.asarray(h), cp.asarray(phi), frames, diagnostics,
                           np.int32(n), np.int32(steps), np.int32(stride), np.float64(dt)),
           shared_mem=4*n*8)
    cp.cuda.Device().synchronize()
    values = cp.asnumpy(diagnostics)
    if np.any(values < 0):raise ValueError('Convexity or positive area lost.')
    return cp.asnumpy(frames), float(values.max())


def metrics(frames, phi):
    dx = 2*math.pi / frames.shape[-1]
    rho = frames + second(frames)
    areas = area(frames)
    perimeter = np.sum(phi*rho, axis=-1)*dx
    # First Fourier modes translate the curve and do not change its shape.
    theta = np.arange(frames.shape[-1])*dx
    centered = frames.copy()
    for mode in [np.cos(theta), np.sin(theta)]:
        centered -= 2*np.mean(frames*mode, axis=-1)[..., None]*mode
    r = np.sqrt(areas/area(phi))
    errors = np.sqrt(np.mean((centered-r[..., None]*phi)**2, axis=-1))
    return {'area':areas, 'perimeter':perimeter, 'shape_error':errors, 'rho':rho}


def render(theta, frames, phi, m, times, report):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    bg='#0d1523';fg='#e8edf7';gold='#f5cd75';cyan='#6bd7dc'
    plt.rcParams.update({'figure.facecolor':bg,'axes.facecolor':bg,'text.color':fg,
        'axes.labelcolor':fg,'xtick.color':fg,'ytick.color':fg,'axes.edgecolor':'#586778'})
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.7), layout='constrained')
    modes=np.fft.fftfreq(len(theta), 1/len(theta))
    def curve(h):
        dh=np.fft.ifft(1j*modes*np.fft.fft(h)).real
        return h*np.cos(theta)-dh*np.sin(theta), h*np.sin(theta)+dh*np.cos(theta)
    for index in [0, len(frames)//8, len(frames)//3, len(frames)-1]:
        x,y=curve(frames[index,0]);axs[0].plot(x,y,alpha=.8,lw=1.4,label=f't={times[index]:.2f}')
    r=math.sqrt(float(area(frames[-1,0])/area(phi)))
    x,y=curve(r*phi);axs[0].plot(x,y,color=gold,ls=':',lw=2,label='Wulff target')
    axs[0].set(aspect='equal',title='A directional shape from the sextic');axs[0].legend(fontsize=8)
    for j in range(frames.shape[1]):
        axs[1].semilogy(times,m['shape_error'][:,j],color=cyan,alpha=.45)
        axs[2].plot(times,m['perimeter'][:,j],color=gold,alpha=.45)
    axs[1].set(xlabel='Time',ylabel='Support-function RMS error',title='Eight initial curves approach Wulff shapes')
    axs[2].set(xlabel='Time',ylabel='Anisotropic perimeter',title='Area constrained; perimeter decreases')
    fig.suptitle('The holdout sextic, interpreted as anisotropy',fontsize=20)
    fig.text(.02,-.055,'Seeded real-plane probe of F; elliptic surface energy constructed from its angular signal.\nConvex smooth-flow discretization with area projection; an experiment inspired by Kim–Kwon, not a Hodge certificate.',fontsize=9,color=fg)
    fig.savefig(OUT/'anisotropic-flow.png',dpi=160,bbox_inches='tight');plt.close(fig)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cpu',action='store_true')
    args=parser.parse_args();OUT.mkdir(parents=True,exist_ok=True)
    cp=handles=None
    if not args.cpu:cp,handles=algebra.load_cupy()
    histories=[];levels=[]
    for n,dt in [(64,.0002),(128,.00005)]:
        theta,plane,angular,phi,a,h,eps,exact=setup(n)
        steps=round(1/dt);stride=steps//100
        if args.cpu:frames,projection=evolve_cpu(h,phi,dt,steps,stride)
        else:frames,projection=evolve_gpu(cp,h,phi,dt,steps,stride)
        m=metrics(frames,phi)
        assert m['rho'].min()>0 and np.max(np.diff(m['perimeter'],axis=0))<1e-10
        drift=float(np.max(np.abs(m['area']/m['area'][0]-1)))
        assert drift<1e-12
        levels.append({'nodes':n,'dt':dt,'steps':steps,'area_relative_drift_after_projection':drift,
                       'max_single_step_area_drift_before_projection':projection,
                       'minimum_curvature_radius':float(m['rho'].min()),
                       'initial_shape_error':m['shape_error'][0].tolist(),
                       'final_shape_error':m['shape_error'][-1].tolist(),
                       'perimeter_decreased':True})
        histories.append(frames)
    # The grids share angles and initial data; compare the final support functions.
    discrepancy=float(np.max(np.abs(histories[0][-1]-histories[1][-1,:,::2])))
    assert discrepancy<.002
    cpu_short,_=evolve_cpu(h,phi,.00005,20,20)
    if not args.cpu:
        gpu_short,_=evolve_gpu(cp,h,phi,.00005,20,20)
        cpu_gpu_error=float(np.max(np.abs(cpu_short-gpu_short)))
        assert cpu_gpu_error<1e-12
    else:cpu_gpu_error=None
    target=ROOT/'sources/sextics/data/holdout/instance.rec'
    report={'paper':'https://arxiv.org/abs/2405.08296v1','seed':SEED,
        'target_sha256':algebra.source_sha256(target),
        'input_hash_encoding':'Source bytes with CRLF normalized to LF.',
        'plane_columns':plane.tolist(),'surface_energy_epsilon':eps,
        'minimum_continuum_stiffness':float(exact.min()),'refinement':levels,
        'final_support_grid_discrepancy':discrepancy,'short_cpu_gpu_max_error':cpu_gpu_error,
        'backend':'NumPy CPU' if args.cpu else cp.cuda.runtime.getDeviceProperties(0)['name'].decode(),
        'construction':'g=(F(U*(cos(theta),sin(theta)))-mean)/max_abs_centered; phi=1+epsilon*g; epsilon=.35/sum_k(abs((1-k^2)*g_hat_k)). The Fourier triangle inequality gives phi+phi_second>=.65. Euclidean mobility.',
        'equation':'h_t=-(phi+phi_second)/(h+h_second)+lambda; lambda=integral(phi+phi_second)/integral(h+h_second).',
        'discretization':'Periodic central differences, forward Euler, per-step rescaling to restore discrete area. The rescaling is a numerical correction, not part of the continuum equation.',
        'scope':'A chosen real-plane probe uses F but not q or A. It is not canonical, does not encode the complex Hodge target, and cannot certify a solve. Only convex smooth curves are represented; no merging or topology changes, and no general flat-flow theorem is verified.'}
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    times=np.linspace(0,1,len(frames))
    np.savez_compressed(OUT/'flow.npz',theta=theta,plane=plane,angular=angular,phi=phi,
                        frames=frames,times=times,area=m['area'],perimeter=m['perimeter'],shape_error=m['shape_error'])
    render(theta,frames,phi,m,times,report)
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O; verification assertions are required.')
    main()

"""Curvature-mediated coefficient response for the actual holdout plane probe.

The finite two-term Hodge complex is built from a response map. It is not
identified with the geometric cohomology of the complex sextic hypersurface.
"""
from pathlib import Path
import argparse, json, math
import numpy as np
from scipy.optimize import brentq, newton
import anisotropic_flow as flow
import gpu_identity_screen as algebra

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'results/response-hodge'


class Probe:
    def __init__(self):
        self.target=algebra.load_target(ROOT/'sources/sextics/data/holdout')
        _,self.plane,*_=flow.setup(64)
        self.exponents=sorted(self.target['F'])
        self.a=np.array([float(self.target['F'][e]) for e in self.exponents])
        t=np.arange(64)*2*np.pi/64
        z=self.plane@np.array([np.cos(t),np.sin(t)])
        raw=np.array([np.prod(z**np.array(e)[:,None],axis=0) for e in self.exponents]).T
        frequencies=np.fft.fftfreq(64,1/64)
        mask=np.abs(frequencies)<=6
        self.k=frequencies[mask]
        self.coefficients=np.fft.fft(raw,axis=0)[mask]/64

    def features(self,t,derivative=0):
        t=np.asarray(t)
        phases=np.exp(1j*t[...,None]*self.k)
        return (phases@((1j*self.k[:,None])**derivative*self.coefficients)).real

    def critical_points(self):
        grid=np.linspace(0,np.pi,2049)
        values=self.features(grid,1)@self.a
        roots=[]
        for x,y,fx,fy in zip(grid[:-1],grid[1:],values[:-1],values[1:]):
            if fx*fy<0:
                root=brentq(lambda t:float(self.features(t,1)@self.a),x,y,xtol=1e-14)
                if not roots or abs(root-roots[-1])>1e-10:roots.append(root)
        assert len(roots)>=2 and len(roots)%2==0
        return roots

    def observable(self,t):
        z=self.plane@np.array([np.cos(t),np.sin(t)])
        A=sum(float(c)*np.prod(z**np.array(e)[:,None],axis=0) for e,c in self.target['A'].items())
        F=self.features(t)@self.a
        assert F.min()>0
        return A/F**(self.target['q']+1)


def thermal(features,a,T,xp=np):
    psi=xp.asarray(features);weights=xp.exp((xp.sum(psi*xp.asarray(a),axis=1)-float(np.max(features@a)))/T)
    weights/=xp.sum(weights)
    mean=xp.sum(weights[:,None]*psi,axis=0)
    centered=psi-mean
    Q=xp.sum(weights[:,None,None]*centered[:,:,None]*centered[:,None,:],axis=0)/T
    return Q,weights,centered


def run(cpu=False):
    probe=Probe();roots=probe.critical_points()
    maxima=[t for t in roots if float(probe.features(t,2)@probe.a)<0]
    maxima.sort(key=lambda t:float(probe.features(t)@probe.a),reverse=True)
    c=maxima[0];K=-float(probe.features(c,2)@probe.a);L=probe.features(c,1)
    gap=float((probe.features(c)-probe.features(maxima[1]))@probe.a) if len(maxima)>1 else None
    assert K>0 and (gap is None or gap>1e-6)
    W=L[None,:]/math.sqrt(K);Q=W.T@W
    D=np.block([[np.zeros((8,8)),W.T],[W,np.zeros((1,1))]])
    squared=np.block([[Q,np.zeros((8,1))],[np.zeros((1,8)),W@W.T]])
    assert np.max(abs(D@D-squared))<1e-14
    eigen,u=np.linalg.eigh(Q);v=W@u[:,-1]/math.sqrt(eigen[-1])
    assert np.max(abs((W@W.T)@v-eigen[-1]*v))<1e-14
    # Compare the analytic envelope Hessian and critical-point derivative to
    # independent local re-optimization at perturbed coefficients.
    rng=np.random.default_rng(202610162231);checks=[]
    for _ in range(8):
        direction=rng.normal(size=8);direction/=np.linalg.norm(direction);step=1e-4
        centers=[];values=[]
        for sign in [-1,1]:
            a=probe.a+sign*step*direction
            root=newton(lambda t:float(probe.features(t,1)@a),c,
                        fprime=lambda t:float(probe.features(t,2)@a),tol=1e-13)
            assert abs(root-c)<.01
            centers.append(root);values.append(float(probe.features(root)@a))
        estimated=(values[0]-2*float(probe.features(c)@probe.a)+values[1])/step**2
        expected=float(direction@Q@direction)
        motion=(centers[1]-centers[0])/(2*step)
        assert abs(estimated-expected)<1e-7
        half=step/2
        fine=[newton(lambda t:float(probe.features(t,1)@(probe.a+s*half*direction)),c,
                     fprime=lambda t:float(probe.features(t,2)@(probe.a+s*half*direction)),tol=1e-13)
              for s in [-1,1]]
        fine_motion=(fine[1]-fine[0])/(2*half)
        motion_error=abs(motion-float(L@direction/K))
        fine_error=abs(fine_motion-float(L@direction/K))
        assert fine_error<1e-8
        assert fine_error<.4*motion_error+1e-11
        checks.append({'envelope_second_difference':estimated,'predicted_curvature_response':expected,
                       'critical_motion_error':motion_error,'refined_critical_motion_error':fine_error})
    cp=handles=None
    if not cpu:cp,handles=algebra.load_cupy()
    xp=np if cpu else cp
    n=16384;t=np.arange(n)*np.pi/n;psi=probe.features(t);O=probe.observable(t)
    temperatures=[.05,.02,.01,.005,.002,.001,.0005,.0002,.0001,.00002]
    records=[];Qs=[];weights_saved=[]
    for T in temperatures:
        raw,p,centered=thermal(psi,probe.a,T,xp)
        if not cpu:raw,p,centered=map(cp.asnumpy,(raw,p,centered))
        R=np.sqrt(p/T)[:,None]*centered
        np.testing.assert_allclose(R.T@R,raw,atol=1e-14)
        lambdas,U=np.linalg.eigh(raw)
        pair_error=0.
        for j in np.flatnonzero(lambdas>1e-10*lambdas[-1]):
            V=R@U[:,j]/math.sqrt(lambdas[j])
            pair_error=max(pair_error,float(np.linalg.norm(R@(R.T@V)-lambdas[j]*V)))
        coarse,_,_=thermal(psi[::2],probe.a,T)
        discrepancy=float(np.linalg.norm(coarse-raw)/np.linalg.norm(raw))
        assert discrepancy<1e-9
        records.append({'T':T,'eigenvalues':lambdas.tolist(),
            'relative_error_to_zero_temperature':float(np.linalg.norm(raw-Q)/np.linalg.norm(Q)),
            'paired_positive_spectral_residual':pair_error,'quadrature_relative_discrepancy':discrepancy,
            'target_observable_mean':float(p@O)})
        Qs.append(raw);weights_saved.append(p)
    assert records[-1]['relative_error_to_zero_temperature']<.01
    # At positive temperature the centered feature curve can have more than
    # one independent direction. This is not a change in spatial Betti numbers.
    singular=np.linalg.svd(psi-psi.mean(axis=0),compute_uv=False)
    feature_rank=int(np.sum(singular>1e-10*singular[0]))
    report={'plane_seed':flow.SEED,'coefficient_exponents':[list(e) for e in probe.exponents],
        'baseline_coefficients':probe.a.tolist(),'domain':'RP^1, theta modulo pi; uniform fixed reference measure',
        'critical_points':roots,'maximum_angle':c,'curvature_K':K,'force_L':L.tolist(),
        'next_local_maximum_height_gap':gap,'critical_point_status':'Numerically bracketed simple stationary points; no interval proof of uniqueness.',
        'zero_temperature_Q':Q.tolist(),'zero_temperature_positive_eigenvalue':float(eigen[-1]),
        'zero_temperature_complex_dimensions':{'degree_0':8,'degree_1':1,'H0':7,'H1':0},
        'sampled_centered_feature_rank':feature_rank,'directional_envelope_checks':checks,'thermal':records,
        'observable':'A/F^(q+1) on the unit projective-circle probe; this retains the specified q and A as a diagnostic only.',
        'target_observable_at_maximum':float(probe.observable(np.array([c]))[0]),
        'backend':'NumPy CPU' if cpu else cp.cuda.runtime.getDeviceProperties(0)['name'].decode(),
        'scope':'Finite response complexes constructed from the sextic coefficient family. No identification with the complex hypersurface cohomology, no Hodge filtration, and no algebraic certificate inferred.'}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    np.savez_compressed(OUT/'response.npz',theta=t,features=psi,temperatures=temperatures,
                        thermal_Q=Qs,zero_Q=Q,weights=weights_saved,target_observable=O)
    render(probe,report,t,Qs,Q)
    print(json.dumps({k:v for k,v in report.items() if k not in ['thermal','zero_temperature_Q','directional_envelope_checks']},indent=2))
    print('Lowest-temperature relative error:',records[-1]['relative_error_to_zero_temperature'])
    return report


def render(probe,report,t,Qs,Q):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    bg='#0d1523';fg='#e8edf7';gold='#f5cd75';cyan='#6bd7dc'
    plt.rcParams.update({'figure.facecolor':bg,'axes.facecolor':bg,'text.color':fg,
        'axes.labelcolor':fg,'xtick.color':fg,'ytick.color':fg,'axes.edgecolor':'#586778'})
    fig,axs=plt.subplots(1,3,figsize=(15,4.5),layout='constrained')
    axs[0].plot(t,probe.features(t)@probe.a,color=gold)
    axs[0].axvline(report['maximum_angle'],color=cyan,ls=':')
    axs[0].set(xlabel='Direction on the projective circle',ylabel='F on the chosen plane',title='Coefficient changes move the preferred direction')
    im=axs[1].imshow(Q,cmap='coolwarm',vmin=-np.max(abs(Q)),vmax=np.max(abs(Q)))
    axs[1].set(xlabel='Sextic coefficient',ylabel='Sextic coefficient',title='Curvature response Q = LᵀK⁻¹L')
    fig.colorbar(im,ax=axs[1],shrink=.75)
    temperatures=np.array([r['T'] for r in report['thermal']])
    vals=np.array([r['eigenvalues'] for r in report['thermal']])
    for j in range(2,8):axs[2].loglog(temperatures,np.maximum(vals[:,j],1e-16),lw=1.5,alpha=.8)
    axs[2].axhline(report['zero_temperature_positive_eigenvalue'],color=gold,ls=':',label='rank-one limit')
    axs[2].set(xlabel='Temperature',ylabel='Response eigenvalues',title='Fluctuations localize to one tangent mode')
    axs[2].legend(fontsize=8)
    fig.suptitle('One coefficient family, paired Hodge response operators',fontsize=20)
    fig.text(.02,-.055,'Eight coefficients; a one-dimensional spatial probe. Positive-temperature covariance sees the feature curve; the zero-temperature limit sees its tangent.\nThe constructed response complex is distinct from the sextic hypersurface’s geometric cohomology.',fontsize=9,color=fg)
    fig.savefig(OUT/'response-hodge.png',dpi=160,bbox_inches='tight');plt.close(fig)


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O; verification assertions are required.')
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--cpu',action='store_true')
    run(parser.parse_args().cpu)

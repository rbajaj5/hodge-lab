"""Product-distribution TV proxy for Gaussian models built from response Grams.

Uses Theorem 1.2 of arXiv:2609.21049v1. The scalar proxy is comparable to TV
up to unspecified universal constants; it is not itself an error probability.
"""
from pathlib import Path
import argparse,json,math
import numpy as np
from scipy.optimize import brentq
from scipy.special import roots_hermitenorm
import gpu_identity_screen as algebra

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/'results/gram-discrimination'


def relative_variances(C0,C1):
    d,U=np.linalg.eigh(C0)
    assert d.min()>0
    whitening=U.T/np.sqrt(d)[:,None]
    np.testing.assert_allclose(whitening@C0@whitening.T,np.eye(len(d)),atol=1e-12)
    B=whitening@C1@whitening.T
    values=np.linalg.eigvalsh(B)
    assert values.min()>0
    return values


def scalar_proxy(variances,repeats=1,nodes=128):
    variances=np.asarray(variances)
    if np.max(abs(variances-1))<1e-14:return 0.
    x,w=roots_hermitenorm(nodes);w=w/math.sqrt(2*math.pi)
    # Under M_i=(P_i+Q_i)/2, with P_i=N(0,1), Q_i=N(0,lambda_i).
    scores=[]
    for var in variances:
        def u(x):return np.tanh(.25*np.log(var)+.25*x*x*(1/var-1))
        scores.append((u(x)**2,u(np.sqrt(var)*x)**2))
    def G(t):
        return repeats*sum(math.log(.5*np.sum(w*(np.sqrt(1+p/t**2)+np.sqrt(1+q/t**2)))) for p,q in scores)
    high=1.
    while G(high)>.5:high*=2
    return brentq(lambda t:G(t)-.5,1e-14,high,xtol=1e-13)


def sampled_tv(variances,repeats,rng,xp=np,samples=65536):
    var=np.tile(variances,repeats);c=.5*float(np.log(var).sum())
    v=xp.asarray(var);coefficient=.5*(1/v-1)
    successes=[]
    for law in [0,1]:
        count=0
        for start in range(0,samples,4096):
            z=xp.asarray(rng.normal(size=(min(4096,samples-start),len(var))))
            logratio=c+xp.sum(z*z*(v if law else 1)*coefficient,axis=1)
            count+=int(xp.sum(logratio>=0))
        successes.append(count)
    probabilities=np.array(successes)/samples
    estimate=float(probabilities[0]-probabilities[1])
    se=float(np.sqrt(np.sum(probabilities*(1-probabilities))/samples))
    return {'tv_estimate':estimate,'standard_error':se,
            'approximate_95_percent_interval':[max(0.,estimate-1.96*se),min(1.,estimate+1.96*se)],
            'samples_per_hypothesis':samples,'likelihood_region_counts':successes}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--cpu',action='store_true')
    args=parser.parse_args();cp=handles=None
    if not args.cpu:cp,handles=algebra.load_cupy()
    xp=np if args.cpu else cp
    with np.load(ROOT/'results/response-hodge/response.npz') as saved:
        base=saved['zero_Q'];thermal=saved['thermal_Q'];temperatures=saved['temperatures']
    ridge=.05*np.linalg.eigvalsh(base)[-1];C0=base+ridge*np.eye(8)
    rng=np.random.default_rng(202610162252);rows=[]
    for temperature in [.005,.001,.0002]:
        index=int(np.flatnonzero(np.isclose(temperatures,temperature,rtol=0,atol=1e-12))[0])
        C1=thermal[index]+ridge*np.eye(8);variances=relative_variances(C0,C1)
        for repeats in [1,8]:
            proxy=scalar_proxy(variances,repeats,128)
            history=[{'nodes':128,'root':proxy}]
            for nodes in [256,512,1024]:
                refined=scalar_proxy(variances,repeats,nodes)
                history.append({'nodes':nodes,'root':refined})
                discrepancy=abs(proxy-refined)
                if discrepancy<1e-7:break
                proxy=refined
            assert discrepancy<1e-7
            result=sampled_tv(variances,repeats,rng,xp)
            rows.append({'response_temperature':temperature,'independent_vectors':repeats,
                         'relative_covariance_eigenvalues':variances.tolist(),
                         'scalar_root':refined,'clipped_proxy':min(1.,refined),
                         'quadrature_root_discrepancy':discrepancy,'quadrature_history':history,**result})
    OUT.mkdir(parents=True,exist_ok=True)
    report={'paper':'https://arxiv.org/abs/2609.21049v1','seed':202610162252,
            'gaussian_model':'N(0,Q_zero+ridge I) versus N(0,Q_T+ridge I). Gram interpreted as covariance, not precision.',
            'ridge':ridge,'cases':rows,
            'backend':'NumPy CPU' if args.cpu else cp.cuda.runtime.getDeviceProperties(0)['name'].decode(),
            'scope':'Statistical distinguishability of explicitly regularized Gaussian models. Independence holds after a common whitening/rotation, and across repeated draws. Gram entries are not treated as independent. Proxy is not TV itself or a certified testing threshold; intervals are Monte Carlo normal approximations. This does not verify a polynomial witness.'}
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O; verification assertions are required.')
    main()

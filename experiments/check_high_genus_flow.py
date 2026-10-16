"""CPU reconstruction of the saved GPU covariance and phase-response results."""
import json, hashlib
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import splu
from scipy.sparse.csgraph import connected_components
from high_genus_flow import OUT, CHI, ANISOTROPY, conductances, phase_prediction, phase_statistics
from high_genus_complex import build_incidence

def run():
    data=np.load(OUT/'fields.npz');mesh=np.load(OUT/'surface.npz')
    report=json.loads((OUT/'report.json').read_text());v,f=mesh['vertices'],mesh['faces']
    assert hashlib.sha256((OUT/'surface.npz').read_bytes()).hexdigest()==report['mesh_sha256']
    t=build_incidence(v,f);e=t['edges'];nv,ne=t['nv'],t['ne']
    d0=sparse.coo_matrix((np.tile([-1.,1.],ne),(np.repeat(np.arange(ne),2),e.ravel())),shape=(ne,nv)).tocsr()
    L0=(d0.T@d0).tocsc()
    assert connected_components(L0,directed=False)[0]==1
    assert nv-ne+len(f)==-94
    # Closed vertex links rule out a pinched complex masquerading as a manifold.
    links=[{} for _ in v]
    for triangle in f:
        for i in range(3):
            center,a,b=map(int,[triangle[i],triangle[(i+1)%3],triangle[(i+2)%3]])
            links[center].setdefault(a,[]).append(b);links[center].setdefault(b,[]).append(a)
    for link in links:
        assert all(len(n)==2 for n in link.values());seen=set();todo=[next(iter(link))]
        while todo:
            i=todo.pop()
            if i not in seen:seen.add(i);todo.extend(link[i])
        assert len(seen)==len(link)
    anchors=data['anchors'];base=np.zeros((nv,len(anchors)));base[anchors,np.arange(len(anchors))]=1;base-=1/nv
    probe=base.copy();dt=report['smoothing_dt']
    for _ in range(report['smoothing_steps']):probe-=dt*(L0@probe)
    worst=0.;standardized=[]
    for i,a in enumerate(ANISOTROPY):
        c=conductances(v,e,a);L=(d0.T@sparse.diags(c)@d0).tocsc();lu=splu(L[1:,1:])
        answer=np.zeros_like(probe);answer[1:]=lu.solve(probe[1:]);answer-=answer.mean(axis=0)
        cov=probe.T@answer;cov=(cov+cov.T)/2
        error=np.linalg.norm(cov-data['covariances'][i])/np.linalg.norm(cov);worst=max(worst,float(error));assert error<1e-8
        prediction,_=phase_prediction(cov,data['stiffness'])
        np.testing.assert_allclose(prediction,data['prediction'][i],rtol=1e-8,atol=1e-10)
        for j,k in enumerate(data['stiffness']):
            m2=abs(np.exp(1j*data['anchor_samples'][i]/(CHI*np.sqrt(k))).mean(axis=0))**2
            np.testing.assert_allclose([m2.mean(),m2.std(ddof=1)/np.sqrt(m2.size)],
                                      [data['mc_mean'][i,j],data['mc_se'][i,j]],rtol=1e-10,atol=1e-13)
        standardized.append(float(np.max(abs(data['mc_mean'][i]-prediction)/data['mc_se'][i])))
        stats=phase_statistics(cov)
        np.testing.assert_allclose(stats['response_peak_stiffness'],report['experiments'][i]['phase_response']['response_peak_stiffness'],rtol=1e-7)
    h=data['harmonic']
    assert np.linalg.norm(d0.T@h)<1e-7
    assert np.linalg.norm((h[t['face_edges']]*t['face_signs']).sum(axis=1))<1e-7
    result={'connected_closed_orientable_manifold_checked':True,'genus':48,
        'all_three_covariances_rebuilt_on_CPU':True,'max_relative_covariance_error':worst,
        'all_303_saved_means_and_standard_errors_recomputed':True,
        'max_absolute_sample_discrepancy_in_pointwise_SE_by_weight':standardized,
        'note':'Pointwise Monte Carlo diagnostics, not simultaneous confidence intervals or a transition test.'}
    print(json.dumps(result,indent=2))
    return result

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O')
    run()

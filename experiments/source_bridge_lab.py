"""Small, reproducible Hodge experiments using the supplied repositories.

Run from the workspace: python experiments/source_bridge_lab.py
Sources are read from pinned Git submodules under sources/.
"""
from pathlib import Path
from itertools import combinations, combinations_with_replacement, permutations
from collections import Counter
from dataclasses import asdict
import json, math, sys, subprocess, time
import numpy as np
from scipy.optimize import linear_sum_assignment
import gpu_identity_screen as gpu

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
OUT=HERE.parent/'results/source-bridges'
OUT.mkdir(parents=True,exist_ok=True)
for repo in ['kemeny-dp-posets','ginibre-braid-dynamics-conjectures','sports-betting-assurance','four-color-proof-program']:
    sys.path.insert(0,str(ROOT/'sources'/repo/'src'))
from kemeny_dp.core import RankingSpace, KemenyAnalyzer
from kemeny_dp.subset_dp import exact_kemeny_stability_subset_dp
from betguard.conditioning import analyze_design_matrix
import braid_stats
import fractional_field_four_color as four

def ranking_experiment():
    m=4;space=RankingSpace.create(m);analyzer=KemenyAnalyzer(space)
    edges=list(combinations(range(m),2))
    B=np.zeros((len(edges),m),dtype=np.int64)
    for e,(i,j) in enumerate(edges):B[e,i]=1;B[e,j]=-1
    signs=[]
    for r in space.rankings:
        pos={v:i for i,v in enumerate(r)}
        signs.append([1 if pos[i]<pos[j] else -1 for i,j in edges])
    signs=np.array(signs)
    counts=Counter();example=None
    for ids in combinations_with_replacement(range(24),3):
        ballots=tuple(space.rankings[i] for i in ids)
        profile=space.profile_from_ballots(ballots)
        best,optima=analyzer.optimum(profile)
        y=signs[list(ids)].sum(axis=0)
        score_num=B.T@y
        exact_num=B@score_num;cycle_num=m*y-exact_num
        assert np.all(B.T@cycle_num==0) and int(exact_num@cycle_num)==0
        assert int(exact_num@exact_num+cycle_num@cycle_num)==m*m*int(y@y)
        order=tuple(sorted(range(m),key=lambda i:(-int(score_num[i]),i)))
        excess=analyzer.score(profile,order)-best
        counts['profiles']+=1;counts['unique_kemeny']+=len(optima)==1
        counts['hodge_order_is_kemeny']+=excess==0
        counts['strict_hodge_scores']+=len(set(score_num))==m
        counts['strict_hodge_but_suboptimal']+=(len(set(score_num))==m and excess>0)
        if len(optima)==1 and len(set(score_num))==m and excess>0 and example is None:
            cert=exact_kemeny_stability_subset_dp(ballots)
            assert cert.solution.optimum_cost==best and cert.solution.selected_ranking==optima[0]
            example={'ballots':[space.ranking_label(r) for r in ballots],
                     'hodge_ranking':space.ranking_label(order),'kemeny_ranking':space.ranking_label(optima[0]),
                     'hodge_cost':best+excess,'kemeny_cost':best,'score_numerators':score_num.tolist(),'score_denominator':m,
                     'edges':edges,'pairwise_margins':y.tolist(),'gradient_numerators':exact_num.tolist(),
                     'cyclic_numerators':cycle_num.tolist(),'component_denominator':m,
                     'cyclic_energy_fraction':float(cycle_num@cycle_num/(m*m*(y@y))),
                     'stability_certificate':asdict(cert)}
    return {'counts':dict(counts),'example':example,
            'scope':'All 2600 unlabeled-voter multisets of three full rankings on four labeled candidates. Hodge least squares uses equal pair weights, with lexicographic score ties. With all triangles filled the harmonic component is zero; cyclic remainder is coexact. This is HodgeRank, not a Hodge-conjecture proof.'}

def fwht(x,xp):
    y=x.copy();n=y.shape[-1];h=1
    while h<n:
        z=y.reshape(*y.shape[:-1],-1,2*h)
        a=z[...,:h].copy();b=z[...,h:].copy()
        z[...,:h]=a+b;z[...,h:]=a-b;h*=2
    return y/math.sqrt(n)

def cube_experiment(cp,rng):
    d=10;n=2**d;batch=2048;mass2=.5
    degrees=np.array([i.bit_count() for i in range(n)])
    lambdas=2*degrees+mass2
    noise=rng.normal(size=(batch,n))
    modes=cp.asarray(noise)/cp.sqrt(cp.asarray(lambdas))
    field=fwht(modes,cp)
    reconstructed=fwht(field,cp)
    error=float(cp.max(cp.abs(reconstructed-modes)))
    assert error<1e-12
    cpu=fwht(noise[:2]/np.sqrt(lambdas),np)
    assert np.max(np.abs(cp.asnumpy(field[:2])-cpu))<1e-12
    energy=cp.asnumpy(cp.sum(reconstructed**2*cp.asarray(lambdas),axis=1))
    z=(float(energy.mean())-n)/math.sqrt(2*n/batch)
    empirical=cp.asnumpy(cp.mean(reconstructed**2,axis=0))
    levels=[{'degree':k,'multiplicity':math.comb(d,k),'theoretical_variance':1/(2*k+mass2),
             'empirical_variance':float(empirical[degrees==k].mean())} for k in range(d+1)]
    np.savez_compressed(OUT/'cube-fields.npz',fields=cp.asnumpy(field[:8]),lambdas=lambdas)
    return {'dimension':d,'vertices':n,'samples':batch,'mass_squared':mass2,'precision_eigenvalues':'2*|S|+mass_squared',
            'mean_precision_energy':float(energy.mean()),'theoretical_mean_energy':n,'mean_energy_z_score':z,
            'inverse_transform_max_error':error,'levels':levels,
            'scope':'Real massive GFF on the Boolean cube graph, counting-measure covariance (L+0.5I)^-1. Walsh transform and filtering on CUDA; seeded Gaussian draws on CPU. Monte Carlo agreement is a finite diagnostic.'}

def spectral_loop(cp,rng):
    n=12;amp=.9
    G=(rng.normal(size=(3,n,n))+1j*rng.normal(size=(3,n,n)))/math.sqrt(2*n)
    def run(steps):
        t=np.linspace(0,1,steps+1)
        gc=cp.asarray(G);tc=cp.asarray(t)
        matrices=cp.asnumpy((gc[0]+amp*cp.cos(2*cp.pi*tc)[:,None,None]*gc[1]+amp*cp.sin(2*cp.pi*tc)[:,None,None]*gc[2])/math.sqrt(1+amp**2))
        matrices[-1]=matrices[0]
        vals,vecs=np.linalg.eig(matrices)
        path=np.empty_like(vals);path[0]=vals[0,np.lexsort((vals[0].imag,vals[0].real))]
        maxratio=0.
        for k in range(1,len(t)):
            rows,cols=linear_sum_assignment(abs(path[k-1,:,None]-vals[k,None,:])**2)
            path[k]=vals[k,cols]
            diff=abs(path[k-1,:,None]-path[k-1,None,:]);np.fill_diagonal(diff,np.inf)
            ratio=np.max(abs(path[k]-path[k-1]))/np.min(diff)
            maxratio=max(maxratio,float(ratio))
        pairs=np.array(list(combinations(range(n),2)))
        z=cp.asarray(path);diff=z[:,pairs[:,0]]-z[:,pairs[:,1]]
        increments=cp.angle(diff[1:]/diff[:-1])
        phase=cp.concatenate((cp.zeros(1),cp.cumsum(2*cp.sum(increments,axis=1))))/(2*cp.pi)
        winding=float(phase[-1]);minsep=float(cp.min(cp.abs(diff)))
        assert abs(winding-round(winding))<1e-9
        finalperm=linear_sum_assignment(abs(path[-1,:,None]-path[0,None,:]))[1]
        # A projection-free, permutation-invariant winding check using normalized discriminants.
        unit_disc=cp.prod((diff/cp.abs(diff))**2,axis=1)
        independent=float(cp.sum(cp.angle(unit_disc[1:]/unit_disc[:-1]))/(2*cp.pi))
        maxdiscstep=float(cp.max(cp.abs(2*cp.sum(increments,axis=1))))
        residuals=np.linalg.norm(matrices@vecs-vecs*vals[:,None,:],axis=(1,2))/np.linalg.norm(matrices,axis=(1,2))
        cond=np.linalg.cond(vecs)
        worst=int(np.argmax(cond));V=vecs[worst]
        realified=np.block([[V.real,-V.imag],[V.imag,V.real]])
        assurance=analyze_design_matrix(realified,standardize=False,condition_limit=1000)
        assert abs(assurance.condition_number/cond[worst]-1)<1e-10
        return {'steps':steps,'winding':winding,'direct_discriminant_winding':independent,
                'min_sampled_gap':minsep,'max_step_over_previous_gap':maxratio,'max_discriminant_phase_step':maxdiscstep,
                'max_eigenpair_relative_residual':float(residuals.max()),'max_eigenvector_condition_number':float(cond.max()),
                'endpoint_permutation':finalperm.tolist(),'conditioning_report':assurance.to_dict()},path,cp.asnumpy(phase),cond
    coarse,_,_,_=run(1024)
    history=[coarse];sampling_resolved=False
    for steps in [2048,4096,8192,16384]:
        fine,path,phase,cond=run(steps)
        previous=history[-1];history.append(fine)
        stable=round(previous['winding'])==round(fine['winding']) and previous['endpoint_permutation']==fine['endpoint_permutation']
        sampling_resolved=stable and fine['max_step_over_previous_gap']<.25 and fine['max_discriminant_phase_step']<math.pi/2
        print('Ginibre refinement',steps,'gap ratio',fine['max_step_over_previous_gap'],'winding',fine['winding'],'stable',stable,flush=True)
        if sampling_resolved:break
    assert sampling_resolved, 'Sampled path unresolved at budget; do not claim reliable winding.'
    assert abs(fine['direct_discriminant_winding']-fine['winding'])<1e-9
    # Conditioning negative control: almost parallel eigenvectors with tiny residual.
    V=np.array([[1.,1.],[0.,1e-10]])
    A=V@np.diag([1.,2.])@np.linalg.inv(V)
    bad=analyze_design_matrix(V,standardize=False,condition_limit=1000)
    bad_residual=float(np.linalg.norm(A@V-V@np.diag([1.,2.])))
    assert bad_residual<1e-12 and not bad.accepted
    np.savez_compressed(OUT/'ginibre-loop.npz',matrices_basis=G,path=path,discriminant_turns=phase,condition=cond)
    words=[(1,1,2,2),(2,2,1,1)]
    winds=[braid_stats.pure_pair_winding_vector(w) for w in words]
    burau=[braid_stats.reduced_burau_minus_one(w) for w in words]
    assert winds[0]==winds[1] and burau[0]!=burau[1]
    signatures=[braid_stats.truncated_pair_log_signature(braid_stats.artin_word_point_path(w,steps_per_letter=256)) for w in words]
    distance=braid_stats.signature_level_two_distance(signatures[0][1],signatures[1][1])
    assert abs(distance-math.sqrt(2))<1e-10
    return {'size':n,'amplitude':amp,'coarse':coarse,'fine':fine,'refinement_history':history,'sampling_resolved':sampling_resolved,'conditioning_negative_control':{'residual':bad_residual,'report':bad.to_dict()},
            'order_sensitive_fixture':{'words':words,'pair_windings':winds,'burau_matrices':burau,'level_two_distance':distance},
            'model':'G(t)=(G0+0.9*cos(2*pi*t)*G1+0.9*sin(2*pi*t)*G2)/sqrt(1+0.9^2), independent normalized complex Ginibre Gi. Every fixed-time marginal is Ginibre; paths are smooth and periodic, not Brownian or OU.',
            'scope':'CUDA loop construction and pair/discriminant phases; CPU eigensolvers, assignment, and conditioning. Agreement under doubling and small sampled steps are numerical evidence, not an interval-certified noncollision theorem. Discriminant winding sees only the braid exponent sum.'}

def field_meshes(cp,rng):
    resolution=16;noise=cp.asarray(rng.normal(size=(resolution,resolution)))
    f=cp.fft.fftfreq(resolution)*resolution
    radius=cp.sqrt(f[:,None]**2+f[None,:]**2);radius[0,0]=1
    result=[];saved={}
    for H in [.15,.5,.85]:
        multiplier=radius**(-H-1);multiplier[0,0]=0
        h=cp.fft.ifft2(cp.fft.fft2(noise,norm='ortho')*multiplier,norm='ortho').real
        # Leave amplitudes linear/Gaussian; unlike a sample-wise normalization,
        # this preserves the precisely declared Gaussian law.
        window=cp.pad(h,((0,1),(0,1)),mode='wrap')
        diag=cp.asnumpy(window[:-1,:-1]+window[1:,1:]-window[1:,:-1]-window[:-1,1:]>=0)
        adj=four.compactified_triangulation_adjacency(diag)
        colors=four.dsatur_coloring(adj)
        assert four.coloring_is_proper(adj,colors)
        V=len(adj);E=sum(map(len,adj))//2;F=2*V-4
        assert V-E+F==2
        odd=sum(len(a)%2 for a in adj)
        result.append({'H':H,'vertices':V,'edges':E,'faces':F,'euler_characteristic':2,
                       'odd_degree_vertices':odd,'colors_used':len(set(colors)),'proper_coloring_verified':True,
                       'surface_harmonic_one_form_dimension':0,'graph_cycle_rank':E-V+1})
        saved['field_'+str(H)]=cp.asnumpy(window);saved['diagonals_'+str(H)]=diag;saved['colors_'+str(H)]=np.array(colors)
    np.savez_compressed(OUT/'fractional-field-meshes.npz',**saved)
    return {'models':result,'scope':'CuPy port of the repository spectral filter; three H values share the same Gaussian noise. No per-sample variance normalization. The boundary is capped by one exterior vertex, not glued into a torus. These are triangulated spheres: surface b1=0 despite many graph cycles. Exact edge checks certify each produced coloring; this is not continuum imaginary geometry.'}

def main():
    start=time.perf_counter();cp,handles=gpu.load_cupy()
    rng=np.random.default_rng(202610162006)
    report={'seed':202610162006,'ranking':ranking_experiment(),'cube_gff':cube_experiment(cp,rng),
            'ginibre':spectral_loop(cp,rng),'fractional_meshes':field_meshes(cp,rng)}
    repos=['a183068-supercongruence','kemeny-dp-posets','ginibre-braid-dynamics-conjectures','sports-betting-assurance','qrcert','hypercube-probabilistic-estimates','four-color-proof-program']
    report['source_commits']={name:subprocess.check_output(['git','-C',str(ROOT/'sources'/name),'rev-parse','HEAD'],text=True).strip() for name in repos}
    report['gpu']=cp.cuda.runtime.getDeviceProperties(0)['name'].decode();report['seconds']=time.perf_counter()-start
    (OUT/'report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({'ranking':report['ranking'],'cube_energy_z':report['cube_gff']['mean_energy_z_score'],
                      'ginibre':report['ginibre'],'meshes':report['fractional_meshes'],'seconds':report['seconds']},indent=2))

if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O; verification assertions are required.')
    main()

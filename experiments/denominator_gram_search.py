"""Compare geometric Gram rankings with the holdout's complete fixed-D E2 problem.

This is a finite ranking experiment, not a search over all degree-six D. The
geometric ranks are fixed before any E2 residual is computed. Exact rational
dual certificates check the union of the selected denominator directions.
"""
from pathlib import Path
from fractions import Fraction as Q
import argparse, copy, hashlib, json, sys, time
import numpy as np
from scipy import sparse
from scipy.sparse.linalg import lsmr
from scipy.stats import spearmanr

ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'algebra'))
import fixed_denominator_search as exact
import gpu_identity_screen as gpu

OUT=ROOT/'results/denominator-gram'
SEED=202610170108
# A sampling restriction informed by the individual-square reductions already
# reported upstream. Completeness of this restriction is NOT needed or claimed
# by this experiment; exact checks below use the unreduced 108+315 model.
OMITTED=[27,56,61,70,81,84,85,86,87,89,91,92,93,94,95,100,101,102,106,107]
SUPPORTS=(2,4)
PER_SUPPORT=384
SELECT_PER_SUPPORT=8
PLANES=24
ANGLES=128
TEMPERATURE_FRACTION=.2


def basis_data():
    bundle=json.loads((ROOT/'algebra/degree6_e1_basis.json').read_text())
    monomials=sorted({tuple(e) for p in bundle['basis'][:108] for c,e in p['D']}
                     |{tuple(e) for c,e in bundle['F']})
    lookup={e:i for i,e in enumerate(monomials)}
    C=np.zeros((len(monomials),108));F=np.zeros(len(monomials));heights=[]
    for j,p in enumerate(bundle['basis'][:108]):
        for c,e in p['D']:C[lookup[tuple(e)],j]=float(Q(c))
        heights.append(sum(abs(Q(c)) for c,e in p['D']))
    for c,e in bundle['F']:F[lookup[tuple(e)]]=float(Q(c))
    # Choose the minimum monomial-coefficient norm representative of D modulo F.
    Cbar=C-np.outer(F,F@C/(F@F))
    assert np.linalg.matrix_rank(Cbar)==108
    return np.asarray(monomials),Cbar,F,heights


def candidates(heights,seed=SEED):
    rng=np.random.default_rng(seed);active=np.array([i for i in range(108) if i not in OMITTED])
    result=[];seen=set()
    for support in SUPPORTS:
        count=0
        while count<PER_SUPPORT:
            indices=sorted(rng.choice(active,support,replace=False).tolist())
            weights=rng.choice([-3,-2,-1,1,2,3],support)
            a={i:Q(int(w))/heights[i] for i,w in zip(indices,weights)}
            lead=a[indices[0]];a={i:c/lead for i,c in a.items()}
            key=tuple(a.items())
            if key in seen:continue
            seen.add(key);result.append(a);count+=1
    return result


def covariance(features,weights,xp=np):
    psi=xp.asarray(features);p=xp.asarray(weights)
    centered=psi-xp.sum(p[:,None]*psi,axis=0)
    return xp.sum(p[:,None,None]*centered[:,:,None]*centered[:,None,:],axis=0)


def gram_matrices(monomials,Cbar,F,seed,xp=np):
    rng=np.random.default_rng(seed);thermal=np.zeros((108,108));uniform=thermal.copy()
    cpu_error=0.;ranges=[]
    theta=np.arange(ANGLES)*np.pi/ANGLES
    for index in range(PLANES):
        plane=np.linalg.qr(rng.normal(size=(6,2)))[0]
        points=(plane@np.array([np.cos(theta),np.sin(theta)])).T
        mon=np.prod(points[:,None,:]**monomials[None,:,:],axis=2)
        psi=mon@Cbar;H=mon@F;T=TEMPERATURE_FRACTION*np.ptp(H)
        assert T>0
        p=np.exp((H-H.max())/T);p/=p.sum();u=np.full(ANGLES,1/ANGLES)
        G=covariance(psi,p,xp)/T;U=covariance(psi,u,xp)/T
        if xp is not np:G,U=xp.asnumpy(G),xp.asnumpy(U)
        if index==0:
            cpu_error=float(np.max(np.abs(G-covariance(psi,p)/T)))
            assert cpu_error<1e-12*max(1,float(np.max(abs(G))))
        thermal+=G/PLANES;uniform+=U/PLANES;ranges.append(float(np.ptp(H)))
    return thermal,uniform,{'plane_seed':seed,'F_ranges':ranges,'first_plane_cpu_gpu_max_error':cpu_error}


def unit_coefficients(pool,Cbar):
    a=np.zeros((len(pool),108))
    for k,row in enumerate(pool):
        for i,c in row.items():a[k,i]=float(c)
    a/=np.linalg.norm(a@Cbar.T,axis=1)[:,None]
    return a


def quadratic_scores(a,G,xp=np):
    v=xp.asarray(a);matrix=xp.asarray(G)
    result=xp.sum(v*xp.sum(matrix[None,:,:]*v[:,None,:],axis=2),axis=1)
    return result if xp is np else xp.asnumpy(result)


class NumericalE2:
    def __init__(self,model):
        entries=np.asarray(model['entries']);r,c=entries[:,:2].astype(int).T
        v=entries[:,2]/entries[:,3];off=model['az_column_offset'];mask=c<off
        aa=np.asarray(model['aa_columns']);self.rows=model['quotient_rows']
        self.ar=r[mask];self.av=v[mask];self.ai,self.aj=aa[c[mask]].T
        self.br=r[~mask];self.bv=v[~mask]
        self.bi,self.bj=divmod(c[~mask]-off,315)

    def specialize(self,a):
        b=np.bincount(self.ar,weights=self.av*a[self.ai]*a[self.aj],minlength=self.rows)
        weights=self.bv*a[self.bi];nz=weights!=0
        M=sparse.coo_matrix((weights[nz],(self.br[nz],self.bj[nz])),shape=(self.rows,315)).tocsr()
        M.eliminate_zeros()
        return b,M

    def residual(self,a):
        b,M=self.specialize(a)
        scales=np.sqrt(np.asarray(M.power(2).sum(axis=0)).ravel());active=scales>0
        scaled=M[:,active].multiply(1/scales[active]).tocsr()
        solution=lsmr(scaled,-b,atol=1e-12,btol=1e-12,conlim=1e12,maxiter=2500)
        r=b+scaled@solution[0]
        kkt=float(np.linalg.norm(scaled.T@r)/max(np.linalg.norm(b),1e-30))
        if solution[1]==7 or kkt>1e-8:
            raise RuntimeError(f'Least squares not converged: stop={solution[1]}, KKT={kkt}')
        return {'E2_residual':float(np.linalg.norm(r)),
                'relative_to_b':float(np.linalg.norm(r)/np.linalg.norm(b)),
                'b_norm':float(np.linalg.norm(b)), 'scaled_normal_equation_residual':kkt,
                'lsmr_stop':int(solution[1]),'lsmr_iterations':int(solution[2])}


def select(score):
    ids=[]
    for offset in range(0,PER_SUPPORT*len(SUPPORTS),PER_SUPPORT):
        ids.extend((offset+np.argsort(score[offset:offset+PER_SUPPORT],kind='stable')[:SELECT_PER_SUPPORT]).tolist())
    return ids


def selection_summary(ids,residual):
    v=residual[ids]
    return {'ids':ids,'mean_E2_residual':float(v.mean()),'median_E2_residual':float(np.median(v)),
            'minimum_E2_residual':float(v.min()),'maximum_E2_residual':float(v.max())}


def check_pool(report,model):
    pool=candidates(basis_data()[3],report['seed']);records=report['candidates']
    assert len(pool)==len(records)==PER_SUPPORT*len(SUPPORTS)
    for a,r in zip(pool,records):
        assert [[i,str(c)] for i,c in a.items()]==r['denominator_coordinates']
    residual=np.array([r['E2_residual'] for r in records])
    for method,key in [('anisotropic','anisotropic_score'),('uniform','uniform_score'),('algebra_reference','E2_residual')]:
        assert select(np.array([r[key] for r in records]))==report['selections'][method]['ids']
    for method,selection in report['selections'].items():
        assert selection_summary(selection['ids'],residual)==selection
    assert select(np.random.default_rng(report['seed']+3).random(len(pool)))==report['selections']['random']['ids']
    selected=set().union(*(set(r['ids']) for r in report['selections'].values()))
    assert selected=={r['candidate_id'] for r in report['exact_checks']}
    for row in report['exact_checks']:
        assert row['denominator_coordinates']==records[row['candidate_id']]['denominator_coordinates']
        exact.check(model,row)
    rejected=next(r for r in report['exact_checks'] if r['status']=='rejected')
    broken=copy.deepcopy(rejected)
    broken['dual_functional']=[[i,str(2*Q(c))] for i,c in broken['dual_functional']]
    try:exact.check(model,broken)
    except AssertionError:pass
    else:raise AssertionError('Corrupted dual certificate accepted.')
    return len(selected),len(pool)


def check_report():
    report=json.loads((OUT/'report.json').read_text());model=exact.load_model()
    assert report['model_sha256']==hashlib.sha256((ROOT/'algebra/degree6_full_e2_model.json.gz').read_bytes()).hexdigest()
    assert report['basis_sha256']==hashlib.sha256((ROOT/'algebra/degree6_e1_basis.json').read_bytes()).hexdigest()
    counts=np.sum([check_pool(r,model) for r in [report,*report['replications']]],axis=0)
    print(json.dumps({'exact_candidates_replayed':int(counts[0]),'seeded_candidates_replayed':int(counts[1]),
                      'corrupted_certificates_rejected':True}),flush=True)


def evaluate_pool(seed,heights,Cbar,G,U,Gtest,Utest,model,xp=np):
    pool=candidates(heights,seed);a=unit_coefficients(pool,Cbar)
    g=quadratic_scores(a,G,xp);u=quadratic_scores(a,U,xp)
    gt=quadratic_scores(a,Gtest,xp);ut=quadratic_scores(a,Utest,xp)
    np.testing.assert_allclose(g,quadratic_scores(a,G),rtol=1e-11,atol=1e-18)
    rng=np.random.default_rng(seed+3)
    # These three choices are made before looking at any algebraic residual.
    ids={'anisotropic':select(g),'uniform':select(u),'random':select(rng.random(len(pool)))}
    print('Built denominator Grams and froze three selections.',flush=True)
    numerical=NumericalE2(model);records=[]
    for i,denom in enumerate(pool):
        row=numerical.residual(a[i]);row.update(candidate_id=i,support=len(denom),
            denominator_coordinates=[[j,str(c)] for j,c in denom.items()],
            anisotropic_score=float(g[i]),uniform_score=float(u[i]),
            fresh_plane_anisotropic_score=float(gt[i]),fresh_plane_uniform_score=float(ut[i]))
        records.append(row)
        if (i+1)%384==0:print('Seed',seed,'numerical full E2 fits:',i+1,flush=True)
    residual=np.array([r['E2_residual'] for r in records])
    # An expensive reference which has inspected all residuals, NOT a fair
    # geometric predictor. Its exact checks reveal whether small means zero.
    ids['algebra_reference']=select(residual)
    selections={name:selection_summary(which,residual) for name,which in ids.items()}
    random_means=[]
    for _ in range(2000):
        chosen=np.concatenate([off+rng.choice(PER_SUPPORT,SELECT_PER_SUPPORT,replace=False)
                               for off in range(0,len(pool),PER_SUPPORT)])
        random_means.append(float(residual[chosen].mean()))
    statistics=[]
    for k,support in enumerate(SUPPORTS):
        sl=slice(k*PER_SUPPORT,(k+1)*PER_SUPPORT)
        statistics.append({'support':support,
            'anisotropic_vs_E2_spearman':float(spearmanr(g[sl],residual[sl]).statistic),
            'uniform_vs_E2_spearman':float(spearmanr(u[sl],residual[sl]).statistic),
            'anisotropic_fresh_planes_spearman':float(spearmanr(g[sl],gt[sl]).statistic),
            'uniform_fresh_planes_spearman':float(spearmanr(u[sl],ut[sl]).statistic)})
    checks=[]
    for i in sorted(set().union(*map(set,ids.values()))):
        b,columns=exact.specialize(model,pool[i]);row=exact.solve(b,columns)
        row.update(candidate_id=i,denominator_coordinates=records[i]['denominator_coordinates'])
        if row['status']=='rejected':
            raw=np.zeros(108)
            for j,c in pool[i].items():raw[j]=float(c)
            dual_norm=np.linalg.norm([float(Q(c)) for j,c in row['dual_functional']])
            bound=1/(np.linalg.norm(Cbar@raw)**2*dual_norm)
            # Cauchy-Schwarz: L(M)=0 implies ||b+Mz|| >= |L(b)|/||L||.
            assert records[i]['E2_residual']>=bound*(1-1e-9)
            row['float_lower_bound_from_exact_dual']=float(bound)
        exact.check(model,row);checks.append(row)
        if len(checks)%16==0:print('Seed',seed,'exact candidates:',len(checks),flush=True)
    return {'seed':seed,'correlations':statistics,'selections':selections,'candidates':records,'exact_checks':checks,
        'random_selection_mean_distribution':{'draws':2000,'mean':float(np.mean(random_means)),
            'central_90_percent_interval':np.quantile(random_means,[.05,.95]).tolist()},
        'exact_rejected':sum(r['status']=='rejected' for r in checks),
        'exact_solvable':sum(r['status']=='solvable' for r in checks)}


def run(cpu=False):
    start=time.perf_counter();monomials,Cbar,F,heights=basis_data();cp=handles=None
    if not cpu:cp,handles=gpu.load_cupy()
    xp=np if cpu else cp
    G,U,geometry=gram_matrices(monomials,Cbar,F,SEED+1,xp)
    Gtest,Utest,geometry_test=gram_matrices(monomials,Cbar,F,SEED+2,xp)
    model=exact.load_model()
    main=evaluate_pool(SEED,heights,Cbar,G,U,Gtest,Utest,model,xp)
    # Replication added after the primary result was observed. All four fixed
    # new seeds are reported; the geometric matrices and ranking rule are held
    # fixed, with no tuning against these new algebraic outcomes.
    replications=[evaluate_pool(SEED+100+k,heights,Cbar,G,U,Gtest,Utest,model,xp) for k in range(4)]
    report={**main,'experiment':'Denominator Gram ranking, fixed finite pools',
        'seed':SEED,'model_sha256':hashlib.sha256((ROOT/'algebra/degree6_full_e2_model.json.gz').read_bytes()).hexdigest(),
        'basis_sha256':hashlib.sha256((ROOT/'algebra/degree6_e1_basis.json').read_bytes()).hexdigest(),
        'candidate_recipe':{'per_support':PER_SUPPORT,'supports':list(SUPPORTS),'omitted_coordinates':OMITTED,
            'weights':'Independent choices from +-1,+-2,+-3 divided by exact basis L1 coefficient height; projectively normalize first nonzero coordinate to 1.',
            'restriction_scope':'Sampling restriction only. Completeness not required for fixed-candidate checks.'},
        'geometry':{'planes':PLANES,'angles':ANGLES,'temperature_fraction_of_plane_F_range':TEMPERATURE_FRACTION,
            'formula':'G=mean_planes Cov_softmax(F/T)(Dbar_i,Dbar_j)/T; uniform control changes only angular weights.',
            'normalization':'Dbar is the coefficient-orthogonal projection of D away from F; score=a^T G a / ||Dbar||_coeff^2.',
            'main':geometry,'fresh_planes':geometry_test,
            'anisotropic_eigenvalues':np.linalg.eigvalsh(G).tolist(),
            'uniform_eigenvalues':np.linalg.eigvalsh(U).tolist()},
        'algebra_metric':'min_z ||b(a)+M(a)z||_2 over all 315 corrections, with ||Dbar||_coeff=1; ordinary monomial-coefficient norm in the fixed remainder modulo F. Numerical surrogate, not distance to the solution set.',
        'selection_rule':'Lowest score, 8 from each support stratum. Geometry and random selections frozen before E2. Algebra reference uses all E2 results.',
        'replications':replications,
        'replication_protocol':'After seeing the primary result, run four fresh fixed candidate seeds with unchanged Gram matrices, support sizes, weights, temperature and selection rule. Report all seeds. Not a preregistered significance test.',
        'backend':'NumPy CPU' if cpu else cp.cuda.runtime.getDeviceProperties(0)['name'].decode(),
        'work_split':'GPU weighted covariance and quadratic scoring; CPU polynomial feature evaluation, sparse least squares, and exact rational certificates.',
        'seconds':time.perf_counter()-start,
        'scope':'Fixed real rational candidates, two support sizes, one temperature, one set of training planes and five candidate seeds. No complex search, global degree-six exclusion, or Hodge certificate inferred. Gram energy is a heuristic; the E2 norm is a coordinate-dependent numerical surrogate. Exact dual checks exclude only their fixed candidates and scalar multiples.'}
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    np.savez_compressed(OUT/'grams.npz',anisotropic=G,uniform=U,fresh_anisotropic=Gtest,
                        fresh_uniform=Utest,denominator_coefficient_matrix=Cbar)
    render(report);check_report()
    print(json.dumps({'pools':[{'seed':r['seed'],'mean_residuals':{k:v['mean_E2_residual'] for k,v in r['selections'].items()},
        'random_distribution':r['random_selection_mean_distribution'],'exact_rejected':r['exact_rejected'],'exact_solvable':r['exact_solvable']}
        for r in [report,*replications]],'seconds':report['seconds']},indent=2),flush=True)


def render(report):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.style.use('dark_background');fig,axes=plt.subplots(2,2,figsize=(13,8.4),constrained_layout=True)
    fig.patch.set_facecolor('#111820');colors={'anisotropic':'#efc75e','uniform':'#56a9eb','random':'#9baaba','algebra_reference':'#81d3ac'}
    rows=report['candidates'];r=np.array([x['E2_residual'] for x in rows]);g=np.array([x['anisotropic_score'] for x in rows])
    for k,support in enumerate(SUPPORTS):
        sl=slice(k*PER_SUPPORT,(k+1)*PER_SUPPORT)
        axes[0,0].scatter(g[sl],r[sl],s=12,alpha=.45,label=f'{support} basis directions')
    axes[0,0].set(xscale='log',yscale='log',xlabel='Anisotropic Gram score (lower selected)',ylabel='Full E2 least-squares residual',title='Does geometric stability predict algebraic fit?')
    axes[0,0].legend(fontsize=9)
    names=list(report['selections']);pools=[report,*report['replications']]
    for name in names:
        means=[pool['selections'][name]['mean_E2_residual'] for pool in pools]
        axes[0,1].plot(range(1,6),means,'o-',color=colors[name],label=name.replace('_',' '))
    intervals=np.array([pool['random_selection_mean_distribution']['central_90_percent_interval'] for pool in pools])
    axes[0,1].fill_between(range(1,6),intervals[:,0],intervals[:,1],color='white',alpha=.10,label='Random sets: central 90%')
    axes[0,1].set(xlabel='Candidate pool (1 primary, 2–5 fresh)',xticks=range(1,6),ylabel='Mean E2 residual of 16 picks',title='Fixed geometric ranking, five candidate pools')
    axes[0,1].legend(fontsize=8,ncol=2)
    for name in names:
        values=np.sort(r[report['selections'][name]['ids']])
        axes[1,0].plot(np.arange(1,len(values)+1),values,'o-',color=colors[name],label=name.replace('_',' '),markersize=3)
    axes[1,0].set(yscale='log',xlabel='Ordered shortlist position (primary pool)',ylabel='Full E2 residual',title='Algebra reference inspects all 768 fits per pool')
    axes[1,0].legend(fontsize=8)
    axes[1,1].axis('off')
    unique={tuple(map(tuple,row['denominator_coordinates'])):row['status'] for pool in pools for row in pool['exact_checks']}
    rejected=sum(status=='rejected' for status in unique.values())
    text=f"5 pools × {len(rows)} rational candidates\n{PLANES} random projective-circle probes\n108 denominator coordinates / 315 corrections\n\n{len(unique)} distinct shortlisted directions checked exactly\n{rejected} rejected by rational dual certificates\n{len(unique)-rejected} solved the fixed-denominator E2 equations\n\nSmall numerical residual is not an exact identity.\nGeometry ranks; exact algebra decides feasibility."
    axes[1,1].text(.03,.93,text,va='top',fontsize=11.5,linespacing=1.6,color='#d7e2ec')
    fig.suptitle('From anisotropic Gram matrices to denominator candidates',fontsize=18)
    fig.savefig(OUT/'denominator-ranking.png',dpi=160);plt.close(fig)


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O: exact verification needs assertions.')
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--cpu',action='store_true');parser.add_argument('--check',action='store_true')
    args=parser.parse_args()
    if args.check:check_report()
    else:run(args.cpu)

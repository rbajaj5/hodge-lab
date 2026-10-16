"""Plot the actual coefficient heat flow for one searched denominator."""
from pathlib import Path
import gzip, json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.linalg import svd
import hodge_projected_search as search

OUT=search.OUT

def run():
    report=json.loads((OUT/'report.json').read_text());data,pairs=search.e1.load()
    fields,_=search.e1.koszul_fields()
    best=min(report['records'],key=lambda r:r['metrics']['coefficient']['residual'])
    b,cols=search.fixed_system(best['spec'],pairs,fields)
    rows=sorted(set(b).union(*(set(c) for c in cols)));lookup={m:i for i,m in enumerate(rows)}
    rhs=np.zeros(len(rows));M=np.zeros((len(rows),840))
    for m,c in b.items():rhs[lookup[m]]=float(c)
    for j,col in enumerate(cols):
        for m,c in col.items():M[lookup[m],j]=float(c)
    scales=np.linalg.norm(M,axis=0);T=M[:,scales>0]/scales[scales>0]
    U,s,V=svd(T,full_matrices=False,lapack_driver='gesdd')
    keep=s>max(T.shape)*np.finfo(float).eps*s[0]
    with gzip.open(OUT/'certificates.json.gz','rt') as f:packet=json.load(f)
    exact=next(c for c in packet['cases'] if c['candidate_id']==best['candidate_id'])
    assert int(keep.sum())==exact['correction_matrix_rank']
    # Null singular directions belong to the cokernel, just like omitted rows.
    coeff=U[:,keep].T@rhs;r=rhs-U[:,keep]@coeff
    plateau=float(r@r/(rhs@rhs));times=np.r_[0,np.logspace(-3,5,240)]
    energy=(r@r+np.exp(-2*times[:,None]*s[keep][None,:]**2)@(coeff**2))/(rhs@rhs)
    reference=best['metrics']['coefficient']['fraction_of_initial_energy']
    assert abs(plateau-reference)<1e-8
    check={'candidate_id':best['candidate_id'],'singular_value_rank':int(keep.sum()),
           'exact_correction_rank':exact['correction_matrix_rank'],
           'heat_plateau_energy_fraction':plateau,'sparse_projection_energy_fraction':reference,
           'agreement':abs(plateau-reference),'time_operator':'column-normalized full correction matrix T; e(t)=exp(-t*T*T^T)b',
           'scope':'A coefficient-space two-term Hodge analogy. No claim that r is a differential form on the surface.'}
    (OUT/'heat-check.json').write_text(json.dumps(check,indent=2)+'\n',encoding='utf-8')
    plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False})
    fig,axs=plt.subplots(1,2,figsize=(12.8,4.8),layout='constrained')
    ax=axs[0];ax.semilogx(times[1:],energy[1:],color='#277e8e',lw=2.5,label='Remaining residual energy')
    ax.axhline(plateau,color='#ba4a73',ls='--',label=f'Unremovable component: {100*plateau:.1f}%')
    ax.set(xlabel='Coefficient heat time (chosen units)',ylabel='Fraction of initial squared residual',ylim=(0,1.03),
           title=f'Heat flow stalls: candidate {best["candidate_id"]}')
    ax.legend(loc='upper right',frameon=False)
    ax=axs[1]
    for j,metric in enumerate(['coefficient','bombieri']):
        fractions=[r['metrics'][metric]['fraction_of_initial_energy'] for r in report['records']]
        ax.hist(fractions,bins=np.linspace(0,1,31),histtype='step',lw=2,
                label='Coefficient norm' if j==0 else 'Bombieri-weighted remainder norm')
    ax.set(xlabel='Unremovable fraction of initial squared residual',ylabel='Number of candidate directions',
           title='600 three-character candidates')
    ax.legend(frameon=False,fontsize=9)
    fig.suptitle('Hodge-inspired correction projection · 34 exact checks, 34 rejections',fontsize=15)
    fig.savefig(OUT/'projection-search.png',dpi=180);plt.close(fig)
    print(json.dumps(check),flush=True)

if __name__=='__main__':run()

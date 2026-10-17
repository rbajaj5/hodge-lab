"""Checked score comparison, rebuild history, and actual Koszul differentials."""
from itertools import combinations,combinations_with_replacement
from fractions import Fraction as Q
import argparse,json
import homology_guided_triples as h


def data():
    report=json.loads((h.OUT/'validation.json').read_text());assert report['status']=='PASS'
    other=json.loads((h.OUT/'independent-validation.json').read_text())
    assert report['families']==other['families'] and report['checks']==other['checks']
    plan=json.loads((h.OUT/'ranking-plan.json').read_text());rows=[]
    for r in plan['all_profiles']:
        n=r['number'];p=h.q.load(h.OUT/f'profile-{n:03d}.json.gz')
        f=next(f for f in report['families'] if f['batch_number']==n)
        scores={tuple(b['character']):b['homology'][1]['homology'][1] if b['homology'] else 0 for b in p['blocks']}
        parts=[scores[tuple(f['third_character'])],scores[(1,2,3)],scores[(5,3,0)]]
        assert sum(parts)==r['score']==f['score']
        group='high' if n in report['comparison']['high']['families'] else 'control' if n in report['comparison']['low_control']['families'] else 'later'
        rows.append({'number':n,'parts':parts,'group':group,'initial':len(f['basis_indices']),
            'after_squares':len(f['baseline_remaining']),'final':len(f['remaining']),
            'excluded':f['excluded'],'seconds':f['attempt']['seconds'],
            'empty_blocks':[b['character'] for b in p['blocks'] if not b['equation_indices']]})
    # Reconstruct d1 and d2 directly from the defining exterior differential.
    # Compare dimensions, ranks and representatives against the checked packet.
    p=h.q.load(h.OUT/'profile-019.json.gz');b=next(b for b in p['blocks'] if b['character']==[0,4,3])
    stage=h.q.load(h.OUT/'baseline-019.json.gz')['stages'][-1]
    eq=[h.cert.decode(stage['necessary'][j]['polynomial']) for j in b['equation_indices']]
    ids=b['ids'];bases=[[(I,m) for I in combinations(range(len(eq)),k)
        for m in combinations_with_replacement(ids,4-2*k)] for k in range(3)]
    maps=[]
    for k in [1,2]:
        index={v:i for i,v in enumerate(bases[k-1])};cols=[]
        for I,m in bases[k]:
            c={}
            for j,g in enumerate(I):
                for mon,value in eq[g].items():
                    at=index[(I[:j]+I[j+1:],tuple(sorted(m+mon)))];c[at]=c.get(at,Q(0))+(-1)**j*value
            cols.append({i:v for i,v in c.items() if v})
        maps.append(cols)
    for c in maps[1]:assert not h.kh.apply(maps[0],c)
    result=h.kh.complex_at(eq,ids,4);assert result==b['homology'][1]
    assert [len(b) for b in bases]==result['dimensions'][:3]
    assert [len(h.kh.image(c).rows) for c in maps]==result['differential_ranks'][:2]
    representative={i:Q(c) for i,c in result['h1_representatives'][0]}
    assert not h.kh.apply(maps[0],representative)
    assert h.kh.image(maps[1]).reduce(representative)  # It is not a boundary.
    r100=next(f for f in report['families'] if f['batch_number']==100)
    history=[{'before':len(c['before']),'after_blocks':len(c['after_blocks']),
        'charts':c['charts'],'after':len(c['after'])} for c in r100['cycles']]
    assert [(c['before'],c['after']) for c in history]==[(13,12),(12,11),(11,11)]
    assert history[0]['charts']==[{'raw':6,'excluded':False},{'raw':211,'excluded':True}]
    assert history[1]['charts']==[{'raw':6,'excluded':True}]
    assert report['excluded']==132 and report['baseline_excluded']==117
    assert all(r['excluded']==4 for r in report['comparison'].values())
    return {'excluded':report['excluded'],'baseline_excluded':report['baseline_excluded'],
        'selected_union':416+report['excluded'],'comparison':report['comparison'],'families':rows,
        'H100_history':history,'H19_complex':{'dimensions':[len(b) for b in bases],
            'ranks':result['differential_ranks'][:2],'homology':result['homology'][:3],
            'kernel_d1':result['kernel_d1'],'boundaries':result['boundaries_d2'],
            'maps':[[[[i,str(c)] for i,c in sorted(col.items())] for col in cols] for cols in maps],
            'representative':result['h1_representatives'][0]},
        'hashes':{p.name:h.digest(p) for p in sorted(h.OUT.glob('*.json.gz'))}}


def save(fig,name,plt):
    fig.savefig(h.OUT/(name+'.png'),dpi=180)
    fig.savefig(h.OUT/(name+'.svg'),metadata={'Date':None});plt.close(fig)
    p=h.OUT/(name+'.svg');p.write_text('\n'.join(l.rstrip() for l in p.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')


def figures(d):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.colors import ListedColormap,BoundaryNorm
    import numpy as np
    plt.rcParams.update({'font.size':11,'svg.fonttype':'none','svg.hashsalt':'homology-guided-triples'})
    colors=['#326f9d','#c07b38','#805488'];rows=d['families']
    fig,axes=plt.subplots(1,2,figsize=(13,7),layout='constrained',gridspec_kw={'width_ratios':[1.25,1]})
    ax=axes[0];left=[0]*len(rows)
    for k,label in enumerate(['Added character','Y0 anchor','Y1 anchor']):
        values=[r['parts'][k] for r in rows];ax.barh(range(len(rows)),values,left=left,color=colors[k],label=label)
        left=[x+y for x,y in zip(left,values)]
    ax.set(yticks=range(len(rows)),yticklabels=[f"H{r['number']}  [{r['group']}]" for r in rows],
        xlabel='Degree-four H1 dimension, summed across blocks',title='Homology selected an order; it did not predict a winner',xlim=(0,66))
    for j,n in enumerate(left):ax.text(n+.7,j,str(n),va='center',fontsize=9)
    ax.invert_yaxis();ax.legend(loc='lower right',frameon=False);ax.spines[['top','right']].set_visible(False)
    ax=axes[1]
    ax.bar(['High H1','Low H1\ncontrol'],[4,4],color=[colors[0],colors[1]],width=.55)
    for i in range(2):ax.text(i,4.1,'4 / 4 excluded',ha='center')
    ax.set(ylim=(0,6.4),yticks=range(5),ylabel='Families excluded in the prospective comparison',title='The same follow-up method worked in both groups')
    ax.text(.5,5.5,'Then all seven unselected survivors also closed.\nNo demonstrated ranking advantage.',ha='center',va='center',fontsize=11)
    ax.text(.5,.31,'117 close with squares\n+ 15 with blocks / shared charts / rebuilding\n= 132 new exclusions',transform=ax.transAxes,ha='center',va='center',fontsize=11,
        bbox={'facecolor':'white','alpha':.95,'edgecolor':'#dddddd','pad':9})
    ax.spines[['top','right']].set_visible(False)
    fig.suptitle('Homology-guided search: useful exclusions, an unconfirmed priority heuristic',fontsize=15)
    fig.supxlabel('H IDs refer to this new Y0/Y1 batch. Empty blocks contribute zero to the score. Small, nonrandomized comparison; holdout remains unsolved.',fontsize=10)
    save(fig,'homology-guided-triples',plt)

    fig,axes=plt.subplots(1,3,figsize=(14,5.5),layout='constrained',gridspec_kw={'width_ratios':[1.6,.8,1.1]})
    c=d['H19_complex'];cmap=ListedColormap(['#286b9b','#fbfbf7','#b87827']);norm=BoundaryNorm([-1.5,-.5,.5,1.5],3)
    for k,ax in enumerate(axes[:2]):
        matrix=np.zeros((c['dimensions'][k],c['dimensions'][k+1]))
        for j,col in enumerate(c['maps'][k]):
            for i,v in col:matrix[i,j]=1 if Q(v)>0 else -1
        ax.imshow(matrix,cmap=cmap,norm=norm,aspect='auto',interpolation='nearest')
        ax.set(title=f"d{k+1}: {matrix.shape[0]} rows × {matrix.shape[1]} columns\nexact rank {c['ranks'][k]}",xlabel=f'K{k+1} basis index',ylabel=f'K{k} basis index')
    ax=axes[2];ax.axis('off')
    ax.text(0,.98,'H19 added-character block',weight='bold',fontsize=12,va='top')
    ax.text(0,.88,'Six quadratics in four variables\nTotal degree four',linespacing=1.6,va='top')
    ax.text(0,.65,'K2 (15) → K1 (60) → K0 (35)\n\nd1 d2 = 0 exactly\n\n25 cycles − 15 boundaries\n= 10 homology classes',linespacing=1.5,va='top')
    ax.text(0,.23,'Blue: negative   Gold: positive\nWhite: zero; magnitude hidden\nPatterns depend on basis order.',fontsize=10,linespacing=1.6,va='top')
    fig.suptitle('The actual Koszul maps behind one part of the ranking',fontsize=15)
    fig.supxlabel('H19 score 60 = 10 from this block + 50 from its Y0 block. These relations are not new physical constraints or a holdout solution.',fontsize=10)
    save(fig,'koszul-maps-H19',plt)

    fig,ax=plt.subplots(figsize=(11,4),layout='constrained');ax.axis('off')
    labels=['13 coefficients\ninitial rebuild','a211 = 0\nchart contradicted','12 coefficients\nrebuild equations','a6 = 0\nchart now contradicted','11 coefficients\nknown pair proof']
    for i,label in enumerate(labels):
        x=.1+i*.2;ax.text(x,.62,label,transform=ax.transAxes,ha='center',va='center',fontsize=11,
            bbox={'boxstyle':'round,pad=.7','facecolor':'#edf2f6' if i%2==0 else '#f8eddf','edgecolor':'#a3a3a3'})
        if i<4:ax.annotate('',xy=(x+.115,.62),xytext=(x+.085,.62),xycoords='axes fraction',arrowprops={'arrowstyle':'->','color':'#777777'},zorder=3)
    ax.text(.1,.22,'a6 = 1 chart\ninitially unresolved',transform=ax.transAxes,ha='center',color='#a34859',fontsize=11)
    ax.annotate('',xy=(.7,.39),xytext=(.19,.17),xycoords='axes fraction',arrowprops={'arrowstyle':'->','connectionstyle':'arc3,rad=.12','linestyle':'--','color':'#a34859'})
    fig.suptitle('H100: keep a failed chart, then rebuild after a verified vanishing',fontsize=14)
    fig.supxlabel('One numerator correction is shared throughout each system. A failed bounded chart search was not counted as an exclusion.',fontsize=10)
    save(fig,'rebuild-H100',plt)


def run(check=False):
    d=data();p=h.OUT/'visual-data.json'
    if check:assert json.loads(p.read_text())==d
    else:p.write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8');figures(d)
    receipt={'status':'PASS','families':len(d['families']),'excluded':d['excluded'],
        'H19_dimensions':d['H19_complex']['dimensions'],'H19_zero_compositions':len(d['H19_complex']['maps'][1]),
        'nonboundary_representative_checked':True,'source_hashes':d['hashes']}
    (h.OUT/'figure-validation.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
    print('PASS: score composition, outcomes, rebuild history, exact differentials, nonboundary class, and packet hashes')


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');run(p.parse_args().check)

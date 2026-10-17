"""Exact basis comparisons prompted by the visible patterns in B19/B49/B100."""
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations_with_replacement as mons
import argparse,hashlib,json
import x1y1_extensions as x
from check_x1y1_extensions import replay_stages
from plot_x1y1_extensions import label
OUT=x.e.ROOT/'results/graded-map-patterns'


def config(n):
    if n==19:
        # a7=u+2t, a119=w+6u, a159=v+3u, a216=t.
        forward={7:{(0,):Q(1),(3,):Q(2)},119:{(2,):Q(1),(0,):Q(6)},159:{(1,):Q(1),(0,):Q(3)},216:{(3,):Q(1)}}
        inverse={0:{(7,):Q(1),(216,):Q(-2)},1:{(159,):Q(1),(7,):Q(-3),(216,):Q(6)},
            2:{(119,):Q(1),(7,):Q(-6),(216,):Q(12)},3:{(216,):Q(1)}}
        weights=[[Q(3),Q(0),Q(-1,12)],[Q(0),Q(0),Q(1,36)],[Q(0),Q(3),Q(1,3)]]
        target=[{(1,1):Q(1)},{(0,1):Q(1)},{(2,2):Q(1),(1,2):Q(-4)}]
        formulas=['v^2','u v','w^2 - 4 v w'];change=['u = a7 - 2 a216','v = a159 - 3 u','w = a119 - 6 u','t = a216']
        geometry='Necessary zero set: v = w = 0; u and t remain free.'
    elif n==49:
        forward={122:{(0,):Q(1,2),(2,):Q(1,6)},138:{(1,):Q(1)},223:{(2,):Q(1)}}
        inverse={0:{(122,):Q(2),(223,):Q(-1,3)},1:{(138,):Q(1)},2:{(223,):Q(1)}}
        weights=[[Q(1)]];target=[{(0,0):Q(1)}];formulas=['u^2'];change=['u = 2 a122 - a223/3','v = a138','w = a223']
        geometry='Necessary zero set: u = 0; the equation retains a square.'
    else:
        assert n==100
        forward={6:{(0,):Q(1),(1,):Q(2)},211:{(1,):Q(1)}}
        inverse={0:{(6,):Q(1),(211,):Q(-2)},1:{(211,):Q(1)}}
        weights=[[Q(-12)]];target=[{(0,0):Q(1),(1,1):Q(1)}];formulas=['u^2 + v^2'];change=['u = a6 - 2 a211','v = a211']
        geometry='Over C: u = i v or u = -i v. Over R: only the origin.'
    return forward,inverse,weights,target,formulas,change,geometry


def mon_label(m,names):
    return ' '.join(names[i]+('^'+str(k) if k>1 else '') for i,k in Counter(m).items()) or '1'


def matrix(eq,ids,degree,names,generators):
    record=x.e.strand(eq,ids,degree);x.e.check_strand(eq,ids,record)
    cols,polys=x.e.mac_map(eq,ids,degree);rows=list(mons(ids,degree));lookup={m:i for i,m in enumerate(rows)}
    cells=[{'row':lookup[m],'column':j,'exact':str(v)} for j,p in enumerate(polys) for m,v in sorted(p.items())]
    return ({k:record[k] for k in ['degree','domain','codomain','rank','kernel','quotient_dimension']} |
        {'rows':[mon_label(m,names) for m in rows],'columns':[generators[j]+' * '+mon_label(m,names) for j,m in cols],
        'cells':cells,'forced_coordinates':[names[p['coordinate']] for p in record['vanishings']]})


def permute(m):
    p=dict(m);rows=sorted(range(m['codomain']),key=lambda i:hashlib.sha256(m['rows'][i].encode()).digest())
    cols=sorted(range(m['domain']),key=lambda i:hashlib.sha256(m['columns'][i].encode()).digest())
    ri={old:new for new,old in enumerate(rows)};ci={old:new for new,old in enumerate(cols)}
    p['rows']=[m['rows'][i] for i in rows];p['columns']=[m['columns'][i] for i in cols]
    p['cells']=[{**r,'row':ri[r['row']],'column':ci[r['column']]} for r in m['cells']]
    assert sorted((p['rows'][c['row']],p['columns'][c['column']],c['exact']) for c in p['cells'])==sorted((m['rows'][c['row']],m['columns'][c['column']],c['exact']) for c in m['cells'])
    return p


def data():
    from check_degree7_triples import IndependentModel
    model=IndependentModel();cases=[];checks=Counter();bindings=[]
    for n in [19,49,100]:
        path=x.OUT/f'family-{n:03d}.json.gz';packet=x.q.load(path)
        _,_,_,counts=replay_stages(model,packet,packet['basis_indices']);checks.update(counts)
        stage=packet['stages'][-1];b=next(b for b in stage['blocks'] if b['character']==packet['third_character'])
        raw=[x.cert.decode(stage['necessary'][j]['polynomial']) for j in b['equation_indices']]
        forward,inverse,weights,target,formulas,change,geometry=config(n)
        assert sorted(forward)==b['active']
        for i,p in forward.items():assert x.cert.substitute(p,inverse)=={(i,):Q(1)}
        for i,p in inverse.items():assert x.cert.substitute(p,forward)=={(i,):Q(1)}
        transformed=[x.cert.substitute(p,forward) for p in raw];adapt=[];rank=x.t.base.Elimination()
        for w in weights:
            p={}
            for c,v in zip(w,transformed):p=x.t.base.padd(p,v,c)
            adapt.append(p);rank.insert({i:c for i,c in enumerate(w) if c})
        assert adapt==target and len(rank.basis)==len(raw)
        maps=[]
        for d in [3,4]:
            old=matrix(raw,b['active'],d,{i:'a'+str(i) for i in b['active']},['P'+str(i) for i in b['equation_indices']])
            new=matrix(adapt,list(range(len(inverse))),d,dict(enumerate(['u','v','w','t'][:len(inverse)])),['R'+str(i) for i in range(len(raw))])
            assert (old['rank'],old['kernel'],old['domain'],old['codomain'])==(new['rank'],new['kernel'],new['domain'],new['codomain'])
            maps.append({'degree':d,'raw':old,'adapted':new,'permuted':permute(old)})
        if n==19:
            # Explicit common-factor syzygy in the original raw variables.
            u=inverse[0];v={ (159,):Q(1) }
            assert not x.t.base.padd(x.cert.product(raw[2],v),x.cert.product(raw[0],u),Q(-108))
            L=inverse[1]
            assert x.cert.product(L,L)==x.t.base.padd({m:3*c for m,c in raw[0].items()},raw[2],Q(-1,12))
        cases.append({'batch_number':n,'pair':'X1/Y1','third_character':packet['third_character'],
            'maps':maps,'change':change,'generators':formulas,'geometry':geometry,
            'generator_transform':[[str(c) for c in w] for w in weights],
            'original_indices':b['equation_indices'],'packet_sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    return {'cases':cases,'checks':dict(checks),'basis_changes_verified':3,
        'scope':'Three already excluded X1/Y1 families. These necessary-block zero sets are not certificate solution sets.'}


def figure(d):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.colors import ListedColormap
    from matplotlib.ticker import MaxNLocator
    cmap=ListedColormap(['#8c62aa','#ffffff','#29866f'])
    fig,axes=plt.subplots(2,3,figsize=(13,9),layout='constrained')
    plt.rcParams.update({'svg.fonttype':'none','svg.hashsalt':'graded-map-patterns'})
    for j,c in enumerate(d['cases']):
        for i,key in enumerate(['raw','adapted']):
            m=c['maps'][1][key];a=axes[i,j];v=np.zeros((m['codomain'],m['domain']))
            for r in m['cells']:v[r['row'],r['column']]=1 if Q(r['exact'])>0 else -1
            a.imshow(v,cmap=cmap,vmin=-1,vmax=1,aspect='auto',interpolation='nearest')
            a.set(title='B'+str(c['batch_number'])+' · '+('original basis' if key=='raw' else ', '.join(c['generators'])),
                xlabel='Equation × monomial column',ylabel='Output monomial row')
            a.xaxis.set_major_locator(MaxNLocator(integer=True));a.yaxis.set_major_locator(MaxNLocator(integer=True))
            a.text(.98,.03,'rank '+str(m['rank'])+'/'+str(m['codomain'])+'; kernel '+str(m['kernel']),transform=a.transAxes,ha='right',bbox={'facecolor':'white','alpha':.88,'edgecolor':'none'})
    fig.suptitle('Degree four: the same graded maps in different bases',fontsize=16)
    fig.supxlabel('Green = positive · purple = negative · white = zero. Exact ranks are unchanged; apparent curves depend on basis and ordering.',fontsize=11)
    fig.savefig(OUT/'graded-map-patterns.png',dpi=170);fig.savefig(OUT/'graded-map-patterns.svg',metadata={'Date':None});plt.close(fig)
    p=OUT/'graded-map-patterns.svg';p.write_text('\n'.join(l.rstrip() for l in p.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')


def run(check=False):
    OUT.mkdir(parents=True,exist_ok=True);d=data();root=x.e.ROOT/'visualizations'
    html=(root/'graded-map-patterns.template.html').read_text(encoding='utf-8').replace('__DATA__',json.dumps(d,separators=(',',':')))
    assert len(html.encode())<1_000_000
    if check:
        assert json.loads((OUT/'data.json').read_text())==d and (root/'graded-map-patterns.html').read_text(encoding='utf-8')==html
    else:
        (OUT/'data.json').write_text(json.dumps(d,indent=2)+'\n');(root/'graded-map-patterns.html').write_text(html,encoding='utf-8');figure(d)
    report={'status':'PASS','basis_changes':3,'graded_maps_checked':12,'ordering_controls_checked':6,'physical_checks':d['checks']}
    (OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');run(p.parse_args().check)

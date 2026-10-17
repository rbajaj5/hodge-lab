"""Build data-linked views of the degree-three necessary-ideal calculation."""
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
import argparse, gzip, hashlib, json
import eisenbud_linear_strand as e

OUT = e.OUT


def mon_label(mon):
    return ' '.join('a[%d]' % k + ('^%d' % n if n > 1 else '') for k, n in sorted(Counter(mon).items())) or '1'


def example(stage, products, label, target):
    equations = [e.t.cert.decode(p['polynomial']) for p in stage['necessary']]
    grouped = {}
    for j, m, c in products: grouped.setdefault(j, []).append([j, m, c])
    polys = {j: e.expand_products(equations, terms) for j, terms in grouped.items()}
    mons = sorted(set().union(*(set(p) for p in polys.values())))
    total = e.expand_products(equations, products)
    assert total == target
    return {'label': label, 'products': products, 'monomials': [mon_label(m) for m in mons],
            'groups': [{'label': 'P%d' % j, 'equation': stage['necessary'][j]['polynomial'],
                        'multipliers': [[m, c] for _, m, c in terms],
                        'values': [str(polys[j].get(m, 0)) for m in mons]}
                       for j, terms in grouped.items()],
            'sums': [str(total.get(m, 0)) for m in mons],
            'defaultMonomial': next((i for i,m in enumerate(mons) if m in target), 0)}


def data():
    with gzip.open(OUT/'certificates.json.gz','rt',encoding='utf-8') as f: packet=json.load(f)
    validation=json.loads((OUT/'validation.json').read_text())
    assert validation['status']=='PASS' and validation['sources']==packet['sources']
    families=[]
    for f in packet['families']:
        stages=[]
        for index,s in enumerate(f['stages']):
            examples=[]; seen=set()
            for strand in s['strands']:
                for p in strand['vanishings']:
                    if p['coordinate'] in seen:continue
                    seen.add(p['coordinate'])
                    target={(p['coordinate'],)*p['power']:Q(1)}
                    examples.append(example(s,p['products'],mon_label(next(iter(target)))+' identity',target))
            linear=s['strands'][1]
            if linear['dependencies']:
                rel=min(linear['dependencies'],key=lambda r:(len(r),r))
                eqs=[e.t.cert.decode(p['polynomial']) for p in s['necessary']]
                labels,_=e.mac_map(eqs,s['active'],3)
                products=[[labels[k][0],list(labels[k][1]),c] for k,c in rel]
                examples.append(example(s,products,'Shortest stored linear syzygy',{}))
            stages.append({'number':index+1,'variables':len(s['active']),'quadratics':len(s['necessary']),
                           'domain':linear['domain'],'rank':linear['rank'],'kernel':linear['kernel'],
                           'codomain':linear['codomain'],'quotient':linear['quotient_dimension'],
                           'removed':s['removed'],'examples':examples})
        families.append({'number':f['number'],'initial':len(f['initial_active']),
                         'remaining':len(f['remaining']),'stages':stages})
    return {'families':families,'packetSha256':hashlib.sha256((OUT/'certificates.json.gz').read_bytes()).hexdigest()}


def figure(d):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    plt.rcParams.update({'font.size':10,'svg.fonttype':'none','svg.hashsalt':'eisenbud-strand'})
    fig,axes=plt.subplots(2,2,figsize=(13,10),gridspec_kw={'height_ratios':[1.3,1]},layout='constrained')
    labels=[str(f['number']) for f in d['families']];x=np.arange(len(labels))
    a=axes[0,0]
    initial=np.array([f['initial'] for f in d['families']]);remaining=np.array([f['remaining'] for f in d['families']])
    a.barh(x,remaining,color='#2b78a6',label='Still active')
    a.barh(x,initial-remaining,left=remaining,color='#e39139',label='Forced zero')
    a.set(yticks=x,yticklabels=labels,ylabel='Selected family',xlabel='Denominator coordinates',
          title='Eleven forced zeros; no additional family closed',xlim=(0,27))
    a.invert_yaxis();a.legend(loc='lower right',frameon=False)
    for i,(r,n) in enumerate(zip(remaining,initial)):a.text(n+.2,i,f'{r}/{n}',va='center',fontsize=8)
    a=axes[0,1]
    first=[f['stages'][0]['kernel'] for f in d['families']];last=[f['stages'][-1]['kernel'] for f in d['families']]
    a.scatter(first,x,label='Initial reduced ideal',s=32,color='#2b78a6')
    a.scatter(last,x,label='After rebuilding',s=30,marker='x',color='#bd4e33')
    for i,(l,r) in enumerate(zip(first,last)):a.plot([l,r],[i,i],color='#999999',linewidth=1,zorder=0)
    a.set(yticks=x,yticklabels=labels,ylabel='Selected family',xlabel='Dimension of linear syzygy space',
          title='Relations among quadratic necessities')
    a.invert_yaxis();a.legend(frameon=False,loc='lower right')
    f=next(f for f in d['families'] if f['number']==6);ex=f['stages'][0]['examples'][0]
    target=ex['defaultMonomial'];cancel=next(i for i,s in enumerate(ex['sums']) if s=='0')
    for a,k in zip(axes[1],[target,cancel]):
        names=[g['label'] for g in ex['groups']]+['Sum']
        values=[float(Q(g['values'][k])) for g in ex['groups']]+[float(Q(ex['sums'][k]))]
        a.barh(names,values,color=['#2b78a6']*(len(names)-1)+['#e39139'])
        a.axvline(0,color='#777777',linewidth=.8)
        a.invert_yaxis();a.set(xlabel='Coefficient in the weighted polynomial sum',ylabel='Equation contribution',
                            title='Family 6: '+ex['monomials'][k])
        a.text(.98,.06,'Exact sum = '+ex['sums'][k],ha='right',transform=a.transAxes)
    fig.suptitle('A finite strand of the necessary ideal — not a full resolution',fontsize=16)
    fig.savefig(OUT/'linear-strand.png',dpi=190)
    fig.savefig(OUT/'linear-strand.svg',metadata={'Date':None})
    plt.close(fig)
    p=OUT/'linear-strand.svg';p.write_text('\n'.join(line.rstrip() for line in p.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')


def build(check=False):
    d=data();json_text=json.dumps(d,separators=(',',':'))
    template=e.ROOT/'visualizations/eisenbud-linear-strand.template.html'
    output=e.ROOT/'visualizations/eisenbud-linear-strand.html'
    text=template.read_text(encoding='utf-8').replace('__DATA__',json_text)
    assert len(text.encode())<1_000_000
    if check:
        assert output.read_text(encoding='utf-8')==text
        assert json.loads((OUT/'visual-data.json').read_text())==d
    else:
        output.write_text(text,encoding='utf-8')
        (OUT/'visual-data.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8')
        figure(d)
    result={'status':'PASS','packetSha256':d['packetSha256'],'families':len(d['families']),
            'stages':sum(len(f['stages']) for f in d['families']),
            'identities_shown':sum(len(s['examples']) for f in d['families'] for s in f['stages']),
            'forced_coordinates':sum(f['initial']-f['remaining'] for f in d['families']),
            'all_displayed_sums_checked_exactly':True,
            'fragmentSha256':hashlib.sha256(text.encode()).hexdigest()}
    (OUT/'figure-validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true')
    build(parser.parse_args().check)

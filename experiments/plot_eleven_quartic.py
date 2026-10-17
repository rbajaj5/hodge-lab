"""Actual-data block ranks and inspectable exact polynomial cancellation."""
from fractions import Fraction as Q
from math import comb
import argparse, hashlib, json
import eleven_quartic as x
from plot_eisenbud_strand import example, mon_label
e=x.e;q=x.q
NAMES={(0,0,0):'trivial',(0,0,1):'X0',(0,1,0):'X1',(1,0,0):'X2',(1,2,3):'Y0',(5,3,0):'Y1'}


def data():
    checked=json.loads((x.OUT/'blocks-validation.json').read_text())
    closure=json.loads((x.OUT/'exclusions-validation.json').read_text())
    assert checked['status']==closure['status']=='PASS'
    packet=q.load(x.OUT/'blocks.json.gz');assert packet['source_sha256']==q.source_sha()
    families=[]
    for number,source in x.source().items():
        stage=source['stages'][-1];blocks=[]
        rows=[b for b in packet['blocks'] if b['number']==number]
        if number in [17,151]:
            rows=rows+[{'active':stage['active'],'equation_indices':list(range(len(stage['necessary']))),
                        'strands':stage['strands']+[q.load(x.OUT/f'full-{number}.json.gz')['quartic']]}]
        for b in rows:
            char=b.get('character');ids=b['active'];index=b['equation_indices']
            eq=[e.t.cert.decode(stage['necessary'][j]['polynomial']) for j in index]
            strands=b['strands'];quartic=strands[-1];examples=[]
            def mapped(products):return [[index[j],m,str(c)] for j,m,c in products]
            for proof in quartic['vanishings']:
                target={(proof['coordinate'],)*4:Q(1)}
                examples.append(example(stage,mapped(proof['products']),mon_label(next(iter(target)))+' identity',target))
            layers=q.syzygy_layers(eq,ids,strands[1],quartic)
            # A genuine Koszul boundary is present even when no power is forced.
            if len(eq)>=2:
                i,j=min(((i,j) for i in range(len(eq)) for j in range(i+1,len(eq))),
                        key=lambda pair:len(eq[pair[0]])+len(eq[pair[1]]))
                products=[[i,m,c] for m,c in eq[j].items()]+[[j,m,-c] for m,c in eq[i].items()]
                examples.append(example(stage,mapped(products),'Koszul boundary of two quadratics',{}))
            if layers['new_representatives']:
                labels,_=e.mac_map(eq,ids,4)
                rel=min((quartic['dependencies'][k] for k in layers['new_representatives']),key=len)
                examples.append(example(stage,mapped([[labels[k][0],labels[k][1],c] for k,c in rel]),
                                        'Relation beyond linear multiples and Koszul boundaries',{}))
            # Exact expansion has already been checked above. The interactive
            # payload needs coefficients only; proof products stay in packets.
            for ex in examples:
                ex.pop('products')
                for group in ex['groups']:
                    group.pop('equation');group.pop('multipliers')
            blocks.append({'name':NAMES[tuple(char)] if char is not None else 'Full necessary ideal',
                'character':char,'variables':len(ids),'quadratics':len(eq),'active':ids,
                'rank':quartic['rank'],'codomain':quartic['codomain'],'kernel':quartic['kernel'],
                'ranks':[r['rank'] for r in strands],'targets':[r['codomain'] for r in strands],
                'linear':layers['linear_multiple_rank'],
                'koszulAdded':layers['linear_plus_koszul_rank']-layers['linear_multiple_rank'],
                'new':layers['new_beyond_linear_and_koszul'],
                'zeros':[p['coordinate'] for p in quartic['vanishings']], 'examples':examples})
        result=next(r for r in closure['families'] if r['number']==number)
        families.append({'number':number,'blocks':blocks,'excluded':result['excluded'],
                         'zeros':result['quartic_zeros'],'remaining':result['remaining_after_quartics']})
    return {'families':families,'sourceSha256':q.source_sha(),
            'packetSha256':hashlib.sha256((x.OUT/'blocks.json.gz').read_bytes()).hexdigest()}


def figure(d):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    plt.rcParams.update({'font.size':10,'svg.fonttype':'none','svg.hashsalt':'eleven-quartic'})
    fig=plt.figure(figsize=(13,10),layout='constrained')
    grid=fig.add_gridspec(2,2,height_ratios=[2,1]);a=fig.add_subplot(grid[0,:])
    names=list(NAMES.values());families=d['families']
    values=np.full((len(families),6),np.nan)
    for i,f in enumerate(families):
        for b in f['blocks']:
            if b['name'] not in names:continue
            j=names.index(b['name']);values[i,j]=b['rank']/b['codomain']
    im=a.imshow(values,cmap='Blues',vmin=0,vmax=1,aspect='auto')
    for i,f in enumerate(families):
        for b in f['blocks']:
            if b['name'] not in names:continue
            j=names.index(b['name']);a.text(j,i,f"{b['rank']}/{b['codomain']}  |  {len(b['zeros'])} zeros",
                ha='center',va='center',color='white' if values[i,j]>.64 else '#17252e',fontsize=10)
    a.set(xticks=range(6),xticklabels=names,yticks=range(len(families)),
          yticklabels=[str(f['number'])+(' — excluded' if f['excluded'] else ' — unresolved') for f in families],
          xlabel='Pure-character block (blank = absent from this family)',ylabel='Selected family',
          title='Quartic image rank / target dimension  |  coordinate fourth powers in the ideal')
    fig.colorbar(im,ax=a,label='Fraction of quartic target reached',shrink=.8)
    a=fig.add_subplot(grid[1,0]);survivors=[f['blocks'][-1] for f in families if not f['excluded']]
    labels=['Family 17','Family 151'];left=np.zeros(2)
    for key,label,color in [('linear','Linear multiples','#2b78a6'),('koszulAdded','Additional Koszul','#d39645'),('new','Further relations','#8e699a')]:
        v=np.array([b[key] for b in survivors]);a.barh(labels,v,left=left,label=label,color=color)
        for y,l,w in zip(labels,left,v):
            if w>=10:a.text(l+w/2,y,str(w),ha='center',va='center')
        left+=v
    a.set(xlabel='Dimension in the full degree-four kernel',title='Relations persist in the two open families')
    a.legend(frameon=False,loc='upper center',bbox_to_anchor=(.5,-.17),ncol=2)
    a=fig.add_subplot(grid[1,1]);a.set_axis_off();a.set_title('What the blocks prove')
    text=('12 blocks fill their quartic target: 60 forced zeros.\n'
          'Family 2 / X0 adds 2 zeros despite rank 65 < 70.\n\n'
          'Replayed residual sectors close 9 complete families.\n'
          'Selected coverage: 141 → 150 of 152.\n\n'
          'Full quartic maps: rank 2161 and 2015 out of 3876.\n'
          'No coordinate fourth power in either surviving ideal.\n'
          'Families 17, 151 and the full holdout remain open.')
    a.text(.02,.9,text,va='top',linespacing=1.6)
    fig.suptitle('Eleven-family continuation: where degree four succeeds and stops',fontsize=16)
    fig.savefig(x.OUT/'eleven-quartic.png',dpi=180)
    fig.savefig(x.OUT/'eleven-quartic.svg',metadata={'Date':None});plt.close(fig)
    p=x.OUT/'eleven-quartic.svg';p.write_text('\n'.join(l.rstrip() for l in p.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')


def build(check=False):
    d=data();template=e.ROOT/'visualizations/eleven-quartic.template.html'
    output=e.ROOT/'visualizations/eleven-quartic.html'
    text=template.read_text(encoding='utf-8').replace('__DATA__',json.dumps(d,separators=(',',':')))
    assert len(text.encode())<1_000_000
    if check:
        assert output.read_text(encoding='utf-8')==text
        assert json.loads((x.OUT/'visual-data.json').read_text())==d
    else:
        output.write_text(text,encoding='utf-8')
        (x.OUT/'visual-data.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8');figure(d)
    result={'status':'PASS','source_sha256':d['sourceSha256'],'packet_sha256':d['packetSha256'],
        'families':len(d['families']),'blocks':sum(len(f['blocks']) for f in d['families']),
        'illustrative_identities':sum(len(b['examples']) for f in d['families'] for b in f['blocks']),
        'all_displayed_sums_checked_exactly':True,'fragment_sha256':hashlib.sha256(text.encode()).hexdigest()}
    (x.OUT/'figure-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');build(p.parse_args().check)

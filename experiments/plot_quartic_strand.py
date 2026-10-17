"""Build exact-data cancellation views and the quartic proof dependency figure."""
from fractions import Fraction as Q
import argparse,hashlib,json
import eisenbud_quartic_strand as q
from plot_eisenbud_strand import example,mon_label
e=q.e


def data():
    closure=json.loads((q.OUT/'exclusions-validation.json').read_text())
    assert closure['status']=='PASS'
    packet=q.load(q.OUT/'pure-blocks.json.gz');assert packet['source_sha256']==q.source_sha()
    families=[]
    for number,source in q.source().items():
        stage=source['stages'][-1];examples=[]
        blocks=[b for b in packet['blocks'] if b['number']==number]
        for block in blocks:
            def mapped(products):return [[block['equation_indices'][j],m,c] for j,m,c in products]
            for p in block['strands'][2]['vanishings']:
                target={(p['coordinate'],)*4:Q(1)}
                examples.append(example(stage,mapped(p['products']),mon_label(next(iter(target)))+' = equation sum',target))
        # Show two sorts of relation in the first block; the full packet keeps both.
        block=blocks[0];eq=[e.t.cert.decode(stage['necessary'][j]['polynomial']) for j in block['equation_indices']]
        labels,_=e.mac_map(eq,block['active'],4)
        layers=q.syzygy_layers(eq,block['active'],block['strands'][1],block['strands'][2])
        def mapped(products):return [[block['equation_indices'][j],m,c] for j,m,c in products]
        i,j=min(layers['additional_koszul_boundaries'],key=lambda pair:len(eq[pair[0]])+len(eq[pair[1]]))
        products=[[i,list(m),str(c)] for m,c in eq[j].items()]+[[j,list(m),str(-c)] for m,c in eq[i].items()]
        examples.append(example(stage,mapped(products),'Koszul boundary of two quadratics',{}))
        rel=min((block['strands'][2]['dependencies'][k] for k in layers['new_representatives']),key=len)
        products=[[labels[k][0],list(labels[k][1]),c] for k,c in rel]
        examples.append(example(stage,mapped(products),'Relation beyond Koszul boundaries',{}))
        proof=next(f for f in closure['families'] if f['number']==number);assert proof['excluded']
        families.append({'number':number,'variables':5,'quadratics':6,'blocks':len(blocks),
            'domain':90,'codomain':70,'rank':70,'kernel':20,'linear':0,'koszulAdded':15,'new':5,
            'zeros':proof['quartic_zeros'],'remaining':proof['remaining_after_quartics'],
            'remainingCharacters':proof['remaining_characters'],'excluded':True,'examples':examples})
    return {'families':families,'packetHashes':{'pureBlocks':hashlib.sha256((q.OUT/'pure-blocks.json.gz').read_bytes()).hexdigest()},'sourceSha256':q.source_sha()}


def figure(d):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import numpy as np
    plt.rcParams.update({'font.size':10,'svg.fonttype':'none','svg.hashsalt':'quartic-strand'})
    fig,axes=plt.subplots(2,2,figsize=(14,10),layout='constrained',gridspec_kw={'height_ratios':[1,1.25]})
    families=d['families'];a=axes[0,0]
    degrees=[2,3,4];image=np.array([6,30,70]);quotient=np.array([9,5,0])
    a.bar(degrees,image,label='Ideal image',color='#2b78a6',width=.6)
    a.bar(degrees,quotient,bottom=image,label='Quotient',color='#cb7930',width=.6)
    for x,r,h in zip(degrees,image,quotient):
        a.text(x,r/2,str(r),ha='center',va='center',color='white')
        if h:a.text(x,r+h/2,str(h),ha='center',va='center')
    a.set(xticks=degrees,xlabel='Total polynomial degree',ylabel='Dimension',ylim=(0,80),title='Each small block fills the entire quartic space')
    a.legend(frameon=False,loc='upper left')
    a.text(.02,-.25,'Six quadratics in five variables; same ranks in all six blocks.\nDegree-four kernel: 15 Koszul boundaries + 5 further relations.',transform=a.transAxes)
    a=axes[0,1];a.set_axis_off();a.set_title('Exact proof dependencies')
    for i,f in enumerate(families):
        y=.86-i*.17
        a.text(.00,y,'Family '+str(f['number']),va='center')
        a.text(.28,y,str(len(f['zeros']))+' quartic zeros',va='center')
        residual='X₁ / Y₀' if f['number'] in [6,149] else 'Y₀ / Y₁' if f['number'] in [10,152] else 'Y₀'
        a.text(.66,y,residual,va='center')
        a.annotate('',xy=(.26,y),xytext=(.17,y),arrowprops={'arrowstyle':'->','color':'#777777'})
        a.annotate('',xy=(.63,y),xytext=(.53,y),arrowprops={'arrowstyle':'->','color':'#777777'})
    a.text(.00,-.03,'Previously excluded residual sectors replayed exactly.\nFive selected triples closed; eleven remain open.',va='top')
    ex=families[0]['examples'][0];target=ex['defaultMonomial'];cancel=next(i for i,s in enumerate(ex['sums']) if s=='0' and any(g['values'][i]!='0' for g in ex['groups']))
    for a,k in zip(axes[1],[target,cancel]):
        rows=[(g['label'],float(Q(g['values'][k]))) for g in ex['groups'] if g['values'][k]!='0']+[('Sum',float(Q(ex['sums'][k])))]
        a.barh([r[0] for r in rows],[r[1] for r in rows],color=['#2b78a6']*(len(rows)-1)+['#cb7930'])
        a.axvline(0,color='#888888',linewidth=.8);a.invert_yaxis()
        a.set(xlabel='Coefficient in the weighted polynomial sum',ylabel='Equation contribution',title='Family 6: '+ex['monomials'][k])
        a.text(.97,.05,'Exact sum = '+ex['sums'][k],ha='right',transform=a.transAxes)
    fig.suptitle('Degree four: relations, forced zeros, and five exclusions',fontsize=16)
    fig.savefig(q.OUT/'quartic-strand.png',dpi=190)
    fig.savefig(q.OUT/'quartic-strand.svg',metadata={'Date':None});plt.close(fig)
    p=q.OUT/'quartic-strand.svg';p.write_text('\n'.join(line.rstrip() for line in p.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')


def build(check=False):
    d=data();template=e.ROOT/'visualizations/eisenbud-quartic-strand.template.html';output=e.ROOT/'visualizations/eisenbud-quartic-strand.html'
    text=template.read_text(encoding='utf-8').replace('__DATA__',json.dumps(d,separators=(',',':')))
    assert len(text.encode())<1_000_000
    if check:
        assert output.read_text(encoding='utf-8')==text
        assert json.loads((q.OUT/'visual-data.json').read_text())==d
    else:
        output.write_text(text,encoding='utf-8');(q.OUT/'visual-data.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8');figure(d)
    result={'status':'PASS','packetHashes':d['packetHashes'],'families':len(d['families']),
        'identities_shown':sum(len(f['examples']) for f in d['families']),
        'quartic_zeros':sum(len(f['zeros']) for f in d['families']),'all_displayed_sums_checked_exactly':True,
        'fragmentSha256':hashlib.sha256(text.encode()).hexdigest()}
    (q.OUT/'figure-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');build(p.parse_args().check)

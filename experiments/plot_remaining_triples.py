"""Show why rebuilding changes one higher-degree search, and where it fails."""
from fractions import Fraction as Q
import argparse,hashlib,json
import remaining_triples_shared as s
from plot_eisenbud_strand import example,mon_label
e=s.e;q=s.q


def data():
    check=json.loads((s.OUT/'validation.json').read_text());assert check['status']=='PASS'
    old=q.load(s.x.OUT/'blocks.json.gz');families=[]
    for number in s.NUMBERS:
        stage=s.x.source()[number]['stages'][-1];rebuilt=q.load(s.OUT/f'rebuilt-{number}.json.gz')
        initial=next(b for b in old['blocks'] if b['number']==number and tuple(b['character']) not in s.RESIDUAL)
        initial={**initial,'strands':initial['strands']+q.load(s.OUT/f'block-{number}.json.gz')['strands']}
        blocks=[]
        for index,(physical,b) in enumerate([(stage,initial),(rebuilt,rebuilt['block'])]):
            indices=b['equation_indices'];eq=[s.cert.decode(physical['necessary'][j]['polynomial']) for j in indices]
            examples=[]
            def mapped(products):return [[indices[j],m,str(c)] for j,m,c in products]
            for proof in sorted(b['strands'][-1]['vanishings'],key=lambda p:len(p['products']))[:2]:
                target={(proof['coordinate'],)*6:Q(1)}
                examples.append(example(physical,mapped(proof['products']),mon_label(next(iter(target)))+' identity',target))
            if number==151 and index==0:
                square=rebuilt['linear_square'];L=s.cert.decode(square['linear'])
                examples.append(example(physical,square['products'],'Square of the new linear relation',s.cert.product(L,L)))
            i,j=min(((i,j) for i in range(len(eq)) for j in range(i+1,len(eq))),key=lambda p:len(eq[p[0]])+len(eq[p[1]]))
            products=[[i,m,c] for m,c in eq[j].items()]+[[j,m,-c] for m,c in eq[i].items()]
            examples.append(example(physical,mapped(products),'Degree-four Koszul boundary',{}))
            for ex in examples:
                ex.pop('products')
                for group in ex['groups']:group.pop('equation');group.pop('multipliers')
            final=b['strands'][-1]
            blocks.append({'name':'Before rebuilding' if index==0 else 'After rebuilding',
                'variables':len(b['active']),'quadratics':len(eq),'active':b['active'],
                'rank':final['rank'],'kernel':final['kernel'],'codomain':final['codomain'],
                'ranks':[r['rank'] for r in b['strands']],'targets':[r['codomain'] for r in b['strands']],
                'hilbert':[1,len(b['active'])]+[r['quotient_dimension'] for r in b['strands']],
                'zeros':[p['coordinate'] for p in final['vanishings']],'examples':examples})
        result=next(r for r in check['families'] if r['number']==number)
        families.append({'number':number,'blocks':blocks,'excluded':result['excluded'],
            'zeros':([56]+result['power_zeros']) if number==17 else [],
            'remaining':[i for i in rebuilt['active'] if i not in result['power_zeros']],
            'reduction':'a[56] = 0' if number==17 else '3a[115] - 6a[133] + a[234] + a[285] + a[288] = 0'})
    return {'families':families,'sourceSha256':q.source_sha(),
            'packetHashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(s.OUT.glob('*.json.gz'))}}


def figure(d):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':11,'svg.fonttype':'none','svg.hashsalt':'remaining-triples'})
    fig,axes=plt.subplots(2,2,figsize=(13,9),layout='constrained',gridspec_kw={'height_ratios':[1.2,1]})
    for a,f in zip(axes[0],d['families']):
        for b,color,style in zip(f['blocks'],['#b06834','#25759b'],['--o','-s']):
            a.plot(range(7),b['hilbert'],style,label=b['name'],color=color,markersize=5)
        a.set(xlabel='Total polynomial degree',ylabel='Quotient dimension',xticks=range(7),
              title='Family '+str(f['number'])+(': excluded' if f['excluded'] else ': reduced, still open'))
        a.legend(frameon=False);a.grid(alpha=.2)
        for i,b in enumerate(f['blocks']):a.annotate(str(b['hilbert'][-1]),(6,b['hilbert'][-1]),xytext=(-5,9 if i==0 else -14),textcoords='offset points')
    a=axes[1,0];a.set_axis_off();a.set_title('Family 17: complete proof chain')
    lines=['Full shared-numerator chart: a[56] = 1 impossible',
           'a[56] = 0; rebuild the physical correction equations',
           'Five quadratics in five X0 coordinates',
           'Degree-six map: rank 210 / 210; all five powers vanish',
           'X0 component = 0; replay fqlx’s X1/Y1 exclusion']
    for i,label in enumerate(lines):
        y=.93-i*.19;a.text(.02,y,label,va='center')
        if i<4:a.annotate('',xy=(.07,y-.14),xytext=(.07,y-.04),arrowprops={'arrowstyle':'->','color':'#777777'})
    a=axes[1,1];a.set_axis_off();a.set_title('Family 151: a useful change of basis')
    lines=[r'$L=3a_{115}-6a_{133}+a_{234}+a_{285}+a_{288}$',
           r'$L^2=108P_{12}-54P_{13}-18P_{11}$',
           r'$a_{133}=(3a_{115}+a_{234}+a_{285}+a_{288})/6$',
           'Rebuilt complementary block: 2 quadratics in 5 variables',
           'Degree-six quotient: 85; no coordinate sixth powers',
           'All five rebuilt shared-numerator charts remain unresolved']
    for i,label in enumerate(lines):a.text(.02,.93-i*.155,label,va='center')
    fig.suptitle('Keep the shared numerator, then rebuild the syzygy search',fontsize=16)
    fig.savefig(s.OUT/'remaining-triples.png',dpi=180)
    fig.savefig(s.OUT/'remaining-triples.svg',metadata={'Date':None});plt.close(fig)
    p=s.OUT/'remaining-triples.svg';p.write_text('\n'.join(l.rstrip() for l in p.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')


def build(check=False):
    d=data();template=e.ROOT/'visualizations/remaining-triples.template.html';output=e.ROOT/'visualizations/remaining-triples.html'
    text=template.read_text(encoding='utf-8').replace('__DATA__',json.dumps(d,separators=(',',':')))
    assert len(text.encode())<1_000_000
    if check:
        assert output.read_text(encoding='utf-8')==text
        assert json.loads((s.OUT/'visual-data.json').read_text())==d
    else:
        output.write_text(text,encoding='utf-8');(s.OUT/'visual-data.json').write_text(json.dumps(d,indent=2)+'\n',encoding='utf-8');figure(d)
    result={'status':'PASS','packetHashes':d['packetHashes'],'illustrative_identities':sum(len(b['examples']) for f in d['families'] for b in f['blocks']),
            'all_displayed_sums_checked_exactly':True,'fragment_sha256':hashlib.sha256(text.encode()).hexdigest()}
    (s.OUT/'figure-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');build(p.parse_args().check)

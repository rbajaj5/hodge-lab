"""Coverage, retained failures, and exact graded maps for X1/Y1 extensions."""
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations_with_replacement
import argparse,hashlib,json
import x1y1_extensions as x


def label(m):
    return ' '.join('a'+str(i)+('^'+str(k) if k>1 else '') for i,k in Counter(m).items()) or '1'


def data():
    first=json.loads((x.OUT/'validation.json').read_text());shared=json.loads((x.OUT/'shared-validation.json').read_text())
    assert first['status']==shared['status']=='PASS' and first['excluded']==123
    cases=[]
    for r in shared['families']:
        n=r['batch_number'];p=x.q.load(x.OUT/f'family-{n:03d}.json.gz');stage=p['stages'][-1]
        b=next(b for b in stage['blocks'] if b['character']==r['third_character'])
        eq=[x.cert.decode(stage['necessary'][j]['polynomial']) for j in b['equation_indices']];maps=[]
        for record in b['strands']:
            x.e.check_strand(eq,b['active'],record);assert not record['vanishings']
            columns,polys=x.e.mac_map(eq,b['active'],record['degree'])
            mons=list(combinations_with_replacement(b['active'],record['degree']));lookup={m:i for i,m in enumerate(mons)}
            cells=[{'row':lookup[m],'column':j,'exact':str(v)} for j,p in enumerate(polys) for m,v in sorted(p.items())]
            assert len(columns)==record['domain'] and len(mons)==record['codomain']
            maps.append({k:record[k] for k in ['degree','domain','codomain','rank','kernel','quotient_dimension']} |
                {'columns':['P'+str(b['equation_indices'][j])+' * '+label(m) for j,m in columns],
                 'rows':[label(m) for m in mons],'cells':cells})
        cases.append({**r,'maps':maps})
    assert len(cases)==9
    return {'excluded':132,'previous':152,'selected_total':284,'all_possible_triples':428536,
        'families':[{'batch_number':f['batch_number'],'third_character':f['third_character'],
                     'initial':len(f['basis_indices']),'shared_needed':not f['excluded']} for f in first['families']],
        'cases':cases,'packetHashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(x.OUT.glob('*.json.gz'))}}


def figure(d):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle,Patch
    plt.rcParams.update({'font.size':11,'svg.fonttype':'none','svg.hashsalt':'x1y1-extensions'})
    fig,axes=plt.subplots(1,2,figsize=(13,6),layout='constrained',gridspec_kw={'width_ratios':[1,1.35]})
    a=axes[0]
    for i,r in enumerate(d['families']):
        col=i%12;row=i//12;color='#d98930' if r['shared_needed'] else '#2b78a6'
        a.add_patch(Rectangle((col+.07,row+.07),.86,.86,facecolor=color,alpha=.23,edgecolor='none'))
        a.text(col+.5,row+.5,str(r['batch_number']),ha='center',va='center',fontsize=9)
    a.set(xlim=(0,12),ylim=(11,0),aspect='equal',title='132 new triples: all excluded')
    a.set_axis_off();a.legend(handles=[Patch(color='#2b78a6',alpha=.4,label='123: necessary block reductions'),
        Patch(color='#d98930',alpha=.4,label='9: shared equations + rebuild')],loc='lower left',bbox_to_anchor=(-.03,-.20),frameon=False)
    a=axes[1];rows=d['cases'];positions=range(len(rows));colors=['#8b8b8b','#2b78a6','#d98930','#3a8b70']
    keys=['initial','after_blocks','after_shared','final'];names=['Initial','After blocks','After shared charts','Residual pair']
    offsets=[-.24,-.08,.08,.24]
    for key,name,color,offset in zip(keys,names,colors,offsets):
        vals=[len(r[key]) if isinstance(r[key],list) else r[key] for r in rows]
        a.scatter(vals,[i+offset for i in positions],s=35,color=color,label=name,marker='s' if key=='final' else 'o')
    a.set(yticks=list(positions),yticklabels=[str(r['batch_number'])+'  '+str(tuple(r['third_character'])) for r in rows],
        xlabel='Retained denominator coordinates',ylabel='New-batch ID and added character',title='The nine first-pass failures, rebuilt')
    a.invert_yaxis();a.grid(axis='x',alpha=.2);a.legend(frameon=False,ncol=2,loc='lower left',bbox_to_anchor=(-.1,-.23),fontsize=10)
    fig.suptitle('X1/Y1 extensions: partial chart exclusions unlock new quadratic constraints',fontsize=15)
    fig.supxlabel('All residual pairs use the reproduced fqlx proof. 284 selected triples excluded; holdout remains unsolved.',fontsize=11)
    fig.savefig(x.OUT/'x1y1-extensions.png',dpi=180);fig.savefig(x.OUT/'x1y1-extensions.svg',metadata={'Date':None});plt.close(fig)
    p=x.OUT/'x1y1-extensions.svg';p.write_text('\n'.join(l.rstrip() for l in p.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')


def run(check=False):
    d=data();root=x.e.ROOT/'visualizations';template=root/'x1y1-extensions.template.html';out=root/'x1y1-extensions.html'
    html=template.read_text(encoding='utf-8').replace('__DATA__',json.dumps(d,separators=(',',':')))
    assert len(html.encode())<1_000_000
    if check:
        assert out.read_text(encoding='utf-8')==html
        assert json.loads((x.OUT/'visual-data.json').read_text())==d
    else:
        out.write_text(html,encoding='utf-8');(x.OUT/'visual-data.json').write_text(json.dumps(d,indent=2)+'\n');figure(d)
    report={'status':'PASS','families':132,'maps':sum(len(r['maps']) for r in d['cases']),
        'nonzero_entries':sum(len(m['cells']) for r in d['cases'] for m in r['maps']),
        'matrix_coefficients_and_ranks_checked':True,'fragment_sha256':hashlib.sha256(html.encode()).hexdigest()}
    (x.OUT/'figure-validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');run(p.parse_args().check)

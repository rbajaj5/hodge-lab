"""Actual polynomial cancellations and bounded-search outcomes for family 151."""
from collections import Counter
from fractions import Fraction as Q
import argparse,hashlib,json
import family151_multipliers as f
cert=f.cert;q=f.q


def data():
    validation=json.loads((f.OUT/'validation.json').read_text());assert validation['status']=='PASS'
    follow=json.loads((f.OUT/'follow-validation.json').read_text());assert follow['status']=='PASS'
    closure=json.loads((f.OUT/'closure-validation.json').read_text());assert closure['status']=='PASS' and closure['family151_excluded']
    desc,physical,_,_=f.build(f.e.t.Model(),None);nD=len(desc['ids']);cases=[]
    def name(mon):
        labels=[('a'+str(desc['ids'][i])) if i<nD else ('z'+str(desc['Koszul_indices'][i-nD])) for i in mon]
        return ' '.join(v+(('^'+str(k)) if k>1 else '') for v,k in Counter(labels).items()) or '1'
    for raw in f.CASES:
        packet=q.load(f.OUT/f'{f.label(raw)}.json.gz');pivot=packet['pivot']
        rows=physical if pivot is None else [cert.substitute(p,{pivot:{():Q(1)}}) for p in physical]
        examples=[]
        chosen=sorted(packet['selected_new'],key=lambda j:len(packet['relations'][j]['products']))[:2 if raw is None else 1]
        for j in chosen:
            relation=packet['relations'][j];claimed=cert.decode(relation['polynomial']);groups={}
            for row,mon,c in relation['products']:
                groups[row]=f.e.t.base.padd(groups.get(row,{}),cert.product(rows[row],{tuple(mon):Q(c)}))
            total={}
            for p in groups.values():total=f.e.t.base.padd(total,p)
            assert total==claimed
            mons=sorted({m for p in groups.values() for m in p},key=lambda m:(not any(i>=nD for i in m),m))
            displayed=[]
            for mon in mons:
                terms=sorted([(i,p[mon]) for i,p in groups.items() if p.get(mon)],key=lambda t:(-abs(t[1]),t[0]))
                # Every coefficient is retained; only the small marks are grouped.
                show=[{'label':'E'+str(i),'exact':str(c)} for i,c in terms[:9]]
                if len(terms)>9:show.append({'label':'Other '+str(len(terms)-9),'exact':str(sum(c for _,c in terms[9:]))})
                assert sum(Q(r['exact']) for r in show)==claimed.get(mon,Q(0))
                displayed.append({'label':name(mon),'rows':show,'sum':str(claimed.get(mon,Q(0))),
                    'numerator':any(i>=nD for i in mon),'equations':len(terms)})
            examples.append({'label':'Relation '+str(j),'index':j,'products':len(relation['products']),
                'monomials':displayed,'defaultMonomial':next((k for k,m in enumerate(displayed) if m['numerator']),0)})
        final=packet['checkpoints'][-1]
        outcome=next((r for r in follow['cases'] if r['raw_pivot']==raw),None)
        cases.append({'key':f.label(raw),'name':'Global homogeneous' if raw is None else 'a'+str(raw)+' = 1',
            'completed':packet['completed'],'newRelations':len(packet['selected_new']),
            'completedBlocks':len(packet['completed_multipliers']),'requestedBlocks':1+len(packet['variables']),
            'oldRank':final['baseline_multiple_rank'],'combinedRank':final['combined_relation_rank'],
            'steps':[{'block':i+1,'newRelations':r['new_relations'],'multiplier':name(tuple(r['multiplier']))} for i,r in enumerate(packet['checkpoints'])],
            'examples':examples,'follow':outcome})
    return {'cases':cases,'blocks':closure['blocks'],'excluded':closure['family151_excluded'],
        'physicalRows':len(physical),'denominatorParameters':nD,'numeratorParameters':len(desc['Koszul_indices']),
        'packetHashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(f.OUT.glob('*.json.gz'))}}


def figure(d):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':11,'svg.fonttype':'none','svg.hashsalt':'family151-multipliers'})
    fig,axes=plt.subplots(1,2,figsize=(13,5.5),layout='constrained')
    global_case=d['cases'][0];a=axes[0]
    a.plot([r['block'] for r in global_case['steps']],[r['newRelations'] for r in global_case['steps']],'-o',color='#276b94')
    a.set(title='Global cubic constraints beyond the old quadratics',xlabel='Completed multiplier blocks (constant, then coordinates)',ylabel='Additional independent denominator relations')
    a.grid(alpha=.2);a.annotate(str(global_case['newRelations']),xy=(global_case['steps'][-1]['block'],global_case['newRelations']),xytext=(-22,-16),textcoords='offset points')
    a=axes[1];blocks=d['blocks'];values=[r['ranks'][-1] for r in blocks]
    a.barh(['X1 block','Y0 block','Y1 block'],values,color='#276b94');a.invert_yaxis()
    a.set(title='Small blocks force thirteen fourth powers',xlabel='Exact degree-four image dimension')
    a.set_xlim(0,85);a.axvline(70,color='#777777',linestyle='--',linewidth=1)
    for i,(value,b) in enumerate(zip(values,blocks)):
        a.text(71,i,str(value)+'/70',va='center')
    a.text(.02,-.22,'13 coordinates vanish; two residual charts contradict.',transform=a.transAxes)
    a.grid(axis='x',alpha=.2)
    fig.suptitle('Family 151: polynomial multipliers cancel shared numerator corrections',fontsize=15)
    fig.supxlabel('Family 151 excluded; all 152 selected triples now excluded. Holdout remains unsolved. Progress curve is discovery telemetry.',fontsize=10)
    fig.savefig(f.OUT/'family151-multipliers.png',dpi=180);fig.savefig(f.OUT/'family151-multipliers.svg',metadata={'Date':None});plt.close(fig)
    p=f.OUT/'family151-multipliers.svg';p.write_text('\n'.join(l.rstrip() for l in p.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')


def run(check=False):
    d=data();root=f.e.ROOT/'visualizations';template=root/'family151-multipliers.template.html';out=root/'family151-multipliers.html'
    html=template.read_text(encoding='utf-8').replace('__DATA__',json.dumps(d,separators=(',',':')))
    assert len(html.encode())<1_000_000
    if check:
        assert out.read_text(encoding='utf-8')==html
        assert json.loads((f.OUT/'visual-data.json').read_text())==d
    else:
        out.write_text(html,encoding='utf-8');(f.OUT/'visual-data.json').write_text(json.dumps(d,indent=2)+'\n');figure(d)
    result={'status':'PASS','examples':sum(len(c['examples']) for c in d['cases']),
        'displayed_monomials':sum(len(ex['monomials']) for c in d['cases'] for ex in c['examples']),
        'all_coefficient_sums_checked_exactly':True,'packetHashes':d['packetHashes'],
        'fragment_sha256':hashlib.sha256(html.encode()).hexdigest()}
    (f.OUT/'figure-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');run(p.parse_args().check)

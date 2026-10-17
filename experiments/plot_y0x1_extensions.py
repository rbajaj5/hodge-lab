"""Data-linked coverage and rebuilding record for the Y0/X1 batch."""
import argparse,hashlib,json
import y0x1_extensions as y


def data():
    report=json.loads((y.OUT/'validation.json').read_text());assert report['status']=='PASS'
    rows=report['families'];assert len(rows)==132
    checkpoint=sum(r['excluded'] for r in rows)
    closure=json.loads((y.OUT/'multipliers-100/closure-validation.json').read_text())
    assert closure['status']=='PASS' and closure['excluded']
    last=next(r for r in rows if r['batch_number']==100)
    assert not last['excluded'] and len(last['remaining'])==13
    last['excluded']=True;last['remaining']=closure['remaining']
    return {'excluded':sum(r['excluded'] for r in rows),'checkpoint_excluded':checkpoint,
        'selected_union':284+sum(r['excluded'] for r in rows),
        'last_family_stages':[13,10,8,len(closure['remaining'])],
        'initial_excluded':sum(r['initial_excluded'] for r in rows),
        'unresolved':[r['batch_number'] for r in rows if not r['excluded']],
        'families':[{'number':r['batch_number'],'third':r['third_character'],'initial':len(r['basis_indices']),
            'after_blocks':len(r['initial_remaining']),'final':len(r['remaining']),
            'first_pass':r['initial_excluded'],'excluded':r['excluded'],
            'cycles':[{'before':len(s['before']),'after_charts':len(s['before'])-len(s['removed']),
                       'after_rebuild':len(s['after']),'chart_zeros':s['removed'],'rebuilt_zeros':s['rebuilt_zeros']} for s in r['cycles']]} for r in rows],
        'packetHashes':{p.relative_to(y.OUT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(y.OUT.rglob('*.json.gz'))}}


def run(check=False):
    d=data();path=y.OUT/'visual-data.json'
    if check:assert json.loads(path.read_text())==d
    else:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.patches import Rectangle,Patch
        plt.rcParams.update({'font.size':11,'svg.fonttype':'none','svg.hashsalt':'y0x1-extensions'})
        fig,axes=plt.subplots(1,2,figsize=(13,6),layout='constrained',gridspec_kw={'width_ratios':[1,1.35]})
        colors=['#287da7','#d58730','#af4a6f'];a=axes[0]
        for i,r in enumerate(d['families']):
            c=colors[0 if r['first_pass'] else 2 if r['number']==100 else 1];col=i%12;row=i//12
            a.add_patch(Rectangle((col+.07,row+.07),.86,.86,facecolor=c,alpha=.25,edgecolor='none'))
            a.text(col+.5,row+.5,str(r['number']),ha='center',va='center',fontsize=9)
        a.set(xlim=(0,12),ylim=(11,0),aspect='equal',title=str(d['excluded'])+'/132 new triples excluded');a.set_axis_off()
        a.legend(handles=[Patch(color=c,alpha=.4,label=l) for c,l in zip(colors,['123: first-pass reductions','8: shared equations + rebuild','1: new cubics + rebuild'])],loc='lower left',bbox_to_anchor=(-.03,-.21),frameon=False)
        a=axes[1];rows=[r for r in d['families'] if not r['first_pass']]
        for k,(key,label,col,offset) in enumerate([('initial','Initial','#888888',-.18),('after_blocks','After blocks',colors[0],0),('final','Final in this batch',colors[1],.18)]):
            a.scatter([r[key] for r in rows],[j+offset for j in range(len(rows))],s=38,color=col,label=label)
        a.set(yticks=range(len(rows)),yticklabels=['Y'+str(r['number'])+' '+str(tuple(r['third']))+(' *' if not r['excluded'] else '') for r in rows],
            xlabel='Retained denominator coefficients',ylabel='Y0/X1 batch ID and added character',title='All nine first-pass survivors now reduce to the old pair')
        a.invert_yaxis();a.grid(axis='x',alpha=.2);a.legend(frameon=False,loc='lower left',bbox_to_anchor=(-.05,-.2),fontsize=10)
        fig.suptitle('Y0/X1 extensions: 132 additional exclusions; 416 selected triples in total',fontsize=15)
        fig.supxlabel('Y100: 13 → 10 → 8 → 6 coefficients, then the verified pair exclusion. Y IDs differ from the old X1/Y1 batch. Holdout remains unsolved.',fontsize=10)
        fig.savefig(y.OUT/'y0x1-extensions.png',dpi=180);fig.savefig(y.OUT/'y0x1-extensions.svg',metadata={'Date':None});plt.close(fig)
        p=y.OUT/'y0x1-extensions.svg';p.write_text('\n'.join(l.rstrip() for l in p.read_text(encoding='utf-8').splitlines())+'\n',encoding='utf-8')
        path.write_text(json.dumps(d,indent=2)+'\n')
    (y.OUT/'figure-validation.json').write_text(json.dumps({'status':'PASS','excluded':d['excluded'],'unresolved':d['unresolved'],'packetHashes':d['packetHashes']},indent=2)+'\n')
    print('PASS: 132 family outcomes, nine continuation histories, exact source hashes')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');run(p.parse_args().check)

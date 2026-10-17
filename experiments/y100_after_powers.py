"""Rebuild the last Y0/X1 extension after the three new quartic vanishings."""
from collections import Counter
import argparse,hashlib,json
import y100_multipliers as m
import family151_cubic_blocks as cb
from check_x1y1_extensions import replay_stages
y=m.y;OUT=m.OUT


def setup(model):
    source=OUT/'global.json.gz';p=y.q.load(source);blocks=y.q.load(OUT/'pure-blocks.json.gz')
    assert blocks['source_sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
    desc,eq,_=m.build(model);assert desc==p['system']
    necessary=[y.cert.decode(r['polynomial']) for r in p['baseline']]+[y.cert.decode(p['relations'][j]['polynomial']) for j in p['selected_new']]
    forced=set()
    for b in blocks['blocks']:
        small=[necessary[j] for j in b['equation_indices']]
        for strand in b['strands']:
            cb.verify_strand(small,b['ids'],strand)
            forced.update(desc['basis_indices'][v['coordinate']] for v in strand['vanishings'])
    assert forced=={123,210,229}
    return desc,sorted(forced),[i for i in desc['basis_indices'] if i not in forced]


def run():
    model=y.t.Model();desc,forced,ids=setup(model);item=y.selection(model)[99]
    packet={'forced':forced,'source_sha256':hashlib.sha256((OUT/'global.json.gz').read_bytes()).hexdigest(),
        'cycles':[],'completed':False,'remaining':ids};path=OUT/'closure.json.gz'
    for cycle in range(len(ids)+1):
        blockpath=OUT/f'power-rebuilt-{cycle}.json.gz';y.blocks(model,item,ids,blockpath)
        r=y.q.load(blockpath);stage={'starting':ids,'block_file':blockpath.name,'block_sha256':hashlib.sha256(blockpath.read_bytes()).hexdigest()}
        ids=r['remaining'];packet['cycles'].append(stage);packet['remaining']=ids;y.q.save(path,packet)
        ending=y.terminal(model,ids)
        if ending:packet['status']=ending;break
        system,eq=y.build(model,item,ids);n=len(ids)+len(system['Koszul_indices']);stage['system']=system;stage['charts']=[]
        for pivot in system['pivots']:
            chart=y.cert.prove_chart(eq,n,pivot);y.cert.verify_chart(eq,n,chart);stage['charts'].append(chart);y.q.save(path,packet)
            print(cycle,'raw',ids[pivot],chart['excluded'],flush=True)
        removed=[ids[c['pivot']] for c in stage['charts'] if c['excluded']];stage['removed']=removed
        if not removed:packet['status']='unresolved';break
        ids=[i for i in ids if i not in removed];packet['remaining']=ids;y.q.save(path,packet)
    else:raise AssertionError('Each cycle must strictly decrease the active coordinates')
    packet['completed']=True;y.q.save(path,packet);print(packet['status'],packet['remaining'])


def check(independent=False):
    from check_quartic_exclusions import y0_x1,single_character
    if independent:
        from check_degree7_triples import IndependentModel
        model=IndependentModel()
    else:model=y.t.Model()
    desc,forced,ids=setup(model);p=y.q.load(OUT/'closure.json.gz');item=y.selection(model)[99];counts=Counter()
    assert p['source_sha256']==hashlib.sha256((OUT/'global.json.gz').read_bytes()).hexdigest() and p['forced']==forced and p['completed']
    for cycle,stage in enumerate(p['cycles']):
        assert stage['starting']==ids and stage['block_file']==f'power-rebuilt-{cycle}.json.gz'
        path=OUT/stage['block_file'];assert hashlib.sha256(path.read_bytes()).hexdigest()==stage['block_sha256']
        r=y.q.load(path);assert r['starting_indices']==ids and r['sources']==y.e.source_hashes()
        for k,v in item.items():assert r[k]==v
        ids,_,_,n=replay_stages(model,r,ids,finish=y.terminal);counts.update(n)
        if 'system' in stage:
            system,eq=y.build(model,item,ids);assert system==stage['system']
            assert [c['pivot'] for c in stage['charts']]==system['pivots'];nv=len(ids)+len(system['Koszul_indices'])
            for c in stage['charts']:counts['chart_inferences']+=y.cert.verify_chart(eq,nv,c)
            removed=[ids[c['pivot']] for c in stage['charts'] if c['excluded']];assert removed==stage['removed']
            ids=[i for i in ids if i not in removed]
    assert ids==p['remaining'];ending=y.terminal(model,ids);assert p['status']==(ending or 'unresolved');closure=None
    if ending=='pair22_dependency':closure=y0_x1(model,ids)
    elif ending=='single_character_dependency':closure=single_character(model,next(iter({model.dc[i] for i in ids})),ids)
    report={'status':'PASS','independent_physical_polynomials':independent,'excluded':ending is not None,'remaining':ids,
        'forced_by_cubics_and_quartics':forced,'checks':dict(counts),'dependency':closure}
    (OUT/(('independent-' if independent else '')+'closure-validation.json')).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--check',action='store_true');p.add_argument('--independent',action='store_true');a=p.parse_args()
    check(a.independent) if a.check else run()

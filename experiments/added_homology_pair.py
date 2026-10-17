"""Replay the full X0/X1 pair needed by the added-character batch.

This re-establishes a known two-character exclusion as an explicit dependency;
it is not counted as a new pair result. Every retained denominator direction is
included before any reduction, and all shared-numerator charts are archived,
including charts that this bounded solver cannot exclude.

Prior pair coverage is credited to fqlx's preceding scan and the continuations
listed in notes/x0-y0-exclusion.md. The terminal one-character packet is the
separate replay of previously reported single-character exclusions.
"""
from collections import Counter
import argparse,json,time
import added_character_homology as h
from check_x1y1_extensions import replay_stages
from check_quartic_exclusions import shared_system,single_character


def terminal(model,ids):
    if not ids:return 'excluded_directly'
    if len({model.dc[i] for i in ids})==1:return 'single_character_dependency'
    return None


def description(model):
    ids=sorted(i for c in h.ANCHOR for i in model.groups[c])
    assert ids==[42,56,88,102,111,114,123,139,180,210,229,232,262]
    return {'characters':sorted(map(list,h.ANCHOR)),'basis_indices':ids,
        'batch_number':0,'third_character':None}


def discover():
    model=h.t.Model();item=description(model);ids=item['basis_indices'][:]
    p={**item,'sources':h.e.source_hashes(),'cycles':[],'remaining':ids,
        'completed':False,'scope':'Full retained X0/X1 pair, replayed as a previously known dependency; not a new pair claim.'}
    path=h.OUT/'full-pair-binding.json.gz'
    for cycle in range(len(ids)+1):
        blockpath=h.OUT/f'full-pair-blocks-{cycle}.json.gz'
        h.x.family(model,item,initial=ids,destination=blockpath,finish=terminal)
        stage={'before':ids,'block_file':blockpath.name,'block_sha256':h.digest(blockpath)}
        ids=h.q.load(blockpath)['remaining'];p['cycles'].append(stage)
        p['remaining']=ids;h.q.save(path,p)
        if terminal(model,ids):break
        system=shared_system(model,ids);stage['system']=system
        eq=[h.cert.decode(e) for e in system['equations']];nv=len(ids)+len(system['ks'])
        stage['charts']=[]
        for pivot in range(len(ids)):
            chart=h.cert.prove_chart(eq,nv,pivot);h.cert.verify_chart(eq,nv,chart)
            stage['charts'].append(chart);h.q.save(path,p)
            print('pair chart',ids[pivot],chart['excluded'],flush=True)
        removed=[ids[c['pivot']] for c in stage['charts'] if c['excluded']]
        stage['removed']=removed;ids=[i for i in ids if i not in removed]
        p['remaining']=ids;h.q.save(path,p)
        if not removed:break
    else:raise AssertionError('Successful cycles strictly decrease directions')
    p.update(completed=True,status=terminal(model,ids) or 'unresolved',remaining=ids)
    h.q.save(path,p);assert terminal(model,ids)
    print('full X0/X1 pair closed at',ids,flush=True)


def replay(model):
    item=description(model);ids=item['basis_indices'][:];counts=Counter()
    path=h.OUT/'full-pair-binding.json.gz';p=h.q.load(path)
    for k,v in item.items():assert p[k]==v
    assert p['sources']==h.e.source_hashes() and p['completed']
    cycles=[]
    for cycle,stage in enumerate(p['cycles']):
        assert stage['before']==ids and not terminal(model,ids)
        assert stage['block_file']==f'full-pair-blocks-{cycle}.json.gz'
        blockpath=h.OUT/stage['block_file'];assert stage['block_sha256']==h.digest(blockpath)
        block=h.q.load(blockpath)
        for k,v in item.items():assert block[k]==v
        assert block['starting_indices']==ids and block['completed'] and block['sources']==h.e.source_hashes()
        ids,zeros,_,cc=replay_stages(model,block,ids,finish=terminal);counts.update(cc)
        assert block['status']==(terminal(model,ids) or 'unresolved_bounded_search')
        detail={'before':stage['before'],'block_zeros':zeros,'after_blocks':ids[:],'charts':[]}
        if 'system' in stage:
            assert not terminal(model,ids)
            system=shared_system(model,ids);assert system==stage['system']
            assert [c['pivot'] for c in stage['charts']]==list(range(len(ids)))
            eq=[h.cert.decode(e) for e in system['equations']];nv=len(ids)+len(system['ks'])
            removed=[]
            for c in stage['charts']:
                counts['pair_chart_inferences']+=h.cert.verify_chart(eq,nv,c)
                counts['pair_charts']+=1
                detail['charts'].append({'raw':ids[c['pivot']],'excluded':c['excluded']})
                if c['excluded']:removed.append(ids[c['pivot']]);counts['pair_excluded_charts']+=1
            assert stage['removed']==removed;ids=[i for i in ids if i not in removed]
        else:assert terminal(model,ids)
        detail['after']=ids[:];cycles.append(detail)
    assert p['remaining']==ids and p['status']==terminal(model,ids) and terminal(model,ids)
    closure=single_character(model,model.dc[ids[0]],ids) if ids else None
    return {'kind':'replayed_full_X0_X1_pair','packet_sha256':h.digest(path),
        'full_pair_basis':item['basis_indices'],'cycles':cycles,'remaining':ids,
        'single_character':closure,'scope':'Known two-character exclusion, explicitly rebound to all thirteen retained directions.'},counts


def check(independent=False):
    start=time.perf_counter()
    if independent:
        from check_degree7_triples import IndependentModel
        model=IndependentModel()
    else:model=h.t.Model()
    result,counts=replay(model)
    report={'status':'PASS','independent_physical_polynomials':independent,
        'checks':dict(counts),'dependency':result,'seconds':time.perf_counter()-start}
    name='full-pair-'+('independent-' if independent else '')+'validation.json'
    (h.OUT/name).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2),flush=True)


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    h.OUT.mkdir(parents=True,exist_ok=True)
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--discover',action='store_true')
    p.add_argument('--independent',action='store_true');a=p.parse_args()
    if a.discover:discover()
    check(a.independent)

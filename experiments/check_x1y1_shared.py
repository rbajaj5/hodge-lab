"""Replay shared charts and rebuilt consequences on all nine survivors."""
from collections import Counter
import argparse,copy,hashlib,json,time
import x1y1_shared as s
from check_x1y1_extensions import replay_stages,pair30_binding
x=s.x;q=s.q;cert=s.cert


def check(independent=False):
    start=time.perf_counter()
    if independent:
        from check_degree7_triples import IndependentModel
        model=IndependentModel()
    else:model=x.t.Model()
    items={r['batch_number']:r for r in x.selection(model)};counts=Counter();results=[]
    plan=json.loads((x.OUT/'shared-plan.json').read_text());selected=s.survivors()
    attempts=json.loads((x.OUT/'shared-attempts.json').read_text())
    assert plan['families']==selected==[r['batch_number'] for r in attempts]
    assert all(r['status']=='completed' and r['exit_code']==0 and r['limit_seconds']==60 for r in attempts)
    for number in selected:
        source=q.load(x.OUT/f'family-{number:03d}.json.gz');item=items[number]
        for k,v in item.items():assert source[k]==v
        assert source['sources']==x.e.source_hashes()
        ids,_,_,checks=replay_stages(model,source,item['basis_indices']);counts.update(checks)
        desc,eq,digest=s.build(model,number)
        path=x.OUT/f'shared-{number:03d}.json.gz';packet=q.load(path)
        assert packet['batch_number']==number and packet['source_sha256']==digest and packet['system']==desc
        assert packet['completed'] and [c['pivot'] for c in packet['charts']]==desc['pivots']
        assert desc['basis_indices']==ids and all(len(m)==2 for p in eq for m in p)
        n=len(ids)+len(desc['Koszul_indices']);removed=[];charts=[]
        for c in packet['charts']:
            counts['chart_inferences']+=cert.verify_chart(eq,n,c);counts['charts']+=1
            raw=ids[c['pivot']]
            if c['excluded']:removed.append(raw);counts['excluded_charts']+=1
            charts.append({'raw_pivot':raw,'excluded':c['excluded'],'remaining_variables':c['remaining_variables']})
        # Homogeneity in (a,z) makes each normalized contradiction a global
        # coordinate vanishing, even when other normalized charts survive.
        broken=copy.deepcopy(next(c for c in packet['charts'] if c['excluded']))
        inference=next(i for stage in broken['stages'] for i in stage['inferences'])
        inference['witness']['polynomial']=[[[],'12345']]
        try:cert.verify_chart(eq,n,broken)
        except AssertionError:counts['chart_mutations_rejected']+=1
        else:raise AssertionError('Altered chart identity accepted')
        reduced=[i for i in ids if i not in removed];continued=q.load(x.OUT/f'continued-{number:03d}.json.gz')
        for k,v in item.items():assert continued[k]==v
        assert continued['sources']==x.e.source_hashes() and continued['shared_removed']==removed
        assert continued['shared_sha256']==hashlib.sha256(path.read_bytes()).hexdigest()
        assert continued['starting_indices']==reduced
        final,zeros,blocks,checks=replay_stages(model,continued,reduced);counts.update(checks)
        assert continued['completed'] and continued['status']==x.terminal(model,final)=='pair30_dependency'
        assert set(final)<=x.PAIR_IDS
        results.append({'batch_number':number,'global_number':item['global_number'],
            'third_character':item['third_character'],'initial':len(item['basis_indices']),
            'after_blocks':len(ids),'numerator_parameters':len(desc['Koszul_indices']),
            'stabilizer_order':desc['stabilizer_order'],'physical_equations':len(eq),
            'charts':charts,'shared_removed':removed,'after_shared':len(reduced),
            'rebuilt_removed':zeros,'rebuilt_blocks':blocks,'final':final,'excluded':True})
    closure=pair30_binding(model,sorted(x.PAIR_IDS),x.OUT/'pair30')
    report={'status':'PASS','independent_physical_polynomials':independent,'checks':dict(counts),
        'families':results,'new_shared_exclusions':len(results),'pair30_binding':closure,
        'seconds':time.perf_counter()-start,
        'scope':'Nine closures after the separately replayed first pass. All 132 new triples are excluded; 284 selected triples including the preceding 152. Not all 428536 triples.'}
    (x.OUT/(('independent-' if independent else '')+'shared-validation.json')).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='families'},indent=2),flush=True)


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--independent',action='store_true');check(p.parse_args().independent)

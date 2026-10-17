"""Exact complete replay of the Y0/X1 batch and all saved follow-up cycles."""
from collections import Counter
import argparse,copy,hashlib,json,time
import y0x1_extensions as y
from check_x1y1_extensions import replay_stages
from check_quartic_exclusions import y0_x1,single_character


def check(independent=False):
    start=time.perf_counter()
    if independent:
        from check_degree7_triples import IndependentModel
        model=IndependentModel()
    else:model=y.t.Model()
    items=y.selection(model);plan=json.loads((y.OUT/'blocks-plan.json').read_text())
    assert plan['new_selection']==items and plan['sources']==y.e.source_hashes() and plan['previous_selection']==284
    attempts=json.loads((y.OUT/'blocks-attempts.json').read_text());assert [a['job'] for a in attempts]==[0,1]
    assert all(a['status']=='completed' and a['exit_code']==0 for a in attempts)
    counts=Counter();results=[];pair=None;singles={};survivors=[]
    for item in items:
        number=item['batch_number'];path=y.OUT/f'family-{number:03d}.json.gz';initial=y.q.load(path)
        for k,v in item.items():assert initial[k]==v
        assert initial['sources']==y.e.source_hashes() and initial['completed']
        ids,zeros,_,n=replay_stages(model,initial,item['basis_indices'],finish=y.terminal);counts.update(n)
        ending=y.terminal(model,ids);assert initial['status']==(ending or 'unresolved_bounded_search')
        result={**item,'initial_remaining':ids[:],'initial_excluded':ending is not None,'cycles':[]}
        if not ending:
            survivors.append(number);followpath=y.OUT/f'follow-{number:03d}.json.gz'
            if followpath.exists():
                packet=y.q.load(followpath)
                assert packet['batch_number']==number and packet['source_sha256']==hashlib.sha256(path.read_bytes()).hexdigest()
                for cycle,stage in enumerate(packet['cycles']):
                    assert not y.terminal(model,ids)
                    desc,eq=y.build(model,item,ids);assert desc==stage['system']
                    assert all(len(m)==2 for p in eq for m in p)
                    assert [c['pivot'] for c in stage['charts']]==desc['pivots'][:len(stage['charts'])]
                    if stage['completed']:assert [c['pivot'] for c in stage['charts']]==desc['pivots']
                    nv=len(ids)+len(desc['Koszul_indices']);removed=[]
                    for c in stage['charts']:
                        counts['chart_inferences']+=y.cert.verify_chart(eq,nv,c);counts['charts']+=1
                        if c['excluded']:removed.append(ids[c['pivot']]);counts['excluded_charts']+=1
                    if stage['charts']:
                        broken=copy.deepcopy(stage['charts'][0]);inf=next((i for s in broken['stages'] for i in s['inferences']),None)
                        if inf:
                            inf['witness']['polynomial']=[[[],'12345']]
                            try:y.cert.verify_chart(eq,nv,broken)
                            except AssertionError:counts['chart_mutations_rejected']+=1
                            else:raise AssertionError('Altered chart accepted')
                    summary={'before':ids[:],'Koszul_coordinates':len(desc['Koszul_indices']),
                        'equations':len(eq),'charts':[{'raw':ids[c['pivot']],'excluded':c['excluded'],'remaining':c['remaining_variables']} for c in stage['charts']],
                        'removed':removed,'rebuilt_zeros':[]}
                    if stage['completed']:
                        assert stage['removed']==removed
                        if removed:
                            ids=[i for i in ids if i not in removed];assert stage['after_shared']==ids
                            if 'rebuilt_file' in stage:
                                path2=y.OUT/stage['rebuilt_file'];assert stage['rebuilt_file']==f'rebuilt-{number:03d}-{cycle}.json.gz'
                                assert hashlib.sha256(path2.read_bytes()).hexdigest()==stage['rebuilt_sha256']
                                row=y.q.load(path2);assert row['starting_indices']==ids and row['sources']==y.e.source_hashes()
                                for k,v in item.items():assert row[k]==v
                                ids,forced,_,n=replay_stages(model,row,ids,finish=y.terminal);counts.update(n);summary['rebuilt_zeros']=forced
                                assert row['completed'] and row['status']==(y.terminal(model,ids) or 'unresolved_bounded_search')
                            else:assert not packet['completed']
                    summary['after']=ids[:];result['cycles'].append(summary)
                # A timed-out partial chart scan is retained without counting
                # unstored rebuilds or assigning a completed-family status.
                if packet['completed']:
                    assert packet['remaining']==ids
                    assert packet['status']==(y.terminal(model,ids) or 'unresolved_shared_charts')
                ending=y.terminal(model,ids)
                result['follow_completed']=packet['completed'];result['follow_status']=packet['status']
        if ending=='pair22_dependency':
            assert set(ids)<=set(i for c in y.ANCHOR for i in model.groups[c])
            if pair is None:pair=y0_x1(model,sorted(i for c in y.ANCHOR for i in model.groups[c]))
        elif ending=='single_character_dependency':
            char=next(iter({model.dc[i] for i in ids}))
            if char not in singles:singles[char]=single_character(model,char,ids)
        result.update({'remaining':ids,'excluded':ending is not None,'dependency':ending});results.append(result)
    fp=json.loads((y.OUT/'follow-plan.json').read_text());assert fp['jobs']==survivors and fp['new_selection']==items
    fa=json.loads((y.OUT/'follow-attempts.json').read_text());assert [a['job'] for a in fa]==survivors
    for a in fa:
        r=next(r for r in results if r['batch_number']==a['job'])
        assert a['status'] in ['completed','timeout','error']
        if a['status']=='completed':assert a['exit_code']==0 and r.get('follow_completed')
    report={'status':'PASS','independent_physical_polynomials':independent,'checks':dict(counts),'families':results,
        'initial_excluded':sum(r['initial_excluded'] for r in results),'excluded':sum(r['excluded'] for r in results),
        'unresolved':[r['batch_number'] for r in results if not r['excluded']],
        'pair22_dependency':pair,'single_character_dependencies':list(singles.values()),'seconds':time.perf_counter()-start,
        'scope':'132 new full retained three-character families, disjoint from the preceding 284. Holdout remains open.'}
    (y.OUT/(('independent-' if independent else '')+'validation.json')).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='families'},indent=2),flush=True)


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--independent',action='store_true');check(p.parse_args().independent)

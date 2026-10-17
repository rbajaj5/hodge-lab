"""Exact baseline, pair-dependency, and optional ordinary continuation replay.

Typed versus untyped experiment records are checked by their own producer;
this file verifies the unchanged physical systems and proof dependencies.
"""
from collections import Counter
from fractions import Fraction as Q
import argparse,copy,json,time
import typed_rewrite_families as h
from check_x1y1_extensions import replay_stages
from check_quartic_exclusions import single_character
from check_added_character_homology import reject_altered_chart


def read(name):return json.loads((h.OUT/name).read_text(encoding='utf-8'))


def check_plan(phase,items):
    plan=read(f'{phase}-plan.json');attempts=read(f'{phase}-attempts.json')
    assert plan['phase']==phase and plan['selection']==items
    assert plan['sources']==h.e.source_hashes()
    assert plan['anchor']==sorted(map(list,h.ANCHOR))
    assert plan['preceding_selected_exclusions']==680
    assert plan['workers']==(1 if phase=='pair' else 2)
    assert len(plan['jobs'])==len(set(plan['jobs']))
    assert [a['job'] for a in attempts]==plan['jobs']
    assert 0<plan['seconds_per_job']<=300
    for a in attempts:
        assert a['status'] in ['completed','timeout','error']
        assert a['limit']==plan['seconds_per_job'] and a['seconds']>=0
        if a['status']=='completed':assert a['exit_code']==0
        elif a['status']=='timeout':assert a['exit_code'] is None
        else:assert isinstance(a['exit_code'],int) and a['exit_code']!=0
    return plan,attempts


def baseline(model,item,row):
    for k,v in item.items():assert row[k]==v
    assert row['sources']==h.e.source_hashes() and row['completed']
    ids=item['basis_indices'][:];counts=Counter()
    for position,stage in enumerate(row['stages']):
        assert stage['active']==ids and not h.terminal(model,ids)
        counts.update(h.e.check_physical(model,stage))
        eq=[h.cert.decode(r['polynomial']) for r in stage['necessary']]
        span=h.t.base.Elimination()
        for p in eq:span.insert(dict(p))
        assert len(span.basis)==stage['rank'];removed=[]
        for c in stage['squares']:
            i=c['coordinate'];assert i in ids and i not in removed
            assert all(not mon for _,mon,_ in c['products'])
            assert h.e.expand_products(eq,c['products'])=={(i,i):Q(1)}
            removed.append(i);counts['square_identities']+=1
        if stage['squares']:
            bad=copy.deepcopy(stage['squares'][0]);bad['products'][0][2]=str(Q(bad['products'][0][2])+1)
            assert h.e.expand_products(eq,bad['products'])!={(bad['coordinate'],)*2:Q(1)}
            counts['altered_squares_rejected']+=1
        else:assert position==len(row['stages'])-1
        ids=[i for i in ids if i not in removed]
    assert row['remaining']==ids and row['status']==(h.terminal(model,ids) or 'unresolved_squares')
    return ids,counts


def replay_continuation(model,item,ids,p,stem,finish,counts):
    assert p['batch_number']==item['batch_number'] and p['starting_indices']==ids
    assert p['sources']==h.e.source_hashes();cycles=[]
    for cycle,stage in enumerate(p['cycles']):
        assert stage['before']==ids and stage['block_file']==f'{stem}-{cycle}.json.gz'
        path=h.OUT/stage['block_file'];assert h.digest(path)==stage['block_sha256']
        block=h.q.load(path)
        for k,v in item.items():assert block[k]==v
        assert block['starting_indices']==ids and block['completed']
        assert block['sources']==h.e.source_hashes()
        ids,zeros,_,cc=replay_stages(model,block,ids,finish=finish);counts.update(cc)
        assert block['status']==(finish(model,ids) or 'unresolved_bounded_search')
        detail={'before':stage['before'],'block_zeros':zeros,'after_blocks':ids[:],'charts':[]}
        if 'system' in stage:
            assert not finish(model,ids)
            desc,eq=h.build(model,item,ids);assert stage['system']==desc
            assert [c['pivot'] for c in stage['charts']]==desc['pivots'][:len(stage['charts'])]
            if p['completed'] or 'removed' in stage:
                assert [c['pivot'] for c in stage['charts']]==desc['pivots']
            removed=[];nvars=len(ids)+len(desc['Koszul_indices'])
            for chart in stage['charts']:
                counts['chart_inferences']+=h.cert.verify_chart(eq,nvars,chart);counts['charts']+=1
                counts['altered_charts_rejected']+=reject_altered_chart(eq,nvars,chart)
                detail['charts'].append({'raw':ids[chart['pivot']],'excluded':chart['excluded']})
                if chart['excluded']:removed.append(ids[chart['pivot']]);counts['excluded_charts']+=1
            if 'removed' in stage:
                assert stage['removed']==removed;ids=[i for i in ids if i not in removed]
        else:assert finish(model,ids) or not p['completed']
        detail['after']=ids[:];cycles.append(detail)
    assert p['remaining']==ids
    if p['completed']:assert p['status']==(finish(model,ids) or 'unresolved')
    return ids,cycles


def replay_pair(model):
    items=h.selection(model);plan,attempts=check_plan('pair',items)
    assert plan['jobs']==[0]
    item=h.pair_description(model);ids=item['basis_indices'][:]
    path=h.OUT/'full-pair-binding.json.gz';p=h.q.load(path);counts=Counter()
    if attempts[0]['status']=='completed':assert p['completed']
    ids,cycles=replay_continuation(model,item,ids,p,'full-pair-blocks',h.pair_terminal,counts)
    assert h.pair_terminal(model,ids),'The anchor-pair dependency is not established'
    closure=single_character(model,model.dc[ids[0]],ids) if ids else None
    return {'kind':'replayed_full_X0_Y1_pair','packet_sha256':h.digest(path),
        'full_pair_basis':item['basis_indices'],'cycles':cycles,'remaining':ids,
        'single_character':closure,
        'scope':'Known two-character exclusion reconstructed from its complete retained anchor space.'},counts


def check(independent=False,include_follow=False,pair_only=False):
    started=time.perf_counter()
    if independent:
        from check_degree7_triples import IndependentModel
        model=IndependentModel()
    else:model=h.Model()
    dependency,pair_counts=replay_pair(model)
    prefix='independent-' if independent else ''
    if pair_only:
        report={'status':'PASS','independent_physical_polynomials':independent,
            'dependency':dependency,'checks':dict(pair_counts),'seconds':time.perf_counter()-started}
        destination=h.OUT/f'pair-{prefix}validation.json'
    else:
        items=h.selection(model);bp,ba=check_plan('baseline',items)
        assert bp['jobs']==[0,1] and bp['seconds_per_job']==300
        assert all(a['status']=='completed' for a in ba)
        counts=Counter();families=[];singles={};attempted={}
        if include_follow:
            fp,fa=check_plan('follow',items);attempted={a['job']:a for a in fa}
            assert set(fp['jobs'])<=set(h.survivors(model))
        for item in items:
            number=item['batch_number'];source=h.OUT/f'baseline-{number:03d}.json.gz'
            row=h.q.load(source);ids,cc=baseline(model,item,row);counts.update(cc)
            initial=h.terminal(model,ids) is not None;cycles=[]
            if number in attempted:
                assert not initial;path=h.OUT/f'follow-{number:03d}.json.gz'
                if path.exists():
                    packet=h.q.load(path);assert packet['source_sha256']==h.digest(source)
                    if attempted[number]['status']=='completed':assert packet['completed']
                    ids,cycles=replay_continuation(model,item,ids,packet,f'rebuild-{number:03d}',h.terminal,counts)
                else:assert attempted[number]['status'] in ['timeout','error']
            ending=h.terminal(model,ids)
            if ending=='single_character_dependency':
                char=model.dc[ids[0]]
                if char not in singles:singles[char]=single_character(model,char,ids)
            families.append({**item,'baseline_remaining':row['remaining'],
                'baseline_packet_sha256':h.digest(source),'initial_excluded':initial,
                'remaining':ids,'excluded':ending is not None,'dependency':ending,
                'attempt':attempted.get(number),'cycles':cycles})
        report={'status':'PASS','independent_physical_polynomials':independent,
            'baseline_excluded':sum(r['initial_excluded'] for r in families),
            'excluded':sum(r['excluded'] for r in families),
            'unresolved':[r['batch_number'] for r in families if not r['excluded']],
            'families':families,'checks':dict(counts),'pair_checks':dict(pair_counts),
            'pair_dependency':dependency,'single_dependencies':list(singles.values()),
            'seconds':time.perf_counter()-started,
            'scope':'132 new complete retained X0/Y1 extensions; this report does not evaluate the separately frozen typed versus untyped comparison.'}
        if include_follow:
            checkpoint=read(f'baseline-{prefix}validation.json')
            assert checkpoint['status']=='PASS' and checkpoint['independent_physical_polynomials']==independent
            assert checkpoint['pair_dependency']==dependency and checkpoint['pair_checks']==dict(pair_counts)
            assert checkpoint['excluded']==report['baseline_excluded']
            assert len(checkpoint['families'])==len(families)
            for before,after in zip(checkpoint['families'],families):
                for key in list(items[0])+['baseline_remaining','baseline_packet_sha256','initial_excluded']:
                    assert before[key]==after[key]
                assert before['attempt'] is None and not before['cycles']
                if after['batch_number'] not in attempted:assert before==after
            report['baseline_checkpoint_excluded']=checkpoint['excluded']
        destination=h.OUT/f'{"follow" if include_follow else "baseline"}-{prefix}validation.json'
    if not include_follow and destination.exists():
        old=read(destination.name)
        assert {k:v for k,v in old.items() if k!='seconds'}=={k:v for k,v in report.items() if k!='seconds'}
    else:destination.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ['families','pair_dependency','dependency']},indent=2),flush=True)


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--independent',action='store_true')
    p.add_argument('--follow',action='store_true');p.add_argument('--pair-only',action='store_true')
    a=p.parse_args();check(a.independent,a.follow,a.pair_only)

"""Replay added-character ranking and all bounded three-character attempts.

The optional comparison checkpoint is written before continuing the remaining
families.  Neither a positive homology score nor a failed chart excludes a
family: only replayed rational identities and checked dependencies do that.
"""
from collections import Counter
from fractions import Fraction as Q
import argparse,copy,json,time
import added_character_homology as h
from check_x1y1_extensions import replay_stages
from check_quartic_exclusions import single_character


def read(name):
    return json.loads((h.OUT/name).read_text(encoding='utf-8'))


def check_plan(phase,items):
    plan=read(f'{phase}-plan.json');attempts=read(f'{phase}-attempts.json')
    assert plan['phase']==phase and plan['selection']==items
    assert plan['sources']==h.e.source_hashes() and plan['workers']==2
    assert len(plan['jobs'])==len(set(plan['jobs']))
    assert [a['job'] for a in attempts]==plan['jobs']
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
            bad=copy.deepcopy(stage['squares'][0])
            bad['products'][0][2]=str(Q(bad['products'][0][2])+1)
            assert h.e.expand_products(eq,bad['products'])!={(bad['coordinate'],)*2:Q(1)}
            counts['altered_squares_rejected']+=1
        else:assert position==len(row['stages'])-1
        ids=[i for i in ids if i not in removed]
    assert row['remaining']==ids
    assert row['status']==(h.terminal(model,ids) or 'unresolved_squares')
    return ids,counts


def profile(model,number,row):
    source=h.OUT/f'baseline-{number:03d}.json.gz'
    p=h.q.load(h.OUT/f'profile-{number:03d}.json.gz')
    assert p['completed'] and p['source_sha256']==h.digest(source)
    assert p['batch_number']==number
    stage=row['stages'][-1];assert stage['active']==row['remaining']
    eq=[h.cert.decode(r['polynomial']) for r in stage['necessary']]
    char=tuple(row['third_character']);assert char not in h.ANCHOR
    ids=[i for i in row['remaining'] if model.dc[i]==char];assert ids
    chosen=[j for j,r in enumerate(eq) if all(i in ids for mon in r for i in mon)]
    small=[eq[j] for j in chosen]
    maps=[h.kh.complex_at(small,ids,d) for d in [3,4]] if small else []
    # A distinct elimination routine cross-checks the first differential ranks.
    for d,r in zip([3,4],maps):
        _,cols=h.e.mac_map(small,ids,d);span=h.t.base.Elimination()
        for column in cols:span.insert(dict(column))
        assert len(span.basis)==r['differential_ranks'][0]
    records=[{'character':list(char),'ids':ids,'equation_indices':chosen,'homology':maps}]
    assert records==p['blocks']
    assert p['score']==(maps[1]['homology'][1] if maps else 0)
    assert p['score_degree3']==(maps[0]['homology'][1] if maps else 0)
    return p


def reject_altered_chart(eq,nvars,proof):
    """Corrupt an asserted polynomial, so rejection does not depend on a rank."""
    for si,stage in enumerate(proof['stages']):
        if stage['inferences']:
            bad=copy.deepcopy(proof)
            witness=bad['stages'][si]['inferences'][0]['witness']
            claim=h.cert.decode(witness['polynomial'])
            claim[()]=claim.get((),Q(0))+1
            witness['polynomial']=h.cert.encode(claim)
            try:h.cert.verify_chart(eq,nvars,bad)
            except AssertionError:return 1
            raise AssertionError('An altered chart polynomial was accepted')
    return 0


def follow(model,item,ids,attempt,counts):
    number=item['batch_number'];path=h.OUT/f'follow-{number:03d}.json.gz'
    if not path.exists():
        assert attempt['status'] in ['timeout','error'];return ids,[]
    p=h.q.load(path)
    assert p['source_sha256']==h.digest(h.OUT/f'baseline-{number:03d}.json.gz')
    assert p['batch_number']==number;cycles=[]
    for cycle,stage in enumerate(p['cycles']):
        assert stage['before']==ids
        assert stage['block_file']==f'rebuild-{number:03d}-{cycle}.json.gz'
        blockpath=h.OUT/stage['block_file']
        assert h.digest(blockpath)==stage['block_sha256']
        r=h.q.load(blockpath)
        assert r['starting_indices']==ids and r['completed']
        assert r['sources']==h.e.source_hashes()
        for k,v in item.items():assert r[k]==v
        ids,zeros,_,cc=replay_stages(model,r,ids,finish=h.terminal)
        counts.update(cc)
        assert r['status']==(h.terminal(model,ids) or 'unresolved_bounded_search')
        detail={'before':stage['before'],'block_zeros':zeros,'after_blocks':ids[:],'charts':[]}
        if 'system' in stage:
            assert not h.terminal(model,ids)
            desc,eq=h.build(model,item,ids);assert desc==stage['system']
            assert [c['pivot'] for c in stage['charts']]==desc['pivots'][:len(stage['charts'])]
            if p['completed'] or 'removed' in stage:
                assert [c['pivot'] for c in stage['charts']]==desc['pivots']
            nvars=len(ids)+len(desc['Koszul_indices']);removed=[]
            for c in stage['charts']:
                counts['chart_inferences']+=h.cert.verify_chart(eq,nvars,c)
                counts['charts']+=1
                counts['altered_charts_rejected']+=reject_altered_chart(eq,nvars,c)
                detail['charts'].append({'raw':ids[c['pivot']],'excluded':c['excluded']})
                if c['excluded']:
                    removed.append(ids[c['pivot']]);counts['excluded_charts']+=1
            if 'removed' in stage:
                assert stage['removed']==removed
                ids=[i for i in ids if i not in removed]
        detail['after']=ids[:];cycles.append(detail)
    assert p['remaining']==ids
    if p['completed']:assert p['status']==(h.terminal(model,ids) or 'unresolved')
    if attempt['status']=='completed':assert p['completed'] and attempt['exit_code']==0
    return ids,cycles


def check(independent=False,comparison=False):
    start=time.perf_counter()
    if independent:
        from check_degree7_triples import IndependentModel
        model=IndependentModel()
    else:model=h.t.Model()
    items=h.selection(model)
    bp,ba=check_plan('baseline',items)
    assert bp['jobs']==[0,1] and all(a['status']=='completed' for a in ba)
    fp,fa=check_plan('follow',items)
    assert fp['seconds_per_job']==120
    attempted={a['job']:a for a in fa};remaining_jobs=[]
    if not comparison and (h.OUT/'remaining-plan.json').exists():
        rp,ra=check_plan('remaining',items)
        assert rp['seconds_per_job']==fp['seconds_per_job']
        remaining_jobs=rp['jobs']
        assert not set(attempted)&set(remaining_jobs)
        attempted.update({a['job']:a for a in ra})
    # A full-pair certificate must bind every retained anchor direction.
    # The replay implementation is supplied by the separate dependency audit.
    from added_homology_pair import replay as replay_pair
    dependency,counts=replay_pair(model)
    counts=Counter(counts);profiles=[];rows=[];singles={}
    for item in items:
        number=item['batch_number']
        row=h.q.load(h.OUT/f'baseline-{number:03d}.json.gz')
        ids,cc=baseline(model,item,row);counts.update(cc)
        initial=h.terminal(model,ids) is not None;score=None;cycles=[]
        if not initial:
            p=profile(model,number,row)
            profiles.append({'number':number,'score':p['score'],
                'profile_sha256':h.digest(h.OUT/f'profile-{number:03d}.json.gz')})
            score=p['score'];counts['homology_complexes']+=sum(len(b['homology']) for b in p['blocks'])
        if number in attempted:
            assert not initial
            ids,cycles=follow(model,item,ids,attempted[number],counts)
        ending=h.terminal(model,ids)
        if ending=='single_character_dependency':
            char=next(iter({model.dc[i] for i in ids}))
            if char not in singles:singles[char]=single_character(model,char,ids)
        rows.append({**item,'baseline_remaining':row['remaining'],'initial_excluded':initial,
            'score':score,'attempt':attempted.get(number),'cycles':cycles,'remaining':ids,
            'excluded':ending is not None,'dependency':ending})
    pp,pa=check_plan('profile',items)
    assert pp['jobs']==[p['number'] for p in profiles]
    assert all(a['status']=='completed' for a in pa)
    ranking=read('ranking-plan.json')
    ordered=sorted(profiles,key=lambda p:(-p['score'],p['number']))
    assert ordered==ranking['all_profiles']
    size=min(4,len(ordered)//2);high=ordered[:size]
    used={p['number'] for p in high}
    low=sorted([p for p in profiles if p['number'] not in used],key=lambda p:(p['score'],p['number']))[:size]
    assert high==ranking['high'] and low==ranking['low_control']
    assert ranking['group_size']==size
    assert ranking['comparison_is_informative']==bool(high and low and
        min(p['score'] for p in high)>max(p['score'] for p in low))
    assert fp['jobs']==[p['number'] for p in high+low]
    assert fp['seconds_per_job']==ranking['follow_seconds_per_family']
    expected_remaining=[p['number'] for p in ordered if p['number'] not in fp['jobs']]
    if not comparison and (h.OUT/'remaining-plan.json').exists():
        assert remaining_jobs==expected_remaining
    by_number={r['batch_number']:r for r in rows}
    summary={label:{'families':[p['number'] for p in group],
        'excluded':sum(by_number[p['number']]['excluded'] for p in group)}
        for label,group in [('high',high),('low_control',low)]}
    prefix='independent-' if independent else ''
    checkpoint_path=h.OUT/f'comparison-{prefix}validation.json'
    checkpoint=None
    if not comparison and checkpoint_path.exists():
        checkpoint=read(checkpoint_path.name)
        assert checkpoint['status']=='PASS' and checkpoint['comparison']==summary
        assert checkpoint['independent_physical_polynomials']==independent
        assert checkpoint['excluded']==sum(r['excluded'] for r in checkpoint['families'])
        assert checkpoint['unresolved']==[r['batch_number'] for r in checkpoint['families'] if not r['excluded']]
        assert len(checkpoint['families'])==len(rows)
        for before,after in zip(checkpoint['families'],rows):
            assert before['batch_number']==after['batch_number']
            if before['batch_number'] not in remaining_jobs:assert before==after
            else:
                assert before['attempt'] is None and not before['cycles']
                assert before['remaining']==before['baseline_remaining']
                for key in items[0].keys():assert before[key]==after[key]
    elif not comparison and remaining_jobs:
        raise AssertionError('Continuation requires the preserved prospective checkpoint')
    result={'status':'PASS','independent_physical_polynomials':independent,
        'checks':dict(counts),'baseline_excluded':sum(r['initial_excluded'] for r in rows),
        'excluded':sum(r['excluded'] for r in rows),
        'unresolved':[r['batch_number'] for r in rows if not r['excluded']],
        'families':rows,'comparison':summary,'pair_dependency':dependency,
        'comparison_is_informative':ranking['comparison_is_informative'],
        'single_dependencies':list(singles.values()),
        'comparison_checkpoint_excluded':checkpoint['excluded'] if checkpoint else None,
        'seconds':time.perf_counter()-start,
        'scope':'132 new complete retained X0/X1 extensions; added-character finite Koszul homology ranking, not a causal efficacy proof or HasCertificate.'}
    destination=checkpoint_path if comparison else h.OUT/f'{prefix}validation.json'
    if comparison and destination.exists():
        old=read(destination.name)
        # Preserve the first checkpoint byte for byte, including its timing.
        assert {k:v for k,v in old.items() if k!='seconds'}=={k:v for k,v in result.items() if k!='seconds'}
    else:destination.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k not in ['families','single_dependencies']},indent=2),flush=True)


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--independent',action='store_true')
    parser.add_argument('--comparison',action='store_true')
    args=parser.parse_args();check(args.independent,args.comparison)

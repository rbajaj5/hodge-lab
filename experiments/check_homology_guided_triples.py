"""Replay physical necessities, homology ranking, and every attempted continuation."""
from collections import Counter
from fractions import Fraction as Q
import argparse,copy,json,time
import homology_guided_triples as h
from check_x1y1_extensions import replay_stages
from check_quartic_exclusions import y0_y1,single_character


def baseline(model,item,row):
    for k,v in item.items():assert row[k]==v
    assert row['sources']==h.e.source_hashes() and row['completed']
    ids=item['basis_indices'];counts=Counter()
    for stage in row['stages']:
        assert stage['active']==ids and not h.terminal(model,ids)
        counts.update(h.e.check_physical(model,stage));eq=[h.cert.decode(r['polynomial']) for r in stage['necessary']]
        span=h.t.base.Elimination()
        for p in eq:span.insert(dict(p))
        assert len(span.basis)==stage['rank'];removed=[]
        for c in stage['squares']:
            i=c['coordinate'];assert i in ids and i not in removed
            assert all(not m for _,m,_ in c['products'])
            assert h.e.expand_products(eq,c['products'])=={(i,i):Q(1)}
            removed.append(i);counts['square_identities']+=1
        if stage['squares']:
            bad=copy.deepcopy(stage['squares'][0]);bad['products'][0][2]=str(Q(bad['products'][0][2])+1)
            assert h.e.expand_products(eq,bad['products'])!={(bad['coordinate'],)*2:Q(1)}
            counts['altered_squares_rejected']+=1
        ids=[i for i in ids if i not in removed]
    assert row['remaining']==ids and row['status']==(h.terminal(model,ids) or 'unresolved_squares')
    return ids,counts


def profile(model,number,row):
    source=h.OUT/f'baseline-{number:03d}.json.gz';p=h.q.load(h.OUT/f'profile-{number:03d}.json.gz')
    assert p['completed'] and p['source_sha256']==h.digest(source) and p['batch_number']==number
    stage=row['stages'][-1];assert stage['active']==row['remaining']
    eq=[h.cert.decode(r['polynomial']) for r in stage['necessary']];records=[]
    for char in sorted({model.dc[i] for i in row['remaining']}):
        ids=[i for i in row['remaining'] if model.dc[i]==char]
        chosen=[j for j,r in enumerate(eq) if all(i in ids for m in r for i in m)]
        small=[eq[j] for j in chosen]
        maps=[h.kh.complex_at(small,ids,d) for d in [3,4]] if small else []
        # Cross-check d1 ranks using the earlier elimination implementation.
        for d,r in zip([3,4],maps):
            _,cols=h.e.mac_map(small,ids,d);span=h.t.base.Elimination()
            for c in cols:span.insert(dict(c))
            assert len(span.basis)==r['differential_ranks'][0]
        records.append({'character':list(char),'ids':ids,'equation_indices':chosen,'homology':maps})
    assert records==p['blocks']
    assert p['score']==sum(b['homology'][1]['homology'][1] for b in records if b['homology'])
    assert p['score_degree3']==sum(b['homology'][0]['homology'][1] for b in records if b['homology'])
    return p


def follow(model,item,ids,attempt,counts):
    number=item['batch_number'];path=h.OUT/f'follow-{number:03d}.json.gz'
    if not path.exists():
        assert attempt['status'] in ['timeout','error'];return ids,[]
    p=h.q.load(path);assert p['source_sha256']==h.digest(h.OUT/f'baseline-{number:03d}.json.gz')
    assert p['batch_number']==number;cycles=[]
    for cycle,stage in enumerate(p['cycles']):
        assert stage['before']==ids and stage['block_file']==f'rebuild-{number:03d}-{cycle}.json.gz'
        blockpath=h.OUT/stage['block_file'];assert h.digest(blockpath)==stage['block_sha256']
        r=h.q.load(blockpath);assert r['starting_indices']==ids and r['completed'] and r['sources']==h.e.source_hashes()
        for k,v in item.items():assert r[k]==v
        ids,zeros,_,cc=replay_stages(model,r,ids,finish=h.terminal);counts.update(cc)
        assert r['status']==(h.terminal(model,ids) or 'unresolved_bounded_search')
        detail={'before':stage['before'],'block_zeros':zeros,'after_blocks':ids[:],'charts':[]}
        if 'system' in stage:
            desc,eq=h.build(model,item,ids);assert desc==stage['system']
            assert [c['pivot'] for c in stage['charts']]==desc['pivots'][:len(stage['charts'])]
            if p['completed'] or 'removed' in stage:assert [c['pivot'] for c in stage['charts']]==desc['pivots']
            nv=len(ids)+len(desc['Koszul_indices']);removed=[]
            for c in stage['charts']:
                counts['chart_inferences']+=h.cert.verify_chart(eq,nv,c);counts['charts']+=1
                detail['charts'].append({'raw':ids[c['pivot']],'excluded':c['excluded']})
                if c['excluded']:removed.append(ids[c['pivot']]);counts['excluded_charts']+=1
            if 'removed' in stage:
                assert stage['removed']==removed;ids=[i for i in ids if i not in removed]
        detail['after']=ids[:];cycles.append(detail)
    assert p['remaining']==ids
    if p['completed']:assert p['status']==(h.terminal(model,ids) or 'unresolved')
    if attempt['status']=='completed':assert p['completed'] and attempt['exit_code']==0
    return ids,cycles


def check(independent=False):
    start=time.perf_counter()
    if independent:
        from check_degree7_triples import IndependentModel
        model=IndependentModel()
    else:model=h.t.Model()
    items=h.selection(model);plan=json.loads((h.OUT/'baseline-plan.json').read_text(encoding='utf-8'))
    assert plan['selection']==items and plan['sources']==h.e.source_hashes()
    attempts=json.loads((h.OUT/'baseline-attempts.json').read_text());assert len(attempts)==2
    assert all(r['status']=='completed' and r['exit_code']==0 for r in attempts)
    # The archived Y0/Y1 certificate has eleven directions, not all fourteen.
    # Explicitly replay the missing reduction before invoking that dependency.
    import check_quartic_exclusions as qc
    old=h.q.load(qc.q.OUT/'y0-y1-closure.json.gz')['ids'];full=sorted(i for c in h.ANCHOR for i in model.groups[c])
    b=h.q.load(h.OUT/'full-pair-binding.json.gz');assert b['basis_indices']==full and b['completed'] and b['sources']==h.e.source_hashes()
    finish=lambda model,ids:'prior_pair_dependency' if set(ids)<=set(old) else None
    residual,zeros,_,counts=replay_stages(model,b,full,finish=finish)
    assert b['status']==finish(model,residual)=='prior_pair_dependency'
    dependency={'full_pair_basis':full,'extra_directions_removed':zeros,'prior_proof':y0_y1(model,residual)}
    profiles=[];rows=[];singles={}
    fp=json.loads((h.OUT/'follow-plan.json').read_text());fa=json.loads((h.OUT/'follow-attempts.json').read_text())
    assert fp['selection']==items and fp['sources']==h.e.source_hashes() and [a['job'] for a in fa]==fp['jobs']
    attempted={r['job']:r for r in fa}
    rp=json.loads((h.OUT/'remaining-plan.json').read_text());ra=json.loads((h.OUT/'remaining-attempts.json').read_text())
    assert rp['selection']==items and rp['sources']==h.e.source_hashes() and [a['job'] for a in ra]==rp['jobs']
    assert not set(attempted)&set(rp['jobs']) and rp['seconds_per_job']==fp['seconds_per_job']==120
    attempted.update({r['job']:r for r in ra})
    for item in items:
        n=item['batch_number'];r=h.q.load(h.OUT/f'baseline-{n:03d}.json.gz')
        ids,cc=baseline(model,item,r);counts.update(cc);initial=h.terminal(model,ids) is not None
        score=None;cycles=[]
        if not initial:
            p=profile(model,n,r);profiles.append({'number':n,'score':p['score'],'profile_sha256':h.digest(h.OUT/f'profile-{n:03d}.json.gz')});score=p['score']
            counts['homology_complexes']+=sum(len(b['homology']) for b in p['blocks'])
        if n in attempted:ids,cycles=follow(model,item,ids,attempted[n],counts)
        ending=h.terminal(model,ids)
        if ending=='single_character_dependency':
            char=next(iter({model.dc[i] for i in ids}))
            if char not in singles:singles[char]=single_character(model,char,ids)
        rows.append({**item,'baseline_remaining':r['remaining'],'initial_excluded':initial,'score':score,
            'attempt':attempted.get(n),'cycles':cycles,'remaining':ids,'excluded':ending is not None,'dependency':ending})
    ranking=json.loads((h.OUT/'ranking-plan.json').read_text())
    ordered=sorted(profiles,key=lambda p:(-p['score'],p['number']));assert ordered==ranking['all_profiles']
    high=ordered[:min(4,len(ordered))];used={r['number'] for r in high}
    low=sorted([r for r in profiles if r['number'] not in used],key=lambda r:(r['score'],r['number']))[:4]
    assert high==ranking['high'] and low==ranking['low_control']
    assert fp['jobs']==[r['number'] for r in high+low] and fp['seconds_per_job']==ranking['follow_seconds_per_family']
    assert rp['jobs']==[r['number'] for r in ordered if r['number'] not in fp['jobs']]
    pp=json.loads((h.OUT/'profile-plan.json').read_text());pa=json.loads((h.OUT/'profile-attempts.json').read_text())
    assert pp['jobs']==[r['number'] for r in profiles]==[a['job'] for a in pa]
    assert pp['selection']==items and pp['sources']==h.e.source_hashes()
    assert all(a['status']=='completed' and a['exit_code']==0 for a in pa)
    summary={label:{'families':[r['number'] for r in group],
        'excluded':sum(next(s['excluded'] for s in rows if s['batch_number']==r['number']) for r in group)}
        for label,group in [('high',high),('low_control',low)]}
    # Keep the first eight prospective outcomes separately from the continuation.
    old=json.loads((h.OUT/('comparison-'+('independent-' if independent else '')+'validation.json')).read_text())
    assert old['status']=='PASS' and old['excluded']==125 and old['comparison']==summary
    assert old['unresolved']==sorted(rp['jobs'])
    for before,after in zip(old['families'],rows):
        if before['batch_number'] not in rp['jobs']:assert before==after
    result={'status':'PASS','independent_physical_polynomials':independent,'checks':dict(counts),
        'baseline_excluded':sum(r['initial_excluded'] for r in rows),'excluded':sum(r['excluded'] for r in rows),
        'unresolved':[r['batch_number'] for r in rows if not r['excluded']],
        'families':rows,'comparison':summary,'pair_dependency':dependency,'single_dependencies':list(singles.values()),
        'seconds':time.perf_counter()-start,'scope':'132 new complete retained Y0/Y1 extensions; bounded prospective homology ranking, not a causal efficacy proof or HasCertificate.'}
    (h.OUT/(('independent-' if independent else '')+'validation.json')).write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='families'},indent=2),flush=True)


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--independent',action='store_true');check(p.parse_args().independent)

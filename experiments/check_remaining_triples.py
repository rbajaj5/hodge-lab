"""Source-only exact replay of the last-two selected-family continuation."""
from collections import Counter
from fractions import Fraction as Q
import argparse,copy,json,time
import remaining_triples_shared as s
from check_eleven_quartic import pair30_binding
e=s.e;q=s.q;cert=s.cert


def make(independent):
    if independent:
        from check_degree7_triples import IndependentModel
        return IndependentModel()
    return e.t.Model()


def initial(model,number):
    source=s.x.source()[number];before=next(f for f in e.original() if f['number']==number)
    counts=Counter(e.t.verify_family(model,before));ids=before['remaining']
    assert source['initial_active']==ids and source['characters']==before['characters']
    for stage in source['stages']:
        assert stage['active']==ids;counts.update(e.check_physical(model,stage))
        eq=[cert.decode(r['polynomial']) for r in stage['necessary']];removed=set()
        for strand in stage['strands']:
            for proof in strand['vanishings']:
                i=proof['coordinate'];assert i in ids
                assert e.expand_products(eq,proof['products'])=={(i,)*proof['power']:Q(1)}
                removed.add(i);counts['inherited_powers']+=1
        assert sorted(removed)==stage['removed'];ids=[i for i in ids if i not in removed]
    assert ids==source['remaining'];return counts


def replay_charts(model,number,packet,ids=None):
    desc,eq=s.construct(model,number,ids);assert desc==packet['system']
    assert packet['completed'] and [p['pivot'] for p in packet['charts']]==desc['pivots']
    n=len(desc['ids'])+len(desc['Koszul_indices']);count=0
    for proof in packet['charts']:count+=cert.verify_chart(eq,n,proof)
    return {'inferences':count,'equations':len(eq),'numerator_parameters':len(desc['Koszul_indices']),
        'stabilizer_order':desc['stabilizer_order'],
        'charts':[{'pivot_raw':desc['ids'][p['pivot']],'excluded':p['excluded'],
                   'retained_coordinates':p['remaining_variables'],
                   'stage_retained_coordinates':[len(v['active']) for v in p['stages']]+[p['remaining_variables']]}
                  for p in packet['charts']]}


def check(independent=False):
    start=time.perf_counter();results=[];allcounts=Counter()
    plan=json.loads((s.OUT/'plan.json').read_text());attempts=json.loads((s.OUT/'attempts.json').read_text())
    assert plan['source_sha256']==q.source_sha()
    assert [(r['kind'],r['number'],r['limit_seconds']) for r in attempts]==[(r['kind'],r['number'],r['limit_seconds']) for r in plan['jobs']]
    assert all(r['status']=='completed' and r['returncode']==0 for r in attempts)
    for number in s.NUMBERS:
        model=make(independent);allcounts.update(initial(model,number))
        source=s.x.source()[number];stage=source['stages'][-1]
        original_eq=[cert.decode(r['polynomial']) for r in stage['necessary']]
        packet=q.load(s.OUT/f'family-{number}.json.gz');assert packet['source_sha256']==q.source_sha()
        original_shared=replay_charts(model,number,packet)
        forced=[r['pivot_raw'] for r in original_shared['charts'] if r['excluded']]
        assert forced==([56] if number==17 else [])
        oldblock=q.load(s.OUT/f'block-{number}.json.gz');assert oldblock['source_sha256']==q.source_sha()
        oldids=[i for i in stage['active'] if model.dc[i] not in s.RESIDUAL]
        assert oldids==oldblock['ids']
        selected=[j for j,p in enumerate(original_eq) if all(i in oldids for m in p for i in m)]
        assert oldblock['equation_indices']==selected
        assert [r['degree'] for r in oldblock['strands']]==[5,6]
        for strand in oldblock['strands']:
            e.check_strand([original_eq[j] for j in selected],oldids,strand)
            assert not strand['vanishings']
        rebuilt=q.load(s.OUT/f'rebuilt-{number}.json.gz');assert rebuilt['source_sha256']==q.source_sha()
        if number==151:
            square=rebuilt['linear_square'];L=cert.decode(square['linear'])
            assert L=={(115,):Q(3),(133,):Q(-6),(234,):Q(1),(285,):Q(1),(288,):Q(1)}
            assert e.expand_products(original_eq,square['products'])==cert.product(L,L)
            change=rebuilt['change'];maps={change['eliminated']:{(i,):Q(a) for i,a in change['replacement']}}
            assert not cert.substitute(L,maps)
            broken=copy.deepcopy(square['products']);broken[0][2]=str(Q(broken[0][2])+1)
            assert e.expand_products(original_eq,broken)!=cert.product(L,L)
            allcounts['linear_square_identities']+=1;allcounts['mutations_rejected']+=1
        # A fresh instance is essential: cached physical columns from the old
        # basis must not survive the explicitly checked basis substitution.
        rebased=make(independent);ids,change=s.rebase(rebased,number)
        assert rebuilt['active']==ids and rebuilt['change']==change
        for i in ids:
            D,N=model.pairs[i];D2,N2=rebased.pairs[i]
            a=dict((j,Q(v)) for j,v in change['replacement']).get(i,Q(0))
            E,P=model.pairs[change['eliminated']]
            assert D2==e.t.base.padd(D,E,a)
            assert N2==[e.t.base.padd(U,V,a) for U,V in zip(N,P)]
        allcounts.update(e.check_physical(rebased,rebuilt))
        eq=[cert.decode(r['polynomial']) for r in rebuilt['necessary']]
        block=rebuilt['block'];small_ids=[i for i in ids if rebased.dc[i] not in s.RESIDUAL]
        assert block['active']==small_ids
        selected=[j for j,p in enumerate(eq) if all(i in small_ids for m in p for i in m)]
        assert block['equation_indices']==selected
        assert [r['degree'] for r in block['strands']]==[2,3,4,5,6]
        for strand in block['strands']:e.check_strand([eq[j] for j in selected],small_ids,strand)
        powers=block['strands'][-1]['vanishings'];closure=None;newshared=None
        if number==17:
            assert [p['coordinate'] for p in powers]==small_ids
            for proof in powers:
                mapped=[[selected[j],m,c] for j,m,c in proof['products']]
                target={(proof['coordinate'],)*6:Q(1)}
                assert e.expand_products(eq,mapped)==target
                broken=copy.deepcopy(mapped);broken[0][2]=str(Q(broken[0][2])+1)
                assert e.expand_products(eq,broken)!=target
                allcounts['sixth_power_identities']+=1;allcounts['mutations_rejected']+=1
            remaining=[i for i in ids if i not in small_ids]
            assert {model.dc[i] for i in remaining}==s.RESIDUAL
            closure=pair30_binding(model,remaining,s.OUT/'pair30')
            # Also corrupt the actual normalized-chart contradiction witness.
            broken=copy.deepcopy(packet)
            item=next(v for p in broken['charts'] if p['excluded'] for st in p['stages'] for v in st['inferences'] if v['kind']=='contradiction')
            item['witness']['polynomial']=[[[],'2']]
            try:replay_charts(model,number,broken)
            except AssertionError:allcounts['mutations_rejected']+=1
            else:raise AssertionError('Corrupted chart contradiction accepted')
        else:
            assert not powers
            newshared=replay_charts(rebased,number,rebuilt['shared'],ids)
            assert not any(p['excluded'] for p in newshared['charts'])
        def summary(r):return {k:r[k] for k in ['degree','domain','codomain','rank','kernel','quotient_dimension']}
        row={'number':number,'excluded':closure is not None,'original_shared':original_shared,
            'original_complementary_block':[summary(r) for r in oldblock['strands']],
            'eliminated_coordinate':change['eliminated'],'replacement':change['replacement'],
            'rebuilt_variables':len(ids),'rebuilt_quadratics':len(eq),
            'block_variables':len(small_ids),'block_quadratics':len(selected),
            'rebuilt_block':[summary(r) for r in block['strands']],
            'power_zeros':[p['coordinate'] for p in powers], 'closure':closure,'rebuilt_shared':newshared}
        results.append(row);print(number,'excluded' if closure else 'reduced but unresolved',flush=True)
    report={'status':'PASS','independent_physical_polynomials':independent,'families':results,
        'checks':dict(allcounts),'source_sha256':q.source_sha(),'seconds':time.perf_counter()-start,
        'scope':'Family 17 excluded; family 151 reduced by one linear relation, still unresolved. Selected coverage 151/152; holdout unsolved.'}
    name=('independent-' if independent else '')+'validation.json'
    (s.OUT/name).write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='families'},indent=2),flush=True)


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--independent',action='store_true')
    check(p.parse_args().independent)

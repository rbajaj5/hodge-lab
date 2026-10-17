"""Replay the new extension batch, including every used residual dependency."""
from collections import Counter
from fractions import Fraction as Q
import argparse,copy,json,time
import x1y1_extensions as x
from check_eleven_quartic import pair30_binding
from check_quartic_exclusions import single_character
e=x.e;q=x.q;t=x.t;cert=x.cert


def replay_stages(model,row,starting,finish=None):
    finish=x.terminal if finish is None else finish
    counts=Counter();ids=starting[:];zeros=[];charts=[];mutated=False
    for stage in row['stages']:
        assert stage['active']==ids and not finish(model,ids)
        counts.update(e.check_physical(model,stage));eq=[cert.decode(r['polynomial']) for r in stage['necessary']]
        span=t.base.Elimination()
        for p in eq:span.insert(dict(p))
        assert len(span.basis)==stage['quadratic_rank'];removed=set()
        for proof in stage['squares']:
            i=proof['coordinate'];assert i in ids and proof['power']==2
            assert all(not mon for _,mon,_ in proof['products'])
            assert e.expand_products(eq,proof['products'])=={(i,i):Q(1)}
            removed.add(i);counts['square_identities']+=1
            if not mutated:
                broken=copy.deepcopy(proof['products']);broken[0][2]=str(Q(broken[0][2])+1)
                assert e.expand_products(eq,broken)!={(i,i):Q(1)}
                counts['mutations_rejected']+=1;mutated=True
        assert bool(stage['blocks'])==(not bool(stage['squares']))
        if stage['blocks']:assert [tuple(b['character']) for b in stage['blocks']]==sorted({model.dc[i] for i in ids})
        for block in stage['blocks']:
            small_ids=[i for i in ids if model.dc[i]==tuple(block['character'])]
            assert block['active']==small_ids
            indices=[j for j,p in enumerate(eq) if all(i in small_ids for m in p for i in m)]
            assert block['equation_indices']==indices
            small=[eq[j] for j in indices]
            assert [r['degree'] for r in block['strands']] in [[3],[3,4]]
            for record in block['strands']:
                e.check_strand(small,small_ids,record);counts['graded_maps']+=1
                for proof in record['vanishings']:
                    removed.add(proof['coordinate']);counts['higher_power_identities']+=1
                    if not mutated:
                        broken=copy.deepcopy(proof['products']);broken[0][2]=str(Q(broken[0][2])+1)
                        assert e.expand_products(small,broken)!={(proof['coordinate'],)*proof['power']:Q(1)}
                        counts['mutations_rejected']+=1;mutated=True
            charts.append({'stage':len(charts),'character':block['character'],'variables':len(small_ids),'equations':len(small),
                'maps':[{k:r[k] for k in ['degree','domain','codomain','rank','kernel','quotient_dimension']} for r in block['strands']],
                'zeros':[r['coordinate'] for r in block['strands'][-1]['vanishings']]})
        assert stage['removed']==sorted(removed)
        zeros+=sorted(removed);ids=[i for i in ids if i not in removed]
    assert row['remaining']==ids
    return ids,zeros,charts,counts


def check(independent=False):
    start=time.perf_counter()
    if independent:
        from check_degree7_triples import IndependentModel
        model=IndependentModel()
    else:model=t.Model()
    plan=json.loads((x.OUT/'plan.json').read_text());attempts=json.loads((x.OUT/'attempts.json').read_text())
    items=x.selection(model);assert plan['sources']==e.source_hashes() and plan['new_selection']==items
    assert plan['max_block_degree']==4 and plan['anchor']==sorted(map(list,x.ANCHOR))
    assert [r['chunk'] for r in attempts]==[0,1]
    counts=Counter();families=[];closure=None;single={}
    for item in items:
        path=x.OUT/f"family-{item['batch_number']:03d}.json.gz"
        if not path.exists():
            assert attempts[(item['batch_number']-1)%2]['status']=='timeout'
            families.append({**item,'status':'not_started','excluded':False});continue
        row=q.load(path)
        for key,value in item.items():assert row[key]==value
        assert row['sources']==plan['sources'];ids=item['basis_indices'][:];zeros=[];charts=[];mutated=False
        ids,zeros,charts,newcounts=replay_stages(model,row,ids);counts.update(newcounts)
        assert row['remaining']==ids
        expected=x.terminal(model,ids)
        if row['completed']:assert row['status']==(expected or 'unresolved_bounded_search')
        else:assert row['status']=='running' and attempts[(item['batch_number']-1)%2]['status']=='timeout'
        dependency=None
        if expected=='pair30_dependency':
            if closure is None:closure=pair30_binding(model,sorted(x.PAIR_IDS),x.OUT/'pair30')
            dependency='fqlx_pair30'
        elif expected=='single_character_dependency':
            char=next(iter({model.dc[i] for i in ids}))
            if char not in single:single[char]=single_character(model,char,ids)
            dependency='single_character'
        excluded=expected is not None
        families.append({**item,'status':row['status'],'completed':row['completed'],'excluded':excluded,
            'remaining':ids,'zeros':zeros,'stages':len(row['stages']),'dependency':dependency,'blocks':charts,
            'seconds':row['seconds'] if 'seconds' in row else None})
    statuses=Counter(r['status'] for r in families)
    report={'status':'PASS','independent_physical_polynomials':independent,'checks':dict(counts),
        'families':families,'statuses':dict(statuses),'excluded':sum(r['excluded'] for r in families),
        'unresolved':[r['batch_number'] for r in families if not r['excluded']],
        'pair30_binding':closure,'single_character_bindings':list(single.values()),'seconds':time.perf_counter()-start,
        'scope':'132 additional full three-character eigenspace families, disjoint from the preceding 152. Holdout remains unsolved.'}
    (x.OUT/(('independent-' if independent else '')+'validation.json')).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['families','single_character_bindings']},indent=2),flush=True)


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--independent',action='store_true');check(p.parse_args().independent)

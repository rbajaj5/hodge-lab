"""Replay polynomial-multiplier identities against the fixed physical target."""
from collections import Counter
from fractions import Fraction as Q
import argparse,copy,hashlib,json,time
import family151_multipliers as f
import check_remaining_triples as prior
e=f.e;q=f.q;cert=f.cert;syz=f.syz


def setup(independent):
    old=prior.make(independent);counts=prior.initial(old,151)
    source=q.load(f.SOURCE);stage=f.s.x.source()[151]['stages'][-1]
    equations=[cert.decode(r['polynomial']) for r in stage['necessary']]
    L=cert.decode(source['linear_square']['linear'])
    assert e.expand_products(equations,source['linear_square']['products'])==cert.product(L,L)
    changes={133:{(i,):Q(c) for i,c in source['change']['replacement']}}
    assert not cert.substitute(L,changes)
    model=prior.make(independent);ids,change=f.s.rebase(model,151)
    assert ids==source['active'] and change==source['change']
    for i in ids:
        a=dict((j,Q(v)) for j,v in change['replacement']).get(i,Q(0))
        D,N=old.pairs[i];E,P=old.pairs[133]
        assert model.pairs[i]==(e.t.base.padd(D,E,a),[e.t.base.padd(U,V,a) for U,V in zip(N,P)])
    desc,rows=f.s.construct(model,151,ids)
    assert desc==source['shared']['system']
    return desc,rows,counts


def check(independent=False):
    start=time.perf_counter();desc,physical,counts=setup(independent);cases=[]
    plan=json.loads((f.OUT/'plan.json').read_text());attempts=json.loads((f.OUT/'attempts.json').read_text())
    assert plan['cases']==f.CASES and [r['raw_pivot'] for r in attempts]==f.CASES
    assert plan['source_sha256']==hashlib.sha256(f.SOURCE.read_bytes()).hexdigest()
    nD=len(desc['ids'])
    for raw,attempt in zip(f.CASES,attempts):
        packet=q.load(f.OUT/f'{f.label(raw)}.json.gz');pivot=None if raw is None else desc['ids'].index(raw)
        assert packet['family']==151 and packet['raw_pivot']==raw and packet['pivot']==pivot
        assert packet['source_sha256']==plan['source_sha256'] and packet['system']==desc
        variables=[i for i in range(nD) if i!=pivot];assert packet['variables']==variables
        rows=physical if pivot is None else [cert.substitute(p,{pivot:{():Q(1)}}) for p in physical]
        requested=[[]]+[[i] for i in variables];done=packet['completed_multipliers']
        assert done==requested[:len(done)] and done
        assert packet['completed']==(done==requested)
        assert (attempt['status']=='completed')==packet['completed'] and attempt['status'] in ['completed','timeout']
        assert [c['multiplier'] for c in packet['checkpoints']]==done
        baseline,rank=syz.necessary_relations(rows,nD,[()]);assert baseline==packet['baseline']
        assert rank==packet['checkpoints'][0]['equation_rank']
        for relation in baseline+packet['relations']:
            counts['equation_products']+=syz.verify_relation(rows,nD,variables,relation)
            counts['identities']+=1
            assert all(mon in done for _,mon,_ in relation['products'])
        old,new,total=syz.select_new(baseline,packet['relations'],variables)
        assert new==packet['selected_new']
        last=packet['checkpoints'][-1]
        assert (old,len(new),total)==(last['baseline_multiple_rank'],last['new_relations'],last['combined_relation_rank'])
        # Verify independence of the exported denominator relations themselves.
        span=e.t.base.Elimination()
        for r in packet['relations']:assert span.insert(cert.decode(r['polynomial'])) is None
        assert len(span.basis)==last['relations']
        broken=copy.deepcopy(packet['relations'][new[0] if new else 0]);broken['products'][0][2]=str(Q(broken['products'][0][2])+1)
        try:syz.verify_relation(rows,nD,variables,broken)
        except AssertionError:counts['mutations_rejected']+=1
        else:raise AssertionError('Altered equation multiplier accepted')
        cases.append({'raw_pivot':raw,'completed':packet['completed'],'completed_multiplier_blocks':len(done),
            'requested_multiplier_blocks':len(requested),'constant_relations':len(baseline),
            'exported_relation_rank':len(packet['relations']),'baseline_multiple_rank':old,
            'new_relation_rank':len(new),'combined_relation_rank':total})
        print(f.label(raw),'verified',len(packet['relations']),'relations;',len(new),'new',flush=True)
    result={'status':'PASS','independent_physical_polynomials':independent,'checks':dict(counts),'cases':cases,
        'source_sha256':plan['source_sha256'],'seconds':time.perf_counter()-start,
        'limits':'Exact identities and independence are replayed; expanded equation ranks and intermediate checkpoint counts are discovery telemetry. No completeness or family exclusion follows from a timeout.'}
    path=f.OUT/(('independent-' if independent else '')+'validation.json')
    path.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))


def follow(independent=False):
    start=time.perf_counter();desc,physical,counts=setup(independent);cases=[];nD=len(desc['ids'])
    plan=json.loads((f.OUT/'follow-plan.json').read_text());attempts=json.loads((f.OUT/'follow-attempts.json').read_text())
    assert plan['cases']==f.CASES[1:] and plan['max_degree']==4
    assert [r['raw_pivot'] for r in attempts]==f.CASES[1:]
    for raw,attempt in zip(f.CASES[1:],attempts):
        path=f.OUT/f'{raw}.json.gz';packet=q.load(path);result=q.load(f.OUT/f'follow-{raw}.json.gz')
        assert result['source_sha256']==hashlib.sha256(path.read_bytes()).hexdigest()
        assert result['max_degree']==4 and result['raw_pivot']==raw
        assert attempt['status'] in ['completed','timeout'] and result['completed']==(attempt['status']=='completed')
        pivot=desc['ids'].index(raw);variables=[i for i in range(nD) if i!=pivot]
        rows=[cert.substitute(p,{pivot:{():Q(1)}}) for p in physical]
        needed=packet['baseline']+[packet['relations'][j] for j in packet['selected_new']]
        for r in needed:counts['relation_products']+=syz.verify_relation(rows,nD,variables,r)
        necessary=[cert.decode(r['polynomial']) for r in needed]
        proof=result['denominator_chart'];assert proof['pivot']==pivot
        counts['chart_inferences']+=cert.verify_chart(necessary,nD,proof)
        maps=syz.chart_maps(nD,pivot,proof);current=[cert.substitute(p,maps) for p in necessary]
        excluded=proof['excluded'];removed=set()
        for claim in result['claims']:
            assert not excluded
            actual=e.expand_products(current,claim['products'])
            assert actual==cert.decode(claim['polynomial'])
            for j,m,c in claim['products']:
                assert 0<=j<len(current) and all(i in variables for i in m)
                assert max(map(len,current[j]))+len(m)<=result['claim_degree']<=4
            if claim['kind']=='constant':assert actual=={():Q(1)};excluded=True
            else:
                assert claim['kind']=='power';i=claim['coordinate'];power=claim['power']
                assert i in variables and i not in removed and 1<=power<=4
                assert actual=={(i,)*power:Q(1)};removed.add(i)
            counts['power_or_constant_identities']+=1
        if result.get('physical_closure'):
            assert not excluded
            maps={i:cert.substitute(p,{j:{} for j in removed}) for i,p in maps.items()}
            proof=result['physical_closure'];assert proof['pivot']==pivot
            counts['chart_inferences']+=cert.verify_chart([cert.substitute(p,maps) for p in rows],nD+len(desc['Koszul_indices']),proof)
            excluded=proof['excluded']
        assert excluded==result['excluded']
        cases.append({'raw_pivot':raw,'completed':result['completed'],'excluded':excluded,
            'coordinate_zeros':[desc['ids'][i] for i in sorted(removed)],'completed_degrees':[r['degree'] for r in result['attempts']]})
    report={'status':'PASS','independent_physical_polynomials':independent,'checks':dict(counts),'cases':cases,
        'seconds':time.perf_counter()-start,'scope':'Verified consequences only; a failed bounded search is not a proof of consistency.'}
    (f.OUT/(('independent-' if independent else '')+'follow-validation.json')).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--independent',action='store_true');p.add_argument('--follow',action='store_true')
    a=p.parse_args();(follow if a.follow else check)(a.independent)

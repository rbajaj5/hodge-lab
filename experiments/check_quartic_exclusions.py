"""Replay the quartic vanishings and their explicit pair/single-character closures.

This proof checker does not rely on the reported Macaulay ranks. It checks
physical necessities and polynomial identities, then the full shared-numerator
chart proofs and the required previously proved single-character sectors.
"""
from collections import Counter
from fractions import Fraction as Q
from itertools import product,combinations_with_replacement
import argparse,gzip,json,time
import eisenbud_quartic_strand as q
e=q.e


def shared_system(model,ids):
    chars=sorted({model.dc[i] for i in ids});assert 1<=len(chars)<=2
    w=chars[0];delta=e.t.minus(chars[-1],w)
    cyclic={tuple(k*x%6 for x in delta) for k in range(6)}
    group=list(product(range(6),repeat=3))
    subgroup=[g for g in group if sum(x*y for x,y in zip(delta,g))%6==0]
    annihilator={c for c in group if all(sum(x*y for x,y in zip(c,g))%6==0 for g in subgroup)}
    assert cyclic==annihilator and len(cyclic)*len(subgroup)==216
    wanted={e.t.plus(e.t.plus(model.alpha,w),c) for c in cyclic}
    ks=[k for k,K in enumerate(model.fields) if e.t.e1.field_characters(K)<=wanted]
    physical={}
    def append(poly,parameter):
        for m,c in poly.items():
            row=physical.setdefault(m,{})
            assert parameter not in row  # Each physical column is inserted once.
            row[parameter]=c
    for i,j in combinations_with_replacement(range(len(ids)),2):
        append(model.quadratic(ids[i],ids[j]),(i,j))
    for i,raw in enumerate(ids):
        # Inspect all 840 source fields, then retain the entire allowed coset.
        for target in sorted({e.t.plus(model.dc[raw],c) for c in wanted}):
            for k,column in model.corrections(raw,target):
                if k in ks:append(column,(i,len(ids)+ks.index(k)))
    mons=sorted(physical)
    return {'ids':ids,'ks':ks,'physical_monomials':[list(m) for m in mons],
            'equations':[e.t.cert.encode(physical[m]) for m in mons],
            'characters':[list(c) for c in chars],'subgroup_order':len(subgroup)}


def single_character(model,char,remaining):
    with gzip.open(e.ROOT/'results/degree7-characters/certificates.json.gz','rt') as f:packet=json.load(f)
    row=next(r for r in packet['families'] if tuple(r['character'])==char)
    ids=row['denominator_basis_indices'];assert set(remaining)<=set(ids)
    assert ids==model.groups[char]
    system=shared_system(model,ids)
    assert system['ks']==row['Koszul_indices']
    assert system['physical_monomials']==row['physical_monomials']
    assert system['equations']==row['equations']
    eq=[e.t.cert.decode(p) for p in system['equations']];n=len(ids)+len(system['ks'])
    assert [p['pivot'] for p in row['charts']]==list(range(len(ids)))
    count=0
    for proof in row['charts']:
        count+=e.t.cert.verify_chart(eq,n,proof);assert proof['excluded']
    return {'character':list(char),'charts':len(row['charts']),'inferences':count}


def y0_x1(model,remaining):
    import degree7_y0_x1 as pair
    packet=q.load(pair.OUT/'certificate.json.gz');description=packet['system']
    ids=description['denominator_basis_indices'];assert set(remaining)<=set(ids)
    system=shared_system(model,ids)
    assert system['ks']==description['Koszul_indices']
    assert system['physical_monomials']==description['physical_monomials']
    assert system['equations']==description['equations']
    result=pair.verify_proof([e.t.cert.decode(p) for p in system['equations']],description,packet['proof'])
    sector=tuple(result['remaining_character'])
    return {'kind':'previous_Y0_X1_pair','pair_inferences':result['exact_inferences'],
            'single_character':single_character(model,sector,model.groups[sector])}


def y0_y1(model,remaining):
    packet=q.load(q.OUT/'y0-y1-closure.json.gz')
    ids=packet['ids'];assert set(remaining)<=set(ids)
    system=shared_system(model,ids)
    for key in ['ks','physical_monomials','equations']:assert system[key]==packet[key]
    eq=[e.t.cert.decode(p) for p in system['equations']];n=len(ids)+len(system['ks'])
    forced=set();inferences=0
    for stage in packet['stages']:
        assert stage['forced_before']==sorted(forced)
        active=[i for i in range(len(ids)) if i not in forced]
        rows=[e.t.cert.substitute(p,{i:{} for i in forced}) for p in eq]
        assert [p['pivot'] for p in stage['charts']]==active
        for proof in stage['charts']:inferences+=e.t.cert.verify_chart(rows,n,proof)
        new=[p['pivot'] for p in stage['charts'] if p['excluded']]
        assert new==stage['new_zeros'];forced.update(new)
    final=[i for j,i in enumerate(ids) if j not in forced]
    chars={model.dc[i] for i in final};assert chars=={(5,3,0)}
    return {'kind':'replayed_Y0_Y1_pair','forced_in_pair':[ids[i] for i in sorted(forced)],
            'chart_inferences':inferences,'single_character':single_character(model,(5,3,0),final)}


def check(independent=False):
    started=time.perf_counter()
    if independent:
        from check_degree7_triples import IndependentModel
        model=IndependentModel()
    else:model=e.t.Model()
    old={f['number']:f for f in e.original()};counts=Counter();results=[]
    for number,source in q.source().items():
        before=old[number];counts.update(e.t.verify_family(model,before))
        active=before['remaining'];assert source['initial_active']==active
        for stage in source['stages']:
            assert stage['active']==active;counts.update(e.check_physical(model,stage))
            eq=[e.t.cert.decode(p['polynomial']) for p in stage['necessary']]
            removed=set()
            for strand in stage['strands']:
                for proof in strand['vanishings']:
                    i=proof['coordinate'];assert i in active
                    assert e.expand_products(eq,proof['products'])=={(i,)*proof['power']:Q(1)}
                    removed.add(i);counts['inherited_power_identities']+=1
            assert sorted(removed)==stage['removed'];active=[i for i in active if i not in removed]
        assert active==source['remaining']
        packet=q.load(q.OUT/'pure-blocks.json.gz')
        assert packet['source_sha256']==q.source_sha()
        removed=set()
        for block in [b for b in packet['blocks'] if b['number']==number]:
            assert set(block['active'])<=set(active)
            for proof in block['strands'][-1]['vanishings']:
                i=proof['coordinate'];assert i in active and proof['power']==4
                products=[[block['equation_indices'][j],mon,a] for j,mon,a in proof['products']]
                assert e.expand_products(eq,products)=={(i,)*4:Q(1)}
                removed.add(i);counts['quartic_power_identities']+=1
        remaining=[i for i in active if i not in removed]
        chars={model.dc[i] for i in remaining}
        if chars=={(0,1,0),(1,2,3)}:closure=y0_x1(model,remaining)
        elif chars=={(1,2,3),(5,3,0)}:closure=y0_y1(model,remaining)
        elif len(chars)==1:closure={'kind':'single_character','proof':single_character(model,next(iter(chars)),remaining)}
        else:raise AssertionError(('Unproved closure',number,chars))
        results.append({'number':number,'excluded':True,'quartic_zeros':sorted(removed),
                        'remaining_after_quartics':remaining,'remaining_characters':sorted(map(list,chars)),
                        'closure':closure})
        print('excluded family',number,flush=True)
    report={'status':'PASS','independent_physical_polynomials':independent,'families':results,
            'checks':dict(counts),'source_sha256':q.source_sha(),'seconds':time.perf_counter()-started,
            'scope':'Five complete selected triple families modulo the established F*S1 gauge; holdout remains unsolved.'}
    name='exclusions-'+('independent-' if independent else '')+'validation.json'
    (q.OUT/name).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,indent=2),flush=True)


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--independent',action='store_true')
    check(parser.parse_args().independent)

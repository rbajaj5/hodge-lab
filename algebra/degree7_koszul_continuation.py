"""Replay a bounded Koszul-correction syzygy continuation after rank identities.

These are relations of the actual certificate correction map. No assertion
identifies this calculation with a geometric K_{p,q}(X,B;L) vanishing theorem.
"""
from pathlib import Path
from collections import Counter
import argparse, copy, json, time
import degree7_rank_strata as rank
s = rank.s
c = rank.c
OUT = rank.OUT


def leaf_equations(model, family, pivot):
    packet = rank.rb.read(OUT/f'chart-{family}-{pivot}.json.gz')
    rank.check_packet(model, packet)
    desc, rows, _ = rank.seed(model, family, pivot)
    nD = len(desc['basis_indices']); nv = nD+len(desc['Koszul_indices'])
    node = packet['tree']
    while True:
        if 'affine_chart' in node:
            maps = s.chart_maps(nv, pivot, node['affine_chart'])
            rows = [c.substitute(p, maps) for p in rows]
        if node['status'] != 'split':
            break
        assert len(node['children']) == 1
        change = rank.zero_map(c.decode(node['claim']['factors'][0]['linear']), nD)
        rows = [c.substitute(p, change) for p in rows]
        node = node['children'][0]
    assert node['status'] == 'unresolved'
    return desc, rows


def verify_relations(rows, packet):
    nD = len(packet['system']['basis_indices'])
    variables = sorted({i for p in rows for m in p for i in m if i<nD})
    assert variables == packet['variables']
    assert packet['rows'] == [c.encode(p) for p in rows]
    counts = Counter()
    necessary = packet.get('baseline', []) + [packet['relations'][j] for j in packet['selected_new']]
    for relation in necessary:
        counts['physical_products'] += s.verify_relation(rows, nD, variables, relation)
        counts['syzygy_identities'] += 1
    if 'denominator_contradiction' in packet:
        proof = packet['denominator_contradiction']; assert proof['excluded']
        assert proof['pivot'] == packet['pivot']
        counts['chart_inferences'] += c.verify_chart([c.decode(r['polynomial']) for r in necessary], nD, proof)
        excluded = True
    elif 'continuation' in packet:
        counts.update(s.verify_continuation(rows, packet))
        excluded = packet['continuation']['excluded']
    else:
        excluded = False
    return excluded, counts


def verify_first(model, packet):
    assert (packet['family'],packet['pivot']) == (16,11)
    desc, rows = leaf_equations(model,16,11)
    assert packet['system'] == desc
    excluded, counts = verify_relations(rows,packet)
    assert excluded
    return counts


def verify_global137(model):
    linear=json.loads((OUT/'global-linear-identities.json').read_text(encoding='utf-8'))[1]
    rank.check_global(model,linear)
    packet=json.loads((OUT/'family137-global-cubes.json').read_text(encoding='utf-8'))
    desc,rows=s.shared.construct(model,s.shared.read_packet()['families'][136])
    assert packet['system']==desc and packet['linear_dependency']==linear['linear']
    change=rank.zero_map(c.decode(linear['linear']),18)
    assert packet['changes']==rank.rb.encode_maps(change)
    rows=[c.substitute(p,change) for p in rows]
    assert [p['coordinate'] for p in packet['claims']]==[1,9]
    for claim in packet['claims']:
        assert claim['power']==3
        actual={}
        for j,mon,q in claim['products']:
            assert 0<=j<len(rows) and len(mon)==1 and 0<=mon[0]<18
            actual=s.triples.base.padd(actual,c.product(rows[j],{tuple(mon):s.triples.Q(q)}))
        assert actual=={(claim['coordinate'],)*3:s.triples.Q(1)}
    return sum(len(p['products']) for p in packet['claims'])


def verify_refined(model, packet, closed):
    assert packet['family'] == 16 and packet['pivot'] != 11
    assert packet['dependency_closed_chart'] == 11 and 11 in closed
    desc, rows, _ = rank.seed(model,16,packet['pivot'])
    assert desc == packet['system']
    global_packet = json.loads((OUT/'global-linear-identities.json').read_text(encoding='utf-8'))[0]
    rank.check_global(model,global_packet)
    initial = {11:{}, **rank.zero_map(c.decode(global_packet['linear']),18)}
    assert packet['initial_changes'] == rank.rb.encode_maps(initial)
    rows = [c.substitute(p,initial) for p in rows]
    nv=18+len(desc['Koszul_indices']);proof=packet['affine_chart']
    assert proof['pivot'] == packet['pivot']
    counts=Counter(affine_inferences=c.verify_chart(rows,nv,proof))
    if proof['excluded']:
        return True,counts
    maps=s.chart_maps(nv,packet['pivot'],proof)
    rows=[c.substitute(p,maps) for p in rows]
    excluded, extra=verify_relations(rows,packet);counts.update(extra)
    return excluded,counts


def verify137(model, packet, closed):
    assert packet['family'] == 137
    verify_global137(model)
    desc, rows, _ = rank.seed(model,137,packet['pivot'])
    assert desc == packet['system']
    global_packet = json.loads((OUT/'global-linear-identities.json').read_text(encoding='utf-8'))[1]
    initial = {1:{}, 9:{}, **rank.zero_map(c.decode(global_packet['linear']),18)}
    if 'dependency_closed_chart' in packet:
        assert packet['dependency_closed_chart'] == 13 and 13 in closed
        assert packet['pivot'] != 13
        initial[13] = {}
    assert packet['initial_changes'] == rank.rb.encode_maps(initial)
    rows = [c.substitute(p,initial) for p in rows]
    nv=18+len(desc['Koszul_indices']);proof=packet['affine_chart']
    assert proof['pivot'] == packet['pivot']
    counts=Counter(affine_inferences=c.verify_chart(rows,nv,proof))
    if proof['excluded']:
        return True,counts
    maps=s.chart_maps(nv,packet['pivot'],proof)
    rows=[c.substitute(p,maps) for p in rows]
    excluded,extra=verify_relations(rows,packet);counts.update(extra)
    return excluded,counts


def check(independent=False):
    start=time.perf_counter()
    if independent:
        from check_degree7_triples import IndependentModel
        model=IndependentModel()
    else:model=s.triples.Model()
    packet=rank.rb.read(OUT/'koszul-16-11.json.gz')
    first=verify_first(model,packet);closed={11}
    results=[{'family':16,'pivot':11,'excluded':True,**first}]
    manifest=json.loads((OUT/'koszul-manifest.json').read_text(encoding='utf-8'))
    for item in manifest['refinements']:
        refined=rank.rb.read(OUT/item['file'])
        excluded,counts=verify_refined(model,refined,closed)
        results.append({'family':16,'pivot':refined['pivot'],'excluded':excluded,**counts})
        if excluded:closed.add(refined['pivot'])
    assert sorted(closed)==manifest['excluded_family16_pivots']
    assert closed=={7,10,11,12,13}
    desc,_=s.shared.construct(model,s.shared.read_packet()['families'][15])
    assert set(desc['pivots'])==closed
    assert all(model.dc[index] in s.shared.ANCHOR for i,index in enumerate(desc['basis_indices']) if i not in closed)
    products137=verify_global137(model)
    closed137=set()
    for item in manifest['family137_charts']:
        current=rank.rb.read(OUT/item['file'])
        assert current['pivot'] not in closed137
        if current['pivot']==13:
            assert not closed137 and 'dependency_closed_chart' not in current
        else:
            assert current['dependency_closed_chart']==13
        excluded,counts=verify137(model,current,closed137)
        assert excluded
        closed137.add(current['pivot'])
        results.append({'family':137,'pivot':current['pivot'],'excluded':excluded,**counts})
    assert sorted(closed137)==manifest['excluded_family137_pivots']
    assert closed137=={8,11,13,16,17}
    desc,_=s.shared.construct(model,s.shared.read_packet()['families'][136])
    assert set(desc['pivots'])==closed137
    assert all(model.dc[index] in s.shared.ANCHOR for i,index in enumerate(desc['basis_indices']) if i not in closed137)
    bad=copy.deepcopy(packet)
    term=bad['continuation']['power_stages'][0]['claims'][0]['products'][0]
    term[2]=str(s.triples.Q(term[2])+1)
    try:verify_first(model,bad)
    except AssertionError:pass
    else:raise AssertionError('Corrupt unit identity accepted.')
    if manifest['refinements']:
        refined=rank.rb.read(OUT/manifest['refinements'][0]['file'])
        try:verify_refined(model,refined,set())
        except AssertionError:pass
        else:raise AssertionError('Unproved chart vanishing accepted.')
    try:verify137(model,current,set())
    except AssertionError:pass
    else:raise AssertionError('Unproved family-137 chart vanishing accepted.')
    return {'status':'PASS','independent_polynomials':independent,'charts':results,
            'excluded_family16_pivots':sorted(closed),'excluded_family137_pivots':sorted(closed137),
            'corrupt_unit_rejected':True,'unproved_chart_dependencies_rejected':True,
            'family137_global_cube_products':products137,
            'seconds':time.perf_counter()-start,
            'scope':manifest['scope']}


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--independent',action='store_true')
    args=parser.parse_args()
    print(json.dumps(check(args.independent),indent=2),flush=True)

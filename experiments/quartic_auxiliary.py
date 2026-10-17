"""Reproduce the alternative equation basis and the residual-pair search.

The archived timings are observations of overlapping local jobs, not a benchmark.
The shared Y0/Y1 pair closure reproduces a previously published exclusion.
"""
from fractions import Fraction as Q
import argparse,json
import eisenbud_quartic_strand as q
import check_quartic_exclusions as c
e=q.e


def rref(equations):
    span=e.t.base.Elimination()
    for j,p in enumerate(equations):span.insert(dict(p),{j:Q(1)})
    assert len(span.basis)==len(equations)
    for pivot,(p,track) in reversed(sorted(span.basis.items())):
        for k,(row,weights) in span.basis.items():
            if k<pivot and pivot in row:
                a=row[pivot];v=e.t.base.padd(row,p,-a);w=e.t.base.padd(weights,track,-a)
                row.clear();row.update(v);weights.clear();weights.update(w)
    result=[(dict(p),dict(t)) for _,(p,t) in sorted(span.basis.items())]
    for p,t in result:
        assert e.expand_products(equations,[[j,[],str(a)] for j,a in t.items()])==p
    return result


def discover_pair():
    model=e.t.Model();packet=c.shared_system(model,[115,133,135,234,235,271,272,285,288,289,293])
    eq=[e.t.cert.decode(p) for p in packet['equations']];n=len(packet['ids'])+len(packet['ks'])
    forced=set();stages=[]
    for _ in range(len(packet['ids'])+1):
        rows=[e.t.cert.substitute(p,{i:{} for i in forced}) for p in eq]
        charts=[e.t.cert.prove_chart(rows,n,i) for i in range(len(packet['ids'])) if i not in forced]
        for proof in charts:e.t.cert.verify_chart(rows,n,proof)
        new=[p['pivot'] for p in charts if p['excluded']]
        stages.append({'forced_before':sorted(forced),'charts':charts,'new_zeros':new})
        if not new:break
        forced.update(new)
    packet['stages']=stages
    packet['attribution']='Reconstruction of the already excluded Y0/Y1 residual pair, family 24 in fqlx upstream actual-pair packet ffff4273a7a04905bb7de50382d731b91e08b328. Not a new pair exclusion.'
    q.save(q.OUT/'y0-y1-closure.json.gz',packet)


def archive_pilots():
    scratch=e.ROOT/'../../work'
    stage=q.source()[6]['stages'][-1];eq=[e.t.cert.decode(p['polynomial']) for p in stage['necessary']]
    transformed=rref(eq);pilot=q.load(scratch/'degree-four-rref-6.json.gz')
    q.check_quartic([p for p,t in transformed],stage['active'],pilot)
    # Keep the alternative basis and its full finite-strand certificate.
    q.save(q.OUT/'rref-pilot.json.gz',{'active':stage['active'],
        'equations':[e.t.cert.encode(p) for p,t in transformed],
        'transforms':[[[j,str(a)] for j,a in sorted(t.items())] for p,t in transformed],
        'quartic':pilot,'seconds':122.4353733,'direct_seconds':52.1916586,
        'timing_limit':'Concurrent local jobs; not a controlled performance comparison.'})
    pair=q.load(scratch/'residual-y0-y1-quartic.json.gz')
    pair['strands']=[e.strand([e.t.cert.decode(p['polynomial']) for p in pair['necessary']],pair['active'],d) for d in [2,3]]
    q.save(q.OUT/'pair-necessary-failure.json.gz',pair)


def check():
    stage=q.source()[6]['stages'][-1];eq=[e.t.cert.decode(p['polynomial']) for p in stage['necessary']]
    pilot=q.load(q.OUT/'rref-pilot.json.gz');transformed=[e.t.cert.decode(p) for p in pilot['equations']]
    assert pilot['active']==stage['active'] and len(transformed)==len(eq)
    change=e.t.base.Elimination()
    for p,t in zip(transformed,pilot['transforms']):
        assert e.expand_products(eq,[[j,[],a] for j,a in t])==p
        change.insert({j:Q(a) for j,a in t})
    assert len(change.basis)==len(eq)
    q.check_quartic(transformed,stage['active'],pilot['quartic'])
    pair=q.load(q.OUT/'pair-necessary-failure.json.gz');model=e.t.Model()
    counts=e.check_physical(model,pair)
    equations=[e.t.cert.decode(p['polynomial']) for p in pair['necessary']]
    for strand in pair['strands']:
        e.check_strand(equations,pair['active'],strand);assert not strand['vanishings']
    q.check_quartic(equations,pair['active'],pair['quartic']);assert not pair['quartic']['vanishings']
    result={'status':'PASS','rref_change_invertible':True,'rref_quartic_rank':pilot['quartic']['rank'],
        'original_quadratic_terms':sum(map(len,eq)),'rref_quadratic_terms':sum(map(len,transformed)),
        'pair_failed_degrees':[2,3,4],'pair_ranks':[s['rank'] for s in pair['strands']]+[pair['quartic']['rank']],
        'pair_coordinate_powers_found':0,'physical_checks':dict(counts)}
    (q.OUT/'auxiliary-validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive-local-pilots',action='store_true');p.add_argument('--discover-pair',action='store_true')
    a=p.parse_args()
    if a.archive_local_pilots:archive_pilots()
    if a.discover_pair:discover_pair()
    check()

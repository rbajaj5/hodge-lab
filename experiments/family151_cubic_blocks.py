"""Small pure-character blocks of the newly discovered global cubics."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from fractions import Fraction as Q
from math import comb
import argparse,hashlib,json,subprocess,sys,time
import family151_multipliers as f
e=f.e;q=f.q;cert=f.cert


def mac_map(eq,ids,degree):
    labels=[]
    for j,p in enumerate(eq):
        degrees={len(m) for m in p};assert len(degrees)==1
        d=degrees.pop();assert d>0
        if degree>=d:labels += [(j,m) for m in e.monomials(ids,degree-d)]
    rows=[cert.product(eq[j],{m:Q(1)}) for j,m in labels]
    assert all(all(len(m)==degree for m in p) for p in rows)
    return labels,rows


def strand(eq,ids,degree):
    labels,rows=mac_map(eq,ids,degree);span=e.t.base.Elimination();dependencies=[]
    for k,row in enumerate(rows):
        rel=span.insert(dict(row),{k:Q(1)})
        if rel is not None:dependencies.append([[j,str(c)] for j,c in sorted(rel.items())])
    found=[]
    for i in ids:
        residual={(i,)*degree:Q(1)};weights={}
        while residual:
            pivot=min(residual)
            if pivot not in span.basis:break
            c=residual[pivot];row,rep=span.basis[pivot]
            residual=e.t.base.padd(residual,row,-c);weights=e.t.base.padd(weights,rep,c)
        if not residual:found.append({'coordinate':i,'power':degree,
            'products':[[labels[j][0],list(labels[j][1]),str(c)] for j,c in sorted(weights.items())]})
    rank=len(span.basis);codomain=comb(len(ids)+degree-1,degree)
    assert rank<=codomain
    return {'degree':degree,'domain':len(rows),'codomain':codomain,'rank':rank,'kernel':len(rows)-rank,
        'quotient_dimension':codomain-rank,'dependencies':dependencies,'vanishings':found,'tested_coordinates':ids}


def verify_strand(eq,ids,record):
    degree=record['degree'];labels,rows=mac_map(eq,ids,degree)
    exact=e.t.base.Elimination();modular=e.t.base.Elimination(prime=1000003)
    for row in rows:
        exact.insert(dict(row))
        modular.insert({m:c.numerator*pow(c.denominator,-1,1000003)%1000003 for m,c in row.items()})
    assert len(exact.basis)==len(modular.basis)==record['rank']
    assert record['domain']==len(rows) and record['codomain']==comb(len(ids)+degree-1,degree)
    assert record['quotient_dimension']==record['codomain']-record['rank']
    assert record['kernel']==len(rows)-record['rank']==len(record['dependencies'])
    previous=-1
    for dep in record['dependencies']:
        weights={k:Q(c) for k,c in dep};assert weights and max(weights)>previous and weights[max(weights)]==1
        previous=max(weights)
        assert all(0<=k<len(labels) for k in weights)
        assert not e.expand_products(eq,[[labels[k][0],labels[k][1],c] for k,c in weights.items()])
    expected=[i for i in ids if not e.t.normal({(i,)*degree:Q(1)},exact)]
    assert record['tested_coordinates']==ids and [r['coordinate'] for r in record['vanishings']]==expected
    for r in record['vanishings']:
        assert r['power']==degree
        assert all(all(i in ids for i in m) and len(m)+len(next(iter(eq[j])))==degree for j,m,c in r['products'])
        assert e.expand_products(eq,r['products'])=={(r['coordinate'],)*degree:Q(1)}


def equations():
    source=q.load(f.OUT/'global.json.gz');model=e.t.Model()
    eq=[cert.decode(r['polynomial']) for r in source['baseline']]
    eq += [cert.decode(source['relations'][j]['polynomial']) for j in source['selected_new']]
    groups={}
    for i,raw in enumerate(source['system']['ids']):groups.setdefault(model.dc[raw],[]).append(i)
    return source,eq,sorted(groups.items())


def produce(block):
    start=time.perf_counter();source,eq,groups=equations();character,ids=groups[block]
    chosen=[j for j,p in enumerate(eq) if all(i in ids for m in p for i in m)]
    small=[eq[j] for j in chosen]
    packet={'block':block,'character':list(character),'ids':ids,'raw_ids':[source['system']['ids'][i] for i in ids],
        'equation_indices':chosen,'source_sha256':hashlib.sha256((f.OUT/'global.json.gz').read_bytes()).hexdigest(),
        'strands':[],'completed':False}
    out=f.OUT/f'cubic-block-{block}.json.gz'
    for degree in [3,4,5,6]:
        record=strand(small,ids,degree);packet['strands'].append(record)
        packet['seconds']=time.perf_counter()-start;q.save(out,packet)
        print(block,character,'degree',degree,'equations',len(chosen),'rank',record['rank'],'/',record['codomain'],
            'zeros',[(source['system']['ids'][v['coordinate']],v['power']) for v in record['vanishings']],flush=True)
        if record['vanishings']:break
    packet['completed']=True;q.save(out,packet)


def run(limit):
    plan={'blocks':[0,1,2],'degrees':[3,4,5,6],'stop_on':'first coordinate power','seconds_per_block':limit,'workers':2}
    (f.OUT/'cubic-block-plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    def worker(block):
        start=time.perf_counter()
        try:
            r=subprocess.run([sys.executable,'-S',str(Path(__file__).resolve()),'--block',str(block)],text=True,capture_output=True,timeout=limit)
            output=r.stdout+r.stderr;code=r.returncode;status='completed' if code==0 else 'error'
        except subprocess.TimeoutExpired as ex:
            def dec(v):return v.decode(errors='replace') if isinstance(v,bytes) else v or ''
            output=dec(ex.stdout)+dec(ex.stderr);code=None;status='timeout'
        (f.OUT/f'cubic-block-{block}.log').write_text(output,encoding='utf-8')
        record={'block':block,'status':status,'returncode':code,'limit_seconds':limit,'seconds':time.perf_counter()-start}
        print(json.dumps(record),output,flush=True);return record
    records=[]
    with ThreadPoolExecutor(max_workers=2) as pool:
        for result in pool.map(worker,[0,1,2]):
            records.append(result);(f.OUT/'cubic-block-attempts.json').write_text(json.dumps(records,indent=2)+'\n')


def closure():
    source,eq,groups=equations();desc,physical,_,_=f.build(e.t.Model(),None)
    removed=set()
    for block in [0,1,2]:
        p=q.load(f.OUT/f'cubic-block-{block}.json.gz')
        for r in p['strands'][-1]['vanishings']:removed.add(r['coordinate'])
    remaining=sorted(set(range(len(desc['ids'])))-removed)
    rows=[cert.substitute(p,{i:{} for i in removed}) for p in physical];proofs=[]
    for pivot in remaining:
        proof=cert.prove_chart(rows,len(desc['ids'])+len(desc['Koszul_indices']),pivot)
        cert.verify_chart(rows,len(desc['ids'])+len(desc['Koszul_indices']),proof);proofs.append(proof)
        print('Residual',desc['ids'][pivot],'excluded',proof['excluded'],flush=True)
    packet={'source_sha256':hashlib.sha256((f.OUT/'global.json.gz').read_bytes()).hexdigest(),
        'removed':sorted(removed),'remaining':remaining,'charts':proofs,'excluded':all(p['excluded'] for p in proofs)}
    q.save(f.OUT/'closure.json.gz',packet)


def check(independent=False):
    from collections import Counter
    import copy
    import check_family151_multipliers as checker
    start=time.perf_counter();desc,physical,counts=checker.setup(independent)
    source,eq,groups=equations();assert desc==source['system']
    for relation in source['baseline']+[source['relations'][j] for j in source['selected_new']]:
        counts['relation_products']+=f.syz.verify_relation(physical,len(desc['ids']),list(range(len(desc['ids']))),relation)
    removed=set();blocks=[]
    for block,(character,ids) in enumerate(groups):
        p=q.load(f.OUT/f'cubic-block-{block}.json.gz')
        assert p['source_sha256']==hashlib.sha256((f.OUT/'global.json.gz').read_bytes()).hexdigest()
        assert p['block']==block and p['character']==list(character) and p['ids']==ids
        assert p['raw_ids']==[desc['ids'][i] for i in ids]
        chosen=[j for j,poly in enumerate(eq) if all(i in ids for m in poly for i in m)]
        assert p['equation_indices']==chosen
        small=[eq[j] for j in chosen]
        for record in p['strands']:
            verify_strand(small,ids,record);counts['graded_maps']+=1
        for proof in p['strands'][-1]['vanishings']:
            removed.add(proof['coordinate']);counts['fourth_powers']+=1
            counts['power_products']+=len(proof['products'])
            broken=copy.deepcopy(proof['products']);broken[0][2]=str(Q(broken[0][2])+1)
            assert e.expand_products(small,broken)!={(proof['coordinate'],)*proof['power']:Q(1)}
            counts['mutations_rejected']+=1
        blocks.append({'character':list(character),'raw_ids':p['raw_ids'],'equation_count':len(chosen),
            'ranks':[r['rank'] for r in p['strands']],'codomains':[r['codomain'] for r in p['strands']],
            'zeros':[desc['ids'][r['coordinate']] for r in p['strands'][-1]['vanishings']]})
    c=q.load(f.OUT/'closure.json.gz');remaining=sorted(set(range(len(desc['ids'])))-removed)
    assert c['source_sha256']==hashlib.sha256((f.OUT/'global.json.gz').read_bytes()).hexdigest()
    assert c['removed']==sorted(removed) and c['remaining']==remaining
    assert [p['pivot'] for p in c['charts']]==remaining
    rows=[cert.substitute(p,{i:{} for i in removed}) for p in physical]
    for proof in c['charts']:counts['residual_inferences']+=cert.verify_chart(rows,len(desc['ids'])+len(desc['Koszul_indices']),proof)
    assert c['excluded']==all(p['excluded'] for p in c['charts'])
    report={'status':'PASS','independent_physical_polynomials':independent,'family151_excluded':c['excluded'],
        'blocks':blocks,'residual_raw_ids':[desc['ids'][i] for i in remaining],'checks':dict(counts),
        'seconds':time.perf_counter()-start,'scope':'Family 151 only; combined with the preceding checked results, all 152 selected triples are excluded. Holdout remains unsolved.'}
    (f.OUT/(('independent-' if independent else '')+'closure-validation.json')).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--block',type=int);p.add_argument('--limit',type=int,default=120)
    p.add_argument('--closure',action='store_true');p.add_argument('--check',action='store_true');p.add_argument('--independent',action='store_true')
    a=p.parse_args()
    if a.check:check(a.independent)
    elif a.closure:closure()
    elif a.block is not None:produce(a.block)
    else:run(a.limit)

"""Replay physical reductions, quartic identities and all residual closures.

Family 30 is credited to fqlx: first run reproduce_pair30.py with its pinned
manifest, saving a fresh replay under results/eleven-quartic/pair30.
"""
from collections import Counter
from fractions import Fraction as Q
import argparse, copy, hashlib, json, sys, time
import eleven_quartic as x
e=x.e;q=x.q;c=x.c


def pair30_binding(model,remaining):
    manifest=json.loads((e.ROOT/'references/fqlx-pair30.json').read_text())
    directory=e.ROOT/'work/upstream-pair30'
    for name,digest in manifest['sha256'].items():
        assert hashlib.sha256((directory/name).read_bytes()).hexdigest()==digest
    replay=json.loads((x.OUT/'pair30/replay.json').read_text())
    assert replay['status']=='PASS' and replay['revision']==manifest['revision']
    assert [r['script'] for r in replay['runs']]==['verify_pair30.py','audit_pair30_independent.py']
    assert all(r['exit_code']==0 for r in replay['runs'])
    # Bind the external proof to the actual target and basis, not just names.
    sys.path.insert(0,str(directory))
    import audit_degree7_e1 as external
    data=external.reconstruct();external.verify(data)
    assert external.F==e.t.base.F and external.A==e.t.base.A
    ids=[123,135,180,210,229,232,235,272,289,293]
    assert set(remaining)<=set(ids)
    for i in ids:
        b=data['basis'][i]
        assert (external.decode(b['D']),[external.decode(p) for p in b['N']])==model.pairs[i]
    return {'kind':'fqlx_pair30','revision':manifest['revision'],'source':manifest['url'],
        'basis_pairs_matched':len(ids),'target_F_A_matched':True,
        'source_files_hash_checked':len(manifest['sha256']),
        'replay':'pair30/replay.json'}


def check(independent=False):
    start=time.perf_counter()
    if independent:
        from check_degree7_triples import IndependentModel
        model=IndependentModel()
    else:model=e.t.Model()
    old={f['number']:f for f in e.original()};counts=Counter();results=[]
    packet=q.load(x.OUT/'blocks.json.gz');assert packet['source_sha256']==q.source_sha()
    for number,source in x.source().items():
        before=old[number];counts.update(e.t.verify_family(model,before))
        active=before['remaining'];assert source['initial_active']==active
        assert source['characters']==before['characters']
        for stage in source['stages']:
            assert stage['active']==active;counts.update(e.check_physical(model,stage))
            eq=[e.t.cert.decode(p['polynomial']) for p in stage['necessary']];removed=set()
            for strand in stage['strands']:
                for proof in strand['vanishings']:
                    i=proof['coordinate'];assert i in active
                    assert e.expand_products(eq,proof['products'])=={(i,)*proof['power']:Q(1)}
                    removed.add(i);counts['inherited_power_identities']+=1
            assert sorted(removed)==stage['removed'];active=[i for i in active if i not in removed]
        assert active==source['remaining'];removed=set()
        for block in [b for b in packet['blocks'] if b['number']==number]:
            assert block['active']==[i for i in active if model.dc[i]==tuple(block['character'])]
            for proof in block['strands'][-1]['vanishings']:
                i=proof['coordinate'];assert i in block['active'] and proof['power']==4
                products=[[block['equation_indices'][j],mon,a] for j,mon,a in proof['products']]
                assert e.expand_products(eq,products)=={(i,)*4:Q(1)}
                removed.add(i);counts['quartic_power_identities']+=1
                broken=copy.deepcopy(products);broken[0][2]=str(Q(broken[0][2])+1)
                assert e.expand_products(eq,broken)!={(i,)*4:Q(1)}
                counts['corrupted_identities_rejected']+=1
        remaining=[i for i in active if i not in removed];chars={model.dc[i] for i in remaining}
        if len(chars)==1:closure={'kind':'single_character','proof':c.single_character(model,next(iter(chars)),remaining)}
        elif chars=={(0,1,0),(5,3,0)}:closure=pair30_binding(model,remaining)
        elif len(chars)==2:closure=x.replay_pair(model,remaining)
        else:
            assert number in [17,151] and not removed
            closure=None
        row={'number':number,'excluded':closure is not None,'quartic_zeros':sorted(removed),
             'remaining_after_quartics':remaining,'remaining_characters':sorted(map(list,chars)),
             'closure':closure}
        results.append(row);print(number,'excluded' if closure else 'unresolved',flush=True)
    report={'status':'PASS','independent_physical_polynomials':independent,'families':results,
        'checks':dict(counts),'excluded':sum(r['excluded'] for r in results),
        'unresolved':[r['number'] for r in results if not r['excluded']],
        'source_sha256':q.source_sha(),'seconds':time.perf_counter()-start,
        'scope':'Eleven complete selected degree-seven triple families modulo the established F*S1 gauge; holdout remains unsolved.'}
    assert report['excluded']==9 and report['unresolved']==[17,151]
    name='exclusions-'+('independent-' if independent else '')+'validation.json'
    (x.OUT/name).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='families'},indent=2),flush=True)


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--independent',action='store_true')
    check(p.parse_args().independent)

"""Degree-four continuation on the eleven remaining selected triples.

Pure-character blocks are subsets of necessary equations, without specializing
other denominator coordinates. Full maps are retained for the two survivors.
"""
from fractions import Fraction as Q
from collections import Counter
from pathlib import Path
import argparse, copy, hashlib, json, subprocess, sys, time
import eisenbud_quartic_strand as q
import check_quartic_exclusions as c
e=q.e
OUT=e.ROOT/'results/eleven-quartic'
NUMBERS=[1,2,4,5,7,9,15,17,39,150,151]


def source():
    packet=q.load(e.OUT/'certificates.json.gz')
    assert packet['sources']==e.source_hashes()
    return {f['number']:f for f in packet['families'] if f['number'] in NUMBERS}


def discover_blocks():
    model=e.t.Model();blocks=[]
    for number,f in source().items():
        stage=f['stages'][-1];ids=stage['active']
        assert ids==f['remaining'] and not stage['removed']
        eq=[e.t.cert.decode(p['polynomial']) for p in stage['necessary']]
        for char in sorted({model.dc[i] for i in ids}):
            small_ids=[i for i in ids if model.dc[i]==char]
            selected=[j for j,p in enumerate(eq) if all(i in small_ids for m in p for i in m)]
            small=[eq[j] for j in selected]
            strands=[e.strand(small,small_ids,d) for d in [2,3,4]]
            blocks.append({'number':number,'character':list(char),'active':small_ids,
                'equation_indices':selected,'strands':strands})
            print(number,char,'rank',strands[-1]['rank'],'/',strands[-1]['codomain'],
                  'zeros',[p['coordinate'] for p in strands[-1]['vanishings']],flush=True)
    q.save(OUT/'blocks.json.gz',{'source_sha256':q.source_sha(),'blocks':blocks})


def full(number):
    start=time.perf_counter();stage=source()[number]['stages'][-1]
    eq=[e.t.cert.decode(p['polynomial']) for p in stage['necessary']]
    record=q.ordered_strand(eq,stage['active'])
    q.save(OUT/f'full-{number}.json.gz',{'number':number,'source_sha256':q.source_sha(),
        'quartic':record,'seconds':time.perf_counter()-start})
    print('full',number,record['rank'],record['kernel'],record['vanishings'],flush=True)


def bounded_full():
    # Run isolated jobs concurrently; each has its own 300-second wall limit.
    # Timings are not a performance comparison.
    from concurrent.futures import ThreadPoolExecutor
    def run(number):
        start=time.perf_counter();command=[sys.executable,'-S',__file__,'--full',str(number)]
        try:
            result=subprocess.run(command,capture_output=True,text=True,timeout=300)
            text=result.stdout+result.stderr;status='completed' if result.returncode==0 else 'error'
            code=result.returncode
        except subprocess.TimeoutExpired as ex:
            def decode(x):return x.decode('utf-8',errors='replace') if isinstance(x,bytes) else x or ''
            text=decode(ex.stdout)+decode(ex.stderr);status='timeout';code=None
        (OUT/f'full-{number}.log').write_text(text,encoding='utf-8')
        return {'number':number,'limit_seconds':300,'elapsed_seconds':time.perf_counter()-start,
                'status':status,'exit_code':code,'search':'exact rational quartic map, sparse-column order'}
    with ThreadPoolExecutor(max_workers=2) as pool:records=list(pool.map(run,[17,151]))
    (OUT/'bounded-runs.json').write_text(json.dumps(records,indent=2)+'\n')
    print(json.dumps(records,indent=2),flush=True)


def remaining(number):
    stage=source()[number]['stages'][-1]
    blocks=q.load(OUT/'blocks.json.gz')['blocks']
    removed={p['coordinate'] for b in blocks if b['number']==number for p in b['strands'][-1]['vanishings']}
    return [i for i in stage['active'] if i not in removed]


def discover_pairs():
    model=e.t.Model();packets=[]
    for number in [1,4]:
        packet=c.shared_system(model,remaining(number));ids=packet['ids']
        eq=[e.t.cert.decode(p) for p in packet['equations']];n=len(ids)+len(packet['ks'])
        forced=set();stages=[]
        for _ in range(len(ids)+1):
            rows=[e.t.cert.substitute(p,{i:{} for i in forced}) for p in eq]
            charts=[e.t.cert.prove_chart(rows,n,i) for i in range(len(ids)) if i not in forced]
            for proof in charts:e.t.cert.verify_chart(rows,n,proof)
            new=[p['pivot'] for p in charts if p['excluded']]
            stages.append({'forced_before':sorted(forced),'charts':charts,'new_zeros':new})
            print('residual',number,'forced',new,flush=True)
            if not new:break
            forced.update(new)
        packet.update(number=number,stages=stages,
            attribution='Replay of a previously excluded two-character sector; not a new pair exclusion.')
        packets.append(packet)
    q.save(OUT/'residual-pairs.json.gz',{'pairs':packets})


def replay_pair(model,remaining_ids):
    candidates=q.load(OUT/'residual-pairs.json.gz')['pairs']
    packet=next(p for p in candidates if set(remaining_ids)<=set(p['ids']))
    ids=packet['ids'];system=c.shared_system(model,ids)
    for key in ['ks','physical_monomials','equations']:assert system[key]==packet[key]
    eq=[e.t.cert.decode(p) for p in packet['equations']];n=len(ids)+len(packet['ks'])
    forced=set();inferences=0
    for stage in packet['stages']:
        assert stage['forced_before']==sorted(forced)
        rows=[e.t.cert.substitute(p,{i:{} for i in forced}) for p in eq]
        assert [p['pivot'] for p in stage['charts']]==[i for i in range(len(ids)) if i not in forced]
        for proof in stage['charts']:inferences+=e.t.cert.verify_chart(rows,n,proof)
        new=[p['pivot'] for p in stage['charts'] if p['excluded']]
        assert new==stage['new_zeros'];forced.update(new)
    final=[i for j,i in enumerate(ids) if j not in forced]
    chars={model.dc[i] for i in final}
    assert len(chars)<=1,('unresolved residual',chars)
    return {'kind':'shared_numerator_pair','charts':sum(len(s['charts']) for s in packet['stages']),
        'inferences':inferences,'forced_raw_ids':[ids[i] for i in sorted(forced)],
        'single_character':c.single_character(model,next(iter(chars)),final) if chars else None}


def check_blocks():
    packet=q.load(OUT/'blocks.json.gz');assert packet['source_sha256']==q.source_sha()
    model=e.t.Model();sources=source();summaries=[]
    assert [(b['number'],tuple(b['character'])) for b in packet['blocks']]==[
        (n,ch) for n,s in sources.items() for ch in sorted({model.dc[i] for i in s['remaining']})]
    for b in packet['blocks']:
        stage=sources[b['number']]['stages'][-1];eq=[e.t.cert.decode(p['polynomial']) for p in stage['necessary']]
        ids=b['active'];assert ids==[i for i in stage['active'] if model.dc[i]==tuple(b['character'])]
        selected=[j for j,p in enumerate(eq) if all(i in ids for m in p for i in m)]
        assert selected==b['equation_indices'];small=[eq[j] for j in selected]
        assert [r['degree'] for r in b['strands']]==[2,3,4]
        for r in b['strands']:
            e.check_strand(small,ids,r) if r['degree']<4 else q.check_quartic(small,ids,r)
        layers=q.syzygy_layers(small,ids,b['strands'][1],b['strands'][2])
        summaries.append({'number':b['number'],'character':b['character'],'active':ids,
            'equations':len(selected),'ranks':[r['rank'] for r in b['strands']],
            'codomains':[r['codomain'] for r in b['strands']],
            'kernels':[r['kernel'] for r in b['strands']],
            'hilbert_function':[1,len(ids)]+[r['quotient_dimension'] for r in b['strands']],
            'quartic_zeros':[p['coordinate'] for p in b['strands'][-1]['vanishings']],
            'layers':layers})
    fulls=[]
    for n in [17,151]:
        row=q.load(OUT/f'full-{n}.json.gz');stage=sources[n]['stages'][-1]
        assert row['number']==n and row['source_sha256']==q.source_sha()
        eq=[e.t.cert.decode(p['polynomial']) for p in stage['necessary']]
        q.check_quartic(eq,stage['active'],row['quartic'])
        assert not row['quartic']['vanishings']
        layers=q.syzygy_layers(eq,stage['active'],stage['strands'][1],row['quartic'])
        fulls.append({'number':n,**{k:row['quartic'][k] for k in
            ['domain','codomain','rank','kernel','quotient_dimension','vanishings']},'layers':layers})
    report={'status':'PASS','blocks':summaries,'full_maps':fulls,
        'quartic_power_identities':sum(len(b['quartic_zeros']) for b in summaries)}
    (OUT/'blocks-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS',len(summaries),'blocks;',report['quartic_power_identities'],'coordinate powers',flush=True)


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    OUT.mkdir(parents=True,exist_ok=True)
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--blocks',action='store_true');p.add_argument('--pairs',action='store_true')
    p.add_argument('--full',type=int,choices=[17,151]);p.add_argument('--bounded-full',action='store_true')
    p.add_argument('--check-blocks',action='store_true');a=p.parse_args()
    if a.blocks:discover_blocks()
    if a.pairs:discover_pairs()
    if a.full:full(a.full)
    if a.bounded_full:bounded_full()
    if a.check_blocks:check_blocks()

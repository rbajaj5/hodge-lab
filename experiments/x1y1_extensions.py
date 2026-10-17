"""Bounded graded-block search on 132 new X1/Y1 three-character extensions."""
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import argparse,json,subprocess,sys,time
import eisenbud_quartic_strand as q
e=q.e;t=e.t;cert=t.cert
OUT=e.ROOT/'results/x1y1-extensions'
ANCHOR={(0,1,0),(5,3,0)}
PAIR_IDS={123,135,180,210,229,232,235,272,289,293}


def selection(model):
    old=set(model.families)
    triples=sorted({tuple(sorted((*ANCHOR,c))) for c in model.groups if c not in ANCHOR}-old)
    assert len(triples)==132
    wanted=set(triples)
    global_ids={cs:i for i,cs in enumerate(combinations(sorted(model.groups),3),1) if cs in wanted}
    return [{'batch_number':i,'global_number':global_ids[cs],'characters':[list(c) for c in cs],
             'third_character':list(next(c for c in cs if c not in ANCHOR)),
             'basis_indices':sorted(j for c in cs for j in model.groups[c])}
            for i,cs in enumerate(triples,1)]


def terminal(model,ids):
    if not ids:return 'excluded_directly'
    chars={model.dc[i] for i in ids}
    if len(chars)==1:return 'single_character_dependency'
    if chars<=ANCHOR and set(ids)<=PAIR_IDS:return 'pair30_dependency'
    return None


def family(model,item,initial=None,destination=None):
    start=time.perf_counter();ids=(item['basis_indices'] if initial is None else initial)[:]
    packet={**item,'sources':e.source_hashes(),'stages':[],'completed':False,
        'status':'running','remaining':ids}
    if initial is not None:packet['starting_indices']=ids[:]
    path=destination or OUT/f"family-{item['batch_number']:03d}.json.gz";q.save(path,packet)
    for iteration in range(len(ids)+1):
        ending=terminal(model,ids)
        if ending:packet['status']=ending;break
        necessary,ranks=model.necessities(ids);eq=[cert.decode(r['polynomial']) for r in necessary]
        assert all(all(len(m)==2 for m in p) for p in eq)
        witness,_,rank=cert.reduce_span(eq);square=[]
        for i in ids:
            w=witness({(i,i):Q(1)})
            if w:square.append({'coordinate':i,'power':2,'products':[[j,[],c] for j,c in w['equation_weights']]})
        stage={'active':ids[:],'necessary':necessary,'correction_ranks':ranks,
            'quadratic_rank':rank,'squares':square,'blocks':[]}
        found={r['coordinate'] for r in square}
        if not found:
            for char in sorted({model.dc[i] for i in ids}):
                small_ids=[i for i in ids if model.dc[i]==char]
                indices=[j for j,p in enumerate(eq) if all(i in small_ids for m in p for i in m)]
                small=[eq[j] for j in indices];strands=[]
                for degree in [3,4]:
                    strand=e.strand(small,small_ids,degree);strands.append(strand)
                    found.update(r['coordinate'] for r in strand['vanishings'])
                    if strand['vanishings']:break
                stage['blocks'].append({'character':list(char),'active':small_ids,
                    'equation_indices':indices,'strands':strands})
        stage['removed']=sorted(found);packet['stages'].append(stage)
        ids=[i for i in ids if i not in found];packet['remaining']=ids
        packet['seconds']=time.perf_counter()-start;q.save(path,packet)
        if not found:packet['status']='unresolved_bounded_search';break
    else:raise AssertionError('Each successful step must strictly reduce coordinates')
    packet['completed']=True;packet['seconds']=time.perf_counter()-start;q.save(path,packet)
    print(item['batch_number'],item['third_character'],len(item['basis_indices']),'->',len(ids),packet['status'],round(packet['seconds'],2),flush=True)


def chunk(index):
    model=t.Model();items=selection(model)
    for item in items[index::2]:family(model,item)


def run(limit=300):
    model=t.Model();items=selection(model)
    plan={'sources':e.source_hashes(),'anchor':sorted(map(list,ANCHOR)),
        'total_character_triples':428536,'previous_selection':152,'new_selection':items,
        'max_block_degree':4,'workers':2,'chunks':2,'seconds_per_chunk':limit,
        'scope':'Full E1 eigenspaces. Necessary equations annihilate independently enlarged correction columns; surviving searches are inconclusive. No family-151 linear reduction is imported.'}
    (OUT/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    def worker(index):
        start=time.perf_counter()
        try:
            p=subprocess.run([sys.executable,'-S',str(Path(__file__).resolve()),'--chunk',str(index)],text=True,capture_output=True,timeout=limit)
            output=p.stdout+p.stderr;code=p.returncode;status='completed' if code==0 else 'error'
        except subprocess.TimeoutExpired as ex:
            def dec(v):return v.decode(errors='replace') if isinstance(v,bytes) else v or ''
            output=dec(ex.stdout)+dec(ex.stderr);code=None;status='timeout'
        (OUT/f'chunk-{index}.log').write_text(output,encoding='utf-8')
        r={'chunk':index,'status':status,'exit_code':code,'limit_seconds':limit,'seconds':time.perf_counter()-start}
        print(json.dumps(r),output,flush=True);return r
    with ThreadPoolExecutor(max_workers=2) as pool:records=list(pool.map(worker,[0,1]))
    (OUT/'attempts.json').write_text(json.dumps(records,indent=2)+'\n')


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    OUT.mkdir(parents=True,exist_ok=True)
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--chunk',type=int,choices=[0,1]);p.add_argument('--limit',type=int,default=300)
    a=p.parse_args();chunk(a.chunk) if a.chunk is not None else run(a.limit)

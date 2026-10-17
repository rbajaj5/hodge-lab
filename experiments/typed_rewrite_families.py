"""Fresh X0/Y1 families for a separately frozen typed-rewrite comparison.

The baseline uses only exact square consequences. Follow-up methods must be
selected before running continuations; no rewrite policy is fitted here.
"""
from concurrent.futures import ThreadPoolExecutor
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,time
import added_character_homology as added
import degree7_triple_shared as shared
from check_quartic_exclusions import shared_system

x=added.x;e=x.e;t=x.t;cert=x.cert;q=x.q;Model=t.Model
OUT=e.ROOT/'results/typed-rewrite-families'
ANCHOR={(0,0,1),(5,3,0)}


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def selection(model):
    covered=set(model.families)|{tuple(tuple(c) for c in r['characters'])
        for r in x.selection(model)+added.y.selection(model)+added.previous.selection(model)+added.selection(model)}
    assert len(covered)==680
    triples=sorted({tuple(sorted((*ANCHOR,c))) for c in model.groups if c not in ANCHOR}-covered)
    assert len(triples)==132
    wanted=set(triples)
    global_ids={c:i for i,c in enumerate(combinations(sorted(model.groups),3),1) if c in wanted}
    return [{'batch_number':i,'global_number':global_ids[c],'characters':[list(a) for a in c],
        'third_character':list(next(a for a in c if a not in ANCHOR)),
        'basis_indices':sorted(j for a in c for j in model.groups[a])} for i,c in enumerate(triples,1)]


def terminal(model,ids):
    if not ids:return 'excluded_directly'
    chars={model.dc[i] for i in ids}
    if chars<=ANCHOR:return 'x0_y1_dependency'
    if len(chars)==1:return 'single_character_dependency'
    return None


def pair_terminal(model,ids):
    if not ids:return 'excluded_directly'
    if len({model.dc[i] for i in ids})==1:return 'single_character_dependency'
    return None


def pair_description(model):
    return {'batch_number':0,'global_number':0,'third_character':None,
        'characters':sorted(map(list,ANCHOR)),
        'basis_indices':sorted(i for c in ANCHOR for i in model.groups[c])}


def baseline(model,item):
    ids=item['basis_indices'][:]
    packet={**item,'sources':e.source_hashes(),'stages':[],'completed':False,'remaining':ids}
    path=OUT/f"baseline-{item['batch_number']:03d}.json.gz"
    for _ in range(len(ids)+1):
        if terminal(model,ids):break
        necessary,ranks=model.necessities(ids);eq=[cert.decode(r['polynomial']) for r in necessary]
        witness,_,rank=cert.reduce_span(eq);squares=[]
        for i in ids:
            w=witness({(i,i):Q(1)})
            if w:squares.append({'coordinate':i,'products':[[j,[],c] for j,c in w['equation_weights']]})
        packet['stages'].append({'active':ids,'necessary':necessary,'correction_ranks':ranks,
            'rank':rank,'squares':squares})
        ids=[i for i in ids if i not in {w['coordinate'] for w in squares}]
        packet['remaining']=ids;q.save(path,packet)
        if not squares:break
    else:raise AssertionError('Successful stages strictly decrease coordinates')
    packet.update(completed=True,remaining=ids,status=terminal(model,ids) or 'unresolved_squares')
    q.save(path,packet)
    print(item['batch_number'],len(item['basis_indices']),'->',len(ids),packet['status'],flush=True)


def survivors(model):
    result=[]
    for item in selection(model):
        row=q.load(OUT/f"baseline-{item['batch_number']:03d}.json.gz")
        assert row['completed']
        if not terminal(model,row['remaining']):result.append(item['batch_number'])
    return result


def build(model,item,ids):
    if len({model.dc[i] for i in ids})==3:
        return shared.construct(model,{'number':item['global_number'],'remaining':ids,
            'characters':item['characters']},anchor=ANCHOR)
    s=shared_system(model,ids);eq=[cert.decode(p) for p in s['equations']]
    return {'family':item['global_number'],'characters':s['characters'],'basis_indices':ids,
        'Koszul_indices':s['ks'],'stabilizer_order':s['subgroup_order'],
        'equations_sha256':hashlib.sha256(json.dumps(s,sort_keys=True).encode()).hexdigest(),
        'pivots':list(range(len(ids)))},eq


def continuation(model,item,ids,path,stem,finish,source=None):
    """Ordinary exact block/chart continuation, with every failed chart retained."""
    packet={'batch_number':item['batch_number'],'sources':e.source_hashes(),
        'starting_indices':ids[:],'cycles':[],'completed':False,'remaining':ids}
    if source is not None:packet['source_sha256']=digest(source)
    q.save(path,packet)
    for cycle in range(len(ids)+1):
        blockpath=OUT/f'{stem}-{cycle}.json.gz'
        x.family(model,item,initial=ids,destination=blockpath,finish=finish)
        stage={'before':ids,'block_file':blockpath.name,'block_sha256':digest(blockpath)}
        ids=q.load(blockpath)['remaining'];packet['cycles'].append(stage)
        packet['remaining']=ids;q.save(path,packet)
        if finish(model,ids):break
        desc,eq=build(model,item,ids);stage['system']=desc;stage['charts']=[]
        nvars=len(ids)+len(desc['Koszul_indices'])
        for pivot in desc['pivots']:
            chart=cert.prove_chart(eq,nvars,pivot);cert.verify_chart(eq,nvars,chart)
            stage['charts'].append(chart);q.save(path,packet)
            print(item['batch_number'],'chart',ids[pivot],chart['excluded'],flush=True)
        removed=[ids[c['pivot']] for c in stage['charts'] if c['excluded']]
        stage['removed']=removed;ids=[i for i in ids if i not in removed]
        packet['remaining']=ids;q.save(path,packet)
        if not removed:break
    else:raise AssertionError('Successful cycles strictly decrease coordinates')
    packet.update(completed=True,status=finish(model,ids) or 'unresolved',remaining=ids)
    q.save(path,packet);print(item['batch_number'],packet['status'],ids,flush=True)


def pair_binding():
    model=Model();item=pair_description(model)
    continuation(model,item,item['basis_indices'][:],OUT/'full-pair-binding.json.gz',
        'full-pair-blocks',pair_terminal)


def follow(number):
    model=Model();item=selection(model)[number-1];source=OUT/f'baseline-{number:03d}.json.gz'
    row=q.load(source);assert row['completed'] and not terminal(model,row['remaining'])
    continuation(model,item,row['remaining'][:],OUT/f'follow-{number:03d}.json.gz',
        f'rebuild-{number:03d}',terminal,source)


def run(phase,limit,jobs=None):
    assert phase in ['baseline','pair','follow']
    assert 0<limit<=300
    model=Model();items=selection(model)
    if phase=='baseline':assert jobs is None and limit==300;jobs=[0,1]
    elif phase=='pair':assert jobs is None;jobs=[0]
    else:
        assert jobs is not None and len(jobs)==len(set(jobs))
        assert set(jobs)<=set(survivors(model))
    workers=1 if phase=='pair' else 2
    plan={'phase':phase,'jobs':jobs,'seconds_per_job':limit,'workers':workers,
        'sources':e.source_hashes(),'selection':items,'anchor':sorted(map(list,ANCHOR)),
        'preceding_selected_exclusions':680}
    planpath=OUT/f'{phase}-plan.json'
    assert not planpath.exists(),'Preserve the first bounded run'
    planpath.write_text(json.dumps(plan,indent=2)+'\n',encoding='utf-8')
    def worker(number):
        args=['--chunk',str(number)] if phase=='baseline' else ['--pair'] if phase=='pair' else ['--follow',str(number)]
        started=time.perf_counter()
        try:
            p=subprocess.run([sys.executable,'-S',str(Path(__file__).resolve()),*args],
                capture_output=True,text=True,encoding='utf-8',timeout=limit)
            status='completed' if p.returncode==0 else 'error';code=p.returncode;output=p.stdout+p.stderr
        except subprocess.TimeoutExpired as ex:
            dec=lambda v:v.decode('utf-8',errors='replace') if isinstance(v,bytes) else v or ''
            status='timeout';code=None;output=dec(ex.stdout)+dec(ex.stderr)
        (OUT/f'{phase}-{number:03d}.log').write_text(output,encoding='utf-8')
        result={'job':number,'status':status,'exit_code':code,'seconds':time.perf_counter()-started,'limit':limit}
        print(json.dumps(result),output,flush=True);return result
    results=[]
    (OUT/f'{phase}-attempts.json').write_text('[]\n',encoding='utf-8')
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for result in pool.map(worker,jobs):
            results.append(result)
            (OUT/f'{phase}-attempts.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Run without -O.')
    OUT.mkdir(parents=True,exist_ok=True);p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--phase',choices=['baseline','pair','follow']);p.add_argument('--limit',type=int,default=300)
    p.add_argument('--chunk',type=int,choices=[0,1]);p.add_argument('--follow',type=int)
    p.add_argument('--pair',action='store_true');p.add_argument('--jobs',type=int,nargs='*');a=p.parse_args()
    if a.chunk is not None:
        model=Model()
        for item in selection(model)[a.chunk::2]:baseline(model,item)
    elif a.pair:pair_binding()
    elif a.follow is not None:follow(a.follow)
    else:run(a.phase,a.limit,a.jobs)
